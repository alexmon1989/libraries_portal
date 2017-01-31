from django import template

register = template.Library()


@register.assignment_tag
def call_method(obj, method_name, *args):
    method = getattr(obj, method_name)
    return method(*args)
