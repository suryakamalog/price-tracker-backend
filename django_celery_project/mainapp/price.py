import requests
from bs4 import BeautifulSoup
from .logger import logger

def filter_price(s):
	price = ""
	for i in s:
		if i == ".":
			break
		if i >= '0' and i <= '9':
			price += i
	return price

class PriceScraper:

	def __init__(self, product):
		self.product = product
		self.website = product.website
		self.url = product.url

	def get_soup(self):
		try:
			headers = {
			"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
			page = requests.get(self.url, headers=headers)
			soup = BeautifulSoup(page.content, "html.parser")
			return soup
		except:
			logger.info("Error while scraping")

	def get_price(self):
		soup = self.get_soup()
		curr_price = ""
		if self.website == 'amazon':
			spans = soup.find_all('span', {'class': 'a-price-whole'}) 
			lines = [span.get_text() for span in spans]
			if len(lines) != 0:
				curr_price = filter_price(lines[0])
			else:
				logger.info("Price not found, recheck the url provided")

		elif self.website == 'flipkart':
			price = soup.find('div', attrs={'class': '_30jeq3 _16Jk6d'})
			if price is None:
				logger.info("Price not found, recheck the url provided")
			else:
				curr_price = filter_price(price.text) 
				logger.info(curr_price)
		else:
			logger.info("Error!")

		return curr_price

	def get_name(self):
		soup = self.get_soup()
		name = ""
		if self.website == 'amazon':
			spans = soup.find_all('span', {'class': 'a-size-large product-title-word-break'}) 
			lines = [span.get_text() for span in spans]
			if len(lines) != 0:
				name = lines[0]
			else:
				logger.info("Name not found, recheck the url provided")

		elif self.website == 'flipkart':
			name = soup.find('div', attrs={'class': 'B_NuCI'})
			if name is None:
				logger.info("Name not found, recheck the url provided")
			else:
				name = name.text 
				logger.info(name)
		else:
			logger.info("Error!")

		return name

	def start(self):
		price = self.get_price()
		name = self.get_name()
		try:
			self.product.price = price
			self.product.title = name
			self.product.save()
		except:
			logger.info(f'Error!!, price:{price}')