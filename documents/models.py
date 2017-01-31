from django.db import models
from django.contrib.auth.models import User
from home.models import Library
from comments.models import Comment


class Rubric(models.Model):
    """Модель для рубрик."""
    title = models.CharField('Название', max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Рубрика'
        verbose_name_plural = 'Рубрики'


class AnotherPerson(models.Model):
    """Модель для других персон."""
    title = models.CharField('Имя', max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Другая персоны'
        verbose_name_plural = 'Другие персоны'


class DocumentType(models.Model):
    """Модель для типов документов."""
    title = models.CharField('Название', max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Тип документа'
        verbose_name_plural = 'Типы документов'


class DocumentStatus(models.Model):
    """Модель для статусов документов (досутупен/недоступен)."""
    title = models.CharField('Название', max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Статус документа'
        verbose_name_plural = 'Статусы документов'


class Document(models.Model):
    """Модель для документов."""
    title = models.CharField('Название', max_length=255)
    catalog_number = models.CharField('Шифр хранения (№ в каталоге)', max_length=255)
    library = models.ForeignKey(Library, on_delete=models.CASCADE, verbose_name="Библиотека", blank=True, null=True)
    author = models.CharField('Автор', max_length=255)
    language = models.CharField('Язык', max_length=255)
    notes = models.TextField('Примечания')
    utilized = models.BooleanField('Списано', default=False)
    document_type = models.ForeignKey(DocumentType,
                                      on_delete=models.CASCADE,
                                      verbose_name="Тип документа",
                                      blank=True,
                                      null=True)
    document_status = models.ForeignKey(DocumentStatus, on_delete=models.CASCADE, verbose_name="Статус документа")
    rubrics = models.ManyToManyField(Rubric, verbose_name="Рубрики", blank=True)
    another_persons = models.ManyToManyField(AnotherPerson, verbose_name="Другие персоны", blank=True)
    comments = models.ManyToManyField(Comment, verbose_name="Комментарии", blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Кем создано")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '"{0}" - {1}'.format(self.title, self.author)

    def get_moderated_comments(self):
        """Возвращает промодерированные комментарии к документу."""
        return self.comments.filter(moderated=True).order_by("-created_at")

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
