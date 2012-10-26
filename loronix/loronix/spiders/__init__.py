# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.


from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

class LoronixSpider(CrawlSpider):
   name = "loronix"
   allowed_domains = ["wordpress.com"]
   start_urls = [
       "http://orfaosdoloronix.wordpress.com/"
       ]
   rules = [Rule(SgmlLinkExtractor(allow=[r'orfaosdoloronix.wordpress.com/\d+/\d+/$']), follow=True), 
	Rule(SgmlLinkExtractor(allow=[r'orfaosdoloronix.wordpress.com/\d+/\d+/page/\d+/$']), follow=True), 
       	Rule(SgmlLinkExtractor(allow=[r'orfaosdoloronix.files.wordpress.com/.+\.jpg'], deny_extensions = []), callback='parse_image')]

   def parse_image(self, response):
	filename = response.url.split("/")[-1]
	print filename
        open('covers/' + filename, 'wb').write(response.body)
