from django.db import models
from django.contrib.auth.models import User
import random


class PatientProfile(models.Model):
    """Extra profile for patients: phone number + OTP verification."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    phone_number = models.CharField(max_length=20, unique=True)
    is_phone_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, blank=True, null=True)

    def generate_otp(self):
        """Generate a 6-digit OTP code and save it."""
        self.otp_code = str(random.randint(100000, 999999))
        self.save()
        return self.otp_code

    def verify_otp(self, code):
        """Check OTP and mark phone as verified."""
        if self.otp_code and self.otp_code == code.strip():
            self.is_phone_verified = True
            self.otp_code = None  # Clear used code
            self.save()
            return True
        return False

    def __str__(self):
        verified = 'verified' if self.is_phone_verified else 'unverified'
        return f"{self.user.username} — {self.phone_number} ({verified})"


class Provider(models.Model):
    SPECIALIZATION_CHOICES = [
        ('cardiologist', 'Cardiologist'),
        ('dermatologist', 'Dermatologist'),
        ('gynecologist', 'Gynecologist'),
        ('dentist', 'Dentist'),
        ('therapist', 'Therapist'),
        ('pediatrician', 'Pediatrician'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(
        max_length=100,
        choices=SPECIALIZATION_CHOICES,
        default='therapist',
    )
    photo = models.ImageField(upload_to='providers/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class TimeSlot(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.provider} | {self.start_time}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE)
    slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client} booked {self.slot} ({self.get_status_display()})"

