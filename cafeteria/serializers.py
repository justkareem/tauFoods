from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
from .models import FoodItem


class FoodItemSerializer(ModelSerializer):
    class Meta:
        model = FoodItem
        fields = '__all__'


class UserSerializer(ModelSerializer):
    class Meta(object):
        model = User
        fields = ['username', 'first_name', 'last_name']
