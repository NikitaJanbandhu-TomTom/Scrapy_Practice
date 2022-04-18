import scrapy 
import re 
from so_poi_sp.items import PoiItem 
import json 
from scrapy import signals 
from so_poi_sp.pipelines.database import * 
from so_poi_sp.pipelines.poi_encoding import unicode 
from scrapy.spidermiddlewares.httperror import HttpError 
from twisted.internet.error import DNSLookupError 
from twisted.internet.error import TimeoutError, TCPTimedOutError 


'''Global variables'''  
global spider_id 
spider_id = '2300' 

global iso_country_code 
iso_country_code = 'GBR' 


class scrapyHeaderSpider(scrapy.Spider): 
    name = '2300' #Please note no spaces are allowed 

    @classmethod 
    def from_crawler(cls, crawler, *args, **kwargs): 
        spider = super(scrapyHeaderSpider, cls).from_crawler(crawler, *args, **kwargs) 
        crawler.signals.connect(spider.spider_error, signal=signals.spider_error) 
        crawler.signals.connect(spider.item_error, signal=signals.item_error) 
        return spider 

    def spider_error(self, spider): 
        status = 'Invalid, Spider Error' 
        database.statusUpdate(spider_id, status) 

    def item_error(self, spider): 
        status = 'Invalid, Item Error' 
        database.statusUpdate(spider_id, status) 

    def start_requests(self): 
        url = 'https://locator.natwest.com/'  

        # Set the headers here. The important part is 'application/json 
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
            'Accept': 'application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8,text/plain, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
        }

        yield scrapy.http.FormRequest(
            url=url, headers=headers, method='GET',
            callback=self.parse, errback=self.errback 
        )

        '''
        Reminder: Method can be changed to POST
        '''
# =============================================================================
#         #Add Request Parameters (set POST)
#         form_data = ''
# 
#         yield scrapy.http.FormRequest(
#             url=url, headers=headers, method='GET', formdata=form_data,
#             callback=self.parse, errback=self.errback 
#         )
# =============================================================================


    def errback(self, failure):
        '''log all failures'''
        self.logger.error(repr(failure))

        '''in case you want to do something special for some errors,
        you may need the failure's type:'''

        if failure.check(HttpError):
            '''these exceptions come from HttpError spider middleware
            you can get the non-200 response'''
            status = 'Invalid, HTTP Error'
            database.statusUpdate(spider_id, status)

        elif failure.check(DNSLookupError):
            # this is the original request
            status = 'Invalid, DNS Error'
            database.statusUpdate(spider_id, status)

        elif failure.check(TimeoutError, TCPTimedOutError):
            status = 'Invalid, TimeOut Error'
            database.statusUpdate(spider_id, status)

    def parse(self, response):
        result = response.text

        ##########################################
        '''
        EXTRACT POI ATTRIBUTES
        You have a choice to use either Regex, xpath or css

        '''

        for match in response.xpath('~expression~'):
            #### Filter name ####
            try:
                poi_name=match.xpath('~expression~').extract_first()
            except:
                poi_name = '$name'
                poi_name = poi_name.replace('_',' ')

            yield PoiItem(
                #### Filter name ####
                name=match.xpath('~expression~').extract_first(),

                #### Filter address ####
                addr_full=match.xpath('~expression~').extract_first(),

                #### City ####
                city=match.xpath('~expression~').extract_first(),

                #### Country ####
                country=match.xpath('~expression~').extract_first(),

                #### Postal Code ####
                postal=match.xpath('~expression~').extract_first(),

                #### Filter latitude ####
                lat=match.xpath('~expression~').extract_first(),

                #### Filter longitude ####
                lon=match.xpath('~expression~').extract_first(),

                #### Phone Number ####
                phone_number=match.xpath('~expression~').extract_first(),

                #### Email ####
                email=match.xpath('~expression~').extract_first(),

                #### Opening Hours ####
                opening_hours=match.xpath('~expression~').extract_first(),

                #### Contains Drive Trough ####
                drive=match.xpath('~expression~').extract_first()

            )
 
            '''
            REGEX Example:

                item = PoiItem()
                poi = []

                text_split = re.split(r'\{'id':', result)

                for text in text_split:
                    text = unicode(text)

                    my_dict = {'name':'',
                           'addr_full':'',
                           'city':'',
                           'country':'',
                           'postal':'',
                           'lat':'',
                           'lon':'',
                           'phone_number':'',
                           'email':'',
                           'iso_country_code':'',
                           'spider_id':''}

                    #### Filter name ####
                    n = re.search(r'~expression~', text, flags=re.I | re.DOTALL | re.MULTILINE | re.U)
                    if n:
                        my_dict['name'] = n.group(1)

                    #### Filter address ####
                    a = re.search(r'~expression~', text, flags=re.I | re.DOTALL | re.MULTILINE | re.U)
                    if a:
                        my_dict['addr_full'] = a.group(1)

                    .....

            item = poi
            return item
            '''
