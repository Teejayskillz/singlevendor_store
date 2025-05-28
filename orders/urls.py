# ~/my_ecommerce_project/orders/urls.py

from django.urls import path
from . import views

app_name = 'orders' # Define app_name for URL namespacing

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('', views.order_list, name='order_list'), # e.g., /orders/
    path('<int:order_id>/', views.order_detail, name='order_detail'), # e.g., /orders/123/
    
     path('<int:order_id>/initiate-payment/', views.initiate_payment, name='initiate_payment'),
    # This URL must match the redirect_url specified in your initiate_payment view payload
    path('<int:order_id>/verify-payment/', views.verify_payment, name='verify_payment'),
    path('<int:order_id>/payment-success/', views.order_paid_success, name='order_paid_success'),
]
