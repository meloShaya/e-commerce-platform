from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from cart.forms import CartAddProductForm
from .recommender import Recommender

# Create your views here.

# This view handles the product listing page, allowing filtering by category.
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    return render(request, 'shop/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

# This view handles the product detail page, displaying information about a specific product.
def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    r = Recommender()
    # Get recommended products based on the current product
    recommended_products = r.suggest_products_for([product], 4)
    return render(request, 'shop/product/detail.html', 
                  {'product': product, 'cart_product_form': cart_product_form, 'recommended_products': recommended_products})
