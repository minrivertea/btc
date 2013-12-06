from django.conf import settings
from models import *
from itertools import chain


def common(request):
    context = {}
    context['base_template'] = settings.BASE_TEMPLATE
    return context
    
  