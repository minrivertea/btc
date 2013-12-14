from django.conf.urls.defaults import *
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

import views

urlpatterns = patterns('',

    url(r'^exchanges/$', views.refresh_exchanges, name="refresh_exchanges"), # UPDATES EXCHANGE DATA
    url(r'^fx/$', views.refresh_fx, name="refresh_fx"), # REFRESHES FX DATA
        
)