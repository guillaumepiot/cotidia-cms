from django.conf.urls import url

from cotidia.cms.views.public import page, browserconfig

urlpatterns = [
    url(r'^$', page, name="home"),
    url(r'^browserconfig\.xml$', browserconfig, name="browserconfig"),
    url(r'^(?P<slug>[-\w\/]+)/$', page, name="page"),
]
