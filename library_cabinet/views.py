from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.http import JsonResponse, Http404, FileResponse
from django.db.models import Q
from wsgiref.util import FileWrapper

from libraries_portal.heplers import library_enabled, group_required
from .forms import DocumentForm, TimeLimitsForm, UserSettingsForm, LibrarySettingsForm, LibraryUserForm, \
    ReportLibraryFundForm, ReportOrdersForm, ReportStaffForm, EnteredDocumentsForm

from orders.models import Order, OrderAction
from home.models import LibraryRequestAccess, ReaderTicket
from documents.models import Document, AnotherPerson, Rubric

from comments.models import Comment

from .library_fund_report import LibraryFundReportContext, LibraryFundReportXLSStrategy, LibraryFundReportDOCStrategy, \
    LibraryFundReportPDFStrategy, LibraryFundReportODSStrategy
from .orders_report import OrdersReportContext, OrdersReportXLSStrategy, OrdersReportDOCStrategy, \
    OrdersReportPDFStrategy, OrdersReportODSStrategy
from .staff_report import StaffReportContext, StaffReportXLSStrategy, StaffReportDOCStrategy, StaffReportPDFStrategy, \
    StaffReportODSStrategy
from .orders_acquisitions_report import OrdersReportContext as OrdersAcquisitionsReportContext, \
    OrdersReportXLSStrategy as OrdersAcquisitionsReportXLSStrategy, \
    OrdersReportDOCStrategy as OrdersAcquisitionsReportDOCStrategy, \
    OrdersReportPDFStrategy as OrdersAcquisitionsReportPDFStrategy, \
    OrdersReportODSStrategy as OrdersAcquisitionsReportODSStrategy
from .entered_documents_report import EnteredDocumentsReportContext, EnteredDocumentsReportDOCStrategy, \
    EnteredDocumentsReportODSStrategy, EnteredDocumentsReportPDFStrategy, EnteredDocumentsReportStrategy, \
    EnteredDocumentsReportXLSStrategy


def get_my_library(request):
    """Возвращает библиотеку текущего пользователя (библиотекаря)."""
    return request.user.library_set.all()[:1].get()


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def index(request):
    """Выводит страницу Главная."""
    return render(request, 'library_cabinet/index.html')


class OrdersListView(generic.ListView):
    """Выводит страницу со списком заказов."""
    template_name = 'library_cabinet/orders/list.html'
    context_object_name = 'orders_list'

    def get_queryset(self):
        """Возвращает список с заказами."""
        return Order.objects.filter(
            document__library=get_my_library(self.request)
        ).order_by('approved', 'status_id')

    @method_decorator(login_required)
    @method_decorator(group_required('Библиотекари-администраторы',
                                     'Библиотекари-каталогизаторы',
                                     'Библиотекари-комплектаторы'))
    @method_decorator(library_enabled())
    def dispatch(self, *args, **kwargs):
        return super(OrdersListView, self).dispatch(*args, **kwargs)


class OrderDetailView(generic.DetailView):
    """Выводит страницу с описанием заказа."""
    template_name = 'library_cabinet/orders/detail.html'

    def get_queryset(self):
        return Order.objects.filter(document__library=get_my_library(self.request))

    @method_decorator(login_required)
    @method_decorator(group_required('Библиотекари-администраторы',
                                     'Библиотекари-каталогизаторы',
                                     'Библиотекари-комплектаторы'))
    @method_decorator(library_enabled())
    def dispatch(self, *args, **kwargs):
        return super(OrderDetailView, self).dispatch(*args, **kwargs)


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def approve_order(request, pk):
    """Одобрение заказа."""
    order = get_object_or_404(Order, pk=pk)
    order.approved = True
    order.save()

    messages.success(request, 'Заказ успешно одобрен.')

    return redirect(reverse('library_cabinet:order_detail', args=[pk]))


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def issue_document(request, pk):
    """Выдача документа."""
    order = get_object_or_404(Order, pk=pk)

    if order.status_id == 1:
        order.status_id = 2
        order.save()

        order_action = OrderAction(user=request.user, status_id=2, order=order)
        order_action.save()

        messages.success(request, 'Статус заказ успешно изменён на "Выдан"')
    else:
        messages.error(request, 'Зазаз должен иметь статус "Забронирован"')

    return redirect(reverse('library_cabinet:order_detail', args=[pk]))


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def pass_document(request, pk):
    """Сдача документа."""
    order = get_object_or_404(Order, pk=pk)
    if order.status_id == 2:
        order.status_id = 3
        order.save()

        order_action = OrderAction(user=request.user, status_id=3, order=order)
        order_action.save()

        messages.success(request, 'Статус заказ успешно изменён на "Возвращён"')
    else:
        messages.error(request, 'Зазаз должен иметь статус "Выдан"')

    return redirect(reverse('library_cabinet:order_detail', args=[pk]))


