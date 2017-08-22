#!/usr/bin/python3
# scrape_amazon.py - Extracts Samsung mobile phones

import json
import os
import requests
from datetime import datetime
from lxml import html
from time import sleep, time
from urllib import parse


def UTCtoEST():
    current = datetime.now()
    return str(current) + ' EST ::'


def create_project(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(os.path.join(os.getcwd(), directory))


def url_parser(url):
    parse_result = parse.urlparse(url)
    base_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parse_result)
    asin_path = '/'.join(parse_result.path.split('/')[2:4])
    new_url = parse.urljoin(base_url, asin_path)
    return new_url


def amazon_item_parser(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
    resp = requests.get(url, headers=headers)
    while True:
        try:
            doc = html.fromstring(resp.content)

            XPATH_NAME = '//h1[@id="title"]//text()'
            XPATH_CATEGORY = '//a[@class="a-link-normal a-color-tertiary"]//text()'
            XPATH_ORIGINAL_PRICE = '//td[contains(text(), "List Price") or contains(text(), "M.R.P") or contains(text(), "Price")]/following-sibling::td/text()'
            XPATH_SALE_PRICE = '//span[contains(@id, "ourprice") or contains(@id, "saleprice")]/text()'
            XPATH_AVAILABITY = '//div[@id="availability"]//text()'
            XPATH_FEATURE = '//ul[@class="a-unordered-list a-vertical a-spacing-none"]//li//text()[not(ancestor::*[@class="aok-hidden"])]'

            RAW_NAME = doc.xpath(XPATH_NAME)
            RAW_CATEGORY = doc.xpath(XPATH_CATEGORY)
            RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
            RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
            RAW_AVAILABILITY = doc.xpath(XPATH_AVAILABITY)
            RAW_FEATURE = doc.xpath(XPATH_FEATURE)

            NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
            CATEGORY = ' > '.join([i.strip() for i in RAW_CATEGORY]) if RAW_ORIGINAL_PRICE else None
            ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None
            SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
            AVAILABILITY = ' '.join([i.strip() for i in RAW_AVAILABILITY]).strip() if RAW_AVAILABILITY else None
            FEATURE = [' '.join(des.strip().split()) for des in RAW_FEATURE if not des.isspace()] if RAW_FEATURE else None

            if not ORIGINAL_PRICE:
                ORIGINAL_PRICE = SALE_PRICE

            if resp.status_code != 200:
                    raise ValueError('captcha')
            data = {'name': NAME,
                    'category': CATEGORY,
                    'original_price': ORIGINAL_PRICE,
                    'sale_price': SALE_PRICE,
                    'availability': AVAILABILITY,
                    'feature': FEATURE,
                    'url': url,
                    }

            return data
        except Exception as e:
            print(UTCtoEST(), e)


def crawl_amazon(max_pages=1):
    page = 1
    extracted_data = []
    crawled = []
    queue = []

    while page <= max_pages:
        sleep(3)
        try:
            # url = 'https://www.amazon.com/s/ref=sr_pg_2?fst=as%3Aoff&rh=n%3A2335752011%2Cn%3A!2335753011%2Cn%3A7072561011%2Cn%3A2407749011%2Cp_89%3ASamsung&page=' + str(page) + '&bbn=2407749011&ie=UTF8&qid=1492470529'
            url = 'https://google.com'
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
            print()
            print(UTCtoEST(), 'Processing page {} of {}.'.format(page, max_pages))
            resp = requests.get(url, headers=headers)
            doc = html.fromstring(resp.content)

            XPATH_LINKS = '//a[@class="a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal"]//@href'
            RAW_LINKS = list(map(url_parser, doc.xpath(XPATH_LINKS)))

            crawled.append(url)
            queue = queue + RAW_LINKS[:]

            print(UTCtoEST(), 'Extracting data...')
            item = 1
            for link in RAW_LINKS:
                if link in queue:
                    data = amazon_item_parser(link)
                    # If data is empty. This checks if the website detects your bot.
                    if not data:
                        print(UTCtoEST(), 'WARNING: YOU\'RE ABOUT TO BE DETECTED!')

                    print('{} Item {} of {}... Done.'.format(UTCtoEST(), item, len(RAW_LINKS)), end='\r')
                    extracted_data.append(data)
                    crawled.append(link)
                    queue.remove(link)
                    item += 1
                    page += 1
                    sleep(4)
            print()
        except Exception as e:
            print(UTCtoEST(), e)
            # When an exception occur the uncomplete extraced data will save to a file
            # for backup
            f = open('samsung_unlocked.json', 'w')
            d = {'product': extracted_data,
                 'total_item': len(extracted_data)
                 }
            json.dump(d, f, indent=4)
            f.close()

    print()
    print(UTCtoEST(), 'Done extracting {} data.'.format(len(extracted_data)))
    print(UTCtoEST(), 'Write data to json file.')

    f = open('samsung_unlocked.json', 'w')
    d = {'product': extracted_data,
         'total_item': len(extracted_data)
         }
    json.dump(d, f, indent=4)
    f.close()

    print(UTCtoEST(), 'Done. Thank you!')


if __name__ == '__main__':
    start_time = time()
    print()
    print(UTCtoEST(), 'Downloading main page...')
    create_project('amazon')
    crawl_amazon(47)
    print('[Finished in {:.1f}s]'.format(time() - start_time))
    # f = open('amazon_samsung_item.html')
    # markup = f.read()
    # f.close()
    # data = amazon_item_parser(markup)
    # from pprint import pprint
    # pprint(data)
