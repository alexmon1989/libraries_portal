from django import forms
from home.models import Region, City, Library


class ReaderTicketForm(forms.Form):
    """Форма редактирования читатальского билета."""
    last_name = forms.CharField(label='Фамилия', max_length=255, required=True)
    first_name = forms.CharField(label='Имя, отчество', max_length=255, required=True)
    region = forms.ChoiceField(label='Регион', required=True)
    city = forms.ChoiceField(label='Населенный пункт', required=True)
    address = forms.CharField(label='Адрес', max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        """Иницализирует форму."""
        region_id = kwargs.pop('region', None)
        user = kwargs.pop('user', None)
        self.base_fields['region'].choices = [(x.id, x.title) for x in Region.objects.order_by('title')]
        if region_id:
            self.base_fields['city'].choices = [(x.id, x.title)
                                                for x in City.objects.all().filter(region_id=region_id)]
        else:
            self.base_fields['city'].choices = [(x.id, x.title)
                                                for x in City.objects.all().filter(
                    region_id=City.objects.filter(pk=user.profile.city_id).get().region_id
                )]
            self.base_fields['city'].initial = user.profile.city_id
        super(ReaderTicketForm, self).__init__(*args, **kwargs)


class SimpleSearchForm(forms.Form):
    """Форма простого поиска."""
    query = forms.CharField(label='Название содержит', min_length=3, max_length=255, required=True)


class ExtendedSearchForm(forms.Form):
    """Форма расширенного поиска."""
    title = forms.CharField(label='Название содержит', min_length=3, max_length=255, required=True)
    region = forms.ChoiceField(label='Регион', required=False)
    city = forms.ChoiceField(label='Населенный пункт', required=False)
    library = forms.ChoiceField(label='Бибилиотека', required=False)

    def __init__(self, *args, **kwargs):
        """Иницализирует форму."""
        region_id = kwargs.pop('region', None)
        city_id = kwargs.pop('city', None)
        user = kwargs.pop('user', None)
        self.base_fields['region'].choices = [(x.id, x.title) for x in Region.objects.order_by('title')]
        self.base_fields['region'].initial = user.profile.city.region_id
        if region_id:
            self.base_fields['city'].choices = [(x.id, x.title)
                                                for x in City.objects.all().filter(region_id=region_id)]
        else:
            self.base_fields['city'].choices = [(x.id, x.title)
                                                for x in City.objects.all().filter(
                    region_id=City.objects.filter(pk=user.profile.city_id).get().region_id
                )]
            self.base_fields['city'].initial = user.profile.city_id
        if city_id:
            self.base_fields['library'].choices = [(x.id, x.title)
                                                   for x in Library.objects.all().filter(city_id=city_id)]
        else:
            self.base_fields['library'].choices = [(x.id, x.title)
                                                   for x in Library.objects.all().filter(city_id=user.profile.city_id)]
        super(ExtendedSearchForm, self).__init__(*args, **kwargs)


class SettingsForm(forms.Form):
    """Форма настроек."""
    email = forms.EmailField(label='E-Mail', max_length=100, required=True)
    password = forms.CharField(label='Новый пароль', min_length=5, max_length=100, widget=forms.PasswordInput(),
                               required=False)
    password_confirm = forms.CharField(label='Подтверждение пароля', max_length=100, widget=forms.PasswordInput(),
                                       required=False)

    def clean(self):
        cleaned_data = super(SettingsForm, self).clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            msg = "Пароли не совпадают."
            self.add_error('password_confirm', msg)


class CommentForm(forms.Form):
    """Форма добавления комментария."""
    text = forms.CharField(label='Текст отзыва', widget=forms.Textarea(attrs={'rows': 2}))
