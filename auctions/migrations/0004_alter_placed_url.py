# Generated by Django 5.0.6 on 2024-08-01 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_placed_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='placed',
            name='url',
            field=models.URLField(default='No Photo'),
        ),
    ]
