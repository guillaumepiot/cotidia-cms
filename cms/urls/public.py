from django.conf.urls import url

urlpatterns = [
	url(r'^$', 'cms.views.public.page', name="home"),
	url(r'^(?P<slug>[-\w\/]+)/$', 'cms.views.public.page', name="page"),
]