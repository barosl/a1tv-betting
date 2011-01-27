from django.conf.urls.defaults import *

from views import *

urlpatterns = patterns('',
	(r'^$', index),
	(r'^update_matches/$', update_matches),
	(r'^update_points/$', update_points),
	(r'^matches/$', matches),
)
