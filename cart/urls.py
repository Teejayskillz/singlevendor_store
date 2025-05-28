from django.urls import path
from . import views

app_name = 'cart' # Define app_name for namespacing

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('update/<int:product_id>/', views.cart_update, name='cart_update'),
    
      # For future use, e.g., quantity changes on cart page
]