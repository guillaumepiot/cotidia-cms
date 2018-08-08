from django.conf.urls import url

# from cotidia.cms.api.image import *
from cotidia.cms.api.page import RegionUpdate

app_name = 'cotidia.cms'

urlpatterns = [
    url(
        r'^update/(?P<id>[-\d]+)/$',
        RegionUpdate.as_view(),
        name='update'
    ),
]
