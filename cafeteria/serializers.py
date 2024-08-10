from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
from .models import FoodItem, Order


class FoodItemSerializer(ModelSerializer):
    class Meta:
        model = FoodItem
        fields = '__all__'


class UserSerializer(ModelSerializer):
    class Meta(object):
        model = User
        fields = ['username', 'first_name', 'last_name']


class OrderSerializer(ModelSerializer):
    class Meta(object):
        model = Order
        fields = '__all__'
