from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('booking.urls')),
    # Redirect root to show list
    path('', RedirectView.as_view(pattern_name='show_list', permanent=False)),
]
