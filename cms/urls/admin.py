from django.conf.urls import url

from cms.views.admin import *
from cms.views.image import ImageList, ImageDelete
from cms.views.dataset import *

urlpatterns =[
    url(r'^$', PageList.as_view(), name='page-list'),
    url(r'^page/add/$', PageCreate.as_view(), name='page-add'),
    url(r'^page/(?P<pk>[\d]+)/$', PageDetail.as_view(), name='page-detail'),
    url(r'^page/(?P<pk>[\d]+)/update/$', PageUpdate.as_view(), name='page-update'),
    url(r'^page/(?P<pk>[\d]+)/delete/$', PageDelete.as_view(), name='page-delete'),
    
    url(r'^page/(?P<page_id>[\d]+)/meta-data/(?P<language_code>[-\w]+)/', add_edit_translation, name='page-metadata-update'),
    
    url(r'^page/(?P<page_id>[\d]+)/(?P<lang>[-\w]+)/url/add/$', 
        PageURLCreate, name='page-url-add'),
    url(r'^page/(?P<page_id>[\d]+)/(?P<lang>[-\w]+)/url/(?P<trans_id>[\d]+)/update/$', 
        PageURLUpdate, name='page-url-update'),

    url(r'^page/(?P<page_id>[\d]+)/(?P<lang>[-\w]+)/title/add/$', 
        PageTitleUpdate, name='page-title-add'),
    url(r'^page/(?P<page_id>[\d]+)/(?P<lang>[-\w]+)/title/(?P<trans_id>[\d]+)/update/$', 
        PageTitleUpdate, name='page-title-update'),

    url(r'^page/(?P<page_id>[\d]+)/publish/$', 
        PagePublish, name='page-publish'),

    url(r'^page/(?P<page_id>[\d]+)/unpublish/$', 
        PageUnpublish, name='page-unpublish'),

    url(r'^image/$', ImageList.as_view(), name='image-list'),
    url(r'^image/(?P<pk>[\d]+)/delete/$', ImageDelete.as_view(), name='image-delete'),

    url(r'^dataset/$', PageDataSetList.as_view(), name='pagedataset-list'),
    url(r'^dataset/add/$', PageDataSetCreate.as_view(), name='pagedataset-add'),
    url(r'^dataset/(?P<pk>[\d]+)/$', PageDataSetDetail.as_view(), name='pagedataset-detail'),
    url(r'^dataset/(?P<pk>[\d]+)/update/$', PageDataSetUpdate.as_view(), name='pagedataset-update'),
    url(r'^dataset/(?P<pk>[\d]+)/delete/$', PageDataSetDelete.as_view(), name='pagedataset-delete'),
]