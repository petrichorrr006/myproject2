<<<<<<< HEAD
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .models import Provider, TimeSlot, Booking, PatientProfile
=======
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Provider, TimeSlot, Booking
>>>>>>> e9f28742f326e05bc75eb6dabc0d6ed2582cc4bf
import json


def _is_phone_verified(user):
    """Check if the user has a verified phone number."""
    profile = getattr(user, 'patient_profile', None)
    return profile is not None and profile.is_phone_verified


# ═══════════════════════════════════════════════
#  AUTH: Login / Register / Logout / Verify Phone
# ═══════════════════════════════════════════════

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # If patient has unverified phone, send them to verify
            profile = getattr(user, 'patient_profile', None)
            if profile and not profile.is_phone_verified:
                profile.generate_otp()
                messages.info(request, f'OTP sent to {profile.phone_number}. Please verify.')
                return redirect('verify_phone')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'booking/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if password != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        elif len(password) < 4:
            messages.error(request, 'Password must be at least 4 characters.')
        elif not phone:
            messages.error(request, 'Phone number is required.')
        elif PatientProfile.objects.filter(phone_number=phone).exists():
            messages.error(request, 'This phone number is already registered.')
        else:
            user = User.objects.create_user(
                username=username, email=email, password=password,
                first_name=first_name, last_name=last_name,
            )
            profile = PatientProfile.objects.create(user=user, phone_number=phone)
            otp = profile.generate_otp()
            login(request, user)
            # In production this would send a real SMS; for now we show it on screen
            messages.info(request, f'OTP code sent to {phone}: {otp}')
            return redirect('verify_phone')
    return render(request, 'booking/register.html')


@login_required(login_url='login')
def verify_phone(request):
    """OTP verification page."""
    profile = getattr(request.user, 'patient_profile', None)
    if not profile:
        messages.error(request, 'No phone number associated with your account.')
        return redirect('home')
    if profile.is_phone_verified:
        messages.success(request, 'Your phone is already verified.')
        return redirect('home')

    if request.method == 'POST':
        code = request.POST.get('otp_code', '').strip()
        if profile.verify_otp(code):
            messages.success(request, 'Phone number verified successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP code. Please try again.')

    return render(request, 'booking/verify_phone.html', {
        'phone_number': profile.phone_number,
        'otp_hint': profile.otp_code,  # Shown on screen for demo purposes
    })


@login_required(login_url='login')
def resend_otp(request):
    """Resend OTP code."""
    profile = getattr(request.user, 'patient_profile', None)
    if profile and not profile.is_phone_verified:
        otp = profile.generate_otp()
        messages.info(request, f'New OTP sent to {profile.phone_number}: {otp}')
    return redirect('verify_phone')


def logout_view(request):
    logout(request)
    return redirect('home')


# ═══════════════════════════════════════════════
#  PAGES: Home / Slots / Specialization / Provider
# ═══════════════════════════════════════════════

def home(request):
    specializations = Provider.SPECIALIZATION_CHOICES
    return render(request, 'booking/home.html', {
        'specializations': specializations,
    })


def slots_page(request):
<<<<<<< HEAD
    slots = TimeSlot.objects.select_related('provider__user').all()
=======
    slots = TimeSlot.objects.select_related('provider').all()
    return render(request, 'booking/slots.html', {'slots': slots})
>>>>>>> e9f28742f326e05bc75eb6dabc0d6ed2582cc4bf

    selected_spec = request.GET.get('spec', '')
    if selected_spec:
        slots = slots.filter(provider__specialization__iexact=selected_spec)

    return render(request, 'booking/slots.html', {
        'slots': slots,
        'specializations': Provider.SPECIALIZATION_CHOICES,
        'selected_spec': selected_spec,
    })


def specialization_page(request, name):
    slots = TimeSlot.objects.filter(
        provider__specialization__iexact=name
    ).select_related('provider__user')
    return render(
        request,
        'booking/specialization.html',
        {'slots': slots, 'specialization': name.capitalize()},
    )


def provider_detail(request, provider_id):
    provider = get_object_or_404(Provider, id=provider_id)
    slots = TimeSlot.objects.filter(provider=provider).order_by('start_time')
    return render(
        request,
        'booking/doctor.html',
        {'provider': provider, 'slots': slots},
    )


# ═══════════════════════════════════════════════
#  BOOKING: Book a slot + confirmation page
# ═══════════════════════════════════════════════

