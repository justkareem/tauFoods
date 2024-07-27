import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from cafeteria.models import Order, FoodItem
from .decorators import redirect_authenticated_user
from .forms import LoginForm, RegistrationForm, FoodForm
import cloudinary.uploader


@redirect_authenticated_user
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Group.objects.get_or_create(name='staff')
            group = Group.objects.get(name='staff')
            user.groups.add(group)
            messages.success(request, 'Registration successful.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


@redirect_authenticated_user
def sign_in(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request=request, username=username, password=password)
            if user is None:
                messages.error(request, 'Invalid login details')
                return redirect('login')

            if not user.groups.filter(name='staff').exists():
                messages.error(request, 'You do not have permission to log in.')
                return redirect('login')

            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@redirect_authenticated_user
def forgot_password(request):
    return render(request, 'forgot-password.html')


@login_required
def sign_out(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {'title': 'Dashboard'})


@login_required
def orders(request):
    return render(request, 'orders.html', {'title': 'Orders'})


@login_required
def transactions(request):
    return render(request, 'transactions.html', {'title': 'Transactions'})


@login_required
def get_processing_orders(request):
    if request.method == 'GET':
        data = list(
            Order.objects.filter(order_status='processing').values('id', 'user__username', 'order_items',
                                                                   'total_amount', 'created_at', 'payment_reference'))
        return JsonResponse(data, safe=False)


@login_required
def update_order(request):
    if request.method == 'POST':
        data = request.body.decode("utf-8")
        data = json.loads(data)
        order = Order.objects.get(id=data.get('id'))
        order.order_status = data.get('order_status')
        order.save()
        return JsonResponse({'status': 'success'}, status=200)


@login_required
def add_food(request):
    if request.method == 'POST':
        form = FoodForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            price = form.cleaned_data['price']
            image = request.FILES['img']
            upload_result = cloudinary.uploader.upload(image)
            image_url = upload_result['url']

            new_food = FoodItem(
                title=title,
                price=price,
                img=image_url
            )
            new_food.save()
            messages.success(request, f'{title} added successfully!')
            return redirect('add_food')
        else:
            messages.error(request, form.errors)
    else:
        form = FoodForm()
    return render(request, 'add_food.html', {'title': 'Add Food', 'form': form})


@login_required
def update_food(request):
    available = request.GET.get('available', 'false').lower() == 'true'
    pk = request.GET.get('id')
    if available is None or pk is None:
        return render(request, 'update_food.html', {'title': 'Change Food Availability'})
    foodItem = FoodItem.objects.get(id=pk)
    foodItem.available = available
    foodItem.save()
    return redirect('update_food')
