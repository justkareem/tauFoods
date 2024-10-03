import json

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from cafeteria.models import Order, FoodItem
from .decorators import redirect_authenticated_user
from .forms import LoginForm, RegistrationForm, FoodForm, AnnouncementForm
import cloudinary.uploader


@redirect_authenticated_user
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get_or_create(name='staff')
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


def send_push_notification(contents, headings):
    url = "https://api.onesignal.com/notifications?c=push"

    payload = {
        "app_id": "c94afd56-3783-4f59-8f0d-88a527439023",
        "headings": {"en": headings},
        "contents": {"en": contents},
        "included_segments": ["All"],
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Basic Y2M1NGZkNTMtYjA2Yi00YmI1LThlZjgtZWRlMjQ4NDI0NWMz"
    }

    response = requests.post(url, json=payload, headers=headers)


@login_required
def send_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']

            # Send push notification
            send_push_notification(contents=content, headings=title)

            # You can add success message or redirect here
            messages.success(request, f'Notification sent successfully!')
            return redirect('send_announcement')

    else:
        form = AnnouncementForm()
    return render(request, 'announcement.html', {'title': 'Announcement', 'form': form})


@login_required
def get_processing_orders(request):
    if request.method == 'GET':
        orders_data = list(Order.objects.filter(order_status='processing').values('id', 'user__username', 'order_items',
                                                                                  'total_amount', 'created_at',
                                                                                  'payment_reference').order_by(
            'created_at'))
        paginator = Paginator(orders_data, 15)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        response_data = {
            'orders': list(page_obj.object_list),  # Add this to limit to the paginated page
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
        }

        return JsonResponse(response_data, safe=False)


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
