import json
import sys
import platform
import time
import datetime

if platform.system() == 'Darwin':  # Mac
    sys.path.append('/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages')
elif platform.system() == 'Linux':  # Linux
    sys.path.append('/')  # TODO
elif platform.system() == 'Windows':  # Windows
    sys.path.append('/')  # TODO

from colors import Colored
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

from escpos import *
from escpos.printer import Network

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import FadeTransition
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics.instructions import Canvas
from kivy.graphics import Rectangle, Color

from threading import Thread
from urllib import error
from urllib import request
from urllib import parse
from urllib.parse import urlencode
from urllib.request import urlopen

auth_user = User()
ERROR_COLOR = 0.94, 0.33, 0.33, 1
DEFAULT_COLOR = 0.5, 0.5, 0.5, 1.0
unix = time.time()
NOW = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))


class MainScreen(Screen):
    update_label = ObjectProperty(None)
    login_button = ObjectProperty(None)
    settings_button = ObjectProperty(None)
    reports_button = ObjectProperty(None)
    delivery_button = ObjectProperty(None)
    dropoff_button = ObjectProperty(None)
    update_button = ObjectProperty(None)
    username = ObjectProperty(None)
    password = ObjectProperty(None)
    login_popup = ObjectProperty(None)

    def update_info(self):
        info = "Last updated {}".format("today")
        return info

    def login(self, *args, **kwargs):

        user = User()
        user.username = self.username.text
        user.password = self.password.text  # cipher and salt later

        # validate the form data
        if not user.username:
            self.username.hint_text = "Username must exist"
            self.username.hint_text_color = ERROR_COLOR
        if not user.password:
            self.password.hint_text = "Password cannot be left empty"
            self.password.hint_text_color = ERROR_COLOR

        # authenticate
        if user.username and user.password:
            self.username.hint_text = "Enter username"
            self.username.hint_text_color = DEFAULT_COLOR
            self.password.hint_text = "Enter password"
            self.password.hint_text_color = DEFAULT_COLOR
            # first check to see if you can authenticate locally
            u1 = user.auth(username=user.username, password=user.password)
            if u1:  # found user register variables, sync data, and show links

                self.login_button.text = "Logout"
                self.login_button.bind(on_release=self.logout)
                self.update_button.disabled = False
                self.settings_button.disabled = False
                self.reports_button.disabled = False
                self.dropoff_button.disabled = False
                self.delivery_button.disabled = False
                self.settings_button.disabled = False
                self.settings_button.disabled = False

                auth_user.username = user.username
                auth_user.company_id = user.company_id
                popup_1 = Popup(title='Authentication Success',
                                content=Label(text='Welcome! You are now logged in as {}!'.format(user.username)),
                                size_hint=(None, None), size=(1000, 600))
                self.login_popup.dismiss()
            else:  # did not find user in local db, look for user on server
                url = 'http://74.207.240.88/admins/api/authenticate/{}/{}'.format(
                    user.username,
                    user.password
                )
                r = request.urlopen(url)
                data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))

                if data['status'] is True:
                    self.login_button.text = "Logout"
                    self.login_button.bind(on_release=self.logout)
                    self.update_button.disabled = False
                    self.settings_button.disabled = False
                    self.reports_button.disabled = False
                    self.dropoff_button.disabled = False
                    self.delivery_button.disabled = False
                    self.settings_button.disabled = False
                    self.settings_button.disabled = False

                    auth_user.username = user.username
                    auth_user.company_id = data['company_id']
                    popup_1 = Popup(title='Authentication Success',
                                    content=Label(text='Welcome! You are now logged in as {}!'.format(user.username)),
                                    size_hint=(None, None), size=(1000, 600))
                    self.login_popup.dismiss()
                else:

                    popup_1 = Popup(title='Authentication Failed',
                                    content=Label(
                                        text='Could not find any user with these credentials. Please try again!'),
                                    size_hint=(None, None), size=(1000, 600))

            user.close_connection()
            popup_1.open()

    def logout(self, *args, **kwargs):
        self.username.text = ''
        self.password.text = ''
        auth_user.username = None
        auth_user.company_id = None
        self.login_button.text = "Login"
        self.login_button.bind(on_release=self.login)
        self.update_button.disabled = True
        self.settings_button.disabled = True
        self.reports_button.disabled = True
        self.dropoff_button.disabled = True
        self.delivery_button.disabled = True
        self.settings_button.disabled = True
        self.settings_button.disabled = True

    def migrate(self, *args, **kwargs):
        color = Colored()
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

        colors_1 = Colored()
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
        company.id = auth_user.company_id
        data = {'company_id': auth_user.company_id}
        c1 = company.where(data)

        if len(c1) > 0:
            for comp in c1:
                dt = datetime.datetime.strptime(comp['server_at'], "%Y-%m-%d %H:%M:%S") if comp['server_at'] is not None else datetime.datetime.strptime('1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
                company.server_at = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
                company.api_token = comp['api_token']
        else:
            company.server_at = 0
            company.api_token = '2063288158-1'

        url = 'http://74.207.240.88/admins/api/update/{}/{}/{}/up={}'.format(
            company.id,
            company.api_token,
            company.server_at,
            json.dumps(to_upload).replace(" ", "")
        )
        r = request.urlopen(url)
        data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))

        if data['status'] is 200:
            # Save the local data
            sync_from_server(data=data)
            # update ids with saved data & update company table with server_at timestamp
            update_database(data=data)
            # update server_at in companies with most current timestamp

            where = {'company_id': auth_user.company_id}
            data = {'server_at': NOW}
            company.put(where, data)
            rows_to_create = data['rows_to_create'] if 'rows_to_create' in data else 0
            rows_saved = data['rows_saved'] if 'rows_saved' in data else 0

            self.update_label.text = 'Success. Returned {} rows to update locally. Saved {} rows to server.'.format(
                rows_to_create, rows_saved
            )

    def search_pre(self):
        search = SearchScreen()
        search.reset()
        Thread(target=self.db_sync()).start()

    def test_sys(self):
        print(sys.path)

    def test_crypt(self):
        pass

    def test_create(self):

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
        print(c1)
        for comp in c1:
            print(comp['name'])

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

    def authenticate(self):
        print('authenticated')

    def test_print(self, *args, **kwargs):

        Epson = Network("10.1.10.10")
        Epson.text("Hello World\n")
        # Print QR Code
        # Epson.qr("You can readme from your smartphone")
        # Print barcode
        # Epson.barcode('1324354657687','EAN13',64,2,'','')
        # Cut paper
        Epson.cut()
        print("done")


