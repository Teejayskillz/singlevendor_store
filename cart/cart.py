# ~/my_ecommerce_project/cart/cart.py

from decimal import Decimal
from django.conf import settings
from products.models import Product

class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        This is a session-based cart.
        """
        self.session = request.session
        # Get the current cart data from the session.
        # It's stored as a dictionary under the CART_SESSION_ID.
        session_cart_data = self.session.get(settings.CART_SESSION_ID)

        # --- DEBUGGING PRINT STATEMENTS ---
        print(f"DEBUG: Raw data from session (key={settings.CART_SESSION_ID}): {session_cart_data}")
        print(f"DEBUG: Type of raw data: {type(session_cart_data)}")
        # --- END DEBUGGING ---

        # Crucial check: If the retrieved data is NOT a dictionary, it's corrupted.
        # In this case, we treat it as if the cart didn't exist and create a fresh one.
        if not isinstance(session_cart_data, dict):
            print("DEBUG: Session cart data is NOT a dictionary. Resetting to empty cart.")
            session_cart_data = {} # Reset to an empty dictionary
            # Also, explicitly clear the corrupted entry from the session to prevent future issues
            if settings.CART_SESSION_ID in self.session:
                del self.session[settings.CART_SESSION_ID]
                self.session.modified = True # Ensure session is saved after deletion

        # If it's still None or an empty dict, initialize it properly
        if not session_cart_data:
            print("DEBUG: Cart data is empty or None. Initializing new empty cart in session.")
            session_cart_data = self.session[settings.CART_SESSION_ID] = {}
        
        self.cart = session_cart_data

        # --- DEBUGGING PRINT STATEMENT ---
        print(f"DEBUG: Final self.cart content after init: {self.cart}")
        print(f"DEBUG: Final type of self.cart after init: {type(self.cart)}")
        # --- END DEBUGGING ---

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        """
        Mark the session as "modified" to make sure it gets saved.
        """
        self.session.modified = True

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products
        from the database.
        """
        # Ensure self.cart is a dictionary before calling .keys()
        if not isinstance(self.cart, dict):
            print("ERROR: self.cart is not a dict in __iter__! Resetting.")
            self.cart = {} # Fallback to empty dict to prevent further errors
            return # Exit if it's still broken, will likely lead to an empty cart displayed

        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        cart_copy = self.cart.copy()
        for product in products:
            if str(product.id) in cart_copy:
                cart_copy[str(product.id)]['product'] = product

        for item in cart_copy.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count all items (total quantity) in the cart.
        """
        # Ensure self.cart is a dictionary before calling .values()
        if not isinstance(self.cart, dict):
            print("ERROR: self.cart is not a dict in __len__! Returning 0.")
            return 0 # Return 0 if it's corrupted

        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Calculate the total cost of all items in the cart.
        """
        if not isinstance(self.cart, dict):
            print("ERROR: self.cart is not a dict in get_total_price! Returning 0.")
            return Decimal(0)

        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Remove the entire cart from the session.
        """
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.save()