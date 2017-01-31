from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.views import generic
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from .forms import ReaderTicketForm, SimpleSearchForm, ExtendedSearchForm, SettingsForm, CommentForm
from home.models import City, Library, LibraryRequestAccess
from documents.models import Document
from libraries_portal.heplers import group_required

from orders.models import Order

from comments.models import Comment


@login_required
@group_required('Читатели')
def index(request):
    """Выводит страницу Главная."""
    return render(request, 'reader_cabinet/index.html')


@login_required
@group_required('Читатели')
def reader_ticket(request):
    """Выводит страницу Читательский билет."""
    if request.method == 'POST':
        form = ReaderTicketForm(request.POST, region=request.POST['region'])
        if form.is_valid():
            request.user.first_name = request.POST['first_name']
            request.user.last_name = request.POST['last_name']
            request.user.profile.city_id = request.POST['city']
            request.user.profile.address = request.POST['address']
            request.user.save()

            messages.success(request, 'Данные успешно сохранены.')
            return HttpResponseRedirect(reverse('reader_cabinet:reader_ticket'))
    else:
        form = ReaderTicketForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'address': request.user.profile.address,
            'region': City.objects.filter(pk=request.user.profile.city_id).get().region_id
        }, user=request.user)

    return render(request, 'reader_cabinet/reader_ticket.html', {'form': form})


@login_required
@group_required('Читатели')
def simple_search(request):
    """Выводит страницу Простого поиска."""
    documents = None
    if request.GET:
        form = SimpleSearchForm(request.GET)
        if form.is_valid():
            documents = Document.objects.filter(title__contains=request.GET['query'])
    else:
        form = SimpleSearchForm()
    return render(request, 'reader_cabinet/simple_search.html', {'form': form, 'documents': documents})


@login_required
@group_required('Читатели')
def extended_search(request):
    """Выводит страницу Расширенного поиска."""
    documents = None
    if request.GET:
        form = ExtendedSearchForm(request.GET,
                                  user=request.user,
                                  region=request.GET.get('region'),
                                  city=request.GET.get('city'))
        if form.is_valid():
            documents = Document.objects.filter(title__contains=request.GET['title'])
            if request.GET.get('region'):
                documents = documents.filter(library__city__region_id=request.GET['region'])
            if request.GET.get('city'):
                documents = documents.filter(library__city__id=request.GET['city'])
            if request.GET.get('library'):
                documents = documents.filter(library_id=request.GET['library'])
    else:
        form = ExtendedSearchForm(user=request.user)
    return render(request, 'reader_cabinet/extended_search.html', {'form': form, 'documents': documents})


class DocumentDetailView(generic.DetailView):
    """Выводит страницу с описанием документа."""
    model = Document
    template_name = 'reader_cabinet/document_detail.html'

    def get_context_data(self, **kwargs):
        context = super(DocumentDetailView, self).get_context_data(**kwargs)
        context['form'] = CommentForm
        return context

    @method_decorator(login_required)
    @method_decorator(group_required('Читатели'))
    def dispatch(self, *args, **kwargs):
        return super(DocumentDetailView, self).dispatch(*args, **kwargs)


class LibraryDetailView(generic.DetailView):
    """Выводит страницу с описанием библиотеки."""
    model = Library
    template_name = 'reader_cabinet/library_detail.html'

    def get_context_data(self, **kwargs):
        context = super(LibraryDetailView, self).get_context_data(**kwargs)
        context['form'] = CommentForm
        return context

    @method_decorator(login_required)
    @method_decorator(group_required('Читатели'))
    def dispatch(self, *args, **kwargs):
        return super(LibraryDetailView, self).dispatch(*args, **kwargs)


class OrdersListView(generic.ListView):
    """Выводит страницу со списком заказов."""
    template_name = 'reader_cabinet/orders/list.html'
    context_object_name = 'orders_list'

    def get_queryset(self):
        """Возвращает список с заказами текущего юзера."""
        return Order.objects.filter(user=self.request.user).order_by('-updated_at')

    @method_decorator(login_required)
    @method_decorator(group_required('Читатели'))
    def dispatch(self, *args, **kwargs):
        return super(OrdersListView, self).dispatch(*args, **kwargs)


class OrderDetailView(generic.DetailView):
    """Выводит страницу с описанием заказа."""
    template_name = 'reader_cabinet/orders/detail.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @method_decorator(login_required)
    @method_decorator(group_required('Читатели'))
    def dispatch(self, *args, **kwargs):
        return super(OrderDetailView, self).dispatch(*args, **kwargs)