class DeliveryScreen(Screen):
    pass


class SearchScreen(Screen):
    customer_id = None
    invoice_table = ObjectProperty(None)
    search = ObjectProperty(None)
    cust_last_name = ObjectProperty(None)
    cust_first_name = ObjectProperty(None)
    cust_phone = ObjectProperty(None)
    cust_last_drop = ObjectProperty(None)
    cust_starch = ObjectProperty(None)
    cust_credit = ObjectProperty(None)
    cust_invoice_memo = ObjectProperty(None)
    cust_important_memo = ObjectProperty(None)

    def reset(self):
        self.search.text = ''
        self.cust_last_name.text = ''
        self.cust_first_name.text = ''
        self.cust_phone.text = ''
        self.cust_last_drop.text = ''
        self.cust_starch.text = ''
        self.cust_credit.text = ''
        self.cust_invoice_memo.text = ''
        self.cust_important_memo.text = ''

    def search_customer(self, *args, **kwargs):
        search_text = self.search.text
        customers = User()
        if self.is_int(search_text):
            # check to see if length is 7 or greater
            if len(search_text) >= 7:  # This is a phone number
                # First check to see if the number is exact
                data = {
                    'phone': '"%{}%"'.format(self.search.text)
                }
                cust1 = customers.like(data)
                # Found customer via where, now display data to screen
                if len(cust1) == 1:

                    for result in cust1:
                        # clear the current widget
                        self.invoice_table.clear_widgets()
                        # add the table headers
                        self.create_invoice_headers()
                        # get the invoice data
                        data = {
                            'customer_id' : result['user_id'],
                            'status': {'<':3}
                        }

                        invoices = Invoice()
                        invs = invoices.where(data)
                        # set the new invoice table
                        if len(invs) > 0:
                            for inv in invs:
                                self.create_invoice_row(inv)
                        # get the custid data

                        # display data
                        self.cust_last_name.text = result['last_name']
                        self.cust_first_name.text = result['first_name']
                        self.cust_phone.text = result['phone']
                        self.cust_last_drop.text = ''
                        self.cust_starch.text = self.get_starch_by_id(result['starch'])
                        self.cust_credit.text = '0.00'
                        try:
                            self.cust_invoice_memo.text = result['invoice_memo']
                        except AttributeError:
                            self.cust_invoice_memo.text = ''

                        try:
                            self.cust_important_memo.text = result['important_memo']
                        except AttributeError:
                            self.cust_important_memo.text = ''

                    # show the proper buttons

                    # clear the search text input
                    self.search.text = ''

                elif len(cust1) > 1:
                    # create popup instance and show customers as a list
                    pass
                else:
                    # If not exact number then use like statements
                    pass

            elif len(search_text) == 6:  # this is an invoice number
                # data = {
                #     'invoice_id' : self.search
                # }
                # inv = Invoice()
                # inv_1 = inv.where(data)
                # if inv_1:
                #
                # else:
                pass
            else:
                pass
        else:  # Lookup by last name || mark
            pass

    def is_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def create_invoice_headers(self):
        h1 = self.build_tr(0,'Inv')
        h3 = self.build_tr(0,'Due')
        h4 = self.build_tr(0,'Rack')
        h5 = self.build_tr(0,'Qty')
        h6 = self.build_tr(0,'Total')
        self.invoice_table.add_widget(Builder.load_string(h1))
        self.invoice_table.add_widget(Builder.load_string(h3))
        self.invoice_table.add_widget(Builder.load_string(h4))
        self.invoice_table.add_widget(Builder.load_string(h5))
        self.invoice_table.add_widget(Builder.load_string(h6))
        return True

    def create_invoice_row(self, row, *args, **kwargs):
        """ Creates invoice table row and displays it to screen """
        invoice_id = row['invoice_id']
        quantity = row['quantity']
        rack = row['rack']
        total = row['total']
        due = row['due_date']
        dt = datetime.datetime.strptime(due, "%Y-%m-%d %H:%M:%S") if due is not None else datetime.datetime.strptime(
            '1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
        due_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        due_date = dt.strftime('%m/%d')
        dt = datetime.datetime.strptime(NOW, "%Y-%m-%d %H:%M:%S") if NOW is not None else datetime.datetime.strptime(
            '1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
        now_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        # check to see if invoice is overdue

        if rack: # racked and ready
            state = 3
        elif due_strtotime < now_strtotime: # overdue
            state = 2
        else: # Not ready yet
            state = 1

        tr_1 = self.build_tr(state,invoice_id)
        tr_3 = self.build_tr(state,due_date)
        tr_4 = self.build_tr(state,rack)
        tr_5 = self.build_tr(state,quantity)
        tr_6 = self.build_tr(state,total)
        self.invoice_table.add_widget(Builder.load_string(tr_1))
        self.invoice_table.add_widget(Builder.load_string(tr_3))
        self.invoice_table.add_widget(Builder.load_string(tr_4))
        self.invoice_table.add_widget(Builder.load_string(tr_5))
        self.invoice_table.add_widget(Builder.load_string(tr_6))

        return True

    def build_tr(self, state, data):
        if state == 0:
            tr = '''
Label:
    size_hint_y: None
    markup: True
    text: "[color=000000][b]{}[/b][/color]"
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
'''.format(data)
        elif state == 3: # Racked and Ready
            tr = '''
Label:
    size_hint_y: None
    markup: True
    text: "[color=3FBF3F][b]{}[/b][/color]"
    canvas.before:
        Color:
            rgba: 0.847, 0.968, 0.847, 1
        Rectangle:
            pos: self.pos
            size: self.size
'''.format(data)
        elif state == 2: # Overdue
            tr = '''
Label:
    size_hint_y: None
    markup: True
    text: "[color=0F47FF][b]{}[/b][/color]"
    canvas.before:
        Color:
            rgba: 0.816, 0.847, 0.961, 1
        Rectangle:
            pos: self.pos
            size: self.size
'''.format(data)
        else: # Not ready yet
            tr = '''
Label:
    size_hint_y: None
    markup: True
    text: "[color=5e5e5e]{}[/color]"
    canvas.before:
        Color:
            rgba: 0.826, 0.826, 0.826, 1
        Rectangle:
            pos: self.pos
            size: self.size
'''.format(data)
        return tr

    def get_starch_by_id(self, starch):
        if starch == 1:
            return 'None'
        elif starch == 2:
            return 'Light'
        elif starch == 3:
            return 'Medium'
        elif starch == 4:
            return 'Heavy'
        else:
            return 'Not Set'

class ReportsScreen(Screen):
    pass


class LoginScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class DropoffScreen(Screen):
    pass


class PickupScreen(Screen):
    pass

class NewCustomerScreen(Screen):
    pass

class EditCustomerScreen(Screen):
    pass

class HistoryScreen(Screen):
    pass



class ScreenManagement(ScreenManager):
    pass


# load kv files
presentation = Builder.load_file("kv/main.kv")

class MainApp(App):
    def build(self):
        return presentation


if __name__ == "__main__":
    # Window.clearcolor = (1, 1, 1, 1)
    # Window.size = (1366, 768)
    # Window.fullscreen = True
    MainApp().run()
