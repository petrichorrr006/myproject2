from django.contrib import admin
from .models import Provider, TimeSlot, Booking, PatientProfile


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_phone_verified')
    list_filter = ('is_phone_verified',)
    search_fields = ('user__username', 'phone_number')

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'photo')
    list_filter = ('specialization',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('provider', 'start_time', 'end_time', 'is_booked')
    list_filter = ('is_booked', 'provider')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'slot', 'status', 'created_at')
    list_filter = ('status',)
