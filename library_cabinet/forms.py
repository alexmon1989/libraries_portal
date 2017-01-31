from django import forms
from django.forms import ModelForm, Textarea
from django.contrib.auth.models import User, Group
from documents.models import Document
from home.models import City, Region, LibraryKind, LibraryType, Library


class DocumentForm(ModelForm):
    """Форма создания/редактирования документа."""
    class Meta:
        model = Document
        fields = ('title',
                  'document_type',
                  'catalog_number',
                  'author',
                  'another_persons',
                  'language',
                  'notes',
                  'rubrics')
        help_texts = {
            'another_persons': '<a href="#" data-toggle="modal" data-target="#add-another-person-modal">Добавить</a>',
            'rubrics': '<a href="#" data-toggle="modal" data-target="#add-rubric-modal">Добавить</a>',
        }
        widgets = {'notes': Textarea(attrs={'rows': 3})}


class TimeLimitsForm(forms.Form):
    """Форма редактирования регламента."""
    reservation_recommended_time = forms.IntegerField(label='Рекомендуемое время бронирования книги, дн.',
                                                      required=True)
    return_time_delay_max = forms.IntegerField(label='Максимальное время просрочки возврата документа, дн.',
                                               required=True)


class UserSettingsForm(forms.Form):
    """Форма настроек пользователя."""
    email = forms.EmailField(label='E-Mail', max_length=100, required=True)
    password = forms.CharField(label='Новый пароль', min_length=5, max_length=100, widget=forms.PasswordInput(),
                               required=False)
    password_confirm = forms.CharField(label='Подтверждение пароля', max_length=100, widget=forms.PasswordInput(),
                                       required=False)

    def clean(self):
        cleaned_data = super(UserSettingsForm, self).clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            msg = "Пароли не совпадают."
            self.add_error('password_confirm', msg)


