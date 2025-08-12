from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Venue(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'OWNER'}, related_name='venues')
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sport_types = models.CharField(max_length=200, help_text="Comma separated values like 'Badminton,Tennis'")
    amenities = models.TextField(blank=True)
    photo = models.ImageField(upload_to='venue_photos/', blank=True, null=True)
    approved = models.BooleanField(default=False)  # admin approves

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Court(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='courts')
    name = models.CharField(max_length=120)
    sport_type = models.CharField(max_length=80)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2)
    operating_start = models.TimeField(blank=True, null=True)
    operating_end = models.TimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.venue.name})"

class TimeSlot(models.Model):
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.court} | {self.start_time} → {self.end_time}"

class Booking(models.Model):
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CHOICES = [
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'USER'}, related_name='bookings')
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='bookings')
    slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_CONFIRMED)
    booked_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user} - {self.court} ({self.status})"
