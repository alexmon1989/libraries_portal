from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save

from home.models import User


class ReaderTicket(models.Model):
    """Модель читательского билета."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @receiver(post_save, sender=User)
    def create_reader_ticket(sender, instance, created, **kwargs):
        if created:
            ReaderTicket.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_reader_ticket(sender, instance, **kwargs):
        instance.readerticket.save()

    def __str__(self):
        """Возвращает строковое представление объекта модели."""
        return '{0} ({1} {2})'.format(self.user.username, self.user.last_name, self.user.first_name)
