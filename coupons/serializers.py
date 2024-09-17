from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    referrer_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'mobile_number', 'full_name',  'wallet_balance', 'referral_code', 'referrer_code']
        extra_kwargs = {
            'wallet_balance': {'read_only': True},
            'referral_code': {'read_only': True},
        }

    def create(self, validated_data):
        referrer_code = validated_data.pop('referrer_code', None)
        user = User.objects.create_user(**validated_data)

        if referrer_code:
            referrer = User.objects.filter(referral_code=referrer_code).first()
            if referrer:
                Referral.objects.create(referrer=referrer, referred_user=user)
        return user
    


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'mobile_number', 'full_name')    
    

class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = '__all__'

class UserWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'mobile_number', 'full_name', 'wallet_balance']

class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_superuser:
                    raise serializers.ValidationError("User does not have admin privileges.")
                data['user'] = user
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")

        return data
            
from django.shortcuts import get_object_or_404

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'created_at', 'images']

class CouponSerializer(serializers.ModelSerializer):
    mobile_number = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    product = ProductSerializer()


    class Meta:
        model = Coupon
        fields = ('id', 'user', 'mobile_number', 'product','full_name','amount', 'quantity', 'coupon_number', 'created_at', 'is_winner')
        read_only_fields = ('coupon_number', 'created_at', 'is_winner')

    def get_mobile_number(self, obj):
        return obj.user.mobile_number
    def get_full_name(self, obj):
        return obj.user.full_name


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['id','image', 'created_at']

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'mobile_number']
        extra_kwargs = {'mobile_number': {'read_only': False}}

class WinningCouponSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Coupon
        fields = ['id', 'user', 'amount', 'coupon_number', 'created_at']

class ReferredUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'full_name', 'mobile_number')

class ReferralViewSerializer(serializers.ModelSerializer):
    referred_users = serializers.SerializerMethodField()
    total_referred = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'mobile_number', 'referral_code', 'referred_users', 'total_referred')

    def get_referred_users(self, obj):
        # Get all users who used the current user's referral code
        referred_users = User.objects.filter(referral_code=obj.referral_code)
        return ReferredUserSerializer(referred_users, many=True).data

    def get_total_referred(self, obj):
        # Count the number of users who used the referral code
        total_referred = User.objects.filter(referral_code=obj.referral_code).count()
        return total_referred
    

class UserReferralCountSerializer(serializers.ModelSerializer):
    total_referred = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'mobile_number', 'total_referred')

    def get_total_referred(self, obj):
        return User.objects.filter(referral_code=obj.referral_code).count()
    


class ReferralUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'full_name', 'mobile_number', 'wallet_balance')

class UserReferralDetailSerializer(serializers.ModelSerializer):
    referred_users = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'mobile_number', 'wallet_balance', 'referred_users')

    def get_referred_users(self, obj):
        referrals = Referral.objects.filter(referrer=obj)
        referred_users = [referral.referred_user for referral in referrals]
        return ReferralUserSerializer(referred_users, many=True).data
    
class CouponAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponAmount
        fields = ['id', 'amount']


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ('id', 'image', 'created_at')


class TimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timer
        fields = ['id', 'start_date', 'end_date', 'is_active']
        read_only_fields = ['is_active']



class ApplyReferralCodeSerializer(serializers.Serializer):
    referrer_code = serializers.CharField(required=True)

    def validate_referrer_code(self, value):
        if not User.objects.filter(referral_code=value).exists():
            raise serializers.ValidationError("Invalid referrer code.")
        return value

    def validate(self, data):
        referrer_code = data['referrer_code']
        user = self.context.get('user')
        
        if not user:
            raise serializers.ValidationError("User is not authenticated.")

        # Check if the referrer code belongs to the user
        referrer_user = User.objects.get(referral_code=referrer_code)
        if referrer_user == user:
            raise serializers.ValidationError("You cannot apply your own referrer code.")
        
        return data

    def apply_referrer_code(self, user):
        referrer_code = self.validated_data['referrer_code']
        referrer_user = User.objects.get(referral_code=referrer_code)
        referral, created = Referral.objects.get_or_create(
            referrer=referrer_user,
            referred_user=user
        )
        if created:
            referral.save()