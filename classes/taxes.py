from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from classes.popups import Popups
from models.taxes import Tax
from models.sync import Sync
ERROR_COLOR = 0.94, 0.33, 0.33, 1
DEFAULT_COLOR = 0.5, 0.5, 0.5, 1.0
SYNC = Sync()

class TaxesScreen(Screen):
    tax_rate_input = ObjectProperty(None)

    def reset(self):
        # Pause Schedule

        taxes = Tax()
        tax_rate = None

        tax_data = SYNC.taxes_query(vars.COMPANY_ID)
        if tax_data:
            for tax in tax_data:
                tax_rate = tax['rate']
        self.tax_rate_input.text = '{0:0>4}'.format((tax_rate * 100)) if tax_rate else ''

    def update(self):
        tax_rate = False
        if self.tax_rate_input.text:
            # convert tax rate into decimal / 100
            tax_rate = float(self.tax_rate_input.text) / 100 if self.tax_rate_input.text else False

        if tax_rate:
            self.tax_rate_input.hint_text = ""
            self.tax_rate_input.hint_text_color = DEFAULT_COLOR
            taxes = Tax()
            taxes.company_id = vars.COMPANY_ID
            taxes.rate = tax_rate
            taxes.status = 1
            if taxes.add():
                Popups.dialog_msg('Update Taxes', 'Successfully updated tax!')

            else:
                Popups.dialog_msg('Error On Update', 'Could not update tax rate! Please try again.')

        else:
            self.tax_rate_input.hint_text = "Enter Tax Rate"
            self.tax_rate_input.hint_text_color = ERROR_COLOR