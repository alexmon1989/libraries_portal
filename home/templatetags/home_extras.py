from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def settings_value(name):
    """Получает значение конфиг. переменной. Для использования из шаблона."""
    return getattr(settings, name, "")
