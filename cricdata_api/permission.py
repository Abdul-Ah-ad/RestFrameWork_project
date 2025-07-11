from rest_framework.permissions import AllowAny, IsAdminUser


class AdminPostPermissionMixin:
    """
    Mixin that allows only admins to perform POST requests,
    and allows any user for safe methods like GET.
    """

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]

