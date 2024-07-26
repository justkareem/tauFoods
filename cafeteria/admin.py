from django.contrib import admin

# Register your models here.
from .models import FoodItem, Order, Payment
admin.site.register(FoodItem)
admin.site.register(Order)
admin.site.register(Payment)

