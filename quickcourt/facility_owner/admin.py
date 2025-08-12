from django.contrib import admin
from .models import Venue, Court, TimeSlot, Booking

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'location', 'approved')
    list_filter = ('approved',)

@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ('name', 'venue', 'sport_type', 'price_per_hour')

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('court', 'start_time', 'end_time', 'is_available')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'court', 'slot', 'status', 'booked_at')
    list_filter = ('status',)
