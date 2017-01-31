import datetime

from django import template
from django.db.models import Q

from library_cabinet.views import get_my_library
from orders.models import Order
from comments.models import Comment

register = template.Library()


@register.simple_tag
def current_time(format_string):
    return datetime.datetime.now().strftime(format_string)


@register.simple_tag
def get_new_orders_count(request):
    return Order.objects.filter(
        document__library=get_my_library(request),
        status__title='Забронирован'
    ).count()


@register.simple_tag
def get_issued_orders_count(request):
    return Order.objects.filter(
        document__library=get_my_library(request),
        status__title='Выдан'
    ).count()


@register.simple_tag
def get_requests_count(request):
    library = get_my_library(request)
    return library.libraryrequestaccess_set.filter(approved=False).count()


@register.simple_tag
def get_unmoderated_comments_count(request):
    library = get_my_library(request)
    return Comment.objects.filter(
        Q(moderated=False),
        Q(library=library) | Q(document__in=library.document_set.all())
    ).count()