@login_required(login_url='login')
def book_slot(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id)

    # Check phone verification (doctors skip this check)
    is_doctor = hasattr(request.user, 'provider')
    if not is_doctor and not _is_phone_verified(request.user):
        messages.warning(request, 'Please verify your phone number before booking.')
        return redirect('verify_phone')

    # Double-booking prevention
    if slot.is_booked:
        messages.error(request, 'This slot is already booked.')
        return redirect('slots')

    # Create booking and mark slot
    booking = Booking.objects.create(
        client=request.user,
        slot=slot,
        status='confirmed',
    )
    slot.is_booked = True
    slot.save()

    return render(request, 'booking/booking_confirmation.html', {
        'booking': booking,
    })


# ═══════════════════════════════════════════════
#  HISTORY: Patient appointments / Doctor schedule
# ═══════════════════════════════════════════════

@login_required(login_url='login')
def my_appointments(request):
    bookings = Booking.objects.filter(
        client=request.user
    ).select_related('slot__provider__user').order_by('-slot__start_time')

    now = timezone.now()
    upcoming = [b for b in bookings if b.slot.start_time >= now and b.status != 'cancelled']
    past = [b for b in bookings if b.slot.start_time < now or b.status == 'cancelled']

    return render(request, 'booking/my_appointments.html', {
        'upcoming': upcoming,
        'past': past,
    })


@login_required(login_url='login')
def my_schedule(request):
    """For doctors: see their own slots and who booked them."""
    try:
        provider = Provider.objects.get(user=request.user)
    except Provider.DoesNotExist:
        messages.info(request, 'You are not registered as a doctor.')
        return redirect('my_appointments')

    slots = TimeSlot.objects.filter(provider=provider).order_by('start_time')

    # Attach booking info to each slot
    slot_ids = [s.id for s in slots]
    bookings_map = {}
    for b in Booking.objects.filter(slot_id__in=slot_ids).select_related('client'):
        bookings_map[b.slot_id] = b

    schedule = []
    for slot in slots:
        schedule.append({
            'slot': slot,
            'booking': bookings_map.get(slot.id),
        })

    return render(request, 'booking/my_schedule.html', {
        'provider': provider,
        'schedule': schedule,
    })


# ═══════════════════════════════════════════════
#  API ENDPOINTS (unchanged)
# ═══════════════════════════════════════════════

def specialization_page(request, name):
    slots = TimeSlot.objects.filter(
        provider__specialization__iexact=name
    ).select_related('provider')
    return render(
        request,
        'booking/specialization.html',
        {'slots': slots, 'specialization': name.capitalize()},
    )


def provider_detail(request, provider_id):
    provider = get_object_or_404(Provider, id=provider_id)
    slots = TimeSlot.objects.filter(provider=provider).order_by('start_time')
    return render(
        request,
        'booking/doctor.html',
        {'provider': provider, 'slots': slots},
    )


# ---------- API: Slots ----------
@csrf_exempt
def slots_api(request, slot_id=None):
    if request.method == 'GET':
        if slot_id is not None:
            slot = get_object_or_404(TimeSlot, id=slot_id)
            data = {
                'id': slot.id,
                'provider_id': slot.provider_id,
                'provider': str(slot.provider),
                'start_time': slot.start_time.isoformat(),
                'end_time': slot.end_time.isoformat(),
                'is_booked': slot.is_booked,
            }
            return JsonResponse(data)
<<<<<<< HEAD
        slots = TimeSlot.objects.select_related('provider__user').all()
=======
        slots = TimeSlot.objects.select_related('provider').all()
>>>>>>> e9f28742f326e05bc75eb6dabc0d6ed2582cc4bf
        data = [
            {
                'id': s.id,
                'provider_id': s.provider_id,
                'provider': str(s.provider),
                'start_time': s.start_time.isoformat(),
                'end_time': s.end_time.isoformat(),
                'is_booked': s.is_booked,
            }
            for s in slots
        ]
        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        data = json.loads(request.body)
        slot = TimeSlot.objects.create(
            provider_id=data['provider_id'],
            start_time=data['start_time'],
            end_time=data['end_time'],
        )
        return JsonResponse({'id': slot.id, 'status': 'created'}, status=201)

    if request.method == 'PUT' and slot_id is not None:
        slot = get_object_or_404(TimeSlot, id=slot_id)
        data = json.loads(request.body)
        if 'is_booked' in data:
            slot.is_booked = data['is_booked']
        if 'start_time' in data:
            slot.start_time = data['start_time']
        if 'end_time' in data:
            slot.end_time = data['end_time']
        slot.save()
        return JsonResponse({'status': 'updated'})

    if request.method == 'DELETE' and slot_id is not None:
        slot = get_object_or_404(TimeSlot, id=slot_id)
        slot.delete()
        return JsonResponse({'status': 'deleted'})

    return JsonResponse({'error': 'Method not allowed'}, status=405)