class RequestAccessesListView(generic.ListView):
    """Выводит страницу со списком заказов."""
    template_name = 'library_cabinet/request_accesses/list.html'
    context_object_name = 'request_accesses_list'

    def get_queryset(self):
        """Возвращает список с заказами текущего юзера."""
        return LibraryRequestAccess.objects.filter(
            library=get_my_library(self.request)
        ).order_by('approved', '-created_at')

    @method_decorator(login_required)
    @method_decorator(group_required('Библиотекари-администраторы',
                                     'Библиотекари-каталогизаторы',
                                     'Библиотекари-комплектаторы'))
    @method_decorator(library_enabled())
    def dispatch(self, *args, **kwargs):
        return super(RequestAccessesListView, self).dispatch(*args, **kwargs)


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def approve_request_access(request, pk):
    """Делает заявку на доступ к библиотеке одобренной."""
    request_access = get_object_or_404(LibraryRequestAccess, pk=pk)
    request_access.approved = True
    request_access.approved_by = request.user
    request_access.library.reader_tickets.add(request_access.user.readerticket)
    request_access.save()

    messages.success(request, 'Заявка пользователя успешно одобрена.')

    return redirect(reverse('library_cabinet:request_accesses_list'))


class ReadersListView(generic.ListView):
    """Выводит страницу со списком читателей библиотеки."""
    template_name = 'library_cabinet/readers/list.html'
    context_object_name = 'readers_list'

    def get_queryset(self):
        """Возвращает список с читателями библиотеки."""
        library = get_my_library(self.request)

        reader_tickets = library.reader_tickets.all()
        readers = ReaderTicket.objects.filter(user__profile__city=library.city, user__groups__name__exact='Читатели')

        records = reader_tickets | readers
        return records.distinct()

    @method_decorator(login_required)
    @method_decorator(group_required('Библиотекари-администраторы',
                                     'Библиотекари-каталогизаторы',
                                     'Библиотекари-комплектаторы'))
    @method_decorator(library_enabled())
    def dispatch(self, *args, **kwargs):
        return super(ReadersListView, self).dispatch(*args, **kwargs)


class ReaderDetailView(generic.DetailView):
    """Выводит страницу с деталями читателя."""
    template_name = 'library_cabinet/readers/detail.html'
    context_object_name = 'reader'

    def get_queryset(self):
        library = get_my_library(self.request)

        reader_tickets = library.reader_tickets.all()
        readers = ReaderTicket.objects.filter(user__profile__city=library.city, user__groups__name__exact='Читатели')

        records = reader_tickets | readers
        return records.distinct()

    @method_decorator(login_required)
    @method_decorator(group_required('Библиотекари-администраторы',
                                     'Библиотекари-каталогизаторы',
                                     'Библиотекари-комплектаторы'))
    @method_decorator(library_enabled())
    def dispatch(self, *args, **kwargs):
        return super(ReaderDetailView, self).dispatch(*args, **kwargs)


class DocumentsListView(generic.ListView):
    """Выводит страницу со списком документов библиотеки."""
    template_name = 'library_cabinet/documents/list.html'
    context_object_name = 'documents_list'

    def get_queryset(self):
        """Возвращает список с документами библиотеки."""
        return get_my_library(self.request).document_set.order_by('-created_at').all()

    @method_decorator(login_required)
    @method_decorator(group_required('Библиотекари-администраторы',
                                     'Библиотекари-каталогизаторы',
                                     'Библиотекари-комплектаторы'))
    @method_decorator(library_enabled())
    def dispatch(self, *args, **kwargs):
        return super(DocumentsListView, self).dispatch(*args, **kwargs)


