
from django.urls import path
from . import views

app_name = 'products' # This is important for namespacing URLs

urlpatterns = [
    # Path for listing all products or products by category
    path('search/', views.search_results_view, name='search_results'),
    path('', views.product_list, name='product_list'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    # Path for a single product detail
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    
]