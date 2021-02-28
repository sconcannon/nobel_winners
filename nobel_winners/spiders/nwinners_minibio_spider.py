#! python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 06:26:28 2021

@author: sconcannon

following ch6 of Data Visualization with Python and Javascript
downloads bios and images of Nobel prize winners, using Scrapy
"""
import scrapy
import re

BASE_URL = 'https://en.wikipedia.org'

class NWinnerBio(scrapy.Item):
    link = scrapy.Field()
    name = scrapy.Field()
    mini_bio = scrapy.Field()
    image_urls = scrapy.Field()
    bio_image = scrapy.Field()
    images = scrapy.Field()
    
class NWinnerSpiderBio(scrapy.Spider):
    """ Scrapes the country and link text of the Nobel winners """
    name = 'nwinners_minibio'
    allowed_domains = ['en.wikipedia.org']
    start_urls = ["https://en.wikipedia.org/wiki/List_of_Nobel_laureates_by_country"]
    
    def parse(self, response):
        filename = response.url.split('/')[-1]
        h3s = response.xpath('//h3')
        
        for h3 in h3s:
            country = h3.xpath('span[@class="mw-headline"]/text()').extract()
            if country:
                winners = h3.xpath('following-sibling::ol[1]')
                for w in winners.xpath('li'):
                    wdata = {}
                    wdata['link'] = BASE_URL + w.xpath('a/@href').extract()[0]
                    # Process the winner's bio page with the get_mini_bio method
                    request = scrapy.Request(
                        wdata['link'],
                        callback=self.get_mini_bio)
                    request.meta['item'] = NWinnerBio(**wdata)
                    yield request
                    
    def get_mini_bio(self, response):
        """ Get the winner's bio-text and photo """
        
        BASE_URL_ESCAPED = 'https:\/\/en.wikipedia.org'
        item = response.meta['item']
        item['image_urls'] = []
        img_src = response.xpath('//table[contains(@class, "infobox")]//img/@src')
        if img_src:
            item['image_urls'] = ['https:' + img_src[0].extract()]
            
        paras = response.xpath('//div[@class="mw-parser-output"]/*')
        mini_bio = ''

        for x in range(0,len(paras)):
          if paras[x].xpath('@id').extract() == ['toc']:
            break # stop after the intro 
          if not paras[x].xpath('@class'): # bio intro paras have no classes
            mini_bio += paras[x].extract()
            
        # correct for wiki-links
        mini_bio = mini_bio.replace('href="/wiki', 'href="' + BASE_URL + '/wiki')
        mini_bio = mini_bio.replace('href="#', item['link'] + '#')
        item['mini_bio'] = mini_bio
        yield item