class DocumentDetailView(generic.DetailView):
    """Выводит страницу с деталями документа."""
    template_name = 'library_cabinet/documents/detail.html'
    context_object_name = 'document'

    def get_queryset(self):
        return get_my_library(self.request).document_set.order_by('-created_at').all()

    @method_decorator(login_required)
    @method_decorator(group_required('Библиотекари-администраторы',
                                     'Библиотекари-каталогизаторы',
                                     'Библиотекари-комплектаторы'))
    @method_decorator(library_enabled())
    def dispatch(self, *args, **kwargs):
        return super(DocumentDetailView, self).dispatch(*args, **kwargs)


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def document_edit(request, pk):
    """Отображает страницу редактирования доуцмента"""
    document = get_object_or_404(Document, pk=pk)

    if request.method == 'POST':
        form = DocumentForm(request.POST, instance=document)
        form.save()
        messages.success(request, 'Документ успешно изменён.')
        return redirect(reverse('library_cabinet:document_edit', args=[pk]))
    else:
        form = DocumentForm(instance=document)

    return render(request, 'library_cabinet/documents/edit.html', {'form': form, 'document': document})


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def document_utilize(request, pk):
    """Списывает документ."""
    document = get_object_or_404(Document, pk=pk)
    if document.library != get_my_library(request):
        messages.error(request, 'Документ не принадлежит библиотеке.')
    else:
        document.utilized = True
        document.save()
        messages.success(request, 'Документ успешно списан.')

    return redirect(reverse('library_cabinet:document_detail', args=[pk]))


@require_POST
@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def add_another_person(request):
    """Добавляет новую Другую персону."""
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            another_person = AnotherPerson.objects.filter(title=name).count()
            if another_person > 0:
                return JsonResponse({'success': False, 'errors': 'Такая персона уже существует!'})

            another_person = AnotherPerson(title=name)
            another_person.save()
            return JsonResponse({'success': True, 'id': another_person.pk})
        else:
            return JsonResponse({'success': False, 'errors': 'Поле не может быть пустым!'})


