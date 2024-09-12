from rest_framework import generics, status, permissions, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from .models import *
from .serializers import *
from PIL import Image
import io
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.permissions import IsAuthenticated
import time
import razorpay
from django.conf import settings
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from django.db.models import Sum
from django.contrib.auth import login
from decimal import Decimal
from rest_framework.exceptions import NotFound




class AdminLoginView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request, *args, **kwargs):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({"detail": "Login successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = []
    
from rest_framework.permissions import IsAdminUser

class AllUsersWalletView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserWalletSerializer
    permission_classes = [IsAdminUser]

class UserWalletView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserWalletSerializer

    def retrieve(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = get_object_or_404(self.get_queryset(), pk=user_id)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReferralListView(generics.ListAPIView):
    queryset = Referral.objects.all()
    serializer_class = ReferralSerializer

from rest_framework.decorators import api_view

@api_view(['POST'])
def UserLoginView(request):
    full_name = request.data.get('full_name')
    mobile_number = request.data.get('mobile_number')
    
    if not full_name or not mobile_number:
        return Response(
            {
                "status": False,
                "error": "full_name and mobile_number are required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = get_object_or_404(User, full_name=full_name, mobile_number=mobile_number)
        serializer = UserLoginSerializer(user)
        return Response(
            {
                "status": True,
                "message": "Login successful",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {
                "status": False,
                "error": str(e)
            },
            status=status.HTTP_404_NOT_FOUND
        )

    
class GetUserByIdView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'

    def get(self, request, id, *args, **kwargs):
        try:
            user = User.objects.get(id=id)
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        

    
class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    authentication_classes = []
    permission_classes = []
    lookup_field = 'id'

def generate_payment_link(request, quantity):
    if not 1 <= quantity <= 10:
        return HttpResponse("Invalid quantity. Must be between 1 and 10.", status=400)
    
    amount = quantity * 500
    payment_link = f'https://razorpay.me/@codeedextp?amount={amount * 1}' 
    
    return redirect(payment_link)

from django.http import JsonResponse



class CreateCouponView(generics.GenericAPIView):
    serializer_class = CouponSerializer
    
    def post(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)
        quantity = int(request.data.get('quantity', 1))
        product_id = request.data.get('product_id')

        # Validate quantity
        if not 1 <= quantity <= 10:
            return Response({"error": "Invalid quantity. Must be between 1 and 10."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate product
        product = get_object_or_404(Product, id=product_id)

        # Get coupon amount
        coupon_amount = CouponAmount.objects.last()
        if not coupon_amount:
            return Response({"error": "Coupon amount is not defined by admin."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate amount in Decimal and paise
        amount = Decimal(quantity) * coupon_amount.amount
        amount_in_paise = int(amount * 100)  # Convert to paise

        # Create order
        order = Order.objects.create(
            user=user,
            product=product,
            quantity=quantity,
            amount=amount,
            amount_in_paise=amount_in_paise
        )

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        data = {
            "amount": amount_in_paise,  # Amount in paise
            "currency": "INR",
            "receipt": f"order_rcptid_{order.id}"
        }

        try:
            razorpay_order = client.order.create(data=data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        order.razorpay_order_id = razorpay_order['id']
        order.save()

        # Response with order details
        return Response({
            "message": f"{quantity} coupon(s) created successfully. Please proceed with payment.",
            "order_id": order.id,
            "razorpay_order_id": razorpay_order['id'],
            "amount": float(amount)  
        }, status=status.HTTP_201_CREATED)



    

class CompletePaymentView(generics.GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id, order_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)
        order = get_object_or_404(Order, id=order_id, user=user)

        if self.process_payment(order):
            order.is_amount_paid = True
            order.save()

            payment_link = f'{settings.RAZORPAY_PAYMENT_LINK}?amount={order.amount * 1}'  

            return Response({
                "user_id": user_id,
                "status": True,
                "message": "Payment initiated. Redirect to the payment page.",
                "payment_link": payment_link
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "user_id": user_id,
                "status": False,
                "error": "Payment failed."
            }, status=status.HTTP_400_BAD_REQUEST)

    def process_payment(self, order):
        # Placeholder for actual payment processing logic
        # Return True if payment is successful, otherwise return False
        return True


@method_decorator(csrf_exempt, name='dispatch')
class RazorpayWebhookView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        return JsonResponse({"message": "Webhook received."}, status=status.HTTP_200_OK)

class UserCouponsView(generics.ListAPIView):
    serializer_class = CouponSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        return Coupon.objects.filter(user=self.request.user)

class UserCouponsByIDView(generics.ListAPIView):
    serializer_class = CouponSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Coupon.objects.filter(user__id=user_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        if queryset.exists():
            response_data = {
                "status": True,
                "data": serializer.data
            }
        else:
            response_data = {
                "status": False,
                "data": "No coupons found"
            }
        
        return Response(response_data)
    
import os   

class GalleryListCreateView(generics.ListCreateAPIView):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    authentication_classes = []
    permission_classes = []
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        self.compress_image(serializer.validated_data['image'])
        serializer.save()

    def compress_image(self, image_field):
        image = Image.open(image_field)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG', quality=85)
        
        image_io.seek(0)
        
        filename = os.path.basename(image_field.name)
        
        filepath = os.path.join(settings.MEDIA_ROOT, 'gallery', filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(image_io.read())

class GalleryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    permission_classes = []

    def perform_update(self, serializer):
        serializer.save()
        self.compress_image(serializer.instance.image)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def compress_image(self, image_field):
        image = Image.open(image_field.path)
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG', quality=85)
        image_file = image_io.getvalue()

        with open(image_field.path, 'wb') as f:
            f.write(image_file)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]

class TotalUsersView(APIView):
    def get(self, request, *args, **kwargs):
        total_users = User.objects.count()
        return Response({'total_users': total_users}, status=status.HTTP_200_OK)    

class CouponListView(generics.ListAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    # permission_classes = [permissions.IsAuthenticated]

class TotalCouponsView(views.APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        total_coupons = Coupon.objects.count()
        return Response({'total_coupons': total_coupons})
    
class TotalAmountGeneratedView(APIView):
    def get(self, request, *args, **kwargs):
        total_amount = Order.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        return Response({'total_amount_generated': total_amount}, status=status.HTTP_200_OK)

@csrf_exempt
def razorpay_webhook(request):
    if request.method == "POST":
        try:
            event = json.loads(request.body.decode('utf-8'))

            # Handle the event
            if event['event'] == 'payment.captured':
                # Extract payment details
                payment_id = event['payload']['payment']['entity']['id']
                amount = event['payload']['payment']['entity']['amount']
                email = event['payload']['payment']['entity']['email']

                # Log the event (you can implement further logic here)
                print(f"Payment captured: {payment_id}, Amount: {amount}, Email: {email}")

                # Example: Create coupons based on payment details
                # This logic can be adjusted based on your needs
                # Assuming `amount` is in paise, converting to INR
                coupon_quantity = amount // 50000  # 50000 paise = 500 INR

                # Get user by email or other identifier
                # Assuming you have a User model with email field
                user = User.objects.get(email=email)

                for _ in range(coupon_quantity):
                    Coupon.objects.create(user=user, amount=500)

            return HttpResponse(status=200)
        except Exception as e:
            print(f"Error in webhook: {e}")
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=405)
    

class PickRandomCouponView(generics.GenericAPIView):
    serializer_class = CouponSerializer
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Check if there is already a winner
        if Coupon.objects.filter(is_winner=True).exists():
            return Response({"error": "A winner has already been picked"}, status=status.HTTP_403_FORBIDDEN)

        # Get all coupons
        coupons = Coupon.objects.all()

        if not coupons.exists():
            return Response({"error": "No coupons available"}, status=status.HTTP_404_NOT_FOUND)

        # Pick a random coupon
        random_coupon = random.choice(coupons)

        # Set is_winner to True
        random_coupon.is_winner = True
        random_coupon.save()

        # Serialize and return the coupon
        serializer = self.get_serializer(random_coupon)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class WinningUsersView(generics.ListAPIView):
    queryset = Coupon.objects.filter(is_winner=True)
    serializer_class = WinningCouponSerializer


class UserReferralsView(generics.GenericAPIView):
    serializer_class = ReferralViewSerializer
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        try:
            user = User.objects.get(id=user_id)
            serializer = self.get_serializer(user)
            return Response({
                "status": True,
                "data": serializer.data
            }, status=200)
        except User.DoesNotExist:
            return Response({
                "status": False,
                "error": "User not found"
            }, status=404)
        

class UserReferralCountView(generics.GenericAPIView):
    serializer_class = UserReferralCountSerializer
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = self.get_serializer(users, many=True)
        return Response({
            "status": True,
            "data": serializer.data
        }, status=200)
    

class UserReferralDetailView(generics.GenericAPIView):
    serializer_class = UserReferralDetailSerializer
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = self.get_serializer(users, many=True)
        return Response({
            "status": True,
            "data": serializer.data
        }, status=200)
    

import logging

logger = logging.getLogger(__name__)

class CompletePurchaseView(generics.GenericAPIView):
    def post(self, request, user_id, order_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)
        order = get_object_or_404(Order, id=order_id, user=user)

        if order.is_amount_paid:
            return Response({
                "user_id": user_id,
                "order_id": order_id,
                "amount": order.amount,
                "status": "Already Paid",
                "quantity": order.quantity,
                "message": "Order is already completed."
            }, status=status.HTTP_200_OK)

        # Mark the order as paid
        order.is_amount_paid = True
        order.save()

        # Create associated coupons and retrieve their numbers
        coupons = []
        for i in range(order.quantity):
            coupon = Coupon.objects.create(
                user=user,
                product=order.product,
                amount=order.amount / order.quantity,
                quantity=1  # Ensure quantity is set if this is a required field
            )
            coupons.append(coupon.coupon_number)
            logger.info(f"Coupon created: {coupon.coupon_number}")

        # Handle referral points on order completion
        if hasattr(user, 'referred_by'):
            referral = user.referred_by
            if not referral.points_credited:
                referrer = referral.referrer
                referrer.wallet_balance += 50
                referrer.save()
                user.wallet_balance += 10
                user.save()
                referral.points_credited = True
                referral.save()

        logger.info(f"Coupons generated: {coupons}")

        return Response({
            "user_id": user_id,
            "order_id": order_id,
            "amount": order.amount,
            "quantity": order.quantity,
            "status": "Paid",
            "message": "Order placed successfully.",
            "coupons": coupons
        }, status=status.HTTP_200_OK)



    
class WithdrawCouponView(generics.GenericAPIView):
    def post(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)

        if user.wallet_balance < 500:
            return Response({
                "status": False,
                "message": "Insufficient wallet balance. You need at least 500 points."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Deduct points from the user's wallet
        user.wallet_balance -= 500
        user.save()

        # Create a new coupon for the user
        coupon = Coupon.objects.create(user=user, amount=500)
        
        return Response({
            "status": True,
            "message": "Coupon withdrawn successfully.",
            "coupon_number": coupon.coupon_number,
            "wallet_balance": user.wallet_balance
        }, status=status.HTTP_200_OK)
    
class ResetWalletBalanceView(generics.GenericAPIView):
    def post(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)
        
        # Reset the wallet balance
        user.wallet_balance = 0
        user.save()
        
        return Response({
            "status": True,
            "message": "User's wallet balance has been reset.",
            "user_id": user_id,
            "wallet_balance": user.wallet_balance
        }, status=status.HTTP_200_OK)
    

class DeleteAllOrdersView(generics.GenericAPIView):
    # permission_classes = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        Order.objects.all().delete()
        return Response({"message": "All orders have been deleted."}, status=status.HTTP_204_NO_CONTENT)

class DeleteAllCouponsView(generics.GenericAPIView):
    # permission_classes = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        Coupon.objects.all().delete()
        return Response({"message": "All coupons have been deleted."}, status=status.HTTP_204_NO_CONTENT)
    
class AddCouponAmountView(generics.CreateAPIView):
    serializer_class = CouponAmountSerializer
    queryset = CouponAmount.objects.all()

class EditCouponAmountView(generics.UpdateAPIView):
    serializer_class = CouponAmountSerializer
    queryset = CouponAmount.objects.all()
    lookup_field = 'pk'

class DeleteCouponAmountView(generics.DestroyAPIView):
    queryset = CouponAmount.objects.all()
    lookup_field = 'pk'

class CarouselView(generics.ListAPIView):
    serializer_class = GallerySerializer

    def get_queryset(self):
        # Fetch the latest three images
        return Gallery.objects.order_by('-created_at')[:3]


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [IsAuthenticated]

class ProductRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [IsAuthenticated]

# ProductImage CRUD operations
class ProductImageListCreateView(generics.ListCreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    # permission_classes = [IsAuthenticated]

class ProductImageRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    # permission_classes = [IsAuthenticated]



class CreateTimerView(generics.CreateAPIView):
    queryset = Timer.objects.all()
    serializer_class = TimerSerializer

class RetrieveUpdateDeleteTimerView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Timer.objects.all()
    serializer_class = TimerSerializer


class ListTimerView(generics.ListAPIView):
    queryset = Timer.objects.all()
    serializer_class = TimerSerializer


class RetrieveEndDateView(generics.GenericAPIView):
    def get(self, request, pk, *args, **kwargs):
        timer = get_object_or_404(Timer, pk=pk)

        # Extract year, month, and day from end_date
        end_date = timer.end_date
        response_data = {
            "year": end_date.year,
            "month": end_date.month,
            "day": end_date.day
        }

        return Response(response_data, status=status.HTTP_200_OK)
    

import logging

logger = logging.getLogger(__name__)

class ApplyReferralCodeView(APIView):
    def post(self, request, user_id, *args, **kwargs):
        try:
            user = get_object_or_404(User, id=user_id)
            serializer = ApplyReferralCodeSerializer(data=request.data, context={'user': user})
            
            if serializer.is_valid():
                serializer.apply_referral_code(user)
                return Response({"status": "Referral code applied successfully."}, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error applying referral code: {e}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)