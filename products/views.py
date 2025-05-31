# ~/my_ecommerce_project/products/views.py

from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from cart.forms import CartAddProductForm
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import SearchForm
from django.utils import timezone


def home(request):
    # Data for 'Our Top Picks' section
    featured_products = Product.objects.filter(available=True, featured=True).order_by('-created')[:6]

    # Data for 'Newly Added Products' section
    newly_added_products = Product.objects.filter(available=True).order_by('-created')[:6]

    # Data for 'Shop by Category' section
    categories = Category.objects.all()[:3]

    # --- Data for 'All Products' section ---
    all_available_products = Product.objects.filter(available=True).order_by('-created')

    # Attach a CartAddProductForm to each product
    products_with_forms = []
    for product in all_available_products:
        product.add_to_cart_form = CartAddProductForm()
        products_with_forms.append(product)

    # Pagination for the 'All Products' section
    paginator = Paginator(products_with_forms, 10)
    page = request.GET.get('page')

    try:
        products_paginated = paginator.page(page)
    except PageNotAnInteger:
        products_paginated = paginator.page(1)
    except EmptyPage:
        products_paginated = paginator.page(paginator.num_pages)

    context = {
        'featured_products': featured_products,
        'newly_added_products': newly_added_products,
        'categories': categories,
        'products': products_paginated,
        'title': 'Welcome to MyStore - Your One-Stop Shop!',
    }
    return render(request, 'home.html', context)


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products_queryset = Product.objects.filter(available=True).order_by('-created')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products_queryset = products_queryset.filter(category=category)

    products_with_forms = []
    for product in products_queryset:
        product.add_to_cart_form = CartAddProductForm()
        products_with_forms.append(product)

    paginator = Paginator(products_with_forms, 10)
    page = request.GET.get('page')

    try:
        products_paginated = paginator.page(page)
    except PageNotAnInteger:
        products_paginated = paginator.page(1)
    except EmptyPage:
        products_paginated = paginator.page(paginator.num_pages)

    return render(request,
                  'products/product_list.html',
                  {'category': category,
                   'categories': categories,
                   'products': products_paginated})


def search_results_view(request):
    temp_search_form = SearchForm(request.GET)
    query = None
    products = Product.objects.filter(available=True)

    if temp_search_form.is_valid():
        query = temp_search_form.cleaned_data['query']
        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            ).distinct()

    return render(request,
                  'products/search_results.html',
                  {'products': products,
                   'query': query,
                   })

def product_detail(request, id, slug):
    product = get_object_or_404(Product,
                                id=id,
                                slug=slug,
                                available=True)
    cart_product_form = CartAddProductForm()
    return render(request,
                  'products/product_detail.html',
                  {'product': product,
                   'cart_product_form': cart_product_form})