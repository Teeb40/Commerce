# Generated by Django 5.0.6 on 2024-08-06 10:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0022_alter_placed_current_bid'),
    ]

    operations = [
        migrations.AddField(
            model_name='placed',
            name='user',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
