from django.conf.urls import url

from cotidia.cms.views.admin.page import (
    PageList,
    PageCreate,
    PageDetail,
    PageUpdate,
    PageDelete,
    PagePublish,
    PageUnpublish
)
from cotidia.cms.views.admin.page_title import (
    PageTitleCreate,
    PageTitleUpdate
)
from cotidia.cms.views.admin.page_url import (
    PageURLUpdate
)

app_name = 'cotidia.cms'

urlpatterns = [
    url(
        r'^$',
        PageList.as_view(),
        name='page-list'
    ),
    url(
        r'^page/add/$',
        PageCreate.as_view(),
        name='page-add'
    ),
    url(
        r'^page/(?P<pk>[\d]+)/$',
        PageDetail.as_view(),
        name='page-detail'),
    url(
        r'^page/(?P<pk>[\d]+)/update/$',
        PageUpdate.as_view(),
        name='page-update'),
    url(
        r'^page/(?P<pk>[\d]+)/delete/$',
        PageDelete.as_view(),
        name='page-delete'),
    url(
        r'^page/(?P<parent_id>[\d]+)/(?P<lang>[-\w]+)/url/(?P<pk>[\d]+)/update/$',
        PageURLUpdate.as_view(),
        name='page-url-update'),
    url(
        r'^page/(?P<parent_id>[\d]+)/(?P<lang>[-\w]+)/title/add/$',
        PageTitleCreate.as_view(),
        name='page-title-add'),
    url(
        r'^page/(?P<parent_id>[\d]+)/(?P<lang>[-\w]+)/title/(?P<pk>[\d]+)/update/$',
        PageTitleUpdate.as_view(),
        name='page-title-update'),
    url(
        r'^page/(?P<page_id>[\d]+)/publish/$',
        PagePublish,
        name='page-publish'),
    url(
        r'^page/(?P<page_id>[\d]+)/unpublish/$',
        PageUnpublish,
        name='page-unpublish'),
]