@require_POST
@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def add_rubric(request):
    """Добавляет новую рубрику."""
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            rubric = Rubric.objects.filter(title=name).count()
            if rubric > 0:
                return JsonResponse({'success': False, 'errors': 'Такая рубрика уже существует!'})

            rubric = Rubric(title=name)
            rubric.save()
            return JsonResponse({'success': True, 'id': rubric.pk})
        else:
            return JsonResponse({'success': False, 'errors': 'Поле не может быть пустым!'})


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def document_create(request):
    """Отображает страницу создания документа и обрабатывает запрос на создание."""
    if request.method == 'POST':
        form = DocumentForm(request.POST)
        if form.is_valid():
            document = form.save(commit=False)
            document.library_id = get_my_library(request).pk
            document.document_status_id = 1
            document.created_by_id = request.user.pk
            document.save()
            messages.success(request, 'Документ успешно создан.')
            return redirect(reverse('library_cabinet:document_edit', args=[document.pk]))
    else:
        form = DocumentForm()

    return render(request, 'library_cabinet/documents/create.html', {'form': form})


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def time_limits(request):
    """Отображает страницу редактирования регламента."""
    library = get_my_library(request)
    if request.method == 'POST':
        form = TimeLimitsForm(request.POST)
        if form.is_valid():
            library.reservation_recommended_time = request.POST['reservation_recommended_time']
            library.return_time_delay_max = request.POST['return_time_delay_max']
            library.save()
            messages.success(request, 'Данные успешно сохранены.')
            return redirect(reverse('library_cabinet:time_limits'))
    else:
        form = TimeLimitsForm(initial={
            'reservation_recommended_time': library.reservation_recommended_time,
            'return_time_delay_max': library.return_time_delay_max,
        })

    return render(request, 'library_cabinet/time_limits.html', {'form': form})


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def library_settings(request):
    """Отображает страницу изменения настроек библиотеки."""
    library = get_my_library(request)
    if request.method == 'POST':
        form = LibrarySettingsForm(request.POST,
                                   library=library,
                                   region=request.POST['region'],
                                   city=request.POST['city'],
                                   library_type=request.POST['library_type'],
                                   library_kind=request.POST['library_kind'])
        if form.is_valid():
            library.title = request.POST['title']
            library.address = request.POST['address']
            library.city_id = request.POST['city']
            library.library_type_id = request.POST['library_type']
            library.library_kind_id = request.POST['library_kind']
            library.legal_entity_name = request.POST['legal_entity_name']
            library.legal_entity_address = request.POST['legal_entity_address']
            library.bin = request.POST['bin']
            library.inn = request.POST['inn']
            library.crr = request.POST['crr']
            library.contact_info = request.POST['contact_info']
            library.about = request.POST['about']
            library.save()

            messages.success(request, 'Данные успешно сохранены')
            return redirect(reverse('library_cabinet:library_settings'))
    else:
        form = LibrarySettingsForm(initial={
            'title': library.title,
            'address': library.address,
            'legal_entity_name': library.legal_entity_name,
            'legal_entity_address': library.legal_entity_address,
            'bin': library.bin,
            'inn': library.inn,
            'crr': library.crr,
            'contact_info': library.contact_info,
            'about': library.about
        }, library=library)
    return render(request, 'library_cabinet/library_settings.html', {'form': form})


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def user_settings(request):
    """Отображает страницу изменения настроек пользователя."""
    if request.method == 'POST':
        form = UserSettingsForm(request.POST)
        if form.is_valid():
            request.user.email = request.POST['email']
            if request.POST.get('password'):
                request.user.set_password(request.POST['password'])
            request.user.save()
            login(request, request.user)
            messages.success(request, 'Данные успешно сохранены')
            return redirect(reverse('library_cabinet:user_settings'))
    else:
        form = UserSettingsForm(initial={'email': request.user.email})
    return render(request, 'library_cabinet/user_settings.html', {'form': form})


class UsersListView(generic.ListView):
    """Выводит страницу со списком отрудников библиотеки."""
    template_name = 'library_cabinet/users/list.html'
    context_object_name = 'users_list'

    def get_queryset(self):
        """Возвращает список с документами библиотеки."""
        return get_my_library(self.request).admins.all()

    @method_decorator(login_required)
    @method_decorator(group_required('Библиотекари-администраторы',
                                     'Библиотекари-каталогизаторы',
                                     'Библиотекари-комплектаторы'))
    @method_decorator(library_enabled())
    def dispatch(self, *args, **kwargs):
        return super(UsersListView, self).dispatch(*args, **kwargs)


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def deactivate_user(request, pk):
    """Деактивирует пользователя."""
    try:
        user = User.objects.get(pk=pk, library__admins=pk, library__admins__library=get_my_library(request).pk)
    except User.DoesNotExist:
        raise Http404("Пользователь не найден.")

    if user != request.user:
        user.is_active = False
        user.save()
        messages.success(request, 'Пользователь успешно деактивирован.')
    else:
        messages.error(request, 'Вы не можете деактивировать себя.')
    return redirect(reverse('library_cabinet:users_list'))


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def activate_user(request, pk):
    """Активирует пользователя."""
    try:
        user = User.objects.get(pk=pk, library__admins=pk, library__admins__library=get_my_library(request).pk)
    except User.DoesNotExist:
        raise Http404("Пользователь не найден.")

    user.is_active = True
    user.save()
    messages.success(request, 'Пользователь успешно активирован.')
    return redirect(reverse('library_cabinet:users_list'))


