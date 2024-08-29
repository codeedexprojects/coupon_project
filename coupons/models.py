from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid
import random
from django.conf import settings
from django.utils import timezone



class MyUserManager(BaseUserManager):
    def create_user(self, mobile_number, full_name, password=None):
        if not mobile_number:
            raise ValueError('Users must have a mobile number')
        if not full_name:
            raise ValueError('Users must have a full name')

        user = self.model(
            mobile_number=mobile_number,
            full_name=full_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, full_name, password=None):
        user = self.create_user(
            mobile_number,
            full_name,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    mobile_number = models.CharField(max_length=10, unique=True)
    full_name = models.CharField(max_length=100)
    referral_code = models.CharField(max_length=14, unique=True, blank=True)
    wallet_balance = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['full_name']

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
        super().save(*args, **kwargs)

    def generate_referral_code(self):
        random_numbers = ''.join(random.choices('0123456789', k=6))
        return f"EH{random_numbers}"

    def __str__(self):
        return self.mobile_number

    @property
    def is_staff(self):
        return self.is_admin

class Referral(models.Model):
    referrer = models.ForeignKey(User, related_name='referrals', on_delete=models.CASCADE)
    referred_user = models.OneToOneField(User, related_name='referred_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    points_credited = models.BooleanField(default=False)  # New field to track if points have been credited



class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for {self.product.name}'

import logging
logger = logging.getLogger(__name__)

class Coupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()
    quantity = models.IntegerField()
    coupon_number = models.CharField(max_length=8, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_winner = models.BooleanField(default=False)
    is_amount_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.coupon_number:
            self.coupon_number = self.generate_coupon_number()

        # Log coupon details before saving
        logger.info(f"Saving Coupon: user={self.user}, product={self.product}, "
                    f"amount={self.amount}, quantity={self.quantity}, "
                    f"coupon_number={self.coupon_number}")
        super().save(*args, **kwargs)

    def generate_coupon_number(self):
        return "CP" + str(random.randint(100000, 999999))

    def __str__(self):
        return self.coupon_number


    
class CouponAmount(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Coupon Amount: {self.amount}"
      


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=0)
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount in INR
    amount_in_paise = models.IntegerField(default=0)  # Default value added
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    is_amount_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


    

def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/gallery_<id>/<filename>
    return 'gallery_{0}/{1}'.format(instance.id, filename)

class Gallery(models.Model):
    image = models.ImageField(upload_to=user_directory_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f'Gallery image {self.id}'



class Timer(models.Model):
    start_date = models.DateTimeField(auto_now_add=True)  # Auto-set on creation
    end_date = models.DateTimeField(null=True, blank=True)  # Can be set via API
    is_active = models.BooleanField(default=True)  # Tracks whether the timer is active

    def save(self, *args, **kwargs):
        # Check if the end_date has passed to determine if the timer is active
        if self.end_date and self.end_date < timezone.now():
            self.is_active = False
        else:
            self.is_active = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Timer - Active: {self.is_active}, Start: {self.start_date}, End: {self.end_date}"