<<<<<<< HEAD
=======
# ---------- API: Providers ----------
>>>>>>> e9f28742f326e05bc75eb6dabc0d6ed2582cc4bf
@csrf_exempt
def providers_api(request, provider_id=None):
    if request.method == 'GET':
        if provider_id is not None:
            provider = get_object_or_404(Provider, id=provider_id)
            data = {
                'id': provider.id,
                'username': provider.user.username,
                'specialization': provider.specialization,
            }
            return JsonResponse(data)
        providers = Provider.objects.select_related('user').all()
        data = [
            {
                'id': p.id,
                'username': p.user.username,
                'specialization': p.specialization,
            }
            for p in providers
        ]
        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        data = json.loads(request.body)
<<<<<<< HEAD
=======
        from django.contrib.auth.models import User
>>>>>>> e9f28742f326e05bc75eb6dabc0d6ed2582cc4bf
        user = User.objects.get(id=data['user_id'])
        provider = Provider.objects.create(
            user=user,
            specialization=data['specialization'],
        )
        return JsonResponse(
            {'id': provider.id, 'status': 'created'},
            status=201,
        )

    if request.method == 'PUT' and provider_id is not None:
        provider = get_object_or_404(Provider, id=provider_id)
        data = json.loads(request.body)
        if 'specialization' in data:
            provider.specialization = data['specialization']
        provider.save()
        return JsonResponse({'status': 'updated'})

    if request.method == 'DELETE' and provider_id is not None:
        provider = get_object_or_404(Provider, id=provider_id)
        provider.delete()
        return JsonResponse({'status': 'deleted'})

    return JsonResponse({'error': 'Method not allowed'}, status=405)


<<<<<<< HEAD
=======
# ---------- API: Bookings ----------
>>>>>>> e9f28742f326e05bc75eb6dabc0d6ed2582cc4bf
@csrf_exempt
def bookings_api(request, booking_id=None):
    if request.method == 'GET':
        if booking_id is not None:
            booking = get_object_or_404(Booking, id=booking_id)
            data = {
                'id': booking.id,
                'client_id': booking.client_id,
                'slot_id': booking.slot_id,
<<<<<<< HEAD
                'status': booking.status,
=======
>>>>>>> e9f28742f326e05bc75eb6dabc0d6ed2582cc4bf
                'created_at': booking.created_at.isoformat(),
            }
            return JsonResponse(data)
        bookings = Booking.objects.select_related('client', 'slot').all()
        data = [
            {
                'id': b.id,
                'client_id': b.client_id,
                'slot_id': b.slot_id,
<<<<<<< HEAD
                'status': b.status,
=======
>>>>>>> e9f28742f326e05bc75eb6dabc0d6ed2582cc4bf
                'created_at': b.created_at.isoformat(),
            }
            for b in bookings
        ]
        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        data = json.loads(request.body)
        booking = Booking.objects.create(
            client_id=data['client_id'],
            slot_id=data['slot_id'],
        )
        slot = booking.slot
        slot.is_booked = True
        slot.save()
        return JsonResponse(
            {'id': booking.id, 'status': 'created'},
            status=201,
        )

    if request.method == 'PUT' and booking_id is not None:
        booking = get_object_or_404(Booking, id=booking_id)
        data = json.loads(request.body)
        old_slot = booking.slot
        if 'slot_id' in data:
            old_slot.is_booked = False
            old_slot.save()
            booking.slot_id = data['slot_id']
            new_slot = booking.slot
            new_slot.is_booked = True
            new_slot.save()
        if 'client_id' in data:
            booking.client_id = data['client_id']
        booking.save()
        return JsonResponse({'status': 'updated'})

    if request.method == 'DELETE' and booking_id is not None:
        booking = get_object_or_404(Booking, id=booking_id)
        slot = booking.slot
        slot.is_booked = False
        slot.save()
        booking.delete()
        return JsonResponse({'status': 'deleted'})

    return JsonResponse({'error': 'Method not allowed'}, status=405)
<<<<<<< HEAD
=======

>>>>>>> e9f28742f326e05bc75eb6dabc0d6ed2582cc4bf
