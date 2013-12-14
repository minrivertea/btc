from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from trader import views as trader_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('website.trader.urls')),
    url(r'^api/', include('website.api.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
    
    
    url(r'^(?P<slug>[\w-]+)/$', trader_views.page, name="page"),
    
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()

