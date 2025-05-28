
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import sys
import json
import httpx # <--- ADD THIS NEW IMPORT
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.cart import Cart # Assuming your cart logic is in cart/cart.py
from .models import Order, OrderItem
from .forms import OrderCreateForm # We'll create this form next
import logging

logger = logging.getLogger(__name__)

# REMOVE THE ENTIRE CustomSSLAdapter CLASS DEFINITION HERE
# class CustomSSLAdapter(HTTPAdapter):
#     def init_poolmanager(self, connections, maxsize, block=False):
#         context = ssl.create_default_context()
#         context.minimum_version = ssl.TLSVersion.TLSv1_2 # Ensure TLSv1.2 is the minimum
#         # context.set_ciphers('DEFAULT@SECLEVEL=1') # Uncomment this line if you are on an older system that might have very strict OpenSSL policies, usually not needed for modern Python.
#         self.poolmanager = requests.packages.urllib3.poolmanager.PoolManager(
#             num_pools=connections,
#             maxsize=maxsize,
#             block=block,
#             ssl_context=context
#         )

@login_required
def order_create(request):
    cart = Cart(request)
    if not cart: # If cart is empty, redirect or show message
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user # Assign the logged-in user to the order
            order.save()

            # Create order items from the cart
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            # Clear the cart immediately after order items are created
            cart.clear()

            messages.success(request, f"Order {order.id} created successfully! Please proceed to payment.")
            # Redirect to the order detail page, which will now have a "Pay Now" button
            return redirect('orders:order_detail', order_id=order.id)
    else:
        # Pre-fill form if user has a profile, otherwise it will be blank
        initial_data = {}
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            profile = request.user.profile
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'address': profile.address,
                'postal_code': profile.zip_code,
                'city': profile.city,
            }
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def initiate_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, paid=False)

    amount_naira = float(order.get_total_cost())

    url = f"{settings.FLUTTERWAVE_BASE_URL}/payments"

    print(f"DEBUG: FLUTTERWAVE_SECRET_KEY as seen by Django: {settings.FLUTTERWAVE_SECRET_KEY}")
    print(f"DEBUG: Python Version: {sys.version}")
    # print(f"DEBUG: Requests Version: {requests.__version__}") # REMOVE THIS LINE
    print(f"DEBUG: HTTPLX Version: {httpx.__version__}") # <--- ADD THIS LINE

    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36"
    }

    tx_ref = f"ORDER-{order.id}-{request.user.id}-{int(order.created.timestamp())}"

    customer_name = f"{request.user.first_name or request.user.username} {request.user.last_name or ''}".strip()
    if not customer_name:
        customer_name = "Anonymous User"

    payload = {
        "tx_ref": tx_ref,
        "amount": amount_naira,
        "currency": "NGN",
        "redirect_url": request.build_absolute_uri(f'/orders/{order.id}/verify-payment/'),
        "customer": {
            "email": order.email,
            "phonenumber": "2348000000000",
            "name": customer_name
        },
        "meta": {
            "order_id": order.id,
            "user_id": request.user.id
        },
        "customizations": {
            "title": "E-commerce Store Payment",
            "description": f"Payment for Order #{order.id}",
            "logo": "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
        }
    }

    print(f"\n--- DEBUG Flutterwave INITIATE ---")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"--- END DEBUG Flutterwave INITIATE ---\n")

    try:
        # --- NEW: Use httpx instead of requests ---
        # httpx uses ssl.create_default_context() by default, similar to CustomSSLAdapter's base behavior.
        # It handles TLS versions and verification differently than requests, which might help bypass the ELB.
        # We don't need a custom adapter or verify=False here by default.
        response = httpx.post(url, headers=headers, json=payload, timeout=30.0) # Use json=payload for automatic JSON serialization
        # --- END NEW: Use httpx ---

        print(f"DEBUG: Flutterwave Raw Response Status Code: {response.status_code}")
        print(f"DEBUG: Flutterwave Raw Response Reason: {response.reason_phrase}") # httpx uses reason_phrase
        print(f"DEBUG: Flutterwave Raw Response Headers: {response.headers}")
        print(f"DEBUG: Flutterwave Raw Response Content: {response.text}")

        response.raise_for_status() # This will raise an HTTPError for 4xx/5xx status codes
        response_data = response.json()

        logger.debug(f"Flutterwave Request: URL={url}, Headers={headers}, Payload={json.dumps(payload)}")
        logger.debug(f"Flutterwave Response: Status Code={response.status_code}, Headers={response.headers}, Content={response.text}")

        if response_data['status'] == 'success' and response_data['data']['link']:
            payment_link = response_data['data']['link']
            order.flutterwave_tx_ref = tx_ref
            order.save()
            messages.success(request, "Redirecting to Flutterwave for payment...")
            return redirect(payment_link)
        else:
            logger.error(f"Flutterwave initiation failed: {response_data.get('message', 'No message')}. Full response: {response.text}")
            messages.error(request, f"Payment initiation failed: {response_data.get('message', 'Unknown error from Flutterwave')}")
            return redirect('orders:order_detail', order_id=order.id)

    except httpx.RequestError as e: # Catch httpx's specific exceptions
        logger.error(f"Flutterwave Request Error (full exception): {e}")
        print(f"DEBUG: Type of RequestException: {type(e)}")
        messages.error(request, f"An error occurred while initiating payment: {e}. Please try again.")
        return redirect('orders:order_detail', order_id=order.id)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        messages.error(request, "An unexpected error occurred.")
        return redirect('orders:order_detail', order_id=order.id)


