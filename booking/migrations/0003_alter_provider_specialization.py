from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_provider_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provider',
            name='specialization',
            field=models.CharField(
                choices=[
                    ('cardiologist', 'Cardiologist'),
                    ('dermatologist', 'Dermatologist'),
                    ('gynecologist', 'Gynecologist'),
                    ('dentist', 'Dentist'),
                    ('therapist', 'Therapist'),
                    ('pediatrician', 'Pediatrician'),
                ],
                default='therapist',
                max_length=100,
            ),
        ),
    ]
