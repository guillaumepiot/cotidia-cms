from django.urls import path

from cotidia.cms.views.public import page, browserconfig

app_name = 'cotidia.cms'

urlpatterns = [
    path('', page, name="home"),
    path('browserconfig\.xml', browserconfig, name="browserconfig"),
    path('(?P<slug>[-\w\/]+)', page, name="page"),
]
