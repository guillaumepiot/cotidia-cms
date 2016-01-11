from django.conf.urls import url

from cms.api.image import *
from cms.api.page import *

urlpatterns = [
    
    url(r'^update/(?P<id>[-\d]+)/$', 
        RegionUpdate.as_view(), name='update'),

    url(r'^images/add/$', ImageAdd.as_view(), 
        name='image-add'),
    
    url(r'^images/update/(?P<id>[-\d]+)/$', ImageUpdate.as_view(), 
        name='image-update'),
    
    url(r'^images/list/$', ImageList.as_view(), 
        name='image-list'),
]