class UserDetailView(generic.DetailView):
    """Выводит страницу с деталями библиотекаря."""
    template_name = 'library_cabinet/users/detail.html'
    context_object_name = 'user'

    def get_queryset(self):
        return get_my_library(self.request).admins.all()

    @method_decorator(login_required)
    @method_decorator(group_required('Библиотекари-администраторы',
                                     'Библиотекари-каталогизаторы',
                                     'Библиотекари-комплектаторы'))
    @method_decorator(library_enabled())
    def dispatch(self, *args, **kwargs):
        return super(UserDetailView, self).dispatch(*args, **kwargs)


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def create_user(request):
    """Создаёт сотрудника библиотеки."""
    if request.method == 'POST':
        form = LibraryUserForm(request.POST)
        form.fields['password'].required = True
        form.fields['password_confirm'].required = True
        if form.is_valid():
            user = User()
            user.username = request.POST['username']
            user.last_name = request.POST['last_name']
            user.first_name = request.POST['first_name']
            user.email = request.POST['email']
            user.set_password(request.POST['password'])
            user.save()

            user.groups.add(Group.objects.get(pk=request.POST['group']))
            user.save()

            library = get_my_library(request)
            library.admins.add(user)
            library.save()

            messages.success(request, 'Сотрудник успешно создан.')
            return redirect(reverse('library_cabinet:users_list'))
    else:
        form = LibraryUserForm()
        form.fields['password'].required = True
        form.fields['password_confirm'].required = True
    return render(request, 'library_cabinet/users/create.html', {'form': form})


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def edit_user(request, pk):
    """Редактирует сотрудника библиотеки."""
    try:
        user = User.objects.get(pk=pk, library__admins=pk, library__admins__library=get_my_library(request).pk)
    except User.DoesNotExist:
        raise Http404("Пользователь не найден.")

    if request.method == 'POST':
        form = LibraryUserForm(request.POST, initial={'username': user.username})
        del form.fields['username']
        if form.is_valid():
            user.last_name = request.POST['last_name']
            user.first_name = request.POST['first_name']
            user.email = request.POST['email']
            if request.POST.get('password'):
                user.set_password(request.POST['password'])
            user.save()

            user.groups = (Group.objects.get(pk=request.POST['group']), )
            user.save()

            messages.success(request, 'Данные сотрудника успешно сохранёны.')
            return redirect(reverse('library_cabinet:user_edit', args=(pk,)))
    else:
        form = LibraryUserForm(initial={
            'username': user.username,
            'last_name': user.last_name,
            'first_name': user.first_name,
            'email': user.email,
            'group': user.groups.first().pk,
        })
        del form.fields['username']
    return render(request, 'library_cabinet/users/edit.html', {'form': form, 'user': user})


class CommentsListView(generic.ListView):
    """Выводит страницу со списком комментариев."""
    template_name = 'library_cabinet/comments/list.html'
    context_object_name = 'comments_list'

    def get_queryset(self):
        """Возвращает список с комментариями."""
        library = get_my_library(self.request)
        return Comment.objects.filter(
            Q(library=library) | Q(document__in=library.document_set.all())
        ).order_by('-updated_at')

    @method_decorator(login_required)
    @method_decorator(group_required('Библиотекари-администраторы',
                                     'Библиотекари-каталогизаторы',
                                     'Библиотекари-комплектаторы'))
    @method_decorator(library_enabled())
    def dispatch(self, *args, **kwargs):
        return super(CommentsListView, self).dispatch(*args, **kwargs)


class CommentDetailView(generic.DetailView):
    """Выводит страницу с описанием комментария."""
    template_name = 'library_cabinet/comments/detail.html'

    def get_queryset(self):
        """Возвращает список с комментариями."""
        library = get_my_library(self.request)
        return Comment.objects.filter(
            Q(library=library) | Q(document__in=library.document_set.all())
        )

    @method_decorator(login_required)
    @method_decorator(group_required('Библиотекари-администраторы',
                                     'Библиотекари-каталогизаторы',
                                     'Библиотекари-комплектаторы'))
    @method_decorator(library_enabled())
    def dispatch(self, *args, **kwargs):
        return super(CommentDetailView, self).dispatch(*args, **kwargs)


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def comment_delete(request, pk):
    """Удаляет комментарий."""
    library = get_my_library(request)
    try:
        comment = Comment.objects.get(Q(pk=pk), Q(library=library) | Q(document__in=library.document_set.all()))
    except Comment.DoesNotExist:
        raise Http404('Комментарий не существует')
    else:
        comment.delete()
        messages.success(request, 'Комментарий успешно удалён')
        redirect_to = request.GET.get('redirect_to')
        if not redirect_to:
            return redirect(request.META.get('HTTP_REFERER', '/library-cabinet/comments/list/'))
        else:
            return redirect(redirect_to)


