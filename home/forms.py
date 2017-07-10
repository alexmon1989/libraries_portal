from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from .models import LibraryType, LibraryKind, Region, City


class AuthForm(forms.Form):
    """Форма авторизации"""
    login = forms.CharField(label='Логин', max_length=100, required=True)
    password = forms.CharField(label='Пароль', max_length=100, widget=forms.PasswordInput(), required=True)
    remember_me = forms.BooleanField(label='Запомнить меня', required=False)

    def clean_remember_me(self):
        """clean method for remember_me """
        remember_me = self.cleaned_data.get('remember_me')
        if not remember_me:
            settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True
        else:
            settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
        return remember_me


class UserRegistrationForm(forms.Form):
    """Форма регистрации читателя"""
    first_name = forms.CharField(label='Имя, Отчество', max_length=255, required=True)
    last_name = forms.CharField(label='Фамилия', max_length=255, required=True)
    region = forms.ChoiceField(label='Регион', required=True)
    city = forms.ChoiceField(label='Населенный пункт', required=True)
    login = forms.CharField(label='Логин', min_length=3, max_length=100, required=True)
    email = forms.EmailField(label='E-Mail', max_length=100, required=True)
    password = forms.CharField(label='Пароль', min_length=5, max_length=100, widget=forms.PasswordInput(),
                               required=True)
    password_confirm = forms.CharField(label='Подтверждение пароля', max_length=100,
                                       widget=forms.PasswordInput(), required=True)

    def __init__(self, *args, **kwargs):
        region_id = kwargs.pop('region', None)
        city_id = kwargs.pop('city', None)
        self.base_fields['region'].choices = [(x.id, x.title) for x in Region.objects.order_by('title')]
        if region_id:
            self.base_fields['city'].choices = [(x.id, x.title)
                                                for x in City.objects.order_by('title').filter(region_id=region_id)]
            self.base_fields['city'].default = city_id
        else:
            self.base_fields['city'].choices = [(x.id, x.title)
                                                for x in City.objects.order_by('title')
                                                    .filter(region_id=self.base_fields['region'].choices[0][0])]
        super(UserRegistrationForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(UserRegistrationForm, self).clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            msg = "Пароли не совпадают."
            self.add_error('password_confirm', msg)

    def clean_login(self):
        username = self.cleaned_data['login']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Логин "{}" уже используется.'.format(username))
        return username


class LibraryRegistrationForm(forms.Form):
    """Форма регистрации библиотеки"""
    first_name = forms.CharField(label='Имя, Отчество (администратора)', max_length=255, required=True)
    last_name = forms.CharField(label='Фамилия (администратора)', max_length=255, required=True)
    login = forms.CharField(label='Логин', min_length=3, max_length=100, required=True)
    email = forms.EmailField(label='E-Mail', max_length=100, required=True)
    password = forms.CharField(label='Пароль', min_length=5, max_length=100, widget=forms.PasswordInput(),
                               required=True)
    password_confirm = forms.CharField(label='Подтверждение пароля', max_length=100,
                                       widget=forms.PasswordInput(), required=True)
    region = forms.ChoiceField(label='Регион', required=True)
    city = forms.ChoiceField(label='Населенный пункт', required=True)
    address = forms.CharField(label='Адрес библиотеки', max_length=255, required=True)
    title = forms.CharField(label='Название библиотеки', max_length=255, required=True)
    library_type = forms.ChoiceField(label='Тип библиотеки',
                                     required=True)
    library_kind = forms.ChoiceField(label='Вид библиотеки', required=True)

    def __init__(self, *args, **kwargs):
        region_id = kwargs.pop('region', None)
        city_id = kwargs.pop('city', None)
        library_type_id = kwargs.pop('library_type', None)
        library_kind_id = kwargs.pop('library_kind', None)
        self.base_fields['region'].choices = [(x.id, x.title) for x in Region.objects.order_by('title')]
        if region_id:
            self.base_fields['city'].choices = [(x.id, x.title)
                                                for x in City.objects.order_by('title').filter(region_id=region_id)]
            self.base_fields['city'].default = city_id
        else:
            self.base_fields['city'].choices = [(x.id, x.title)
                                                for x in City.objects.order_by('title')
                                                    .filter(region_id=self.base_fields['region'].choices[0][0])]
        self.base_fields['library_type'].choices = [(x.id, x.title) for x in LibraryType.objects.order_by('title')]
        if library_type_id:
            self.base_fields['library_kind'].choices = [(x.id, x.title)
                                                        for x in LibraryKind.objects.all()
                                                            .filter(librarytype=library_type_id).order_by('title')]
            self.base_fields['library_kind'].default = library_kind_id
        else:
            self.base_fields['library_kind'].choices = [(x.id, x.title)
                                                        for x in LibraryKind.objects.all()
                                                            .filter(librarytype=self.base_fields['library_type'].choices[0][0]).order_by('title')]
        super(LibraryRegistrationForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(LibraryRegistrationForm, self).clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            msg = "Пароли не совпадают."
            self.add_error('password_confirm', msg)

    def clean_login(self):
        username = self.cleaned_data['login']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Логин "{}" уже используется.'.format(username))
        return username
