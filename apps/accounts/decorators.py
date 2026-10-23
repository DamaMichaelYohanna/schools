from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied


def role_required(*allowed_roles):
    """
    Decorator for views that checks whether a user has one of the allowed roles.
    Superusers always pass.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, "Access denied: You do not have permission to access that resource.")
            return redirect('core:dashboard')
        return _wrapped_view
    return decorator


def principal_required(view_func):
    return role_required('PRINCIPAL', 'ADMIN')(view_func)


def teacher_required(view_func):
    return role_required('TEACHER', 'PRINCIPAL', 'ADMIN')(view_func)


def accountant_required(view_func):
    return role_required('ACCOUNTANT', 'PRINCIPAL', 'ADMIN')(view_func)


class RoleRequiredMixin(AccessMixin):
    """CBV Mixin to restrict views to designated roles."""
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.is_superuser or request.user.role in self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)

        messages.error(request, "Access denied: You do not have permission to access that page.")
        return redirect('core:dashboard')
