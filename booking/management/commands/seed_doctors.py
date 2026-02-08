"""
Populate database with realistic sample data:
  - 8 doctors (providers) across 6 specializations
  - 10 patients (regular users)
  - Time slots for every doctor
  - Appointments linking patients to doctor slots

Usage:
    python manage.py seed_doctors          # only creates what doesn't exist yet
    python manage.py seed_doctors --reset  # deletes all sample data and re-creates
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import Provider, TimeSlot, Booking
from django.utils import timezone
from datetime import timedelta
import random


# ── Sample doctors ──────────────────────────────────────────────
DOCTORS = [
    {'username': 'dr_smith',    'first': 'John',    'last': 'Smith',    'spec': 'cardiologist'},
    {'username': 'dr_johnson',  'first': 'Emily',   'last': 'Johnson',  'spec': 'dermatologist'},
    {'username': 'dr_williams', 'first': 'Michael', 'last': 'Williams', 'spec': 'gynecologist'},
    {'username': 'dr_brown',    'first': 'Sarah',   'last': 'Brown',    'spec': 'dentist'},
    {'username': 'dr_davis',    'first': 'David',   'last': 'Davis',    'spec': 'therapist'},
    {'username': 'dr_wilson',   'first': 'Anna',    'last': 'Wilson',   'spec': 'pediatrician'},
    {'username': 'dr_lee',      'first': 'James',   'last': 'Lee',      'spec': 'cardiologist'},
    {'username': 'dr_taylor',   'first': 'Maria',   'last': 'Taylor',   'spec': 'dermatologist'},
]

# ── Sample patients ─────────────────────────────────────────────
PATIENTS = [
    {'username': 'alice_k',    'first': 'Alice',    'last': 'Kim',       'email': 'alice.kim@mail.com'},
    {'username': 'bob_m',      'first': 'Bob',      'last': 'Martinez',  'email': 'bob.martinez@mail.com'},
    {'username': 'clara_n',    'first': 'Clara',    'last': 'Nguyen',    'email': 'clara.nguyen@mail.com'},
    {'username': 'daniel_o',   'first': 'Daniel',   'last': 'O\'Brien',  'email': 'daniel.obrien@mail.com'},
    {'username': 'elena_p',    'first': 'Elena',    'last': 'Petrova',   'email': 'elena.petrova@mail.com'},
    {'username': 'frank_r',    'first': 'Frank',    'last': 'Robinson',  'email': 'frank.robinson@mail.com'},
    {'username': 'grace_s',    'first': 'Grace',    'last': 'Singh',     'email': 'grace.singh@mail.com'},
    {'username': 'henry_t',    'first': 'Henry',    'last': 'Thompson',  'email': 'henry.thompson@mail.com'},
    {'username': 'irene_u',    'first': 'Irene',    'last': 'Ueda',      'email': 'irene.ueda@mail.com'},
    {'username': 'jack_v',     'first': 'Jack',     'last': 'Vasquez',   'email': 'jack.vasquez@mail.com'},
]


class Command(BaseCommand):
    help = 'Populate database with sample doctors, patients, slots and bookings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all sample data before re-creating',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self._reset()

        providers = self._create_doctors()
        patients = self._create_patients()
        slots = self._create_slots(providers)
        self._create_bookings(patients, slots)

        self.stdout.write(self.style.SUCCESS('\nDone! Sample data is ready.'))

    # ── Doctors ──────────────────────────────────────────────────
    def _create_doctors(self):
        self.stdout.write('\n--- Doctors ---')
        providers = []
        for d in DOCTORS:
            user, created = User.objects.get_or_create(
                username=d['username'],
                defaults={
                    'first_name': d['first'],
                    'last_name': d['last'],
                    'email': f"{d['username']}@clinic.com",
                },
            )
            if created:
                user.set_password('doctor123')
                user.save()

            provider, p_created = Provider.objects.get_or_create(
                user=user,
                defaults={'specialization': d['spec']},
            )
            providers.append(provider)
            status = 'CREATED' if p_created else 'exists'
            self.stdout.write(f"  Dr. {d['first']} {d['last']} ({d['spec']}) — {status}")

        return providers

    # ── Patients ─────────────────────────────────────────────────
    def _create_patients(self):
        self.stdout.write('\n--- Patients ---')
        patients = []
        for p in PATIENTS:
            user, created = User.objects.get_or_create(
                username=p['username'],
                defaults={
                    'first_name': p['first'],
                    'last_name': p['last'],
                    'email': p['email'],
                },
            )
            if created:
                user.set_password('patient123')
                user.save()
            patients.append(user)
            status = 'CREATED' if created else 'exists'
            self.stdout.write(f"  {p['first']} {p['last']} ({p['email']}) — {status}")

        return patients

    # ── Time slots ───────────────────────────────────────────────
    def _create_slots(self, providers):
        self.stdout.write('\n--- Time Slots ---')
        base = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        all_slots = []

        for provider in providers:
            existing = TimeSlot.objects.filter(provider=provider).count()
            if existing >= 4:
                self.stdout.write(f"  {provider} — already has {existing} slots, skipping")
                all_slots.extend(list(TimeSlot.objects.filter(provider=provider)))
                continue

            # Create 4 slots per doctor (9:00, 11:00, 14:00, 16:00)
            hours = [0, 2, 5, 7]
            for h in hours:
                start = base + timedelta(hours=h)
                slot = TimeSlot.objects.create(
                    provider=provider,
                    start_time=start,
                    end_time=start + timedelta(minutes=30),
                )
                all_slots.append(slot)
            self.stdout.write(f"  {provider} — 4 slots created")

        return all_slots

    # ── Bookings ─────────────────────────────────────────────────
    def _create_bookings(self, patients, slots):
        self.stdout.write('\n--- Bookings ---')
        if Booking.objects.exists():
            self.stdout.write('  Bookings already exist, skipping')
            return

        available_slots = [s for s in slots if not s.is_booked]
        random.shuffle(available_slots)
        statuses = ['confirmed', 'confirmed', 'confirmed', 'pending', 'pending', 'cancelled']

        booked_count = 0
        for i, patient in enumerate(patients):
            if i >= len(available_slots):
                break
            slot = available_slots[i]
            status = random.choice(statuses)

            Booking.objects.create(
                client=patient,
                slot=slot,
                status=status,
            )

            # Mark slot as booked (unless cancelled)
            if status != 'cancelled':
                slot.is_booked = True
                slot.save()

            booked_count += 1
            self.stdout.write(
                f"  {patient.get_full_name()} -> Dr. {slot.provider} "
                f"({slot.start_time.strftime('%b %d %H:%M')}) — {status.upper()}"
            )

        self.stdout.write(f'  Total: {booked_count} bookings')

    # ── Reset ────────────────────────────────────────────────────
    def _reset(self):
        self.stdout.write(self.style.WARNING('\nResetting sample data...'))
        all_usernames = [d['username'] for d in DOCTORS] + [p['username'] for p in PATIENTS]

        Booking.objects.filter(client__username__in=all_usernames).delete()
        TimeSlot.objects.filter(provider__user__username__in=[d['username'] for d in DOCTORS]).delete()
        Provider.objects.filter(user__username__in=[d['username'] for d in DOCTORS]).delete()
        User.objects.filter(username__in=all_usernames).delete()

        self.stdout.write('  Cleared all sample doctors, patients, slots and bookings.')
