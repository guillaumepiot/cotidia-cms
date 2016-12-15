from django.conf.urls import url

from cotidia.cms.views.public import page

urlpatterns = [
	url(r'^$', page, name="home"),
	url(r'^(?P<slug>[-\w\/]+)/$', page, name="page"),
]
