from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Show URLs
    path('', views.ShowListView.as_view(), name='show_list'),
    path('shows/<int:pk>/', views.ShowDetailView.as_view(), name='show_detail'),
    
    # Booking URLs
    path('shows/<int:pk>/book/', views.BookingCreateView.as_view(), name='booking_create'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('bookings/', views.BookingHistoryView.as_view(), name='booking_history'),
    
    # Admin URLs
    path('admin/shows/', views.AdminShowListView.as_view(), name='admin_show_list'),
    path('admin/shows/create/', views.AdminShowCreateView.as_view(), name='admin_show_create'),
    path('admin/shows/<int:pk>/update/', views.AdminShowUpdateView.as_view(), name='admin_show_update'),
    path('admin/shows/<int:pk>/delete/', views.AdminShowDeleteView.as_view(), name='admin_show_delete'),
    path('admin/bookings/', views.AdminBookingListView.as_view(), name='admin_booking_list'),
]
