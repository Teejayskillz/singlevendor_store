

from django.db import models
from django.conf import settings # To link to the AUTH_USER_MODEL
from products.models import Product # To link to your Product model
from decimal import Decimal # For precise currency calculations

class Order(models.Model):
    # Link to the User who placed the order (optional, could be null for guest checkout)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='orders',
                             on_delete=models.SET_NULL, # If user is deleted, keep order but set user to null
                             null=True, blank=True)

    # Personal/Shipping Information (can be pre-filled from user profile or entered during checkout)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)

    # Order Status and Timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False) # To track if the order has been paid


    # Add these fields for Flutterwave integration if they are not already there
    flutterwave_tx_ref = models.CharField(max_length=100, blank=True, null=True, unique=True, help_text="Flutterwave transaction reference (used for initiation)")
    flutterwave_ref = models.CharField(max_length=100, blank=True, null=True, help_text="Flutterwave unique transaction ID (from verification)")


    class Meta:
        ordering = ['-created'] # Order by creation date, newest first
        indexes = [
            models.Index(fields=['-created']), # Add database index for faster queries
        ]

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        # Sums the total cost of all items in this order
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    # Link to the Order this item belongs to
    order = models.ForeignKey(Order,
                              related_name='items',
                              on_delete=models.CASCADE) # If order is deleted, delete its items

    # Link to the Product that was ordered
    product = models.ForeignKey(Product,
                                related_name='order_items',
                                on_delete=models.CASCADE) # If product is deleted, delete its order items

    # Store price and quantity at the time of purchase (important for historical accuracy)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        # Calculates the total cost for this specific order item
        return self.price * self.quantity