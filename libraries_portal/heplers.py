from django.contrib.auth.decorators import user_passes_test


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated():
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
            return False
    return user_passes_test(in_groups)


def library_enabled(*args, **kwargs):
    """Проверяет активирована ли библиотека."""
    def is_library_enabled(u):
        if u.is_authenticated():
            return u.library_set.all()[:1].get().enabled
    return user_passes_test(is_library_enabled)
