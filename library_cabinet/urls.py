from django.conf.urls import url

from . import views

app_name = 'library_cabinet'
urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^orders/list/$', views.OrdersListView.as_view(), name='orders_list'),
    url(r'^orders/show/(?P<pk>[0-9]+)/$', views.OrderDetailView.as_view(), name='order_detail'),
    url(r'^orders/approve-order/(?P<pk>[0-9]+)/$', views.approve_order, name='approve_order'),
    url(r'^orders/issue-document/(?P<pk>[0-9]+)/$', views.issue_document, name='issue_document'),
    url(r'^orders/pass-document/(?P<pk>[0-9]+)/$', views.pass_document, name='pass_document'),
    url(r'^request-accesses/list/$', views.RequestAccessesListView.as_view(), name='request_accesses_list'),
    url(r'^request-accesses/approve/(?P<pk>[0-9]+)/$', views.approve_request_access, name='approve_request_access'),
    url(r'^readers/list/$', views.ReadersListView.as_view(), name='readers_list'),
    url(r'^readers/show/(?P<pk>[0-9]+)/$', views.ReaderDetailView.as_view(), name='reader_detail'),
    url(r'^documents/list/$', views.DocumentsListView.as_view(), name='documents_list'),
    url(r'^documents/show/(?P<pk>[0-9]+)/$', views.DocumentDetailView.as_view(), name='document_detail'),
    url(r'^documents/edit/(?P<pk>[0-9]+)/$', views.document_edit, name='document_edit'),
    url(r'^documents/create/$', views.document_create, name='document_create'),
    url(r'^documents/utilize/(?P<pk>[0-9]+)/$', views.document_utilize, name='document_utilize'),
    url(r'^another-persons/add/$', views.add_another_person, name='add_another_person'),
    url(r'^rubrics/add/$', views.add_rubric, name='add_rubric'),
    url(r'^time-limits/$', views.time_limits, name='time_limits'),
    url(r'^library-settings/$', views.library_settings, name='library_settings'),
    url(r'^user-settings/$', views.user_settings, name='user_settings'),
    url(r'^users/list/$', views.UsersListView.as_view(), name='users_list'),
    url(r'^users/deactivate/(?P<pk>[0-9]+)/$', views.deactivate_user, name='deactivate_user'),
    url(r'^users/activate/(?P<pk>[0-9]+)/$', views.activate_user, name='activate_user'),
    url(r'^users/show/(?P<pk>[0-9]+)/$', views.UserDetailView.as_view(), name='user_detail'),
    url(r'^users/edit/(?P<pk>[0-9]+)/$', views.edit_user, name='user_edit'),
    url(r'^users/create/$', views.create_user, name='user_create'),
    url(r'^comments/list/$', views.CommentsListView.as_view(), name='comments_list'),
    url(r'^comments/show/(?P<pk>[0-9]+)/$', views.CommentDetailView.as_view(), name='comment_show'),
    url(r'^comments/delete/(?P<pk>[0-9]+)/$', views.comment_delete, name='comment_delete'),
    url(r'^comments/moderate/(?P<pk>[0-9]+)/$', views.comment_moderate, name='comment_moderate'),
    url(r'^reports/library-fund/$', views.report_library_fund, name='report_library_fund'),
    url(r'^reports/orders/$', views.report_orders, name='report_orders'),
    url(r'^reports/staff/$', views.report_staff, name='report_staff'),
    url(r'^reports/orders-acquisitions/$', views.report_orders_acquisitions, name='report_orders_acquisitions'),
    url(r'^reports/entered-documents/$', views.report_entered_documents, name='report_entered_documents'),
]