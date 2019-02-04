from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Test 
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('send/', views.email, name='email'),

    # Account
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name = 'rideService/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name = 'rideService/logout.html'), name='logout'),

    # Ride Create/Edit
    path('request/create', views.RequestCreateView.as_view(), name='request-create'),
    path('request/<int:pk>/update/', views.RequestUpdateView.as_view(), name='request-update'),
    path('request/<int:pk>/delete/', views.RequestDeleteView.as_view(), name='request-delete'),
    
    # Ride Searching/Status Viewing (Owner)
    path('owner/requests/', views.ownerRequest, name='owner-all-requests'),
    path('owner/requests/<int:pk>/detail/', views.RequestDetailView.as_view(), name='request-detail'),

    # Ride Searching/Status Viewing (Sharer)
    path('sharer/search/',views.SharerSearchView, name = 'sharer-search'),
    path('sharer/join/<int:pk>/<int:num_sharer>/', views.sharerJoinRide, name = "join-ride"),
    path('sharer/rides/',views.sharerViewRides, name = 'sharer-detail'),
    path('sharer/leave/<int:pk>/', views.sharerLeaveRide, name='leave-ride'),

    # Ride Searching/Status Viewing (Driver)
    path('driver/requests/find', views.driverFindRequest, name='driver-requests'),
    path('driver/requests/confirmed', views.driverConfirmedRides, name='driver-confirmed-requests'),
    path('driver/requests/<int:pk>/complete', views.DriverCompleteRides, name='complete-request'),
    path('driver/requests/<int:pk>/detail/', views.DriverRequestDetailView.as_view(), name='driver-request-detail'),
    path('driver/requests/confirmed/<int:pk>/detail/', views.DriverConfirmedRequestDetailView.as_view(), name='driver-confirmed-request-detail'),
    path('driver/requests/<int:pk>/<time>/accept', views.driverAccpetRequest, name='accept-request'),

    # Registration/Edit (Driver)
    path('driver/create', views.DriverCreateView.as_view(), name='driver-create'),
    path('driver/<int:pk>/profile/', views.DriverDetailView.as_view(), name='driver-profile'),
    path('driver/<int:pk>/update/', views.DriverUpdateView.as_view(), name='driver-update'),

    # Homepage
    path('role/', views.role, name = 'role'),

]