@login_required
@group_required('Библиотекари-администраторы', 'Библиотекари-каталогизаторы', 'Библиотекари-комплектаторы')
@library_enabled()
def comment_moderate(request, pk):
    """Удаляет комментарий."""
    library = get_my_library(request)
    try:
        comment = Comment.objects.get(Q(pk=pk), Q(library=library) | Q(document__in=library.document_set.all()))
    except Comment.DoesNotExist:
        raise Http404('Комментарий не существует')
    else:
        comment.moderated = True
        comment.save()
        messages.success(request, 'Комментарий успешно одобрен')
        return redirect(reverse('library_cabinet:comment_show', args=(pk,)))


@login_required
@group_required('Библиотекари-администраторы')
@library_enabled()
def report_library_fund(request):
    if request.method == 'POST':
        form = ReportLibraryFundForm(request.POST, library=get_my_library(request))
        if form.is_valid():
            if request.POST['format'] == 'doc':
                context = LibraryFundReportContext(LibraryFundReportDOCStrategy(), request.POST)
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                file_format = 'docx'
            elif request.POST['format'] == 'pdf':
                context = LibraryFundReportContext(LibraryFundReportPDFStrategy(), request.POST)
                content_type = 'application/pdf'
                file_format = 'pdf'
            elif request.POST['format'] == 'ods':
                context = LibraryFundReportContext(LibraryFundReportODSStrategy(), request.POST)
                content_type = 'application/vnd.oasis.opendocument.spreadsheet'
                file_format = 'ods'
            else:
                # xlsx
                context = LibraryFundReportContext(LibraryFundReportXLSStrategy(), request.POST)
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                file_format = 'xlsx'

            report_file = context.get_report()
            response = FileResponse(FileWrapper(open(report_file, 'rb')), content_type=content_type)
            response['Content-Disposition'] = "attachment; filename={}.{}".format('report_library_fund', file_format)
            return response
    else:
        form = ReportLibraryFundForm(library=get_my_library(request))
    return render(request, 'library_cabinet/reports/library_fund.html', {'form': form})


@login_required
@group_required('Библиотекари-администраторы')
@library_enabled()
def report_orders(request):
    library = get_my_library(request)
    if request.method == 'POST':
        form = ReportOrdersForm(request.POST, library=library)
        if form.is_valid():
            if request.POST['format'] == 'doc':
                context = OrdersReportContext(OrdersReportDOCStrategy(), request.POST, library)
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                file_format = 'docx'
            elif request.POST['format'] == 'pdf':
                context = OrdersReportContext(OrdersReportPDFStrategy(), request.POST, library)
                content_type = 'application/pdf'
                file_format = 'pdf'
            elif request.POST['format'] == 'ods':
                context = OrdersReportContext(OrdersReportODSStrategy(), request.POST, library)
                content_type = 'application/vnd.oasis.opendocument.spreadsheet'
                file_format = 'ods'
            else:
                # xlsx
                context = OrdersReportContext(OrdersReportXLSStrategy(), request.POST, library=library)
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                file_format = 'xlsx'

            report_file = context.get_report()
            response = FileResponse(FileWrapper(open(report_file, 'rb')), content_type=content_type)
            response['Content-Disposition'] = "attachment; filename={}.{}".format('orders', file_format)
            return response
    else:
        form = ReportOrdersForm(library=library)
    return render(request, 'library_cabinet/reports/orders.html', {'form': form})


