# Generated by Django 5.0.6 on 2024-08-13 03:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0015_product_alter_coupon_quantity_coupon_product_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='product',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='coupons.product'),
        ),
    ]
