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
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import auth
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404
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
from models import *


# the render shortcut
def _render(request, template, context_dict=None, **kwargs):
    
    # for the AB test
    ab_paths = ['/faster-data/', '/get-alerts/']
    if request.path in ab_paths:
        request.session['AB_TEST_COMPLETE'] = True
        context_dict['ab_test_complete'] = True
    
    try:
        context_dict['ab_test_complete'] = request.session['AB_TEST_COMPLETE']
    except:
        pass
        
    return render_to_response(
        template, context_dict or {}, context_instance=RequestContext(request),
                              **kwargs
    )



def strip_non_numbers(string):
    """Returns a string of numbers without annoying currency signs"""
    stripped = (c for c in string if not c.isdigit())
    return ''.join(stripped)


def nearest(ts):
    # Given a presorted list of timestamps:  s = sorted(index)
    i = bisect_left(s, ts)
    return min(s[max(0, i-1): i+2], key=lambda t: abs(ts - t))
    


#@cache_page(60 * 2)
def home(request): 

    """ The principle here is that we get everything from Redis, to save hitting
    the sites constantly. There's a background task scraping the sites every few 
    minutes. If we have no data, show no data. If the data is out of date, then 
    show a warning saying this could be out of date. 
    
    The redis stored data should be something like:
    
        'key': timestamp,
        'site1': {}, # dictionary of values
        'site2': {}, # dictionary of values etc.
        '': # currencies
    
    The keys will be something like this:
    
        '2013-12-02-0600' this means 2nd December 2013, 6am
    
    """
    
    now = datetime.now()
    
    
    # GET TODAY'S EXCHANGE RATES
    key = 'FX-%s-%s-%s' % (now.year, now.month, now.day)
    fx_rates = _search_redis(key)
    
    
    buy_data = []
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
            
        buy_data.append(result) 
                    
    return _render(request, 'home.html', locals())


def buy(request, id):
    return


def page(request, slug):
    
    template = '%s.html' % slug
    
    return _render(request, template, locals())  


    
    
    
    
    
    