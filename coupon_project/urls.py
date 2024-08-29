from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from coupons.views import razorpay_webhook  


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('coupons.urls')),
    path('razorpay/webhook/', razorpay_webhook, name='razorpay_webhook'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
