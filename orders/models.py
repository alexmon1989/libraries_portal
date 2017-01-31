from django.db import models
from documents.models import Document
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone


class OrderStatus(models.Model):
    """Модель статусов заказа."""
    title = models.CharField('Название', max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Статус заказа'
        verbose_name_plural = 'Статусы заказов'


class Order(models.Model):
    """Модель для заказов."""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, verbose_name='Документ')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь (читатель)')
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, verbose_name='Статус заказа', default=1)
    approved = models.BooleanField('Одобрено', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.document.title

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def get_recommended_return_date(self):
        """Возвращает дату, когда надо вернуть документ."""
        if self.status.title == 'Выдан':
            action = self.orderaction_set.filter(status__title='Выдан').first()
            return action.action_date + timedelta(self.document.library.reservation_recommended_time)
        else:
            return None

    def get_max_return_date(self):
        """Возвращает дату, когда надо вернуть документ."""
        if self.status.title == 'Выдан':
            action = self.orderaction_set.filter(status__title='Выдан').first()
            return action.action_date \
                   + timedelta(self.document.library.reservation_recommended_time) \
                   + timedelta(self.document.library.return_time_delay_max)
        else:
            return None

    def is_overdue(self):
        """Вышло ли рекомендованное время возврата."""
        if self.status.title == 'Выдан':
            if self.get_recommended_return_date() < timezone.now():
                return True
        return False


class OrderAction(models.Model):
    """Модель для действий по заказов."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, verbose_name='Статус заказа', default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь (библиотекарь)')
    action_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.status.title

    class Meta:
        verbose_name = 'Деёствие по заказу'
        verbose_name_plural = 'Действия по заказам'
