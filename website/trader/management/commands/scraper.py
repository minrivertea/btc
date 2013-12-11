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
    help = 'Scrapes a list of sites and adds data to Redis'

    def handle_noargs(self, **options):
        
        now = datetime.now()
        
        
        # GET THE EXCHANGE RATES
        currency_key = 'FX-%s-%s-%s' % (now.year, now.month, now.day)
        if not _search_redis(currency_key):
            
            currency_mapping = {}

            # FROM OPENEXCHANGERATES.ORG
            try:
                r = requests.get('http://openexchangerates.org/api/latest.json?app_id=16924ac0d18643f5b37c73e370b9a366')
                j = simplejson.loads(r.content)
                # remember base currency is USD
                currency_mapping['USD_GBP'] = j['rates']['GBP'] # eg. 1.645
                currency_mapping['USD_EUR'] = j['rates']['EUR']
                
                currency_mapping['GBP_USD'] = (1/j['rates']['GBP'])
                currency_mapping['GBP_EUR'] = j['rates']['GBP']/j['rates']['EUR']
                
                currency_mapping['EUR_GBP'] = j['rates']['EUR']/j['rates']['GBP']
                currency_mapping['EUR_USD'] = (1/j['rates']['EUR'])
            except:
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
                
                currency_mapping['GBP_RMB'] = rmb_gbp_buy_rate
                currency_mapping['USD_RMB'] = rmb_usd_buy_rate
                currency_mapping['EUR_RMB'] = rmb_eur_buy_rate
                currency_mapping['RMB_USD'] = (1/rmb_usd_sell_rate)
                currency_mapping['RMB_GBP'] = (1/rmb_gbp_sell_rate)
                currency_mapping['RMB_EUR'] = (1/rmb_eur_sell_rate)
                
                
            except requests.ConnectionError:
                print "failed to add BOC rates"
        
            _add_to_redis(currency_key, currency_mapping)
        
        
        # THIS PROVIDES THE BASE KEY FOR ALL THE SITES WE'LL ADD
        rounded_now = now - timedelta(minutes=now.minute % settings.SCRAPE_INTERVAL,
                                 seconds=now.second,
                                 microseconds=now.microsecond)
        base_key = rounded_now.strftime("%Y-%m-%d-%H%M")   

        
        
        site = 'MTGOX'
        try:
            r = requests.get('http://data.mtgox.com/api/2/BTCGBP/money/ticker_fast')
            j = simplejson.loads(r.content)    
            mapping = {}
            mapping['name'] = site
            mapping['url'] = 'http://www.mtgox.com'
            mapping['price'] = '%.2f' % float(j['data']['buy']['value'])
            mapping['curr'] = j['data']['buy']['currency']
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        except JSONDecodeError:
            print "Failed to add %s prices" % site
            
        
        site = 'BITTYLICIOUS'
        try:
            # BITTYLICIOUS (ALWAYS GBP)
            r = requests.get('https://bittylicious.com/api/v1/quote/BTC/GB/GBP/BANK/1')
            j = simplejson.loads(r.content)
            mapping = {}
            mapping['name'] = 'Bittylicious'
            mapping['url'] = 'http://www.bittylicious.com'
            mapping['price'] = '%.2f' % float(j['totalPrice'])
            mapping['curr'] = 'GBP'
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        except:
            print "failed to add %s prices" % site
            
            
            
        site = "BITSTAMP"            
        try:    
            r = requests.get('https://www.bitstamp.net/api/ticker/')
            j = simplejson.loads(r.content)
            mapping = {}
            mapping['name'] = site
            mapping['url'] = 'http://www.bitstamp.net'
            mapping['price'] = '%.2f' % float(j['last'])
            mapping['curr'] = 'USD'
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        except:
            print "failed to add %s prices" % site
        
        
        site = "BTC-E"
        try:
            r = requests.get('https://btc-e.com/api/2/btc_usd/ticker')
            j = simplejson.loads(r.content)
            mapping = {}
            mapping['name'] = site
            mapping['url'] = 'http://www.btc-e.com'
            mapping['price'] = '%.2f' % float(j['ticker']['last'])
            mapping['curr'] = 'USD'
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        except:
            print "Failed to add %s prices" % site
       
       
        site = "BTCTRADE"        
        try:
            r = requests.get('http://www.btcclubs.com/btc_sum.js?t=6428515')
            j = simplejson.loads(r.content)
            total = 0
            count = 0
            for item in j['buy']:
                total += float(item['p'])
                count += 1
            mapping = {}
            mapping['name'] = site
            mapping['url'] = 'http://www.btcclubs.com'
            mapping['price'] = "%.2f" % float(total/count)
            mapping['curr'] = 'RMB'
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
            
        except:
            print "Failed to add %s prices" % site
        
        
        site = "HUOBI"
        try:
            r = requests.get('https://www.huobi.com/market/huobi.php?a=detail&jsoncallback=jQuery1710527118019146838_1386320502376&_=1386320662397', verify=False)
            content = r.content.lstrip('jQuery1710527118019146838_1386320502376').replace('(', '').replace(')', '')    
            j = simplejson.loads(content)
            mapping = {}
            mapping['name'] = site
            mapping['url'] = "http://www.huobi.com"
            mapping['price'] = j['sells'][0]['price']
            mapping['curr'] = 'RMB'
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        except:
            print "Failed to add %s prices" % site
            


        site = "CHBTC"
        try:
            r = requests.get('https://www.chbtc.com/data/userticker')
            j = simplejson.loads(r.content)
            mapping = {}
            mapping['name'] = site
            mapping['url'] = 'http://www.chbtc.com'
            mapping['price'] = "%.2f" % float(j['ticker']['sell'])
            mapping['curr'] = 'RMB'
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        except:
            print "Failed to add %s prices" % site
            
        
        site = "BTCCHINA"
        try:
            r = requests.get('http://www.btcchina.com/bc/ticker')
            j = simplejson.loads(r.content)
            mapping = {}
            mapping['name'] = site
            mapping['url'] = 'http://www.btcchina.com'
            mapping['price'] = "%.2f" % float(j['ticker']['sell'])
            mapping['curr'] = 'RMB'
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        except:
            print "Failed to add %s prices" % site    

        
        
        site = "796"
        try:
            r = requests.get('http://api.796.com/apiV2/ticker.html?op=futures')
            j = simplejson.loads(r.content)
            mapping = {}
            mapping['name'] = site
            mapping['url'] = 'https://796.com'
            mapping['price'] = "%.2f" % float(j['return']['last'])
            mapping['curr'] = 'USD'
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        except:
            print "Failed to add %s prices" % site 
        
        
        site = "BTC38"
        try:
            r = requests.get('http://www.btc38.com/trade/getTradeList.php?coinname=BTC')
            j = simplejson.loads(r.content.strip())
            mapping = {}
            mapping['name'] = site
            mapping['url'] = 'https://www.btc38.com'
            
            count = 0
            total = 0
            for x in j['buyOrder']:
                count += 1
                total += x['price']
            
            mapping['price'] = "%.2f" % float(total/count)
            mapping['curr'] = 'RMB'
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        except JSONDecodeError:
            print "Failed to add %s prices (%s)" % (site, 'JSONDecodeError')
        except requests.ConnectionError:
            print "Failed to add %s prices (%s)" % (site, 'Connection Error')
        
        
        
        site = "BTER"
        try:
            r = requests.get('https://bter.com/api/1/ticker/btc_cny')
            j = simplejson.loads(r.content.strip())
            mapping = {}
            mapping['name'] = site
            mapping['url'] = 'https://www.bter.com'
            mapping['price'] = "%.2f" % float(j['avg'])
            mapping['curr'] = 'RMB'
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        except JSONDecodeError:
            print "Failed to add %s prices (%s)" % (site, 'JSONDecodeError')
        
        
        
        site = 'OKCOIN'
        # {"ticker": {"buy": "5730.0", "high":"5887.0", "last":"5730.5", "low":"5250.0","sell": "5730.5", "vol":"50207.4845"}}
        try:
            r = requests.get('https://www.okcoin.com/api/ticker.do')
            j = simplejson.loads(r.content.strip())
            mapping = {}
            mapping['name'] = site
            mapping['url'] = 'https://www.okcoin.com'
            mapping['price'] = "%.2f" % float(j['ticker']['buy'])
            mapping['curr'] = 'RMB'
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        except JSONDecodeError:
            print "Failed to add %s prices (%s)" % (site, 'JSONDecodeError')
            
                
        
        site = 'FxBTC'
        try:
            r = requests.get('https://data.fxbtc.com/api?op=query_ticker&symbol=btc_cny')
            j = simplejson.loads(r.content.strip())
            mapping = {}
            mapping['name'] = site
            mapping['url'] = 'https://www.fxbtc.com'
            mapping['price'] = "%.2f" % float(j['ticker']['last_rate'])
            mapping['curr'] = 'RMB'
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        
        except JSONDecodeError:
            print "Failed to add %s prices (%s)" % (site, 'JSONDecodeError')
        
               
        #site = 'GOXBTC'
        #https://www.goxbtc.com/homepage/createOrderInfo.json
        
        site = 'RMBTB'
        #{"ticker":{"high":"596.0000", "low":"570.0000", "buy":"580.0000", "sell":"584.9900", "last":"583.0000", "vol":"1281.9785"}}
        try:
            r = requests.get('http://www.rmbtb.com/api/thirdparty/ticker/')
            j = simplejson.loads(r.content.strip())
            mapping = {}
            mapping['name'] = site
            mapping['url'] = 'https://www.rmbtb.com'
            mapping['price'] = "%.2f" % float(j['ticker']['buy'])
            mapping['curr'] = 'RMB'
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        
        except JSONDecodeError:
            print "Failed to add %s prices (%s)" % (site, 'JSONDecodeError')
        
        
        
        
        
        
        