@login_required
@group_required('Читатели')
def create_order(request, pk):
    """Создаёт заказ и переадресовывает на страницу заказа."""
    document = get_object_or_404(Document, pk=pk)
    # Проверка есть ли доступ в эту библиотеку
    if request.user.profile.has_access_to_library(document.library.id):
        try:
            # Проверка есть ли незакрытый заказ на данный документ
            order = Order.objects.get(user=request.user, document_id=pk, status__title__in=['Забронирован', 'Выдан'])
        except Order.DoesNotExist:
            # Создание заказа
            order = Order(document_id=pk, user=request.user)
            order.save()
            messages.success(request, 'Заказ создан. Вы были переадресованы на страницу заказа.')
        else:
            messages.error(request, 'Такой заказ уже существует. Вы были переадресованы на страницу этого заказа.')
    else:
        messages.error(request, 'У вас нет доступа к этой библиотеке.')
        return redirect(request.META.get('HTTP_REFERER', '/reader-cabinet/'))

    return redirect(reverse('reader_cabinet:order_detail', args=[order.id]))


@login_required
@group_required('Читатели')
def access_request(request, library_id):
    """Запрос доступа к библиотеке."""
    # Проверка имеет ли уже доступ к этой библиотеке пользователь
    if not request.user.profile.has_access_to_library(library_id):
        # Проверка нет ли уже такой заявки
        try:
            LibraryRequestAccess.objects.get(user=request.user, library_id=library_id)
        except LibraryRequestAccess.DoesNotExist:
            library_request_access = LibraryRequestAccess(user=request.user, library_id=library_id)
            library_request_access.save()
            messages.success(request,
                             'Заявка на получение доступа создана. Вскоре сотрудники библиотеки её рассмотрят.')
        else:
            messages.error(request, 'Такая заявка уже существует.')
    else:
        messages.success(request, 'У вас уже есть доступ к этой библиотеке.')

    return redirect(request.META.get('HTTP_REFERER', '/reader-cabinet/'))


@login_required
@group_required('Читатели')
def settings(request):
    """Отображает страницу настроек."""
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            request.user.email = request.POST['email']
            if request.POST.get('password'):
                request.user.set_password(request.POST['password'])
            request.user.save()
            login(request, request.user)
            messages.success(request, 'Данные успешно сохранены')
            return redirect(reverse('reader_cabinet:settings'))
    else:
        form = SettingsForm(initial={'email': request.user.email})
    return render(request, 'reader_cabinet/settings.html', {'form': form})


@login_required
@group_required('Читатели')
@require_POST
def add_document_comment(request, document_id):
    """Создаёт комментарий к документу."""
    comment = Comment(text=request.POST['text'], user=request.user)
    comment.save()

    document = Document.objects.get(pk=document_id)
    document.comments.add(comment)
    document.save()

    messages.success(request, 'Отзыв успешно сохранён.')

    return redirect(reverse('reader_cabinet:document_show', args=[document_id]))


@login_required
@group_required('Читатели')
@require_POST
def add_library_comment(request, library_id):
    """Создаёт комментарий к библиотеке."""
    comment = Comment(text=request.POST['text'], user=request.user)
    comment.save()

    library = Library.objects.get(pk=library_id)
    library.comments.add(comment)
    library.save()

    messages.success(request, 'Отзыв успешно сохранён. После прохождения модерации он появится на странице.')

    return redirect(reverse('reader_cabinet:library_show', args=[library_id]))


class CommentsListView(generic.ListView):
    """Выводит страницу со списком комментариев."""
    template_name = 'reader_cabinet/comments/list.html'
    context_object_name = 'comments_list'

    def get_queryset(self):
        """Возвращает список с комментариями текущего юзера."""
        return Comment.objects.filter(user=self.request.user).order_by('-updated_at')

    @method_decorator(login_required, group_required('Читатели'))
    def dispatch(self, *args, **kwargs):
        return super(CommentsListView, self).dispatch(*args, **kwargs)


class CommentDetailView(generic.DetailView):
    """Выводит страницу с описанием комментария."""
    template_name = 'reader_cabinet/comments/detail.html'

    def get_queryset(self):
        """Возвращает список с комментариями текущего юзера."""
        return Comment.objects.filter(user=self.request.user)

    @method_decorator(login_required)
    @method_decorator(group_required('Читатели'))
    def dispatch(self, *args, **kwargs):
        return super(CommentDetailView, self).dispatch(*args, **kwargs)


@login_required
@group_required('Читатели')
def comment_delete(request, pk):
    """Удаляет комментарий."""
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    comment.delete()
    messages.success(request, 'Комментарий успешно удалён')

    redirect_to = request.GET.get('redirect_to')
    if not redirect_to:
        return redirect(request.META.get('HTTP_REFERER', '/reader-cabinet/my-comments/list/'))
    else:
        return redirect(redirect_to)
