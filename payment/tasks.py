from io import BytesIO
from celery import shared_task
import weasyprint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Order

@shared_task
def payment_completed(order_id):
    """
    Task to handle the completion of a payment.
    This task generates a PDF invoice for the order and sends it via email.
    """
    order = Order.objects.get(id=order_id)
    
    # Generate PDF invoice
    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    weasyprint.HTML(string=html).write_pdf(stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')], target=out)
    # out.seek(0)

    # Create email
    email = EmailMessage(
        subject=f'Invoice for Order {order.id}',
        body='Please find attached your invoice.',
        from_email='admin@myshop.com',
        to=[order.email]
    )
    
    # Attach PDF file
    email.attach(f'invoice_{order.id}.pdf', out.getvalue(), 'application/pdf')
    
    # Send email
    email.send()