# Generated by Django 5.0.6 on 2024-07-09 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0007_auto_20240706_0901'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='coupons/'),
        ),
    ]
