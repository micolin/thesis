from django.conf.urls import patterns, include, url
from views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'MRP.views.home', name='home'),
    # url(r'^MRP/', include('MRP.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
	url(r'^home/$',home),
	url(r'^$',home),
	url(r'^about/$',about),
	url(r'^search/$',search),
	url(r'^detail/$',detail),
)
