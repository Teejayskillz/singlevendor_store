
from django.db import models
from products.models import Product # Import the Product model

class Cart(models.Model):
    # We use session_key to uniquely identify a cart, allowing anonymous carts.
    # For logged-in users, you can associate this cart with a User later.
    session_key = models.CharField(max_length=40, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'cart'
        verbose_name_plural = 'carts'

    def __str__(self):
        return f"Cart {self.id} ({self.session_key or 'anonymous'})"

    def get_total_price(self):
        # Calculate the total price of all items in the cart
        return sum(item.get_item_price() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product') # A product can only appear once in a given cart
        verbose_name = 'cart item'
        verbose_name_plural = 'cart items'

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.id}"

    def get_item_price(self):
        return self.quantity * self.product.price