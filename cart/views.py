# ~/my_ecommerce_project/cart/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from products.models import Product
from .forms import CartAddProductForm
from django.http import JsonResponse
from decimal import Decimal # Import Decimal for accurate price calculations
import json 
from .cart import Cart 

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])
        
        # Check if it's an AJAX request (from X-Requested-With header)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # IMPORTANT: Include 'cart_count' in the JSON response
            return JsonResponse({'success': True, 'cart_count': len(cart)})
        else:
            return redirect('cart:cart_detail')
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Return form errors for AJAX requests
            return JsonResponse({'success': False, 'errors': form.errors}, status=400) # Use status=400 for bad requests
        else:
            # Handle non-AJAX form invalidation (e.g., re-render product page with errors)
            # This part would typically be more complex, likely re-rendering the product detail page
            # For simplicity, if not AJAX, we might just redirect back or raise an error for now.
            return redirect('products:product_detail', id=product_id, slug=product.slug)


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # IMPORTANT: Include 'cart_total_price', 'cart_total_items', and 'cart_count'
        return JsonResponse({
            'success': True,
            'cart_total_price': float(cart.get_total_price()), # Convert Decimal to float for JSON
            'cart_total_items': len(cart), # Total items (different from unique products)
            'cart_count': len(cart) # Number of unique products in cart
        })
    else:
        return redirect('cart:cart_detail')


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        # Call cart.add with override=True to set the quantity directly
        cart.add(product=product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])

        # --- CRUCIAL CHANGE HERE: Retrieve updated item from DB-backed cart ---
        # After cart.add (which saves to DB), get the updated CartItem object
        updated_cart_item = cart.db_cart.items.get(product=product)
        
        # Now use its properties
        item_quantity = updated_cart_item.quantity
        # Assuming CartItem has a product attribute, and product has a price
        item_price = updated_cart_item.product.price
        item_total_price = float(item_quantity * item_price) # Calculate total price for this item

        return JsonResponse({
            'success': True,
            'item_quantity': item_quantity,
            'item_total_price': item_total_price,
            'cart_total_quantity': len(cart),
            'cart_total_price': float(cart.get_total_price())
        })
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


def cart_detail(request):
    cart = Cart(request)

    for item in cart: # 'item' here is a dictionary
        # Fix: Access dictionary values using square brackets []
        form_initial_data = {'quantity': item['quantity'], 'override': True}

        form_instance = CartAddProductForm(initial=form_initial_data)

        # Debug: Check if the form instance itself thinks it's valid with the initial data
        if not form_instance.is_valid():
            print(f"Debugging: Form for product {item['product'].id} is NOT valid on initialization!")
            # Explicitly print non-field errors
            if form_instance.non_field_errors():
                print(f"Debugging: Non-field errors: {form_instance.non_field_errors()}")
            # Print field errors (will still be empty for quantity, but good to keep)
            print(f"Debugging: Field Errors: {form_instance.errors}")
        else:
            print(f"Debugging: Form for product {item['product'].id} IS valid on initialization.")

        print(f"Debugging: Form HTML for product {item['product'].id}:\n{form_instance.as_p()}")

        # Assign the form instance to a key in the item dictionary
        item['update_quantity_form'] = form_instance

    return render(request, 'cart/detail.html', {'cart': cart})