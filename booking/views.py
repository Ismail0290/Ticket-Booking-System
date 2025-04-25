from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import transaction
from django.contrib import messages
from .models import Show, Seat, Booking
import json

# Authentication Views
class RegisterView(View):
    template_name = 'auth/register.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('show_list')
        return render(request, self.template_name)
    
    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if password != confirm_password:
            messages.error(request, "Passwords don't match")
            return render(request, self.template_name)
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, self.template_name)
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(request, self.template_name)
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, "Registration successful")
        return redirect('show_list')

class LoginView(View):
    template_name = 'auth/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('show_list')
        return render(request, self.template_name)
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful")
            return redirect('show_list')
        else:
            messages.error(request, "Invalid username or password")
            return render(request, self.template_name)

class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "Logged out successfully")
        return redirect('login')

# Show Views
class ShowListView(ListView):
    model = Show
    template_name = 'shows/list.html'
    context_object_name = 'shows'

class ShowDetailView(DetailView):
    model = Show
    template_name = 'shows/detail.html'
    context_object_name = 'show'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        show = self.get_object()
        
        # Create a 2D array of seats (10 rows x 10 columns for simplicity)
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        seats_matrix = []
        
        for row in rows:
            row_seats = []
            for num in range(1, 11):
                try:
                    seat = Seat.objects.get(show=show, row=row, number=num)
                    row_seats.append({
                        'id': seat.id,
                        'row': row,
                        'number': num,
                        'available': seat.is_available
                    })
                except Seat.DoesNotExist:
                    # Create seat if it doesn't exist
                    seat = Seat.objects.create(show=show, row=row, number=num)
                    row_seats.append({
                        'id': seat.id,
                        'row': row,
                        'number': num,
                        'available': True
                    })
            seats_matrix.append(row_seats)
        
        context['seats_matrix'] = seats_matrix
        return context

# Booking Views
class BookingCreateView(LoginRequiredMixin, View):
    template_name = 'booking/create.html'
    login_url = '/login/'
    
    def post(self, request, pk):
        show = get_object_or_404(Show, pk=pk)
        seat_ids = request.POST.getlist('seats')
        
        if not seat_ids:
            messages.error(request, "Please select at least one seat")
            return redirect('show_detail', pk=pk)
        
        seats = Seat.objects.filter(id__in=seat_ids, show=show)
        
        # Check if seats are available
        unavailable_seats = seats.filter(is_available=False)
        if unavailable_seats.exists():
            messages.error(request, "Some selected seats are no longer available")
            return redirect('show_detail', pk=pk)
        
        # Calculate total price
        total_price = show.price_per_seat * len(seats)
        
        # Create booking with transaction to ensure atomicity
        try:
            with transaction.atomic():
                booking = Booking.objects.create(
                    user=request.user,
                    show=show,
                    total_price=total_price,
                    status='confirmed'
                )
                booking.seats.set(seats)
                
                # Mark seats as unavailable
                seats.update(is_available=False)
                
                messages.success(request, "Booking confirmed successfully")
                return redirect('booking_detail', pk=booking.pk)
        except Exception as e:
            messages.error(request, f"Booking failed: {str(e)}")
            return redirect('show_detail', pk=pk)

class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'booking/detail.html'
    context_object_name = 'booking'
    login_url = '/login/'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

class BookingHistoryView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'booking/history.html'
    context_object_name = 'bookings'
    login_url = '/login/'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-booking_time')

# Admin Views (Custom admin panel as per requirements)
class AdminShowListView(LoginRequiredMixin, ListView):
    model = Show
    template_name = 'admin/show_list.html'
    context_object_name = 'shows'
    login_url = '/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access this page")
            return redirect('show_list')
        return super().dispatch(request, *args, **kwargs)

class AdminShowCreateView(LoginRequiredMixin, View):
    template_name = 'admin/show_form.html'
    login_url = '/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access this page")
            return redirect('show_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')
        time = request.POST.get('time')
        venue = request.POST.get('venue')
        total_seats = request.POST.get('total_seats')
        price_per_seat = request.POST.get('price_per_seat')
        
        # Validation
        if not all([title, description, date, time, venue, total_seats, price_per_seat]):
            messages.error(request, "All fields are required")
            return render(request, self.template_name)
        
        try:
            show = Show.objects.create(
                title=title,
                description=description,
                date=date,
                time=time,
                venue=venue,
                total_seats=total_seats,
                price_per_seat=price_per_seat
            )
            messages.success(request, "Show created successfully")
            return redirect('admin_show_list')
        except Exception as e:
            messages.error(request, f"Failed to create show: {str(e)}")
            return render(request, self.template_name)

class AdminShowUpdateView(LoginRequiredMixin, View):
    template_name = 'admin/show_form.html'
    login_url = '/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access this page")
            return redirect('show_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, pk):
        show = get_object_or_404(Show, pk=pk)
        return render(request, self.template_name, {'show': show})
    
    def post(self, request, pk):
        show = get_object_or_404(Show, pk=pk)
        
        show.title = request.POST.get('title')
        show.description = request.POST.get('description')
        show.date = request.POST.get('date')
        show.time = request.POST.get('time')
        show.venue = request.POST.get('venue')
        show.total_seats = request.POST.get('total_seats')
        show.price_per_seat = request.POST.get('price_per_seat')
        
        # Validation
        if not all([show.title, show.description, show.date, show.time, show.venue, show.total_seats, show.price_per_seat]):
            messages.error(request, "All fields are required")
            return render(request, self.template_name, {'show': show})
        
        try:
            show.save()
            messages.success(request, "Show updated successfully")
            return redirect('admin_show_list')
        except Exception as e:
            messages.error(request, f"Failed to update show: {str(e)}")
            return render(request, self.template_name, {'show': show})

class AdminShowDeleteView(LoginRequiredMixin, View):
    login_url = '/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access this page")
            return redirect('show_list')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, pk):
        show = get_object_or_404(Show, pk=pk)
        try:
            show.delete()
            messages.success(request, "Show deleted successfully")
        except Exception as e:
            messages.error(request, f"Failed to delete show: {str(e)}")
        return redirect('admin_show_list')

class AdminBookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'admin/booking_list.html'
    context_object_name = 'bookings'
    login_url = '/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access this page")
            return redirect('show_list')
        return super().dispatch(request, *args, **kwargs)
