from django.conf.urls import url

from . import views

app_name = 'reader_cabinet'
urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^my-ticket/$', views.reader_ticket, name='reader_ticket'),
    url(r'^simple-search/$', views.simple_search, name='simple_search'),
    url(r'^extended-search/$', views.extended_search, name='extended_search'),
    url(r'^document/show/(?P<pk>[0-9]+)/$', views.DocumentDetailView.as_view(), name='document_show'),
    url(r'^library/show/(?P<pk>[0-9]+)/$', views.LibraryDetailView.as_view(), name='library_show'),
    url(r'^my-orders/list/$', views.OrdersListView.as_view(), name='orders_list'),
    url(r'^my-orders/show/(?P<pk>[0-9]+)/$', views.OrderDetailView.as_view(), name='order_detail'),
    url(r'^document/create-order/(?P<pk>[0-9]+)/$', views.create_order, name='create_order'),
    url(r'^library/access-request/(?P<library_id>[0-9]+)/$', views.access_request, name='access_request'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^add-document-comment/(?P<document_id>[0-9]+)/$', views.add_document_comment, name='add_document_comment'),
    url(r'^add-library-comment/(?P<library_id>[0-9]+)/$', views.add_library_comment, name='add_library_comment'),
    url(r'^my-comments/list/$', views.CommentsListView.as_view(), name='comments_list'),
    url(r'^my-comments/show/(?P<pk>[0-9]+)/$', views.CommentDetailView.as_view(), name='comment_show'),
    url(r'^my-comments/delete/(?P<pk>[0-9]+)/$', views.comment_delete, name='comment_delete'),
]
