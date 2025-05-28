
from products.forms import SearchForm

def search_form_processor(request):
    """
    Adds the SearchForm to the context of every template.
    """
    return {'search_form': SearchForm(request.GET)}