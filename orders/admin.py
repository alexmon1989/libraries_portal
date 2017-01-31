from django.contrib import admin
from .models import Order, OrderAction, OrderStatus


class OrderActionsInline(admin.StackedInline):
    model = OrderAction
    can_delete = True
    verbose_name_plural = 'Действия по заказу'
    verbose_name = 'Действие по заказу'


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderActionsInline]

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderStatus)
