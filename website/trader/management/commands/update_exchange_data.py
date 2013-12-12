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
        
        # THIS PROVIDES THE BASE KEY FOR ALL THE SITES WE'LL ADD
        rounded_now = now - timedelta(minutes=now.minute % settings.SCRAPE_INTERVAL,
                                 seconds=now.second,
                                 microseconds=now.microsecond)
        base_key = rounded_now.strftime("%Y-%m-%d-%H%M")   

        
        
        site = 'MTGOX (GBP)'
        try:
            r = requests.get('https://data.mtgox.com/api/2/BTCGBP/money/ticker_fast')
            j = simplejson.loads(r.content)    
            mapping = {}
            mapping['name'] = site
            mapping['parent'] = 'MTGOX'
            mapping['url'] = 'http://www.mtgox.com'
            mapping['price'] = '%.2f' % float(j['data']['buy']['value'])
            mapping['curr'] = j['data']['buy']['currency']
            mapping['trade_fee'] = '0.006' # this is a percent where 1 = 100%
            mapping['transfer_fee'] = '0.001' # this is a BTC
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        except JSONDecodeError:
            print "Failed to add %s prices (JSONDecodeError)" % site
        
        
        site = 'MTGOX (USD)'
        try:
            r = requests.get('https://data.mtgox.com/api/2/BTCUSD/money/ticker_fast')
            j = simplejson.loads(r.content)    
            mapping = {}
            mapping['name'] = site
            mapping['parent'] = 'MTGOX'
            mapping['url'] = 'http://www.mtgox.com'
            mapping['price'] = '%.2f' % float(j['data']['buy']['value'])
            mapping['curr'] = j['data']['buy']['currency']
            mapping['trade_fee'] = '0.006' # this is a percent where 1 = 100%
            mapping['transfer_fee'] = '0.001' # this is a BTC
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        except JSONDecodeError:
            print "Failed to add %s prices (JSONDecodeError)" % site
         
         
         
        site = 'MTGOX (EUR)'
        try:
            r = requests.get('https://data.mtgox.com/api/2/BTCEUR/money/ticker_fast')
            j = simplejson.loads(r.content)    
            mapping = {}
            mapping['name'] = site
            mapping['parent'] = 'MTGOX'
            mapping['url'] = 'http://www.mtgox.com'
            mapping['price'] = '%.2f' % float(j['data']['buy']['value'])
            mapping['curr'] = j['data']['buy']['currency']
            mapping['trade_fee'] = '0.006' # this is a percent where 1 = 100%
            mapping['transfer_fee'] = '0.001' # this is a BTC
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        except JSONDecodeError:
            print "Failed to add %s prices (JSONDecodeError)" % site
            
               
        
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
            mapping['trade_fee'] = '0.01' # this is a percent
            mapping['transfer_fee'] = '0' # this is a BTC
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        except JSONDecodeError:
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
            mapping['trade_fee'] = '0' # this is a percent
            mapping['transfer_fee'] = '0.001' # this is a BTC
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
            mapping['trade_fee'] = '0' # this is a percent
            mapping['transfer_fee'] = '0.001' # this is a BTC
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
            mapping['trade_fee'] = '0' # this is a percent
            mapping['transfer_fee'] = '0.001' # this is a BTC
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
            mapping['trade_fee'] = '0' # this is a percent
            mapping['transfer_fee'] = '0.001' # this is a BTC
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
            mapping['trade_fee'] = '0' # this is a percent
            mapping['transfer_fee'] = '0.001' # this is a BTC
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
            mapping['trade_fee'] = '0' # this is a percent
            mapping['transfer_fee'] = '0.001' # this is a BTC
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
            mapping['trade_fee'] = '0' # this is a percent
            mapping['transfer_fee'] = '0.001' # this is a BTC
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
            mapping['trade_fee'] = '0' # this is a percent
            mapping['transfer_fee'] = '0.001' # this is a BTC
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
            mapping['trade_fee'] = '0' # this is a percent
            mapping['transfer_fee'] = '0.001' # this is a BTC
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
            mapping['trade_fee'] = '0' # this is a percent
            mapping['transfer_fee'] = '0.001' # this is a BTC
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
            mapping['trade_fee'] = '0' # this is a percent
            mapping['transfer_fee'] = '0.001' # this is a BTC
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        
        except JSONDecodeError:
            print "Failed to add %s prices (%s)" % (site, 'JSONDecodeError')
        except requests.ConnectionError:
            print "Failed to add %s prices (%s)" % (site, 'ConnectionError')
        
               
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
            mapping['trade_fee'] = '0' # this is a percent
            mapping['transfer_fee'] = '0.001' # this is a BTC
            key = "%s:%s" % (base_key, site)
            _add_to_redis(key, mapping)
        
        except JSONDecodeError:
            print "Failed to add %s prices (%s)" % (site, 'JSONDecodeError')
        
        
        
        
        
        
        
