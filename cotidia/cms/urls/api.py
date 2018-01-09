from django.conf.urls import url

# from cotidia.cms.api.image import *
from cotidia.cms.api.page import RegionUpdate

app_name = 'cotidia.cms'

urlpatterns = [

    url(r'^update/(?P<id>[-\d]+)/$',
        RegionUpdate.as_view(), name='update'),

    # url(r'^images/add/$', ImageAdd.as_view(),
    #     name='image-add'),

    # url(r'^images/update/(?P<id>[-\d]+)/$', ImageUpdate.as_view(),
    #     name='image-update'),

    # url(r'^images/list/$', ImageList.as_view(),
    #     name='image-list'),
]
