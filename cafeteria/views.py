import json
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import FoodItem, Order, Payment
from .serializers import FoodItemSerializer, UserSerializer, OrderSerializer
import requests
from datetime import datetime


@api_view(["POST"])
def signUp(request):
    data = request.body.decode("utf-8")
    data = json.loads(data)
    try:
        validate_email(value=data["email"])
        validate_password(password=data["password"])
    except ValidationError as e:
        return Response(e.message, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    try:
        user = User.objects.create_user(username=data["email"], password=data["password"], )
        user.first_name = data["firstName"]
        user.last_name = data["lastName"]
        user.save()
    except IntegrityError:
        return Response("This email already exists", status=status.HTTP_409_CONFLICT)

    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def login(request):
    data = request.body.decode("utf-8")
    data = json.loads(data)
    username = data.get("username")
    password = data.get("password")
    user = authenticate(request, username=username, password=password)

    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user, many=False)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    if request.method == 'GET':
        # Delete user's token to log them out
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def getRoutes(request):
    routes = [
        {
            "Endpoint": "/foods/",
            "method": "GET",
            "body": None,
            "description": "returns an array of foodItems",
        },
        {
            "Endpoint": "/foods/id/",
            "method": "GET",
            "body": None,
            "description": "returns a specific foodItem",
        },
        {
            "Endpoint": "/foods/available/",
            "method": "GET",
            "body": None,
            "description": "returns an array of available foodItems",
        },
        {
            "Endpoint": "/foods/unavailable/",
            "method": "GET",
            "body": None,
            "description": "returns an array of unavailable foodItems",
        },
        {
            "Endpoint": "/foods/add/",
            "method": "POST",
            "body": {
                "title": "",
                "vendor": "",
                "price": "",
                "img": ""
            },
            "description": "adds a new foodItem to database",
        },
        {
            "Endpoint": "/foods/id/delete/",
            "method": "DELETE",
            "body": {
                "id": ""
            },
            "description": "deletes an existing foodItem",
        },
    ]

    return Response(routes)


@api_view(['GET'])
def getFoodItems(request):
    foodItems = FoodItem.objects.all()
    serializer = FoodItemSerializer(foodItems, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def newOrder(request):
    data = request.body.decode("utf-8")
    data = json.loads(data)
    payment_reference = data.get("payment_reference")

    url = f"https://api.paystack.co/transaction/verify/{payment_reference}"
    headers = {
        "Authorization": "Bearer sk_test_2593bb320e01393d88f91427c697cb31ce52bc55"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        res = response.json()
        if res['data']['status'] == 'success':
            order = Order.objects.create(
                user=request.user,
                order_items=json.loads(data.get("order_items")),
                total_amount=float(data.get("amount")),
                payment_reference=data.get("payment_reference")
            )
            Payment.objects.create(
                order=order,
                payment_channel=res['data']['channel'],
                paid_at=datetime.strptime(res['data']['paid_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                created_at=datetime.strptime(res['data']['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                ip_address=res['data']['ip_address'],
            )
    else:
        # Handle errors or unsuccessful status codes
        print(f"Error: {response.status_code}")
        print(response.text)
        return Response({'message': response.text}, response.status_code)

    return Response({'message': 'Order created successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def getFoodItem(request, pk):
    foodItem = FoodItem.objects.get(id=pk)
    serializer = FoodItemSerializer(foodItem, many=False)
    return Response(serializer.data)


@api_view(['GET'])
def getAvailableFoodItems(request):
    availableFoodItems = FoodItem.objects.filter(available__exact=True).defer('available')
    serializer = FoodItemSerializer(availableFoodItems, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getUnavailableFoodItems(request):
    unavailableFoodItems = FoodItem.objects.filter(available__exact=False).defer('available')
    serializer = FoodItemSerializer(unavailableFoodItems, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def searchFoodItems(request):
    query = request.GET.get('q', '')
    foodItems = FoodItem.objects.filter(title__icontains=query, available__exact=True).defer('available')
    print(foodItems)
    serializer = FoodItemSerializer(foodItems, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def addFoodItem(request):
    data = request.body

    foodItem = FoodItem.objects.create(
        title=data["title"],
        vendor=data["vendor"],
        price=data["price"],
        img=data["img"],
        available=False,
    )

    serializer = FoodItemSerializer(foodItem, many=False)
    return Response(serializer.data)


@api_view(['DELETE'])
def deleteFoodItem(request, pk):
    foodItem = FoodItem.objects.get(id=pk)
    foodItem.delete()
    return Response("FoodItem has been deleted!")


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getUserOrders(request):
    data = request.body.decode("utf-8")
    data = json.loads(data)
    if request.user.username != data['email']:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

