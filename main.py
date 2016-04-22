import json
import time
import requests
import urllib


from colors import Color
from companies import Company
from custids import Custid
from deliveries import Delivery
from discounts import Discount
from inventories import Inventory
from inventory_items import InventoryItem
from invoices import Invoice
from invoice_items import InvoiceItem
from memos import Memo
from server import sync_from_server
from server import update_database
from printers import Printer
from reward_transactions import RewardTransaction
from rewards import Reward
from schedules import Schedule
from taxes import Tax
from transactions import Transaction
from users import User

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import FadeTransition
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from urllib import error
from urllib import request
from urllib import parse
from urllib.parse import urlencode
from urllib.request import urlopen


class MainScreen(Screen):
    update_label = ObjectProperty(None)

    def update_info(self):
        info = "Last updated {}".format("today")
        return info

    def login(self):
        pass

    def logout(self):
        pass

    def migrate(self):
        color = Color()
        company = Company()
        custid = Custid()
        delivery = Delivery()
        discount = Discount()
        inventory = Inventory()
        inventory_item = InventoryItem()
        invoice = Invoice()
        invoice_item = InvoiceItem()
        memo = Memo()
        printer = Printer()
        reward_transaction = RewardTransaction()
        reward = Reward()
        schedule = Schedule()
        tax = Tax()
        transaction = Transaction()
        user = User()
        color.create_table()
        company.create_table()
        custid.create_table()
        delivery.create_table()
        discount.create_table()
        inventory.create_table()
        inventory_item.create_table()
        invoice.create_table()
        invoice_item.create_table()
        memo.create_table()
        printer.create_table()
        reward_transaction.create_table()
        reward.create_table()
        schedule.create_table()
        tax.create_table()
        transaction.create_table()
        user.create_table()

    def db_sync(self):
        # start upload text
        self.update_label.text = 'Connecting to server...'

        # create an array of data that need to be uploaded to the server
        to_upload = {}
        to_upload_rows = 0

        colors_1 = Color()
        to_upload['colors'] = colors_1.where({'color_id': None})
        to_upload_rows += len(to_upload['colors'])

        companies_1 = Company()
        to_upload['companies'] = companies_1.where({'company_id': None})
        to_upload_rows += len(to_upload['companies'])

        custids_1 = Custid()
        to_upload['custids'] = custids_1.where({'cust_id': None})
        to_upload_rows += len(to_upload['custids'])

        deliveries_1 = Delivery()
        to_upload['deliveries'] = deliveries_1.where({'delivery_id': None})
        to_upload_rows += len(to_upload['deliveries'])

        discounts_1 = Discount()
        to_upload['discounts'] = discounts_1.where({'discount_id': None})
        to_upload_rows += len(to_upload['discounts'])

        invoices_1 = Invoice()
        to_upload['invoices'] = invoices_1.where({'invoice_id': None})
        to_upload_rows += len(to_upload['invoices'])

        invoice_items_1 = InvoiceItem()
        to_upload['invoice_items'] = invoice_items_1.where({'invoice_items_id': None})
        to_upload_rows += len(to_upload['invoice_items'])

        inventories_1 = Inventory()
        to_upload['inventories'] = inventories_1.where({'inventory_id': None})
        to_upload_rows += len(to_upload['inventories'])

        inventory_items_1 = InventoryItem()
        to_upload['inventory_items'] = inventory_items_1.where({'item_id': None})
        to_upload_rows += len(to_upload['inventory_items'])

        memos_1 = Memo()
        to_upload['memos'] = memos_1.where({'memo_id': None})
        to_upload_rows += len(to_upload['memos'])

        printers_1 = Printer()
        to_upload['printers'] = printers_1.where({'printer_id': None})
        to_upload_rows += len(to_upload['colors'])

        reward_transactions_1 = RewardTransaction()
        to_upload['reward_transactions'] = reward_transactions_1.where({'reward_id': None})
        to_upload_rows += len(to_upload['reward_transactions'])

        rewards_1 = Reward()
        to_upload['rewards'] = rewards_1.where({'reward_id': None})
        to_upload_rows += len(to_upload['rewards'])

        schedules_1 = Schedule()
        to_upload['schedules'] = schedules_1.where({'schedule_id': None})
        to_upload_rows += len(to_upload['schedules'])

        taxes_1 = Tax()
        to_upload['taxes'] = taxes_1.where({'tax_id': None})
        to_upload_rows += len(to_upload['taxes'])

        transactions_1 = Transaction()
        to_upload['transactions'] = transactions_1.where({'transaction_id': None})
        to_upload_rows += len(to_upload['transactions'])

        users_1 = User()
        to_upload['users'] = users_1.where({'user_id': None})
        to_upload_rows += len(to_upload['users'])
        self.update_label.text = 'Sending {} rows to server.'.format(to_upload_rows)

        company = Company()
        company.id = 1
        company.api_token = "2063288158-1"
        url = 'http://74.207.240.88/admins/api/update/{}/{}/up={}'.format(
            company.id,
            company.api_token,
            json.dumps(to_upload).replace(" ", "")
        )
        r = request.urlopen(url)
        data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))

        if data['status'] is 200:
            # Save the local data
            sync_from_server(data=data)
            # update ids with saved data
            update_database(data=data)
            
            self.update_label.text = 'Success. Returned {} rows to update locally. Saved {} rows to server.'.format(
                data['rows_to_create'], data['rows_saved']
            )

    def test_create(self):
        # company = Company()
        # company.id = 1
        # company.company_id = 1
        # company.name = 'Jays Cleaners Montlake'
        # company.street = '2350 24th Ave E'
        # company.suite = 'A'
        # company.city = 'Seattle'
        # company.state = 'WA'
        # company.zipcode = '98125'
        # company.email = 'wondo@eyelevate.com'
        # company.phone = '2063288158'
        # company.api_key = company.phone + '-1'

        # if company.add():
        #     popup = Popup(title='Company Registration',
        #                   content=Label(text='Successfully saved company!'),
        #                   size_hint=(None, None), size=(400, 400))
        #
        # company.close_connection()

        invoice = Invoice()
        invoice.company_id = 1
        invoice.customer_id = 1
        invoice.quantity = 1
        invoice.pretax = 12.50
        invoice.tax = 2.37
        invoice.total = 14.87
        invoice.due_date = '2016-04-20 16:00:00'
        invoice.memo = 'test'
        invoice.status = 1

        if invoice.add():
            popup = Popup(title='Invoice Added',
                              content=Label(text='Successfully added an invoice!'),
                              size_hint=(None, None), size=(400, 400))

            invoice.close_connection()

        popup.open()

    def test_edit(self):
        # company = Company()
        # company.id = 1
        # company.company_id = 1
        # company.name = 'Jays Cleaners Montlake'
        # company.street = '2350 24th Ave E'
        # company.suite = 'A'
        # company.city = 'Seattle'
        # company.state = 'WA'
        # company.zip = '98112'
        # company.email = 'wondo@eyelevate.com'
        # company.phone = '2063288158'
        # company.api_token = company.phone + '-1'

        invoice = Invoice()
        invoice.id = 1
        invoice.invoice_id = 1
        invoice.company_id = 1
        invoice.customer_id = 1
        invoice.quantity = 1
        invoice.pretax = 1
        invoice.tax = 0.1
        invoice.reward_id = 1
        invoice.discount_id = 1
        invoice.total = 1.1
        invoice.status = 1

        if invoice.update():
            popup = Popup(title='Invoice updated',
                          content=Label(text='Successfully edited invoice!'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()

        invoice.close_connection()

    def test_delete(self):
        company = Company()

        data = {
            'company_id': 1
        }

        if company.delete(data):
            popup = Popup(title='Company Registration',
                          content=Label(text='Successfully deleted company!'),
                          size_hint=(None, None), size=(400, 400))
        else:
            popup = Popup(title='Company Registration',
                          content=Label(text='Could not delete Company'),
                          size_hint=(None, None), size=(400, 400))

        company.close_connection()
        popup.open()

    def test_find(self):
        company = Company()

        company.company_id = 1
        c1 = company.find()
        if c1:
            popup = Popup(title='Company Registration',
                          content=Label(text='found company! {}'.format(c1)),
                          size_hint=(None, None), size=(400, 400))

        else:
            popup = Popup(title='Company Registration',
                          content=Label(text='Could not delete Company'),
                          size_hint=(None, None), size=(400, 400))

        company.close_connection()
        popup.open()

    def test_where(self):
        company = Company()

        data = {
            'company_id': 1
        }
        c1 = company.where(data)
        if c1:
            popup = Popup(title='Company Registration',
                          content=Label(text='found company! {}'.format(c1)),
                          size_hint=(None, None), size=(400, 400))
        else:
            popup = Popup(title='Company Registration',
                          content=Label(text='Could not delete Company'),
                          size_hint=(None, None), size=(400, 400))

        company.close_connection()
        popup.open()


class DeliveryScreen(Screen):
    pass


class DropoffScreen(Screen):
    pass


class ReportsScreen(Screen):
    pass


class LoginScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class ScreenManagement(ScreenManager):
    pass


presentation = Builder.load_file("kv/style.kv")


class MainApp(App):
    def build(self):
        # Instantiate logged in user data
        self.user = None
        self.company_id = None
        return presentation


if __name__ == "__main__":
    # Window.clearcolor = (1, 1, 1, 1)
    # Window.size = (1366, 768)
    # Window.fullscreen = True
    MainApp().run()
