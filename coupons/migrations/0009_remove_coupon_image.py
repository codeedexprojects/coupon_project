# Generated by Django 5.0.6 on 2024-07-12 04:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0008_coupon_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupon',
            name='image',
        ),
    ]
