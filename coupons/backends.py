from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class MobileNumberNameBackend(BaseBackend):
    def authenticate(self, request, mobile_number=None, full_name=None):
        try:
            user = User.objects.get(mobile_number=mobile_number, full_name=full_name)
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
