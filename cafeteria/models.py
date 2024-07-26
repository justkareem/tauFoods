from django.contrib.auth.models import User
from django.db import models


class FoodItem(models.Model):
    title = models.TextField(max_length=30, unique=True)
    vendor = models.TextField(max_length=30, default="TAU cafeteria")
    price = models.IntegerField()
    img = models.TextField()
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-available']


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('ready', 'Ready'),
        ('processing', 'Processing'),
        ('refunded', 'Refunded'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_status = models.CharField(choices=ORDER_STATUS_CHOICES, max_length=10, default='processing')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_items = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_reference = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'Order {self.id}'


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('successful', 'Successful'),
        ('refunded', 'Refunded'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, primary_key=True)
    payment_status = models.CharField(choices=PAYMENT_STATUS_CHOICES, max_length=10, default='successful')
    paid_at = models.DateTimeField()
    created_at = models.DateTimeField()
    payment_channel = models.CharField()
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f'Payment for {self.order}'
