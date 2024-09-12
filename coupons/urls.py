from django.urls import path
from .views import *



urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('referrals/', ReferralListView.as_view(), name='referral_list'),
    path('login/', UserLoginView, name='login'),

    path('user/update/<int:id>/', UserUpdateView.as_view(), name='user_update'),
    path('user/<int:id>/', GetUserByIdView.as_view(), name='get_user_by_id'),
    path('total_users/', TotalUsersView.as_view(), name='total_users'),
    path('create_coupon/<int:user_id>/', CreateCouponView.as_view(), name='create_coupon'),
    path('complete_purchase/<int:user_id>/<int:order_id>/', CompletePurchaseView.as_view(), name='complete_purchase'),

    path('complete_payment/<int:user_id>/<int:order_id>/', CompletePaymentView.as_view(), name='complete_payment'),
    path('my_coupons/', UserCouponsView.as_view(), name='my_coupons'),
    path('user_coupons/<int:user_id>/', UserCouponsByIDView.as_view(), name='user_coupons'),
    path('gallery/', GalleryListCreateView.as_view(), name='gallery_list_create'),
    path('gallery/<int:pk>/', GalleryDetailView.as_view(), name='gallery_detail'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('coupons/', CouponListView.as_view(), name='coupon_list'),
    path('coupons-total/', TotalCouponsView.as_view(), name='total_coupons'),
    path('generate_payment_link/<int:quantity>/', generate_payment_link, name='generate_payment_link'),
    path('razorpay/webhook/', RazorpayWebhookView.as_view(), name='razorpay_webhook'),
    path('random_coupon/', PickRandomCouponView.as_view(), name='random_coupon'),
    path('total_amount_generated/', TotalAmountGeneratedView.as_view(), name='total_amount_generated'),
    path('winner/', WinningUsersView.as_view(), name='winning_users'),
    path('adminlogin/', AdminLoginView.as_view(), name='admin-login'),
    path('all-users-wallet/', AllUsersWalletView.as_view(), name='all-users-wallet'),
    path('user-wallet/<int:pk>/', UserWalletView.as_view(), name='user-wallet'),
    path('user/<int:user_id>/referrals/', UserReferralsView.as_view(), name='user-referrals'),
    path('users/referral-count/', UserReferralCountView.as_view(), name='user-referral-count'),
    path('users/referral-details/', UserReferralDetailView.as_view(), name='user-referral-details'),
    path('withdraw_coupon/<int:user_id>/', WithdrawCouponView.as_view(), name='withdraw_coupon'),
    path('reset_wallet_balance/<int:user_id>/', ResetWalletBalanceView.as_view(), name='reset_wallet_balance'),
    path('delete_all_orders/', DeleteAllOrdersView.as_view(), name='delete_all_orders'),
    path('delete_all_coupons/', DeleteAllCouponsView.as_view(), name='delete_all_coupons'),
    path('add_coupon_amount/', AddCouponAmountView.as_view(), name='add_coupon_amount'),
    path('edit_coupon_amount/<int:pk>/', EditCouponAmountView.as_view(), name='edit_coupon_amount'),
    path('delete_coupon_amount/<int:pk>/', DeleteCouponAmountView.as_view(), name='delete_coupon_amount'),
    path('carousel/', CarouselView.as_view(), name='carousel'),

  # Product routes
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDeleteView.as_view(), name='product-retrieve-update-delete'),

    # ProductImage routes
    path('product-images/', ProductImageListCreateView.as_view(), name='product-image-list-create'),
    path('product-images/<int:pk>/', ProductImageRetrieveUpdateDeleteView.as_view(), name='product-image-retrieve-update-delete'),

    #Timer
    path('timer-create/', CreateTimerView.as_view(), name='create-timer'),
    path('alltimers/', ListTimerView.as_view(), name='list-timers'),
    path('timer-edit-del-up-ret/<int:pk>/', RetrieveUpdateDeleteTimerView.as_view(), name='retrieve-update-delete-timer'),
    path('end-date/<int:pk>/', RetrieveEndDateView.as_view(), name='retrieve-end-date'),

    path('apply-referral-code/<int:user_id>/', ApplyReferralCodeView.as_view(), name='apply_referral_code'),





]
