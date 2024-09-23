import click
import yaml
from datetime import datetime

from pdf import PDF

with open('config/config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

with open('config/iterator.yaml', 'r') as iterator_file:
    iterator = yaml.safe_load(iterator_file).get('iterator')


@click.group(chain=True)
def cli():
    """Command line application for invoice generation"""
    pass


@cli.command()
@click.option('--client-id', prompt=True, type=str)
@click.option('--client-name', prompt=True, type=str)
@click.option('--client-address', prompt=True, type=str)
@click.option('--client-postal_code', prompt=True, type=str)
@click.option('--client-city', prompt=True, type=str)
@click.option('--client-country', prompt=True, type=str)
@click.option('--invoice-date', prompt=True, type=str, default=datetime.now().strftime('%d-%m-%Y'))
@click.option('--client-vat-registered-number', prompt=True, type=str)
@click.option('--vat-percentage', prompt=True, type=int, default=config['payment_details']['vat'])
@click.option('--invoice-language', prompt=True, type=str, default=config['pdf']['language'], help='en/nl')
def generate_invoice(client_id, client_name, client_address, client_postal_code, client_city, client_country,
                     invoice_date, client_vat_registered_number, vat_percentage, invoice_language):
    client_details = {
        'name': client_name,
        'address': client_address,
        'postal_code': client_postal_code,
        'city': client_city,
        'country': client_country,
    }
    date_split = invoice_date.split('-')
    invoice_details = {
        'id': config['payment_details']['invoice_prefix'] + '{:02d}'.format(iterator),
        'date': datetime(int(date_split[2]), int(date_split[1]), int(date_split[0])).strftime('%d %B %Y'),
        'client_id': client_id,
        'client_vat_number': client_vat_registered_number,
        'vat_percentage': vat_percentage,
    }
    articles = lines()

    pdf = PDF('P', 'mm', 'Letter', invoice_language)
    pdf.generate_content(client_details, invoice_details, articles)

    with open('config/iterator.yaml', 'w') as iterator_file:
        yaml.dump(dict(iterator=iterator + 1), iterator_file)


def lines():
    print(f'Manage invoice lines')
    lines = []
    while True:
        title = input('Title') if len(lines) == 0 else input('Title (leave empty to commit current list)')
        if title == '':
            break
        price = float(input('Price'))
        amount = int(input('Amount'))
        if title and price and amount:
            lines.append({
                'title': title,
                'amount': amount,
                'price': price
            })
            print(f'Successfully added {title}')
        else:
            print(f'Error: fill in all values')
    return lines


if __name__ == '__main__':
    cli()
