from django.db import models
from shop.models import Product

# Create your models here.

class Order(models.Model):
    """
    Model to represent an order in the e-commerce application.
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['-paid']),
        ]

    def __str__(self):
        return f'Order {self.id} by {self.first_name} {self.last_name}'
    
    def get_total_cost(self):
        """
        Calculate the total cost of the order by summing the prices of all items in the order.
        """
        return sum(item.get_cost() for item in self.items.all())
    
class OrderItem(models.Model):
    """
    Model to represent an item in an order.
    Each item is linked to a specific product and an order.
    """
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} of {self.product.name} (Order {self.order.id})'
    
    def get_cost(self):
        """
        Calculate the cost of this order item.
        """
        return self.price * self.quantity