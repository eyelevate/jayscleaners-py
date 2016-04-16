# import json

import requests

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
from printers import Printer
from reward_transactions import RewardTransaction
from rewards import Reward
from schedules import Schedule
from taxes import Tax
from transactions import Transaction
from users import User

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import FadeTransition
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.popup import Popup


class MainScreen(Screen):
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
        memo.create_table()
        printer.create_table()
        reward_transaction.create_table()
        reward.create_table()
        schedule.create_table()
        tax.create_table()
        transaction.create_table()
        user.create_table()

    def update_database(self):
        company_id = 1
        company_api = "2063288158-1"
        url = 'http://74.207.240.88/admins/api/update'
        data = {"id": company_id, "api_token": company_api}
        r = requests.post(url, json={data})
        if (r.status_code == 200):
            return r
        else:
            pass

    def test_create(self):
        company = Company()
        company.id = 1
        company.company_id = 1
        company.name = 'Jays Cleaners Montlake'
        company.street = '2350 24th Ave E'
        company.suite = 'A'
        company.city = 'Seattle'
        company.state = 'WA'
        company.zipcode = '98125'
        company.email = 'wondo@eyelevate.com'
        company.phone = '2063288158'
        company.api_key = company.phone + '-1'

        if company.add():
            popup = Popup(title='Company Registration',
                          content=Label(text='Successfully saved company!'),
                          size_hint=(None, None), size=(400, 400))

        company.close_connection()
        popup.open()

    def test_edit(self):
        company = Company()
        company.id = 1
        company.company_id = 1
        company.name = 'Jays Cleaners Montlake'
        company.street = '2350 24th Ave E'
        company.suite = 'A'
        company.city = 'Seattle'
        company.state = 'WA'
        company.zipcode = '98112'
        company.email = 'wondo@eyelevate.com'
        company.phone = '2063288158'
        company.api_key = company.phone + '-1'

        if company.update():
            popup = Popup(title='Company Registration',
                          content=Label(text='Successfully edited company!'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()

        company.close_connection()


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
