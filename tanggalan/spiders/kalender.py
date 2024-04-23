from datetime import datetime
import scrapy
import json
import s3fs

class KalenderSpider(scrapy.Spider):
    name = "kalender"
    allowed_domains = ["tanggalan.com"]
    # ==============================================
    start_urls = ["https://tanggalan.com/2024"] # ganti tahunnya atau tambah link lagi
    # ==============================================

    def parse(self, response):
        for kalender in response.css('#main > article > ul'):
            link_bulan = kalender.css('li:nth-child(1) > a::attr(href)').get()
            yield response.follow(link_bulan, callback=self.parse_month)
    
    def parse_month(self, response):
        link = response.url
        domain = link.split('/')[2]
        source = 'tanggalan'
        data_name = 'kalender'
        
        month = link.split('/')[-1].split('-')[0]
        year = link.split('/')[-1].split('-')[1]
        hari_list = ["minggu", "senin", "selasa", "rabu", "kamis", "jumat", "sabtu"]
        events = []
        data = {
            'link': link,
            'domain': domain,
            'source': source,
            'data_name': data_name,
            'calendar': {
                'year': year,
                'month': month,
                'events': {
                    'details': [],
                }
            },
            'crawling_time': None,
            'crawling_time_epoch': None
        }
        
        for event in response.css('#events > div'):
            tanggal = event.css('div.gruphari::text').get()
            events.append(tanggal)
            
        days = response.css('#main > ul > li:nth-child(2) > *')
        for index, day in enumerate(days):
            date = day.css('div:nth-child(1)::text').get()
            day_name = hari_list[index % 7]
            if date is not None:
                if date in events:
                    for event in response.css('#events > div'):
                        if event.css('div.gruphari::text').get() == date:
                            event_name = event.css('div.event > div.namaevent::text').getall()
                            data['calendar']['events']['details'].append({
                                'date': date,
                                'day': day_name,
                                'event': event_name
                            })
                else:
                    data['calendar']['events']['details'].append({
                        'date': date,
                        'day': day_name,
                        'event': None
                    })

                file_name = f'{month}_{year}.json'
                # =======================================================
                folder = 'f:/Work/Garapan gweh/html/tanggalan/json' # ganti path 
                # =======================================================

                data['crawling_time'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                data['crawling_time_epoch'] = int(datetime.now().timestamp())

                with open(f'{folder}/{file_name}', 'w') as outfile:
                    json.dump(data, outfile)