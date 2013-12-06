from django.conf.urls.defaults import *
from django.utils.translation import ugettext_lazy as _

import views

urlpatterns = patterns('',

    url(r'^$', views.home, name="home"),
    url(r'^buy/(\w+)/$', views.buy, name="buy"),
    
    # RELATED TO BASKET FUNCTIONS
    #url(r'^basket/$', views.basket, name="basket"),
    #url(r'^basket/add/(\w+)$', views.add_to_basket, name="add_to_basket"),

    # get objects by ID urls
    #url(r'^page/(?P<slug>[\w-]+)/$', views.page, name="page"),
    #url(r'^page/(\w+)/$', views.page_by_id, name="page_by_id"),
    #url(r'^product/(\w+)/$', views.product_by_id, name="product_by_id"),
    #url(r'^category/(\w+)/$', views.category_by_id, name="category_by_id"),
    
    
    
)