from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess
import os
import json
from os import remove
from scrapy.exceptions import CloseSpider
from multiprocessing.context import Process
from datetime import datetime



################################
#Func. ScrappyPPS: Scrapea la info de la pagina principal de PPS
################################
def ScrappyPPS():
  
  class Pasantia(Item):
    id = Field()
    link = Field()
    titulo = Field()
    fecha = Field()
    descripcion = Field()
    fechaScrappy = Field()

  class FIPasantiasSpider(Spider):
    name = "PasantiasSpider"

    custom_settings = {
        "USER-AGENT":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
    }
    start_urls = ['https://www.facet.unt.edu.ar/sbe/pasantias-y-pps/']

    def parse(self, response):
        sel = Selector(response)
        listaPasantia = sel.xpath("//div[@id='panel-194-0-0-0']//article[contains(@id, 'post-')]")

        i = 0
        
        for p in listaPasantia:
          item = ItemLoader(Pasantia(), p)
  
          item.add_value("id", i)
          item.add_xpath("link", ".//h1/a/@href")
          item.add_xpath("titulo", ".//h1/a/text()")
          item.add_xpath("fecha", ".//div[@class='entry-meta']/a/time/text()")
  
          x = p.xpath(".//div[@class='entry-content']//div[contains(@class,'siteorigin-widget')]/p/span/text()")
  
          if x == []:
              item.add_xpath("descripcion", ".//div[@class='entry-content']//div[contains(@class,'siteorigin-widget')]/p/text()")
          else:
              item.add_xpath("descripcion", ".//div[@class='entry-content']//div[contains(@class,'siteorigin-widget')]/p/span/text()")
  
          i += 1
          item.add_value("fechaScrappy", datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
  
          yield item.load_item()


#CORRIENDO SCRAPY SIN LA TERMINAL

  archivo = "pasantias.json"

  if (os.path.isfile(archivo)):
    remove(archivo)

  def crawl():
    crawler = CrawlerProcess({
      'FEED_FORMAT': 'json',
      'FEED_URI': 'pasantias.json'
    })
    crawler.crawl(FIPasantiasSpider)
    crawler.start()
  
  processPPS = Process(target=crawl)
  processPPS.start()
  processPPS.join()





################################
#Func. ScrappyPPSInicial: Scrapea solo el titulo de la ultima PPS
################################
def ScrappyPPSInicial():
  
  class PasantiaInicial(Item):

    titulo = Field()
    fechaScrappy = Field()

  class FIPasantiasSpiderInicial(Spider):
    name = "PasantiasSpider"

    custom_settings = {
        "USER-AGENT":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
    }
    start_urls = ['https://www.facet.unt.edu.ar/sbe/pasantias-y-pps/']

    def parse(self, response):
        sel = Selector(response)
        p = sel.xpath("//div[@id='panel-194-0-0-0']//article[contains(@id, 'post-')][1]")

        item = ItemLoader(PasantiaInicial(), p)  
        item.add_xpath("titulo", ".//h1/a/text()")
        item.add_value("fechaScrappy", datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
      
        yield item.load_item()


  #CORRIENDO SCRAPY SIN LA TERMINAL

  archivo = "pasantias.json"

  if (os.path.isfile(archivo)):
    remove(archivo)

  def crawl():
    crawler = CrawlerProcess({
      'FEED_FORMAT': 'json',
      'FEED_URI': 'pasantias.json'
    })
    crawler.crawl(FIPasantiasSpiderInicial)
    crawler.start()
  
  processPPS = Process(target=crawl)
  processPPS.start()
  processPPS.join()
  
  #####################
  #Leo y devuelvo el titulo de la ultima pasantia publicada.
  #####################
  
  ruta = 'pasantias.json'
  with open(ruta) as contenido:
    
    pasantia = json.load(contenido)
    p = pasantia[0]
    tituloPPS = p["titulo"][0]
    fechaPPS = p["fechaScrappy"][0]

    return (tituloPPS, fechaPPS)