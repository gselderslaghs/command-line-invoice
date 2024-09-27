import yaml
from datetime import datetime

from config import config


class Invoice:
    def __init__(self, invoice_date, customer_id, customer_name, customer_address, customer_postal_code, customer_city,
                 customer_country,
                 customer_vat_registered_number, vat_percentage):
        self.iterator = self.get_iterator()
        self.invoice_id = config['payment_details']['invoice_prefix'] + '{:02d}'.format(self.iterator)
        self.invoice_date = datetime.strptime(invoice_date, '%Y-%m-%d').strftime(config['date_format'])

        self.customer_id = customer_id
        self.customer_name = customer_name
        self.customer_address = customer_address
        self.customer_postal_code = customer_postal_code
        self.customer_city = customer_city
        self.customer_country = customer_country
        self.customer_vat_number = customer_vat_registered_number
        self.vat_percentage = vat_percentage

    def set_articles(self, articles):
        self.articles = articles

    def get_iterator(self):
        with open('config/iterator.yaml', 'r') as iterator_file:
            return yaml.safe_load(iterator_file).get('iterator')

    def increment_iterator(self):
        with open('config/iterator.yaml', 'w') as iterator_file:
            yaml.dump(dict(iterator=self.iterator + 1), iterator_file)