@login_required
@csrf_exempt # CSRF exemption is needed for the callback from Flutterwave
def verify_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, paid=False)

    # Get transaction reference from the URL query parameters
    tx_ref = request.GET.get('tx_ref')
    status = request.GET.get('status') # 'successful', 'cancelled', 'failed'

    if not tx_ref:
        logger.warning(f"Flutterwave callback received without tx_ref for order {order.id}.")
        messages.error(request, 'Payment verification failed: No transaction reference.')
        return redirect('orders:order_detail', order_id=order.id)

    # IMPORTANT: Always verify transactions on your backend!
    # Do NOT rely solely on the callback status from the URL.

    url = f"{settings.FLUTTERWAVE_BASE_URL}/transactions/{tx_ref}/verify"
    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # Use httpx for verification as well for consistency
        response = httpx.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()
        response_data = response.json()

        logger.debug(f"Flutterwave Verification Request: URL={url}, Headers={headers}")
        logger.debug(f"Flutterwave Verification Response: Status Code={response.status_code}, Content={response.text}")

        if response_data['status'] == 'success' and response_data['data']['status'] == 'successful':
            # Verify the amount paid matches the order total
            expected_amount = float(order.get_total_cost())
            actual_amount = float(response_data['data']['amount'])
            currency = response_data['data']['currency']

            if actual_amount >= expected_amount and currency == "NGN": # Use >= for amount
                order.paid = True
                order.flutterwave_ref = response_data['data']['id'] # Store Flutterwave's unique transaction ID
                order.save()

                # Clear the cart
                cart = Cart(request)
                cart.clear()

                # Redirect to a success page or order detail
                messages.success(request, 'Payment successful!')
                return redirect('orders:order_paid_success', order_id=order.id)
            else:
                logger.error(f"Flutterwave verification: Amount mismatch for order {order.id}. Expected: {expected_amount}, Actual: {actual_amount}")
                messages.error(request, 'Payment verification failed: Amount mismatch.')
                return redirect('orders:order_detail', order_id=order.id)
        else:
            logger.error(f"Flutterwave verification failed for order {order.id}: {response_data.get('message', 'Unknown error')}")
            messages.error(request, 'Payment verification failed.')
            return redirect('orders:order_detail', order_id=order.id)

    except httpx.RequestError as e: # Catch httpx's specific exceptions
        logger.error(f"Flutterwave Verification Request Error for order {order.id}: {e}")
        messages.error(request, f"An error occurred during payment verification: {e}.")
        return redirect('orders:order_detail', order_id=order.id)
    except Exception as e:
        logger.error(f"An unexpected error occurred during verification for order {order.id}: {e}")
        messages.error(request, 'An unexpected error occurred during payment verification.')
        return redirect('orders:order_detail', order_id=order.id)

@login_required
def order_paid_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if not order.paid:
        messages.warning(request, "This order has not been paid for or payment is still pending.")
        return redirect('orders:order_detail', order_id=order_id)
    return render(request, 'orders/order/paid_success.html', {'order': order})