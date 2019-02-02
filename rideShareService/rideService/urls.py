from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name = 'rideService/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name = 'rideService/logout.html'), name='logout'),
    path('request/create', views.RequestCreateView.as_view(), name='request-create'),
    path('request/<int:pk>/update/', views.RequestUpdateView.as_view(), name='request-update'),
    path('request/<int:pk>/delete/', views.RequestDeleteView.as_view(), name='request-delete'),
    path('owner/requests/all', views.ownerRequest, name='owner-all-requests'),
    path('driver/requests/', views.driverRequest, name='driver-requests'),
    path('driver/create', views.DriverCreateView.as_view(), name='driver-create'),
    path('driver/<int:pk>/update/', views.DriverUpdateView.as_view(), name='driver-update'),
    path('role/', views.role, name = 'role'),
]