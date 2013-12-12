#!/usr/bin/python
# -*- coding: utf8 -*-


# DJANGO
from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError

# PYTHON CORE
import time
import requests
import simplejson
from simplejson import JSONDecodeError
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# APP
from website.redis_helper import _get_redis, _add_to_redis, _search_redis




class Command(NoArgsCommand):
    help = 'Scrapes for exchange rate (FX) data from a variety of sources'

    def handle_noargs(self, **options):
        
        now = datetime.now()
        
        # GET THE EXCHANGE RATES
        currency_key = 'FX-%s-%s-%s' % (now.year, now.month, now.day)
        currency_mapping = {}

        # FROM OPENEXCHANGERATES.ORG
        try:
            r = requests.get('http://openexchangerates.org/api/latest.json?app_id=16924ac0d18643f5b37c73e370b9a366')
            j = simplejson.loads(r.content)
            # remember base currency is USD
            currency_mapping['USD_GBP_ideal'] = j['rates']['GBP'] 
            currency_mapping['USD_EUR_ideal'] = j['rates']['EUR']
            currency_mapping['USD_RMB_ideal'] = j['rates']['CNY']
            
            currency_mapping['GBP_USD_ideal'] = (1/j['rates']['GBP'])
            currency_mapping['GBP_EUR_ideal'] = j['rates']['EUR']/j['rates']['GBP']
            currency_mapping['GBP_RMB_ideal'] = (1/ (j['rates']['GBP']/j['rates']['CNY']))
            
            
            currency_mapping['EUR_GBP_ideal'] = j['rates']['GBP']/j['rates']['EUR']
            currency_mapping['EUR_USD_ideal'] = (1/j['rates']['EUR'])
            currency_mapping['EUR_RMB_ideal'] = (1/ (j['rates']['EUR']/j['rates']['CNY']))
            
            
            currency_mapping['RMB_USD_ideal'] = (1/j['rates']['CNY'])
            currency_mapping['RMB_GBP_ideal'] = (1/j['rates']['CNY']) * j['rates']['GBP']
            currency_mapping['RMB_EUR_ideal'] = (1/j['rates']['CNY']) * j['rates']['EUR']
            
            
            # faking these 'realworld' rates for now because we have no reliable source.
            currency_mapping['USD_GBP_real'] = j['rates']['GBP'] 
            currency_mapping['USD_EUR_real'] = j['rates']['EUR']
            currency_mapping['GBP_USD_real'] = (1/j['rates']['GBP'])
            currency_mapping['GBP_EUR_real'] = j['rates']['EUR']/j['rates']['GBP']
            currency_mapping['EUR_GBP_real'] = j['rates']['GBP']/j['rates']['EUR']
            currency_mapping['EUR_USD_real'] = (1/j['rates']['EUR'])


        except JSONDecodeError:
            print "Failed to get exchange rates from openexchangerates.org"
            
        
        # GET BANK OF CHINA EXCHANGE RATES
        try:
            r = requests.get('http://www.boc.cn/sourcedb/whpj/enindex.html')
            soup = BeautifulSoup(r.content)
            
            rmb_gbp_buy_rate = (float(soup.body.find_all('td', text='GBP')[0].findNextSibling('td').text) / 100)
            rmb_usd_buy_rate = (float(soup.body.find_all('td', text='USD')[0].findNextSibling('td').text) / 100)
            rmb_eur_buy_rate = (float(soup.body.find_all('td', text='EUR')[0].findNextSibling('td').text) / 100)
                        
            rmb_gbp_sell_rate = (float(soup.body.find_all('td', text='GBP')[0].findNextSibling('td').findNextSibling('td').findNextSibling('td').text) / 100)
            rmb_usd_sell_rate = (float(soup.body.find_all('td', text='USD')[0].findNextSibling('td').findNextSibling('td').findNextSibling('td').text) / 100)   
            rmb_eur_sell_rate = (float(soup.body.find_all('td', text='EUR')[0].findNextSibling('td').findNextSibling('td').findNextSibling('td').text) / 100)
            
            currency_mapping['GBP_RMB_real'] = rmb_gbp_buy_rate
            currency_mapping['USD_RMB_real'] = rmb_usd_buy_rate
            currency_mapping['EUR_RMB_real'] = rmb_eur_buy_rate
            
            currency_mapping['RMB_USD_real'] = (1/rmb_usd_sell_rate)
            currency_mapping['RMB_GBP_real'] = (1/rmb_gbp_sell_rate)
            currency_mapping['RMB_EUR_real'] = (1/rmb_eur_sell_rate)
            
            
        except requests.ConnectionError:
            print "failed to add BOC rates"
    
        _add_to_redis(currency_key, currency_mapping)
        