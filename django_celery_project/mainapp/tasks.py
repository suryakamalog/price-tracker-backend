from celery import shared_task
from .price import PriceScraper
from .models import Product
from .logger import logger

@shared_task(bind=True)
def price_scraping_task(self, product_id):
    product = Product.objects.get(id=product_id)
    logger.info(f'Starting price scraping task for Product id: {product_id}')
    p = PriceScraper(product)
    p.start()

@shared_task(bind=True)
def periodic_update_task(self):
    products = Product.objects.all()
    for product in products:
        logger.info(f'Periodic price scraping task sent for Product id: {product.id}')
        p = PriceScraper(product)
        p.start()
