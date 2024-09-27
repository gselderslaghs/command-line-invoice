import locale

import yaml
from fpdf import XPos, YPos
from config import config
from pdf import PDF

locale.setlocale(locale.LC_ALL, config['pdf']['locale'])


class InvoicePDF(PDF):
    def __init__(self, invoice, language, orientation='P', unit='mm', format='Letter'):
        self.invoice = invoice
        super().__init__(orientation, unit, format, self.invoice.invoice_id, language)
        self.set_page_title(self.translations['invoice'])
        try:
            with open('translations/terms.' + language + '.yaml', 'r') as terms_file:
                self.terms = yaml.safe_load(terms_file)
        except FileNotFoundError:
            self.terms = None

    def render_currency(self, amount):
        return locale.currency(amount, grouping=True, international=True, symbol=True)

    def generate_document(self):
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_font(config['pdf']['font'], '', size=9)

        # Supplier & client subheader
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'], config['company']['name'])
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'], self.invoice.customer_name,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'], config['company']['address'])
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'], self.invoice.customer_address,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'],
                  config['company']['postal_code'] + ' ' + config['company']['city'])
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'],
                  str(self.invoice.customer_postal_code) + ' ' + self.invoice.customer_city, new_x=XPos.LMARGIN,
                  new_y=YPos.NEXT)
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'], config['company']['country'])
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'], self.invoice.customer_country,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'],
                  config['company']['vat_registered_number'],
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'], config['company']['phone_1'],
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if 'phone_2' in config['company']:
            self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'], config['company']['phone_2'],
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.render_line_space()

        # Invoice details
        self.set_font(config['pdf']['font'], 'b', size=9)
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.translations['invoice_date'])
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'],
                  self.translations['invoice_number'])
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'],
                  self.translations['customer_vat_registered_number'])
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.translations['customer_id'],
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font(config['pdf']['font'], '', size=9)
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.invoice.invoice_date)
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.invoice.invoice_id)
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.invoice.customer_vat_number)
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], str(self.invoice.customer_id),
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.render_line_space()

        # Invoice lines
        self.set_font(config['pdf']['font'], 'b', size=9)
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.translations['description'])
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.translations['amount'])
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.translations['price'],
                  align='R')
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.translations['total_price'],
                  align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font(config['pdf']['font'], '', size=9)
        for article in self.invoice.articles:
            self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], article['title'])
            self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], str(article['amount']))
            self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'],
                      self.render_currency(article['price']),
                      align='R')
            self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'],
                      self.render_currency(article['amount'] * article['price']),
                      align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Totals
        subtotal = sum([article['amount'] * article['price'] for article in self.invoice.articles])
        vat_amount = subtotal * self.invoice.vat_percentage / 100

        self.render_line_space(1)

        if self.invoice.vat_percentage > 0:
            self.render_cell_spacer(2)
            self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.translations['subtotal'],
                      align='R')
            self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'],
                      str(self.render_currency(subtotal)),
                      align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            self.render_cell_spacer(2)
            self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'],
                      self.translations['vat_label'].format(str(self.invoice.vat_percentage)), align='R')
            self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'],
                      str(self.render_currency(vat_amount)),
                      align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.render_cell_spacer(2)
        self.set_font(config['pdf']['font'], 'b', size=9)
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.translations['total'],
                  align='R')
        self.set_font(config['pdf']['font'], '', size=9)
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'],
                  str(self.render_currency(subtotal + vat_amount)),
                  align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Payment info
        self.render_line_space(1)
        payment_info = self.translations['payment_info'].format(
            str(self.render_currency(subtotal + vat_amount)),
            config['payment_details']['bank_iban'],
            config['payment_details']['bank_bic'],
            self.invoice.invoice_id,
            config['payment_details']['invoice_due_date'])
        self.multi_cell(0, config['pdf']['cell_height'],
                        payment_info + ' ' + self.translations[
                            'terms_info'] if self.terms is not None else payment_info)

        if self.terms is not None:
            self.add_page()
            for term in self.terms:
                self.multi_cell(0, config['pdf']['cell_height'], term, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self.render_line_space(1)

        super().generate_document()
