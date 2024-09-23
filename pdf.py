import locale
import yaml

from fpdf import FPDF, XPos, YPos

with open('config/config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

locale.setlocale(locale.LC_ALL, config['pdf']['locale'])


class PDF(FPDF):
    def __init__(self, orientation, unit, format, language=config['pdf']['language']):
        super().__init__(orientation, unit, format)
        with open('translations/language.' + language + '.yaml', 'r') as translations_file:
            self.translations = yaml.safe_load(translations_file)
        try:
            with open('translations/terms.' + language + '.yaml', 'r') as terms_file:
                self.terms = yaml.safe_load(terms_file)
        except FileNotFoundError:
            self.terms = None

    def header(self):
        if 'logo' in config['pdf']:
            self.image(config['pdf']['logo'], 10, 10, 20)
        self.set_font(config['pdf']['font'], '', size=29)
        self.cell(0, config['pdf']['cell_height'] * 2, self.translations['invoice'], border=False, align='C',
                  new_x=XPos.LMARGIN)
        self.ln(25)

    def footer(self):
        self.set_y(-10)
        self.set_font(config['pdf']['font'], '', size=6)
        self.cell(0, config['pdf']['cell_height'], f'{self.translations['page']} {self.page_no()}/{{nb}}', align='C')

    def render_currency(self, amount):
        return locale.currency(amount, grouping=True, international=True, symbol=True)

    def render_line_space(self, cells=2):
        return self.cell(config['pdf']['cell_width'] * cells, config['pdf']['cell_height'], '', new_x=XPos.LMARGIN,
                         new_y=YPos.NEXT)

    def render_cell_spacer(self, cells):
        return self.cell(config['pdf']['cell_width'] * cells, config['pdf']['cell_height'] * cells, '')

    def generate_content(self, client_details, invoice_details, articles):
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_font(config['pdf']['font'], '', size=9)

        # Supplier & client subheader
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'], config['company']['name'])
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'], client_details['name'],
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'], config['company']['address'])
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'], client_details['address'],
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'],
                  config['company']['postal_code'] + ' ' + config['company']['city'])
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'],
                  client_details['postal_code'] + ' ' + client_details['city'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'], config['company']['country'])
        self.cell(config['pdf']['cell_width'] * 2, config['pdf']['cell_height'], client_details['country'],
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
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.translations['invoice_number'])
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'],
                  self.translations['client_vat_registered_number'])
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.translations['client_id'],
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font(config['pdf']['font'], '', size=9)
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], invoice_details['date'])
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], invoice_details['id'])
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], invoice_details['client_vat_number'])
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], invoice_details['client_id'],
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.render_line_space()

        # Invoice lines
        self.set_font(config['pdf']['font'], 'b', size=9)
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.translations['description'])
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.translations['amount'])
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.translations['price'], align='R')
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.translations['total_price'],
                  align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font(config['pdf']['font'], '', size=9)
        for article in articles:
            self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], article['title'])
            self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], str(article['amount']))
            self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'],
                      str(self.render_currency(article['price'])),
                      align='R')
            self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'],
                      str(self.render_currency(article['amount'] * article['price'])),
                      align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Totals
        subtotal = sum([article['amount'] * article['price'] for article in articles])
        vat_amount = subtotal * invoice_details['vat_percentage'] / 100

        self.render_line_space(1)

        if invoice_details['vat_percentage'] > 0:
            self.render_cell_spacer(2)
            self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.translations['subtotal'],
                      align='R')
            self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], str(self.render_currency(subtotal)),
                      align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            self.render_cell_spacer(2)
            self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'],
                      self.translations['vat_label'].format(str(invoice_details['vat_percentage'])), align='R')
            self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], str(self.render_currency(vat_amount)),
                      align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.render_cell_spacer(2)
        self.set_font(config['pdf']['font'], 'b', size=9)
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'], self.translations['total'], align='R')
        self.set_font(config['pdf']['font'], '', size=9)
        self.cell(config['pdf']['cell_width'], config['pdf']['cell_height'],
                  str(self.render_currency(subtotal + vat_amount)),
                  align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Payment info
        self.render_line_space(1)
        payment_info = self.translations['payment_info'].format(str(self.render_currency(subtotal + vat_amount)),
                                                                config['payment_details']['bank_iban'],
                                                                config['payment_details']['bank_bic'],
                                                                invoice_details['id'],
                                                                config['payment_details']['invoice_due_date'])
        self.multi_cell(0, config['pdf']['cell_height'],
                        payment_info + ' ' + self.translations['terms_info'] if self.terms is not None else payment_info)

        if self.terms is not None:
            self.add_page()
            for term in self.terms:
                self.cell(0, config['pdf']['cell_height'] * 2, term, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.output(f'{invoice_details['id']}.pdf')
