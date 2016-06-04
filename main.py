import json
import sys
import platform
import time
import datetime
import os
import calendar

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
from jobs import Job
from static import Static
from sync import Sync

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
elif platform.system() == 'Windows':  # Windows
    sys.path.append('/')  # TODO

auth_user = User()
Job = Job()
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
        popup.size = '600sp', '300sp'

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
                for user1 in u1:
                    auth_user.id = user1['id']
                    auth_user.user_id = user1['user_id']
                    auth_user.username = user1['username']
                    auth_user.company_id = user1['company_id']

                popup.title = 'Authentication Success!'
                popup.content = Builder.load_string(
                    KV.popup_alert('You are now logged in as {}!'.format(user.username)))
                self.login_popup.dismiss()
            else:  # did not find user in local db, look for user on server
                sync = Sync()
                data = sync.server_login(username=user.username, password=user.password)

                if data['status']:
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

    def db_sync(self, *args, **kwargs):
        # self.update_label.text = 'Connecting to server...'
        sync = Sync()
        # sync.migrate()
        sync.db_sync(auth_user.company_id)
        # sync.get_chunk(table='invoices',start=50001,end=60000)

        # self.update_label.text = 'Server updated at {}'.format()

    def search_pre(self):

        Thread(target=self.db_sync()).start()

    def test_sys(self):
        print(sys.path)

    def test_mark(self):
        # marks = Custid()
        # customers = User()
        # starch = customers.get_starch(3)
        # custid = marks.create_customer_mark(last_name='Tim',
        #                                     customer_id=str(6251) if Job.is_int(6251) else '6251',
        #                                     starch='Medium')
        # print(starch)
        # print(custid)
        invoices = Invoice()
        data = {'id': {'>': 0}}
        invs = invoices.where(data)
        if invs:
            for inv in invs:
                invoice_id = inv['id']
                customer_id = inv['customer_id']
                data = {'customer_id':customer_id}
                custs = User()
                if custs:
                    for cust in custs:
                        cust_id = cust['id']
                        invs_1 = Invoice()
                        where = {'id':invoice_id}
                        data = {'customer_id':cust_id}
                data = {'status': 5}
                where = {'id': inv['id']}
                invoices.put(where=where, data=data)
                print("Saved id {} to status 5".format(inv['id']))

    def test_crypt(self):
        dt = datetime.datetime.strptime(NOW, "%Y-%m-%d %H:%M:%S") if NOW is not None else datetime.datetime.strptime(
            '1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")

        print(str(dt).replace(" ", "_"))
        server_at = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        print(server_at)
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
    last_name = ObjectProperty(None)
    first_name = ObjectProperty(None)
    phone = ObjectProperty(None)
    email = ObjectProperty(None)
    important_memo = ObjectProperty(None)
    invoice_memo = ObjectProperty(None)
    shirt_finish = 1
    shirt_preference = 1
    shirts_finish_hanger = ObjectProperty(None)
    shirts_finish_box = ObjectProperty(None)
    shirts_preference_none = ObjectProperty(None)
    shirts_preference_light = ObjectProperty(None)
    shirts_preference_medium = ObjectProperty(None)
    shirts_preference_heavy = ObjectProperty(None)
    is_delivery = ObjectProperty(None)
    mark_text = ObjectProperty(None)
    marks_table = ObjectProperty(None)
    street = ObjectProperty(None)
    suite = ObjectProperty(None)
    city = ObjectProperty(None)
    zipcode = ObjectProperty(None)
    concierge_name = ObjectProperty(None)
    concierge_number = ObjectProperty(None)
    special_instructions = ObjectProperty(None)

    def reset(self):
        self.last_name.text = ''
        self.last_name.hint_text = 'Last Name'
        self.last_name.hint_text_color = DEFAULT_COLOR
        self.first_name.text = ''
        self.first_name.hint_text = 'First Name'
        self.first_name.hint_text_color = DEFAULT_COLOR
        self.phone.text = ''
        self.phone.hint_text = '(XXX) XXX-XXXX'
        self.phone.hint_text_color = DEFAULT_COLOR
        self.email.text = ''
        self.email.hint_text = 'example@example.com'
        self.email.hint_text_color = DEFAULT_COLOR
        self.important_memo.text = ''
        self.important_memo.hint_text = 'Important Memo'
        self.important_memo.hint_text_color = DEFAULT_COLOR
        self.invoice_memo.text = ''
        self.invoice_memo.hint_text = 'Invoiced Memo'
        self.invoice_memo.hint_text_color = DEFAULT_COLOR
        self.shirts_finish_hanger.active = True
        self.shirts_finish_box.active = False
        self.shirts_preference_none.active = True
        self.shirts_preference_light.active = False
        self.shirts_preference_medium.active = False
        self.shirts_preference_heavy.active = False
        self.street.text = ''
        self.street.hint_text = 'Street Address'
        self.street.hint_text_color = DEFAULT_COLOR
        self.street.disabled = True
        self.suite.text = ''
        self.suite.hint_text = 'Suite'
        self.suite.hint_text_color = DEFAULT_COLOR
        self.suite.disabled = True
        self.city.text = ''
        self.city.hint_text = 'City'
        self.city.hint_text_color = DEFAULT_COLOR
        self.city.disabled = True
        self.zipcode.text = ''
        self.zipcode.hint_text = 'Zipcode'
        self.zipcode.hint_text_color = DEFAULT_COLOR
        self.zipcode.disabled = True
        self.concierge_name.text = ''
        self.concierge_name.hint_text = 'Concierge Name'
        self.concierge_name.hint_text_color = DEFAULT_COLOR
        self.concierge_name.disabled = True
        self.concierge_number.text = ''
        self.concierge_number.hint_text = 'Concierge Number'
        self.concierge_number.hint_text_color = DEFAULT_COLOR
        self.concierge_number.disabled = True
        self.special_instructions.text = ''
        self.special_instructions.hint_text = 'Special Instructions'
        self.special_instructions.hint_text_color = DEFAULT_COLOR
        self.special_instructions.disabled = True
        self.mark_text.text = ''
        self.is_delivery.active = False
        self.marks_table.clear_widgets()

    def load(self):
        if vars.CUSTOMER_ID:
            customers = User()
            customers.user_id = vars.CUSTOMER_ID
            data = {'user_id': vars.CUSTOMER_ID}
            customer = customers.where(data)
            if customer:
                for cust in customer:
                    self.last_name.text = cust['last_name'] if cust['last_name'] else ''
                    self.last_name.hint_text = 'Last Name'
                    self.last_name.hint_text_color = DEFAULT_COLOR
                    self.first_name.text = cust['first_name'] if cust['first_name'] else ''
                    self.first_name.hint_text = 'First Name'
                    self.first_name.hint_text_color = DEFAULT_COLOR
                    self.phone.text = cust['phone'] if cust['phone'] else ''
                    self.phone.hint_text = '(XXX) XXX-XXXX'
                    self.phone.hint_text_color = DEFAULT_COLOR
                    self.email.text = cust['email'] if cust['email'] else ''
                    self.email.hint_text = 'example@example.com'
                    self.email.hint_text_color = DEFAULT_COLOR
                    self.important_memo.text = cust['important_memo'] if cust['important_memo'] else ''
                    self.important_memo.hint_text = 'Important Memo'
                    self.important_memo.hint_text_color = DEFAULT_COLOR
                    self.invoice_memo.text = cust['invoice_memo'] if cust['invoice_memo'] else ''
                    self.invoice_memo.hint_text = 'Invoiced Memo'
                    self.invoice_memo.hint_text_color = DEFAULT_COLOR
                    if cust['shirt'] == 1:
                        self.shirts_finish_hanger.active = True
                    if cust['shirt'] == 2:
                        self.shirts_finish_box.active = True
                    if cust['starch'] == 1:
                        self.shirts_preference_none.active = True
                    if cust['starch'] == 2:
                        self.shirts_preference_light.active = True
                    if cust['starch'] == 3:
                        self.shirts_preference_medium.active = True
                    if cust['starch'] == 4:
                        self.shirts_preference_heavy.active = True
                    if cust['street']:
                        self.is_delivery.active = False
                        self.street.text = cust['street'] if cust['street'] else ''
                        self.street.hint_text = 'Street Address'
                        self.street.hint_text_color = DEFAULT_COLOR
                        self.street.disabled = False
                        self.suite.text = cust['suite'] if cust['suite'] else ''
                        self.suite.hint_text = 'Suite'
                        self.suite.hint_text_color = DEFAULT_COLOR
                        self.suite.disabled = False
                        self.city.text = cust['city'] if cust['city'] else ''
                        self.city.hint_text = 'City'
                        self.city.hint_text_color = DEFAULT_COLOR
                        self.city.disabled = False
                        self.zipcode.text = cust['zipcode'] if cust['zipcode'] else ''
                        self.zipcode.hint_text = 'Zipcode'
                        self.zipcode.hint_text_color = DEFAULT_COLOR
                        self.zipcode.disabled = False
                        self.concierge_name.text = cust['concierge_name'] if cust['concierge_name'] else ''
                        self.concierge_name.hint_text = 'Concierge Name'
                        self.concierge_name.hint_text_color = DEFAULT_COLOR
                        self.concierge_name.disabled = False
                        self.concierge_number.text = cust['concierge_number'] if cust['concierge_number'] else ''
                        self.concierge_number.hint_text = 'Concierge Number'
                        self.concierge_number.hint_text_color = DEFAULT_COLOR
                        self.concierge_number.disabled = False
                        self.special_instructions.text = cust['special_instructions'] if cust[
                            'special_instructions'] else ''
                        self.special_instructions.hint_text = 'Special Instructions'
                        self.special_instructions.hint_text_color = DEFAULT_COLOR
                        self.special_instructions.disabled = False
                        self.mark_text.text = ''
                        self.marks_table.clear_widgets()
                        self.update_marks_table()
                    else:
                        self.street.text = ''
                        self.street.hint_text = 'Street Address'
                        self.street.hint_text_color = DEFAULT_COLOR
                        self.street.disabled = True
                        self.suite.text = ''
                        self.suite.hint_text = 'Suite'
                        self.suite.hint_text_color = DEFAULT_COLOR
                        self.suite.disabled = True
                        self.city.text = ''
                        self.city.hint_text = 'City'
                        self.city.hint_text_color = DEFAULT_COLOR
                        self.city.disabled = True
                        self.zipcode.text = ''
                        self.zipcode.hint_text = 'Zipcode'
                        self.zipcode.hint_text_color = DEFAULT_COLOR
                        self.zipcode.disabled = True
                        self.concierge_name.text = ''
                        self.concierge_name.hint_text = 'Concierge Name'
                        self.concierge_name.hint_text_color = DEFAULT_COLOR
                        self.concierge_name.disabled = True
                        self.concierge_number.text = ''
                        self.concierge_number.hint_text = 'Concierge Number'
                        self.concierge_number.hint_text_color = DEFAULT_COLOR
                        self.concierge_number.disabled = True
                        self.special_instructions.text = ''
                        self.special_instructions.hint_text = 'Special Instructions'
                        self.special_instructions.hint_text_color = DEFAULT_COLOR
                        self.special_instructions.disabled = True
                        self.mark_text.text = ''
                        self.marks_table.clear_widgets()

    def set_result_status(self):
        vars.SEARCH_RESULTS_STATUS = True

    def create_mark(self):
        popup = Popup()
        popup.size = 900, 600
        # check for previous marks set
        marks = Custid()
        custids = marks.where({'mark': '"{}"'.format(self.mark_text.text)})
        if custids:
            for custid in custids:
                cust_id = custid['mark']
            popup.title = 'Customer Mark Error'

            popup.content = Builder.load_string(
                KV.popup_alert('{} has already been taken. Please select another.'.format(cust_id)
                               )
            )
            popup.open()
        else:
            # save the mark
            marks.company_id = auth_user.company_id
            marks.customer_id = vars.CUSTOMER_ID
            marks.mark = self.mark_text.text
            marks.status = 1
            if marks.add():
                # update the marks table
                self.update_marks_table()
                marks.close_connection()
                popup.title = 'Success'
                popup.content = Builder.load_string(KV.popup_alert('Successfully added a new mark!'))
                popup.open()

    def set_shirt_finish(self, value):
        self.shirt_finish = str(value)

    def set_shirt_preference(self, value):
        self.shirt_preference = str(value)

    def set_delivery(self):
        self.street.text = ''
        self.street.hint_text = 'Street Address'
        self.street.hint_text_color = DEFAULT_COLOR
        self.street.disabled = False if self.is_delivery.active else True
        self.suite.text = ''
        self.suite.hint_text = 'Suite'
        self.suite.hint_text_color = DEFAULT_COLOR
        self.suite.disabled = False if self.is_delivery.active else True
        self.city.text = ''
        self.city.hint_text = 'City'
        self.city.hint_text_color = DEFAULT_COLOR
        self.city.disabled = False if self.is_delivery.active else True
        self.zipcode.text = ''
        self.zipcode.hint_text = 'Zipcode'
        self.zipcode.hint_text_color = DEFAULT_COLOR
        self.zipcode.disabled = False if self.is_delivery.active else True
        self.concierge_name.text = ''
        self.concierge_name.hint_text = 'Concierge Name'
        self.concierge_name.hint_text_color = DEFAULT_COLOR
        self.concierge_name.disabled = False if self.is_delivery.active else True
        self.concierge_number.text = ''
        self.concierge_number.hint_text = 'Concierge Number'
        self.concierge_number.hint_text_color = DEFAULT_COLOR
        self.concierge_number.disabled = False if self.is_delivery.active else True
        self.special_instructions.text = ''
        self.special_instructions.hint_text = 'Special Instructions'
        self.special_instructions.hint_text_color = DEFAULT_COLOR
        self.special_instructions.disabled = False if self.is_delivery.active else True

    def delete_mark(self, mark=False, *args, **kwargs):
        print(mark)
        popup = Popup()
        popup.size = 800, 600
        popup.title = 'Marks deleted'
        marks = Custid()
        custids = marks.where({'mark': '"{}"'.format(mark)})
        if custids:
            for custid in custids:
                marks.id = custid['id']
                if marks.delete():
                    popup.content = Builder.load_string(KV.popup_alert('Mark has been succesfully deleted.'))

        else:
            popup.content = Builder.load_string(KV.popup_alert('No such mark to delete. Try again!'))
        popup.open()
        self.update_marks_table()

    def update_marks_table(self):
        self.marks_table.clear_widgets()
        # create the headers
        h1 = KV.invoice_tr(0, '#')
        h2 = KV.invoice_tr(0, 'Customer ID')
        h3 = KV.invoice_tr(0, 'Location')
        h4 = KV.invoice_tr(0, 'Mark')
        h5 = KV.invoice_tr(0, 'Status')
        h6 = KV.invoice_tr(0, 'Action')
        self.marks_table.add_widget(Builder.load_string(h1))
        self.marks_table.add_widget(Builder.load_string(h2))
        self.marks_table.add_widget(Builder.load_string(h3))
        self.marks_table.add_widget(Builder.load_string(h4))
        self.marks_table.add_widget(Builder.load_string(h5))
        self.marks_table.add_widget(Builder.load_string(h6))

        marks = Custid()
        custids = marks.where({'customer_id': vars.CUSTOMER_ID})
        even_odd = 0
        if custids:
            for custid in custids:
                status = 'Active' if custid['status'] == 1 else 'Not Active'
                even_odd += 1
                rgba = '0.369,0.369,0.369,1' if even_odd % 2 == 0 else '0.826, 0.826, 0.826, 1'
                background_rgba = '0.369,0.369,0.369,0.1' if even_odd % 2 == 0 else '0.826, 0.826, 0.826, 0.1'
                text_color = 'e5e5e5' if even_odd % 2 == 0 else '5e5e5e'
                tr1 = KV.widget_item(type='Label', data=even_odd, rgba=rgba,
                                     background_rgba=background_rgba, text_color=text_color)
                tr2 = KV.widget_item(type='Label', data=vars.CUSTOMER_ID, rgba=rgba,
                                     background_rgba=background_rgba, text_color=text_color)
                tr3 = KV.widget_item(type='Label', data=custid['company_id'], rgba=rgba,
                                     background_rgba=background_rgba, text_color=text_color)
                tr4 = KV.widget_item(type='Label', data=custid['mark'], rgba=rgba,
                                     background_rgba=background_rgba, text_color=text_color)
                tr5 = KV.widget_item(type='Label', data=status, rgba=rgba,
                                     background_rgba=background_rgba, text_color=text_color)
                tr6 = KV.widget_item(type='Button', data='Delete',
                                     callback='self.parent.parent.parent.parent.parent.delete_mark(mark="{}")'
                                     .format(custid['mark']))
                self.marks_table.add_widget(Builder.load_string(tr1))
                self.marks_table.add_widget(Builder.load_string(tr2))
                self.marks_table.add_widget(Builder.load_string(tr3))
                self.marks_table.add_widget(Builder.load_string(tr4))
                self.marks_table.add_widget(Builder.load_string(tr5))
                self.marks_table.add_widget(Builder.load_string(tr6))

    def validate(self):
        customers = User()
        popup = Popup()
        popup.size_hint = (None, None)
        popup.size = '600sp', '300sp'
        # sync database first
        sync = Sync()

        # check for errors
        errors = 0
        if self.phone.text == '':
            errors += 1
            self.phone.hint_text = "required"
            self.phone.hint_text_color = ERROR_COLOR
        else:
            # check if the phone number already exists
            phone = Job.make_numeric(data=self.phone.text)
            data = {'phone': phone}
            check_duplicate = customers.where(data)
            if len(check_duplicate) > 0:
                for cd in check_duplicate:
                    if cd['user_id'] != vars.CUSTOMER_ID:
                        errors += 1
                        self.phone.hint_text = "duplicate number"
                        self.phone.hint_text_color = ERROR_COLOR
                        # create popup
                        content = KV.popup_alert(
                            'The phone number {} has been taken. Please use a new number'.format(self.phone.text))
                        popup.content = Builder.load_string(content)
                        popup.open()

            elif not Job.check_valid_phone(phone):
                errors += 1
                self.phone.hint_text = "not valid"
                self.phone.hint_text_color = ERROR_COLOR
                # create popup
                content = KV.popup_alert(
                    'The phone number {} is not a valid phone number. Please try again'.format(self.phone.text))
                popup.content = Builder.load_string(content)
                popup.open()
            else:
                self.phone.hint_text = "(XXX) XXX-XXXX"
                self.phone.hint_text_color = DEFAULT_COLOR

        if self.last_name.text == '':
            errors += 1
            self.last_name.hint_text = "required"
            self.last_name.hint_text_color = ERROR_COLOR
        else:
            self.last_name.hint_text = "Last Name"
            self.last_name.hint_text_color = DEFAULT_COLOR

        if self.first_name.text == '':
            errors += 1
            self.first_name.hint_text = "required"
            self.first_name.hint_text_color = ERROR_COLOR
        else:
            self.first_name.hint_text = "Last Name"
            self.first_name.hint_text_color = DEFAULT_COLOR

        if self.email.text and not Job.check_valid_email(self.email.text):
            errors += 1
            self.email.text = ''
            self.email.hint_text = 'Not valid'
            self.email.hint_text_color = ERROR_COLOR

        # Check if delivery is active
        if self.is_delivery.active:
            if self.street.text == '':
                errors += 1
                self.street.hint_text = 'required'
                self.street.hint_text_color = ERROR_COLOR
            else:
                self.street.hint_text = 'Street'
                self.street.hint_text_color = DEFAULT_COLOR
            if self.city.text == '':
                errors += 1
                self.city.hint_text = 'required'
                self.city.hint_text_color = ERROR_COLOR
            else:
                self.city.hint_text = 'City'
                self.city.hint_text_color = DEFAULT_COLOR
            if self.zipcode.text == '':
                errors += 1
                self.zipcode.hint_text = 'required'
                self.zipcode.hint_text_color = ERROR_COLOR
            else:
                self.zipcode.hint_text = 'Zipcode'
                self.zipcode.hint_text_color = DEFAULT_COLOR

        if errors == 0:  # if no errors then save
            where = {'user_id': vars.CUSTOMER_ID}
            data = {}
            data['company_id'] = auth_user.company_id
            data['phone'] = Job.make_numeric(data=self.phone.text)
            data['last_name'] = Job.make_no_whitespace(data=self.last_name.text)
            data['first_name'] = Job.make_no_whitespace(data=self.first_name.text)
            data['email'] = self.email.text if Job.check_valid_email(email=self.email.text) else None
            data['important_memo'] = self.important_memo.text if self.important_memo.text else None
            data['invoice_memo'] = self.invoice_memo.text if self.invoice_memo.text else None
            data['shirt'] = self.shirt_finish
            data['starch'] = self.shirt_preference
            if self.is_delivery.active:
                data['customers'].street = self.street.text
                data['customers.suite'] = Job.make_no_whitespace(data=self.suite.text)
                data['customers.city'] = Job.make_no_whitespace(data=self.city.text)
                data['customers.zipcode'] = Job.make_no_whitespace(data=self.zipcode.text)
                data['customers.concierge_name'] = self.concierge_name.text
                data['customers.concierge_number'] = Job.make_numeric(data=self.concierge_number.text)
                data[
                    'customers.special_instructions'] = self.special_instructions.text if self.special_instructions.text else None

            if customers.put(where=where, data=data):
                # create the customer mark
                marks = Custid()

                updated_mark = marks.create_customer_mark(last_name=self.last_name.text,
                                                          customer_id=str(vars.CUSTOMER_ID),
                                                          starch=customers.get_starch(self.shirt_preference))
                where = {'customer_id': vars.CUSTOMER_ID}
                data = {'mark': updated_mark}
                if marks.put(where=where, data=data):
                    sync.db_sync(auth_user.company_id)  # update the database with the new mark and save it

                self.reset()
                self.customer_select(vars.CUSTOMER_ID)
                # create popup
                content = KV.popup_alert("You have successfully edited this customer.")
                popup.content = Builder.load_string(content)
                popup.open()
                marks.close_connection()

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


class HistoryScreen(Screen):
    invoices_table = ObjectProperty(None)
    items_table = ObjectProperty(None)
    invs_results_label = ObjectProperty(None)

    def get_history(self):

        self.invoices_table.clear_widgets()
        self.items_table.clear_widgets()

        # create the invoice count list
        invoices = Invoice()
        data = {'customer_id': vars.CUSTOMER_ID}
        vars.ROW_CAP = len(invoices.where(data))
        if vars.ROW_CAP < 10 and vars.ROW_CAP <= vars.ROW_SEARCH[1]:
            vars.ROW_SEARCH =0, vars.ROW_CAP
        self.invs_results_label.text = '[color=000000]Showing rows [b]{}[/b] - [b]{}[/b] out of [b]{}[/b][/color]'.format(
            vars.ROW_SEARCH[0],
            vars.ROW_SEARCH[1],
            vars.ROW_CAP
        )
        data = {
            'customer_id': '"%{}%"'.format(vars.CUSTOMER_ID),
            'ORDER_BY': 'id DESC',
            'LIMIT': '{},{}'.format(vars.ROW_SEARCH[0], vars.ROW_SEARCH[1])
        }

        invoices = Invoice()
        invs = invoices.like(data)
        vars.SEARCH_RESULTS = invs
        # get invoice rows and display them to the table

        # create TH
        h1 = KV.invoice_tr(0, 'ID')
        h2 = KV.invoice_tr(0, 'Loc')
        h3 = KV.invoice_tr(0, 'Due')
        h4 = KV.invoice_tr(0, 'Rack')
        h5 = KV.invoice_tr(0, 'Qty')
        h6 = KV.invoice_tr(0, 'Total')
        self.invoices_table.add_widget(Builder.load_string(h1))
        self.invoices_table.add_widget(Builder.load_string(h2))
        self.invoices_table.add_widget(Builder.load_string(h3))
        self.invoices_table.add_widget(Builder.load_string(h4))
        self.invoices_table.add_widget(Builder.load_string(h5))
        self.invoices_table.add_widget(Builder.load_string(h6))

        # create Tbody TR
        if len(vars.SEARCH_RESULTS) > 0:
            for cust in vars.SEARCH_RESULTS:
                self.create_invoice_row(cust)

        vars.SEARCH_RESULTS = []

    pass

    def create_invoice_row(self, row, *args, **kwargs):
        """ Creates invoice table row and displays it to screen """
        check_invoice_id = int(vars.INVOICE_ID) if vars.INVOICE_ID else vars.INVOICE_ID
        invoice_id = row['invoice_id']
        company_id = row['company_id']
        quantity = row['quantity']
        rack = row['rack']
        total = '${:,.2f}'.format(row['total'])
        due = row['due_date']
        status = row['status']
        try:
            dt = datetime.datetime.strptime(due,"%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = datetime.datetime.strptime('1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
        due_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        dow = vars.dow(dt.replace(tzinfo=datetime.timezone.utc).weekday())
        due_date = dt.strftime('%m/%d {}').format(dow)
        try:
            dt = datetime.datetime.strptime(NOW,"%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = datetime.datetime.strptime('1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")

        now_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()

        if status <= 3 and due_strtotime < now_strtotime:  # overdue
            state = 2
        else:
            state = status

        selected = True if invoice_id == check_invoice_id else False

        tr_1 = KV.invoice_tr(state, invoice_id, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        tr_2 = KV.invoice_tr(state, company_id, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        tr_3 = KV.invoice_tr(state, due_date, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        tr_4 = KV.invoice_tr(state, rack, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        tr_5 = KV.invoice_tr(state, quantity, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        tr_6 = KV.invoice_tr(state, total, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        self.invoices_table.add_widget(Builder.load_string(tr_1))
        self.invoices_table.add_widget(Builder.load_string(tr_2))
        self.invoices_table.add_widget(Builder.load_string(tr_3))
        self.invoices_table.add_widget(Builder.load_string(tr_4))
        self.invoices_table.add_widget(Builder.load_string(tr_5))
        self.invoices_table.add_widget(Builder.load_string(tr_6))

        return True

    def set_result_status(self):
        vars.SEARCH_RESULTS_STATUS = True

    def invoice_next(self):
        if vars.ROW_SEARCH[1] + 10 >= vars.ROW_CAP:
            vars.ROW_SEARCH = vars.ROW_CAP - 10, vars.ROW_CAP
        else:
            vars.ROW_SEARCH = vars.ROW_SEARCH[1] + 1, vars.ROW_SEARCH[1] + 10
        data = {
            'customer_id': '"%{}%"'.format(vars.CUSTOMER_ID),
            'ORDER_BY': 'id DESC',
            'LIMIT': '{},{}'.format(vars.ROW_SEARCH[0], vars.ROW_SEARCH[1])
        }

        invoices = Invoice()
        invs = invoices.like(data)
        vars.SEARCH_RESULTS = invs
        self.invs_results_label.text = "[color=000000]Showing rows [b]{}[/b] - [b]{}[/b] out of [b]{}[/b][/color]".format(
            vars.ROW_SEARCH[0], vars.ROW_SEARCH[1], vars.ROW_CAP
        )
        self.get_history()

    def invoice_prev(self):
        if vars.ROW_SEARCH[0] - 10 < 10:
            vars.ROW_SEARCH = 0, 10
        else:
            vars.ROW_SEARCH = vars.ROW_SEARCH[0] - 10, vars.ROW_SEARCH[1] - 10

        self.invs_results_label.text = "[color=000000]Showing rows [b]{}[/b] - [b]{}[/b] out of [b]{}[/b][/color]".format(
            vars.ROW_SEARCH[0], vars.ROW_SEARCH[1], vars.ROW_CAP
        )

        data = {
            'customer_id': '"%{}%"'.format(vars.CUSTOMER_ID),
            'ORDER_BY': 'id DESC',
            'LIMIT': '{},{}'.format(vars.ROW_SEARCH[0], vars.ROW_SEARCH[1])
        }
        invoices = Invoice()
        invs = invoices.like(data)
        vars.SEARCH_RESULTS = invs
        self.invs_results_label.text = "[color=000000]Showing rows [b]{}[/b] - [b]{}[/b] out of [b]{}[/b][/color]".format(
            vars.ROW_SEARCH[0], vars.ROW_SEARCH[1], vars.ROW_CAP
        )
        self.get_history()

    def invoice_selected(self, invoice_id):
        vars.INVOICE_ID = invoice_id
        iitems = InvoiceItem()
        data = {'invoice_id':vars.INVOICE_ID}
        inv_items = iitems.where(data)
        if inv_items:
            self.items_table.clear_widgets()
            # create headers
            # create TH
            h1 = KV.invoice_tr(0, 'Item')
            h2 = KV.invoice_tr(0, 'Qty')
            h3 = KV.invoice_tr(0, 'Total')
            h4 = KV.invoice_tr(0, 'Colors')
            h5 = KV.invoice_tr(0, 'Memos')
            self.items_table.add_widget(Builder.load_string(h1))
            self.items_table.add_widget(Builder.load_string(h2))
            self.items_table.add_widget(Builder.load_string(h3))
            self.items_table.add_widget(Builder.load_string(h4))
            self.items_table.add_widget(Builder.load_string(h5))
            items = {}

            for invoice_item in inv_items:
                item_id = invoice_item['item_id']
                items_search = InventoryItem()
                itm_srch = items_search.where({'item_id':item_id})

                if itm_srch:
                    for itm in itm_srch:
                        item_name = itm['name']
                else:
                    item_name = ''

                items[item_id] = {
                    'name' : item_name,
                    'total' : 0,
                    'quantity': 0,
                    'color': [],
                    'memo': []
                }
            # populate correct item totals
            if items:
                for key, value in items.items():
                    item_id = key
                    data = {
                        'invoice_id':vars.INVOICE_ID,
                        'item_id':item_id
                    }
                    print(data)
                    iinv_items = InvoiceItem().where(data)
                    if iinv_items:
                        for inv_item in iinv_items:
                            items[item_id]['quantity'] += int(inv_item['quantity']) if inv_item['quantity'] else 1
                            items[item_id]['total'] += float(inv_item['pretax']) if inv_item['pretax'] else 0
                            if inv_item['color']:
                                items[item_id]['color'].append(inv_item['color'])
                            if inv_item['memo']:
                                items[item_id]['memo'].append(inv_item['memo'])
            # print out the items into the table
            if items:
                for key,value in items.items():
                    tr1 = KV.invoice_tr(1,value['name'])
                    tr2 = KV.invoice_tr(1,value['quantity'])
                    tr3 = KV.invoice_tr(1,'${:,.2f}'.format(value['total']))
                    tr4 = KV.invoice_tr(1,value['color'], spinner = True, spinner_text = 'color(s)')
                    tr5 = KV.invoice_tr(1,value['memo'], spinner = True, spinner_text = 'memo(s)')
                    self.items_table.add_widget(Builder.load_string(tr1))
                    self.items_table.add_widget(Builder.load_string(tr2))
                    self.items_table.add_widget(Builder.load_string(tr3))
                    self.items_table.add_widget(Builder.load_string(tr4))
                    self.items_table.add_widget(Builder.load_string(tr5))
            print(items)





class Last10Screen(Screen):
    last10_table = ObjectProperty(None)
    last10_footer = ObjectProperty(None)

    def get_last10(self):
        vars.SEARCH_RESULTS_STATUS = True  # make sure search screen isnt reset
        self.last10_table.clear_widgets()
        self.last10_footer.clear_widgets()

        # create TH
        h1 = KV.widget_item(type='Label', data='#', text_color='000000', rgba=(1, 1, 1, 1))
        h2 = KV.widget_item(type='Label', data='ID', text_color='000000', rgba=(1, 1, 1, 1))
        h3 = KV.widget_item(type='Label', data='Mark', text_color='000000', rgba=(1, 1, 1, 1))
        h4 = KV.widget_item(type='Label', data='Last', text_color='000000', rgba=(1, 1, 1, 1))
        h5 = KV.widget_item(type='Label', data='First', text_color='000000', rgba=(1, 1, 1, 1))
        h6 = KV.widget_item(type='Label', data='Phone', text_color='000000', rgba=(1, 1, 1, 1))
        h7 = KV.widget_item(type='Label', data='Action', text_color='000000', rgba=(1, 1, 1, 1))
        self.last10_table.add_widget(Builder.load_string(h1))
        self.last10_table.add_widget(Builder.load_string(h2))
        self.last10_table.add_widget(Builder.load_string(h3))
        self.last10_table.add_widget(Builder.load_string(h4))
        self.last10_table.add_widget(Builder.load_string(h5))
        self.last10_table.add_widget(Builder.load_string(h6))
        self.last10_table.add_widget(Builder.load_string(h7))
        customers = User()
        # create Tbody TR
        even_odd = 0
        if len(vars.LAST10) > 0:
            for customer_id in vars.LAST10:
                even_odd += 1
                rgba = '0.369,0.369,0.369,1' if even_odd % 2 == 0 else '0.826, 0.826, 0.826, 1'
                background_rgba = '0.369,0.369,0.369,0.1' if even_odd % 2 == 0 else '0.826, 0.826, 0.826, 0.1'
                text_color = 'e5e5e5' if even_odd % 2 == 0 else '5e5e5e'
                data = {'user_id': customer_id}
                cust1 = customers.where(data)
                if len(cust1) > 0:
                    for cust in cust1:
                        marks = Custid()
                        mark = ''
                        custids = marks.where({'customer_id': cust['user_id']})
                        if custids:
                            for custid in custids:
                                mark = custid['mark']
                        tr1 = KV.widget_item(type='Label', data=even_odd, rgba=rgba,
                                             background_rgba=background_rgba, text_color=text_color)
                        tr2 = KV.widget_item(type='Label', data=customer_id, rgba=rgba,
                                             background_rgba=background_rgba, text_color=text_color)
                        tr3 = KV.widget_item(type='Label', data=mark, rgba=rgba,
                                             background_rgba=background_rgba, text_color=text_color)
                        tr4 = KV.widget_item(type='Label', data=cust['last_name'], rgba=rgba,
                                             background_rgba=background_rgba, text_color=text_color)
                        tr5 = KV.widget_item(type='Label', data=cust['first_name'], rgba=rgba,
                                             background_rgba=background_rgba, text_color=text_color)
                        tr6 = KV.widget_item(type='Label', data=cust['phone'], rgba=rgba,
                                             background_rgba=background_rgba, text_color=text_color)
                        tr7 = KV.widget_item(type='Button', data='View',
                                             callback='self.parent.parent.parent.customer_select({})'
                                             .format(customer_id))
                        self.last10_table.add_widget(Builder.load_string(tr1))
                        self.last10_table.add_widget(Builder.load_string(tr2))
                        self.last10_table.add_widget(Builder.load_string(tr3))
                        self.last10_table.add_widget(Builder.load_string(tr4))
                        self.last10_table.add_widget(Builder.load_string(tr5))
                        self.last10_table.add_widget(Builder.load_string(tr6))
                        self.last10_table.add_widget(Builder.load_string(tr7))
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
    last_name = ObjectProperty(None)
    first_name = ObjectProperty(None)
    phone = ObjectProperty(None)
    email = ObjectProperty(None)
    important_memo = ObjectProperty(None)
    invoice_memo = ObjectProperty(None)
    shirt_finish = '1'
    shirt_preference = '1'
    default_shirts_finish = ObjectProperty(None)
    is_delivery = ObjectProperty(None)
    street = ObjectProperty(None)
    suite = ObjectProperty(None)
    city = ObjectProperty(None)
    zipcode = ObjectProperty(None)
    concierge_name = ObjectProperty(None)
    concierge_number = ObjectProperty(None)
    special_instructions = ObjectProperty(None)

    def reset(self):
        self.last_name.text = ''
        self.last_name.hint_text = 'Last Name'
        self.last_name.hint_text_color = DEFAULT_COLOR
        self.first_name.text = ''
        self.first_name.hint_text = 'First Name'
        self.first_name.hint_text_color = DEFAULT_COLOR
        self.phone.text = ''
        self.phone.hint_text = '(XXX) XXX-XXXX'
        self.phone.hint_text_color = DEFAULT_COLOR
        self.email.text = ''
        self.email.hint_text = 'example@example.com'
        self.email.hint_text_color = DEFAULT_COLOR
        self.important_memo.text = ''
        self.important_memo.hint_text = 'Important Memo'
        self.important_memo.hint_text_color = DEFAULT_COLOR
        self.invoice_memo.text = ''
        self.invoice_memo.hint_text = 'Invoiced Memo'
        self.invoice_memo.hint_text_color = DEFAULT_COLOR
        self.default_shirts_finish.active = True
        self.default_shirts_preference.active = True
        self.street.text = ''
        self.street.hint_text = 'Street Address'
        self.street.hint_text_color = DEFAULT_COLOR
        self.street.disabled = True
        self.suite.text = ''
        self.suite.hint_text = 'Suite'
        self.suite.hint_text_color = DEFAULT_COLOR
        self.suite.disabled = True
        self.city.text = ''
        self.city.hint_text = 'City'
        self.city.hint_text_color = DEFAULT_COLOR
        self.city.disabled = True
        self.zipcode.text = ''
        self.zipcode.hint_text = 'Zipcode'
        self.zipcode.hint_text_color = DEFAULT_COLOR
        self.zipcode.disabled = True
        self.concierge_name.text = ''
        self.concierge_name.hint_text = 'Concierge Name'
        self.concierge_name.hint_text_color = DEFAULT_COLOR
        self.concierge_name.disabled = True
        self.concierge_number.text = ''
        self.concierge_number.hint_text = 'Concierge Number'
        self.concierge_number.hint_text_color = DEFAULT_COLOR
        self.concierge_number.disabled = True
        self.special_instructions.text = ''
        self.special_instructions.hint_text = 'Special Instructions'
        self.special_instructions.hint_text_color = DEFAULT_COLOR
        self.special_instructions.disabled = True
        self.is_delivery.active = False

    def set_shirt_finish(self, value):
        self.shirt_finish = str(value)

    def set_shirt_preference(self, value):
        self.shirt_preference = str(value)

    def set_delivery(self):
        self.street.text = ''
        self.street.hint_text = 'Street Address'
        self.street.hint_text_color = DEFAULT_COLOR
        self.street.disabled = False if self.is_delivery.active else True
        self.suite.text = ''
        self.suite.hint_text = 'Suite'
        self.suite.hint_text_color = DEFAULT_COLOR
        self.suite.disabled = False if self.is_delivery.active else True
        self.city.text = ''
        self.city.hint_text = 'City'
        self.city.hint_text_color = DEFAULT_COLOR
        self.city.disabled = False if self.is_delivery.active else True
        self.zipcode.text = ''
        self.zipcode.hint_text = 'Zipcode'
        self.zipcode.hint_text_color = DEFAULT_COLOR
        self.zipcode.disabled = False if self.is_delivery.active else True
        self.concierge_name.text = ''
        self.concierge_name.hint_text = 'Concierge Name'
        self.concierge_name.hint_text_color = DEFAULT_COLOR
        self.concierge_name.disabled = False if self.is_delivery.active else True
        self.concierge_number.text = ''
        self.concierge_number.hint_text = 'Concierge Number'
        self.concierge_number.hint_text_color = DEFAULT_COLOR
        self.concierge_number.disabled = False if self.is_delivery.active else True
        self.special_instructions.text = ''
        self.special_instructions.hint_text = 'Special Instructions'
        self.special_instructions.hint_text_color = DEFAULT_COLOR
        self.special_instructions.disabled = False if self.is_delivery.active else True

    def validate(self):
        customers = User()
        popup = Popup()
        popup.size_hint = (None, None)
        popup.size = '600sp', '300sp'
        # sync database first
        sync = Sync()

        # check for errors
        errors = 0
        if self.phone.text == '':
            errors += 1
            self.phone.hint_text = "required"
            self.phone.hint_text_color = ERROR_COLOR
        else:
            # check if the phone number already exists
            phone = Job.make_numeric(data=self.phone.text)
            data = {'phone': phone}
            if len(customers.where(data)) > 0:
                errors += 1
                self.phone.hint_text = "duplicate number"
                self.phone.hint_text_color = ERROR_COLOR
                # create popup
                content = KV.popup_alert(
                    'The phone number {} has been taken. Please use a new number'.format(self.phone.text))
                popup.content = Builder.load_string(content)
                popup.open()

            elif not Job.check_valid_phone(phone):
                errors += 1
                self.phone.hint_text = "not valid"
                self.phone.hint_text_color = ERROR_COLOR
                # create popup
                content = KV.popup_alert(
                    'The phone number {} is not a valid phone number. Please try again'.format(self.phone.text))
                popup.content = Builder.load_string(content)
                popup.open()
            else:
                self.phone.hint_text = "(XXX) XXX-XXXX"
                self.phone.hint_text_color = DEFAULT_COLOR

        if self.last_name.text == '':
            errors += 1
            self.last_name.hint_text = "required"
            self.last_name.hint_text_color = ERROR_COLOR
        else:
            self.last_name.hint_text = "Last Name"
            self.last_name.hint_text_color = DEFAULT_COLOR

        if self.first_name.text == '':
            errors += 1
            self.first_name.hint_text = "required"
            self.first_name.hint_text_color = ERROR_COLOR
        else:
            self.first_name.hint_text = "Last Name"
            self.first_name.hint_text_color = DEFAULT_COLOR

        if self.email.text and not Job.check_valid_email(self.email.text):
            errors += 1
            self.email.text = ''
            self.email.hint_text = 'Not valid'
            self.email.hint_text_color = ERROR_COLOR

        # Check if delivery is active
        if self.is_delivery.active:
            if self.street.text == '':
                errors += 1
                self.street.hint_text = 'required'
                self.street.hint_text_color = ERROR_COLOR
            else:
                self.street.hint_text = 'Street'
                self.street.hint_text_color = DEFAULT_COLOR
            if self.city.text == '':
                errors += 1
                self.city.hint_text = 'required'
                self.city.hint_text_color = ERROR_COLOR
            else:
                self.city.hint_text = 'City'
                self.city.hint_text_color = DEFAULT_COLOR
            if self.zipcode.text == '':
                errors += 1
                self.zipcode.hint_text = 'required'
                self.zipcode.hint_text_color = ERROR_COLOR
            else:
                self.zipcode.hint_text = 'Zipcode'
                self.zipcode.hint_text_color = DEFAULT_COLOR

        if errors == 0:  # if no errors then save
            customers.company_id = auth_user.company_id
            customers.role_id = 3
            customers.phone = Job.make_numeric(data=self.phone.text)
            customers.last_name = Job.make_no_whitespace(data=self.last_name.text)
            customers.first_name = Job.make_no_whitespace(data=self.first_name.text)
            customers.email = self.email.text if Job.check_valid_email(email=self.email.text) else None
            customers.important_memo = self.important_memo.text if self.important_memo.text else None
            customers.invoice_memo = self.invoice_memo.text if self.invoice_memo.text else None
            customers.shirt = self.shirt_finish
            customers.starch = self.shirt_preference
            if self.is_delivery.active:
                customers.street = self.street.text
                customers.suite = Job.make_no_whitespace(data=self.suite.text)
                customers.city = Job.make_no_whitespace(data=self.city.text)
                customers.zipcode = Job.make_no_whitespace(data=self.zipcode.text)
                customers.concierge_name = self.concierge_name.text
                customers.concierge_number = Job.make_numeric(data=self.concierge_number.text)
                customers.special_instructions = self.special_instructions.text if self.special_instructions.text else None

            if customers.add():

                if sync.db_sync(auth_user.company_id):  # send the data to the server and get back the updated user id
                    # send user to search
                    last_row = customers.get_last_inserted_row()
                    customers.id = last_row
                    new_customer = customers.first({'id': customers.id})
                    customers.user_id = new_customer['user_id']
                    # create the customer mark
                    marks = Custid()
                    marks.customer_id = customers.user_id
                    marks.company_id = auth_user.company_id
                    marks.mark = marks.create_customer_mark(last_name=customers.last_name,
                                                            customer_id=str(customers.user_id),
                                                            starch=customers.get_starch(customers.starch))
                    marks.status = 1
                    if marks.add():
                        sync.db_sync(auth_user.company_id)  # update the database with the new mark and save it

                    self.reset()
                    self.customer_select(customers.user_id)
                    # create popup
                    content = KV.popup_alert("You have successfully created a new customer.")
                    popup.content = Builder.load_string(content)
                    popup.open()
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
    customer_mark_l = ObjectProperty(None)
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
        vars.ROW_SEARCH = 0, 10
        vars.ROW_CAP = 0
        vars.SEARCH_TEXT = None
        if vars.SEARCH_RESULTS_STATUS:

            self.edit_invoice_btn.disabled = True
            data = {'user_id': vars.CUSTOMER_ID}
            customers = User()
            results = customers.where(data)
            self.customer_results(results)
        else:
            vars.CUSTOMER_ID = None
            self.search.text = ''
            self.customer_mark_l = ''
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
        popup = Popup()
        search_text = self.search.text
        customers = User()

        data = {'mark': '"%{}%"'.format(self.search.text)}
        marks = Custid()
        custids = marks.like(data)
        where = []
        for custid in custids:
            cust_id = custid['customer_id']
            where.append(cust_id)

        if len(where) == 1:
            data = {'user_id': where[0]}
            cust1 = customers.where(data)
            self.customer_results(cust1)
        elif len(where) > 1:
            cust1 = customers.or_search(where=where)
            self.customer_results(cust1)

        elif Job.is_int(search_text):
            # check to see if length is 7 or greater
            if len(search_text) >= 7:  # This is a phone number
                # First check to see if the number is exact
                data = {'phone': '"%{}%"'.format(self.search.text)}
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
                    popup.title = 'No such invoice'
                    popup.size_hint = None, None
                    popup.size = 800, 600
                    content = KV.popup_alert(msg="Could not find an invoice with this invoice id. Please try again")
                    popup.content = Builder.load_string(content)
                    popup.open()

            else:  # look for a customer id
                data = {'user_id': self.search.text}
                cust1 = customers.where(data)
                self.customer_results(cust1)

        else:  # Lookup by last name || mark

            data = {'last_name': '"%{}%"'.format(self.search.text)}
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

    def create_invoice_headers(self):

        h1 = KV.invoice_tr(0, 'Inv')
        h2 = KV.invoice_tr(0, 'Loc')
        h3 = KV.invoice_tr(0, 'Due')
        h4 = KV.invoice_tr(0, 'Rack')
        h5 = KV.invoice_tr(0, 'Qty')
        h6 = KV.invoice_tr(0, 'Total')
        self.invoice_table.add_widget(Builder.load_string(h1))
        self.invoice_table.add_widget(Builder.load_string(h2))
        self.invoice_table.add_widget(Builder.load_string(h3))
        self.invoice_table.add_widget(Builder.load_string(h4))
        self.invoice_table.add_widget(Builder.load_string(h5))
        self.invoice_table.add_widget(Builder.load_string(h6))
        return True

    def create_invoice_row(self, row, *args, **kwargs):
        """ Creates invoice table row and displays it to screen """
        check_invoice_id = int(vars.INVOICE_ID) if vars.INVOICE_ID else vars.INVOICE_ID
        invoice_id = row['invoice_id']
        company_id = row['company_id']
        quantity = row['quantity']
        rack = row['rack']
        total = row['total']
        due = row['due_date']
        dt = datetime.datetime.strptime(due,
                                        "%Y-%m-%d %H:%M:%S") if due is not None else datetime.datetime.strptime(
            '1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
        due_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        dow = vars.dow(dt.replace(tzinfo=datetime.timezone.utc).weekday())
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

        tr_1 = KV.invoice_tr(state, invoice_id, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        tr_2 = KV.invoice_tr(state, company_id, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        tr_3 = KV.invoice_tr(state, due_date, selected=selected, invoice_id=invoice_id,
        callback = 'self.parent.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        tr_4 = KV.invoice_tr(state, rack, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        tr_5 = KV.invoice_tr(state, quantity, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        tr_6 = KV.invoice_tr(state, total, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        self.invoice_table.add_widget(Builder.load_string(tr_1))
        self.invoice_table.add_widget(Builder.load_string(tr_2))
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
                            dow = vars.dow(dt.replace(tzinfo=datetime.timezone.utc).weekday())
                            try:
                                last_drop = '{} {}'.format(dow, dt.strftime('%m/%d/%y %I:%M%P'))
                            except ValueError:
                                last_drop = '{} {}'.format(dow, dt.strftime('%m/%d/%y'))
                        else:
                            last_drop = ''
                invoices.close_connection()

                # get the custid data
                data = {'customer_id': vars.CUSTOMER_ID}
                custids = Custid()
                custid_string = custids.make_string(custids.where(data))

                # display data
                self.cust_mark_label.text = custid_string
                self.cust_last_name.text = result['last_name'] if result['last_name'] else '';
                self.cust_first_name.text = result['first_name'] if result['first_name'] else '';
                self.cust_phone.text = result['phone'] if result['phone'] else ''
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
        h2 = KV.widget_item(type='Label', data='Mark', text_color='000000', rgba=(1, 1, 1, 1))
        h3 = KV.widget_item(type='Label', data='Last', text_color='000000', rgba=(1, 1, 1, 1))
        h4 = KV.widget_item(type='Label', data='First', text_color='000000', rgba=(1, 1, 1, 1))
        h5 = KV.widget_item(type='Label', data='Phone', text_color='000000', rgba=(1, 1, 1, 1))
        h6 = KV.widget_item(type='Label', data='Action', text_color='000000', rgba=(1, 1, 1, 1))
        self.search_results_table.add_widget(Builder.load_string(h1))
        self.search_results_table.add_widget(Builder.load_string(h2))
        self.search_results_table.add_widget(Builder.load_string(h3))
        self.search_results_table.add_widget(Builder.load_string(h4))
        self.search_results_table.add_widget(Builder.load_string(h5))
        self.search_results_table.add_widget(Builder.load_string(h6))

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
                marks = Custid()
                mark = ''
                custids = marks.where({'customer_id': cust['user_id']})
                if custids:
                    for custid in custids:
                        mark = custid['mark']
                marks.close_connection()
                tr1 = KV.widget_item(type='Label', data=customer_id, rgba=rgba,
                                     background_rgba=background_rgba, text_color=text_color)
                tr2 = KV.widget_item(type='Label', data=mark, rgba=rgba,
                                     background_rgba=background_rgba, text_color=text_color)
                tr3 = KV.widget_item(type='Label', data=last_name, rgba=rgba,
                                     background_rgba=background_rgba, text_color=text_color)
                tr4 = KV.widget_item(type='Label', data=first_name, rgba=rgba,
                                     background_rgba=background_rgba, text_color=text_color)
                tr5 = KV.widget_item(type='Label', data=phone, rgba=rgba,
                                     background_rgba=background_rgba, text_color=text_color)
                tr6 = KV.widget_item(type='Button', data='View',
                                     callback='self.parent.parent.parent.customer_select({})'
                                     .format(customer_id))
                self.search_results_table.add_widget(Builder.load_string(tr1))
                self.search_results_table.add_widget(Builder.load_string(tr2))
                self.search_results_table.add_widget(Builder.load_string(tr3))
                self.search_results_table.add_widget(Builder.load_string(tr4))
                self.search_results_table.add_widget(Builder.load_string(tr5))
                self.search_results_table.add_widget(Builder.load_string(tr6))
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
            vars.ROW_SEARCH = vars.ROW_SEARCH[1] + 1, vars.ROW_SEARCH[1] + 10
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
        if vars.ROW_SEARCH[0] - 10 < 10:
            vars.ROW_SEARCH = 0, 10
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
presentation = Builder.load_file("main.kv")



class MainApp(App):
    def build(self):
        self.title = 'Jays POS'
        return presentation


if __name__ == "__main__":
    MainApp().run()
