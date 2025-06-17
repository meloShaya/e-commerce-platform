from decimal import Decimal
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, reverse, get_object_or_404
from orders.models import Order

# Create your views here.

# create the stripe instance
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

def payment_process(request):
    """
    Process the payment for the order.
    """
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

        # Create a Stripe Checkout Session data
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }

        # Add the order items to the session data
        for item in order.items.all():
            session_data['line_items'].append({
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(item.price * Decimal('100')),  # Stripe expects amount in cents
                    'product_data': {
                        'name': item.product.name,
                        # 'description': item.product.description,
                    },
                },
                'quantity': item.quantity,
            })

        # create a stripe checkout session
        session = stripe.checkout.Session.create(**session_data)
        # redirect to the Stripe Checkout page
        return redirect(session.url, code=303)
    else:
        return render(request, 'payment/process.html', locals())
    
def payment_completed(request):
    """
    Handle the payment completion.
    """
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    # Clear the order from the session
    del request.session['order_id']
    
    return render(request, 'payment/completed.html', {'order': order})

def payment_canceled(request):
    """
    Handle the payment cancellation.
    """
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    # Clear the order from the session
    del request.session['order_id']
    
    return render(request, 'payment/canceled.html', {'order': order})
                    