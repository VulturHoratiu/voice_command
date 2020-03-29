import scrapy
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.joke = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            self.start_joke = True
        if tag == 'em':
            self.start_joke = False

        print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        if tag == 'div':
            self.start_joke = False

        print("Encountered an end tag :", tag)

    def handle_data(self, data):
        if self.start_joke == True:
            self.joke += data.strip()

        print("Encountered some data  :", data)

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
                'https://www.rd.com/jokes/dad/',
                'https://www.rd.com/jokes/doctor/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        div = response.selector.xpath('//div[@class="content-wrapper hidden"]').getall()
        filename = response.url.split("/")[4]
        with open("jokes-%s" % filename, 'w') as f:
            for i in div:
                parser = MyHTMLParser()
                parser.feed(i)
                parser.joke += '\r\n'
                parser.joke = parser.joke.replace("Q: ", " ")
                parser.joke = parser.joke.replace("A: ", " ")
                parser.joke = parser.joke.replace("Q. ", " ")
                parser.joke = parser.joke.replace("A. ", " ")
                f.write(parser.joke)

