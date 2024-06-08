from celery import Celery, shared_task
from celery.utils.log import get_task_logger
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

app = Celery('coinapp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

logger = get_task_logger(__name__)

class CoinMarketCap:
    def __init__(self, coin_acronym):
        self.coin_acronym = coin_acronym
        self.base_url = 'https://coinmarketcap.com/currencies/'
        self.url = self.base_url + self.coin_acronym.lower()
        self.driver = webdriver.Chrome()  # Use your preferred browser driver
        self.data = {}
        print("url ", self.base_url)
    def make_request(self):
        print("In the scraping data")
        self.driver.get(self.url)
        # Wait for the page to fully load and elements to appear
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, '__next')))

    def scrape_data(self):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        print("In the scraping data scrap data")
        try:
            # Price
            print("In the scraping data try")
            self.data['price'] = float(soup.find('div', class_='priceValue').text.replace(',', ''))
            print("Priceing :- ",self.data['price'])
            # Price Change
            self.data['price_change'] = float(soup.find('span', class_='priceChange').text.replace('%', ''))
            # Market Cap
            self.data['market_cap'] = int(soup.find('span', class_='cmc-details-panel-item__value').text.replace(',', ''))
            # Market Cap Rank
            self.data['market_cap_rank'] = int(soup.find('span', class_='cmc-details-panel-item__value').find_next_sibling('span').text.strip())
            # Volume
            self.data['volume'] = int(soup.find('span', class_='cmc-details-panel-item__value', text=lambda text: 'Volume' in text).text.replace(',', ''))
            # Volume Rank
            self.data['volume_rank'] = int(soup.find('span', class_='cmc-details-panel-item__value', text=lambda text: 'Volume' in text).find_next_sibling('span').text.strip())
            # Volume Change
            self.data['volume_change'] = float(soup.find('span', class_='cmc-details-panel-item__value', text=lambda text: 'Volume Change' in text).text.replace('%', ''))
            # Circulating Supply
            self.data['circulating_supply'] = float(soup.find('span', class_='cmc-details-panel-item__value', text=lambda text: 'Circulating Supply' in text).text.replace(',', ''))
            # Total Supply
            self.data['total_supply'] = float(soup.find('span', class_='cmc-details-panel-item__value', text=lambda text: 'Total Supply' in text).text.replace(',', ''))
            # Diluted Market Cap
            self.data['diluted_market_cap'] = int(soup.find('span', class_='cmc-details-panel-item__value', text=lambda text: 'Diluted Market Cap' in text).text.replace(',', ''))
            # Contracts
            self.data['contracts'] = []
            for contract in soup.find_all('div', class_='cmc-details-panel-item__value', text=lambda text: 'Contract' in text):
                self.data['contracts'].append({
                    'name': contract.find_previous_sibling('span').text.strip(),
                    'address': contract.text.strip()
                })
            # Official Links
            self.data['official_links'] = []
            for link in soup.find_all('a', class_='cmc-details-panel-item__value', text=lambda text: 'Official Website' in text):
                self.data['official_links'].append({
                    'name': 'website',
                    'link': link['href']
                })
            # Socials
            self.data['socials'] = []
            for social_link in soup.find_all('a', class_='cmc-details-panel-item__value', text=lambda text: 'Social' in text):
                self.data['socials'].append({
                    'name': social_link.text.strip().lower(),
                    'url': social_link['href']
                })
            print("The data collected:- ",self.data)
        except AttributeError as e:
            logger.error(f"Error scraping data for {self.coin_acronym}: {e}")

    def process_data(self):
        # Convert scraped data to desired format - already done in scrape_data
        pass 

    def get_json_response(self):
        # Construct JSON response
        return json.dumps(self.data)

    def close_driver(self):
        self.driver.quit()


@shared_task
def scrape_coin(coin_acronym):
    """
    Scrapes data for a single coin.
    """
    logger.info(f"Scrape coin task called for {coin_acronym}")
    coin = CoinMarketCap(coin_acronym)
    coin.make_request()
    coin.scrape_data()
    coin.process_data()
    coin.close_driver()
    return coin.get_json_response() 