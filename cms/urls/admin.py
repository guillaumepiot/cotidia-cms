from django.conf.urls import url, patterns

from cms.views.admin import *
from cms.views.image import ImageList, ImageDelete

urlpatterns = patterns(
    '',
    url(r'^$', PageList.as_view(), name='page_list'),
    url(r'^page/add/$', PageCreate.as_view(), name='page_add'),
    url(r'^page/(?P<pk>[\d]+)/$', PageDetail.as_view(), name='page_detail'),
    url(r'^page/(?P<pk>[\d]+)/update/$', PageUpdate.as_view(), name='page_update'),
    url(r'^page/(?P<pk>[\d]+)/delete/$', PageDelete.as_view(), name='page_delete'),

    url(r'^page/(?P<page_id>[\d]+)/(?P<lang>[a-z]+)/url/add/$', 
        PageURLCreate, name='page_url_add'),
    url(r'^page/(?P<page_id>[\d]+)/(?P<lang>[a-z]+)/url/(?P<trans_id>[\d]+)/update/$', 
        PageURLUpdate, name='page_url_update'),

    url(r'^page/(?P<page_id>[\d]+)/(?P<lang>[a-z]+)/title/add/$', 
        PageTitleUpdate, name='page_title_add'),
    url(r'^page/(?P<page_id>[\d]+)/(?P<lang>[a-z]+)/title/(?P<trans_id>[\d]+)/update/$', 
        PageTitleUpdate, name='page_title_update'),

    url(r'^page/(?P<page_id>[\d]+)/publish/$', 
        PagePublish, name='page_publish'),

    url(r'^page/(?P<page_id>[\d]+)/unpublish/$', 
        PageUnpublish, name='page_unpublish'),

    url(r'^image/$', ImageList.as_view(), name='image_list'),
    url(r'^image/(?P<pk>[\d]+)/delete/$', ImageDelete.as_view(), name='image_delete'),

)
