import yaml

from fpdf import FPDF, XPos, YPos
from config import config


class PDF(FPDF):
    def __init__(self, orientation, unit, format, output_filename, language=config['pdf']['language']):
        super().__init__(orientation, unit, format)
        self.output_filename = output_filename
        with open('translations/language.' + language + '.yaml', 'r') as translations_file:
            self.translations = yaml.safe_load(translations_file)

    def set_page_title(self, page_title):
        self.page_title = page_title

    def header(self):
        if 'logo' in config['pdf']:
            self.image(config['pdf']['logo'], 10, 10, 20)
        self.set_font(config['pdf']['font'], '', size=29)
        self.cell(0, config['pdf']['cell_height'] * 2, self.page_title, border=False, align='C',
                  new_x=XPos.LMARGIN)
        self.ln(25)

    def footer(self):
        self.set_y(-10)
        self.set_font(config['pdf']['font'], '', size=6)
        self.cell(0, config['pdf']['cell_height'], f'{self.translations['page']} {self.page_no()}/{{nb}}', align='C')

    def render_line_space(self, cells=2):
        return self.cell(config['pdf']['cell_width'] * cells, config['pdf']['cell_height'], '', new_x=XPos.LMARGIN,
                         new_y=YPos.NEXT)

    def render_cell_spacer(self, cells):
        return self.cell(config['pdf']['cell_width'] * cells, config['pdf']['cell_height'] * cells, '')

    def generate_document(self):
        self.output(f'{self.output_filename}.pdf')