class LibrarySettingsForm(forms.Form):
    """Форма настроек библиотеки."""
    title = forms.CharField(label='Названиие', max_length=255, required=True)
    region = forms.ChoiceField(label='Регион', required=True)
    city = forms.ChoiceField(label='Населенный пункт', required=True)
    address = forms.CharField(label='Адрес', max_length=255, required=True)
    library_type = forms.ChoiceField(label='Тип библиотеки',
                                     required=True)
    library_kind = forms.ChoiceField(label='Вид библиотеки', required=True)
    legal_entity_name = forms.CharField(label='Наименование юридического лица', max_length=255, required=False)
    legal_entity_address = forms.CharField(label='Адрес (место нахождения) юридического лица',
                                           max_length=255,
                                           required=False)
    bin = forms.CharField(label='ОГРН', max_length=255, required=False)
    inn = forms.CharField(label='ИНН', max_length=255, required=False)
    crr = forms.CharField(label='КПП', max_length=255, required=False)
    contact_info = forms.CharField(label='Контактная информация', max_length=255, required=False)
    about = forms.CharField(label='О нас', max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        region_id = kwargs.pop('region', None)
        city_id = kwargs.pop('city', None)
        library_type_id = kwargs.pop('library_type', None)
        library_kind_id = kwargs.pop('library_kind', None)
        library = kwargs.pop('library', None)
        self.base_fields['region'].choices = [(x.id, x.title) for x in Region.objects.order_by('title')]
        self.base_fields['region'].initial = library.city.region_id
        if not region_id:
            self.base_fields['city'].choices = [(x.id, x.title)
                                                for x in City.objects.order_by('title')
                                                    .filter(region_id=library.city.region_id)]
            self.base_fields['city'].initial = library.city.id
        else:
            self.base_fields['city'].choices = [(x.id, x.title)
                                                for x in City.objects.order_by('title').filter(region_id=region_id)]
            self.base_fields['city'].initial = city_id

        self.base_fields['library_type'].choices = [(x.id, x.title) for x in LibraryType.objects.order_by('title')]
        self.base_fields['library_type'].initial = library.library_type_id
        if not library_type_id:
            self.base_fields['library_kind'].choices = [(x.id, x.title)
                                                        for x in LibraryKind.objects.order_by('title')
                                                            .filter(librarytype=library.library_type_id)]
            self.base_fields['library_kind'].initial = library.library_kind_id
        else:
            self.base_fields['library_kind'].choices = [(x.id, x.title)
                                                        for x in LibraryKind.objects.order_by('title')
                                                            .filter(librarytype=library_type_id)]
            self.base_fields['library_kind'].initial = library_kind_id

        super(LibrarySettingsForm, self).__init__(*args, **kwargs)


class LibraryUserForm(forms.Form):
    """Форма для создания/редактирования сотрудника библиотеки."""
    username = forms.CharField(label='Логин', min_length=3, max_length=100, required=True)
    last_name = forms.CharField(label='Фамилия', max_length=255, required=True)
    first_name = forms.CharField(label='Имя, отчество', max_length=255, required=True)
    email = forms.EmailField(label='E-Mail', max_length=100, required=True)
    group = forms.ChoiceField(label='Группа',
                              required=True,
                              choices=(
                                  (2, 'Библиотекари-администраторы'),
                                  (3, 'Библиотекари-комплектаторы'),
                                  (4, 'Библиотекари-каталогизаторы'),
                              ))
    password = forms.CharField(label='Пароль',
                               min_length=5,
                               max_length=100,
                               widget=forms.PasswordInput(),
                               required=False,
                               help_text='Если не хотите менять пароль, оставьте это и следующее поля пустыми.')
    password_confirm = forms.CharField(label='Подтверждение пароля', max_length=100, widget=forms.PasswordInput(),
                                       required=False)

    def clean(self):
        cleaned_data = super(LibraryUserForm, self).clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            msg = "Пароли не совпадают."
            self.add_error('password_confirm', msg)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Логин "{}" уже используется.'.format(username))
        return username


class ReportLibraryFundForm(forms.Form):
    """Форма для формирования отчёта Библиотечный фонд."""
    user = forms.MultipleChoiceField(label='Сотрудник',
                                     required=True)
    date_from = forms.CharField(label='Дата от', required=True)
    date_to = forms.CharField(label='Дата до', required=True)
    format = forms.ChoiceField(label='Формат отчёта',
                               widget=forms.RadioSelect,
                               choices=(('xls', '.XLS'), ('doc', '.DOC'), ('pdf', '.PDF'), ('ods', '.ODS')),
                               initial='xls',
                               required=False)

    def __init__(self, *args, **kwargs):
        library = kwargs.pop('library')
        self.base_fields['user'].choices = [(x.id, x) for x in library.admins.all()]
        self.base_fields['user'].help_text = '<a href="#" id="select-all-users">Выбрать всех</a>'
        super(ReportLibraryFundForm, self).__init__(*args, **kwargs)


class ReportOrdersForm(forms.Form):
    """Форма для формирования отчёта Заказы читателей."""
    reader = forms.MultipleChoiceField(label='Читатель',
                                       required=True)
    date_from = forms.CharField(label='Дата от', required=True)
    date_to = forms.CharField(label='Дата до', required=True)
    status = forms.MultipleChoiceField(label='Статус заказа',
                                       choices=(('1', 'Забронирован'), ('2', 'Выдан'), ('3', 'Возвращён')),
                                       required=False)
    format = forms.ChoiceField(label='Формат отчёта',
                               widget=forms.RadioSelect,
                               choices=(('xls', '.XLS'), ('doc', '.DOC'), ('pdf', '.PDF'), ('ods', '.ODS')),
                               initial='xls',
                               required=False)

    def __init__(self, *args, **kwargs):
        library = kwargs.pop('library')
        self.base_fields['reader'].choices = [(x.id, x) for x in library.get_readers()]
        self.base_fields['reader'].help_text = '<a href="#" id="select-all-readers">Выбрать всех</a>'
        self.base_fields['status'].help_text = '<a href="#" id="select-all-statuses">Выбрать все</a>'
        super(ReportOrdersForm, self).__init__(*args, **kwargs)


class ReportStaffForm(forms.Form):
    """Форма для формирования отчёта Персонал библиотеки."""
    user = forms.MultipleChoiceField(label='Сотрудник',
                                     required=True)
    date_from = forms.CharField(label='Дата от', required=True)
    date_to = forms.CharField(label='Дата до', required=True)
    format = forms.ChoiceField(label='Формат отчёта',
                               widget=forms.RadioSelect,
                               choices=(('xls', '.XLS'), ('doc', '.DOC'), ('pdf', '.PDF'), ('ods', '.ODS')),
                               initial='xls',
                               required=False)

    def __init__(self, *args, **kwargs):
        library = kwargs.pop('library')
        self.base_fields['user'].choices = [(x.id, x) for x in library.admins.all()]
        self.base_fields['user'].help_text = '<a href="#" id="select-all-users">Выбрать всех</a>'
        super(ReportStaffForm, self).__init__(*args, **kwargs)


class EnteredDocumentsForm(forms.Form):
    """Форма для формирования отчёта Внесенные документы."""
    date_from = forms.CharField(label='Дата от', required=True)
    date_to = forms.CharField(label='Дата до', required=True)
    format = forms.ChoiceField(label='Формат отчёта',
                               widget=forms.RadioSelect,
                               choices=(('xls', '.XLS'), ('doc', '.DOC'), ('pdf', '.PDF'), ('ods', '.ODS')),
                               initial='xls',
                               required=False)
