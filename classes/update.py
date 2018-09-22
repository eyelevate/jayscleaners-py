import re

from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from classes.popups import Popups
from models.companies import Company
from models.inventory_items import InventoryItem
from models.invoice_items import InvoiceItem
from models.invoices import Invoice
from models.sync import Sync
from models.taxes import Tax
SYNC = Sync()

class UpdateScreen(Screen):
    item_name = ObjectProperty(None)
    item_color = ObjectProperty(None)
    item_memo = ObjectProperty(None)
    item_pretax = ObjectProperty(None)
    item_tax = ObjectProperty(None)
    item_total = ObjectProperty(None)
    search_input = ObjectProperty(None)
    company_select = ObjectProperty(None)
    location_select = ObjectProperty(None)
    company_id = None
    new_pretax = []
    new_total = []
    invoice_id = None

    def reset(self):
        # Pause Schedule

        self.search_input.text = ''
        self.company_select.text = "Store Name"
        self.company_select.values = Company().prepareCompanyList()
        self.location_select.text = "Select Last Scanned"
        self.location_select.values = InvoiceItem().prepareLocationList()
        self.item_name.text = ''
        self.item_color.text = ''
        self.item_memo.text = ''
        self.item_pretax.text = ''
        self.item_tax.text = ''
        self.item_total.text = ''
        self.invoice_id = ''
        self.new_pretax = []
        self.new_total = []
        self.company_id = None
        pass

    def search(self):
        invitems = SYNC.invoice_item_grab(self.search_input.text)
        if invitems:

            item_id = invitems['item_id']
            company_id = invitems['company_id']
            self.invoice_id = invitems['invoice_id']
            self.company_id = company_id
            companies = SYNC.company_grab(company_id)
            if companies:
                company_name = companies['name']
            else:
                company_name = 'Store Name'
            location = int(invitems['status']) - 1
            locations = InvoiceItem().prepareLocationList()
            location_name = locations[location]
            item_name = InventoryItem().getItemName(item_id)
            self.company_select.text = company_name
            self.company_select.values = Company().prepareCompanyList()
            self.location_select.text = location_name
            self.location_select.values = locations
            self.item_name.text = item_name
            self.item_color.text = invitems['color'] if invitems['color'] else ''
            self.item_memo.text = invitems['memo'] if invitems['memo'] else ''
            self.item_pretax.text = str('{:,.2f}'.format(invitems['pretax']))
            self.new_pretax = list(str(int(invitems['pretax'] * 100)))
            self.item_tax.text = str('{:,.2f}'.format(invitems['tax']))
            self.item_total.text = str('{:,.2f}'.format(invitems['total']))
            self.new_total = list(str(int(invitems['total'] * 100)))
        else:
            Popups.dialog_msg('No Such Invoice Item', 'Could not find any invoice item with that id. Please try again')

            self.reset()
        pass

    def update_total(self):
        try:
            p = float(re.sub('[^0-9]', '', self.item_pretax.text))
        except ValueError:
            p = 0
        pretax = p / 100 if p > 0 else 0
        tax_rate = Tax().getTaxRate(self.company_id)
        tax = '{:.2f}'.format(round(pretax * tax_rate, 2))
        total = '{:.2f}'.format(round(pretax * (1 + tax_rate), 2))
        self.item_tax.text = str(tax)
        self.item_total.text = str(total)

        pass

    def update_pretax(self):

        try:
            t = float(re.sub('[^0-9]', '', self.item_total.text))
        except ValueError:
            t = 0
        total = t / 100 if t > 0 else 0
        tax_rate = Tax().getTaxRate(self.company_id)
        pretax = '{:.2f}'.format(round(total / (1 + tax_rate), 2))
        tax = '{:.2f}'.format(round(total - float(pretax), 2))
        self.item_tax.text = str(tax)
        self.item_pretax.text = str(pretax)

        pass

    def clear_pretax(self):
        self.item_pretax.text = ''
        self.new_pretax = []

    def clear_total(self):
        self.item_total.text = ''
        self.new_total = []

    def update_inventory_item(self):
        invoice_items = InvoiceItem()
        tax_rate = Tax().getTaxRate(self.company_id)
        # get the location status
        location_selected = invoice_items.prepareLocationStatus(self.location_select.text)
        data = {
            'company_id': self.company_id,
            'status': location_selected,
            'pretax': self.item_pretax.text,
            'tax': self.item_tax.text,
            'total': self.item_total.text,
            'memo': self.item_memo.text,
            'color': self.item_color.text
        }
        where = {
            'invoice_items_id': str(self.search_input.text)
        }
        if invoice_items.put(where=where, data=data):
            invoices = Invoice()
            # get the invoice totals from the invoice items
            pretax = invoice_items.sum(column='pretax',
                                       where={'invoice_items_id': self.search_input.text})
            if pretax:
                # calculate the tax
                tax = '{:.2f}'.format(round(pretax * tax_rate, 2))
                # calculate the total
                total = '{:.2f}'.format(round(pretax * (1 + tax_rate), 2))
                data = {'pretax': pretax,
                        'tax': tax,
                        'total': total}
                where = {'invoice_id': self.invoice_id}
                if invoices.put(where=where, data=data):
                    # reset the data form
                    self.reset()
                    # sync the database

                    # alert the user
                    Popups.dialog_msg('Update Invoice Item Success', 'Successfully updated the invoice item.')

        pass