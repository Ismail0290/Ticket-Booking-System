from django.db import models
from django.contrib.auth.models import User
import json

class Show(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=200)
    total_seats = models.IntegerField(default=100)
    price_per_seat = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.date} {self.time}"
    
    def available_seats(self):
        booked_seats = Seat.objects.filter(show=self, is_available=False).count()
        return self.total_seats - booked_seats

class Seat(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='seats')
    row = models.CharField(max_length=5)
    number = models.IntegerField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('show', 'row', 'number')
    
    def __str__(self):
        return f"{self.show.title} - {self.row}{self.number}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='bookings')
    seats = models.ManyToManyField(Seat, related_name='bookings')
    booking_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.user.username} - {self.show.title}"
    
    def seat_details(self):
        seats_list = list(self.seats.all().values_list('row', 'number'))
        return ", ".join([f"{row}{number}" for row, number in seats_list])
