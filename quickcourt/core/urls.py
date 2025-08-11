from django.urls import path,include
from . import views
from django.contrib.auth.decorators import login_required




urlpatterns = [
    
    path('', views.landingpage, name='landingpage'),
    path('login/', views.login_view, name='login'),
    path('otp/', views.otp_view, name='otp'),
    path('otp/verify/', views.otp_verify, name='otp_verify'),
    #path('home/', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path("test-auth/", views.test_auth),
    path('api/search_venues/', views.search_venues, name='search_venues'),
    path('home/', login_required(views.home), name='home'),
    path('venues/', views.list_venues, name='list_venues'),
    path('venues/<str:venue_id>/', views.single_venue, name='single_venue'),
    path('bookings/create/', views.create_booking, name='create_booking'),
    path('bookings/mine/', views.my_bookings, name='my_bookings'),
    path('bookings/<str:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
]
