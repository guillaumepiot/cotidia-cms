from django.conf.urls import patterns, include, url

urlpatterns = patterns('cms.views.public',
	url(r'^$', 'page', name="home"),
	url(r'^(?P<slug>[-\w\/]+)/$', 'page', name="page"),
)