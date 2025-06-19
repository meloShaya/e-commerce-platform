from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from coupons.forms import CouponApplyForm
from shop.recommender import Recommender

# Create your views here.
@require_POST
def cart_add(request, product_id):
    """
    View to add a product to the cart.
    It handles POST requests to add a product with a specified quantity.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, available=True)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], update_quantity=cd['override'])
    
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    """
    View to remove a product from the cart.
    It handles GET requests to remove a specified product.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, available=True)
    cart.remove(product)
    
    return redirect('cart:cart_detail')

def cart_detail(request):
    """
    View to display the cart details.
    It handles GET requests to show the products in the cart and their total price.
    """
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })
        coupon_apply_form = CouponApplyForm()

    r = Recommender()
    # Get recommended products based on the cart items
    cart_products = [item['product'] for item in cart]
    if (cart_products):
        recommended_products = r.suggest_products_for(cart_products, max_results=4)
    else:
        recommended_products = []
    
    return render(request, 'cart/detail.html', {'cart': cart, 'coupon_apply_form': coupon_apply_form, 'recommended_products': recommended_products})
