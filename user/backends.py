from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

class ActiveStudentBackend(ModelBackend):
    def user_can_authenticate(self, user):
        # Gọi check mặc định (is_active = True)
        is_auth = super().user_can_authenticate(user)
        if not is_auth:
            return False

        # Nếu là SV -> check status
        if hasattr(user, "sv"):
            return user.sv.status == "A"

        return True
