from django.contrib.auth.backends import ModelBackend
from .models import User

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        try:
            if email:
                user = User.objects.get(email=email)
            else:
                user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None
