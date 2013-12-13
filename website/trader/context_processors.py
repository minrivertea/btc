from django.conf import settings
from models import *
from itertools import chain


def common(request):
    context = {}
    context['base_template'] = settings.BASE_TEMPLATE
    context['scrape_interval'] = settings.SCRAPE_INTERVAL
    context['analytics_on'] = settings.ANALYTICS_ON
    context['site_url'] = settings.SITE_URL
    
    return context
    
  