@login_required
@group_required('Библиотекари-администраторы')
@library_enabled()
def report_staff(request):
    library = get_my_library(request)
    if request.method == 'POST':
        form = ReportStaffForm(request.POST, library=library)
        if form.is_valid():
            if request.POST['format'] == 'doc':
                context = StaffReportContext(StaffReportDOCStrategy(), request.POST)
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                file_format = 'docx'
            elif request.POST['format'] == 'pdf':
                context = StaffReportContext(StaffReportPDFStrategy(), request.POST)
                content_type = 'application/pdf'
                file_format = 'pdf'
            elif request.POST['format'] == 'ods':
                context = StaffReportContext(StaffReportODSStrategy(), request.POST)
                content_type = 'application/vnd.oasis.opendocument.spreadsheet'
                file_format = 'ods'
            else:
                # xlsx
                context = StaffReportContext(StaffReportXLSStrategy(), request.POST)
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                file_format = 'xlsx'

            report_file = context.get_report()
            response = FileResponse(FileWrapper(open(report_file, 'rb')), content_type=content_type)
            response['Content-Disposition'] = "attachment; filename={}.{}".format('staff', file_format)
            return response
    else:
        form = ReportStaffForm(library=library)
    return render(request, 'library_cabinet/reports/staff.html', {'form': form})


@login_required
@group_required('Библиотекари-комплектаторы')
@library_enabled()
def report_orders_acquisitions(request):
    library = get_my_library(request)
    if request.method == 'POST':
        form = ReportOrdersForm(request.POST, library=library)
        if form.is_valid():
            if request.POST['format'] == 'doc':
                context = OrdersAcquisitionsReportContext(OrdersAcquisitionsReportDOCStrategy(),
                                                          request.POST,
                                                          user=request.user)
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                file_format = 'docx'
            elif request.POST['format'] == 'pdf':
                context = OrdersAcquisitionsReportContext(OrdersAcquisitionsReportPDFStrategy(),
                                                          request.POST,
                                                          user=request.user)
                content_type = 'application/pdf'
                file_format = 'pdf'
            elif request.POST['format'] == 'ods':
                context = OrdersAcquisitionsReportContext(OrdersAcquisitionsReportODSStrategy(),
                                                          request.POST,
                                                          user=request.user)
                content_type = 'application/vnd.oasis.opendocument.spreadsheet'
                file_format = 'ods'
            else:
                # xlsx
                context = OrdersAcquisitionsReportContext(OrdersAcquisitionsReportXLSStrategy(),
                                                          request.POST,
                                                          user=request.user)
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                file_format = 'xlsx'

            report_file = context.get_report()
            response = FileResponse(FileWrapper(open(report_file, 'rb')), content_type=content_type)
            response['Content-Disposition'] = "attachment; filename={}.{}".format('orders', file_format)
            return response
    else:
        form = ReportOrdersForm(library=library)
    return render(request, 'library_cabinet/reports/orders_acquisitions.html', {'form': form})


@login_required
@group_required('Библиотекари-комплектаторы', 'Библиотекари-каталогизаторы')
@library_enabled()
def report_entered_documents(request):
    """Отображает страницу формирования отчёта Внесенные книги"""
    if request.method == 'POST':
        form = EnteredDocumentsForm(request.POST)
        if form.is_valid():
            if request.POST['format'] == 'doc':
                context = EnteredDocumentsReportContext(EnteredDocumentsReportDOCStrategy(), request.POST,
                                                        user=request.user)
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                file_format = 'docx'
            elif request.POST['format'] == 'pdf':
                context = EnteredDocumentsReportContext(EnteredDocumentsReportPDFStrategy(), request.POST,
                                                        user=request.user)
                content_type = 'application/pdf'
                file_format = 'pdf'
            elif request.POST['format'] == 'ods':
                context = EnteredDocumentsReportContext(EnteredDocumentsReportODSStrategy(),
                                                        request.POST,
                                                        user=request.user)
                content_type = 'application/vnd.oasis.opendocument.spreadsheet'
                file_format = 'ods'
            else:
                # xlsx
                context = EnteredDocumentsReportContext(EnteredDocumentsReportXLSStrategy(), request.POST,
                                                        user=request.user)
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                file_format = 'xlsx'

            report_file = context.get_report()
            response = FileResponse(FileWrapper(open(report_file, 'rb')), content_type=content_type)
            response['Content-Disposition'] = "attachment; filename={}.{}".format('entered-documents', file_format)
            return response
    else:
        form = EnteredDocumentsForm()
    return render(request, 'library_cabinet/reports/entered_documents.html', {'form': form})
