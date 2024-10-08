# Generated by Django 5.0.6 on 2024-07-13 06:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0009_remove_coupon_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gallery',
            name='user',
        ),
        migrations.AddField(
            model_name='user',
            name='referral_code',
            field=models.CharField(blank=True, max_length=12, unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='wallet_balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('referred_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='referred_by', to='coupons.user')),
                ('referrer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referrals', to='coupons.user')),
            ],
        ),
    ]
