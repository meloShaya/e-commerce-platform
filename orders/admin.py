from django.contrib import admin
from .models import Order, OrderItem
from django.utils.safestring import mark_safe
import csv
import datetime
from django.http import HttpResponse
from django.urls import reverse
# Register your models here.

# create a custom admin action to export orders to CSV
def export_orders_to_csv(modeladmin, request, queryset):
    """
    Export selected orders to a CSV file.
    """
    opts = modeladmin.model._meta
    content_disposition = f'attachment; filename={opts.verbose_name}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition

    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]

    writer.writerow([field.verbose_name for field in fields])
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, datetime.date):
                value = value.strftime('%Y-%m-%d')
            elif isinstance(value, bool):
                value = 'Yes' if value else 'No'
            data_row.append(value)
        writer.writerow(data_row)

    return response
export_orders_to_csv.short_description = "Export selected orders to CSV"

def order_pdf(obj):
    """
    Display a link to the PDF invoice for the order.
    """
    url = reverse('orders:admin_order_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')
order_pdf.short_description = 'Invoice'

def order_payment(obj):
    """
    Display a link to the Stripe payment URL for the order.
    """
    url = obj.get_stripe_url()
    if obj.stripe_id:
        html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
        return mark_safe(html)
    return "Not Paid"
order_payment.short_description = 'Stripe payment'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

def order_detail(obj):
    url = reverse('orders:admin_order_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'paid', order_payment, 'created', 'updated', order_detail, order_pdf]
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
    search_fields = ['first_name', 'last_name', 'email']
    ordering = ['-created']
    actions = [export_orders_to_csv]


    
