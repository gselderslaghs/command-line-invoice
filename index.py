import click
from datetime import datetime
from pdf_invoice_util import Config, Invoice, InvoicePDF

config = Config()


@click.group(chain=True)
def cli():
    """Command line application for invoice generation"""
    pass


@cli.command()
@click.option('--customer-id', prompt=True, type=int)
@click.option('--customer-name', prompt=True, type=str)
@click.option('--customer-address', prompt=True, type=str)
@click.option('--customer-postal_code', prompt=True, type=int)
@click.option('--customer-city', prompt=True, type=str)
@click.option('--customer-country', prompt=True, type=str)
@click.option('--invoice-id', prompt=True, type=int)
@click.option('--invoice-date', prompt=True, type=str, default=datetime.now().strftime('%Y-%m-%d'))
@click.option('--customer-vat-registered-number', prompt=True, type=str)
@click.option('--vat-percentage', prompt=True, type=int, default=config.load()['payment_details']['vat'])
@click.option('--invoice-language', prompt=True, type=click.Choice(['en', 'nl']),
              default=config.load()['pdf']['language'])
def generate_invoice(customer_id, customer_name, customer_address, customer_postal_code, customer_city,
                     customer_country, invoice_id, invoice_date, customer_vat_registered_number, vat_percentage,
                     invoice_language):
    invoice = Invoice(invoice_id, invoice_date, customer_id, customer_name, customer_address, customer_postal_code,
                      customer_city, customer_country, customer_vat_registered_number, vat_percentage)
    invoice.set_articles(generate_invoice_lines())
    pdf = InvoicePDF(invoice, invoice_language)
    pdf.generate_document()


def generate_invoice_line():
    while True:
        title_prompt_label = 'Title\n'
        title = input(title_prompt_label)
        if validate_input(title, 'str'):
            break
        continue

    while True:
        price = input('Price\n')
        if (validate_input(price, 'float', True)):
            break
        continue

    while True:
        amount = input('Amount\n')
        if (validate_input(amount, 'int', True)):
            break
        continue

    description = input('Description\n')
    return {'title': title, 'amount': int(amount), 'price': float(price), 'description': description}


def generate_invoice_lines():
    print(f'Manage invoice lines')
    lines = []
    while True:
        invoice_line = generate_invoice_line()
        lines.append(invoice_line)
        print(f'Successfully added {invoice_line['title']}')
        new = input('Create new line? Y/n\n')
        if new in ['Y', '']:
            continue
        break
    return lines


def validate_input(value, validation_type, required=False):
    if required != False and len(value) == 0:
        return False
    try:
        match validation_type:
            case 'str':
                return str(value)
            case 'int':
                return int(value)
            case 'float':
                return float(value)
            case '_':
                raise ValueError('Invalid validation type')
    except ValueError as e:
        print(f'Value Error: {e}\nPlease try again')
        return False


if __name__ == '__main__':
    cli()
