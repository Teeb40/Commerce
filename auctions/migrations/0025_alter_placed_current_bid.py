# Generated by Django 5.0.6 on 2024-08-06 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0024_alter_placed_current_bid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='placed',
            name='current_bid',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
