# Generated by Django 5.0.6 on 2024-08-03 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0018_remove_bids_bidding_bids_amount_bids_item_user_bids'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bids',
            name='item',
            field=models.IntegerField(default=0),
        ),
    ]
