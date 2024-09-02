# Generated by Django 5.0.6 on 2024-09-02 15:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0028_comments_comment_comments_created_at_comments_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='comment',
            field=models.CharField(default='comment', max_length=300, validators=[django.core.validators.MinLengthValidator(1)]),
        ),
    ]