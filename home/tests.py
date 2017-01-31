from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group

from home.forms import UserRegistrationForm


setup_test_environment()
client = Client()


class IndexViewTests(TestCase):
    fixtures = [
        'regions.xml',
        'cities.xml',
        'library_kinds.xml',
        'library_types.xml'
    ]

    def test_index_view(self):
        """Тест индексной страницы."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Вход на сайт")
        self.assertContains(response, "Регистрация")


class UserRegistrationTests(TestCase):
    """Класс для тестирования функционала регистрации читателя."""

    fixtures = [
        'regions.xml',
        'cities.xml',
        'library_kinds.xml',
        'library_types.xml',
        'users.xml',
        'groups'
    ]

    def test_form_validation(self):
        """Тест валидации формы регистрации читателя."""
        form_data = {
            'first_name': '',
            'last_name': '',
            'region': '',
            'city': '',
            'login': '',
            'email': '',
            'password': '',
            'password_confirm': '',
        }
        form = UserRegistrationForm(data=form_data, region=form_data['region'])
        # Тест с пустыми данными
        self.assertFalse(form.is_valid())
        self.assertIn("Обязательное поле.", form['first_name'].errors)
        self.assertIn("Обязательное поле.", form['last_name'].errors)
        self.assertIn("Обязательное поле.", form['region'].errors)
        self.assertIn("Обязательное поле.", form['city'].errors)
        self.assertIn("Обязательное поле.", form['login'].errors)
        self.assertIn("Обязательное поле.", form['email'].errors)
        self.assertIn("Обязательное поле.", form['password'].errors)
        self.assertIn("Обязательное поле.", form['password_confirm'].errors)

        # Тест длины логина
        form_data['login'] = 'l'
        form = UserRegistrationForm(data=form_data, region=form_data['region'])
        self.assertIn("Убедитесь, что это значение содержит не менее 3 символов (сейчас 1).", form['login'].errors)

        # Тест длины логина
        form_data['login'] = 'l'*101
        form = UserRegistrationForm(data=form_data, region=form_data['region'])
        self.assertIn("Убедитесь, что это значение содержит не более 100 символов (сейчас 101).", form['login'].errors)

        # Тест уникальности логина
        form_data['login'] = 'admin'
        form = UserRegistrationForm(data=form_data, region=form_data['region'])
        self.assertIn("Логин \"admin\" уже используется.", form['login'].errors)

        # Тест длины пароля
        form_data['password'] = 'p'
        form = UserRegistrationForm(data=form_data, region=form_data['region'])
        self.assertIn("Убедитесь, что это значение содержит не менее 5 символов (сейчас 1).", form['password'].errors)

        # Тест совпадения пароля
        form_data['password'] = 'password1'
        form_data['password_confirm'] = 'password2'
        form = UserRegistrationForm(data=form_data, region=form_data['region'])
        self.assertIn("Пароли не совпадают.", form['password_confirm'].errors)

        # Правильные данные
        form_data = {
            'first_name': 'Test',
            'last_name': 'Test',
            'region': 1,
            'city': 1,
            'login': 'test_test',
            'email': 'test@test.com',
            'password': 'test_test',
            'password_confirm': 'test_test',
        }
        form = UserRegistrationForm(data=form_data, region=form_data['region'])
        self.assertTrue(form.is_valid())

    def test_registration(self):
        """Тест процедуры регистрации."""
        form_data = {
            'first_name': 'Test',
            'last_name': 'Test',
            'region': 1,
            'city': 1,
            'login': 'test_test',
            'email': 'test@test.com',
            'password': 'test_test',
            'password_confirm': 'test_test',
        }

        response = client.post(reverse('user_register'), form_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Проверка создался ли юзер в БД
        created_user = User.objects.filter(username=form_data['login']).first()
        self.assertTrue(created_user)

        # Проверка в группе читателей ли юзер
        self.assertTrue(created_user.groups.filter(name='Читатели').exists())

