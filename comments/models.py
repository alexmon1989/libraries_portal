from django.db import models
from django.contrib.auth.models import User


class Comment(models.Model):
    """Модель для комментариев."""
    text = models.TextField('Текст комментария')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    moderated = models.BooleanField('Промодерирован', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        text = self.text
        if len(text) > 100:
            text = text[:100] + '...'
        return text

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
