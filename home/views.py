from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse

from .forms import AuthForm, UserRegistrationForm, LibraryRegistrationForm
from .models import City, Library, LibraryKind, LibraryType


def index(request):
    """Отображает стартовую страницу."""
    # Форма авторизации
    form_auth_data = request.session.get('auth_form_data', None)
    if form_auth_data:
        auth_form = AuthForm(form_auth_data)
        auth_form.is_valid()
        del request.session['auth_form_data']
    else:
        auth_form = AuthForm()

    active_tab = 'user'

    # Форма регистрации читателя
    user_registration_form_data = request.session.get('user_registration_form_data', None)
    if user_registration_form_data:
        user_registration_form = UserRegistrationForm(user_registration_form_data,
                                                      region=user_registration_form_data['region'],
                                                      city=user_registration_form_data['city'])
        user_registration_form.is_valid()
        del request.session['user_registration_form_data']
    else:
        user_registration_form = UserRegistrationForm()

    # Форма регистрации библиотеки
    library_registration_form_data = request.session.get('library_registration_form_data', None)
    if library_registration_form_data:
        library_registration_form = LibraryRegistrationForm(library_registration_form_data,
                                                            region=library_registration_form_data['region'],
                                                            city=library_registration_form_data['city'],
                                                            library_type=library_registration_form_data['library_type'],
                                                            library_kind=library_registration_form_data['library_kind'])
        library_registration_form.is_valid()
        del request.session['library_registration_form_data']
        active_tab = 'library'
    else:
        library_registration_form = LibraryRegistrationForm()

    return render(request, 'home/index.html', {
        'auth_form': auth_form,
        'user_registration_form': user_registration_form,
        'library_registration_form': library_registration_form,
        'active_tab': active_tab
    })


@require_POST
def login(request):
    """Обрабатывает POST-запрос на авторизацию пользователя."""
    form = AuthForm(request.POST)
    if form.is_valid():
        username = request.POST['login']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                messages.success(request, 'Вы успешно вошли в систему.')
            else:
                messages.error(request, 'Ваш аккаунт не активирован.')
        else:
            messages.error(request, 'Неправильный логин и/или пароль.')
            return HttpResponseRedirect('/')
        groups = user.groups.values_list('name', flat=True)
        if 'Читатели' in groups:
            return HttpResponseRedirect(reverse('reader_cabinet:home'))
        else:
            if 'Библиотекари-администраторы' in groups or 'Библиотекари-каталогизаторы' in groups \
                   or 'Библиотекари-комплектаторы' in groups:
                # Проверка активная ли библиотека
                if not user.library_set.all()[:1].get().enabled:
                    messages.error(request, 'Библиотека не активирована администратором системы. '
                                            'Пока что вы не можете войти в кабинет библиотекаря.')
                return HttpResponseRedirect(reverse('library_cabinet:home'))
        return HttpResponseRedirect('/admin/')
    else:
        request.session['auth_form_data'] = request.POST
        return HttpResponseRedirect('/')


@require_POST
def user_register(request):
    """Обрабатывает POST-запрос на регистрацию пользователя (читателя)."""
    form = UserRegistrationForm(request.POST,
                                region=request.POST['region'])
    if form.is_valid():
        # Добавление пользователя
        username = request.POST['login']
        email = request.POST['email']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)

        user.profile.city = City.objects.get(pk=request.POST['city'])

        group = Group.objects.get(name='Читатели')
        user.groups.add(group)

        user.save()

        messages.success(request, 'Вы успешно зарегистрировались. '
                                  'Можете использовать указанные логин и пароль для входа.')
        return HttpResponseRedirect(reverse('reader_cabinet:home'))
    else:
        request.session['user_registration_form_data'] = request.POST
        return HttpResponseRedirect('/')


@require_POST
def library_register(request):
    """Обрабатывает POST-запрос на регистрацию библиотеки."""
    form = LibraryRegistrationForm(request.POST,
                                   region=request.POST['region'],
                                   library_type=request.POST['library_type'],
                                   library_kind=request.POST['library_kind'])
    if form.is_valid():
        # Добавление пользователя
        username = request.POST['login']
        email = request.POST['email']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        user = User.objects.create_user(username,
                                        email,
                                        password,
                                        first_name=first_name,
                                        last_name=last_name)
        user.profile.city = City.objects.get(pk=request.POST['city'])

        group = Group.objects.get(name='Библиотекари-администраторы')
        user.groups.add(group)

        user.save()

        # Добавление библиотеки
        library = Library(title=request.POST['title'],
                          address=request.POST['address'],
                          library_kind=LibraryKind.objects.get(pk=request.POST['library_kind']),
                          library_type=LibraryType.objects.get(pk=request.POST['library_type']),
                          city=City.objects.get(pk=request.POST['city']))
        library.save()
        library.admins.add(user)
        library.save()

        messages.success(request, 'Вы успешно зарегистрировали библиотеку. '
                                  'После того как администратор подтвердит регистрацию библиотеки, '
                                  'вы сможете использовать указанные логин и пароль для входа.')

        return HttpResponseRedirect('/')
    else:
        request.session['library_registration_form_data'] = request.POST
        return HttpResponseRedirect('/')


def get_cities(request, region_id):
    """Возвращает JSON с городами определённого региона."""
    cities = City.objects.filter(region_id=region_id).order_by('title')
    return JsonResponse([(x.id, x.title) for x in cities], safe=False)


def get_library_kinds(request, library_type_id):
    """Возвращает JSON с городами определённого региона."""
    kinds = LibraryKind.objects.all().filter(librarytype=library_type_id).order_by('title')
    return JsonResponse([(x.id, x.title) for x in kinds], safe=False)


def get_libraries_in_city(request, city_id):
    """Возвращает JSON с библиотеками определённого города."""
    libraries = Library.objects.filter(city=city_id, enabled=True).order_by('title')
    return JsonResponse([(x.id, x.title) for x in libraries], safe=False)
