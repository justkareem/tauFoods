from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.sign_in, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('orders/', views.orders, name='orders'),
    path('transactions/', views.transactions, name='transactions'),
    path('logout/', views.sign_out, name='logout'),
    path('get-processing-orders/', views.get_processing_orders, name='get_processing_orders'),
    path('update-order/', views.update_order, name='update_order'),
    path('food/add-food/', views.add_food, name='add_food'),
    path('food/update-food/', views.update_food, name='update_food'),

]
