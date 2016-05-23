import json
import sys
import platform
import time
import datetime
import os

# Models
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

# Helpers
from kv_generator import KvString
from static import Static

# from escpos import *
# from escpos.printer import Network

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

if platform.system() == 'Darwin':  # Mac
    sys.path.append('/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages')
elif platform.system() == 'Linux':  # Linux
    sys.path.append('/')  # TODO
    # Window.size = (800, 480)
    Window.fullscreen = True
elif platform.system() == 'Windows':  # Windows
    sys.path.append('/')  # TODO


auth_user = User()
ERROR_COLOR = 0.94, 0.33, 0.33, 1
DEFAULT_COLOR = 0.5, 0.5, 0.5, 1.0
unix = time.time()
NOW = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
vars = Static()
CUSTOMER_ID = vars.CUSTOMER_ID
INVOICE_ID = vars.INVOICE_ID
SEARCH_NEW = vars.SEARCH_NEW
LAST10 = vars.LAST10
SEARCH_RESULTS = vars.SEARCH_RESULTS
KV = KvString()


class MainApp(App):
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
            popup = Popup()
            popup.size_hint = (None, None)
            popup.size = '600sp','300sp'

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
                    popup.title = 'Authentication Success!'
                    popup.content = Builder.load_string(
                        KV.popup_alert('You are now logged in as {}!'.format(user.username)))
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
                        popup.title = 'Authentication Success!'
                        content = KV.popup_alert(msg='You are now logged in as {}!'.format(user.username))
                        popup.content = Builder.load_string(content)
                        self.login_popup.dismiss()

                    else:
                        popup.title = 'Authentication Failed!'
                        popup.content = Builder.load_string(
                            KV.popup_alert(msg='Could not find any user with these credentials. '
                                               'Please try again!!'))

                user.close_connection()
                popup.open()

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

        def db_sync(self, *args, **kwargs):
            # start upload text
            self.update_label.text = 'Connecting to server...'

            # create an array of data that need to be uploaded to the server
            to_upload = {}
            to_upload_rows = 0

            colors_1 = Colored()
            to_upload['colors'] = colors_1.where({'color_id': None})
            to_upload_rows += len(to_upload['colors'])
            colors_1.close_connection()

            companies_1 = Company()
            to_upload['companies'] = companies_1.where({'company_id': None})
            to_upload_rows += len(to_upload['companies'])
            companies_1.close_connection()

            custids_1 = Custid()
            to_upload['custids'] = custids_1.where({'cust_id': None})
            to_upload_rows += len(to_upload['custids'])
            custids_1.close_connection()

            deliveries_1 = Delivery()
            to_upload['deliveries'] = deliveries_1.where({'delivery_id': None})
            to_upload_rows += len(to_upload['deliveries'])
            deliveries_1.close_connection()

            discounts_1 = Discount()
            to_upload['discounts'] = discounts_1.where({'discount_id': None})
            to_upload_rows += len(to_upload['discounts'])
            discounts_1.close_connection()

            invoices_1 = Invoice()
            to_upload['invoices'] = invoices_1.where({'invoice_id': None})
            to_upload_rows += len(to_upload['invoices'])
            invoices_1.close_connection()

            invoice_items_1 = InvoiceItem()
            to_upload['invoice_items'] = invoice_items_1.where({'invoice_items_id': None})
            to_upload_rows += len(to_upload['invoice_items'])
            invoice_items_1.close_connection()

            inventories_1 = Inventory()
            to_upload['inventories'] = inventories_1.where({'inventory_id': None})
            to_upload_rows += len(to_upload['inventories'])
            inventories_1.close_connection()

            inventory_items_1 = InventoryItem()
            to_upload['inventory_items'] = inventory_items_1.where({'item_id': None})
            to_upload_rows += len(to_upload['inventory_items'])
            inventory_items_1.close_connection()

            memos_1 = Memo()
            to_upload['memos'] = memos_1.where({'memo_id': None})
            to_upload_rows += len(to_upload['memos'])
            memos_1.close_connection()

            printers_1 = Printer()
            to_upload['printers'] = printers_1.where({'printer_id': None})
            to_upload_rows += len(to_upload['colors'])
            printers_1.close_connection()

            reward_transactions_1 = RewardTransaction()
            to_upload['reward_transactions'] = reward_transactions_1.where({'reward_id': None})
            to_upload_rows += len(to_upload['reward_transactions'])
            reward_transactions_1.close_connection()

            rewards_1 = Reward()
            to_upload['rewards'] = rewards_1.where({'reward_id': None})
            to_upload_rows += len(to_upload['rewards'])
            rewards_1.close_connection()

            schedules_1 = Schedule()
            to_upload['schedules'] = schedules_1.where({'schedule_id': None})
            to_upload_rows += len(to_upload['schedules'])
            schedules_1.close_connection()

            taxes_1 = Tax()
            to_upload['taxes'] = taxes_1.where({'tax_id': None})
            to_upload_rows += len(to_upload['taxes'])
            taxes_1.close_connection()

            transactions_1 = Transaction()
            to_upload['transactions'] = transactions_1.where({'transaction_id': None})
            to_upload_rows += len(to_upload['transactions'])
            transactions_1.close_connection()

            users_1 = User()
            to_upload['users'] = users_1.where({'user_id': None})
            to_upload_rows += len(to_upload['users'])
            users_1.close_connection()

            self.update_label.text = 'Sending {} rows to server.'.format(to_upload_rows)
            company = Company()
            company.id = auth_user.company_id
            data = {'company_id': auth_user.company_id}
            c1 = company.where(data)

            if len(c1) > 0:
                for comp in c1:
                    dt = datetime.datetime.strptime(comp['server_at'], "%Y-%m-%d %H:%M:%S") if comp[
                                                                                                   'server_at'] is not None else datetime.datetime.strptime(
                        '1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
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
            company.close_connection()

        def search_pre(self):

            Thread(target=self.db_sync()).start()

        def test_sys(self):
            print(sys.path)

        def test_crypt(self):
            pass

        def test_print(self, *args, **kwargs):

            pass
            # Epson = Network("10.1.10.10")
            # Epson.text("Hello World\n")
            # # Print QR Code
            # # Epson.qr("You can readme from your smartphone")
            # # Print barcode
            # # Epson.barcode('1324354657687','EAN13',64,2,'','')
            # # Cut paper
            # Epson.cut()
            # print("done")

    class DeliveryScreen(Screen):
        pass

    class DropoffScreen(Screen):
        pass

    class EditCustomerScreen(Screen):
        pass

    class HistoryScreen(Screen):
        pass

    class Last10Screen(Screen):
        last10_table = ObjectProperty(None)
        last10_footer = ObjectProperty(None)

        def get_last10(self):
            vars.SEARCH_RESULTS_STATUS = True # make sure search screen isnt reset
            self.last10_table.clear_widgets()
            self.last10_footer.clear_widgets()

            # create TH
            h1 = KV.widget_item(type='Label', data='#', text_color='000000', rgba=(1, 1, 1, 1))
            h2 = KV.widget_item(type='Label', data='ID', text_color='000000', rgba=(1, 1, 1, 1))
            h3 = KV.widget_item(type='Label', data='Last', text_color='000000', rgba=(1, 1, 1, 1))
            h4 = KV.widget_item(type='Label', data='First', text_color='000000', rgba=(1, 1, 1, 1))
            h5 = KV.widget_item(type='Label', data='Phone', text_color='000000', rgba=(1, 1, 1, 1))
            h6 = KV.widget_item(type='Label', data='Action', text_color='000000', rgba=(1, 1, 1, 1))
            self.last10_table.add_widget(Builder.load_string(h1))
            self.last10_table.add_widget(Builder.load_string(h2))
            self.last10_table.add_widget(Builder.load_string(h3))
            self.last10_table.add_widget(Builder.load_string(h4))
            self.last10_table.add_widget(Builder.load_string(h5))
            self.last10_table.add_widget(Builder.load_string(h6))
            customers = User()
            # create Tbody TR
            even_odd = 0
            if len(vars.LAST10) > 0:
                for customer_id in vars.LAST10:
                    even_odd += 1
                    rgba = '0.369,0.369,0.369,1' if even_odd % 2 == 0 else '0.826, 0.826, 0.826, 1'
                    background_rgba = '0.369,0.369,0.369,0.1' if even_odd % 2 == 0 else '0.826, 0.826, 0.826, 0.1'
                    text_color = 'e5e5e5' if even_odd % 2 == 0 else '5e5e5e'
                    data = {'user_id':customer_id}
                    cust1 = customers.where(data)
                    if len(cust1) > 0:
                        for cust in cust1:

                            tr1 = KV.widget_item(type='Label', data=even_odd, rgba=rgba,
                                                 background_rgba=background_rgba, text_color=text_color)
                            tr2 = KV.widget_item(type='Label', data=customer_id, rgba=rgba,
                                                 background_rgba=background_rgba, text_color=text_color)
                            tr3 = KV.widget_item(type='Label', data=cust['last_name'], rgba=rgba,
                                                 background_rgba=background_rgba, text_color=text_color)
                            tr4 = KV.widget_item(type='Label', data=cust['first_name'], rgba=rgba,
                                                 background_rgba=background_rgba, text_color=text_color)
                            tr5 = KV.widget_item(type='Label', data=cust['phone'], rgba=rgba,
                                                 background_rgba=background_rgba, text_color=text_color)
                            tr6 = KV.widget_item(type='Button', data='View',
                                                 callback='self.parent.parent.parent.customer_select({})'
                                                 .format(customer_id))
                            self.last10_table.add_widget(Builder.load_string(tr1))
                            self.last10_table.add_widget(Builder.load_string(tr2))
                            self.last10_table.add_widget(Builder.load_string(tr3))
                            self.last10_table.add_widget(Builder.load_string(tr4))
                            self.last10_table.add_widget(Builder.load_string(tr5))
                            self.last10_table.add_widget(Builder.load_string(tr6))
            fc_cancel = KV.widget_item(type='Button', data='Cancel', callback='app.root.current = "search"')
            self.last10_footer.add_widget(Builder.load_string(fc_cancel))
            customers.close_connection()

        def customer_select(self, customer_id, *args, **kwargs):
            vars.SEARCH_RESULTS_STATUS = True
            vars.ROW_CAP = 0
            vars.CUSTOMER_ID = customer_id
            vars.INVOICE_ID = None
            vars.ROW_SEARCH = 0, 9
            self.parent.current = 'search'
            # last 10 setup
            vars.update_last_10()

    class LoginScreen(Screen):
        pass

    class NewCustomerScreen(Screen):
        pass

    class PickupScreen(Screen):
        pass

    class ReportsScreen(Screen):
        pass

    class SearchScreen(Screen):
        id = ObjectProperty(None)
        cust_mark_label = ObjectProperty(None)
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
        history_btn = ObjectProperty(None)
        edit_customer_btn = ObjectProperty(None)
        edit_invoice_btn = ObjectProperty(None)
        print_card_btn = ObjectProperty(None)
        reprint_btn = ObjectProperty(None)
        quick_btn = ObjectProperty(None)
        pickup_btn = ObjectProperty(None)
        dropoff_btn = ObjectProperty(None)
        search_popup = ObjectProperty(None)
        search_results_table = ObjectProperty(None)
        search_results_footer = ObjectProperty(None)

        def reset(self, *args, **kwargs):
            vars.ROW_SEARCH = 0, 9
            vars.ROW_CAP = 0
            vars.SEARCH_TEXT = None
            if vars.SEARCH_RESULTS_STATUS:

                self.edit_invoice_btn.disabled = True
                data = {
                    'user_id': vars.CUSTOMER_ID
                }
                customers = User()
                results = customers.where(data)
                self.customer_results(results)
            else:
                vars.CUSTOMER_ID = None
                self.search.text = ''
                self.cust_last_name.text = ''
                self.cust_first_name.text = ''
                self.cust_phone.text = ''
                self.cust_last_drop.text = ''
                self.cust_starch.text = ''
                self.cust_credit.text = ''
                self.cust_invoice_memo.text = ''
                self.cust_important_memo.text = ''
                # show the proper buttons
                self.history_btn.disabled = True
                self.edit_invoice_btn.disabled = True
                self.edit_customer_btn.disabled = True
                self.print_card_btn.disabled = True
                self.reprint_btn.disabled = True
                self.quick_btn.disabled = True
                self.pickup_btn.disabled = True
                self.dropoff_btn.disabled = True
                # clear the search text input
                self.search.text = ''
                # clear the inventory table
                self.invoice_table.clear_widgets()
                # add the table headers
                self.create_invoice_headers()

            vars.SEARCH_RESULTS_STATUS = False

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
                    self.customer_results(cust1)

                elif len(search_text) == 6:  # this is an invoice number
                    data = {
                        'invoice_id': '"{}"'.format(int(self.search.text))
                    }
                    inv = Invoice()
                    inv_1 = inv.where(data)
                    if len(inv_1) > 0:
                        for invoice in inv_1:
                            vars.INVOICE_ID = self.search.text
                            vars.CUSTOMER_ID = invoice['customer_id']
                            self.invoice_selected(invoice_id=vars.INVOICE_ID)


                    else:
                        self.search_popup.title = 'No such invoice'
                        self.search_popup.size_hint = None, None
                        self.search_popup.size = 900, 600
                        content = KV.popup_alert(msg="Could not find an invoice with this invoice id. Please try again")
                        self.search_popup.content = Builder.load_string(content)
                        self.search_popup.open()
                else:  # look for a customer id
                    data = {
                        'user_id': self.search.text
                    }
                    cust1 = customers.where(data)
                    self.customer_results(cust1)


            else:  # Lookup by last name || mark
                data = {
                    'last_name': '"%{}%"'.format(self.search.text),
                }
                vars.ROW_CAP = len(customers.like(data))
                vars.SEARCH_TEXT = self.search.text

                data = {
                    'last_name': '"%{}%"'.format(self.search.text),
                    'ORDER_BY': 'last_name ASC',
                    'LIMIT': '{},{}'.format(vars.ROW_SEARCH[0], vars.ROW_SEARCH[1])
                }
                cust1 = customers.like(data)
                self.customer_results(cust1)

            customers.close_connection()


        def is_int(self, s):
            try:
                int(s)
                return True
            except ValueError:
                return False

        def create_invoice_headers(self):

            h1 = KV.invoice_tr(0, 'Inv')
            h3 = KV.invoice_tr(0, 'Due')
            h4 = KV.invoice_tr(0, 'Rack')
            h5 = KV.invoice_tr(0, 'Qty')
            h6 = KV.invoice_tr(0, 'Total')
            self.invoice_table.add_widget(Builder.load_string(h1))
            self.invoice_table.add_widget(Builder.load_string(h3))
            self.invoice_table.add_widget(Builder.load_string(h4))
            self.invoice_table.add_widget(Builder.load_string(h5))
            self.invoice_table.add_widget(Builder.load_string(h6))
            return True

        def create_invoice_row(self, row, *args, **kwargs):
            """ Creates invoice table row and displays it to screen """
            check_invoice_id = int(vars.INVOICE_ID) if vars.INVOICE_ID else vars.INVOICE_ID
            invoice_id = row['invoice_id']
            quantity = row['quantity']
            rack = row['rack']
            total = row['total']
            due = row['due_date']
            dt = datetime.datetime.strptime(due,
                                            "%Y-%m-%d %H:%M:%S") if due is not None else datetime.datetime.strptime(
                '1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
            due_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
            dow = self.dow(dt.replace(tzinfo=datetime.timezone.utc).weekday())
            due_date = dt.strftime('%m/%d {}').format(dow)
            dt = datetime.datetime.strptime(NOW,
                                            "%Y-%m-%d %H:%M:%S") if NOW is not None else datetime.datetime.strptime(
                '1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
            now_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
            # check to see if invoice is overdue

            if rack:  # racked and ready
                state = 3
            elif due_strtotime < now_strtotime:  # overdue
                state = 2
            else:  # Not ready yet
                state = 1

            selected = True if invoice_id == check_invoice_id else False

            tr_1 = KV.invoice_tr(state, invoice_id, selected=selected, invoice_id=invoice_id)
            tr_3 = KV.invoice_tr(state, due_date, selected=selected, invoice_id=invoice_id)
            tr_4 = KV.invoice_tr(state, rack, selected=selected, invoice_id=invoice_id)
            tr_5 = KV.invoice_tr(state, quantity, selected=selected, invoice_id=invoice_id)
            tr_6 = KV.invoice_tr(state, total, selected=selected, invoice_id=invoice_id)
            self.invoice_table.add_widget(Builder.load_string(tr_1))
            self.invoice_table.add_widget(Builder.load_string(tr_3))
            self.invoice_table.add_widget(Builder.load_string(tr_4))
            self.invoice_table.add_widget(Builder.load_string(tr_5))
            self.invoice_table.add_widget(Builder.load_string(tr_6))

            return True

        def invoice_selected(self, invoice_id):
            vars.INVOICE_ID = invoice_id
            data = {
                'user_id': '"{}"'.format(vars.CUSTOMER_ID)
            }
            customers = User()
            cust1 = customers.where(data)
            self.customer_results(cust1)

            # show the edit button
            self.edit_invoice_btn.disabled = False
            customers.close_connection()

        def customer_select(self, customer_id):
            users = User()
            data = {'customer_id': customer_id}
            customers = users.where(data)
            self.customer_results(customers)
            vars.INVOICE_ID = None
            users.close_connection()

        def customer_results(self, data):
            # Found customer via where, now display data to screen
            if len(data) == 1:

                for result in data:
                    vars.CUSTOMER_ID = result['user_id']
                    # last 10 setup
                    vars.update_last_10()
                    # clear the current widget
                    self.invoice_table.clear_widgets()
                    # add the table headers
                    self.create_invoice_headers()
                    # get the invoice data
                    data = {
                        'customer_id': vars.CUSTOMER_ID,
                        'status': {'<': 3}
                    }

                    invoices = Invoice()
                    invs = invoices.where(data)
                    # set the new invoice table
                    if len(invs) > 0:
                        for inv in invs:
                            self.create_invoice_row(inv)

                    # get last drop data
                    data = {
                        'customer_id': vars.CUSTOMER_ID,
                        'LIMIT': 1,
                        'ORDER_BY': 'invoice_id DESC'
                    }
                    last_invoice = invoices.where(data)
                    last_drop = ''
                    if len(last_invoice) > 0:
                        for last in last_invoice:
                            last_drop = last['created_at']
                            if last_drop is not None:

                                dt = datetime.datetime.strptime(last_drop, "%Y-%m-%d %H:%M:%S")
                                dow = self.dow(dt.replace(tzinfo=datetime.timezone.utc).weekday())
                                last_drop = dt.strftime('{} %m/%d/%y %I:%M%P').format(dow)
                            else:
                                last_drop = ''
                    invoices.close_connection()

                    # get the custid data
                    data = {'customer_id': vars.CUSTOMER_ID}
                    custids = Custid()
                    custid_string = custids.make_string(custids.where(data))

                    # display data
                    self.cust_mark_label.text = custid_string
                    self.cust_last_name.text = result['last_name']
                    self.cust_first_name.text = result['first_name']
                    self.cust_phone.text = result['phone']
                    self.cust_last_drop.text = last_drop
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
                    custids.close_connection()
                # show the proper buttons
                self.history_btn.disabled = False
                self.edit_customer_btn.disabled = False
                self.print_card_btn.disabled = False
                self.reprint_btn.disabled = False
                self.quick_btn.disabled = False
                self.pickup_btn.disabled = False
                self.dropoff_btn.disabled = False
                # clear the search text input
                self.search.text = ''

            elif len(data) > 1:
                # show results in new screen search results
                self.search_results(data)
            else:

                popup = Popup()
                popup.title = 'Search Results'
                popup.size_hint = None, None
                popup.size = 800, 600
                content = KV.popup_alert(msg="No customers found! Please try again!")
                popup.content = Builder.load_string(content)
                popup.open()

        def search_results(self, data):
            vars.SEARCH_RESULTS = data
            self.parent.current = 'search_results'

            pass

        def dow(self, day):
            if day == 0:
                return 'Mon'
            elif day == 1:
                return 'Tue'
            elif day == 2:
                return 'Wed'
            elif day == 3:
                return 'Thu'
            elif day == 4:
                return 'Fri'
            elif day == 5:
                return 'Sat'
            else:
                return 'Sun'

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

    class SearchResultsScreen(Screen):
        """Takes in a customer searched dictionary and gives a table to select which customer we want to find
        once the user selects the customer gives an action to go back to the search screen with the correct
        customer id"""
        search_results_table = ObjectProperty(None)
        search_results_footer = ObjectProperty(None)
        search_results_label = ObjectProperty(None)

        def get_results(self):
            self.search_results_table.clear_widgets()
            self.search_results_footer.clear_widgets()
            self.search_results_label.text = "[color=000000]Showing rows [b]{}[/b] - [b]{}[/b] out of [b]{}[/b][/color]".format(
                vars.ROW_SEARCH[0], vars.ROW_SEARCH[1], vars.ROW_CAP
            )

            # create TH
            h1 = KV.widget_item(type='Label', data='ID', text_color='000000', rgba=(1, 1, 1, 1))
            h2 = KV.widget_item(type='Label', data='Last', text_color='000000', rgba=(1, 1, 1, 1))
            h3 = KV.widget_item(type='Label', data='First', text_color='000000', rgba=(1, 1, 1, 1))
            h4 = KV.widget_item(type='Label', data='Phone', text_color='000000', rgba=(1, 1, 1, 1))
            h5 = KV.widget_item(type='Label', data='Action', text_color='000000', rgba=(1, 1, 1, 1))
            self.search_results_table.add_widget(Builder.load_string(h1))
            self.search_results_table.add_widget(Builder.load_string(h2))
            self.search_results_table.add_widget(Builder.load_string(h3))
            self.search_results_table.add_widget(Builder.load_string(h4))
            self.search_results_table.add_widget(Builder.load_string(h5))

            # create Tbody TR
            even_odd = 0
            if len(vars.SEARCH_RESULTS) > 0:
                for cust in vars.SEARCH_RESULTS:
                    even_odd += 1
                    first_name = cust['first_name']
                    last_name = cust['last_name']
                    customer_id = cust['user_id']
                    phone = cust['phone']
                    rgba = '0.369,0.369,0.369,1' if even_odd % 2 == 0 else '0.826, 0.826, 0.826, 1'
                    background_rgba = '0.369,0.369,0.369,0.1' if even_odd % 2 == 0 else '0.826, 0.826, 0.826, 0.1'
                    text_color = 'e5e5e5' if even_odd % 2 == 0 else '5e5e5e'
                    tr1 = KV.widget_item(type='Label', data=customer_id, rgba=rgba,
                                         background_rgba=background_rgba, text_color=text_color)
                    tr2 = KV.widget_item(type='Label', data=last_name, rgba=rgba,
                                         background_rgba=background_rgba, text_color=text_color)
                    tr3 = KV.widget_item(type='Label', data=first_name, rgba=rgba,
                                         background_rgba=background_rgba, text_color=text_color)
                    tr4 = KV.widget_item(type='Label', data=phone, rgba=rgba,
                                         background_rgba=background_rgba, text_color=text_color)
                    tr5 = KV.widget_item(type='Button', data='View',
                                         callback='self.parent.parent.parent.customer_select({})'
                                         .format(customer_id))
                    self.search_results_table.add_widget(Builder.load_string(tr1))
                    self.search_results_table.add_widget(Builder.load_string(tr2))
                    self.search_results_table.add_widget(Builder.load_string(tr3))
                    self.search_results_table.add_widget(Builder.load_string(tr4))
                    self.search_results_table.add_widget(Builder.load_string(tr5))
            fc_cancel = KV.widget_item(type='Button', data='Cancel', callback='app.root.current = "search"')
            fc_up = KV.widget_item(type='Button', data='Prev', callback='self.parent.parent.parent.prev()')
            fc_down = KV.widget_item(type='Button', data='Next', callback='self.parent.parent.parent.next()')
            self.search_results_footer.add_widget(Builder.load_string(fc_cancel))
            self.search_results_footer.add_widget(Builder.load_string(fc_up))
            self.search_results_footer.add_widget(Builder.load_string(fc_down))
            vars.SEARCH_RESULTS = []

        def next(self):
            if vars.ROW_SEARCH[1] + 10 >= vars.ROW_CAP:
                vars.ROW_SEARCH = vars.ROW_CAP - 10, vars.ROW_CAP
            else:
                vars.ROW_SEARCH = vars.ROW_SEARCH[0] + 10, vars.ROW_SEARCH[1] + 10
            data = {
                'last_name': '"%{}%"'.format(vars.SEARCH_TEXT),
                'ORDER_BY': 'last_name ASC',
                'LIMIT': '{},{}'.format(vars.ROW_SEARCH[0], vars.ROW_SEARCH[1])
            }
            customers = User()
            cust1 = customers.like(data)
            vars.SEARCH_RESULTS = cust1
            self.search_results_label.text = "[color=000000]Showing rows [b]{}[/b] - [b]{}[/b] out of [b]{}[/b][/color]".format(
                vars.ROW_SEARCH[0], vars.ROW_SEARCH[1], vars.ROW_CAP
            )
            self.get_results()

        def prev(self):
            if vars.ROW_SEARCH[1] - 10 < 10:
                vars.ROW_SEARCH = 0, 9
            else:
                vars.ROW_SEARCH = vars.ROW_SEARCH[0] - 10, vars.ROW_SEARCH[1] - 10

            self.search_results_label.text = "[color=000000]Showing rows [b]{}[/b] - [b]{}[/b] out of [b]{}[/b][/color]".format(
                vars.ROW_SEARCH[0], vars.ROW_SEARCH[1], vars.ROW_CAP
            )

            data = {
                'last_name': '"%{}%"'.format(vars.SEARCH_TEXT),
                'ORDER_BY': 'last_name ASC',
                'LIMIT': '{},{}'.format(vars.ROW_SEARCH[0], vars.ROW_SEARCH[1])
            }
            customers = User()
            cust1 = customers.like(data)
            vars.SEARCH_RESULTS = cust1
            self.search_results_label.text = "[color=000000]Showing rows [b]{}[/b] - [b]{}[/b] out of [b]{}[/b][/color]".format(
                vars.ROW_SEARCH[0], vars.ROW_SEARCH[1], vars.ROW_CAP
            )
            self.get_results()

        def customer_select(self, customer_id, *args, **kwargs):
            vars.SEARCH_RESULTS_STATUS = True
            vars.ROW_CAP = 0
            vars.CUSTOMER_ID = customer_id
            vars.INVOICE_ID = None
            vars.ROW_SEARCH = 0, 9
            self.parent.current = 'search'
            # last 10 setup
            vars.update_last_10()


    class SettingsScreen(Screen):
        pass

    class ScreenManagement(ScreenManager):
        pass

    # load kv files
    presentation = Builder.load_file("kv/main.kv")

    def build(self):
        return self.presentation


if __name__ == "__main__":

    # Window.clearcolor = (1, 1, 1, 1)
    MainApp().run()
