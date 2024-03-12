import re
import scrapy
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from scrapy.crawler import CrawlerProcess


class Rentfaster1Spider(scrapy.Spider):
    name = "rentfaster1"
    start_urls = ['https://www.rentfaster.ca/sitemap-listings.xml']

    def __init__(self):
        super().__init__()
        self.google_sheet_links = self.Google_sheet_read()

    def Google_sheet_read(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('bold-site-413506-601790b6c62f.json', scope)
        client = gspread.authorize(creds)
        sheet_name = 'Rentfaster'
        sheet = client.open(sheet_name).sheet1

        column_data = sheet.col_values(1)
        web_links = column_data[1:]

        return web_links

    def parse(self, response):
        filtered_links = []
        all_location_links = re.findall('<loc>(.*?)</loc>', response.text)

        for link in all_location_links:
            if ("calgary/rentals" in link or
                "airdrie/rentals" in link or
                "cochrane/rentals" in link) and ("house" in link and "townhouse" not in link):
                filtered_links.append(link)

        links_not_in_google_sheet = [link for link in filtered_links if link not in self.google_sheet_links]

        for link in links_not_in_google_sheet:
            yield scrapy.Request(link, callback=self.parse_property)

    def parse_property(self, response):
        try:
            address1 = ''.join(response.xpath('//div[@class="column"]/div[1]//text()').extract()).replace('\t',
                                                                                                          '').replace(
                '\n', '')
        except:
            address1 = ''
        try:
            address2 = ''.join(
                response.xpath('//div[@class="column"]/div[2]//text()').extract()).replace('\t', '').replace('\n', '')
        except:
            address2 = ''

        if address1 and address2:
            address = f"{address1}, {address2}"
        elif address1:
            address = address1
        else:
            address = address2

        try:
            price = ''.join(
                response.xpath('//div[@class="card-content"]//li[@title="Rent"]//text()').extract()).strip()
        except:
            price = ''
        try:
            id = response.url.split('/')[-1]
        except:
            id = ''
        type = 'House'
        try:
            number = response.text.split('"phone":')[1].split(',')[0].replace('"', '').replace('(', '').replace(')',
                                                                                                                '').replace(
                '-', '')
        except:
            number = ''

        item = {
            'Web Link': response.url,
            'Listing ID': id,
            'Type': type,
            'Price': price,
            'Address': address,
            'Number': number
        }
        data = [response.url, id, type, price, address, number]
        self.Google_add(data)
        yield item

        

    def Google_add(self, data):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('bold-site-413506-601790b6c62f.json', scope)
        client = gspread.authorize(creds)
        sheet_name = 'Rentfaster'
        sheet = client.open(sheet_name).sheet1

        sheet.append_row(data)
        self.logger.info("Data added to Google Sheet successfully!")
        self.logger.info("Data saved: %s", data)


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
})
process.crawl(Rentfaster1Spider)
process.start()

