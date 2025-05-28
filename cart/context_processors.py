from .cart import Cart

def cart(request):
    # This context processor will make 'cart' available in all templates
    return {'cart': Cart(request)}