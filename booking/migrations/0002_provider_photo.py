from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='provider',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='providers/'),
        ),
    ]
