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


# APP
from website.redis_helper import _get_redis, _search_redis
from models import *


# the render shortcut
def _render(request, template, context_dict=None, **kwargs):
        
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
    

def _scraper(request):    
    
    # GET THE RMB PRICE ON btctrade.com
    r = requests.get('http://www.btctrade.com/btc_sum')
    j = simplejson.loads(r.content)
    total = 0
    count = 0
    for item in j['buy']:
        total += float(item['p'])
        count += 1
    rmb_price = total / count
    
    
    # get the GBP buy price right now
    r = requests.get('http://blockchain.info/ticker')
    j = simplejson.loads(r.content)  
    gbp_price =  j['GBP']['buy']
    usd_price = j['USD']['buy']
    eur_price = j['EUR']['buy']
    
    
    # get the GBP:RMB exchange rate today
    r = requests.get('http://www.boc.cn/sourcedb/whpj/enindex.html')
    soup = BeautifulSoup(r.content)
    rmb_gbp_buy_rate = float(soup.body.find_all('td', text='GBP')[0].findNextSibling('td').text)
    rmb_gbp_sell_rate = float(soup.body.find_all('td', text='GBP')[0].findNextSibling('td').findNextSibling('td').findNextSibling('td').text)
    
    
    rmb_usd_fx_rate = float(soup.body.find_all('td', text='USD')[0].findNextSibling('td').text)
    rmb_eur_fx_rate = float(soup.body.find_all('td', text='EUR')[0].findNextSibling('td').text)
    
    
    mtgox_commission = 0.006
    okpay_fee = 0.00
    swift_fee = 17 # GBP
    btctrade_fee = 0.005
    
    
    initial = 260 # GBP
    
    
    # THE INITIAL PURCHASE IN EUR
    print "*" * 80
    print "Initial investment: %s GBP" % initial
    print "  GBP price = %s" % 520
    cash = (initial - (initial * okpay_fee))
    print "  Initial minus OKpay transfer fee: %s" % cash
    btc_purchased = 0.5 #((initial - (initial * mtgox_commission)) / 520)
    print "  Purchases %s BTC" % btc_purchased
    
    
    # THE RMB TRANSFER
    print ""
    print "Now selling %s BTC at %s RMB" % (btc_purchased, rmb_price)
    rmb_total = ((btc_purchased - (btc_purchased * btctrade_fee)) * rmb_price)
    print "  Total RMB: %s " % rmb_total
    
    print ""
    print "A direct FX transfer would yield:"
    print "  RMB/GBP FX Rate: %s" % (rmb_gbp_buy_rate/100)
    fx_total = ((initial - swift_fee) * (rmb_gbp_buy_rate/100))
    print "  %s RMB" % fx_total
    
    print "" 
    print "TOTALS"
    profit = (rmb_total - fx_total)
    print "  Profit: %s RMB" % profit
    print "  GBP Equivalent: %s" % (profit / (rmb_gbp_sell_rate/100))
    total_gbp_output = (rmb_total / (rmb_gbp_sell_rate/100))
    print "  Total output: %s" % total_gbp_output
    print "  Percent change: %s" % (((total_gbp_output/initial) * 100)-100)
    print "*" * 80
    
    return locals()



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
    
    
    # GET TODAY'S BOC EXCHANGE RATES
    key = 'FX-%s-%s-%s' % (now.year, now.month, now.day)
    fx_rates = _search_redis(key)
    
    fx_rates = ast.literal_eval(fx_rates['rates'])
    
    fx_data = []
    for x in fx_rates:
        mapping = {}
        
        mapping['buy_curr'] = x['name']
        mapping['sell_curr'] = 'RMB'
        mapping['price'] = x['buy']
        fx_data.append(mapping)    
        
        mapping = {}
        mapping['buy_curr'] = 'RMB'
        mapping['sell_curr'] = x['name']
        mapping['price'] = (1 / x['sell'])
        fx_data.append(mapping)
    
    
    
    
    
    # GET THE WESTERN BTC TRADE SITES
    buy_data = []
    sell_data = []
    for s in settings.WESTERN_SITES:
        rounded_now = now - timedelta(minutes=now.minute % 15,
                            seconds=now.second,
                            microseconds=now.microsecond)
        key = "%s:%s" % (rounded_now.strftime("%Y-%m-%d-%H%M"), s)
        result = _search_redis(key)
        
        if not result:
            rounded_now = now - timedelta(minutes=now.minute % 30,
                            seconds=now.second,
                            microseconds=now.microsecond)
            key = "%s:%s" % (rounded_now.strftime("%Y-%m-%d-%H%M"), s)
            result = _search_redis(key)
            if result:
                result['old'] = True
            
        buy_data.append(result)
        sell_data.append(result)
        
        
        
    # GET THE CHINESE SITES    
    
    for s in settings.CHINESE_SITES:
        rounded_now = now - timedelta(minutes=now.minute % 15,
                            seconds=now.second,
                            microseconds=now.microsecond)
        key = "%s:%s" % (rounded_now.strftime("%Y-%m-%d-%H%M"), s)
        result = _search_redis(key)
        
        if not result:
            rounded_now = now - timedelta(minutes=now.minute % 30,
                            seconds=now.second,
                            microseconds=now.microsecond)
            key = "%s:%s" % (rounded_now.strftime("%Y-%m-%d-%H%M"), s)
            result = _search_redis(key)
            if result:
                result['old'] = True
        
        buy_data.append(result)
        sell_data.append(result)
                
    return _render(request, 'home.html', locals())


def buy(request, id):
    return
