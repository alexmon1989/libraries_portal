from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from reader_cabinet.models import ReaderTicket
from comments.models import Comment


class LibraryKind(models.Model):
    """Модель для видов библиотек"""
    title = models.CharField('Название', max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Вид библиотеки'
        verbose_name_plural = 'Виды библиотек'


class LibraryType(models.Model):
    """Модель для типов библиотек"""
    title = models.CharField('Название', max_length=255)
    kinds = models.ManyToManyField(LibraryKind, verbose_name="Виды библиотек")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Тип библиотеки'
        verbose_name_plural = 'Типы библиотек'


class Region(models.Model):
    """Модель для регионов"""
    title = models.CharField('Название', max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'


class City(models.Model):
    """Модель для городов"""
    title = models.CharField('Название', max_length=255)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name="Регион")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class Library(models.Model):
    """Модель для библиотек"""
    title = models.CharField('Название', max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="Город")
    address = models.CharField('Адрес', max_length=255)
    contact_info = models.CharField('Контактная информация', max_length=255, blank=True)
    about = models.CharField('О нас', max_length=255, blank=True)
    library_kind = models.ForeignKey(LibraryKind, on_delete=models.CASCADE, verbose_name="Вид библиотеки")
    library_type = models.ForeignKey(LibraryType, on_delete=models.CASCADE, verbose_name="Тип библиотеки")
    legal_entity_name = models.CharField('Наименование юридического лица', max_length=255, blank=True)
    legal_entity_address = models.CharField('Адрес (место нахождения) юридического лица', max_length=255, blank=True)
    bin = models.CharField('ОГРН', max_length=255, blank=True)
    inn = models.CharField('ИНН', max_length=255, blank=True)
    crr = models.CharField('КПП', max_length=255, blank=True)
    reservation_recommended_time = models.IntegerField('Рекомендуемое время бронирования книги, дн.',
                                                       blank=True, null=True)
    return_time_delay_max = models.IntegerField('Максимальное время просрочки возврата документа, дн.',
                                                blank=True, null=True)
    reader_tickets = models.ManyToManyField(ReaderTicket, verbose_name="Читатели библиотеки", blank=True)
    admins = models.ManyToManyField(User, verbose_name="Администраторы", blank=True)
    comments = models.ManyToManyField(Comment, verbose_name="Комментарии", blank=True)
    enabled = models.BooleanField('Включено', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Библиотека'
        verbose_name_plural = 'Библиотеки'

    def get_moderated_comments(self):
        """Возвращает промодерированные комментарии к библиотеке."""
        return self.comments.filter(moderated=True).order_by("-created_at")

    def get_readers(self):
        """Возвращает читателей библиотеки (город + отдельно зарегистрированные)."""
        return User.objects.filter(Q(groups__name__exact='Читатели'),
                                   Q(profile__city_id=self.city_id) | Q(readerticket__in=self.reader_tickets.all()))


def library_directory_path(instance, filename):
    return 'library_{0}/{1}'.format(instance.library.id, filename)


class LibraryDocument(models.Model):
    """Модель для документов библиотек (нормативные, планы, отчёты и т.д.)"""
    title = models.CharField('Название', max_length=255)
    library = models.ForeignKey(Library, on_delete=models.CASCADE, verbose_name="Библиотека")
    upload = models.FileField(upload_to=library_directory_path, verbose_name="Файл")

    def __str__(self):
        return self.title


class LibraryRequestAccess(models.Model):
    """Модель для запросов читателей на доступ к библиотеке"""
    library = models.ForeignKey(Library, on_delete=models.CASCADE, verbose_name="Библиотека")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="user")
    approved = models.BooleanField(verbose_name="Утверждено", default=False)
    approved_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE,
                                    verbose_name="Кем одобрено",
                                    null=True,
                                    blank=True,
                                    related_name="user_approved_by")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0} ({1} {2})'.format(self.user.username, self.user.last_name, self.user.first_name)

    class Meta:
        verbose_name = 'Заявка на получение доступа'
        verbose_name_plural = 'Заявки на получение доступа'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="Город", blank=True, null=True)
    address = models.CharField('Адрес', max_length=255, null=True, blank=True)
    dnevnik_id = models.IntegerField('id в Дневник.ру', blank=True, null=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.get_or_create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def save(self, *args, **kwargs):
        if not self.pk:
            try:
                p = Profile.objects.get(user=self.user)
                self.pk = p.pk
            except Profile.DoesNotExist:
                pass

        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username

    def has_access_to_library(self, library_id):
        """Проверяет имеет ли пользователь доступ к конкретной библиотеке."""
        library = Library.objects.get(pk=library_id)
        if self.city_id == library.city_id or self.user.readerticket in library.reader_tickets.all():
            return True
        return False

    def get_issued_orders(self):
        """Возвращает количество выданных заказов."""
        return self.user.orderaction_set.filter(status_id=2).count()

    def get_passed_orders(self):
        """Возвращает количество принятых заказов."""
        return self.user.orderaction_set.filter(status_id=3).count()

    def get_approved_request_accesses(self):
        """Возвращает количество одобренных заказов на вступление в библиотеку."""
        return self.user.user_approved_by.filter(approved=True).count()


def get_login_and_name(self):
    """Возвращает отформатированную строку с логином и именем пользователя."""
    return '{0} ({1} {2})'.format(self.username, self.last_name, self.first_name)

# Переопределение метода __str__ класса User
User.add_to_class("__str__", get_login_and_name)
