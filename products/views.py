# ~/my_ecommerce_project/products/views.py

from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from cart.forms import CartAddProductForm 
from django.db.models import Q 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Import SearchForm specifically for processing the query in search_results_view
# It will no longer be passed explicitly in contexts as it's handled by context processor.
from .forms import SearchForm 

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products_queryset = Product.objects.filter(available=True) # Use this for initial filtering
    
    # Do not re-initialize products here as it will lose filtering from products_queryset
    # products = Product.objects.filter(available=True) 

    # query is no longer directly handled here as search goes to search_results_view
    # query = None 

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products_queryset = products_queryset.filter(category=category)

    # Attach a form instance to each product for the list page
    products_with_forms = []
    for product in products_queryset: # Iterate over products_queryset
        product.add_to_cart_form = CartAddProductForm()
        products_with_forms.append(product)

    # Paginate results (10 products per page) - paginate products_with_forms
    paginator = Paginator(products_with_forms, 10) 
    page = request.GET.get('page')

    try:
        products_paginated = paginator.page(page) # Use a new variable name for paginated results
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        products_paginated = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver the last page of results.
        products_paginated = paginator.page(paginator.num_pages)

    return render(request,
                  'products/product_list.html',
                  {'category': category,
                   'categories': categories,
                   'products': products_paginated}) # Pass the paginated products

def search_results_view(request):
    # SearchForm is provided globally by the context processor for rendering in base.html.
    # However, we still need to instantiate it here to process the incoming GET request data.
    temp_search_form = SearchForm(request.GET) 
    query = None
    products = Product.objects.filter(available=True) # Start with all available products

    if temp_search_form.is_valid():
        query = temp_search_form.cleaned_data['query']
        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            ).distinct() # Use distinct to avoid duplicate results if a product matches both name and description

    return render(request,
                  'products/search_results.html', 
                  {'products': products,
                   'query': query,
                   # 'search_form': search_form # REMOVED: search_form is now provided by context processor
                   })

def product_detail(request, id, slug):
    product = get_object_or_404(Product,
                                id=id,
                                slug=slug,
                                available=True)
    cart_product_form = CartAddProductForm() # Instantiate the form here
    return render(request,
                  # Corrected template name from 'detail.html' to 'product_detail.html'
                  'products/product_detail.html', 
                  {'product': product,
                   'cart_product_form': cart_product_form})