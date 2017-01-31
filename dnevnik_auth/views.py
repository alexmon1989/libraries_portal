from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User, Group

import requests
import json
import random
import string
import csv

from home.models import City, Region


def import_cities(request):
    """Имортирует регионы и города из файла в БД."""
    with open('cities_regions.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';', quotechar='\n')
        csv_list = list(reader)

    # Импорт регионов
    for item in csv_list:
        Region.objects.get_or_create(title=item[3])

    # Импорт городов
    for item in csv_list:
        City.objects.get_or_create(title=item[0], region__title=item[3], defaults={
            'region_id': Region.objects.filter(title=item[3]).first().id
        })

    return HttpResponse('Импорт городов и библиотек успешно завершён!')


def index(request):
    """Проверяет есть ли юзер в системе (регистрирует его если нет) и переадресовывает в кабинет читателя."""
    # Если вернулась ошибка на этапе авторизации
    error_code = request.GET.get('error')
    error_msg = 'Ошибка при авторизации через Дневник.ру'
    if error_code:
        if error_code == 'access_denied':
            messages.add_message(request, messages.ERROR, '{}: отказано в доступе.'.format(error_msg))
        elif error_code == 'invalid_request':
            messages.add_message(request, messages.ERROR, '{}: неверный запрос.'.format(error_msg))
        elif error_code == 'unauthorized_client':
            messages.add_message(request, messages.ERROR, '{}: неверный идентификатор приложения.'.format(error_msg))
        elif error_code == 'invalid_scope':
            messages.add_message(request, messages.ERROR, '{}: неверный набор прав доступа.'.format(error_msg))
        else:
            messages.add_message(request, messages.ERROR, error_msg)
        return HttpResponseRedirect(reverse('index'))

    # Получение токена
    code = request.GET.get('code')
    if not code:
        messages.add_message(request, messages.ERROR, error_msg)
        return HttpResponseRedirect(reverse('index'))
    DNEVNIK_API_URL = getattr(settings, 'DNEVNIK_API_URL', '')
    headers = {
        'Content-Type': 'application/json',
    }
    r = requests.post('{}/authorizations'.format(DNEVNIK_API_URL),
                      headers=headers,
                      data=json.dumps({
                          'client_id': getattr(settings, 'DNEVNIK_CLIENT_ID', ''),
                          'code': code,
                          'client_secret': getattr(settings, 'DNEVNIK_SECRET_KEY', ''),
                          'grant_type': 'AuthorizationCode'
                      }))
    response_dict = json.loads(r.text)
    try:
        headers['Access-Token'] = response_dict['accessToken']
    except KeyError:
        messages.add_message(request, messages.ERROR, error_msg)
        return HttpResponseRedirect(reverse('index'))

    # Получение данных юзера
    r = requests.get('{}/users/me'.format(DNEVNIK_API_URL), headers=headers)
    user_data_dnevnik = json.loads(r.text)

    # Проверка есть ли юзер в системе
    user = User.objects.filter(profile__dnevnik_id=user_data_dnevnik['id'])
    if not user.exists():
        # Получение города юзера из дневник.ру
        r = requests.get('{}/users/me/schools'.format(DNEVNIK_API_URL), headers=headers)
        schools_ids = (r.text[1:len(r.text)-1].split(','))
        if len(schools_ids) == 0:
            messages.add_message(request, messages.ERROR,
                                 '{}: невозможно определить город пользователя.'.format(error_msg))
            return HttpResponseRedirect(reverse('index'))
        r = requests.get('{}/schools/{}'.format(DNEVNIK_API_URL, schools_ids[len(schools_ids)-1]), headers=headers)
        school_data = json.loads(r.text)
        region_title = school_data['municipality'].split(',')[1].strip()
        try:
            city = City.objects.get(
                title=school_data['city'],
                region__title=region_title
            )
        except City.DoesNotExist:
            region = Region.objects.get_or_create(title=region_title)
            city = City.objects.get_or_create(title=school_data['city'],
                                              region=region,
                                              defaults={'region_id': region.id})

        # Логин юзера. Проверка не занят ли логин. Если занят, то добавление суффикса dnevnik_ru.
        username = user_data_dnevnik['login']
        if User.objects.filter(username=username).exists():
            username = '{}_dnevnik_ru'.format(username)

        # Создание юзера
        user = User.objects.create_user(
            username,
            user_data_dnevnik['email'],
            ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10)),
            first_name='{} {}'.format(user_data_dnevnik['firstName'], user_data_dnevnik['middleName']),
            last_name=user_data_dnevnik['lastName']
        )
        user.profile.city = city
        user.profile.dnevnik_id = user_data_dnevnik['id']
        group = Group.objects.get(name='Читатели')
        user.groups.add(group)
        user.save()
    else:
        user = user.first()

    # Авторизация юзера
    auth_login(request, user)
    messages.success(request, 'Вы успешно вошли в систему.')

    # Переадресация в читательский кабинет
    return HttpResponseRedirect(reverse('reader_cabinet:home'))


