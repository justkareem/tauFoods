from django.urls import path
from . import views


urlpatterns = [
    path('', views.getRoutes),
    path('foods/', views.getFoodItems, name='get_all_foods'),
    path('foods/available/', views.getAvailableFoodItems),
    path('foods/unavailable/', views.getUnavailableFoodItems),
    path('foods/<int:pk>/', views.getFoodItem),
    path('foods/add/', views.addFoodItem),
    path('foods/delete/<int:pk>', views.deleteFoodItem),
    path('foods/search/', views.searchFoodItems),
    path('user/signup/', views.signUp),
    path('user/login/', views.login),
    path('user/logout/', views.logout),
    path('order/new/', views.newOrder),
    path('orders/', views.getUserOrders)
]
