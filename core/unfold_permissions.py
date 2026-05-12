def is_superuser(request) -> bool:
    user = getattr(request, 'user', None)
    return bool(user and user.is_authenticated and user.is_active and user.is_superuser)


def can_access_admissions(request) -> bool:
    user = getattr(request, 'user', None)
    return bool(user and user.is_authenticated and user.is_active and user.is_staff)
