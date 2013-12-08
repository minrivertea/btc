
# DJANGO
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
        
        # GET BANK OF CHINA EXCHANGE RATES
        key = 'FX-%s-%s-%s' % (now.year, now.month, now.day)
        if not _search_redis(key):
            try:
                r = requests.get('http://www.boc.cn/sourcedb/whpj/enindex.html')
                soup = BeautifulSoup(r.content)
                
                rmb_gbp_buy_rate = (float(soup.body.find_all('td', text='GBP')[0].findNextSibling('td').text) / 100)
                rmb_usd_buy_rate = (float(soup.body.find_all('td', text='USD')[0].findNextSibling('td').text) / 100)
                rmb_eur_buy_rate = (float(soup.body.find_all('td', text='EUR')[0].findNextSibling('td').text) / 100)
                            
                rmb_gbp_sell_rate = (float(soup.body.find_all('td', text='GBP')[0].findNextSibling('td').findNextSibling('td').findNextSibling('td').text) / 100)
                rmb_usd_sell_rate = (float(soup.body.find_all('td', text='USD')[0].findNextSibling('td').findNextSibling('td').findNextSibling('td').text) / 100)   
                rmb_eur_sell_rate = (float(soup.body.find_all('td', text='EUR')[0].findNextSibling('td').findNextSibling('td').findNextSibling('td').text) / 100)
                
                
                rates = []
                rates.append({'name': 'USD', 'buy':rmb_usd_buy_rate, 'sell': rmb_usd_sell_rate})
                rates.append({'name': 'GBP', 'buy':rmb_gbp_buy_rate, 'sell': rmb_gbp_sell_rate})
                rates.append({'name': 'EUR','buy':rmb_eur_buy_rate, 'sell': rmb_eur_sell_rate})
    
                mapping = {
                    'rates': rates,
                }
                
                _add_to_redis(key, mapping)
                
            except requests.ConnectionError:
                print "failed to add BOC rates"
        
        
        
        # THIS PROVIDES THE BASE KEY FOR ALL THE SITES WE'LL ADD
        rounded_now = now - timedelta(minutes=now.minute % 15,
                                 seconds=now.second,
                                 microseconds=now.microsecond)
        base_key = rounded_now.strftime("%Y-%m-%d-%H%M")   

        
        
        try:
            # MTGOX TRADE DATA IN GBP
            r = requests.get('http://data.mtgox.com/api/2/BTCGBP/money/ticker_fast')
            j = simplejson.loads(r.content)    
            mapping = {}
            mapping['name'] = 'MtGOX'
            mapping['price'] = '%.2f' % float(j['data']['buy']['value'])
            mapping['curr'] = j['data']['buy']['currency']
            key = "%s:%s" % (base_key, 'MTGOX')
            _add_to_redis(key, mapping)
        except:
            pass
            
        
        site = 'BITTYLICIOUS'
        try:
            # BITTYLICIOUS (ALWAYS GBP)
            r = requests.get('https://bittylicious.com/api/v1/quote/BTC/GB/GBP/BANK/1')
            j = simplejson.loads(r.content)
            mapping = {}
            mapping['name'] = 'Bittylicious'
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
