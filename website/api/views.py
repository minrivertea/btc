#!/usr/bin/python
# -*- coding: utf8 -*-

# PYTHON CORE
import time
import requests
import simplejson
from simplejson import JSONDecodeError
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import ast

# DJANGO
from django.core import serializers
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import auth
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView


# APP
from website.redis_helper import _get_redis, _search_redis



def refresh_exchanges(request):
    
    now = datetime.now()
    response_data = []
    for s in settings.BITCOIN_EXCHANGES:
        rounded_now = now - timedelta(minutes=now.minute % settings.SCRAPE_INTERVAL,
                            seconds=now.second,
                            microseconds=now.microsecond)
        key = "%s:%s" % (rounded_now.strftime("%Y-%m-%d-%H%M"), s)
        result = _search_redis(key)
        if not result:
            rounded_now = rounded_now - timedelta(minutes=settings.SCRAPE_INTERVAL)
            key = "%s:%s" % (rounded_now.strftime("%Y-%m-%d-%H%M"), s)
            result = _search_redis(key)
            if not result:
                rounded_now = rounded_now - timedelta(minutes=settings.SCRAPE_INTERVAL)
                key = "%s:%s" % (rounded_now.strftime("%Y-%m-%d-%H%M"), s)
                result = _search_redis(key)
            
        response_data.append(result)
        
    
    return HttpResponse(simplejson.dumps(response_data), content_type="application/json")
   
   
        
def refresh_fx(request):
    
    now = datetime.now()
    key = 'FX-%s-%s-%s' % (now.year, now.month, now.day)
    response_data = _search_redis(key)
            
    return HttpResponse(simplejson.dumps(response_data), content_type="application/json")
        
        
    
    