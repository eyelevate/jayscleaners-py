import json
import sys
import platform
import time
import datetime
import os
import re
from collections import OrderedDict
#!/usr/local/bin/python3
#!/usr/bin/env python3

os.environ['TZ'] = 'US/Pacific'
if platform.system() == 'Darwin':  # Mac
    sys.path.append('~/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages')
    time.tzset()
    time.tzset()
elif platform.system() == 'Linux':  # Linux
    sys.path.append('/')  # TODO
    time.tzset()
elif platform.system() == 'Windows':  # Windows
    sys.path.append('/')  # TODO
    import usb.backend.libusb0
    import usb.backend.libusb1

# Models
from addresses import Address
from cards import Card
from colors import Colored
from companies import Company
from credits import Credit
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
from profiles import Profile
from reward_transactions import RewardTransaction
from rewards import Reward
from schedules import Schedule
from sync import Sync
from taxes import Tax
from transactions import Transaction
from users import User
from zipcodes import Zipcode

# Helpers
import asyncio
import calendar
from calendar import Calendar
from decimal import *
import urllib
from urllib import error, request, parse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerNotRunningError

getcontext().prec = 3
from kv_generator import KvString
from jobs import Job
from static import Static
from multiprocessing import Process
import threading
import queue
import authorize
from escpos import *
from escpos.escpos import Escpos
from escpos.printer import Usb
from escpos.exceptions import USBNotFoundError
from escpos.exceptions import TextError
import phonenumbers
from threading import Thread
import usb
import usb.core
import usb.util
import webbrowser
import math
from kivy.clock import Clock

from kivy.app import App
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.dropdown import DropDown
from kivy.uix.filechooser import FileChooser
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.listview import ListView
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, partial, StringProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import FadeTransition
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.uix.tabbedpanel import TabbedPanelContent
from kivy.graphics.instructions import Canvas
from kivy.graphics import Rectangle, Color
from kivy.uix.widget import WidgetException
from kivy.clock import Clock

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
SYNC = Sync()
queueLock = threading.Lock()
workQueue = queue.Queue(10)
list_len = []
printer_list = {}
SYNC_POPUP = Popup()
SCHEDULER = BackgroundScheduler()
SCHEDULER.start()

# handles multithreads for database sync
class MultiThread(threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q

    def run(self):
        print("Starting " + self.name)
        process_data(threadName=self.name, q=self.q)
        print("Exiting " + self.name)


def process_data(threadName, q):
    while not vars.EXITFLAG:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            # do method in here
            if data == "Sync":
                SYNC.run_sync()

            queueLock.release()
            print("{} processing {}".format(threadName, data))
        else:
            queueLock.release()
        time.sleep(0.1)


def threads_start():
    vars.THREADID += 1
    thread = MultiThread(vars.THREADID, 'Thread-{}'.format(len(vars.WORKLIST)), workQueue)
    thread.start()
    vars.THREADS.append(thread)

    # Fill the queue
    queueLock.acquire()
    for word in vars.WORKLIST:
        workQueue.put(word)
    queueLock.release()

    # Wait for queue to empty
    while not workQueue.empty():
        pass

    # Notify threads it's time to exit
    vars.EXITFLAG = True

    # Wait for all threads to complete
    thread.join()

    # reset query variables
    vars.THREADS = []
    vars.WORKLIST = []
    vars.EXITFLAG = False
    vars.THREADID = 1

    print("Exiting Main Thread")
    SYNC_POPUP.dismiss()


# SCREEN CLASSES
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
    login_button = ObjectProperty(None)
    item_search_button = ObjectProperty(None)
    main_popup = Popup()
    pb_table = ObjectProperty(None)
    pb_items = ObjectProperty(None)
    table_description = ObjectProperty(None)
    item_description = ObjectProperty(None)

    def update_info(self):
        info = "Last updated {}".format("today")
        return info

    def check_username(self, value):
        print(value)

    def login_show(self):
        self.login_popup = Popup()
        self.login_popup.size_hint = (None, None)
        self.login_popup.size = '400sp', '200sp'
        self.login_popup.title = 'Login Screen'
        layout = BoxLayout(orientation='vertical')
        inner_content_1 = GridLayout(rows=2,
                                     cols=2,
                                     row_force_default=True,
                                     row_default_height='40sp',
                                     size_hint=(1, 0.7))
        inner_content_1.add_widget(Label(text="username",
                                         size_hint_y=None,
                                         font_size='20sp'))
        self.username = Factory.CenterVerticalTextInput(id='username',
                                                        write_tab=False,
                                                        hint_text='Username',
                                                        on_text_validate=self.login)
        inner_content_1.add_widget(self.username)
        self.username.focus = True
        inner_content_1.add_widget(Label(text="password",
                                         size_hint_y=None,
                                         font_size='20sp'))
        self.password = Factory.CenterVerticalTextInput(id='password',
                                                        write_tab=False,
                                                        password=True,
                                                        hint_text='Password',
                                                        on_text_validate=self.login)
        inner_content_1.add_widget(self.password)
        inner_content_2 = BoxLayout(orientation='horizontal',
                                    size_hint=(1, 0.3))
        inner_content_2.add_widget(Button(text="Cancel",
                                          font_size='20sp',
                                          on_release=self.login_popup.dismiss))
        inner_content_2.add_widget(Button(text="Login",
                                          font_size='20sp',
                                          on_release=self.login))
        layout.add_widget(inner_content_1)
        layout.add_widget(inner_content_2)
        self.login_popup.content = layout
        self.login_popup.open()

    def login(self, *args, **kwargs):

        user = User()
        user.username = self.username.text
        user.password = self.password.text  # cipher and salt later
        # SYNC_POPUP.size_hint = (None, None)
        # SYNC_POPUP.size = '600sp', '400sp'
        SYNC_POPUP.title = 'Login Screen'
        db_sync_status = False
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
                self.item_search_button.disabled = False
                for user1 in u1:
                    auth_user.id = user1['id']
                    auth_user.user_id = user1['user_id']
                    auth_user.username = user1['username']
                    auth_user.company_id = user1['company_id']
                    vars.COMPANY_ID = user1['company_id']
                    SYNC.company_id = user1['company_id']
                    print('successfull server auth - company_id = {}'.format(vars.COMPANY_ID))
                print_data = Printer().where({'company_id': auth_user.company_id, 'type': 1})
                if print_data:
                    for pr in print_data:
                        self.print_setup(hex(int(pr['vendor_id'], 16)), hex(int(pr['product_id'], 16)))

                print_data_tag = Printer().where({'company_id': auth_user.company_id, 'type': 2})
                if print_data_tag:
                    for prt in print_data_tag:
                        self.print_setup_tag(hex(int(prt['vendor_id'], 16)), hex(int(prt['product_id'], 16)))

                print_data_label = Printer().where({'company_id': auth_user.company_id, 'type': 3})
                if print_data_label:
                    for prl in print_data_label:
                        self.print_setup_label(hex(int(prl['vendor_id'], 16)), hex(int(prl['product_id'], 16)))
                SYNC_POPUP.title = 'Authentication Success!'
                SYNC_POPUP.content = Builder.load_string(
                    KV.popup_alert(
                        'You are now logged in as {}! Please wait as we sync the database.'.format(user.username)))
                self.login_popup.dismiss()
                db_sync_status = True
            else:  # did not find user in local db, look for user on server

                data = SYNC.server_login(username=user.username, password=user.password)

                if data['status']:
                    self.login_button.text = "Logout"
                    self.login_button.bind(on_release=self.logout)
                    self.update_button.disabled = False
                    self.settings_button.disabled = False
                    self.reports_button.disabled = False
                    self.dropoff_button.disabled = False
                    self.delivery_button.disabled = False
                    self.item_search_button.disabled = False

                    auth_user.username = user.username
                    auth_user.company_id = data['company_id']
                    vars.COMPANY_ID = data['company_id']
                    print('successfull db lookup company_id = {}'.format(vars.COMPANY_ID))
                    print_data = Printer().where({'company_id': auth_user.company_id, 'type': 1})
                    if print_data:
                        for pr in print_data:
                            self.print_setup(hex(int(pr['vendor_id'], 16)), hex(int(pr['product_id'], 16)))
                    print_data_tag = Printer().where({'company_id': auth_user.company_id, 'type': 2})
                    if print_data_tag:
                        for prt in print_data_tag:
                            self.print_setup_tag(hex(int(prt['vendor_id'], 16)), hex(int(prt['product_id'], 16)))
                    print_data_label = Printer().where({'company_id': auth_user.company_id, 'type': 3})
                    if print_data_label:
                        for prl in print_data_label:
                            self.print_setup_label(hex(int(prl['vendor_id'], 16)), hex(int(prl['product_id'], 16)))

                    SYNC.company_id = data['company_id']
                    SYNC_POPUP.title = 'Authentication Success!'
                    content = KV.popup_alert(
                        msg='You are now logged in as {}! Please wait as we sync the database.'.format(user.username))
                    SYNC_POPUP.content = Builder.load_string(content)
                    self.login_popup.dismiss()
                    db_sync_status = True

                else:
                    SYNC_POPUP.title = 'Authentication Failed!'
                    SYNC_POPUP.content = Builder.load_string(
                        KV.popup_alert(msg='Could not find any user with these credentials. '
                                           'Please try again!!'))

            user.close_connection()

            if db_sync_status:
                SYNC_POPUP.title = 'Syncing DB'
                content = Builder.load_string(KV.popup_alert(msg="Obtaining data from the server. Please wait..."))
                SYNC_POPUP.content = content
                SYNC_POPUP.open()
                Clock.schedule_once(self.db_sync, 2)

    def logout(self, *args, **kwargs):
        self.username.text = ''
        self.password.text = ''
        auth_user.username = None
        vars.COMPANY_ID = None
        self.login_button.text = "Login"
        self.login_button.bind(on_release=self.login)
        self.update_button.disabled = True
        self.settings_button.disabled = True
        self.reports_button.disabled = True
        self.dropoff_button.disabled = True
        self.delivery_button.disabled = True
        self.item_search_button.disabled = True

    def db_sync(self, *args, **kwargs):

        # quick sync

        t1 = Thread(target=SYNC.db_sync, args=[vars.COMPANY_ID])
        t1.start()
        t1.join()
        SYNC_POPUP.dismiss()
        # print('initializing auto-sync every 20 seconds')
        # SCHEDULER.start()

        # sync.get_chunk(table='invoice_items',start=140001,end=150000)

        # self.update_label.text = 'Server updated at {}'.format()

    def sync_rackable_invoices(self, *args, **kwargs):
        t1 = Thread(target=self.do_rackable_invoices)
        t1.start()

    def do_rackable_invoices(self):
        url = 'http://www.jayscleaners.com/admins/api/sync-rackable-invoices'

        # attempt to connect to server
        data = parse.urlencode({'company_id': 'None'}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"

        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            self.set_pb_max(len(data_1))
            if len(data_1) > 0:
                idx = 0
                for invoices in data_1:
                    idx += 1
                    self.set_pb_value(idx)
                    self.set_pb_desc("Updating Invoice Table {} of {}".format(str(idx),str(len(data_1))))
                    invoice = Invoice()
                    invoice.invoice_id = invoices['id']
                    invoice.company_id = invoices['company_id']
                    invoice.customer_id = invoices['customer_id']
                    invoice.quantity = invoices['quantity']
                    invoice.pretax = invoices['pretax']
                    invoice.tax = invoices['tax']
                    invoice.reward_id = invoices['reward_id']
                    invoice.discount_id = invoices['discount_id']
                    invoice.total = invoices['total']
                    invoice.rack = invoices['rack']
                    invoice.rack_date = invoices['rack_date']
                    invoice.due_date = invoices['due_date']
                    invoice.memo = invoices['memo']
                    invoice.transaction_id = invoices['transaction_id']
                    invoice.schedule_id = invoices['schedule_id']
                    invoice.status = invoices['status']
                    invoice.deleted_at = invoices['deleted_at']
                    invoice.created_at = invoices['created_at']
                    invoice.updated_at = invoices['updated_at']

                    count_invoice = invoice.where({'invoice_id': invoice.invoice_id})
                    if len(count_invoice) > 0 or invoice.deleted_at:
                        for data in count_invoice:
                            invoice.id = data['id']
                            if invoice.deleted_at:
                                invoice.delete()
                    else:
                        invoice.add_special()
                    invoice.close_connection()

                    # extra loop through invoice items to delete or check for data
                    if 'invoice_items' in invoices:

                        iitems = invoices['invoice_items']
                        self.set_pb_items_max(len(iitems))
                        if len(iitems) > 0:
                            itdx = 0
                            for iitem in iitems:
                                itdx += 1
                                self.set_pb_items_value(itdx)
                                self.set_pb_items_desc("Updating Invoice Items Table {} of {}".format(str(itdx),str(len(iitems))))
                                invoice_item = InvoiceItem()
                                invoice_item.invoice_items_id = iitem['id']
                                invoice_item.invoice_id = iitem['invoice_id']
                                invoice_item.item_id = iitem['item_id']
                                invoice_item.inventory_id = iitem['inventory_id']
                                invoice_item.company_id = iitem['company_id']
                                invoice_item.customer_id = iitem['customer_id']
                                invoice_item.quantity = iitem['quantity']
                                invoice_item.color = iitem['color']
                                invoice_item.memo = iitem['memo']
                                invoice_item.pretax = iitem['pretax']
                                invoice_item.tax = iitem['tax']
                                invoice_item.total = iitem['total']
                                invoice_item.status = iitem['status']
                                invoice_item.deleted_at = iitem['deleted_at']
                                invoice_item.created_at = iitem['created_at']
                                invoice_item.updated_at = iitem['updated_at']
                                count_invoice_item = invoice_item.where(
                                    {'invoice_items_id': invoice_item.invoice_items_id})
                                if len(count_invoice_item) > 0 or invoice_item.deleted_at:
                                    for data in count_invoice_item:
                                        invoice_item.id = data['id']
                                        if invoice_item.deleted_at:
                                            invoice_item.delete()
                                else:
                                    invoice_item.add_special()
                            invoice_item.close_connection()

        except urllib.error.URLError as e:
            print('Error sending post data: {}'.format(e.reason))


    def print_setup_label(self, vendor_id, product_id):
        vendor_int = int(vendor_id, 16)
        product_int = int(product_id, 16)
        # find our device
        dev = usb.core.find(idVendor=vendor_int, idProduct=product_int)

        # was it found?
        if dev is not None:
            print('device found')

            # set the active configuration. With no arguments, the first
            # configuration will be the active one
            dev.set_configuration()

            # get an endpoint instance
            cfg = dev.get_active_configuration()
            intf = cfg[(0, 0)]

            vars.ZEBRA = usb.util.find_descriptor(
                intf,
                # match the first OUT endpoint
                custom_match= \
                    lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_OUT)

        else:
            vars.ZEBRA = False
            popup = Popup()
            popup.title = 'Printer Error'
            content = KV.popup_alert('Tag printer not found.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()

    def sync_db_popup(self):

        self.main_popup.title = 'Auto Sync'
        layout = BoxLayout(orientation="vertical")
        inner_layout_1 = Factory.ScrollGrid()
        inner_layout_1.ids.main_table.cols = 1
        table_label = Factory.BottomLeftFormLabel(text="Overall Progress")
        items_label = Factory.BottomLeftFormLabel(text="Table Progress")
        self.pb_table = ProgressBar(max=21)
        self.pb_items = ProgressBar()
        self.table_description = Factory.TopLeftFormLabel()
        self.item_description = Factory.TopLeftFormLabel()

        inner_layout_1.ids.main_table.add_widget(table_label)
        inner_layout_1.ids.main_table.add_widget(self.pb_table)
        inner_layout_1.ids.main_table.add_widget(self.table_description)
        inner_layout_1.ids.main_table.add_widget(items_label)
        inner_layout_1.ids.main_table.add_widget(self.pb_items)
        inner_layout_1.ids.main_table.add_widget(self.item_description)
        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="Done",
                               on_release=self.main_popup.dismiss)
        sync_2_button = Button(text='Sync 2 days',
                               on_release=self.sync_rackable_invoices)
        run_sync_button = Button(text="Run",
                                 on_release=self.sync_db)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(run_sync_button)
        inner_layout_2.add_widget(sync_2_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.main_popup.content = layout
        self.main_popup.open()

    def set_pb_desc(self, description, *args, **kwargs):
        self.table_description.text = description

    def set_pb_value(self, value, *args, **kwargs):
        self.pb_table.value = int(value)

    def set_pb_max(self, value, *args, **kwargs):
        self.pb_table.max=int(value)

    def set_pb_items_desc(self, description, *args, **kwargs):
        self.item_description.text = description

    def set_pb_items_value(self, value, *args, **kwargs):
        self.pb_items.value = int(value)

    def set_pb_items_max(self, value, *args, **kwargs):
        self.pb_items.max = int(value)

    def sync_db(self, *args, **kwargs):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()

        t1 = Thread(target=self.auto_update, args=())
        t1.start()
        # t1.join()
        # print('all done')

    
    def auto_update(self,*args, **kwargs):
        tables = [
            'addresses',
            'cards',
            'colors',
            'companies',
            'credits',
            'custids',
            'deliveries',
            'discounts',
            'inventories',
            'inventory_items',
            'invoices',
            'invoice_items',
            'memos',
            'profiles',
            'reward_transactions',
            'rewards',
            'schedules',
            'taxes',
            'transactions',
            'users',
            'zipcodes'
        ]
        max = 21
        self.set_pb_max(21)
        idx = 0
        filename = 'db/jayscleaners.db'
        try:
            os.remove(filename)
            SYNC.migrate()
        except OSError:
            pass
        for table in tables:
            idx += 1

            self.set_pb_desc('Syncing {} Table {} of {}'.format(table, str(idx), str(max)))
            self.set_pb_value(idx)
            check_finish = self.process_sync(table, idx)
            if check_finish:
                continue
        
        

        print('Process Complete. Local database has been completely synced.')
        Company().server_at_update()

    def process_sync(self, table, idx, *args, **kwargs):

        url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        print('Syncing table - {} ({} / 21)'.format(table, idx))
        try:
            r = request.urlopen(url)
            count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if (count_data['status'] is 200):
                start = int(count_data['data']['first_row'])
                end = int(count_data['data']['last_row'])

                if int(end - start) > 0:  # reset table db and start pulling in new data from server

                    if end > 5000:
                        for num in range(start, end, 5000):
                            idx_start = num
                            idx_end = num + 5000
                            print('Obtaining rows {} through {}'.format(idx_start, idx_end))
                            self.get_chunk(table,idx_start,idx_end, end)

                    else:
                        print('Obtaining rows {} through {}'.format(start, end))
                        self.get_chunk(table,0,5000,end)
                        return True

        except urllib.error.URLError as e:
            print(e)

        return False

    def get_chunk(self, table=False, start=False, end=False, last=False, *args, **kwargs):
        company_id = 1
        api_token = '2064535930-1'

        url = 'http://www.jayscleaners.com/admins/api/chunk/{}/{}/{}/{}/{}'.format(
            company_id,
            api_token,
            table,
            start,
            end
        )
        # print(url)
        try:
            r = request.urlopen(url)
            data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))

            if data['status'] is True:
                # Save the local data
                self.sync_from_server(data, start, end, last)


        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on

    def sync_from_server(self,data, start, end, last,*args, **kwargs):
        # print('sync from server')
        # start upload text
        # print(data)
        # print(data['rows_to_create'])
        if int(data['rows_to_create']) > 0:
            updates = data['updates']
            if 'addresses' in updates:

                table_len = len(updates['addresses'])
                self.set_pb_items_max(last)
                idx = start
                for addresses in updates['addresses']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,str(last)))
                    address = Address()
                    address.address_id = addresses['id']
                    address.user_id = addresses['user_id']
                    address.name = addresses['name']
                    address.street = addresses['street']
                    address.suite = addresses['suite']
                    address.city = addresses['city']
                    address.state = addresses['state']
                    address.zipcode = addresses['zipcode']
                    address.primary_address = addresses['primary_address']
                    address.concierge_name = addresses['concierge_name']
                    address.concierge_number = addresses['concierge_number']
                    address.status = addresses['status']
                    address.deleted_at = addresses['deleted_at']
                    address.created_at = addresses['created_at']
                    address.updated_at = addresses['updated_at']
                    # check to see if color_id already exists and update

                    count_address = address.where({'address_id': address.address_id})
                    if len(count_address) > 0 or address.deleted_at:
                        for data in count_address:
                            address.id = data['id']
                            if address.deleted_at:
                                address.delete()
                            else:
                                address.update_special()
                    else:
                        address.add_special()
                address.close_connection()

            if 'cards' in updates:
                table_len = len(updates['cards'])
                self.set_pb_items_max(last)
                idx = start
                for cards in updates['cards']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    card = Card()
                    card.card_id = cards['id']
                    card.company_id = cards['company_id']
                    card.user_id = cards['user_id']
                    card.profile_id = cards['profile_id']
                    card.payment_id = cards['payment_id']
                    card.root_payment_id = cards['root_payment_id']
                    card.street = cards['street']
                    card.suite = cards['suite']
                    card.city = cards['city']
                    card.state = cards['state']
                    card.zipcode = cards['zipcode']
                    card.exp_month = cards['exp_month']
                    card.exp_year = cards['exp_year']
                    card.status = cards['status']
                    card.deleted_at = cards['deleted_at']
                    card.created_at = cards['created_at']
                    card.updated_at = cards['updated_at']
                    # check to see if color_id already exists and update

                    count_card = card.where({'card_id': card.card_id})
                    if len(count_card) > 0 or card.deleted_at:
                        for data in count_card:
                            card.id = data['id']
                            if card.deleted_at:
                                card.delete()
                            else:
                                card.update_special()
                    else:
                        card.add_special()
                card.close_connection()

            if 'colors' in updates:
                table_len = len(updates['colors'])
                self.set_pb_items_max(last)
                idx = start
                for colors in updates['colors']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    color = Colored()
                    color.color_id = colors['id']
                    color.company_id = colors['company_id']
                    color.color = colors['color']
                    color.name = colors['name']
                    color.ordered = colors['ordered']
                    color.status = colors['status']
                    color.deleted_at = colors['deleted_at']
                    color.created_at = colors['created_at']
                    color.updated_at = colors['updated_at']
                    # check to see if color_id already exists and update

                    count_color = color.where({'color_id': color.color_id})
                    if len(count_color) > 0 or color.deleted_at:
                        for data in count_color:
                            color.id = data['id']
                            if color.deleted_at:
                                color.delete()
                            else:
                                color.update_special()
                    else:
                        color.add_special()
                color.close_connection()

            if 'companies' in updates:
                table_len = len(updates['companies'])
                self.set_pb_items_max(last)
                idx = start
                for companies in updates['companies']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    company = Company()
                    company.company_id = companies['id']
                    company.name = companies['name']
                    company.street = companies['street']
                    company.city = companies['city']
                    company.state = companies['state']
                    company.zip = companies['zip']
                    company.email = companies['email']
                    company.phone = companies['phone']
                    company.store_hours = companies['store_hours']
                    company.turn_around = companies['turn_around']
                    company.api_token = companies['api_token']
                    company.payment_gateway_id = companies['payment_gateway_id']
                    company.payment_api_login = companies['payment_api_login']
                    company.deleted_at = companies['deleted_at']
                    company.created_at = companies['created_at']
                    company.updated_at = companies['updated_at']
                    count_company = company.where({'company_id': company.company_id})
                    if len(count_company) > 0 or company.deleted_at:
                        for data in count_company:
                            company.id = data['id']
                            if company.deleted_at:
                                company.delete()
                            else:
                                company.update_special()
                    else:
                        company.add_special()
                company.close_connection()

            if 'credits' in updates:
                table_len = len(updates['credits'])
                self.set_pb_items_max(last)
                idx = start
                for credits in updates['credits']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    credit = Credit()
                    credit.credit_id = credits['id']
                    credit.employee_id = credits['employee_id']
                    credit.customer_id = credits['customer_id']
                    credit.amount = credits['amount']
                    credit.reason = credits['reason']
                    credit.status = credits['status']
                    credit.deleted_at = credits['deleted_at']
                    credit.created_at = credits['created_at']
                    credit.updated_at = credits['updated_at']
                    # check to see already exists and update

                    count_credit = credit.where({'credit_id': credit.credit_id})
                    if len(count_credit) > 0 or credit.deleted_at:
                        for data in count_credit:
                            credit.id = data['id']
                            if credit.deleted_at:
                                credit.delete()
                            else:
                                credit.update_special()
                    else:
                        credit.add_special()
                credit.close_connection()
            if 'custids' in updates:
                table_len = len(updates['custids'])
                self.set_pb_items_max(last)
                idx = start
                for custids in updates['custids']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    custid = Custid()
                    custid.cust_id = custids['id']
                    custid.customer_id = custids['customer_id']
                    custid.company_id = custids['company_id']
                    custid.mark = custids['mark']
                    custid.status = custids['status']
                    custid.deleted_at = custids['deleted_at']
                    custid.created_at = custids['created_at']
                    custid.updated_at = custids['updated_at']
                    count_custid = custid.where({'cust_id': custids['id']})
                    if len(count_custid) > 0 or custid.deleted_at:
                        for data in count_custid:
                            custid.id = data['id']
                            if custid.deleted_at:
                                custid.delete()
                            else:
                                custid.update_special()
                    else:
                        custid.add_special()
                custid.close_connection()

            if 'deliveries' in updates:
                table_len = len(updates['deliveries'])
                self.set_pb_items_max(last)
                idx = start
                for deliveries in updates['deliveries']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    delivery = Delivery()
                    delivery.delivery_id = deliveries['id']
                    delivery.company_id = deliveries['company_id']
                    delivery.route_name = deliveries['route_name']
                    delivery.day = deliveries['day']
                    delivery.delivery_limit = deliveries['limit']
                    delivery.start_time = deliveries['start_time']
                    delivery.end_time = deliveries['end_time']
                    delivery.zipcode = deliveries['zipcode']
                    delivery.blackout = deliveries['blackout']
                    delivery.status = deliveries['status']
                    delivery.deleted_at = deliveries['deleted_at']
                    delivery.created_at = deliveries['created_at']
                    delivery.updated_at = deliveries['updated_at']
                    count_delivery = delivery.where({'delivery_id': delivery.delivery_id})
                    if len(count_delivery) > 0 or delivery.deleted_at:
                        for data in count_delivery:
                            delivery.id = data['id']
                            if delivery.deleted_at:
                                delivery.delete()
                            else:
                                delivery.update_special()
                    else:
                        delivery.add_special()
                delivery.close_connection()

            if 'discounts' in updates:
                table_len = len(updates['discounts'])
                self.set_pb_items_max(last)
                idx = start
                for discounts in updates['discounts']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    discount = Discount()
                    discount.discount_id = discounts['id']
                    discount.company_id = discounts['company_id']
                    discount.inventory_id = discounts['inventory_id']
                    discount.inventory_item_id = discounts['inventory_item_id']
                    discount.name = discounts['name']
                    discount.type = discounts['type']
                    discount.discount = discounts['discount']
                    discount.rate = discounts['rate']
                    discount.end_time = discounts['end_time']
                    discount.start_date = discounts['start_date']
                    discount.end_date = discounts['end_date']
                    discount.status = discounts['status']
                    discount.deleted_at = discounts['deleted_at']
                    discount.created_at = discounts['created_at']
                    discount.updated_at = discounts['updated_at']
                    count_discount = discount.where({'discount_id': discount.discount_id})
                    if len(count_discount) > 0 or discount.deleted_at:
                        for data in count_discount:
                            discount.id = data['id']
                            if discount.deleted_at:
                                discount.delete()
                            else:
                                discount.update_special()
                    else:
                        discount.add_special()
                discount.close_connection()

            if 'inventories' in updates:
                table_len = len(updates['inventories'])
                self.set_pb_items_max(last)
                idx = start
                for inventories in updates['inventories']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    inventory = Inventory()
                    inventory.inventory_id = inventories['id']
                    inventory.company_id = inventories['company_id']
                    inventory.name = inventories['name']
                    inventory.description = inventories['description']
                    inventory.ordered = inventories['ordered']
                    inventory.laundry = inventories['laundry']
                    inventory.status = inventories['status']
                    inventory.deleted_at = inventories['deleted_at']
                    inventory.create_at = inventories['created_at']
                    inventory.updated_at = inventories['updated_at']
                    count_inventory = inventory.where({'inventory_id': inventory.inventory_id})
                    if len(count_inventory) > 0 or inventory.deleted_at:
                        for data in count_inventory:
                            inventory.id = data['id']
                            if inventory.deleted_at:
                                inventory.delete()
                            else:
                                inventory.update_special()
                    else:
                        inventory.add_special()
                inventory.close_connection()

            if 'inventory_items' in updates:
                table_len = len(updates['inventory_items'])
                self.set_pb_items_max(last)
                idx = start
                for inventory_items in updates['inventory_items']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    inventory_item = InventoryItem()
                    inventory_item.item_id = inventory_items['id']
                    inventory_item.inventory_id = inventory_items['inventory_id']
                    inventory_item.company_id = inventory_items['company_id']
                    inventory_item.name = inventory_items['name']
                    inventory_item.description = inventory_items['description']
                    inventory_item.tags = inventory_items['tags']
                    inventory_item.quantity = inventory_items['quantity']
                    inventory_item.ordered = inventory_items['ordered']
                    inventory_item.price = inventory_items['price']
                    inventory_item.image = inventory_items['image']
                    inventory_item.status = inventory_items['status']
                    inventory_item.deleted_at = inventory_items['deleted_at']
                    inventory_item.created_at = inventory_items['created_at']
                    inventory_item.updated_at = inventory_items['updated_at']
                    count_inventory_item = inventory_item.where({'item_id': inventory_item.item_id})
                    if len(count_inventory_item) > 0 or inventory_item.deleted_at:
                        for data in count_inventory_item:
                            inventory_item.id = data['id']
                            if inventory_item.deleted_at:
                                inventory_item.delete()
                            else:
                                inventory_item.update_special()
                    else:
                        inventory_item.add_special()
                inventory_item.close_connection()

            if 'invoice_items' in updates:
                table_len = len(updates['invoice_items'])
                self.set_pb_items_max(last)
                idx = start
                for invoice_items in updates['invoice_items']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    invoice_item = InvoiceItem()
                    invoice_item.invoice_items_id = invoice_items['id']
                    invoice_item.invoice_id = invoice_items['invoice_id']
                    invoice_item.item_id = invoice_items['item_id']
                    invoice_item.inventory_id = invoice_items['inventory_id']
                    invoice_item.company_id = invoice_items['company_id']
                    invoice_item.customer_id = invoice_items['customer_id']
                    invoice_item.quantity = invoice_items['quantity']
                    invoice_item.color = invoice_items['color']
                    invoice_item.memo = invoice_items['memo']
                    invoice_item.pretax = invoice_items['pretax']
                    invoice_item.tax = invoice_items['tax']
                    invoice_item.total = invoice_items['total']
                    invoice_item.status = invoice_items['status']
                    invoice_item.deleted_at = invoice_items['deleted_at']
                    invoice_item.created_at = invoice_items['created_at']
                    invoice_item.updated_at = invoice_items['updated_at']
                    count_invoice_item = invoice_item.where({'invoice_items_id': invoice_item.invoice_items_id})
                    if len(count_invoice_item) > 0 or invoice_item.deleted_at:
                        for data in count_invoice_item:
                            invoice_item.id = data['id']
                            if invoice_item.deleted_at:
                                invoice_item.delete()
                            else:
                                invoice_item.update_special()
                    else:
                        invoice_item.add_special()

            if 'invoices' in updates:
                table_len = len(updates['invoices'])
                self.set_pb_items_max(last)
                idx = start
                for invoices in updates['invoices']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    invoice = Invoice()
                    invoice.invoice_id = invoices['id']
                    invoice.company_id = invoices['company_id']
                    invoice.customer_id = invoices['customer_id']
                    invoice.quantity = invoices['quantity']
                    invoice.pretax = invoices['pretax']
                    invoice.tax = invoices['tax']
                    invoice.reward_id = invoices['reward_id']
                    invoice.discount_id = invoices['discount_id']
                    invoice.total = invoices['total']
                    invoice.rack = invoices['rack']
                    invoice.rack_date = invoices['rack_date']
                    invoice.due_date = invoices['due_date']
                    invoice.memo = invoices['memo']
                    invoice.transaction_id = invoices['transaction_id']
                    invoice.schedule_id = invoices['schedule_id']
                    invoice.status = invoices['status']
                    invoice.deleted_at = invoices['deleted_at']
                    invoice.created_at = invoices['created_at']
                    invoice.updated_at = invoices['updated_at']

                    count_invoice = invoice.where({'invoice_id': invoice.invoice_id})
                    if len(count_invoice) > 0 or invoice.deleted_at:
                        for data in count_invoice:
                            invoice.id = data['id']
                            if invoice.deleted_at:
                                invoice.delete()
                            else:
                                invoice.update_special()
                    else:
                        invoice.add_special()

            if 'memos' in updates:
                table_len = len(updates['memos'])
                self.set_pb_items_max(last)
                idx = start
                for memos in updates['memos']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    memo = Memo()
                    memo.memo_id = memos['id']
                    memo.company_id = memos['company_id']
                    memo.memo = memos['memo']
                    memo.ordered = memos['ordered']
                    memo.status = memos['status']
                    memo.deleted_at = memos['deleted_at']
                    memo.created_at = memos['created_at']
                    memo.updated_at = memos['updated_at']
                    count_memo = memo.where({'memo_id': memo.memo_id})
                    if len(count_memo) > 0 or memo.deleted_at:
                        for data in count_memo:
                            memo.id = data['id']
                            if memo.deleted_at:
                                memo.delete()
                            else:
                                memo.update_special()
                    else:
                        memo.add_special()
                memo.close_connection()

            if 'profiles' in updates:
                table_len = len(updates['profiles'])
                self.set_pb_items_max(last)
                idx = start
                for profiles in updates['profiles']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    profile = Profile()
                    profile.p_id = profiles['id']
                    profile.company_id = profiles['company_id']
                    profile.user_id = profiles['user_id']
                    profile.profile_id = profiles['profile_id']
                    profile.status = profiles['status']
                    profile.deleted_at = profiles['deleted_at']
                    profile.created_at = profiles['created_at']
                    profile.updated_at = profiles['updated_at']
                    count_profile = profile.where({'p_id': profile.p_id})
                    if len(count_profile) > 0 or profile.deleted_at:
                        for data in count_profile:
                            profile.id = data['id']
                            if profile.deleted_at:
                                profile.delete()
                            else:
                                profile.update_special()
                    else:
                        profile.add_special()
                profile.close_connection()

            if 'reward_transactions' in updates:
                table_len = len(updates['reward_transactions'])
                self.set_pb_items_max(last)
                idx = start
                for reward_transactions in updates['reward_transactions']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    reward_transaction = RewardTransaction()
                    reward_transaction.reward_id = reward_transactions['reward_id']
                    reward_transaction.transaction_id = reward_transactions['transaction_id']
                    reward_transaction.customer_id = reward_transactions['customer_id']
                    reward_transaction.employee_id = reward_transactions['employee_id']
                    reward_transaction.company_id = reward_transactions['company_id']
                    reward_transaction.type = reward_transactions['type']
                    reward_transaction.points = reward_transactions['points']
                    reward_transaction.credited = reward_transactions['credited']
                    reward_transaction.reduced = reward_transactions['reduced']
                    reward_transaction.running_total = reward_transactions['running_total']
                    reward_transaction.reason = reward_transactions['reason']
                    reward_transaction.name = reward_transactions['name']
                    reward_transaction.status = reward_transactions['status']
                    reward_transaction.deleted_at = reward_transactions['deleted_at']
                    reward_transaction.created_at = reward_transactions['created_at']
                    reward_transaction.updated_at = reward_transactions['updated_at']
                    count_reward_transaction = reward_transaction.where({'reward_id': reward_transaction.reward_id})
                    if len(count_reward_transaction) > 0 or reward_transaction.deleted_at:
                        for data in count_reward_transaction:
                            reward_transaction.id = data['id']
                            if reward_transaction.deleted_at:
                                reward_transaction.delete()
                            else:
                                reward_transaction.update_special()
                    else:
                        reward_transaction.add_special()
                reward_transaction.close_connection()

            if 'rewards' in updates:
                table_len = len(updates['rewards'])
                self.set_pb_items_max(last)
                idx = start
                for rewards in updates['rewards']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    reward = Reward()
                    reward.reward_id = rewards['id']
                    reward.company_id = rewards['company_id']
                    reward.name = rewards['name']
                    reward.points = rewards['points']
                    reward.discount = rewards['discount']
                    reward.status = rewards['status']
                    reward.deleted_at = rewards['deleted_at']
                    reward.created_at = rewards['created_at']
                    reward.updated_at = rewards['updated_at']
                    count_reward = reward.where({'reward_id': reward.reward_id})
                    if len(count_reward) > 0 or reward.deleted_at:
                        for data in count_reward:
                            reward.id = data['id']
                            if reward.deleted_at:
                                reward.delete()
                            else:
                                reward.update_special()
                    else:
                        reward.add_special()
                reward.close_connection()

            if 'schedules' in updates:
                table_len = len(updates['schedules'])
                self.set_pb_items_max(last)
                idx = start
                for schedules in updates['schedules']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    schedule = Schedule()
                    schedule.schedule_id = schedules['id']
                    schedule.company_id = schedules['company_id']
                    schedule.customer_id = schedules['customer_id']
                    schedule.card_id = schedules['card_id']
                    schedule.pickup_delivery_id = schedules['pickup_delivery_id']
                    schedule.pickup_address = schedules['pickup_address']
                    schedule.pickup_date = schedules['pickup_date']
                    schedule.dropoff_delivery_id = schedules['dropoff_delivery_id']
                    schedule.dropoff_address = schedules['dropoff_address']
                    schedule.dropoff_date = schedules['dropoff_date']
                    schedule.special_instructions = schedules['special_instructions']
                    schedule.type = schedules['type']
                    schedule.token = schedules['token']
                    schedule.status = schedules['status']
                    schedule.deleted_at = schedules['deleted_at']
                    schedule.created_at = schedules['created_at']
                    schedule.updated_at = schedules['updated_at']
                    count_schedule = schedule.where({'schedule_id': schedule.schedule_id})
                    if len(count_schedule) > 0 or schedule.deleted_at:
                        for data in count_schedule:
                            schedule.id = data['id']
                            if schedule.deleted_at:
                                schedule.delete()
                            else:
                                schedule.update_special()
                    else:
                        schedule.add_special()
                schedule.close_connection()

            if 'taxes' in updates:
                table_len = len(updates['taxes'])
                self.set_pb_items_max(last)
                idx = start
                for taxes in updates['taxes']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    tax = Tax()
                    tax.tax_id = taxes['id']
                    tax.company_id = taxes['company_id']
                    tax.rate = taxes['rate']
                    tax.status = taxes['status']
                    tax.deleted_at = taxes['deleted_at']
                    tax.created_at = taxes['created_at']
                    tax.updated_at = taxes['updated_at']
                    count_tax = tax.where({'tax_id': tax.tax_id})
                    if len(count_tax) > 0 or tax.deleted_at:
                        for data in count_tax:
                            tax.id = data['id']
                            if tax.deleted_at:
                                tax.delete()
                            else:
                                tax.update_special()
                    else:
                        tax.add_special()
                tax.close_connection()

            if 'transactions' in updates:
                table_len = len(updates['transactions'])
                self.set_pb_items_max(last)
                idx = start
                for transactions in updates['transactions']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    transaction = Transaction()
                    transaction.trans_id = transactions['id']
                    transaction.company_id = transactions['company_id']
                    transaction.customer_id = transactions['customer_id']
                    transaction.schedule_id = transactions['schedule_id']
                    transaction.pretax = transactions['pretax']
                    transaction.tax = transactions['tax']
                    transaction.aftertax = transactions['aftertax']
                    transaction.credit = transactions['credit']
                    transaction.discount = transactions['discount']
                    transaction.total = transactions['total']
                    transaction.invoices = transactions['invoices'] if transactions['invoices'] else None
                    transaction.account_paid = transactions['account_paid']
                    transaction.account_paid_on = transactions['account_paid_on']
                    transaction.type = transactions['type']
                    transaction.last_four = transactions['last_four']
                    transaction.tendered = transactions['tendered']
                    transaction.transaction_id = transactions['transaction_id']
                    transaction.status = transactions['status']
                    transaction.deleted_at = transactions['deleted_at']
                    transaction.created_at = transactions['created_at']
                    transaction.updated_at = transactions['updated_at']
                    count_transaction = transaction.where({'trans_id': transaction.trans_id})
                    if len(count_transaction) > 0 or transaction.deleted_at:
                        for data in count_transaction:
                            transaction.id = data['id']
                            if transaction.deleted_at:
                                transaction.delete()
                            else:
                                transaction.update_special()
                    else:
                        transaction.add_special()
                transaction.close_connection()

            if 'users' in updates:
                table_len = len(updates['users'])
                self.set_pb_items_max(last)
                idx = start
                for users in updates['users']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    user = User()
                    user.user_id = users['id']
                    user.company_id = users['company_id']
                    user.username = users['username']
                    user.first_name = users['first_name']
                    user.last_name = users['last_name']
                    user.street = users['street']
                    user.suite = users['suite']
                    user.city = users['city']
                    user.state = users['state']
                    user.zipcode = users['zipcode']
                    user.email = users['email']
                    user.phone = users['phone']
                    user.intercom = users['intercom']
                    user.concierge_name = users['concierge_name']
                    user.concierge_number = users['concierge_number']
                    user.special_instructions = users['special_instructions']
                    user.shirt_old = users['shirt_old']
                    user.shirt = users['shirt']
                    user.delivery = users['delivery']
                    user.profile_id = users['profile_id']
                    user.payment_status = users['payment_status']
                    user.payment_id = users['payment_id']
                    user.token = users['token']
                    user.api_token = users['api_token']
                    user.reward_status = users['reward_status']
                    user.reward_points = users['reward_points']
                    user.account = users['account']
                    user.account_total = users['account_total']
                    user.credits = users['credits']
                    user.starch = users['starch']
                    user.important_memo = users['important_memo']
                    user.invoice_memo = users['invoice_memo']
                    user.role_id = users['role_id']
                    user.deleted_at = users['deleted_at']
                    user.created_at = users['created_at']
                    user.updated_at = users['updated_at']
                    count_user = user.where({'user_id': user.user_id})
                    if len(count_user) > 0 or user.deleted_at:
                        for data in count_user:
                            user.id = data['id']
                            if user.deleted_at:
                                user.delete()
                            else:
                                user.update_special()
                    else:
                        user.add_special()
                user.close_connection()

            if 'zipcodes' in updates:
                table_len = len(updates['zipcodes'])
                self.set_pb_items_max(last)
                idx = start
                for zipcodes in updates['zipcodes']:
                    idx += 1
                    self.set_pb_items_value(idx)
                    self.set_pb_items_desc('Syncing Row {} of {} out of {}'.format(idx,end,last))
                    zipcode = Zipcode()
                    zipcode.zipcode_id = zipcodes['id']
                    zipcode.company_id = zipcodes['company_id']
                    zipcode.delivery_id = zipcodes['delivery_id']
                    zipcode.zipcode = zipcodes['zipcode']
                    zipcode.status = zipcodes['status']
                    zipcode.deleted_at = zipcodes['deleted_at']
                    zipcode.created_at = zipcodes['created_at']
                    zipcode.updated_at = zipcodes['updated_at']
                    # check to see if color_id already exists and update

                    count_zipcode = zipcode.where({'zipcode_id': zipcode.zipcode_id})
                    if len(count_zipcode) > 0 or zipcode.deleted_at:
                        for data in count_zipcode:
                            zipcode.id = data['id']
                            if zipcode.deleted_at:
                                zipcode.delete()
                            else:
                                zipcode.update_special()
                    else:
                        zipcode.add_special()
                zipcode.close_connection()
    

    def sync_customer(self, customer_id):
        url = 'http://www.jayscleaners.com/admins/api/sync-customer'

        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"

        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if len(data_1) > 0:
                for invoices in data_1:
                    invoice = Invoice()
                    invoice.invoice_id = invoices['id']
                    invoice.company_id = invoices['company_id']
                    invoice.customer_id = invoices['customer_id']
                    invoice.quantity = invoices['quantity']
                    invoice.pretax = invoices['pretax']
                    invoice.tax = invoices['tax']
                    invoice.reward_id = invoices['reward_id']
                    invoice.discount_id = invoices['discount_id']
                    invoice.total = invoices['total']
                    invoice.rack = invoices['rack']
                    invoice.rack_date = invoices['rack_date']
                    invoice.due_date = invoices['due_date']
                    invoice.memo = invoices['memo']
                    invoice.transaction_id = invoices['transaction_id']
                    invoice.schedule_id = invoices['schedule_id']
                    invoice.status = invoices['status']
                    invoice.deleted_at = invoices['deleted_at']
                    invoice.created_at = invoices['created_at']
                    invoice.updated_at = invoices['updated_at']

                    count_invoice = invoice.where({'invoice_id': invoice.invoice_id})
                    if len(count_invoice) > 0 or invoice.deleted_at:
                        for data in count_invoice:
                            invoice.id = data['id']
                            if invoice.deleted_at:
                                invoice.delete()
                            else:
                                invoice.update_special()
                    else:
                        invoice.add()
                    invoice.close_connection()

                    # extra loop through invoice items to delete or check for data
                    if 'invoice_items' in invoices:

                        iitems = invoices['invoice_items']
                        if len(iitems) > 0:
                            for iitem in iitems:
                                invoice_item = InvoiceItem()
                                invoice_item.invoice_items_id = iitem['id']
                                invoice_item.invoice_id = iitem['invoice_id']
                                invoice_item.item_id = iitem['item_id']
                                invoice_item.inventory_id = iitem['inventory_id']
                                invoice_item.company_id = iitem['company_id']
                                invoice_item.customer_id = iitem['customer_id']
                                invoice_item.quantity = iitem['quantity']
                                invoice_item.color = iitem['color']
                                invoice_item.memo = iitem['memo']
                                invoice_item.pretax = iitem['pretax']
                                invoice_item.tax = iitem['tax']
                                invoice_item.total = iitem['total']
                                invoice_item.status = iitem['status']
                                invoice_item.deleted_at = iitem['deleted_at']
                                invoice_item.created_at = iitem['created_at']
                                invoice_item.updated_at = iitem['updated_at']
                                count_invoice_item = invoice_item.where(
                                    {'invoice_items_id': invoice_item.invoice_items_id})
                                if len(count_invoice_item) > 0 or invoice_item.deleted_at:
                                    for data in count_invoice_item:
                                        invoice_item.id = data['id']
                                        if invoice_item.deleted_at:
                                            invoice_item.delete()
                                        else:
                                            invoice_item.update_special()
                                else:
                                    invoice_item.add()
                            invoice_item.close_connection()

        except urllib.error.URLError as e:
            print('Error sending post data: {}'.format(e.reason))



    def test_sys(self):
        Sync().migrate()

    def test_mark(self):

        invoices = Invoice()
        data = {'id': {'>': 0}}
        invs = invoices.where(data)
        if invs:
            for inv in invs:
                invoice_id = inv['id']
                customer_id = inv['customer_id']
                data = {'customer_id': customer_id}
                custs = User()
                if custs:
                    for cust in custs:
                        cust_id = cust['id']
                        invs_1 = Invoice()
                        where = {'id': invoice_id}
                        data = {'customer_id': cust_id}
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

    def print_setup_test(self):

        pass

    def print_setup_tag(self, vendor_id, product_id):
        vendor_int = int(vendor_id, 16)
        product_int = int(product_id, 16)
        # find our device
        dev = usb.core.find(idVendor=vendor_int, idProduct=product_int)

        # was it found?
        if dev is not None:
            print('device found')

            # set the active configuration. With no arguments, the first
            # configuration will be the active one
            dev.set_configuration()

            # get an endpoint instance
            cfg = dev.get_active_configuration()
            intf = cfg[(0, 0)]

            vars.BIXOLON = usb.util.find_descriptor(
                intf,
                # match the first OUT endpoint
                custom_match= \
                    lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_OUT)

        else:
            vars.BIXOLON = False
            popup = Popup()
            popup.title = 'Printer Error'
            content = KV.popup_alert('Tag printer not found.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()

    def print_setup(self, vendor_id, product_id):
        vendor_int = int(vendor_id, 16)
        product_int = int(product_id, 16)
        # find our device
        dev = usb.core.find(idVendor=vendor_int, idProduct=product_int)

        # was it found?
        if dev is not None:
            print('Receipt Device Found')

            # set the active configuration. With no arguments, the first
            # configuration will be the active one
            dev.set_configuration()

            # get an endpoint instance
            cfg = dev.get_active_configuration()
            intf = cfg[(0, 0)]

            vars.EPSON = usb.util.find_descriptor(
                intf,
                # match the first OUT endpoint
                custom_match= \
                    lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_OUT)


        else:
            vars.EPSON = False
            popup = Popup()
            popup.title = 'Printer Error'
            content = KV.popup_alert('Receipt printer not found.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()

    # def print_setup(self, vendor_id, product_id):
    #
    #     vendor_int = int(vendor_id, 16)
    #     vendor_id_hex = hex(vendor_int)
    #     product_int = int(product_id, 16)
    #     product_id_hex = hex(product_int)
    #     print('{} - {}'.format(vendor_id_hex, product_id_hex))
    #     interface_number = 0
    #     in_ep = 0x81
    #     out_ep = 0x02
    #     try:
    #         dev = usb.core.find(idVendor=vendor_int, idProduct=product_int)
    #         # was it found?
    #         if dev is None:
    #             print('Device not found')
    #
    #         # set the active configuration. With no arguments, the first
    #         # configuration will be the active one
    #         dev.set_configuration()
    #
    #         # get an endpoint instance
    #         cfg = dev.get_active_configuration()
    #         for cfg in dev:
    #             sys.stdout.write(str(cfg.bConfigurationValue) + '\n')
    #             for intf in cfg:
    #                 interface_number = intf.bInterfaceNumber
    #                 idx = 0
    #                 for ep in intf:
    #                     idx += 1
    #                     if idx is 1:
    #                         in_ep = ep.bEndpointAddress
    #                     else:
    #                         out_ep = ep.bEndpointAddress
    #
    #     except AttributeError:
    #         print('Error Attribute')
    #     except TypeError:
    #         print('Type Error')
    #
    #     try:
    #         vars.EPSON = printer.Usb(vendor_int, product_int, interface_number, in_ep, out_ep)
    #         print('printer set')
    #     except USBNotFoundError:
    #         vars.EPSON = False
    #         popup = Popup()
    #         popup.title = 'Printer Error'
    #         content = KV.popup_alert('Unable to locate usb printer.')
    #         popup.content = Builder.load_string(content)
    #         popup.open()
    #         # Beep Sound
    #         sys.stdout.write('\a')
    #         sys.stdout.flush()
    #     except TextError:
    #         print('Text error')

    def reports_page(self):
        webbrowser.open("https://www.jayscleaners.com/reports")

    def delivery_page(self):
        webbrowser.open("https://www.jayscleaners.com/delivery/overview")


class ColorsScreen(Screen):
    select_color = ObjectProperty(None)
    colors_table = ObjectProperty(None)
    add_popup = Popup()
    color_name = ObjectProperty(None)
    color_hex = None
    color_id = None
    color_rgba = StringProperty(None)
    reorder_start_id = False
    reorder_end_id = False

    def reset(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
        self.set_color_table()
        self.color_hex = ''
        self.color_id = ''
        self.reorder_end_id = False

    pass

    def set_color_table(self):
        self.colors_table.clear_widgets()

        colored = Colored()
        colorings = colored.where({'company_id': vars.COMPANY_ID, 'ORDER_BY': 'ordered asc'})

        if colorings:
            for clr in colorings:
                if self.reorder_start_id and clr['color_id'] == self.reorder_start_id:
                    c1 = '''
Button:
    font_size:'17sp'
    markup:True
    text: '[b]{color_name}[/b]'
    disabled: False
    text_size:self.size
    valign:'bottom'
    halign:'center'
    on_release: root.parent.parent.parent.parent.parent.action_popup({color_id})
    background_normal: ''
    background_color: {background_rgba}
    Label:
        id: color_label
        size: '50sp','50sp'
        center_x: self.parent.center_x
        center_y: self.parent.center_y + sp(20)
        canvas.before:
            Color:
                rgba: {color_rgba}
            Rectangle:
                pos: self.pos
                size: self.size
'''.format(color_name=clr['name'],
           color_id=clr['color_id'],
           background_rgba=(0, 0.64, 0.149, 1),
           color_rgba=vars.color_rgba(clr['color']))
                elif self.reorder_start_id and clr['color_id'] != self.reorder_start_id:
                    c1 = '''
Button:
    font_size:'17sp'
    markup:True
    text: '[b]{color_name}[/b]'
    disabled: False
    text_size:self.size
    valign:'bottom'
    halign:'center'
    on_release: root.parent.parent.parent.parent.parent.change_order({color_id})
    Label:
        id: color_label
        size: '50sp','50sp'
        center_x: self.parent.center_x
        center_y: self.parent.center_y + sp(20)
        canvas.before:
            Color:
                rgba: {color_rgba}
            Rectangle:
                pos: self.pos
                size: self.size
'''.format(color_name=clr['name'],
           color_id=clr['color_id'],
           color_rgba=vars.color_rgba(clr['color']))
                else:
                    c1 = '''
Button:
    font_size:'17sp'
    markup:True
    text: '[b]{color_name}[/b]'
    disabled: False
    text_size:self.size
    valign:'bottom'
    halign:'center'
    on_release: root.parent.parent.parent.parent.parent.action_popup({color_id})
    Label:
        id: color_label
        size: '50sp','50sp'
        center_x: self.parent.center_x
        center_y: self.parent.center_y + sp(20)
        canvas.before:
            Color:
                rgba: {color_rgba}
            Rectangle:
                pos: self.pos
                size: self.size
'''.format(color_name=clr['name'],
           color_id=clr['color_id'],
           color_rgba=vars.color_rgba(clr['color']))

                self.colors_table.add_widget(Builder.load_string(c1))

    def change_order(self, color_id, *args, **kwargs):
        self.reorder_end_id = color_id
        swap_order = {self.reorder_start_id: '', self.reorder_end_id: ''}
        coloreds = Colored()
        start_colors = coloreds.where({'color_id': self.reorder_start_id, 'company_id': vars.COMPANY_ID})
        if start_colors:
            for clr in start_colors:
                swap_order[self.reorder_end_id] = clr['ordered']

        end_colors = coloreds.where({'color_id': self.reorder_end_id, 'company_id': vars.COMPANY_ID})
        if end_colors:
            for clr in end_colors:
                swap_order[self.reorder_start_id] = clr['ordered']
        if swap_order:
            for key, index in swap_order.items():
                coloreds.put(where={'color_id': key, 'company_id': vars.COMPANY_ID},
                             data={'ordered': index})

        self.reorder_end_id = False
        self.reorder_start_id = False
        self.reset()

    def popup_add(self):
        self.add_popup.title = 'Add Color'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(size_hint=(1, 0.9),
                                   orientation='vertical')
        color_widget = ColorPicker()
        color_widget.bind(color=self.set_color)
        color_grid = GridLayout(size_hint_x=1,
                                size_hint_y=None,
                                cols=2,
                                rows=1,
                                row_force_default=True,
                                row_default_height='40sp',
                                padding=[10, 10, 10, 10])
        self.color_name = Factory.CenterVerticalTextInput()
        color_grid.add_widget(Factory.CenteredFormLabel(text='Color Name:'))
        color_grid.add_widget(self.color_name)
        inner_layout_1.add_widget(color_grid)
        inner_layout_1.add_widget(color_widget)

        inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                   orientation='horizontal')
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_release=self.add_popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=19ff52][b]Add[/b][/color]',
                                         on_release=self.add_color))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.add_popup.content = layout
        self.add_popup.open()

    def popup_edit(self, *args, **kwargs):
        coloreds = Colored()
        clrds = coloreds.where({'color_id': self.color_id, 'company_id': vars.COMPANY_ID})
        color_name = ''
        color_hex = ''
        if clrds:
            for clr in clrds:
                color_name = clr['name']
                color_hex = clr['color']

        self.add_popup.title = 'Add Color'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(size_hint=(1, 0.9),
                                   orientation='vertical')
        color_widget = ColorPicker(hex_color=color_hex)
        color_widget.bind(color=self.set_color)
        color_grid = GridLayout(size_hint_x=1,
                                size_hint_y=None,
                                cols=2,
                                rows=1,
                                row_force_default=True,
                                row_default_height='40sp',
                                padding=[10, 10, 10, 10])
        self.color_name = Factory.CenterVerticalTextInput(text='{}'.format(color_name))
        color_grid.add_widget(Factory.CenteredFormLabel(text='Color Name:'))
        color_grid.add_widget(self.color_name)
        inner_layout_1.add_widget(color_grid)
        inner_layout_1.add_widget(color_widget)

        inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                   orientation='horizontal')
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_release=self.add_popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=19ff52][b]Edit[/b][/color]',
                                         on_release=self.edit_color))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.add_popup.content = layout
        self.add_popup.open()

    def set_color(self, instance, *args, **kwargs):
        self.color_hex = instance.hex_color

    def add_color(self, *args, **kwargs):

        coloreds = Colored()
        # get new ordered number
        new_orders = coloreds.where({'company_id': vars.COMPANY_ID, 'ORDER_BY': 'id desc', 'LIMIT': 1})
        new_order = 1
        if new_orders:
            for no in new_orders:
                ordered = no['ordered']
                new_order = ordered + 1
        coloreds.company_id = vars.COMPANY_ID
        coloreds.color = self.color_hex
        coloreds.name = self.color_name.text
        coloreds.ordered = new_order
        coloreds.status = 1
        if coloreds.add():
            popup = Popup()
            popup.title = 'New Color'
            popup.size_hint = (None, None)
            popup.size = (800, 600)
            popup.content = Builder.load_string(KV.popup_alert('Succesfully added a new color.'))
            popup.open()
            self.add_popup.dismiss()

    def edit_color(self, *args, **kwargs):

        coloreds = Colored()
        # get new ordered number
        put = coloreds.put(where={'color_id': self.color_id, 'company_id': vars.COMPANY_ID},
                           data={'color': self.color_hex,
                                 'name': self.color_name.text})

        if put:
            popup = Popup()
            popup.title = 'Edit Color'
            popup.size_hint = (None, None)
            popup.size = (800, 600)
            popup.content = Builder.load_string(KV.popup_alert('Succesfully edited color.'))
            popup.open()
            self.add_popup.dismiss()

    def action_popup(self, id, *args, **kwargs):
        self.color_id = id
        popup = Popup()
        popup.title = 'Edit Color'
        popup.size_hint = (None, None)
        popup.size = (800, 600)
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.7))
        inner_layout_1.add_widget(Button(text='Reorder',
                                         on_press=popup.dismiss,
                                         on_release=self.reorder_start))
        inner_layout_1.add_widget(Button(text='Edit',
                                         on_press=popup.dismiss,
                                         on_release=self.popup_edit))
        inner_layout_1.add_widget(Button(text='Delete',
                                         on_release=self.delete_confirm))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.3))
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_release=popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def reorder_start(self, *args, **kwargs):
        self.reorder_start_id = self.color_id
        self.reset()

    def delete_confirm(self, *args, **kwargs):
        print('here')
        popup = Popup()
        popup.size_hint = (None, None)
        popup.size = (800, 600)
        popup.title = 'Delete Confirmation'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = Label(size_hint=(1, 0.7),
                               markup=True,
                               text='Are you sure you wish to delete this Color (#{})?'.format(self.color_id))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.3))
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_release=popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=FF0000][b]Delete[/b][/color]',
                                         on_press=self.delete_item,
                                         on_release=popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def delete_item(self, *args, **kwargs):
        coloreds = Colored()
        deleted = coloreds.where({'company_id': vars.COMPANY_ID,
                                  'color_id': self.color_id})
        if deleted:
            for deleted_color in deleted:
                coloreds.id = deleted_color['id']
                if coloreds.delete():
                    popup = Popup()
                    popup.title = 'Deleted Color Notification'
                    popup.size_hint = (None, None)
                    popup.size = (800, 600)
                    content = KV.popup_alert('Successfully deleted color')
                    popup.content = Builder.load_string(content)
                    popup.open()
        else:
            popup = Popup()
            popup.title = 'Deleted Color Notification'
            popup.size_hint = (None, None)
            popup.size = (800, 600)
            content = KV.popup_alert('Could not delete color. Try again.')
            popup.content = Builder.load_string(content)
            popup.open()
        self.reset()


class CompanyScreen(Screen):
    company_name = ObjectProperty(None)
    company_phone = ObjectProperty(None)
    company_email = ObjectProperty(None)
    company_street = ObjectProperty(None)
    company_city = ObjectProperty(None)
    company_state = ObjectProperty(None)
    company_zipcode = ObjectProperty(None)
    company_payment_gateway_id = ObjectProperty(None)
    company_payment_api_login = ObjectProperty(None)
    store_hours_table = ObjectProperty(None)
    store_hours = []
    load_popup = Popup()
    load_count = False

    def reset(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
        companies = Company().where({'company_id': vars.COMPANY_ID})
        if companies:
            for company in companies:
                self.company_name.text = company['name'] if company['name'] else ''
                self.company_phone.text = company['phone'] if company['phone'] else ''
                self.company_email.text = company['email'] if company['email'] else ''
                self.company_street.text = company['street'] if company['street'] else ''
                self.company_city.text = company['city'] if company['city'] else ''
                self.company_state.text = company['state'] if company['state'] else ''
                self.company_zipcode.text = company['zip'] if company['zip'] else ''
                self.company_payment_gateway_id.text = company['payment_gateway_id'] if company[
                    'payment_gateway_id'] else ''
                self.company_payment_api_login.text = company['payment_api_login'] if company[
                    'payment_api_login'] else ''
                self.store_hours = json.loads(company['store_hours'])

        # update hours table
        self.load_count = False

    def update_store_hours_table(self):
        if not self.load_count:
            self.load_count = True
            self.store_hours_table.clear_widgets()

            # start store hours table
            h1 = KV.invoice_tr(0, 'Day')
            h2 = KV.invoice_tr(0, 'Status')
            h3 = KV.invoice_tr(0, 'Op. H')
            h4 = KV.invoice_tr(0, 'Op. M')
            h5 = KV.invoice_tr(0, 'Op. A')
            h6 = KV.invoice_tr(0, 'Cl. H')
            h7 = KV.invoice_tr(0, 'Cl. M')
            h8 = KV.invoice_tr(0, 'Cl. A')
            h9 = KV.invoice_tr(0, 'Turn')
            h10 = KV.invoice_tr(0, 'Due H')
            h11 = KV.invoice_tr(0, 'Due M')
            h12 = KV.invoice_tr(0, 'Due A')
            self.store_hours_table.add_widget(Builder.load_string(h1))
            self.store_hours_table.add_widget(Builder.load_string(h2))
            self.store_hours_table.add_widget(Builder.load_string(h3))
            self.store_hours_table.add_widget(Builder.load_string(h4))
            self.store_hours_table.add_widget(Builder.load_string(h5))
            self.store_hours_table.add_widget(Builder.load_string(h6))
            self.store_hours_table.add_widget(Builder.load_string(h7))
            self.store_hours_table.add_widget(Builder.load_string(h8))
            self.store_hours_table.add_widget(Builder.load_string(h9))
            self.store_hours_table.add_widget(Builder.load_string(h10))
            self.store_hours_table.add_widget(Builder.load_string(h11))
            self.store_hours_table.add_widget(Builder.load_string(h12))
            hours = []
            for index in range(1, 13):
                hours.append(str(index))

            mins = []
            for index in range(0, 60):
                mins.append(':{0:0>2}'.format(index))

            turnaround = []
            for index in range(0, 11):
                turnaround.append(str(index))

            if self.store_hours:
                idx = - 1
                for store_hour in self.store_hours:
                    if store_hour['status'] == '1':
                        store_hour['open_hour'] = "1"
                        store_hour['open_minutes'] = "0"
                        store_hour['open_ampm'] = 'am'
                        store_hour['turnaround'] = "0"
                        store_hour['closed_hour'] = "1"
                        store_hour['closed_minutes'] = "0"
                        store_hour['closed_ampm'] = 'am'
                        store_hour['due_hour'] = "1"
                        store_hour['due_minutes'] = "0"
                        store_hour['due_ampm'] = 'am'
                    idx += 1
                    dow = vars.dow_schedule(idx)
                    c1 = Label(text='{}'.format(dow))
                    c2 = Switch()
                    c2.active = False if store_hour['status'] == '1' else True
                    c2.bind(active=partial(self.set_status, idx))
                    c3 = Spinner(text='{}'.format(str(store_hour['open_hour'])),
                                 values=hours,
                                 disabled=True if store_hour['status'] == '1' else False)
                    c3.bind(text=partial(self.set_store_open_hour, idx))
                    c4 = Spinner(text=':{0:0>2}'.format(store_hour['open_minutes']),
                                 values=mins,
                                 disabled=True if store_hour['status'] == '1' else False)
                    c4.bind(text=partial(self.set_store_open_minutes, idx))
                    c5 = Spinner(text='{}'.format(store_hour['open_ampm']),
                                 values=('am', 'pm'),
                                 disabled=True if store_hour['status'] == '1' else False)
                    c5.bind(text=partial(self.set_store_open_ampm, idx))
                    c6 = Spinner(text='{}'.format(str(store_hour['closed_hour'])),
                                 values=hours,
                                 disabled=True if store_hour['status'] == '1' else False)
                    c6.bind(text=partial(self.set_store_closed_hour, idx))
                    c7 = Spinner(text=':{0:0>2}'.format(store_hour['closed_minutes']),
                                 values=mins,
                                 disabled=True if store_hour['status'] == '1' else False)
                    c7.bind(text=partial(self.set_store_closed_minutes, idx))
                    c8 = Spinner(text='{}'.format(store_hour['closed_ampm']),
                                 values=('am', 'pm'),
                                 disabled=True if store_hour['status'] == '1' else False)
                    c8.bind(text=partial(self.set_store_closed_ampm, idx))
                    c9 = Spinner(text='{}'.format(store_hour['turnaround']),
                                 values=turnaround,
                                 disabled=True if store_hour['status'] == '1' else False)
                    c9.bind(text=partial(self.set_store_turnaround, idx))
                    c10 = Spinner(text='{}'.format(store_hour['due_hour']),
                                  values=hours,
                                  disabled=True if store_hour['status'] == '1' else False)
                    c10.bind(text=partial(self.set_store_due_hour, idx))
                    c11 = Spinner(text=':{0:0>2}'.format(store_hour['due_minutes']),
                                  values=mins,
                                  disabled=True if store_hour['status'] == '1' else False)
                    c11.bind(text=partial(self.set_store_due_minutes, idx))
                    c12 = Spinner(text='{}'.format(store_hour['due_ampm']),
                                  values=('am', 'pm'),
                                  disabled=True if store_hour['status'] == '1' else False)
                    c12.bind(text=partial(self.set_store_due_ampm, idx))

                    self.store_hours_table.add_widget(c1)
                    self.store_hours_table.add_widget(c2)
                    self.store_hours_table.add_widget(c3)
                    self.store_hours_table.add_widget(c4)
                    self.store_hours_table.add_widget(c5)
                    self.store_hours_table.add_widget(c6)
                    self.store_hours_table.add_widget(c7)
                    self.store_hours_table.add_widget(c8)
                    self.store_hours_table.add_widget(c9)
                    self.store_hours_table.add_widget(c10)
                    self.store_hours_table.add_widget(c11)
                    self.store_hours_table.add_widget(c12)

    def set_status(self, day, item, status, *args, **kwargs):
        if self.store_hours:
            self.store_hours[day]['status'] = 2 if not status else 1

    def set_store_open_hour(self, day, item, hour, *args, **kwargs):
        if self.store_hours:
            self.store_hours[day]['open_hour'] = hour

    def set_store_open_minutes(self, day, item, minutes, *args, **kwargs):
        if self.store_hours:
            self.store_hours[day]['open_minutes'] = re.sub(r'\W+', '', minutes)

    def set_store_open_ampm(self, day, item, ampm, *args, **kwargs):
        if self.store_hours:
            self.store_hours[day]['open_ampm'] = ampm

    def set_store_closed_hour(self, day, item, hour, *args, **kwargs):
        if self.store_hours:
            self.store_hours[day]['closed_hour'] = hour

    def set_store_closed_minutes(self, day, item, minutes, *args, **kwargs):
        if self.store_hours:
            self.store_hours[day]['closed_minutes'] = '{0:0>2}'.format(re.sub(r'\W+', '', minutes))

    def set_store_closed_ampm(self, day, item, ampm, *args, **kwargs):
        if self.store_hours:
            self.store_hours[day]['closed_ampm'] = ampm

    def set_store_turnaround(self, day, item, turnaround, *args, **kwargs):
        if self.store_hours:
            self.store_hours[day]['turnaround'] = turnaround

    def set_store_due_hour(self, day, item, hour, *args, **kwargs):
        if self.store_hours:
            self.store_hours[day]['due_hour'] = hour

    def set_store_due_minutes(self, day, item, minutes, *args, **kwargs):
        if self.store_hours:
            self.store_hours[day]['due_minutes'] = '{0:0>2}'.format(re.sub(r'\W+', '', minutes))

    def set_store_due_ampm(self, day, item, ampm, *args, **kwargs):
        if self.store_hours:
            self.store_hours[day]['due_ampm'] = ampm

    def update(self):

        companies = Company()
        put = companies.put(where={'company_id': vars.COMPANY_ID},
                            data={'name': self.company_name.text,
                                  'phone': self.company_phone.text,
                                  'email': self.company_email.text,
                                  'street': self.company_street.text,
                                  'city': self.company_city.text,
                                  'state': self.company_state.text,
                                  'zip': self.company_zipcode.text,
                                  'payment_gateway_id': self.company_payment_gateway_id.text,
                                  'payment_api_login': self.company_payment_api_login.text,
                                  'store_hours': self.store_hours
                                  })
        if put:
            vars.WORKLIST.append("Sync")
            threads_start()
            popup = Popup()
            popup.title = 'Company Update'
            content = KV.popup_alert('Successfully updated company!')
            popup.content = Builder.load_string(content)
            popup.open()


class DeliveryScreen(Screen):
    pass


class DropoffScreen(Screen):
    sm = ObjectProperty(None)
    inv_qty_list = ['1']
    qty_clicks = 0
    inv_qty = 1
    adjust_sum_grid = ObjectProperty(None)
    adjust_individual_grid = ObjectProperty(None)
    invoice_list = OrderedDict()
    invoice_list_copy = OrderedDict()
    inventory_panel = ObjectProperty(None)
    items_grid = GridLayout()
    qty_count_label = ObjectProperty(None)
    item_selected_row = 0
    items_layout = ObjectProperty(None)
    memo_text_input = TextInput(size_hint=(1, 0.4),
                                multiline=True)
    summary_table = ObjectProperty(None)
    summary_quantity_label = ObjectProperty(None)
    summary_tags_label = ObjectProperty(None)
    summary_subtotal_label = ObjectProperty(None)
    summary_tax_label = ObjectProperty(None)
    summary_discount_label = ObjectProperty(None)
    summary_total_label = ObjectProperty(None)
    quantity = 0
    tags = 0
    subtotal = 0
    tax = 0
    discount = 0
    total = 0
    adjust_price = 0
    adjusted_price = ObjectProperty(None)
    calculator_text = ObjectProperty(None)
    adjust_price_list = []
    memo_color_popup = Popup()
    date_picker = ObjectProperty(None)
    due_date = None
    due_date_string = None
    now = datetime.datetime.now()
    month = now.month
    year = now.year
    day = now.day
    calendar_layout = ObjectProperty(None)
    month_button = ObjectProperty(None)
    year_button = ObjectProperty(None)
    print_popup = ObjectProperty(None)
    deleted_rows = []
    starch = None
    memo_list = []
    colors_table_main = ObjectProperty(None)
    customer_id_backup = None
    discount_id = None

    def reset(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
        # reset the inventory table
        self.inventory_panel.clear_widgets()
        self.get_inventory()
        self.summary_table.clear_widgets()
        store_hours = Company().get_store_hours(vars.COMPANY_ID)
        today = datetime.datetime.today()
        dow = int(datetime.datetime.today().strftime("%w"))
        turn_around_day = int(store_hours[dow]['turnaround']) if store_hours[dow]['turnaround'] else 0
        turn_around_hour = store_hours[dow]['due_hour'] if store_hours[dow]['due_hour'] else '4'
        turn_around_minutes = store_hours[dow]['due_minutes'] if store_hours[dow]['due_minutes'] else '00'
        turn_around_ampm = store_hours[dow]['due_ampm'] if store_hours[dow]['due_ampm'] else 'pm'
        new_date = today + datetime.timedelta(days=turn_around_day)
        date_string = '{} {}:{}:00'.format(new_date.strftime("%Y-%m-%d"),
                                           turn_around_hour if turn_around_ampm == 'am' else int(turn_around_hour) + 12,
                                           turn_around_minutes)
        self.due_date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        self.due_date_string = '{}'.format(self.due_date.strftime('%a %m/%d %I:%M%p'))
        self.date_picker.text = self.due_date_string
        self.inventory_panel.clear_widgets()
        self.get_inventory()
        self.memo_color_popup.dismiss()
        self.qty_clicks = 0
        self.inv_qty = 1
        self.inv_qty_list = ['1']
        self.qty_count_label.text = '1'
        self.invoice_list = OrderedDict()
        self.invoice_list_copy = OrderedDict()
        self.memo_text_input.text = ''
        self.summary_table.clear_widgets()
        self.summary_quantity_label.text = '[color=000000]0[/color]'
        self.summary_tags_label.text = '[color=000000]0[/color]'
        self.summary_subtotal_label.text = '[color=000000]$0.00[/color]'
        self.summary_tax_label.text = '[color=000000]$0.00[/color]'
        self.summary_discount_label.text = '[color=000000]($0.00)[/color]'
        self.summary_total_label.text = '[color=000000]$0.00[/color]'
        self.quantity = 0
        self.tags = 0
        self.subtotal = 0
        self.tax = 0
        self.discount = 0
        self.total = 0
        self.adjust_price = 0
        self.discount_id = None
        self.customer_id_backup = vars.CUSTOMER_ID
        self.adjust_price_list = []
        vars.ITEM_ID = None
        # reset the inventory table
        self.inventory_panel.clear_widgets()
        self.get_inventory()
        # create th for invoice summary table
        h1 = KV.sized_invoice_tr(0, 'Type', size_hint_x=0.1)
        h2 = KV.sized_invoice_tr(0, 'Qty', size_hint_x=0.1)
        h3 = KV.sized_invoice_tr(0, 'Item', size_hint_x=0.6)
        h4 = KV.sized_invoice_tr(0, 'Subtotal', size_hint_x=0.2)
        self.summary_table.add_widget(Builder.load_string(h1))
        self.summary_table.add_widget(Builder.load_string(h2))
        self.summary_table.add_widget(Builder.load_string(h3))
        self.summary_table.add_widget(Builder.load_string(h4))
        self.get_inventory()
        self.deleted_rows = []
        self.memo_list = []
        self.colors_table_main.clear_widgets()
        self.get_colors_main()
        taxes = Tax().where({'company_id': vars.COMPANY_ID, 'status': 1})
        if taxes:
            for tax in taxes:
                vars.TAX_RATE = tax['rate']
        else:
            vars.TAX_RATE = 0.096

        customers = User().where({'user_id': vars.CUSTOMER_ID})
        if customers:
            for customer in customers:
                self.starch = vars.get_starch_by_code(customer['starch'])
        else:
            self.starch = vars.get_starch_by_code(None)

        SYNC_POPUP.dismiss()

    def set_result_status(self):
        vars.SEARCH_RESULTS_STATUS = True
        self.summary_table.clear_widgets()


    def get_colors_main(self):

        colors = Colored().where({'company_id': vars.COMPANY_ID, 'ORDER_BY': 'ordered asc'})
        if colors:
            for color in colors:
                color_btn = Button(markup=True,
                                   text='[b]{color_name}[/b]'.format(color_name=color['name']),
                                   min_state_time=0.020)
                color_btn.bind(on_release=partial(self.color_selected_main, color['name']))
                color_btn.background_normal = ''
                color_btn.background_color = vars.color_rgba(color['name'])
                self.colors_table_main.add_widget(color_btn)

    def color_selected_main(self, color_name, *args, **kwargs):
        # quantity

        qty = self.inv_qty

        if vars.ITEM_ID in self.invoice_list_copy:
            # loop through the invoice list and see how many colors are set and which is the last row to be set
            total_colors_usable = 0
            rows_updatable = []
            row_to_update = -1
            for row in self.invoice_list_copy[vars.ITEM_ID]:
                row_to_update += 1

                if 'color' in self.invoice_list_copy[vars.ITEM_ID][row_to_update]:
                    if self.invoice_list_copy[vars.ITEM_ID][row_to_update]['color'] is '':
                        total_colors_usable += 1
                        rows_updatable.append(row_to_update)

            if total_colors_usable >= qty:
                qty_countdown = qty
                for row in rows_updatable:

                    if 'color' in self.invoice_list_copy[vars.ITEM_ID][row]:
                        if self.invoice_list_copy[vars.ITEM_ID][row]['color'] is '':
                            qty_countdown -= 1
                            if qty_countdown >= 0:
                                self.invoice_list_copy[vars.ITEM_ID][row]['color'] = color_name

                # save rows and continue

                self.save_memo_color()

                self.create_summary_table()
            else:
                popup = Popup()
                popup.title = 'Color Quantity Error'
                content = KV.popup_alert('Color quantity does not match invoice item quantity. Please try again.')
                popup.content = Builder.load_string(content)
                popup.open()
                # Beep Sound
                sys.stdout.write('\a')
                sys.stdout.flush()

        # reset qty
        self.set_qty('C')

        pass

    def get_inventory(self):
        inventories = Inventory().where({'company_id': '{}'.format(vars.COMPANY_ID)})
        if inventories:
            idx = 0
            self.inventory_panel.clear_tabs()
            self.inventory_panel.clear_widgets()
            for inventory in inventories:
                idx += 1
                inventory_id = inventory['inventory_id']
                inventory_name = inventory['name']
                iitems = InventoryItem()
                inventory_items = iitems.where({'inventory_id': inventory_id, 'ORDER_BY': 'ordered ASC'})
                tph = TabbedPanelHeader(text='{}'.format(inventory_name))
                layout = ScrollView()
                content = '''
GridLayout:
    size_hint_y:None
    height: self.minimum_height
    cols:4
    row_force_default: True
    row_default_height:'150sp'
'''
                if inventory_items:
                    for item in inventory_items:
                        item_id = item['item_id']
                        item_price = '${:,.2f}'.format(item['price'])
                        content += '''
    Button:
        font_size:'17sp'
        markup:True
        text: '[b]{item_name}[/b]\\n[i]{item_price}[/i]'
        disabled: False
        text_size:self.size
        valign:'bottom'
        halign:'center'
        min_state_time: 0.010
        on_release: root.parent.parent.parent.parent.parent.parent.set_item({item_id})
        background_rgba:(.7,.3,.5,1)
        Image:
            id: item_image
            source: '{img_src}'
            size: '50sp','50sp'
            center_x: self.parent.center_x
            center_y: self.parent.center_y + sp(20)
            allow_stretch: True'''.format(item_name=item['name'],
                                          item_price=item_price,
                                          item_id=item_id,
                                          img_src=iitems.get_image_src(item['item_id']))

                layout.add_widget(Builder.load_string(content))
                tph.content = layout
                self.inventory_panel.add_widget(tph)
                if idx == 1:
                    self.inventory_panel.switch_to(tph)

    def set_qty(self, qty):

        if qty == 'C':
            self.qty_clicks = 0
            self.inv_qty_list = ['1']
        elif self.qty_clicks is 0 and qty is 0:
            self.qty_clicks += 0
            self.inv_qty_list = ['0']
        elif self.qty_clicks == 0 and qty is 1:
            self.qty_clicks += 1
            self.inv_qty_list = ['1']
        elif self.qty_clicks == 0 and qty > 1:
            self.qty_clicks += 1
            self.inv_qty_list = ['{}'.format(str(qty))]
        else:
            self.qty_clicks += 1
            self.inv_qty_list.append('{}'.format(str(qty)))
        inv_str = ''.join(self.inv_qty_list)
        if len(self.inv_qty_list) > 3:
            self.qty_clicks = 0
            self.inv_qty_list = ['1']
            inv_str = '1'
        self.qty_count_label.text = inv_str
        self.inv_qty = int(inv_str)

    def set_item(self, item_id):
        vars.ITEM_ID = item_id
        items = InventoryItem().where({'item_id': item_id})
        if items:
            for item in items:
                inventory_id = item['inventory_id']
                item_price = item['price']

                item_tags = item['tags'] if item['tags'] else 1
                item_quantity = item['quantity'] if item['quantity'] else 1
                inventories = Inventory().where({'inventory_id': '{}'.format(str(inventory_id))})
                if inventories:
                    for inventory in inventories:
                        inventory_init = inventory['name'][:1].capitalize()
                        laundry = inventory['laundry']
                else:
                    inventory_init = ''
                    laundry = 0

                starch = self.starch if laundry else ''
                item_name = '{} ({})'.format(item['name'], starch) if laundry else item['name']

                for x in range(0, self.inv_qty):

                    if item_id in self.invoice_list:
                        self.invoice_list[item_id].append({
                            'type': inventory_init,
                            'inventory_id': inventory_id,
                            'item_id': item_id,
                            'item_name': item_name,
                            'item_price': item_price,
                            'color': '',
                            'memo': '',
                            'qty': int(item_quantity),
                            'tags': int(item_tags)
                        })
                        self.invoice_list_copy[item_id].append({
                            'type': inventory_init,
                            'inventory_id': inventory_id,
                            'item_id': item_id,
                            'item_name': item_name,
                            'item_price': item_price,
                            'color': '',
                            'memo': '',
                            'qty': int(item_quantity),
                            'tags': int(item_tags)
                        })
                    else:
                        self.invoice_list[item_id] = [{
                            'type': inventory_init,
                            'inventory_id': inventory_id,
                            'item_id': item_id,
                            'item_name': item_name,
                            'item_price': item_price,
                            'color': '',
                            'memo': '',
                            'qty': int(item_quantity),
                            'tags': int(item_tags)
                        }]
                        self.invoice_list_copy[item_id] = [{
                            'type': inventory_init,
                            'inventory_id': inventory_id,
                            'item_id': item_id,
                            'item_name': item_name,
                            'item_price': item_price,
                            'color': '',
                            'memo': '',
                            'qty': int(item_quantity),
                            'tags': int(item_tags)
                        }]
        # update dictionary make sure that the most recently selected item is on top
        row = self.invoice_list[vars.ITEM_ID]
        del self.invoice_list[vars.ITEM_ID]
        self.invoice_list[item_id] = row

        self.create_summary_table()
        self.set_qty('C')

    def create_summary_table(self):
        self.summary_table.clear_widgets()

        # create th
        h1 = KV.sized_invoice_tr(0, 'Type', size_hint_x=0.1)
        h2 = KV.sized_invoice_tr(0, 'Qty', size_hint_x=0.1)
        h3 = KV.sized_invoice_tr(0, 'Item', size_hint_x=0.5)
        h4 = KV.sized_invoice_tr(0, 'Subtotal', size_hint_x=0.2)
        h5 = KV.sized_invoice_tr(0, 'A.', size_hint_x=0.1)
        self.summary_table.add_widget(Builder.load_string(h1))
        self.summary_table.add_widget(Builder.load_string(h2))
        self.summary_table.add_widget(Builder.load_string(h3))
        self.summary_table.add_widget(Builder.load_string(h4))
        self.summary_table.add_widget(Builder.load_string(h5))

        if self.invoice_list:

            for key, values in OrderedDict(reversed(list(self.invoice_list.items()))).items():
                item_id = key
                total_qty = len(values)
                colors = {}
                item_price = 0
                color_string = []
                memo_string = []
                if values:
                    for item in values:
                        item_name = item['item_name']
                        item_type = item['type']
                        item_color = item['color']
                        item_memo = item['memo']
                        item_price += item['item_price'] if item['item_price'] else 0
                        if item['color']:
                            if item_color in colors:
                                colors[item_color] += 1
                            else:
                                colors[item_color] = 1
                        if item_memo:
                            regexed_memo = item_memo.replace('"', '**Inch(es)')
                            memo_string.append(regexed_memo)
                    if colors:
                        for color_name, color_amount in colors.items():
                            if color_name:
                                color_string.append('{}-{}'.format(color_amount, color_name))

                    item_string = '[b]{}[/b] \\n{}\\n{}'.format(item_name, ', '.join(color_string),
                                                                '/ '.join(memo_string))
                    selected = True if vars.ITEM_ID == item_id else False
                    tr1 = KV.sized_invoice_tr(1,
                                              item_type,
                                              size_hint_x=0.1,
                                              selected=selected,
                                              on_release='self.parent.parent.parent.parent.parent.parent.select_item({})'.format(
                                                  item_id))
                    tr2 = KV.sized_invoice_tr(1,
                                              total_qty,
                                              size_hint_x=0.1,
                                              selected=selected,
                                              on_release='self.parent.parent.parent.parent.parent.parent.select_item({})'.format(
                                                  item_id))
                    tr3 = KV.sized_invoice_tr(1,
                                              item_string,
                                              size_hint_x=0.5,
                                              selected=selected,
                                              text_wrap=True,
                                              on_release='self.parent.parent.parent.parent.parent.parent.select_item({})'.format(
                                                  item_id))
                    tr4 = KV.sized_invoice_tr(1,
                                              vars.us_dollar(item_price),
                                              size_hint_x=0.2,
                                              selected=selected,
                                              on_release='self.parent.parent.parent.parent.parent.parent.select_item({})'.format(
                                                  item_id))
                    tr5 = Button(size_hint_x=0.1,
                                 markup=True,
                                 text="[color=ffffff][b]-[/b][/color]",
                                 background_color=(1, 0, 0, 1),
                                 background_normal='',
                                 on_release=partial(self.remove_item_row, item_id))
                    self.summary_table.add_widget(Builder.load_string(tr1))
                    self.summary_table.add_widget(Builder.load_string(tr2))
                    self.summary_table.add_widget(Builder.load_string(tr3))
                    self.summary_table.add_widget(Builder.load_string(tr4))
                    self.summary_table.add_widget(tr5)
        self.create_summary_totals()

    def select_item(self, item_id, *args, **kwargs):
        vars.ITEM_ID = item_id
        self.create_summary_table()

    def remove_item_row(self, item_id, *args, **kwargs):
        vars.ITEM_ID = item_id
        if vars.ITEM_ID in self.invoice_list:
            del self.invoice_list[vars.ITEM_ID]
        if vars.ITEM_ID in self.invoice_list_copy:
            del self.invoice_list_copy[vars.ITEM_ID]
        if self.invoice_list:
            idx = 0
            for row_key, row_value in self.invoice_list.items():
                idx += 1
                if idx == 1:
                    vars.ITEM_ID = row_key
                    break
        self.create_summary_table()
        self.create_summary_totals()

    def create_summary_totals(self):
        self.quantity = 0
        self.tags = 0
        self.subtotal = 0
        self.tax = 0
        self.discount = 0
        self.total = 0
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))

        # calculate totals
        if len(self.invoice_list):
            for item_key, item_values in self.invoice_list.items():
                for item in item_values:
                    self.quantity += 1
                    self.tags += int(item['tags']) if item['tags'] else 1
                    self.subtotal += float(item['item_price']) if item['item_price'] else 0
                    # calculate discounts
                    discounts = Discount().where({'company_id': vars.COMPANY_ID,
                                                  'start_date': {'<=': '"{}"'.format(now)},
                                                  'end_date': {'>=': '"{}"'.format(now)},
                                                  'inventory_id':item['inventory_id']});
                    if discounts:
                        for discount in discounts:
                            discount_rate = float(discount['rate'])
                            discount_price = float(discount['discount'])
                            self.discount_id = discount['discount_id']
                            if discount_rate > 0:
                                self.discount += (float(item['item_price'] * discount_rate))
                            elif discount_rate is 0 and discount_price > 0:
                                self.discount += (float(item['item_price']) - discount_price)
                            else:
                                self.discount += 0
            self.tax = (self.subtotal - self.discount) * vars.TAX_RATE
            self.total = (self.subtotal - self.discount) + self.tax
            self.summary_quantity_label.text = '[color=000000]{}[/color] pcs'.format(self.quantity)
            self.summary_tags_label.text = '[color=000000]{} tags'.format(self.tags)
            self.summary_subtotal_label.text = '[color=000000]{}[/color]'.format(vars.us_dollar(self.subtotal))
            self.summary_tax_label.text = '[color=000000]{}[/color]'.format(vars.us_dollar(self.tax))
            self.summary_discount_label.text = '[color=000000]({})[/color]'.format(vars.us_dollar(self.discount))
            self.summary_total_label.text = '[color=000000][b]{}[/b][/color]'.format(vars.us_dollar(self.total))

    def make_memo_color(self):

        self.item_row_selected(row=0)

        # make popup
        self.memo_color_popup.title = "Add Memo / Color"

        layout = BoxLayout(orientation='vertical',
                           pos_hint={'top': 1},
                           size_hint=(1, 1))

        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.9))
        memo_color_layout = BoxLayout(orientation='vertical',
                                      size_hint=(0.5, 1))
        color_layout = ScrollView(size_hint=(1, 0.4))
        color_title = Label(markup=True,
                            text='[b]Select A Color[/b]',
                            size_hint=(1, 0.1))
        memo_color_layout.add_widget(color_title)
        color_grid = GridLayout(size_hint_y=None,
                                cols=5,
                                row_force_default=True,
                                row_default_height='60sp')
        color_grid.bind(minimum_height=color_grid.setter('height'))
        colors = Colored().where({'company_id': vars.COMPANY_ID, 'ORDER_BY': 'ordered asc'})
        if colors:
            for color in colors:
                color_btn = Button(markup=True,
                                   text='[b]{color_name}[/b]'.format(color_name=color['name']),
                                   on_release=partial(self.color_selected, color['name']))
                color_btn.text_size = color_btn.size
                color_btn.font_size = '12sp'
                color_btn.valign = 'bottom'
                color_btn.halign = 'center'
                color_btn.background_normal = ''
                color_btn.background_color = vars.color_rgba(color['name'])
                color_grid.add_widget(color_btn)
        color_layout.add_widget(color_grid)
        # memo section
        memo_layout = BoxLayout(orientation='vertical',
                                size_hint=(1, 0.5))
        memo_inner_layout_1 = BoxLayout(orientation='vertical',
                                        size_hint=(1, 0.8))
        memo_scroll_view = ScrollView()
        memo_grid_layout = Factory.GridLayoutForScrollView(row_default_height='50sp',
                                                           cols=4)
        mmos = Memo()
        memos = mmos.where({'company_id': vars.COMPANY_ID,
                            'ORDER_BY': 'ordered asc'})
        if memos:
            for memo in memos:
                btn_memo = Factory.LongButton(text=str(memo['memo']),
                                              on_release=partial(self.append_memo, memo['memo']))
                memo_grid_layout.add_widget(btn_memo)

        memo_scroll_view.add_widget(memo_grid_layout)

        memo_inner_layout_2 = BoxLayout(orientation='horizontal',
                                        size_hint=(1, 0.2))
        memo_title = Label(markup=True,
                           pos_hint={'top': 1},
                           text='[b]Create Memo[/b]',
                           size_hint=(1, 0.1))
        memo_text_input = Factory.CenterVerticalTextInput(text='',
                                                          size_hint=(0.7, 1),
                                                          multiline=False)
        memo_inner_layout_1.add_widget(memo_title)
        memo_inner_layout_1.add_widget(memo_scroll_view)

        try:
            memo_inner_layout_2.add_widget(memo_text_input)
        except WidgetException:
            memo_inner_layout_2.remove_widget(memo_text_input)
            memo_inner_layout_2.add_widget(memo_text_input)
        memo_layout.add_widget(memo_inner_layout_1)
        memo_layout.add_widget(memo_inner_layout_2)
        self.memo_text_input = memo_text_input
        memo_add_button = Button(text='Add',
                                 size_hint=(0.3, 1),
                                 on_press=self.add_memo)
        memo_inner_layout_2.add_widget(memo_add_button)

        memo_color_layout.add_widget(color_layout)
        memo_color_layout.add_widget(memo_layout)
        # make items side
        self.items_layout = ScrollView(size_hint=(0.5, 1),
                                       pos_hint={'top': 1})
        self.items_grid = GridLayout(size_hint_y=None,
                                     cols=5,
                                     row_force_default=True,
                                     row_default_height='60sp')
        self.make_items_table()
        self.items_layout.add_widget(self.items_grid)

        inner_layout_1.add_widget(memo_color_layout)
        inner_layout_1.add_widget(self.items_layout)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        cancel_button = Button(markup=True,
                               text="Cancel",
                               on_press=self.memo_color_popup.dismiss)
        save_button = Button(markup=True,
                             text="[color=00f900][b]Save[/b][/color]",
                             on_press=self.save_memo_color,
                             on_release=self.memo_color_popup.dismiss)

        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(save_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.memo_color_popup.content = layout
        # show layout
        self.memo_color_popup.open()

    def append_memo(self, msg, *args, **kwargs):
        if not self.memo_list:
            self.memo_list = [msg]
        else:
            self.memo_list.append(msg)
        self.memo_text_input.text = ', '.join(self.memo_list)

    def make_items_table(self):
        self.items_grid.clear_widgets()
        item_th1 = KV.sized_invoice_tr(0, '#', size_hint_x=0.1)
        item_th2 = KV.sized_invoice_tr(0, 'Item', size_hint_x=0.2)
        item_th3 = KV.sized_invoice_tr(0, 'Color', size_hint_x=0.1)
        item_th4 = KV.sized_invoice_tr(0, 'Memo', size_hint_x=0.5)
        item_th5 = KV.sized_invoice_tr(0, 'A.', size_hint_x=0.1)

        self.items_grid.add_widget(Builder.load_string(item_th1))
        self.items_grid.add_widget(Builder.load_string(item_th2))
        self.items_grid.add_widget(Builder.load_string(item_th3))
        self.items_grid.add_widget(Builder.load_string(item_th4))
        self.items_grid.add_widget(Builder.load_string(item_th5))
        if vars.ITEM_ID:
            if vars.ITEM_ID in self.invoice_list_copy:
                idx = -1
                for items in self.invoice_list_copy[vars.ITEM_ID]:
                    idx += 1
                    background_color = (0.36862745, 0.36862745, 0.36862745, 1) if idx == self.item_selected_row else (
                        0.89803922, 0.89803922, 0.89803922, 1)
                    background_normal = ''
                    text_color = 'e5e5e5' if idx == self.item_selected_row else '000000'
                    item_name = items['item_name']
                    item_color = items['color']
                    item_memo = items['memo']
                    items_tr1 = Button(markup=True,
                                       text='[color=#{text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                        msg=str((idx + 1))),
                                       on_press=partial(self.item_row_selected, idx),
                                       size_hint_x=0.1,
                                       font_size='12sp',
                                       background_color=background_color,
                                       background_normal=background_normal)
                    items_tr2 = Button(markup=True,
                                       text='[color=#{text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                        msg=item_name),
                                       on_press=partial(self.item_row_selected, idx),
                                       size_hint_x=0.2,
                                       font_size='12sp',
                                       background_color=background_color,
                                       background_normal=background_normal)

                    items_tr3 = Button(markup=True,
                                       text='[color=#{text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                        msg=item_color),
                                       on_press=partial(self.item_row_selected, idx),
                                       size_hint_x=0.2,
                                       font_size='12sp',
                                       background_color=background_color,
                                       background_normal=background_normal)
                    items_tr4 = Factory.LongButton(
                        text='[color=#{text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                         msg=item_memo),
                        on_press=partial(self.item_row_selected, idx),
                        size_hint_x=0.4,
                        size_hint_y=None,
                        background_color=background_color,
                        background_normal=background_normal)
                    items_tr5 = Button(markup=True,
                                       text='[color=ff0000][b]Edit[b][/color]',
                                       on_press=partial(self.item_row_selected, idx),
                                       on_release=partial(self.item_row_edit, idx),
                                       size_hint_x=0.1,
                                       font_size='12sp',
                                       background_color=background_color,
                                       background_normal=background_normal)

                    self.items_grid.add_widget(items_tr1)
                    self.items_grid.add_widget(items_tr2)
                    self.items_grid.add_widget(items_tr3)
                    self.items_grid.add_widget(items_tr4)
                    items_tr4.text_size = (items_tr4.width + 200, items_tr4.height)

                    self.items_grid.add_widget(items_tr5)
        self.items_grid.bind(minimum_height=self.items_grid.setter('height'))

    def add_memo(self, *args, **kwargs):
        if vars.ITEM_ID in self.invoice_list_copy:
            self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]['memo'] = self.memo_text_input.text
            next_row = self.item_selected_row + 1 if (self.item_selected_row + 1) < len(
                self.invoice_list_copy[vars.ITEM_ID]) else 0
            self.item_selected_row = next_row
            self.make_items_table()
            self.memo_text_input.text = ''
            self.memo_list = []

    def color_selected(self, color=False, *args, **kwargs):
        if vars.ITEM_ID in self.invoice_list_copy:
            self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]['color'] = color
            next_row = self.item_selected_row + 1 if (self.item_selected_row + 1) < len(
                self.invoice_list_copy[vars.ITEM_ID]) else 0
            self.item_selected_row = next_row
            self.make_items_table()

    def item_row_edit(self, row, *args, **kwargs):
        popup = Popup(title='Remove Colors / Memo')
        popup.size_hint = None, None
        popup.size = 900, 600
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.7))
        inner_layout_1.add_widget(Button(markup=True,
                                         text='Remove Color',
                                         on_press=self.remove_color,
                                         on_release=popup.dismiss))
        inner_layout_1.add_widget(Button(markup=True,
                                         text='Remove Memo',
                                         on_press=self.remove_memo,
                                         on_release=popup.dismiss))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.3))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='Cancel',
                                         on_release=popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def remove_color(self, *args, **kwargs):
        if vars.ITEM_ID in self.invoice_list_copy:
            self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]['color'] = ''
            self.make_items_table()

    def remove_memo(self, *args, **kwargs):
        if vars.ITEM_ID in self.invoice_list_copy:
            self.memo_list = []
            self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]['memo'] = ''
            self.make_items_table()

    def item_row_selected(self, row, *args, **kwargs):
        self.item_selected_row = row
        self.make_items_table()

    def save_memo_color(self, *args, **kwargs):
        if vars.ITEM_ID in self.invoice_list_copy:
            idx = -1
            for items in self.invoice_list_copy[vars.ITEM_ID]:
                idx += 1
                color = items['color']
                memo = items['memo']
                self.invoice_list[vars.ITEM_ID][idx]['color'] = color
                self.invoice_list[vars.ITEM_ID][idx]['memo'] = memo
        self.create_summary_table()

    def make_adjust(self):
        self.item_selected_row = 0
        popup = Popup()
        popup.title = 'Adjust Items'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.9))
        adjust_sum_section = BoxLayout(orientation='vertical',
                                       size_hint=(0.5, 1))
        adjust_sum_title = Label(size_hint=(1, 0.1),
                                 markup=True,
                                 text='[b]Adjust Sum Total[/b]')
        adjust_sum_scroll = ScrollView(size_hint=(1, 0.9))
        self.adjust_sum_grid = GridLayout(size_hint_y=None,
                                          cols=4,
                                          row_force_default=True,
                                          row_default_height='50sp')
        self.adjust_sum_grid.bind(minimum_height=self.adjust_sum_grid.setter('height'))
        self.make_adjustment_sum_table()
        adjust_sum_scroll.add_widget(self.adjust_sum_grid)
        adjust_sum_section.add_widget(adjust_sum_title)
        adjust_sum_section.add_widget(adjust_sum_scroll)
        inner_layout_1.add_widget(adjust_sum_section)
        adjust_individual_section = BoxLayout(orientation='vertical',
                                              size_hint=(0.5, 1))

        adjust_individual_title = Label(size_hint=(1, 0.1),
                                        markup=True,
                                        text='[b]Adjust Individual Totals[/b]')
        adjust_individual_scroll = ScrollView(size_hint=(1, 0.9))
        self.adjust_individual_grid = GridLayout(size_hint_y=None,
                                                 cols=5,
                                                 row_force_default=True,
                                                 row_default_height='50sp')
        self.adjust_individual_grid.bind(minimum_height=self.adjust_individual_grid.setter('height'))
        self.make_adjustment_individual_table()
        adjust_individual_scroll.add_widget(self.adjust_individual_grid)
        adjust_individual_section.add_widget(adjust_individual_title)
        adjust_individual_section.add_widget(adjust_individual_scroll)
        inner_layout_1.add_widget(adjust_individual_section)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(markup=True,
                                         text="Cancel",
                                         on_release=popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text="[color=00f900][b]save[/b][/color]",
                                         on_press=self.save_price_adjustment,
                                         on_release=popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def make_adjustment_sum_table(self):
        self.adjust_sum_grid.clear_widgets()
        if vars.ITEM_ID in self.invoice_list_copy:
            if len(self.invoice_list_copy[vars.ITEM_ID]) > 1:
                # create th
                h1 = KV.sized_invoice_tr(0, 'Type', size_hint_x=0.1)
                h2 = KV.sized_invoice_tr(0, 'Qty', size_hint_x=0.1)
                h3 = KV.sized_invoice_tr(0, 'Item', size_hint_x=0.6)
                h4 = KV.sized_invoice_tr(0, 'Subtotal', size_hint_x=0.2)
                self.adjust_sum_grid.add_widget(Builder.load_string(h1))
                self.adjust_sum_grid.add_widget(Builder.load_string(h2))
                self.adjust_sum_grid.add_widget(Builder.load_string(h3))
                self.adjust_sum_grid.add_widget(Builder.load_string(h4))

                if self.invoice_list:

                    for key, values in OrderedDict(reversed(list(self.invoice_list_copy.items()))).items():
                        if key == vars.ITEM_ID:
                            item_id = key
                            total_qty = len(values)
                            colors = {}
                            item_price = 0
                            color_string = []
                            memo_string = []
                            if values:
                                for item in values:
                                    item_name = item['item_name']
                                    item_type = item['type']
                                    item_color = item['color']
                                    item_memo = item['memo']
                                    item_price += item['item_price'] if item['item_price'] else 0
                                    if item['color']:
                                        if item_color in colors:
                                            colors[item_color] += 1
                                        else:
                                            colors[item_color] = 1
                                    if item_memo:
                                        regexed_memo = item_memo.replace('"', '**Inch(es)')
                                        memo_string.append(regexed_memo)
                                if colors:
                                    for color_name, color_amount in colors.items():
                                        if color_name:
                                            color_string.append('{}-{}'.format(color_amount, color_name))

                                item_string = '[b]{}[/b] \n{}\n{}'.format(item_name, ', '.join(color_string),
                                                                          '/ '.join(memo_string))
                                tr1 = Button(size_hint_x=0.1,
                                             markup=True,
                                             text='{}'.format(item_type),
                                             on_release=partial(self.adjustment_calculator,
                                                                1,
                                                                item_price))
                                tr2 = Button(size_hint_x=0.1,
                                             markup=True,
                                             text='{}'.format(total_qty),
                                             on_release=partial(self.adjustment_calculator,
                                                                1,
                                                                item_price))
                                tr3 = Factory.LongButton(size_hint_x=0.6,
                                                         size_hint_y=None,
                                                         markup=True,
                                                         text='{}'.format(item_string),
                                                         on_release=partial(self.adjustment_calculator,
                                                                            1,
                                                                            item_price))

                                tr4 = Button(size_hint_x=0.2,
                                             markup=True,
                                             text='{}'.format(vars.us_dollar(item_price)),
                                             on_release=partial(self.adjustment_calculator,
                                                                1,
                                                                item_price))

                                self.adjust_sum_grid.add_widget(tr1)
                                self.adjust_sum_grid.add_widget(tr2)
                                self.adjust_sum_grid.add_widget(tr3)
                                self.adjust_sum_grid.add_widget(tr4)

    def make_adjustment_individual_table(self):
        self.adjust_individual_grid.clear_widgets()
        # create th
        h1 = KV.sized_invoice_tr(0, 'Type', size_hint_x=0.1)
        h2 = KV.sized_invoice_tr(0, 'Qty', size_hint_x=0.1)
        h3 = KV.sized_invoice_tr(0, 'Item', size_hint_x=0.5)
        h4 = KV.sized_invoice_tr(0, 'Subtotal', size_hint_x=0.2)
        h5 = KV.sized_invoice_tr(0, 'A', size_hint_x=0.1)
        self.adjust_individual_grid.add_widget(Builder.load_string(h1))
        self.adjust_individual_grid.add_widget(Builder.load_string(h2))
        self.adjust_individual_grid.add_widget(Builder.load_string(h3))
        self.adjust_individual_grid.add_widget(Builder.load_string(h4))
        self.adjust_individual_grid.add_widget(Builder.load_string(h5))

        if self.invoice_list:

            for key, values in OrderedDict(reversed(list(self.invoice_list_copy.items()))).items():
                if key == vars.ITEM_ID:
                    idx = -1
                    for item in values:
                        idx += 1
                        item_name = item['item_name']
                        item_type = item['type']
                        item_color = item['color']
                        item_memo = item['memo']
                        item_price = item['item_price'] if item['item_price'] else 0
                        item_string = '[b]{}[/b] \n{}\n{}'.format(item_name, item_color, item_memo)
                        background_color = (
                            0.36862745, 0.36862745, 0.36862745, 1) if idx == self.item_selected_row else (
                            0.89803922, 0.89803922, 0.89803922, 1)
                        background_normal = ''
                        text_color = 'e5e5e5' if idx == self.item_selected_row else '000000'

                        tr1 = Button(size_hint_x=0.1,
                                     markup=True,
                                     text='[color={text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                     msg=item_type),
                                     on_press=partial(self.item_row_adjusted_selected, idx),
                                     on_release=partial(self.adjustment_calculator,
                                                        2,
                                                        item_price,
                                                        idx),
                                     background_color=background_color,
                                     background_normal=background_normal)
                        tr2 = Button(size_hint_x=0.1,
                                     markup=True,
                                     text='[color={text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                     msg=1),
                                     on_press=partial(self.item_row_adjusted_selected, idx),
                                     on_release=partial(self.adjustment_calculator,
                                                        2,
                                                        item_price,
                                                        idx),
                                     background_color=background_color,
                                     background_normal=background_normal)
                        tr3 = Factory.LongButton(size_hint_x=0.6,
                                                 size_hint_y=None,
                                                 markup=True,
                                                 text='[color={text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                                 msg=item_string),
                                                 on_press=partial(self.item_row_adjusted_selected, idx),
                                                 on_release=partial(self.adjustment_calculator,
                                                                    2,
                                                                    item_price,
                                                                    idx),
                                                 background_color=background_color,
                                                 background_normal=background_normal)
                        tr4 = Button(size_hint_x=0.2,
                                     markup=True,
                                     text='[color={text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                     msg=vars.us_dollar(item_price)),
                                     on_press=partial(self.item_row_adjusted_selected, idx),
                                     on_release=partial(self.adjustment_calculator,
                                                        2,
                                                        item_price,
                                                        idx),
                                     background_color=background_color,
                                     background_normal=background_normal)

                        tr5 = Button(size_hint_x=0.1,
                                     markup=True,
                                     text='[color=ffffff][b]-[/b][/color]',
                                     on_release=partial(self.item_row_delete_selected, idx),
                                     background_color=(1, 0, 0, 1),
                                     background_normal='')

                        self.adjust_individual_grid.add_widget(tr1)
                        self.adjust_individual_grid.add_widget(tr2)
                        self.adjust_individual_grid.add_widget(tr3)
                        self.adjust_individual_grid.add_widget(tr4)
                        self.adjust_individual_grid.add_widget(tr5)

    def adjustment_calculator(self, type=None, price=0, row=None, *args, **kwargs):
        self.adjust_price = 0
        self.adjust_price_list = []
        popup = Popup()
        popup.title = 'Adjustment Calculator'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.9))
        calculator_layout = BoxLayout(orientation='vertical',
                                      size_hint=(0.5, 1))
        calculator_top = GridLayout(cols=1,
                                    rows=1,
                                    size_hint=(1, 0.2))
        self.calculator_text = Factory.CenteredLabel(text="[color=000000][b]{}[/b][/color]".format(vars.us_dollar(0)))
        calculator_top.add_widget(self.calculator_text)
        calculator_main_layout = GridLayout(cols=3,
                                            rows=4,
                                            size_hint=(1, 0.8))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]7[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '7')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]8[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '8')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]9[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '9')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]4[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '4')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]5[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '5')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]6[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '6')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]1[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '1')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]2[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '2')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]3[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '3')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]0[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '0')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]00[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '00')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[color=ff0000][b]C[/b][/color]",
                                                 on_release=partial(self.set_price_adjustment_sum, 'C')))
        calculator_layout.add_widget(calculator_top)
        calculator_layout.add_widget(calculator_main_layout)
        summary_layout = BoxLayout(orientation='vertical',
                                   size_hint=(0.5, 1))
        summary_layout.add_widget(Label(markup=True,
                                        text="[b]Summary Totals[/b]",
                                        size_hint=(1, 0.1)))
        summary_grid = GridLayout(size_hint=(1, 0.9),
                                  cols=2,
                                  rows=2,
                                  row_force_default=True,
                                  row_default_height='50sp')
        summary_grid.add_widget(Label(markup=True,
                                      text="Original Price"))
        original_price = Factory.ReadOnlyLabel(text='[color=e5e5e5]{}[/color]'.format(vars.us_dollar(price)))
        summary_grid.add_widget(original_price)
        summary_grid.add_widget(Label(markup=True,
                                      text="Adjusted Price"))
        self.adjusted_price = Factory.ReadOnlyLabel(
            text='[color=e5e5e5]{}[/color]'.format(vars.us_dollar(self.adjust_price)))
        summary_grid.add_widget(self.adjusted_price)
        summary_layout.add_widget(summary_grid)

        inner_layout_1.add_widget(calculator_layout)
        inner_layout_1.add_widget(summary_layout)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(markup=True,
                                         text="cancel",
                                         on_release=popup.dismiss))

        inner_layout_2.add_widget(Button(markup=True,
                                         text="[color=00f900][b]OK[/b][/color]",
                                         on_press=self.set_price_adjustment_sum_correct_individual if type == 1 else partial(
                                             self.set_price_adjustment_individual_correct_sum, row),
                                         on_release=popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def set_price_adjustment_sum(self, digit, *args, **kwargs):
        if digit == 'C':
            self.adjust_price = 0
            self.adjust_price_list = []

        else:
            self.adjust_price_list.append(digit)
            self.adjust_price = int(''.join(self.adjust_price_list)) / 100
        self.calculator_text.text = '[color=000000][b]{}[/b][/color]'.format(vars.us_dollar(self.adjust_price))
        self.adjusted_price.text = '[color=e5e5e5][b]{}[/b][/color]'.format(vars.us_dollar(self.adjust_price))

    def set_price_adjustment_sum_correct_individual(self, row, *args, **kwargs):
        if vars.ITEM_ID in self.invoice_list_copy:
            total_count = len(self.invoice_list_copy[vars.ITEM_ID])
            new_avg_price = round(self.adjust_price / total_count, 2)
            minus_total = self.adjust_price
            idx = -1
            for items in self.invoice_list_copy[vars.ITEM_ID]:
                idx += 1
                minus_total -= new_avg_price
                if idx < len(self.invoice_list_copy[vars.ITEM_ID]) - 1:
                    self.invoice_list_copy[vars.ITEM_ID][idx]['item_price'] = new_avg_price
                else:
                    self.invoice_list_copy[vars.ITEM_ID][idx]['item_price'] = round(new_avg_price + minus_total, 2)
            self.make_adjustment_sum_table()
            self.make_adjustment_individual_table()

    def set_price_adjustment_individual_correct_sum(self, row, *args, **kwargs):
        if vars.ITEM_ID in self.invoice_list_copy:
            self.invoice_list_copy[vars.ITEM_ID][row]['item_price'] = self.adjust_price
            self.make_adjustment_sum_table()
            self.make_adjustment_individual_table()

    def save_price_adjustment(self, *args, **kwargs):
        if vars.ITEM_ID in self.invoice_list_copy:
            idx = -1
            for items in self.invoice_list_copy[vars.ITEM_ID]:
                idx += 1
                new_price = items['item_price']
                self.invoice_list[vars.ITEM_ID][idx]['item_price'] = new_price
            self.create_summary_table()
            self.create_summary_totals()

    def item_row_delete_selected(self, row, *args, **kwargs):
        del self.invoice_list[vars.ITEM_ID][row]
        del self.invoice_list_copy[vars.ITEM_ID][row]
        self.item_selected_row = 0
        self.make_adjustment_sum_table()
        self.make_adjustment_individual_table()
        self.create_summary_table()
        self.create_summary_totals()

    def item_row_adjusted_selected(self, row, *args, **kwargs):
        self.item_selected_row = row
        self.adjust_individual_grid.clear_widgets()
        self.make_adjustment_individual_table()

    def make_calendar(self):

        store_hours = Company().get_store_hours(vars.COMPANY_ID)
        today = datetime.datetime.today()
        dow = int(datetime.datetime.today().strftime("%w"))
        turn_around_day = int(store_hours[dow]['turnaround']) if store_hours[dow]['turnaround'] else 0
        turn_around_hour = store_hours[dow]['due_hour'] if store_hours[dow]['due_hour'] else '4'
        turn_around_minutes = store_hours[dow]['due_minutes'] if store_hours[dow]['due_minutes'] else '00'
        turn_around_ampm = store_hours[dow]['due_ampm'] if store_hours[dow]['due_ampm'] else 'pm'
        new_date = today + datetime.timedelta(days=turn_around_day)
        date_string = '{} {}:{}:00'.format(new_date.strftime("%Y-%m-%d"),
                                           turn_around_hour if turn_around_ampm == 'am' else int(turn_around_hour) + 12,
                                           turn_around_minutes)
        due_date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        self.month = int(due_date.strftime('%m'))

        popup = Popup()
        popup.title = 'Calendar'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(size_hint=(1, 0.9),
                                   orientation='vertical')
        calendar_selection = GridLayout(cols=4,
                                        rows=1,
                                        size_hint=(1, 0.1))
        prev_month = Button(markup=True,
                            text="<",
                            font_size="30sp",
                            on_release=self.prev_month)
        next_month = Button(markup=True,
                            text=">",
                            font_size="30sp",
                            on_release=self.next_month)
        select_month = Factory.SelectMonth()
        self.month_button = Button(text='{}'.format(vars.month_by_number(self.month)),
                                   on_release=select_month.open)
        for index in range(12):
            month_options = Button(text='{}'.format(vars.month_by_number(index)),
                                   size_hint_y=None,
                                   height=40,
                                   on_release=partial(self.select_calendar_month, index))
            select_month.add_widget(month_options)

        select_month.on_select = lambda instance, x: setattr(self.month_button, 'text', x)
        select_year = Factory.SelectMonth()

        self.year_button = Button(text="{}".format(self.year),
                                  on_release=select_year.open)
        for index in range(10):
            year_options = Button(text='{}'.format(int(self.year) + index),
                                  size_hint_y=None,
                                  height=40,
                                  on_release=partial(self.select_calendar_year, index))
            select_year.add_widget(year_options)

        select_year.bind(on_select=lambda instance, x: setattr(self.year_button, 'text', x))
        calendar_selection.add_widget(prev_month)
        calendar_selection.add_widget(self.month_button)
        calendar_selection.add_widget(self.year_button)
        calendar_selection.add_widget(next_month)
        self.calendar_layout = GridLayout(cols=7,
                                          rows=8,
                                          size_hint=(1, 0.9))
        self.create_calendar_table()

        inner_layout_1.add_widget(calendar_selection)
        inner_layout_1.add_widget(self.calendar_layout)
        inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                   orientation='horizontal')
        inner_layout_2.add_widget(Button(markup=True,
                                         text="Okay",
                                         on_release=popup.dismiss))

        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def create_calendar_table(self):
        # set the variables

        store_hours = Company().get_store_hours(vars.COMPANY_ID)
        today_date = datetime.datetime.today()
        today_string = today_date.strftime('%Y-%m-%d 00:00:00')
        check_today = datetime.datetime.strptime(today_string, "%Y-%m-%d %H:%M:%S").timestamp()
        due_date_string = self.due_date.strftime('%Y-%m-%d 00:00:00')
        check_due_date = datetime.datetime.strptime(due_date_string, "%Y-%m-%d %H:%M:%S").timestamp()

        self.calendar_layout.clear_widgets()
        calendars = Calendar()
        calendars.setfirstweekday(calendar.SUNDAY)
        selected_month = self.month - 1
        year_dates = calendars.yeardays2calendar(year=self.year, width=1)
        th1 = KV.invoice_tr(0, 'Su')
        th2 = KV.invoice_tr(0, 'Mo')
        th3 = KV.invoice_tr(0, 'Tu')
        th4 = KV.invoice_tr(0, 'We')
        th5 = KV.invoice_tr(0, 'Th')
        th6 = KV.invoice_tr(0, 'Fr')
        th7 = KV.invoice_tr(0, 'Sa')
        self.calendar_layout.add_widget(Builder.load_string(th1))
        self.calendar_layout.add_widget(Builder.load_string(th2))
        self.calendar_layout.add_widget(Builder.load_string(th3))
        self.calendar_layout.add_widget(Builder.load_string(th4))
        self.calendar_layout.add_widget(Builder.load_string(th5))
        self.calendar_layout.add_widget(Builder.load_string(th6))
        self.calendar_layout.add_widget(Builder.load_string(th7))
        if year_dates[selected_month]:
            for month in year_dates[selected_month]:
                for week in month:
                    for day in week:
                        if day[0] > 0:
                            check_date_string = '{}-{}-{} 00:00:00'.format(self.year,
                                                                           Job.date_leading_zeroes(self.month),
                                                                           Job.date_leading_zeroes(day[0]))
                            today_base = datetime.datetime.strptime(check_date_string, "%Y-%m-%d %H:%M:%S")
                            check_date = today_base.timestamp()
                            dow_check = today_base.strftime("%w")
                            # rule #1 remove all past dates so users cannot set a due date previous to today
                            if check_date < check_today:
                                item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                              disabled=True)
                            elif int(store_hours[int(dow_check)]['status']) > 1:  # check to see if business is open
                                if check_date == check_today:
                                    item = Factory.CalendarButton(text="[color=37FDFC][b]{}[/b][/color]".format(day[0]),
                                                                  background_color=(0, 0.50196078, 0.50196078, 1),
                                                                  background_normal='',
                                                                  on_release=partial(self.select_due_date, today_base))
                                elif check_date == check_due_date:
                                    item = Factory.CalendarButton(text="[color=008080][b]{}[/b][/color]".format(day[0]),
                                                                  background_color=(
                                                                      0.2156862, 0.9921568, 0.98823529, 1),
                                                                  background_normal='',
                                                                  on_release=partial(self.select_due_date, today_base))
                                elif check_today < check_date < check_due_date:
                                    item = Factory.CalendarButton(text="[color=008080][b]{}[/b][/color]".format(day[0]),
                                                                  background_color=(0.878431372549020, 1, 1, 1),
                                                                  background_normal='',
                                                                  on_release=partial(self.select_due_date, today_base))
                                else:
                                    item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                                  on_release=partial(self.select_due_date, today_base))
                            else:  # store is closed
                                item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                              disabled=True)
                        else:
                            item = Factory.CalendarButton(disabled=True)
                        self.calendar_layout.add_widget(item)

    def prev_month(self, *args, **kwargs):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.month_button.text = '{}'.format(vars.month_by_number(self.month))
        self.year_button.text = '{}'.format(self.year)
        self.create_calendar_table()

    def next_month(self, *args, **kwargs):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.month_button.text = '{}'.format(vars.month_by_number(self.month))
        self.year_button.text = '{}'.format(self.year)
        self.create_calendar_table()

    def select_calendar_month(self, month, *args, **kwargs):
        self.month = month
        self.create_calendar_table()

    def select_calendar_year(self, year, *args, **kwargs):
        self.year = year
        self.create_calendar_table()

    def select_due_date(self, selected_date, *args, **kwargs):
        store_hours = Company().get_store_hours(vars.COMPANY_ID)

        dow = int(selected_date.strftime("%w"))
        turn_around_hour = store_hours[dow]['due_hour'] if store_hours[dow]['due_hour'] else '4'
        turn_around_minutes = store_hours[dow]['due_minutes'] if store_hours[dow]['due_minutes'] else '00'
        turn_around_ampm = store_hours[dow]['due_ampm'] if store_hours[dow]['due_ampm'] else 'pm'
        date_string = '{} {}:{}:00'.format(selected_date.strftime("%Y-%m-%d"),
                                           turn_around_hour if turn_around_ampm == 'am' else int(turn_around_hour) + 12,
                                           turn_around_minutes)
        self.due_date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        self.due_date_string = '{}'.format(self.due_date.strftime('%a %m/%d %I:%M%p'))
        self.date_picker.text = self.due_date_string
        self.create_calendar_table()

    def print_selection(self):
        self.print_popup = Popup()
        self.print_popup.title = 'Print Selection'
        self.print_popup.size_hint = (None, None)
        self.print_popup.size = (800, 600)
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.7))
        button_1 = Factory.PrintButton(text='Cust. + Store',
                                       on_release=partial(self.wait_popup, 'both'))

        inner_layout_1.add_widget(button_1)
        button_2 = Factory.PrintButton(text='Store Only',
                                       on_release=partial(self.wait_popup, 'store'))

        inner_layout_1.add_widget(button_2)
        button_3 = Factory.PrintButton(text='No Print',
                                       on_release=partial(self.wait_popup, 'none'))

        inner_layout_1.add_widget(button_3)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.3))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='Cancel',
                                         on_release=self.print_popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.print_popup.content = layout
        self.print_popup.open()

    def wait_popup(self, type, *args, **kwargs):
        SYNC_POPUP.title = 'Syncing Data'
        content = KV.popup_alert("Syncing data to server, please wait...")
        SYNC_POPUP.content = Builder.load_string(content)
        SYNC_POPUP.open()
        Clock.schedule_once(partial(self.finish_invoice, type))

    def finish_invoice(self, type, *args, **kwargs):
        vars.CUSTOMER_ID = self.customer_id_backup
        self.set_result_status()
        self.now = datetime.datetime.now()
        # determine the types of invoices we need to print
        # set the printer data
        laundry_to_print = []
        printers = Printer()
        thermal_printers = printers.get_printer_ids(vars.COMPANY_ID, 1)

        # splt up invoice by inventory group
        save_invoice = {}
        save_totals = {}
        save_invoice_items = {}
        inventories = Inventory().where({'company_id': vars.COMPANY_ID})
        if inventories:
            for inventory in inventories:
                # iterate through the newly created invoice list and group each inventory id into one invoice
                inventory_id = inventory['inventory_id']
                save_invoice[inventory_id] = []
                save_totals[inventory_id] = {'quantity': 0,
                                             'tags': 0,
                                             'subtotal': 0,
                                             'tax': 0,
                                             'discount': 0,
                                             'total': 0}
                for invoice_item_key, invoice_item_value in self.invoice_list.items():
                    for iivalue in invoice_item_value:
                        if inventory_id == iivalue['inventory_id']:
                            save_invoice[inventory_id].append(iivalue)
                            save_totals[inventory_id]['quantity'] += iivalue['qty']
                            save_totals[inventory_id]['tags'] += iivalue['tags']
                            save_totals[inventory_id]['subtotal'] += iivalue['item_price']
                            save_totals[inventory_id]['discount'] += 0

        if save_invoice:
            print_sync_invoice = {}  # if synced to server
            print_sync_totals = {}
            print_invoice = {}  # if not synced to server
            print_totals = {}
            for inventory_id, invoice_group in save_invoice.items():
                if inventory_id in save_invoice:
                    inventory_discount = 0
                    if len(save_invoice[inventory_id]) > 0:
                        # calculate discounts if any
                        discounts = Discount().where({'company_id': vars.COMPANY_ID,
                                                      'start_date': {'<=': '"{}"'.format(self.now)},
                                                      'end_date': {'>=': '"{}"'.format(self.now)},
                                                      'inventory_id': inventory_id});
                        if discounts:
                            for discount in discounts:
                                discount_rate = float(discount['rate'])
                                discount_price = float(discount['discount'])
                                inventory_discount_id = discount['discount_id']
                                if discount_rate > 0:
                                    inventory_discount = (float(save_totals[inventory_id]['subtotal'] * discount_rate))
                                elif discount_rate is 0 and discount_price > 0:
                                    inventory_discount = (float(save_totals[inventory_id]['subtotal']) - discount_price)
                                else:
                                    inventory_discount = 0


                        tax_amount = (save_totals[inventory_id]['subtotal'] - inventory_discount) * vars.TAX_RATE

                        total = (save_totals[inventory_id]['subtotal'] - inventory_discount) + tax_amount

                        # set invoice data to save
                        new_invoice = Invoice()
                        new_invoice.company_id = vars.COMPANY_ID
                        new_invoice.customer_id = self.customer_id_backup
                        new_invoice.quantity = save_totals[inventory_id]['quantity']
                        new_invoice.pretax = float('%.2f' % (save_totals[inventory_id]['subtotal']))
                        if self.discount_id is not None:
                            new_invoice.discount_id = self.discount_id
                        new_invoice.tax = float('%.2f' % (tax_amount))
                        new_invoice.total = float('%.2f' % (total))
                        new_invoice.due_date = '{}'.format(self.due_date.strftime("%Y-%m-%d %H:%M:%S"))
                        new_invoice.status = 1
                        # save to local db
                        if new_invoice.add():
                            last_insert_id = new_invoice.get_last_insert_id()
                            print_totals[last_insert_id] = {
                                'quantity': new_invoice.quantity,
                                'subtotal': new_invoice.pretax,
                                'discount': float('%.2f' % (inventory_discount)),
                                'tax': new_invoice.tax,
                                'total': new_invoice.total
                            }
                            save_invoice_items[last_insert_id] = invoice_group
                            idx = -1
                            colors = {}
                            print_invoice[last_insert_id] = {}
                            for iis in save_invoice_items[last_insert_id]:
                                item_id = save_invoice_items[last_insert_id][idx]['item_id']
                                colors[item_id] = {}
                            for inv_items in save_invoice_items[last_insert_id]:
                                idx += 1
                                save_invoice_items[last_insert_id][idx]['status'] = 3
                                save_invoice_items[last_insert_id][idx]['invoice_id'] = last_insert_id
                                save_invoice_items[last_insert_id][idx]['inventory_id'] = inventory_id
                                item_id = save_invoice_items[last_insert_id][idx]['item_id']
                                item_name = save_invoice_items[last_insert_id][idx]['item_name']
                                item_price = save_invoice_items[last_insert_id][idx]['item_price']
                                item_type = save_invoice_items[last_insert_id][idx]['type']
                                item_color = save_invoice_items[last_insert_id][idx]['color']
                                item_memo = save_invoice_items[last_insert_id][idx]['memo']
                                if item_id in colors:
                                    if item_color in colors[item_id]:
                                        colors[item_id][item_color] += 1
                                    else:
                                        colors[item_id][item_color] = 1
                                if last_insert_id in print_invoice:
                                    if item_id in print_invoice[last_insert_id]:
                                        print_invoice[last_insert_id][item_id]['item_price'] += item_price
                                        print_invoice[last_insert_id][item_id]['qty'] += 1
                                        if item_id in colors:
                                            print_invoice[last_insert_id][item_id]['colors'] = colors[item_id]
                                        else:
                                            print_invoice[last_insert_id][item_id]['colors'] = []
                                        if item_memo:
                                            print_invoice[last_insert_id][item_id]['memos'].append(item_memo)
                                    else:

                                        print_invoice[last_insert_id][item_id] = {
                                            'item_id': item_id,
                                            'type': item_type,
                                            'name': item_name,
                                            'item_price': item_price,
                                            'qty': 1,
                                            'memos': [item_memo] if item_memo else [],
                                            'colors': colors[item_id] if item_id in colors else []
                                        }

            # save the invoices to the db and return the proper invoice_ids
            run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
            try:
                run_sync.start()
            finally:
                run_sync.join()
                print('sync now finished')
                for id in save_invoice_items:
                    invoices = Invoice().where({'id': id})
                    if invoices:
                        for invoice in invoices:
                            new_invoice_id = invoice['invoice_id']
                            idx = -1
                            colors = {}
                            discount_id = invoice['discount_id']
                            invoice_discount = 0
                            if discount_id is not None:
                                # calculate discounts if any
                                discounts = Discount().where({'discount_id':discount_id});
                                if discounts:
                                    for discount in discounts:
                                        discount_rate = float(discount['rate'])
                                        discount_price = float(discount['discount'])
                                        inventory_discount_id = discount['discount_id']
                                        if discount_rate > 0:
                                            invoice_discount = (
                                            float(invoice['pretax'] * discount_rate))
                                        elif discount_rate is 0 and discount_price > 0:
                                            invoice_discount = (
                                            float(invoice['pretax']) - discount_price)
                                        else:
                                            invoice_discount = 0
                            print_sync_totals[new_invoice_id] = {
                                'quantity': invoice['quantity'],
                                'subtotal': invoice['pretax'],
                                'discount': vars.us_dollar(invoice_discount),
                                'tax': invoice['tax'],
                                'total': invoice['total']
                            }
                            print_sync_invoice[new_invoice_id] = {}
                            for items in save_invoice_items[id]:
                                item_id = items['item_id']
                                colors[item_id] = {}
                            for items in save_invoice_items[id]:
                                idx += 1
                                save_invoice_items[id][idx]['invoice_id'] = new_invoice_id
                                save_invoice_items[id][idx]['status'] = 1
                                item_id = items['item_id']
                                item_name = items['item_name']
                                item_price = items['item_price']
                                item_type = items['type']
                                item_color = items['color']
                                item_memo = items['memo']
                                if item_id in colors:
                                    if item_color in colors[item_id]:
                                        colors[item_id][item_color] += 1
                                    else:
                                        colors[item_id][item_color] = 1
                                if new_invoice_id in print_sync_invoice:
                                    if item_id in print_sync_invoice[new_invoice_id]:

                                        print_sync_invoice[new_invoice_id][item_id]['item_price'] += item_price
                                        print_sync_invoice[new_invoice_id][item_id]['qty'] += 1
                                        if item_memo:
                                            print_sync_invoice[new_invoice_id][item_id]['memos'].append(item_memo)
                                        if item_id in colors:
                                            print_sync_invoice[new_invoice_id][item_id]['colors'] = colors[item_id]
                                        else:
                                            print_sync_invoice[new_invoice_id][item_id]['colors'] = []
                                    else:
                                        print_sync_invoice[new_invoice_id][item_id] = {
                                            'item_id': item_id,
                                            'type': item_type,
                                            'name': item_name,
                                            'item_price': item_price,
                                            'qty': 1,
                                            'memos': [item_memo] if item_memo else [],
                                            'colors': {item_color: 1}
                                        }

            if len(save_invoice_items) > 0:
                for iitems_id in save_invoice_items:
                    for item in save_invoice_items[iitems_id]:
                        item_price = float(item['item_price']) if item['item_price'] else 0
                        item_tax = float('%.2f' % (item_price * vars.TAX_RATE))
                        item_total = float('%.2f' % (item_price * (1 + vars.TAX_RATE)))
                        # set invoice data to save
                        new_invoice_item = InvoiceItem()
                        new_invoice_item.company_id = vars.COMPANY_ID
                        new_invoice_item.customer_id = self.customer_id_backup
                        new_invoice_item.invoice_id = item['invoice_id']
                        new_invoice_item.item_id = item['item_id']
                        new_invoice_item.inventory_id = item['inventory_id']
                        new_invoice_item.quantity = item['qty']
                        new_invoice_item.color = item['color']
                        new_invoice_item.memo = item['memo']
                        new_invoice_item.pretax = item_price
                        new_invoice_item.tax = item_tax
                        new_invoice_item.total = item_total
                        new_invoice_item.status = item['status']
                        # save to local db
                        if new_invoice_item.add():
                            print('saved invoice item')
            # set invoice_items data to save
            run_sync2 = threading.Thread(target=SYNC.db_sync, args=[vars.COMPANY_ID])
            try:
                run_sync2.start()
            finally:
                run_sync2.join()



                self.print_popup.dismiss()
                t1 = Thread(target=self.print_function, args=[type,
                                                              print_invoice,
                                                              print_totals,
                                                              print_sync_invoice,
                                                              print_sync_totals])
                t1.start()
            SYNC_POPUP.dismiss()


    def print_function(self,type, print_invoice, print_totals, print_sync_invoice, print_sync_totals, *args, **kwargs):
        print('sync invoice items now finished')
        companies = Company()
        comps = companies.where({'company_id': vars.COMPANY_ID}, set=True)
        pr = Printer()
        if comps:
            for company in comps:
                companies.id = company['id']
                companies.company_id = company['company_id']
                companies.name = company['name']
                companies.street = company['street']
                companies.suite = company['suite']
                companies.city = company['city']
                companies.state = company['state']
                companies.zip = company['zip']
                companies.email = company['email']
                companies.phone = company['phone']
        customers = User()
        custs = customers.where({'user_id': '{}'.format(self.customer_id_backup)}, set=True)
        if custs:
            for user in custs:
                customers.id = user['id']
                customers.user_id = user['user_id']
                customers.company_id = user['company_id']
                customers.username = user['username']
                customers.first_name = user['first_name'].upper() if user['first_name'] else ''
                customers.last_name = user['last_name'].upper() if user['last_name'] else ''
                customers.street = user['street']
                customers.suite = user['suite']
                customers.city = user['city']
                customers.state = user['state']
                customers.zipcode = user['zipcode']
                customers.email = user['email']
                customers.phone = user['phone']
                customers.intercom = user['intercom']
                customers.concierge_name = user['concierge_name']
                customers.concierge_number = user['concierge_number']
                customers.special_instructions = user['special_instructions']
                customers.shirt_old = user['shirt_old']
                customers.shirt = user['shirt']
                customers.delivery = user['delivery']
                customers.profile_id = user['profile_id']
                customers.payment_status = user['payment_status']
                customers.payment_id = user['payment_id']
                customers.token = user['token']
                customers.api_token = user['api_token']
                customers.reward_status = user['reward_status']
                customers.reward_points = user['reward_points']
                customers.account = user['account']
                customers.starch = user['starch']
                customers.important_memo = user['important_memo']
                customers.invoice_memo = user['invoice_memo']
                customers.password = user['password']
                customers.role_id = user['role_id']
                customers.remember_token = user['remember_token']
        # print invoices
        if vars.EPSON:
            if type is 'both':  # print customer copy

                # CENTER ALIGN
                vars.EPSON.write(pr.pcmd('TXT_ALIGN_CT'))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                density=5, invert=False, smooth=False, flip=False))
                vars.EPSON.write("::CUSTOMER::\n")

                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                invert=False, smooth=False, flip=False))

                vars.EPSON.write("{}\n".format(companies.name))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write("{}\n".format(companies.street))
                vars.EPSON.write("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))

                vars.EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
                vars.EPSON.write("{}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                invert=False, smooth=False, flip=False))
                padded_customer_id = '{0:05d}'.format(self.customer_id_backup)
                vars.EPSON.write("{}\n".format(padded_customer_id))

                # Print barcode
                vars.EPSON.write(pr.pcmd_barcode(str(padded_customer_id)))

                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('{}, {}\n'.format(customers.last_name, customers.first_name))

                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('{}\n'.format(Job.make_us_phone(customers.phone)))
                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('-----------------------------------------\n')

                # display invoice details
                if self.invoice_list:

                    for key, values in OrderedDict(reversed(list(self.invoice_list.items()))).items():
                        total_qty = len(values)
                        colors = {}
                        item_price = 0
                        color_string = []
                        memo_string = []
                        if values:
                            for item in values:
                                item_name = item['item_name']
                                item_type = item['type']
                                item_color = item['color']
                                item_memo = item['memo']
                                item_price += item['item_price'] if item['item_price'] else 0
                                if item['color']:
                                    if item_color in colors:
                                        colors[item_color] += 1
                                    else:
                                        colors[item_color] = 1
                                if item_memo:
                                    regexed_memo = item_memo.replace('"', '**Inch(es)')
                                    memo_string.append(regexed_memo)
                            if colors:
                                for color_name, color_amount in colors.items():
                                    if color_name:
                                        color_string.append('{}-{}'.format(color_amount, color_name))

                            vars.EPSON.write(
                                pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=5, invert=False, smooth=False, flip=False))
                            vars.EPSON.write('{} {}   '.format(item_type, total_qty, item_name))
                            vars.EPSON.write(
                                pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'B', width=1, height=1,
                                            density=5, invert=False, smooth=False, flip=False))
                            vars.EPSON.write('{}\n'.format(item_name))
                            if len(memo_string) > 0:

                                vars.EPSON.write(
                                    pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                height=1,
                                                density=5, invert=False, smooth=False, flip=False))
                                vars.EPSON.write('     {}\n'.format('/ '.join(memo_string)))
                            if len(color_string):

                                vars.EPSON.write(
                                    pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                height=1, density=5, invert=False, smooth=False, flip=False))
                                vars.EPSON.write('     {}\n'.format(', '.join(color_string)))

                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('-----------------------------------------\n')
                vars.EPSON.write(
                    pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('{} PCS\n'.format(self.quantity))
                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('-----------------------------------------\n')
                # Cut paper
                vars.EPSON.write('\n\n\n\n\n\n')
                vars.EPSON.write(pr.pcmd('PARTIAL_CUT'))

            # Print store copies (ALWAYS)
            if print_sync_invoice:  # if invoices synced
                for invoice_id, item_id in print_sync_invoice.items():

                    # start invoice
                    vars.EPSON.write(pr.pcmd('TXT_ALIGN_CT'))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                    density=5, invert=False, smooth=False, flip=False))
                    vars.EPSON.write("::STORE::\n")
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2,
                                    density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write("{}\n".format(companies.name))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                    density=5, invert=False, smooth=False, flip=False))
                    vars.EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
                    vars.EPSON.write("{}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2,
                                    density=5, invert=False, smooth=False, flip=False))
                    vars.EPSON.write(
                        "READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4,
                                    density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write("{}\n".format('{0:06d}'.format(invoice_id)))
                    # Print barcode
                    vars.EPSON.write(pr.pcmd_barcode('{}'.format('{0:06d}'.format(invoice_id))))

                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3,
                                    density=6, invert=False, smooth=False, flip=False))

                    vars.EPSON.write(
                        '{}, {}\n'.format(customers.last_name, customers.first_name))

                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                    density=2, invert=False, smooth=False, flip=False))
                    vars.EPSON.write('{}\n'.format(Job.make_us_phone(customers.phone)))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                    density=1, invert=False, smooth=False, flip=False))
                    vars.EPSON.write('-----------------------------------------\n')
                    if invoice_id in print_sync_invoice:
                        for item_id, invoice_item in print_sync_invoice[invoice_id].items():
                            item_name = invoice_item['name']
                            item_price = invoice_item['item_price']
                            item_qty = invoice_item['qty']
                            item_color_string = []
                            item_memo = invoice_item['memos']
                            item_type = invoice_item['type']
                            if invoice_item['colors']:
                                for color_name, color_qty in invoice_item['colors'].items():
                                    if color_name:
                                        item_color_string.append('{}-{}'.format(color_qty, color_name))
                            string_length = len(item_type) + len(str(item_qty)) + len(item_name) + len(
                                vars.us_dollar(item_price)) + 4
                            string_offset = 42 - string_length if 42 - string_length > 0 else 0
                            vars.EPSON.write('{} {}   {}{}{}\n'.format(item_type,
                                                                       item_qty,
                                                                       item_name,
                                                                       ' ' * string_offset,
                                                                       vars.us_dollar(item_price)))

                            # vars.EPSON.write('\r\x1b@\x1b\x61\x02{}\n'.format(vars.us_dollar(item_price)))
                            if len(item_memo) > 0:
                                vars.EPSON.write(
                                    pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                height=1, density=5, invert=False, smooth=False,
                                                flip=False))
                                vars.EPSON.write('     {}\n'.format('/ '.join(item_memo)))
                            if len(item_color_string) > 0:
                                vars.EPSON.write(
                                    pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                height=1, density=5, invert=False, smooth=False,
                                                flip=False))
                                vars.EPSON.write('     {}\n'.format(', '.join(item_color_string)))

                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                    density=1, invert=False, smooth=False, flip=False))
                    vars.EPSON.write('-----------------------------------------\n')
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3,
                                    density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('{} PCS\n'.format(print_sync_totals[invoice_id]['quantity']))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                    density=1, invert=False, smooth=False, flip=False))
                    vars.EPSON.write('-----------------------------------------\n')
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('    SUBTOTAL:')
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    string_length = len(vars.us_dollar(print_sync_totals[invoice_id]['subtotal']))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write('{}{}\n'.format(' ' * string_offset,
                                                     vars.us_dollar(
                                                         print_sync_totals[invoice_id]['subtotal'])))
                    vars.EPSON.write('    DISCOUNT:')
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    string_length = len(vars.us_dollar(print_sync_totals[invoice_id]['discount']))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write('{}({})\n'.format(' ' * string_offset,
                                                     vars.us_dollar(print_sync_totals[invoice_id]['discount'])))
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    vars.EPSON.write('         TAX:')
                    string_length = len(vars.us_dollar(print_sync_totals[invoice_id]['tax']))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    vars.EPSON.write('{}{}\n'.format(' ' * string_offset,
                                                     vars.us_dollar(print_sync_totals[invoice_id]['tax'])))
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    vars.EPSON.write('       TOTAL:')
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    string_length = len(vars.us_dollar(print_sync_totals[invoice_id]['total']))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write('{}{}\n'.format(' ' * string_offset,
                                                     vars.us_dollar(
                                                         print_sync_totals[invoice_id]['total'])))
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    vars.EPSON.write('     BALANCE:')
                    string_length = len(vars.us_dollar(print_sync_totals[invoice_id]['total']))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write('{}{}\n\n'.format(' ' * string_offset,
                                                       vars.us_dollar(
                                                           print_sync_totals[invoice_id]['total'])))
                    if item_type == 'L':
                        # get customer mark
                        marks = Custid()
                        marks_list = marks.where({'customer_id': self.customer_id_backup, 'status': 1})
                        if marks_list:
                            m_list = []
                            for mark in marks_list:
                                m_list.append(mark['mark'])
                            vars.EPSON.write(
                                pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=3, height=4,
                                            density=8, invert=False, smooth=False, flip=False))
                            vars.EPSON.write('{}\n\n'.format(', '.join(m_list)))

                    # Cut paper
                    vars.EPSON.write('\n\n\n\n\n\n')
                    vars.EPSON.write(pr.pcmd('PARTIAL_CUT'))
            else:
                for invoice_id, item_id in print_invoice.items():
                    if isinstance(invoice_id, str):
                        invoice_id = int(invoice_id)
                    # start invoice
                    vars.EPSON.write(pr.pcmd('TXT_ALIGN_CT'))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2,
                                    density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write("{}\n".format(companies.name))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                    density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
                    vars.EPSON.write("{}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=2, height=3,
                                    density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write(
                        "READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4,
                                    density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write("--{}--\n".format('{0:06d}'.format(invoice_id)))
                    # Print barcode
                    vars.EPSON.write(pr.pcmd('{}'.format('{0:06d}'.format(invoice_id))))

                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3,
                                    density=6,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write(
                        '{}, {}\n'.format(customers.last_name, customers.first_name))

                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                    density=2,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('{}\n'.format(Job.make_us_phone(customers.phone)))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                    density=1,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('-----------------------------------------\n')
                    if invoice_id in print_sync_invoice:
                        if item_id in print_sync_invoice[invoice_id]:
                            for invoice_item in print_sync_invoice[invoice_id][item_id]:
                                item_name = invoice_item['name']
                                item_price = invoice_item['item_price']
                                item_qty = invoice_item['qty']
                                item_color_string = []
                                item_memo = invoice_item['memos']
                                item_type = invoice_item['type']
                                if invoice_item['colors']:
                                    for color_name, color_qty in invoice_item['colors'].items():
                                        if color_name:
                                            item_color_string.append('{}-{}'.format(color_qty, color_name))
                                string_length = len(item_type) + len(str(item_qty)) + len(item_name) + len(
                                    vars.us_dollar(item_price)) + 4
                                string_offset = 42 - string_length if 42 - string_length > 0 else 0
                                vars.EPSON.write('{} {}   {}{}{}\n'.format(item_type,
                                                                           item_qty,
                                                                           item_name,
                                                                           ' ' * string_offset,
                                                                           vars.us_dollar(item_price)))

                                if len(item_memo) > 0:

                                    vars.EPSON.write(
                                        pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                    height=1,
                                                    density=5, invert=False, smooth=False, flip=False))
                                    vars.EPSON.write('     {}\n'.format('/ '.join(item_memo)))
                                if len(item_color_string) > 0:
                                    vars.EPSON.write(
                                        pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                    height=1,
                                                    density=5, invert=False, smooth=False, flip=False))
                                    vars.EPSON.write('     {}\n'.format(', '.join(item_color_string)))

                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                    density=1,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('-----------------------------------------\n')
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3,
                                    density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('{} PCS\n'.format(print_sync_totals[invoice_id]['quantity']))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                    density=1,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('-----------------------------------------\n')
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('    SUBTOTAL:')
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    string_length = len(vars.us_dollar(print_totals[invoice_id]['subtotal']))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write('{}{}\n'.format(' ' * string_offset,
                                                     vars.us_dollar(print_totals[invoice_id]['subtotal'])))
                    vars.EPSON.write('    DISCOUNT:')
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    string_length = len(vars.us_dollar(print_totals[invoice_id]['discount']))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write('{}{}\n'.format(' ' * string_offset,vars.us_dollar(print_totals[invoice_id]['discount'])))
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    vars.EPSON.write('         TAX:')
                    string_length = len(vars.us_dollar(print_totals[invoice_id]['tax']))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    vars.EPSON.write('{}{}\n'.format(' ' * string_offset,
                                                     vars.us_dollar(print_totals[invoice_id]['tax'])))
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    vars.EPSON.write('       TOTAL:')
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    string_length = len(vars.us_dollar(print_totals[invoice_id]['total']))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write('{}{}\n'.format(' ' * string_offset,
                                                     vars.us_dollar(print_totals[invoice_id]['total'])))
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    vars.EPSON.write('     BALANCE:')
                    string_length = len(vars.us_dollar(print_totals[invoice_id]['total']))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write('{}{}\n\n'.format(' ' * string_offset,
                                                       vars.us_dollar(print_totals[invoice_id]['total'])))
                    if customers.invoice_memo:
                        vars.EPSON.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3,
                                        density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('{}\n'.format(customers.invoice_memo))
                    if item_type == 'L':
                        # get customer mark
                        marks = Custid()
                        marks_list = marks.where({'customer_id': self.customer_id_backup, 'status': 1})
                        if marks_list:
                            m_list = []
                            for mark in marks_list:
                                m_list.append(mark['mark'])
                            vars.EPSON.write(
                                pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=3, height=4,
                                            density=8, invert=False, smooth=False, flip=False))
                            vars.EPSON.write('{}\n\n'.format(', '.join(m_list)))

                    # Cut paper
                    vars.EPSON.write('\n\n\n\n\n\n')
                    vars.EPSON.write(pr.pcmd('PARTIAL_CUT'))


        else:
            popup = Popup()
            popup.title = 'Printer Error'
            content = KV.popup_alert('Could not find usb.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()
            time.sleep(2)
            popup.dismiss()
            SYNC_POPUP.dismiss()
            vars.CUSTOMER_ID = self.customer_id_backup

            # PRINT TAG

        if vars.BIXOLON:
            print('Starting tag printing')

            if print_sync_invoice:  # if invoices synced
                for invoice_id, item_id in print_sync_invoice.items():
                    invoice_id_str = str(invoice_id)
                    invoice_last_four = '{0:04d}'.format(int(invoice_id_str[-4:]))
                    text_left = "{} {}".format(invoice_last_four,
                                               self.due_date.strftime('%a').upper())
                    text_right = "{} {}".format(self.due_date.strftime('%a').upper(),
                                                invoice_last_four)
                    text_name = "{}, {}".format(customers.last_name.upper(),
                                                customers.first_name.upper()[:1])
                    phone_number = Job.make_us_phone(customers.phone)
                    total_length = 32
                    text_offset = total_length - len(text_name) - len(phone_number)
                    name_number_string = '{}{}{}'.format(text_name, ' ' * text_offset,
                                                         phone_number)
                    vars.BIXOLON.write('\x1b\x40')
                    vars.BIXOLON.write('\x1b\x6d')
                    invoice_items = InvoiceItem().where({'invoice_id': invoice_id})
                    laundry_to_print = []
                    if invoice_items:
                        for ii in invoice_items:
                            iitem_id = ii['item_id']
                            tags_to_print = InventoryItem().tagsToPrint(iitem_id)
                            item_name = InventoryItem().getItemName(iitem_id)
                            item_color = ii['color']
                            invoice_item_id = ii['invoice_items_id']
                            laundry_tag = InventoryItem().getLaundry(iitem_id)
                            memo_string = ii['memo']
                            if laundry_tag and tags_to_print > 0:
                                laundry_to_print.append(invoice_item_id)
                            else:
                                for _ in range(tags_to_print):

                                    vars.BIXOLON.write('\x1b!\x30')  # QUAD SIZE
                                    vars.BIXOLON.write('{}{}\n'.format(text_left, text_right))
                                    vars.BIXOLON.write('\x1b!\x00')
                                    vars.BIXOLON.write(name_number_string)
                                    vars.BIXOLON.write('\n')
                                    vars.BIXOLON.write('{0:06d}'.format(int(invoice_item_id)))
                                    vars.BIXOLON.write(' {} {}'.format(item_name, item_color))
                                    if memo_string:
                                        vars.BIXOLON.write('\n{}'.format(memo_string))
                                        memo_len = '\n\n\n' if len(
                                            memo_string) <= 32 else '\n\n\n' + '\n' * int(
                                            (len(memo_string)) / 32)
                                        vars.BIXOLON.write(memo_len)
                                        vars.BIXOLON.write('\x1b\x6d')

                                    else:

                                        vars.BIXOLON.write('\n\n\n')
                                        vars.BIXOLON.write('\x1b\x6d')

            if len(laundry_to_print) is 0:
                # FINAL CUT
                vars.BIXOLON.write('\n\n\n\n\n\n')
                vars.BIXOLON.write('\x1b\x6d')

            else:
                laundry_count = len(laundry_to_print)
                shirt_mark = Custid().getCustomerMark(self.customer_id_backup)
                name_text_offset = total_length - len(text_name) - len(text_name)
                shirt_mark_length = len(shirt_mark)
                mark_text_offset = 16 - (shirt_mark_length * 2)
                if vars.COMPANY_ID is 1: # hard code montlake store does not use this. REMOVE LATER TODO
                    for i in range(0, laundry_count, 2):
                        start = i
                        end = i + 1
                        invoice_item_id_start = '{0:06d}'.format(int(laundry_to_print[start]))
                        id_offset = total_length - 12
                        try:
                            invoice_item_id_end = '{0:06d}'.format(int(laundry_to_print[end]))
                            name_name_string = '{}{}{}'.format(text_name, ' ' * name_text_offset, text_name)
                            mark_mark_string = '{}{}{}'.format(shirt_mark, ' ' * mark_text_offset, shirt_mark)
                            id_id_string = '{}{}{}'.format(invoice_item_id_start, ' ' * id_offset,
                                                           invoice_item_id_end)

                        except IndexError:
                            name_name_string = '{}'.format(text_name)
                            mark_mark_string = '{}'.format(shirt_mark)
                            id_id_string = '{}'.format(invoice_item_id_start)

                        vars.BIXOLON.write('\x1b!\x30')  # QUAD SIZE
                        vars.BIXOLON.write(mark_mark_string)
                        vars.BIXOLON.write('\n')
                        vars.BIXOLON.write('\x1b!\x00')
                        vars.BIXOLON.write(name_name_string)
                        vars.BIXOLON.write('\n')
                        vars.BIXOLON.write(id_id_string)

                        vars.BIXOLON.write('\n\n\n\x1b\x6d')
                # FINAL CUT
                vars.BIXOLON.write('\n\n\n\n\n\n')
                vars.BIXOLON.write('\x1b\x6d')


class EditInvoiceScreen(Screen):
    inv_qty_list = ['1']
    qty_clicks = 0
    inv_qty = 1
    adjust_sum_grid = ObjectProperty(None)
    adjust_individual_grid = ObjectProperty(None)
    invoice_list = OrderedDict()
    invoice_list_copy = OrderedDict()
    inventory_panel = ObjectProperty(None)
    items_grid = GridLayout()
    qty_count_label = ObjectProperty(None)
    item_selected_row = 0
    items_layout = ObjectProperty(None)
    memo_text_input = TextInput(size_hint=(1, 0.4),
                                multiline=True)
    summary_table = ObjectProperty(None)
    summary_quantity_label = ObjectProperty(None)
    summary_tags_label = ObjectProperty(None)
    summary_subtotal_label = ObjectProperty(None)
    summary_tax_label = ObjectProperty(None)
    summary_discount_label = ObjectProperty(None)
    summary_total_label = ObjectProperty(None)
    quantity = 0
    tags = 0
    subtotal = 0
    tax = 0
    discount = 0
    total = 0
    adjust_price = 0
    adjusted_price = ObjectProperty(None)
    calculator_text = ObjectProperty(None)
    adjust_price_list = []
    memo_color_popup = Popup()
    date_picker = ObjectProperty(None)
    due_date = None
    due_date_string = None
    now = datetime.datetime.now()
    month = now.month
    year = now.year
    day = now.day
    calendar_layout = ObjectProperty(None)
    month_button = ObjectProperty(None)
    year_button = ObjectProperty(None)
    print_popup = ObjectProperty(None)
    deleted_rows = []
    inventory_id = 1
    starch = None
    colors_table_main = ObjectProperty(None)
    customer_id_backup = None
    final_total = 0
    invoice_id = None
    discount_id = None
    memo_list = []
    invoice_items_id = None

    def reset(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
        # reset the inventory table
        self.customer_id_backup = vars.CUSTOMER_ID
        self.invoice_id = vars.INVOICE_ID
        self.inventory_panel.clear_widgets()
        self.get_inventory()
        self.summary_table.clear_widgets()
        self.colors_table_main.clear_widgets()
        self.final_total = 0
        self.discount_id = None
        self.invoice_items_id = None
        self.memo_list = []
        store_hours = Company().get_store_hours(vars.COMPANY_ID)
        today = datetime.datetime.today()
        dow = int(datetime.datetime.today().strftime("%w"))
        turn_around_day = int(store_hours[dow]['turnaround']) if 'turnaround' in store_hours[dow] else 0
        turn_around_hour = store_hours[dow]['due_hour'] if 'due_hour' in store_hours[dow] else '4'
        turn_around_minutes = store_hours[dow]['due_minutes'] if 'due_minutes' in store_hours[dow] else '00'
        turn_around_ampm = store_hours[dow]['due_ampm'] if 'due_ampm' in store_hours[dow] else 'pm'
        new_date = today + datetime.timedelta(days=turn_around_day)
        date_string = '{} {}:{}:00'.format(new_date.strftime("%Y-%m-%d"),
                                           turn_around_hour if turn_around_ampm == 'am' else int(turn_around_hour) + 12,
                                           turn_around_minutes)

        total_tags = InvoiceItem().total_tags(self.invoice_id)
        invoice_items = InvoiceItem().where({'invoice_id': self.invoice_id})
        self.invoice_list = OrderedDict()
        self.invoice_list_copy = OrderedDict()
        customers = User().where({'user_id': self.customer_id_backup})
        if customers:
            for customer in customers:
                self.starch = vars.get_starch_by_code(customer['starch'])
        else:
            self.starch = vars.get_starch_by_code(None)
        if invoice_items:
            for invoice_item in invoice_items:
                invoice_items_id = invoice_item['invoice_items_id']
                item_id = invoice_item['item_id']
                items = InventoryItem().where({'item_id': item_id})
                if items:
                    for item in items:
                        inventory_id = item['inventory_id']
                        self.inventory_id = inventory_id
                        inventories = Inventory().where({'inventory_id': '{}'.format(str(inventory_id))})
                        tags = item['tags']
                        if inventories:
                            for inventory in inventories:
                                inventory_init = inventory['name'][:1].capitalize()
                                laundry = inventory['laundry']
                        else:
                            inventory_init = ''
                            laundry = 0

                        item_name = '{} ({})'.format(item['name'], self.starch) if laundry else item['name']
                        if item_id in self.invoice_list:
                            self.invoice_list[item_id].append({
                                'invoice_items_id': invoice_items_id,
                                'type': inventory_init,
                                'inventory_id': inventory_id,
                                'item_id': item_id,
                                'item_name': item_name,
                                'item_price': invoice_item['pretax'],
                                'color': invoice_item['color'],
                                'memo': invoice_item['memo'],
                                'qty': int(invoice_item['quantity']),
                                'tags': int(tags) if tags else 1,
                                'deleted': False
                            })
                            self.invoice_list_copy[item_id].append({
                                'invoice_items_id': invoice_items_id,
                                'type': inventory_init,
                                'inventory_id': inventory_id,
                                'item_id': item_id,
                                'item_name': item_name,
                                'item_price': invoice_item['pretax'],
                                'color': invoice_item['color'],
                                'memo': invoice_item['memo'],
                                'qty': int(invoice_item['quantity']),
                                'tags': int(tags) if tags else 1,
                                'deleted': False
                            })
                        else:
                            self.invoice_list[item_id] = [{
                                'invoice_items_id': invoice_items_id,
                                'type': inventory_init,
                                'inventory_id': inventory_id,
                                'item_id': item_id,
                                'item_name': item_name,
                                'item_price': invoice_item['pretax'],
                                'color': invoice_item['color'],
                                'memo': invoice_item['memo'],
                                'qty': int(invoice_item['quantity']),
                                'tags': int(tags) if tags else 1,
                                'deleted': False
                            }]
                            self.invoice_list_copy[item_id] = [{
                                'invoice_items_id': invoice_items_id,
                                'type': inventory_init,
                                'inventory_id': inventory_id,
                                'item_id': item_id,
                                'item_name': item_name,
                                'item_price': invoice_item['pretax'],
                                'color': invoice_item['color'],
                                'memo': invoice_item['memo'],
                                'qty': int(invoice_item['quantity']),
                                'tags': int(tags) if tags else 1,
                                'deleted': False
                            }]

        invoices = Invoice().where({'invoice_id': self.invoice_id})
        if invoices:
            for invoice in invoices:
                self.due_date = datetime.datetime.strptime(invoice['due_date'], "%Y-%m-%d %H:%M:%S")
                self.due_date_string = '{}'.format(self.due_date.strftime('%a %m/%d %I:%M%p'))
                self.summary_quantity_label.text = '[color=000000]{}[/color]'.format(invoice['quantity'])
                self.summary_tags_label.text = '[color=000000]{}[/color]'.format(total_tags)
                self.summary_subtotal_label.text = '[color=000000]{}[/color]'.format(vars.us_dollar(invoice['pretax']))
                self.summary_tax_label.text = '[color=000000]{}[/color]'.format(vars.us_dollar(invoice['tax']))
                self.summary_discount_label.text = '[color=000000]($0.00)[/color]'
                self.summary_total_label.text = '[color=000000]{}[/color]'.format(vars.us_dollar(invoice['total']))
                self.quantity = invoice['quantity']
                self.tags = total_tags
                self.subtotal = float(invoice['pretax'])
                self.tax = float(invoice['tax'])
                self.discount = 0
                self.total = float(invoice['total'])
        else:
            self.due_date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
            self.due_date_string = '{}'.format(self.due_date.strftime('%a %m/%d %I:%M%p'))
            self.summary_quantity_label.text = '[color=000000]0[/color]'
            self.summary_tags_label.text = '[color=000000]0[/color]'
            self.summary_subtotal_label.text = '[color=000000]$0.00[/color]'
            self.summary_tax_label.text = '[color=000000]$0.00[/color]'
            self.summary_discount_label.text = '[color=000000]($0.00)[/color]'
            self.summary_total_label.text = '[color=000000]$0.00[/color]'
            self.quantity = 0
            self.tags = 0
            self.subtotal = 0
            self.tax = 0
            self.discount = 0
            self.total = 0

        self.date_picker.text = self.due_date_string
        self.inventory_panel.clear_widgets()
        self.get_inventory()
        self.memo_color_popup.dismiss()
        self.qty_clicks = 0
        self.inv_qty = 1
        self.inv_qty_list = ['1']
        self.qty_count_label.text = '1'
        self.memo_text_input.text = ''
        self.summary_table.clear_widgets()
        self.adjust_price = 0
        self.adjust_price_list = []
        vars.ITEM_ID = None

        # create th for invoice summary table
        h1 = KV.sized_invoice_tr(0, 'Type', size_hint_x=0.1)
        h2 = KV.sized_invoice_tr(0, 'Qty', size_hint_x=0.1)
        h3 = KV.sized_invoice_tr(0, 'Item', size_hint_x=0.6)
        h4 = KV.sized_invoice_tr(0, 'Subtotal', size_hint_x=0.2)
        self.summary_table.add_widget(Builder.load_string(h1))
        self.summary_table.add_widget(Builder.load_string(h2))
        self.summary_table.add_widget(Builder.load_string(h3))
        self.summary_table.add_widget(Builder.load_string(h4))
        self.get_inventory()
        self.get_colors_main()
        taxes = Tax().where({'company_id': vars.COMPANY_ID, 'status': 1})
        if taxes:
            for tax in taxes:
                vars.TAX_RATE = tax['rate']
        else:
            vars.TAX_RATE = 0.096
        self.create_summary_table()
        self.create_summary_totals()
        self.deleted_rows = []
        SYNC_POPUP.dismiss()

    def set_result_status(self):
        vars.CUSTOMER_ID = self.customer_id_backup
        vars.INVOICE_ID = self.invoice_id
        vars.SEARCH_RESULTS_STATUS = True
        self.summary_table.clear_widgets()

    def get_colors_main(self):

        colors = Colored().where({'company_id': vars.COMPANY_ID, 'ORDER_BY': 'ordered asc'})
        if colors:
            for color in colors:
                color_btn = Button(markup=True,
                                   text='[b]{color_name}[/b]'.format(color_name=color['name']),
                                   on_release=partial(self.color_selected_main, color['name']))
                color_btn.background_normal = ''
                color_btn.background_color = vars.color_rgba(color['name'])
                self.colors_table_main.add_widget(color_btn)

    def color_selected_main(self, color_name, *args, **kwargs):
        # quantity

        qty = self.inv_qty

        if vars.ITEM_ID in self.invoice_list_copy:
            # loop through the invoice list and see how many colors are set and which is the last row to be set
            total_colors_usable = 0
            rows_updatable = []
            row_to_update = -1
            for row in self.invoice_list_copy[vars.ITEM_ID]:
                row_to_update += 1

                if 'color' in self.invoice_list_copy[vars.ITEM_ID][row_to_update]:
                    if self.invoice_list_copy[vars.ITEM_ID][row_to_update]['color'] is '':
                        total_colors_usable += 1
                        rows_updatable.append(row_to_update)

            if total_colors_usable >= qty:
                qty_countdown = qty
                for row in rows_updatable:

                    if 'color' in self.invoice_list_copy[vars.ITEM_ID][row]:
                        if self.invoice_list_copy[vars.ITEM_ID][row]['color'] is '':
                            qty_countdown -= 1
                            if qty_countdown >= 0:
                                self.invoice_list_copy[vars.ITEM_ID][row]['color'] = color_name

                # save rows and continue

                self.save_memo_color()

                self.create_summary_table()
            else:
                popup = Popup()
                popup.title = 'Color Quantity Error'
                content = KV.popup_alert('Color quantity does not match invoice item quantity. Please try again.')
                popup.content = Builder.load_string(content)
                popup.open()
                # Beep Sound
                sys.stdout.write('\a')
                sys.stdout.flush()

        # reset qty
        self.set_qty('C')

        pass

    def get_inventory(self):
        inventories = Inventory().where({'company_id': '{}'.format(vars.COMPANY_ID)})
        if inventories:
            idx = 0
            self.inventory_panel.clear_tabs()
            self.inventory_panel.clear_widgets()
            for inventory in inventories:
                idx += 1
                inventory_id = inventory['inventory_id']
                inventory_name = inventory['name']
                iitems = InventoryItem()
                inventory_items = iitems.where({'inventory_id': inventory_id, 'ORDER_BY': 'ordered ASC'})
                tph = TabbedPanelHeader(text='{}'.format(inventory_name))
                layout = ScrollView()
                content = '''
GridLayout:
    size_hint_y:None
    height: self.minimum_height
    cols:4
    row_force_default: True
    row_default_height:'150sp'
'''
                if inventory_items:
                    for item in inventory_items:
                        item_id = item['item_id']
                        item_price = '${:,.2f}'.format(item['price'])
                        content += '''
    Button:
        font_size:'17sp'
        markup:True
        text: '[b]{item_name}[/b]\\n[i]{item_price}[/i]'
        disabled: False
        text_size:self.size
        valign:'bottom'
        halign:'center'
        on_release: root.parent.parent.parent.parent.parent.parent.set_item({item_id})
        background_rgba:(.7,.3,.5,1)
        Image:
            id: item_image
            source: '{img_src}'
            size: '50sp','50sp'
            center_x: self.parent.center_x
            center_y: self.parent.center_y
            allow_stretch: True'''.format(item_name=item['name'],
                                          item_price=item_price,
                                          item_id=item_id,
                                          img_src=iitems.get_image_src(item['item_id']))

                layout.add_widget(Builder.load_string(content))
                tph.content = layout
                self.inventory_panel.add_widget(tph)
                if idx == 1:
                    self.inventory_panel.switch_to(tph)

    def set_qty(self, qty):

        if qty is 'C':
            self.qty_clicks = 0
            self.inv_qty_list = ['1']
        elif self.qty_clicks is 0 and qty is 0:
            self.qty_clicks += 0
            self.inv_qty_list = ['0']
        elif self.qty_clicks == 0 and qty is 1:
            self.qty_clicks += 1
            self.inv_qty_list = ['1']
        elif self.qty_clicks == 0 and qty > 1:
            self.qty_clicks += 1
            self.inv_qty_list = ['{}'.format(str(qty))]
        else:
            self.qty_clicks += 1
            self.inv_qty_list.append('{}'.format(str(qty)))
        inv_str = ''.join(self.inv_qty_list)
        if len(self.inv_qty_list) > 3:
            self.qty_clicks = 0
            self.inv_qty_list = ['1']
            inv_str = '1'
        self.qty_count_label.text = inv_str
        self.inv_qty = int(inv_str)

    def set_item(self, item_id):

        vars.ITEM_ID = item_id
        items = InventoryItem().where({'item_id': item_id})
        if items:
            for item in items:
                inventory_id = item['inventory_id']
                item_price = item['price']
                item_tags = item['tags'] if item['tags'] else 1
                item_quantity = item['quantity'] if item['quantity'] else 1
                inventories = Inventory().where({'inventory_id': '{}'.format(str(inventory_id))})
                if inventories:
                    for inventory in inventories:
                        inventory_init = inventory['name'][:1].capitalize()
                        laundry = inventory['laundry']
                else:
                    inventory_init = ''
                    laundry = 0

                item_name = '{} ({})'.format(item['name'], self.starch) if laundry else item['name']
                for x in range(0, self.inv_qty):

                    if item_id in self.invoice_list:
                        self.invoice_list[item_id].append({
                            'type': inventory_init,
                            'inventory_id': inventory_id,
                            'item_id': item_id,
                            'item_name': item_name,
                            'item_price': item_price,
                            'color': '',
                            'memo': '',
                            'qty': int(item_quantity),
                            'tags': int(item_tags)
                        })
                        self.invoice_list_copy[item_id].append({
                            'type': inventory_init,
                            'inventory_id': inventory_id,
                            'item_id': item_id,
                            'item_name': item_name,
                            'item_price': item_price,
                            'color': '',
                            'memo': '',
                            'qty': int(item_quantity),
                            'tags': int(item_tags)
                        })
                    else:
                        self.invoice_list[item_id] = [{
                            'type': inventory_init,
                            'inventory_id': inventory_id,
                            'item_id': item_id,
                            'item_name': item_name,
                            'item_price': item_price,
                            'color': '',
                            'memo': '',
                            'qty': int(item_quantity),
                            'tags': int(item_tags)
                        }]
                        self.invoice_list_copy[item_id] = [{
                            'type': inventory_init,
                            'inventory_id': inventory_id,
                            'item_id': item_id,
                            'item_name': item_name,
                            'item_price': item_price,
                            'color': '',
                            'memo': '',
                            'qty': int(item_quantity),
                            'tags': int(item_tags)
                        }]
        # update dictionary make sure that the most recently selected item is on top
        row = self.invoice_list[vars.ITEM_ID]
        del self.invoice_list[vars.ITEM_ID]
        self.invoice_list[item_id] = row

        self.create_summary_table()
        self.inv_qty_list = ['1']
        self.qty_clicks = 0
        self.inv_qty = 1
        self.qty_count_label.text = '1'

    def create_summary_table(self):
        self.summary_table.clear_widgets()

        # create th
        h1 = KV.sized_invoice_tr(0, 'Type', size_hint_x=0.1)
        h2 = KV.sized_invoice_tr(0, 'Qty', size_hint_x=0.1)
        h3 = KV.sized_invoice_tr(0, 'Item', size_hint_x=0.5)
        h4 = KV.sized_invoice_tr(0, 'Subtotal', size_hint_x=0.2)
        h5 = KV.sized_invoice_tr(0, 'A.', size_hint_x=0.1)
        self.summary_table.add_widget(Builder.load_string(h1))
        self.summary_table.add_widget(Builder.load_string(h2))
        self.summary_table.add_widget(Builder.load_string(h3))
        self.summary_table.add_widget(Builder.load_string(h4))
        self.summary_table.add_widget(Builder.load_string(h5))

        if self.invoice_list:

            for key, values in OrderedDict(reversed(list(self.invoice_list.items()))).items():
                item_id = key
                total_qty = len(values)
                colors = {}
                item_price = 0
                color_string = []
                memo_string = []
                if values:
                    for item in values:
                        item_name = item['item_name']
                        item_type = item['type']
                        item_color = item['color']
                        item_memo = item['memo']
                        item_price += item['item_price'] if item['item_price'] else 0
                        if item['color']:
                            if item_color in colors:
                                colors[item_color] += 1
                            else:
                                colors[item_color] = 1
                        if item_memo:
                            regexed_memo = item_memo.replace('"','**Inch(es)')
                            memo_string.append(regexed_memo)
                    if colors:
                        for color_name, color_amount in colors.items():
                            if color_name:
                                color_string.append('{}-{}'.format(color_amount, color_name))

                    item_string = '[b]{}[/b] \\n{}\\n{}'.format(item_name, ', '.join(color_string),
                                                                '/ '.join(memo_string))
                    selected = True if vars.ITEM_ID == item_id else False
                    tr1 = KV.sized_invoice_tr(1,
                                              item_type,
                                              size_hint_x=0.1,
                                              selected=selected,
                                              on_release='self.parent.parent.parent.parent.parent.parent.select_item({})'.format(
                                                  item_id))
                    tr2 = KV.sized_invoice_tr(1,
                                              total_qty,
                                              size_hint_x=0.1,
                                              selected=selected,
                                              on_release='self.parent.parent.parent.parent.parent.parent.select_item({})'.format(
                                                  item_id))
                    tr3 = KV.sized_invoice_tr(1,
                                              item_string,
                                              size_hint_x=0.5,
                                              selected=selected,
                                              text_wrap=True,
                                              on_release='self.parent.parent.parent.parent.parent.parent.select_item({})'.format(
                                                  item_id))
                    tr4 = KV.sized_invoice_tr(1,
                                              vars.us_dollar(item_price),
                                              size_hint_x=0.2,
                                              selected=selected,
                                              on_release='self.parent.parent.parent.parent.parent.parent.select_item({})'.format(
                                                  item_id))
                    tr5 = Button(size_hint_x=0.1,
                                 markup=True,
                                 text="[color=ffffff][b]-[/b][/color]",
                                 background_color=(1, 0, 0, 1),
                                 background_normal='',
                                 on_release=partial(self.remove_item_row, item_id))
                    self.summary_table.add_widget(Builder.load_string(tr1))
                    self.summary_table.add_widget(Builder.load_string(tr2))
                    self.summary_table.add_widget(Builder.load_string(tr3))
                    self.summary_table.add_widget(Builder.load_string(tr4))
                    self.summary_table.add_widget(tr5)
        self.create_summary_totals()

    def select_item(self, item_id, *args, **kwargs):
        vars.ITEM_ID = item_id
        self.create_summary_table()

    def remove_item_row(self, item_id, *args, **kwargs):
        vars.ITEM_ID = item_id
        print('test0')
        if vars.ITEM_ID in self.invoice_list:
            print('text1')
            idx = -1
            for row in self.invoice_list[vars.ITEM_ID]:
                print('test2')
                idx += 1
                if 'invoice_items_id' in row:
                    print('found rows to delete deleting #{}'.format(row['invoice_items_id']))
                    self.invoice_list[vars.ITEM_ID][idx]['delete'] = True
                    self.deleted_rows.append(row['invoice_items_id'])

                    # delete from local db
                    invoice_items = InvoiceItem()
                    invoice_items.delete_item(row['invoice_items_id'])
            t1 = Thread(target=SYNC.db_sync,args=())
            t1.start()

            del self.invoice_list[vars.ITEM_ID]
        if vars.ITEM_ID in self.invoice_list_copy:
            del self.invoice_list_copy[vars.ITEM_ID]
        if self.invoice_list:
            idx = 0
            for row_key, row_value in self.invoice_list.items():
                idx += 1
                if idx == 1:
                    vars.ITEM_ID = row_key
                    break
        print(self.deleted_rows)
        self.create_summary_table()
        self.create_summary_totals()

    def create_summary_totals(self):
        self.quantity = 0
        self.tags = 0
        self.subtotal = 0
        self.tax = 0
        self.discount = 0
        self.total = 0
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))

        # calculate totals
        tax_rate = float(vars.TAX_RATE)
        if len(self.invoice_list):
            for item_key, item_values in self.invoice_list.items():
                for item in item_values:
                    self.quantity += 1
                    self.tags += int(item['tags']) if item['tags'] else 1
                    self.subtotal += float(item['item_price']) if item['item_price'] else 0
                    # calculate discounts
                    discounts = Discount().where({'company_id': vars.COMPANY_ID,
                                                  'start_date': {'<=': '"{}"'.format(now)},
                                                  'end_date': {'>=': '"{}"'.format(now)},
                                                  'inventory_id': item['inventory_id']});
                    if discounts:
                        for discount in discounts:
                            discount_rate = float(discount['rate'])
                            discount_price = float(discount['discount'])
                            self.discount_id = discount['discount_id']
                            if discount_rate > 0:
                                self.discount += (float(item['item_price'] * discount_rate))
                            elif discount_rate is 0 and discount_price > 0:
                                self.discount += (float(item['item_price'] - discount_price))
                            else:
                                self.discount += 0

            tax = float(float(self.subtotal) * float(tax_rate))

            total = float(self.subtotal + tax)
            self.subtotal = "{0:.2f}".format(self.subtotal)
            self.tax = "{0:.2f}".format(tax)
            self.total = "{0:.2f}".format(total)
            self.final_total = "{0:.2f}".format(total)

            self.tax = (float(self.subtotal) - float(self.discount)) * float(tax_rate)
            self.total = (float(self.subtotal) - float(self.discount)) + float(self.tax)
            self.summary_quantity_label.text = '[color=000000]{}[/color] pcs'.format(self.quantity)
            self.summary_tags_label.text = '[color=000000]{} tags'.format(self.tags)
            self.summary_subtotal_label.text = '[color=000000]{}[/color]'.format(vars.us_dollar(self.subtotal))
            self.summary_tax_label.text = '[color=000000]{}[/color]'.format(vars.us_dollar(self.tax))
            self.summary_discount_label.text = '[color=000000]({})[/color]'.format(vars.us_dollar(self.discount))
            self.summary_total_label.text = '[color=000000][b]{}[/b][/color]'.format(vars.us_dollar(self.total))


    def make_memo_color(self):

        self.item_row_selected(row=0)

        # make popup
        self.memo_color_popup.title = "Add Memo / Color"

        layout = BoxLayout(orientation='vertical',
                           pos_hint={'top': 1},
                           size_hint=(1, 1))

        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.9))
        memo_color_layout = BoxLayout(orientation='vertical',
                                      size_hint=(0.5, 1))
        color_layout = ScrollView(size_hint=(1, 0.4))
        color_title = Label(markup=True,
                            text='[b]Select A Color[/b]',
                            size_hint=(1, 0.1))
        memo_color_layout.add_widget(color_title)
        color_grid = GridLayout(size_hint_y=None,
                                cols=5,
                                row_force_default=True,
                                row_default_height='60sp')
        color_grid.bind(minimum_height=color_grid.setter('height'))
        colors = Colored().where({'company_id': vars.COMPANY_ID, 'ORDER_BY': 'ordered asc'})
        if colors:
            for color in colors:
                color_btn = Button(markup=True,
                                   text='[b]{color_name}[/b]'.format(color_name=color['name']),
                                   on_release=partial(self.color_selected, color['name']))
                color_btn.text_size = color_btn.size
                color_btn.font_size = '12sp'
                color_btn.valign = 'bottom'
                color_btn.halign = 'center'
                color_btn.background_normal = ''
                color_btn.background_color = vars.color_rgba(color['name'])
                color_grid.add_widget(color_btn)
        color_layout.add_widget(color_grid)
        # memo section
        memo_layout = BoxLayout(orientation='vertical',
                                size_hint=(1, 0.5))
        memo_inner_layout_1 = BoxLayout(orientation='vertical',
                                        size_hint=(1, 0.8))
        memo_scroll_view = ScrollView()
        memo_grid_layout = Factory.GridLayoutForScrollView(row_default_height='50sp',
                                                           cols=4)
        mmos = Memo()
        memos = mmos.where({'company_id': vars.COMPANY_ID,
                            'ORDER_BY': 'ordered asc'})
        if memos:
            for memo in memos:
                btn_memo = Factory.LongButton(text=str(memo['memo']),
                                              on_release=partial(self.append_memo, memo['memo']))
                memo_grid_layout.add_widget(btn_memo)

        memo_scroll_view.add_widget(memo_grid_layout)

        memo_inner_layout_2 = BoxLayout(orientation='horizontal',
                                        size_hint=(1, 0.2))
        memo_title = Label(markup=True,
                           pos_hint={'top': 1},
                           text='[b]Create Memo[/b]',
                           size_hint=(1, 0.1))
        memo_text_input = Factory.CenterVerticalTextInput(text='',
                                                          size_hint=(0.7, 1),
                                                          multiline=False)
        memo_inner_layout_1.add_widget(memo_title)
        memo_inner_layout_1.add_widget(memo_scroll_view)

        try:
            memo_inner_layout_2.add_widget(memo_text_input)
        except WidgetException:
            memo_inner_layout_2.remove_widget(memo_text_input)
            memo_inner_layout_2.add_widget(memo_text_input)
        memo_layout.add_widget(memo_inner_layout_1)
        memo_layout.add_widget(memo_inner_layout_2)
        self.memo_text_input = memo_text_input
        memo_add_button = Button(text='Add',
                                 size_hint=(0.3, 1),
                                 on_press=self.add_memo)
        memo_inner_layout_2.add_widget(memo_add_button)

        memo_color_layout.add_widget(color_layout)
        memo_color_layout.add_widget(memo_layout)
        # make items side
        self.items_layout = ScrollView(size_hint=(0.5, 1),
                                       pos_hint={'top': 1})
        self.items_grid = GridLayout(size_hint_y=None,
                                     cols=5,
                                     row_force_default=True,
                                     row_default_height='60sp')
        self.make_items_table()
        self.items_layout.add_widget(self.items_grid)

        inner_layout_1.add_widget(memo_color_layout)
        inner_layout_1.add_widget(self.items_layout)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        cancel_button = Button(markup=True,
                               text="Cancel",
                               on_press=self.memo_color_popup.dismiss)
        save_button = Button(markup=True,
                             text="[color=00f900][b]Save[/b][/color]",
                             on_press=self.save_memo_color,
                             on_release=self.memo_color_popup.dismiss)

        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(save_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.memo_color_popup.content = layout
        # show layout
        self.memo_color_popup.open()

    def append_memo(self, msg, *args, **kwargs):
        if not self.memo_list:
            self.memo_list = [msg]
        else:
            self.memo_list.append(msg)
        self.memo_text_input.text = ', '.join(self.memo_list)

    def make_items_table(self):
        self.items_grid.clear_widgets()
        item_th1 = KV.sized_invoice_tr(0, '#', size_hint_x=0.1)
        item_th2 = KV.sized_invoice_tr(0, 'Item', size_hint_x=0.2)
        item_th3 = KV.sized_invoice_tr(0, 'Color', size_hint_x=0.1)
        item_th4 = KV.sized_invoice_tr(0, 'Memo', size_hint_x=0.5)
        item_th5 = KV.sized_invoice_tr(0, 'A.', size_hint_x=0.1)

        self.items_grid.add_widget(Builder.load_string(item_th1))
        self.items_grid.add_widget(Builder.load_string(item_th2))
        self.items_grid.add_widget(Builder.load_string(item_th3))
        self.items_grid.add_widget(Builder.load_string(item_th4))
        self.items_grid.add_widget(Builder.load_string(item_th5))

        try:
            self.invoice_list_copy[vars.ITEM_ID]
            idx = -1
            for items in self.invoice_list_copy[vars.ITEM_ID]:
                idx += 1
                background_color = (0.36862745, 0.36862745, 0.36862745, 1) if idx == self.item_selected_row else (
                    0.89803922, 0.89803922, 0.89803922, 1)
                background_normal = ''
                text_color = 'e5e5e5' if idx == self.item_selected_row else '000000'
                item_name = items['item_name']
                item_color = items['color']
                item_memo = items['memo']
                items_tr1 = Button(markup=True,
                                   text='[color=#{text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                    msg=str((idx + 1))),
                                   on_press=partial(self.item_row_selected, idx),
                                   size_hint_x=0.1,
                                   font_size='12sp',
                                   background_color=background_color,
                                   background_normal=background_normal)
                items_tr2 = Button(markup=True,
                                   text='[color=#{text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                    msg=item_name),
                                   on_press=partial(self.item_row_selected, idx),
                                   size_hint_x=0.2,
                                   font_size='12sp',
                                   background_color=background_color,
                                   background_normal=background_normal)

                items_tr3 = Button(markup=True,
                                   text='[color=#{text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                    msg=item_color),
                                   on_press=partial(self.item_row_selected, idx),
                                   size_hint_x=0.2,
                                   font_size='12sp',
                                   background_color=background_color,
                                   background_normal=background_normal)
                items_tr4 = Factory.LongButton(text='[color=#{text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                                msg=item_memo),
                                               on_press=partial(self.item_row_selected, idx),
                                               size_hint_x=0.4,
                                               size_hint_y=None,
                                               background_color=background_color,
                                               background_normal=background_normal)
                items_tr5 = Button(markup=True,
                                   text='[color=ff0000][b]Edit[b][/color]',
                                   on_press=partial(self.item_row_selected, idx),
                                   on_release=partial(self.item_row_edit, idx),
                                   size_hint_x=0.1,
                                   font_size='12sp',
                                   background_color=background_color,
                                   background_normal=background_normal)

                self.items_grid.add_widget(items_tr1)
                self.items_grid.add_widget(items_tr2)
                self.items_grid.add_widget(items_tr3)
                self.items_grid.add_widget(items_tr4)
                items_tr4.text_size = (items_tr4.width + 200, items_tr4.height)

                self.items_grid.add_widget(items_tr5)
        except KeyError as e:
            popup = Popup()
            popup.title = 'Selection Error'
            content = KV.popup_alert('Please select an item before attempting an edit.')
            popup.content = Builder.load_string(content)
            popup.open()
            sys.stdout.write('\a')
            sys.stdout.flush()
            return False
        self.items_grid.bind(minimum_height=self.items_grid.setter('height'))

    def add_memo(self, *args, **kwargs):
        if vars.ITEM_ID in self.invoice_list_copy:
            self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]['memo'] = self.memo_text_input.text
            next_row = self.item_selected_row + 1 if (self.item_selected_row + 1) < len(
                self.invoice_list_copy[vars.ITEM_ID]) else 0
            self.item_selected_row = next_row

            self.make_items_table()
            self.memo_text_input.text = ''

    def color_selected(self, color=False, *args, **kwargs):
        if vars.ITEM_ID in self.invoice_list_copy:
            self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]['color'] = color
            next_row = self.item_selected_row + 1 if (self.item_selected_row + 1) < len(
                self.invoice_list_copy[vars.ITEM_ID]) else 0
            self.item_selected_row = next_row
            self.make_items_table()

    def item_row_edit(self, row, *args, **kwargs):
        popup = Popup(title='Remove Colors / Memo')
        popup.size_hint = None, None
        popup.size = 900, 600
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.7))
        inner_layout_1.add_widget(Button(markup=True,
                                         text='Remove Color',
                                         on_press=self.remove_color,
                                         on_release=popup.dismiss))
        inner_layout_1.add_widget(Button(markup=True,
                                         text='Remove Memo',
                                         on_press=self.remove_memo,
                                         on_release=popup.dismiss))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.3))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='Cancel',
                                         on_release=popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def remove_color(self, *args, **kwargs):
        if vars.ITEM_ID in self.invoice_list_copy:
            self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]['color'] = ''
            self.make_items_table()

    def remove_memo(self, *args, **kwargs):
        if vars.ITEM_ID in self.invoice_list_copy:
            self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]['memo'] = ''
            self.make_items_table()

    def item_row_selected(self, row, *args, **kwargs):
        self.item_selected_row = row
        self.make_items_table()

    def save_memo_color(self, *args, **kwargs):
        if vars.ITEM_ID in self.invoice_list_copy:
            idx = -1
            for items in self.invoice_list_copy[vars.ITEM_ID]:
                idx += 1
                color = items['color']
                memo = items['memo']
                self.invoice_list[vars.ITEM_ID][idx]['color'] = color
                self.invoice_list[vars.ITEM_ID][idx]['memo'] = memo
        self.create_summary_table()

    def make_adjust(self):
        self.item_selected_row = 0
        popup = Popup()
        popup.title = 'Adjust Items'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.9))
        adjust_sum_section = BoxLayout(orientation='vertical',
                                       size_hint=(0.5, 1))
        adjust_sum_title = Label(size_hint=(1, 0.1),
                                 markup=True,
                                 text='[b]Adjust Sum Total[/b]')
        adjust_sum_scroll = ScrollView(size_hint=(1, 0.9))
        self.adjust_sum_grid = GridLayout(size_hint_y=None,
                                          cols=4,
                                          row_force_default=True,
                                          row_default_height='50sp')
        self.adjust_sum_grid.bind(minimum_height=self.adjust_sum_grid.setter('height'))
        self.make_adjustment_sum_table()
        adjust_sum_scroll.add_widget(self.adjust_sum_grid)
        adjust_sum_section.add_widget(adjust_sum_title)
        adjust_sum_section.add_widget(adjust_sum_scroll)
        inner_layout_1.add_widget(adjust_sum_section)
        adjust_individual_section = BoxLayout(orientation='vertical',
                                              size_hint=(0.5, 1))

        adjust_individual_title = Label(size_hint=(1, 0.1),
                                        markup=True,
                                        text='[b]Adjust Individual Totals[/b]')
        adjust_individual_scroll = ScrollView(size_hint=(1, 0.9))
        self.adjust_individual_grid = GridLayout(size_hint_y=None,
                                                 cols=5,
                                                 row_force_default=True,
                                                 row_default_height='50sp')
        self.adjust_individual_grid.bind(minimum_height=self.adjust_individual_grid.setter('height'))
        self.make_adjustment_individual_table()
        adjust_individual_scroll.add_widget(self.adjust_individual_grid)
        adjust_individual_section.add_widget(adjust_individual_title)
        adjust_individual_section.add_widget(adjust_individual_scroll)
        inner_layout_1.add_widget(adjust_individual_section)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(markup=True,
                                         text="Cancel",
                                         on_release=popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text="[color=00f900][b]save[/b][/color]",
                                         on_press=self.save_price_adjustment,
                                         on_release=popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def make_adjustment_sum_table(self):
        self.adjust_sum_grid.clear_widgets()
        if vars.ITEM_ID in self.invoice_list_copy and len(self.invoice_list_copy[vars.ITEM_ID]) > 1:
            # create th
            h1 = KV.sized_invoice_tr(0, 'Type', size_hint_x=0.1)
            h2 = KV.sized_invoice_tr(0, 'Qty', size_hint_x=0.1)
            h3 = KV.sized_invoice_tr(0, 'Item', size_hint_x=0.6)
            h4 = KV.sized_invoice_tr(0, 'Subtotal', size_hint_x=0.2)
            self.adjust_sum_grid.add_widget(Builder.load_string(h1))
            self.adjust_sum_grid.add_widget(Builder.load_string(h2))
            self.adjust_sum_grid.add_widget(Builder.load_string(h3))
            self.adjust_sum_grid.add_widget(Builder.load_string(h4))

            if self.invoice_list:

                for key, values in OrderedDict(reversed(list(self.invoice_list_copy.items()))).items():
                    if key == vars.ITEM_ID:
                        item_id = key
                        total_qty = len(values)
                        colors = {}
                        item_price = 0
                        color_string = []
                        memo_string = []
                        if values:
                            for item in values:
                                item_name = item['item_name']
                                item_type = item['type']
                                item_color = item['color']
                                item_memo = item['memo']
                                item_price += item['item_price'] if item['item_price'] else 0
                                if item['color']:
                                    if item_color in colors:
                                        colors[item_color] += 1
                                    else:
                                        colors[item_color] = 1
                                if item_memo:
                                    regexed_memo = item_memo.replace('"', '**Inch(es)')
                                    memo_string.append(regexed_memo)
                            if colors:
                                for color_name, color_amount in colors.items():
                                    if color_name:
                                        color_string.append('{}-{}'.format(color_amount, color_name))

                            item_string = '[b]{}[/b] \n{}\n{}'.format(item_name, ', '.join(color_string),
                                                                      '/ '.join(memo_string))
                            tr1 = Button(size_hint_x=0.1,
                                         markup=True,
                                         text='{}'.format(item_type),
                                         on_release=partial(self.adjustment_calculator,
                                                            1,
                                                            item_price))
                            tr2 = Button(size_hint_x=0.1,
                                         markup=True,
                                         text='{}'.format(total_qty),
                                         on_release=partial(self.adjustment_calculator,
                                                            1,
                                                            item_price))
                            tr3 = Factory.LongButton(size_hint_x=0.6,
                                                     size_hint_y=None,
                                                     markup=True,
                                                     text='{}'.format(item_string),
                                                     on_release=partial(self.adjustment_calculator,
                                                                        1,
                                                                        item_price))

                            tr4 = Button(size_hint_x=0.2,
                                         markup=True,
                                         text='{}'.format(vars.us_dollar(item_price)),
                                         on_release=partial(self.adjustment_calculator,
                                                            1,
                                                            item_price))

                            self.adjust_sum_grid.add_widget(tr1)
                            self.adjust_sum_grid.add_widget(tr2)
                            self.adjust_sum_grid.add_widget(tr3)
                            self.adjust_sum_grid.add_widget(tr4)

    def make_adjustment_individual_table(self):
        self.adjust_individual_grid.clear_widgets()
        # create th
        h1 = KV.sized_invoice_tr(0, 'Type', size_hint_x=0.1)
        h2 = KV.sized_invoice_tr(0, 'Qty', size_hint_x=0.1)
        h3 = KV.sized_invoice_tr(0, 'Item', size_hint_x=0.5)
        h4 = KV.sized_invoice_tr(0, 'Subtotal', size_hint_x=0.2)
        h5 = KV.sized_invoice_tr(0, 'A', size_hint_x=0.1)
        self.adjust_individual_grid.add_widget(Builder.load_string(h1))
        self.adjust_individual_grid.add_widget(Builder.load_string(h2))
        self.adjust_individual_grid.add_widget(Builder.load_string(h3))
        self.adjust_individual_grid.add_widget(Builder.load_string(h4))
        self.adjust_individual_grid.add_widget(Builder.load_string(h5))

        if self.invoice_list:

            for key, values in OrderedDict(reversed(list(self.invoice_list_copy.items()))).items():
                if key == vars.ITEM_ID:
                    idx = -1
                    for item in values:
                        idx += 1
                        item_name = item['item_name']
                        item_type = item['type']
                        item_color = item['color']
                        item_memo = item['memo']
                        item_price = item['item_price'] if item['item_price'] else 0
                        item_string = '[b]{}[/b] \n{}\n{}'.format(item_name, item_color, item_memo)
                        background_color = (
                            0.36862745, 0.36862745, 0.36862745, 1) if idx == self.item_selected_row else (
                            0.89803922, 0.89803922, 0.89803922, 1)
                        background_normal = ''
                        text_color = 'e5e5e5' if idx == self.item_selected_row else '000000'

                        tr1 = Button(size_hint_x=0.1,
                                     markup=True,
                                     text='[color={text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                     msg=item_type),
                                     on_press=partial(self.item_row_adjusted_selected, idx),
                                     on_release=partial(self.adjustment_calculator,
                                                        2,
                                                        item_price,
                                                        idx),
                                     background_color=background_color,
                                     background_normal=background_normal)
                        tr2 = Button(size_hint_x=0.1,
                                     markup=True,
                                     text='[color={text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                     msg=1),
                                     on_press=partial(self.item_row_adjusted_selected, idx),
                                     on_release=partial(self.adjustment_calculator,
                                                        2,
                                                        item_price,
                                                        idx),
                                     background_color=background_color,
                                     background_normal=background_normal)
                        tr3 = Factory.LongButton(size_hint_x=0.6,
                                                 size_hint_y=None,
                                                 markup=True,
                                                 text='[color={text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                                 msg=item_string),
                                                 on_press=partial(self.item_row_adjusted_selected, idx),
                                                 on_release=partial(self.adjustment_calculator,
                                                                    2,
                                                                    item_price,
                                                                    idx),
                                                 background_color=background_color,
                                                 background_normal=background_normal)
                        tr4 = Button(size_hint_x=0.2,
                                     markup=True,
                                     text='[color={text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                     msg=vars.us_dollar(item_price)),
                                     on_press=partial(self.item_row_adjusted_selected, idx),
                                     on_release=partial(self.adjustment_calculator,
                                                        2,
                                                        item_price,
                                                        idx),
                                     background_color=background_color,
                                     background_normal=background_normal)

                        tr5 = Button(size_hint_x=0.1,
                                     markup=True,
                                     text='[color=ffffff][b]-[/b][/color]',
                                     on_release=partial(self.item_row_delete_selected, idx),
                                     background_color=(1, 0, 0, 1),
                                     background_normal='')

                        self.adjust_individual_grid.add_widget(tr1)
                        self.adjust_individual_grid.add_widget(tr2)
                        self.adjust_individual_grid.add_widget(tr3)
                        self.adjust_individual_grid.add_widget(tr4)
                        self.adjust_individual_grid.add_widget(tr5)

    def adjustment_calculator(self, type=None, price=0, row=None, *args, **kwargs):
        self.adjust_price = 0
        self.adjust_price_list = []
        popup = Popup()
        popup.title = 'Adjustment Calculator'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.9))
        calculator_layout = BoxLayout(orientation='vertical',
                                      size_hint=(0.5, 1))
        calculator_top = GridLayout(cols=1,
                                    rows=1,
                                    size_hint=(1, 0.2))
        self.calculator_text = Factory.CenteredLabel(text="[color=000000][b]{}[/b][/color]".format(vars.us_dollar(0)))
        calculator_top.add_widget(self.calculator_text)
        calculator_main_layout = GridLayout(cols=3,
                                            rows=4,
                                            size_hint=(1, 0.8))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]7[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '7')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]8[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '8')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]9[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '9')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]4[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '4')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]5[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '5')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]6[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '6')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]1[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '1')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]2[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '2')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]3[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '3')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]0[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '0')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[b]00[/b]",
                                                 on_release=partial(self.set_price_adjustment_sum, '00')))
        calculator_main_layout.add_widget(Button(markup=True,
                                                 text="[color=ff0000][b]C[/b][/color]",
                                                 on_release=partial(self.set_price_adjustment_sum, 'C')))
        calculator_layout.add_widget(calculator_top)
        calculator_layout.add_widget(calculator_main_layout)
        summary_layout = BoxLayout(orientation='vertical',
                                   size_hint=(0.5, 1))
        summary_layout.add_widget(Label(markup=True,
                                        text="[b]Summary Totals[/b]",
                                        size_hint=(1, 0.1)))
        summary_grid = GridLayout(size_hint=(1, 0.9),
                                  cols=2,
                                  rows=2,
                                  row_force_default=True,
                                  row_default_height='50sp')
        summary_grid.add_widget(Label(markup=True,
                                      text="Original Price"))
        original_price = Factory.ReadOnlyLabel(text='[color=e5e5e5]{}[/color]'.format(vars.us_dollar(price)))
        summary_grid.add_widget(original_price)
        summary_grid.add_widget(Label(markup=True,
                                      text="Adjusted Price"))
        self.adjusted_price = Factory.ReadOnlyLabel(
            text='[color=e5e5e5]{}[/color]'.format(vars.us_dollar(self.adjust_price)))
        summary_grid.add_widget(self.adjusted_price)
        summary_layout.add_widget(summary_grid)

        inner_layout_1.add_widget(calculator_layout)
        inner_layout_1.add_widget(summary_layout)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(markup=True,
                                         text="cancel",
                                         on_release=popup.dismiss))

        inner_layout_2.add_widget(Button(markup=True,
                                         text="[color=00f900][b]OK[/b][/color]",
                                         on_press=self.set_price_adjustment_sum_correct_individual if type == 1 else partial(
                                             self.set_price_adjustment_individual_correct_sum, row),
                                         on_release=popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def set_price_adjustment_sum(self, digit, *args, **kwargs):
        if digit == 'C':
            self.adjust_price = 0
            self.adjust_price_list = []

        else:
            self.adjust_price_list.append(digit)
            self.adjust_price = int(''.join(self.adjust_price_list)) / 100
        self.calculator_text.text = '[color=000000][b]{}[/b][/color]'.format(vars.us_dollar(self.adjust_price))
        self.adjusted_price.text = '[color=e5e5e5][b]{}[/b][/color]'.format(vars.us_dollar(self.adjust_price))

    def set_price_adjustment_sum_correct_individual(self, row, *args, **kwargs):
        if vars.ITEM_ID in self.invoice_list_copy:
            total_count = len(self.invoice_list_copy[vars.ITEM_ID])
            new_avg_price = round(self.adjust_price / total_count, 2)
            minus_total = self.adjust_price
            idx = -1
            for items in self.invoice_list_copy[vars.ITEM_ID]:
                idx += 1
                minus_total -= new_avg_price
                if idx < len(self.invoice_list_copy[vars.ITEM_ID]) - 1:
                    self.invoice_list_copy[vars.ITEM_ID][idx]['item_price'] = new_avg_price
                else:
                    self.invoice_list_copy[vars.ITEM_ID][idx]['item_price'] = round(new_avg_price + minus_total, 2)
            self.make_adjustment_sum_table()
            self.make_adjustment_individual_table()

    def set_price_adjustment_individual_correct_sum(self, row, *args, **kwargs):
        if vars.ITEM_ID in self.invoice_list_copy:
            self.invoice_list_copy[vars.ITEM_ID][row]['item_price'] = self.adjust_price
            self.make_adjustment_sum_table()
            self.make_adjustment_individual_table()

    def save_price_adjustment(self, *args, **kwargs):

        if vars.ITEM_ID in self.invoice_list_copy:
            idx = -1
            for items in self.invoice_list_copy[vars.ITEM_ID]:
                idx += 1
                new_price = items['item_price']
                self.invoice_list[vars.ITEM_ID][idx]['item_price'] = new_price
            self.create_summary_table()
            self.create_summary_totals()

    def item_row_delete_selected(self, row, *args, **kwargs):
        if vars.ITEM_ID in self.invoice_list:
            if row in self.invoice_list[vars.ITEM_ID]:
                if 'invoice_items_id' in self.invoice_list[vars.ITEM_ID][row]:
                    self.invoice_list[vars.ITEM_ID][row]['delete'] = True
                    self.deleted_rows.append(self.invoice_list[vars.ITEM_ID][row]['invoice_items_id'])
        print(self.deleted_rows)
        del self.invoice_list[vars.ITEM_ID][row]
        del self.invoice_list_copy[vars.ITEM_ID][row]
        self.item_selected_row = 0
        self.make_adjustment_sum_table()
        self.make_adjustment_individual_table()
        self.create_summary_table()
        self.create_summary_totals()

    def item_row_adjusted_selected(self, row, *args, **kwargs):
        self.item_selected_row = row
        self.adjust_individual_grid.clear_widgets()
        self.make_adjustment_individual_table()

    def make_calendar(self):

        store_hours = Company().get_store_hours(vars.COMPANY_ID)
        today = datetime.datetime.today()
        dow = int(datetime.datetime.today().strftime("%w"))
        turn_around_day = int(store_hours[dow]['turnaround']) if store_hours[dow]['turnaround'] else 0
        turn_around_hour = store_hours[dow]['due_hour'] if store_hours[dow]['due_hour'] else '4'
        turn_around_minutes = store_hours[dow]['due_minutes'] if store_hours[dow]['due_minutes'] else '00'
        turn_around_ampm = store_hours[dow]['due_ampm'] if store_hours[dow]['due_ampm'] else 'pm'
        new_date = today + datetime.timedelta(days=turn_around_day)
        date_string = '{} {}:{}:00'.format(new_date.strftime("%Y-%m-%d"),
                                           turn_around_hour if turn_around_ampm == 'am' else int(turn_around_hour) + 12,
                                           turn_around_minutes)
        due_date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        self.month = int(due_date.strftime('%m'))

        popup = Popup()
        popup.title = 'Calendar'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(size_hint=(1, 0.9),
                                   orientation='vertical')
        calendar_selection = GridLayout(cols=4,
                                        rows=1,
                                        size_hint=(1, 0.1))
        prev_month = Button(markup=True,
                            text="<",
                            font_size="30sp",
                            on_release=self.prev_month)
        next_month = Button(markup=True,
                            text=">",
                            font_size="30sp",
                            on_release=self.next_month)
        select_month = Factory.SelectMonth()
        self.month_button = Button(text='{}'.format(vars.month_by_number(self.month)),
                                   on_release=select_month.open)
        for index in range(12):
            month_options = Button(text='{}'.format(vars.month_by_number(index)),
                                   size_hint_y=None,
                                   height=40,
                                   on_release=partial(self.select_calendar_month, index))
            select_month.add_widget(month_options)

        select_month.on_select = lambda instance, x: setattr(self.month_button, 'text', x)
        select_year = Factory.SelectMonth()

        self.year_button = Button(text="{}".format(self.year),
                                  on_release=select_year.open)
        for index in range(10):
            year_options = Button(text='{}'.format(int(self.year) + index),
                                  size_hint_y=None,
                                  height=40,
                                  on_release=partial(self.select_calendar_year, index))
            select_year.add_widget(year_options)

        select_year.bind(on_select=lambda instance, x: setattr(self.year_button, 'text', x))
        calendar_selection.add_widget(prev_month)
        calendar_selection.add_widget(self.month_button)
        calendar_selection.add_widget(self.year_button)
        calendar_selection.add_widget(next_month)
        self.calendar_layout = GridLayout(cols=7,
                                          rows=8,
                                          size_hint=(1, 0.9))
        self.create_calendar_table()

        inner_layout_1.add_widget(calendar_selection)
        inner_layout_1.add_widget(self.calendar_layout)
        inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                   orientation='horizontal')
        inner_layout_2.add_widget(Button(markup=True,
                                         text="Okay",
                                         on_release=popup.dismiss))

        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def create_calendar_table(self):
        # set the variables

        store_hours = Company().get_store_hours(vars.COMPANY_ID)
        today_date = datetime.datetime.today()
        today_string = today_date.strftime('%Y-%m-%d 00:00:00')
        check_today = datetime.datetime.strptime(today_string, "%Y-%m-%d %H:%M:%S").timestamp()
        due_date_string = self.due_date.strftime('%Y-%m-%d 00:00:00')
        check_due_date = datetime.datetime.strptime(due_date_string, "%Y-%m-%d %H:%M:%S").timestamp()

        self.calendar_layout.clear_widgets()
        calendars = Calendar()
        calendars.setfirstweekday(calendar.SUNDAY)
        selected_month = self.month - 1
        year_dates = calendars.yeardays2calendar(year=self.year, width=1)
        th1 = KV.invoice_tr(0, 'Su')
        th2 = KV.invoice_tr(0, 'Mo')
        th3 = KV.invoice_tr(0, 'Tu')
        th4 = KV.invoice_tr(0, 'We')
        th5 = KV.invoice_tr(0, 'Th')
        th6 = KV.invoice_tr(0, 'Fr')
        th7 = KV.invoice_tr(0, 'Sa')
        self.calendar_layout.add_widget(Builder.load_string(th1))
        self.calendar_layout.add_widget(Builder.load_string(th2))
        self.calendar_layout.add_widget(Builder.load_string(th3))
        self.calendar_layout.add_widget(Builder.load_string(th4))
        self.calendar_layout.add_widget(Builder.load_string(th5))
        self.calendar_layout.add_widget(Builder.load_string(th6))
        self.calendar_layout.add_widget(Builder.load_string(th7))
        if year_dates[selected_month]:
            for month in year_dates[selected_month]:
                for week in month:
                    for day in week:
                        if day[0] > 0:
                            check_date_string = '{}-{}-{} 00:00:00'.format(self.year,
                                                                           Job.date_leading_zeroes(self.month),
                                                                           Job.date_leading_zeroes(day[0]))
                            today_base = datetime.datetime.strptime(check_date_string, "%Y-%m-%d %H:%M:%S")
                            check_date = today_base.timestamp()
                            dow_check = today_base.strftime("%w")
                            # rule #1 remove all past dates so users cannot set a due date previous to today
                            if check_date < check_today:
                                item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                              disabled=True)
                            elif int(store_hours[int(dow_check)]['status']) > 1:  # check to see if business is open
                                if check_date == check_today:
                                    item = Factory.CalendarButton(text="[color=37FDFC][b]{}[/b][/color]".format(day[0]),
                                                                  background_color=(0, 0.50196078, 0.50196078, 1),
                                                                  background_normal='',
                                                                  on_release=partial(self.select_due_date, today_base))
                                elif check_date == check_due_date:
                                    item = Factory.CalendarButton(text="[color=008080][b]{}[/b][/color]".format(day[0]),
                                                                  background_color=(
                                                                      0.2156862, 0.9921568, 0.98823529, 1),
                                                                  background_normal='',
                                                                  on_release=partial(self.select_due_date, today_base))
                                elif check_today < check_date < check_due_date:
                                    item = Factory.CalendarButton(text="[color=008080][b]{}[/b][/color]".format(day[0]),
                                                                  background_color=(0.878431372549020, 1, 1, 1),
                                                                  background_normal='',
                                                                  on_release=partial(self.select_due_date, today_base))
                                else:
                                    item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                                  on_release=partial(self.select_due_date, today_base))
                            else:  # store is closed
                                item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                              disabled=True)
                        else:
                            item = Factory.CalendarButton(disabled=True)
                        self.calendar_layout.add_widget(item)

    def prev_month(self, *args, **kwargs):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.month_button.text = '{}'.format(vars.month_by_number(self.month))
        self.year_button.text = '{}'.format(self.year)
        self.create_calendar_table()

    def next_month(self, *args, **kwargs):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.month_button.text = '{}'.format(vars.month_by_number(self.month))
        self.year_button.text = '{}'.format(self.year)
        self.create_calendar_table()

    def select_calendar_month(self, month, *args, **kwargs):
        self.month = month
        self.create_calendar_table()

    def select_calendar_year(self, year, *args, **kwargs):
        self.year = year
        self.create_calendar_table()

    def select_due_date(self, selected_date, *args, **kwargs):
        store_hours = Company().get_store_hours(vars.COMPANY_ID)

        dow = int(selected_date.strftime("%w"))
        turn_around_hour = store_hours[dow]['due_hour'] if store_hours[dow]['due_hour'] else '4'
        turn_around_minutes = store_hours[dow]['due_minutes'] if store_hours[dow]['due_minutes'] else '00'
        turn_around_ampm = store_hours[dow]['due_ampm'] if store_hours[dow]['due_ampm'] else 'pm'
        date_string = '{} {}:{}:00'.format(selected_date.strftime("%Y-%m-%d"),
                                           turn_around_hour if turn_around_ampm == 'am' else int(turn_around_hour) + 12,
                                           turn_around_minutes)
        self.due_date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        self.due_date_string = '{}'.format(self.due_date.strftime('%a %m/%d %I:%M%p'))
        self.date_picker.text = self.due_date_string
        self.create_calendar_table()

    def print_selection(self):
        self.print_popup = Popup()
        self.print_popup.title = 'Print Selection'
        self.print_popup.size_hint = (None, None)
        self.print_popup.size = (800, 600)
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.7))
        button_1 = Factory.PrintButton(text='Cust. + Store',
                                       on_release=partial(self.wait_popup, 'both'))

        inner_layout_1.add_widget(button_1)
        button_2 = Factory.PrintButton(text='Store Only',
                                       on_release=partial(self.wait_popup, 'store'))

        inner_layout_1.add_widget(button_2)
        button_3 = Factory.PrintButton(text='No Print',
                                       on_release=partial(self.wait_popup, 'none'))

        inner_layout_1.add_widget(button_3)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.3))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='Cancel',
                                         on_release=self.print_popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.print_popup.content = layout
        self.print_popup.open()

    def wait_popup(self, type, *args, **kwargs):
        SYNC_POPUP.title = 'Syncing Data'
        content = KV.popup_alert("Syncing data to server, please wait...")
        SYNC_POPUP.content = Builder.load_string(content)
        SYNC_POPUP.open()
        Clock.schedule_once(partial(self.finish_invoice, type))

    def finish_invoice(self, type, *args, **kwargs):

        # determine the types of invoices we need to print
        self.create_summary_totals()
        self.now = datetime.datetime.now()
        # set the printer data
        tax_rate = vars.TAX_RATE

        if self.invoice_list:
            invoice_items = InvoiceItem()
            print_invoice = {}
            print_invoice[self.invoice_id] = {}

            for invoice_item_key, invoice_item_value in self.invoice_list.items():
                colors = {}
                for iivalue in invoice_item_value:
                    item_id = iivalue['item_id']
                    colors[item_id] = {}
                for iivalue in invoice_item_value:
                    qty = iivalue['qty']
                    pretax = "{0:.2f}".format(float(iivalue['item_price'])) if iivalue['item_price'] else 0
                    tax = "{0:.2f}".format(float(iivalue['item_price']) * float(tax_rate))
                    total = "{0:.2f}".format(float(iivalue['item_price']) * (1 + float(tax_rate)))
                    item_id = iivalue['item_id']
                    inventory_id = InventoryItem().getInventoryId(item_id)
                    item_name = iivalue['item_name']
                    item_price = iivalue['item_price']
                    item_type = iivalue['type']
                    item_color = iivalue['color']
                    item_memo = iivalue['memo']
                    if item_id in colors:
                        if item_color in colors[item_id]:
                            colors[item_id][item_color] += 1
                        else:
                            colors[item_id][item_color] = 1
                    if self.invoice_id in print_invoice:
                        if item_id in print_invoice[self.invoice_id]:
                            print_invoice[self.invoice_id][item_id]['item_price'] += item_price
                            print_invoice[self.invoice_id][item_id]['qty'] += 1
                            if item_id in colors:
                                print_invoice[self.invoice_id][item_id]['colors'] = colors[item_id]
                            else:
                                print_invoice[self.invoice_id][item_id]['colors'] = []
                            if item_memo:
                                print_invoice[self.invoice_id][item_id]['memos'].append(item_memo)
                        else:

                            print_invoice[self.invoice_id][item_id] = {
                                'item_id': item_id,
                                'type': item_type,
                                'name': item_name,
                                'item_price': item_price,
                                'qty': 1,
                                'memos': [item_memo] if item_memo else [],
                                'colors': colors[item_id] if item_id in colors else []
                            }
                    if 'invoice_items_id' in iivalue:
                        invoice_items.put(where={'invoice_items_id': iivalue['invoice_items_id']},
                                          data={'quantity': iivalue['qty'],
                                                'color': iivalue['color'] if iivalue['color'] else None,
                                                'memo': item_memo if item_memo is not None else None,
                                                'pretax': pretax,
                                                'tax': tax,
                                                'total': total})
                        print('invoice item updated')
                    else:
                        print('Here...')
                        new_invoice_item = InvoiceItem()
                        new_invoice_item.company_id = vars.COMPANY_ID
                        new_invoice_item.customer_id = self.customer_id_backup
                        new_invoice_item.invoice_id = self.invoice_id
                        new_invoice_item.item_id = item_id
                        new_invoice_item.inventory_id = inventory_id
                        new_invoice_item.quantity = qty
                        new_invoice_item.color = str(item_color) if item_color else None
                        new_invoice_item.memo = str(item_memo) if item_memo else None
                        new_invoice_item.pretax = pretax
                        new_invoice_item.tax = tax
                        new_invoice_item.total = total
                        new_invoice_item.status = 1
                        new_invoice_item.add()
            self.update_invoice()
        time.sleep(1)
        run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
        try:
            run_sync.start()
        finally:
            run_sync.join()

        # print invoices
        if vars.EPSON:
            pr = Printer()
            companies = Company()
            comps = companies.where({'company_id': vars.COMPANY_ID}, set=True)
            if comps:
                for company in comps:
                    companies.id = company['id']
                    companies.company_id = company['company_id']
                    companies.name = company['name']
                    companies.street = company['street']
                    companies.suite = company['suite']
                    companies.city = company['city']
                    companies.state = company['state']
                    companies.zip = company['zip']
                    companies.email = company['email']
                    companies.phone = company['phone']
            customers = User()
            custs = customers.where({'user_id': self.customer_id_backup}, set=True)
            if custs:
                for user in custs:
                    customers.id = user['id']
                    customers.user_id = user['user_id']
                    customers.company_id = user['company_id']
                    customers.username = user['username']
                    customers.first_name = user['first_name'].upper() if user['first_name'] else ''
                    customers.last_name = user['last_name']
                    customers.street = user['street']
                    customers.suite = user['suite']
                    customers.city = user['city']
                    customers.state = user['state']
                    customers.zipcode = user['zipcode']
                    customers.email = user['email']
                    customers.phone = user['phone']
                    customers.intercom = user['intercom']
                    customers.concierge_name = user['concierge_name']
                    customers.concierge_number = user['concierge_number']
                    customers.special_instructions = user['special_instructions']
                    customers.shirt_old = user['shirt_old']
                    customers.shirt = user['shirt']
                    customers.delivery = user['delivery']
                    customers.profile_id = user['profile_id']
                    customers.payment_status = user['payment_status']
                    customers.payment_id = user['payment_id']
                    customers.token = user['token']
                    customers.api_token = user['api_token']
                    customers.reward_status = user['reward_status']
                    customers.reward_points = user['reward_points']
                    customers.account = user['account']
                    customers.starch = user['starch']
                    customers.important_memo = user['important_memo']
                    customers.invoice_memo = user['invoice_memo']
                    customers.password = user['password']
                    customers.role_id = user['role_id']
                    customers.remember_token = user['remember_token']

            if type is 'none':
                self.set_result_status()
                self.print_popup.dismiss()
                pass
            elif type is 'both':
                print('Customer & Store Copy')
                vars.EPSON.write(pr.pcmd('TXT_ALIGN_CT'))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                density=5, invert=False, smooth=False, flip=False))
                vars.EPSON.write("::CUSTOMER::\n")
                vars.EPSON.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                             invert=False, smooth=False, flip=False))
                vars.EPSON.write("{}\n".format(companies.name))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write("{}\n".format(companies.street))
                vars.EPSON.write("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))

                vars.EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
                vars.EPSON.write("edited on: {}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                vars.EPSON.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                             invert=False, smooth=False, flip=False))
                padded_customer_id = '{0:05d}'.format(self.customer_id_backup)
                vars.EPSON.write("{}\n".format(padded_customer_id))

                # Print barcode
                vars.EPSON.write(pr.pcmd_barcode(str(padded_customer_id)))

                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('{}\n'.format(Job.make_us_phone(customers.phone)))
                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('-----------------------------------------\n')

                # display invoice details
                if self.invoice_list:

                    for key, values in OrderedDict(reversed(list(self.invoice_list.items()))).items():
                        total_qty = len(values)
                        colors = {}
                        item_price = 0
                        color_string = []
                        memo_string = []
                        if values:
                            for item in values:
                                item_name = item['item_name']
                                item_type = item['type']
                                item_color = item['color']
                                item_memo = item['memo']
                                item_price += item['item_price'] if item['item_price'] else 0
                                if item['color']:
                                    if item_color in colors:
                                        colors[item_color] += 1
                                    else:
                                        colors[item_color] = 1
                                if item_memo:
                                    regexed_memo = item_memo.replace('"', '**Inch(es)')
                                    memo_string.append(regexed_memo)
                            if colors:
                                for color_name, color_amount in colors.items():
                                    if color_name:
                                        color_string.append('{}-{}'.format(color_amount, color_name))

                            vars.EPSON.write(
                                pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=5, invert=False, smooth=False, flip=False))
                            vars.EPSON.write('{} {}    '.format(item_type, total_qty, item_name))
                            vars.EPSON.write(pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'B', width=1, height=1,
                                                         density=5, invert=False, smooth=False, flip=False))
                            vars.EPSON.write('{}\n'.format(item_name))
                            if len(memo_string) > 0:

                                vars.EPSON.write(
                                    pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                density=5, invert=False, smooth=False, flip=False))
                                vars.EPSON.write('  {}\n'.format('/ '.join(memo_string)))
                            if len(color_string):

                                vars.EPSON.write(
                                    pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                density=5, invert=False, smooth=False, flip=False))
                                vars.EPSON.write('{}\n'.format(', '.join(color_string)))

                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('-----------------------------------------\n')
                vars.EPSON.write(pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                             invert=False, smooth=False, flip=False))
                vars.EPSON.write('{} PCS\n'.format(self.quantity))
                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('-----------------------------------------\n')
                # Cut paper
                vars.EPSON.write('\n\n\n\n\n\n')
                vars.EPSON.write(pr.pcmd('PARTIAL_CUT'))

                # Print store copies
                if print_invoice:  # if invoices synced
                    for invoice_id, item_id in print_invoice.items():
                        if isinstance(invoice_id, str):
                            invoice_id = int(invoice_id)
                        # start invoice
                        vars.EPSON.write(pr.pcmd('TXT_ALIGN_CT'))
                        vars.EPSON.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write("::COPY::\n")
                        vars.EPSON.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write("{}\n".format(companies.name))
                        vars.EPSON.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
                        vars.EPSON.write("edited: {}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                        vars.EPSON.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                        vars.EPSON.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write("{}\n".format('{0:06d}'.format(invoice_id)))
                        # Print barcode
                        vars.EPSON.write(pr.pcmd_barcode('{}'.format('{0:06d}'.format(invoice_id))))

                        vars.EPSON.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                        vars.EPSON.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('{}\n'.format(Job.make_us_phone(customers.phone)))
                        vars.EPSON.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('-----------------------------------------\n')
                        if invoice_id in print_invoice:
                            for item_id, invoice_item in print_invoice[invoice_id].items():
                                item_name = invoice_item['name']
                                item_price = invoice_item['item_price']
                                item_qty = invoice_item['qty']
                                item_color_string = []
                                item_memo = invoice_item['memos']
                                item_type = invoice_item['type']
                                if 'colors' in invoice_item:
                                    for color_name, color_qty in invoice_item['colors'].items():
                                        if color_name:
                                            item_color_string.append('{}-{}'.format(color_qty, color_name))
                                string_length = len(item_type) + len(str(item_qty)) + len(item_name) + len(
                                    vars.us_dollar(item_price)) + 4
                                string_offset = 42 - string_length if 42 - string_length > 0 else 0
                                vars.EPSON.write('{} {}   {}{}{}\n'.format(item_type,
                                                                           item_qty,
                                                                           item_name,
                                                                           ' ' * string_offset,
                                                                           vars.us_dollar(item_price)))

                                # vars.EPSON.write('\r\x1b@\x1b\x61\x02{}\n'.format(vars.us_dollar(item_price)))
                                if len(item_memo) > 0:
                                    vars.EPSON.write(
                                        pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                    density=5, invert=False, smooth=False, flip=False))
                                    vars.EPSON.write('     {}\n'.format('/ '.join(item_memo)))
                                if len(item_color_string) > 0:
                                    vars.EPSON.write(
                                        pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                    density=5, invert=False, smooth=False, flip=False))
                                    vars.EPSON.write('     {}\n'.format(', '.join(item_color_string)))

                        vars.EPSON.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('-----------------------------------------\n')
                        vars.EPSON.write(
                            pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('{} PCS\n'.format(self.quantity))
                        vars.EPSON.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('-----------------------------------------\n')
                        vars.EPSON.write(
                            pr.pcmd_set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('    SUBTOTAL:')
                        vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                        string_length = len(vars.us_dollar(self.subtotal))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.write('{}{}\n'.format(' ' * string_offset,
                                                         vars.us_dollar(self.subtotal)))
                        vars.EPSON.write('    DISCOUNT:')
                        vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                        string_length = len(vars.us_dollar(self.discount))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.write('{}({})\n'.format(' ' * string_offset,
                                                         vars.us_dollar(self.discount)))
                        vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                        vars.EPSON.write('         TAX:')
                        string_length = len(vars.us_dollar(self.tax))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                        vars.EPSON.write('{}{}\n'.format(' ' * string_offset,
                                                         vars.us_dollar(self.tax)))
                        vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                        vars.EPSON.write('       TOTAL:')
                        vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                        string_length = len(vars.us_dollar(self.total))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.write('{}{}\n'.format(' ' * string_offset,
                                                         vars.us_dollar(self.total)))
                        vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                        vars.EPSON.write('     BALANCE:')
                        string_length = len(vars.us_dollar(self.total))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.write('{}{}\n\n'.format(' ' * string_offset,
                                                           vars.us_dollar(self.total)))
                        if item_type == 'L':
                            # get customer mark
                            marks = Custid()
                            marks_list = marks.where({'customer_id': self.customer_id_backup, 'status': 1})
                            if marks_list:
                                m_list = []
                                for mark in marks_list:
                                    m_list.append(mark['mark'])
                                vars.EPSON.write(
                                    pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=3, height=4,
                                                density=8, invert=False, smooth=False, flip=False))
                                vars.EPSON.write('{}\n\n'.format(', '.join(m_list)))

                        # Cut paper
                        vars.EPSON.write('\n\n\n\n\n\n')
                        vars.EPSON.write(pr.pcmd('PARTIAL_CUT'))
            elif type is 'store':
                print('Store Copy Only')
                # Print store copies
                if print_invoice:  # if invoices synced
                    for invoice_id, item_id in print_invoice.items():
                        if isinstance(invoice_id, str):
                            invoice_id = int(invoice_id) if invoice_id else 0
                        # start invoice
                        vars.EPSON.write(pr.pcmd('TXT_ALIGN_CT'))
                        vars.EPSON.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write("::COPY::\n")
                        vars.EPSON.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write("{}\n".format(companies.name))
                        vars.EPSON.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
                        vars.EPSON.write("edited: {}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                        vars.EPSON.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                        vars.EPSON.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write("{}\n".format('{0:06d}'.format(invoice_id)))
                        # Print barcode
                        vars.EPSON.write(pr.pcmd_barcode('{0:06d}'.format(invoice_id)))

                        vars.EPSON.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                        vars.EPSON.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('{}\n'.format(Job.make_us_phone(customers.phone)))
                        vars.EPSON.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('-----------------------------------------\n')

                        if invoice_id in print_invoice:
                            for item_id, invoice_item in print_invoice[invoice_id].items():
                                item_name = invoice_item['name']
                                item_price = invoice_item['item_price']
                                item_qty = invoice_item['qty']
                                item_color_string = []
                                item_memo = invoice_item['memos']
                                item_type = invoice_item['type']
                                if 'colors' in invoice_item:
                                    for color_name, color_qty in invoice_item['colors'].items():
                                        if color_name:
                                            item_color_string.append('{}-{}'.format(color_qty, color_name))
                                string_length = len(item_type) + len(str(item_qty)) + len(item_name) + len(
                                    vars.us_dollar(item_price)) + 4
                                string_offset = 42 - string_length if 42 - string_length > 0 else 0
                                vars.EPSON.write('{} {}   {}{}{}\n'.format(item_type,
                                                                           item_qty,
                                                                           item_name,
                                                                           ' ' * string_offset,
                                                                           vars.us_dollar(item_price)))

                                # vars.EPSON.write('\r\x1b@\x1b\x61\x02{}\n'.format(vars.us_dollar(item_price)))
                                if len(item_memo) > 0:
                                    vars.EPSON.write(
                                        pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                    density=5, invert=False, smooth=False, flip=False))
                                    vars.EPSON.write('     {}\n'.format('/ '.join(item_memo)))
                                if len(item_color_string) > 0:
                                    vars.EPSON.write(
                                        pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                    density=5, invert=False, smooth=False, flip=False))
                                    vars.EPSON.write('     {}\n'.format(', '.join(item_color_string)))

                        vars.EPSON.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('-----------------------------------------\n')
                        vars.EPSON.write(
                            pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('{} PCS\n'.format(self.quantity))
                        vars.EPSON.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('-----------------------------------------\n')
                        vars.EPSON.write(
                            pr.pcmd_set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('    SUBTOTAL:')
                        vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                        string_length = len(vars.us_dollar(self.subtotal))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.write('{}{}\n'.format(' ' * string_offset,
                                                         vars.us_dollar(self.subtotal)))
                        vars.EPSON.write('    DISCOUNT:')
                        vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                        string_length = len(vars.us_dollar(self.discount))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.write('{}({})\n'.format(' ' * string_offset,
                                                           vars.us_dollar(self.discount)))
                        vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                        vars.EPSON.write('         TAX:')
                        string_length = len(vars.us_dollar(self.tax))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                        vars.EPSON.write('{}{}\n'.format(' ' * string_offset,
                                                         vars.us_dollar(self.tax)))
                        vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                        vars.EPSON.write('       TOTAL:')
                        vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                        string_length = len(vars.us_dollar(self.total))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.write('{}{}\n'.format(' ' * string_offset,
                                                         vars.us_dollar(self.total)))
                        vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                        vars.EPSON.write('     BALANCE:')
                        string_length = len(vars.us_dollar(self.total))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.write('{}{}\n\n'.format(' ' * string_offset,
                                                           vars.us_dollar(self.total)))
                        if customers.invoice_memo:
                            vars.EPSON.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write('{}\n'.format(customers.invoice_memo))
                        if item_type == 'L':
                            # get customer mark
                            marks = Custid()
                            marks_list = marks.where({'customer_id': self.customer_id_backup, 'status': 1})
                            if marks_list:
                                m_list = []
                                for mark in marks_list:
                                    m_list.append(mark['mark'])
                                vars.EPSON.write(
                                    pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=3, height=4,
                                                density=8, invert=False, smooth=False, flip=False))
                                vars.EPSON.write('{}\n\n'.format(', '.join(m_list)))

                        # Cut paper
                        vars.EPSON.write('\n\n\n\n\n\n')
                        vars.EPSON.write(pr.pcmd('PARTIAL_CUT'))

        else:
            popup = Popup()
            popup.title = 'Printer Error'
            content = KV.popup_alert('Unable to locate usb printer.')
            popup.content = Builder.load_string(content)
            popup.open()
            sys.stdout.write('\a')
            sys.stdout.flush()
            time.sleep(2)
            popup.dismiss()

        vars.CUSTOMER_ID = self.customer_id_backup
        self.set_result_status()

        self.print_popup.dismiss()
        SYNC_POPUP.dismiss()


    def update_invoice(self, *arkgs, **kwargs):
        print('starting update on invoice - {}'.format(self.invoice_id))
        inv_save = Invoice()
        invs = inv_save.where({'invoice_id':self.invoice_id})
        if invs:
            for inv in invs:
                inv_save.id = inv['id']
                inv_save.invoice_id = inv['invoice_id']
                inv_save.company_id = inv['company_id']
                inv_save.customer_id = inv['customer_id']
                inv_save.quantity = self.tags
                inv_save.pretax = '{0:.2f}'.format(float(self.subtotal))
                inv_save.tax = '{0:.2f}'.format(float(self.tax))
                inv_save.reward_id = inv['reward_id']
                inv_save.discount_id = self.discount_id if self.discount_id is not None else inv['discount_id']
                inv_save.rack = inv['rack']
                inv_save.rack_date = inv['rack_date']
                inv_save.due_date = self.due_date
                inv_save.memo = inv['memo']
                inv_save.transaction_id = inv['transaction_id']
                inv_save.schedule_id = inv['schedule_id']
                inv_save.status = inv['status']
                inv_save.total = '{0:.2f}'.format(float(self.total))
                if inv_save.update():
                    print('updated invoice')
                    vars.CUSTOMER_ID = self.customer_id_backup
                    vars.SEARCH_RESULTS_STATUS = True


class EditCustomerScreen(Screen):
    last_name = ObjectProperty(None)
    first_name = ObjectProperty(None)
    phone = ObjectProperty(None)
    email = ObjectProperty(None)
    important_memo = ObjectProperty(None)
    invoice_memo = ObjectProperty(None)
    shirt_finish = 1
    shirt_preference = 1
    shirt_finish_spinner = ObjectProperty(None)
    shirt_preference_spinner = ObjectProperty(None)
    is_delivery = ObjectProperty(None)
    is_account = ObjectProperty(None)
    mark_text = ObjectProperty(None)
    marks_table = ObjectProperty(None)
    street = ObjectProperty(None)
    suite = ObjectProperty(None)
    city = ObjectProperty(None)
    zipcode = ObjectProperty(None)
    concierge_name = ObjectProperty(None)
    concierge_number = ObjectProperty(None)
    special_instructions = ObjectProperty(None)
    address_id = None
    delete_customer_spinner = ObjectProperty(None)
    delete_customer = None
    popup = Popup()
    tab_new_customer = ObjectProperty(None)
    new_customer_panel = ObjectProperty(None)

    def reset(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
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
        self.address_id = None
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
        self.is_account.active = False
        self.delete_customer = False
        # reset spinner values
        self.marks_table.clear_widgets()
        # back to main tab

        self.new_customer_panel.switch_to(header=self.tab_new_customer)

    def load(self):
        self.reset()
        if vars.CUSTOMER_ID:
            customers = User()
            customers.user_id = vars.CUSTOMER_ID
            addresses = Address().where({'user_id': vars.CUSTOMER_ID,
                                         'primary_address': 1})
            data = {'user_id': vars.CUSTOMER_ID}
            customer = customers.where(data)
            self.shirt_finish_spinner.bind(text=self.select_shirts_finish)
            self.shirt_preference_spinner.bind(text=self.select_shirts_preference)
            self.delete_customer_spinner.bind(text=self.select_delete_customer)

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
                    self.shirt_finish_spinner.text = 'Hanger' if cust['shirt'] is 1 else 'Box'
                    self.delete_customer_spinner.text = "No"
                    self.shirt_finish = cust['shirt']

                    if cust['starch'] == 1:
                        self.shirt_preference_spinner.text = 'None'
                        self.shirt_preference = 1
                    if cust['starch'] == 2:
                        self.shirt_preference_spinner.text = 'Light'
                        self.shirt_preference = 2
                    if cust['starch'] == 3:
                        self.shirt_preference_spinner.text = 'Medium'
                        self.shirt_preference = 3
                    if cust['starch'] == 4:
                        self.shirt_preference_spinner.text = 'Heavy'
                        self.shirt_preference = 4

                    # delete customer


                    # if addresses:
                    #     for address in addresses:
                    #         self.address_id = address['id']
                    #         self.is_delivery.active = True
                    #
                    #         self.concierge_name.text = address['concierge_name'] if address['concierge_name'] else ''
                    #         self.concierge_name.hint_text = 'Concierge Name'
                    #         self.concierge_name.hint_text_color = DEFAULT_COLOR
                    #         self.concierge_name.disabled = False
                    #         self.concierge_number.text = address['concierge_number'] if address[
                    #             'concierge_number'] else ''
                    #         self.concierge_number.hint_text = 'Concierge Number'
                    #         self.concierge_number.hint_text_color = DEFAULT_COLOR
                    #         self.concierge_number.disabled = False
                    #         # self.special_instructions.text = address['special_instructions'] if address[
                    #         #     'special_instructions'] else ''
                    #         self.special_instructions.hint_text = 'Special Instructions'
                    #         self.special_instructions.hint_text_color = DEFAULT_COLOR
                    #         self.special_instructions.disabled = False

                    self.update_marks_table()

                    if cust['account'] is 1:
                        self.is_account.active = True
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
                    else:
                        self.is_account.active = False
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
                        self.mark_text.text = ''

    def select_shirts_finish(self, *args, **kwargs):
        self.shirt_finish = self.shirt_finish_spinner.text
        if self.shirt_finish_spinner.text is 'Hanger':
            self.shirt_finish = 1
        elif self.shirt_finish_spinner.text is 'Box':
            self.shirt_finish = 2

        print(self.shirt_finish)

    def select_shirts_preference(self, *args, **kwargs):
        self.shirt_preference = 0
        if self.shirt_preference_spinner.text is 'None':
            self.shirt_preference = 1
        elif self.shirt_preference_spinner.text is 'Light':
            self.shirt_preference = 2
        elif self.shirt_preference_spinner.text is 'Medium':
            self.shirt_preference = 3
        elif self.shirt_preference_spinner.text is 'Heavy':
            self.shirt_preference = 4
        print(self.shirt_preference)

    def select_delete_customer(self, *args, **kwargs):
        if self.delete_customer_spinner.text is 'Yes':
            self.popup.title = 'Are you sure?'
            content = BoxLayout(orientation="vertical")
            inner_layout_1 = BoxLayout(orientation="horizontal",
                                       size_hint=(1, 0.9))
            msg = Label(text="Are you sure you wish to delete this customer?")
            inner_layout_1.add_widget(msg)
            inner_layout_2 = BoxLayout(orientation="horizontal",
                                       size_hint=(1, 0.1))
            cancel = Button(text="cancel",
                            on_release=self.popup.dismiss)
            delete_btn = Button(markup=True,
                                text="[color=FF0000]Delete[/color]",
                                on_release=self.delete_final)
            inner_layout_2.add_widget(cancel)
            inner_layout_2.add_widget(delete_btn)
            content.add_widget(inner_layout_1)
            content.add_widget(inner_layout_2)
            self.popup.content = content
            self.popup.open()

        pass

    def delete_final(self, *args, **kwargs):
        customer = User()
        customers = customer.where({'user_id': vars.CUSTOMER_ID})
        if customer:
            for cust in customers:
                customer.id = cust['id']
                if (customer.delete()):
                    t1 = Thread(target=SYNC.db_sync, args=[vars.COMPANY_ID])
                    t1.start()
                    vars.SEARCH_RESULTS_STATUS = False
                    vars.ROW_CAP = 0
                    vars.CUSTOMER_ID = None
                    vars.INVOICE_ID = None
                    vars.ROW_SEARCH = 0, 9

                    self.parent.current = 'search'
                    self.popup.dismiss()
                    popup = Popup()
                    popup.content = Builder.load_string(KV.popup_alert("Sucessfully deleted customer from system"))
                    popup.open()
                    # last 10 setup
                    vars.update_last_10()

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
            marks.company_id = vars.COMPANY_ID
            marks.customer_id = vars.CUSTOMER_ID
            marks.mark = self.mark_text.text
            marks.status = 1
            if marks.add():
                # update the marks table
                self.mark_text.text = ''
                self.update_marks_table()
                marks.close_connection()
                popup.title = 'Success'
                popup.content = Builder.load_string(KV.popup_alert('Successfully added a new mark!'))
                popup.open()

    def set_delivery(self):

        self.concierge_name.hint_text = 'Concierge Name'
        self.concierge_name.hint_text_color = DEFAULT_COLOR
        self.concierge_name.disabled = False if self.is_delivery.active else True

        self.concierge_number.hint_text = 'Concierge Number'
        self.concierge_number.hint_text_color = DEFAULT_COLOR
        self.concierge_number.disabled = False if self.is_delivery.active else True

        self.special_instructions.hint_text = 'Special Instructions'
        self.special_instructions.hint_text_color = DEFAULT_COLOR
        self.special_instructions.disabled = False if self.is_delivery.active else True

    def set_account(self):
        self.street.hint_text = 'Street Address'
        self.street.hint_text_color = DEFAULT_COLOR
        self.street.disabled = False if self.is_account.active else True

        self.suite.hint_text = 'Suite'
        self.suite.hint_text_color = DEFAULT_COLOR
        self.suite.disabled = False if self.is_account.active else True

        self.city.hint_text = 'City'
        self.city.hint_text_color = DEFAULT_COLOR
        self.city.disabled = False if self.is_account.active else True

        self.zipcode.hint_text = 'Zipcode'
        self.zipcode.hint_text_color = DEFAULT_COLOR
        self.zipcode.disabled = False if self.is_account.active else True

    def delete_mark(self, mark=False, *args, **kwargs):
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
                text_color = 'e5e5e5' if even_odd % 2 == 0 else '000000'
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
                    check_phone = cd['phone']
                    if cd['user_id'] != vars.CUSTOMER_ID and check_phone is phone:
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

        # if self.email.text and not Job.check_valid_email(self.email.text):
        #     errors += 1
        #     self.email.text = ''
        #     self.email.hint_text = 'Not valid'
        #     self.email.hint_text_color = ERROR_COLOR

        # Check if delivery is active
        if self.is_delivery.active:
            pass

        if self.is_account.active:
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
            data = {
                'company_id': vars.COMPANY_ID,
                'phone': Job.make_numeric(data=self.phone.text),
                'last_name': Job.make_no_whitespace(data=self.last_name.text),
                'first_name': Job.make_no_whitespace(data=self.first_name.text),
                'email': self.email.text if Job.check_valid_email(email=self.email.text) else None,
                'invoice_memo': self.invoice_memo.text if self.invoice_memo.text else None,
                'important_memo': self.important_memo.text if self.important_memo.text else None,
                'shirt': str(self.shirt_finish),
                'starch': str(self.shirt_preference),
                'street': self.street.text,
                'suite': Job.make_no_whitespace(data=self.suite.text),
                'city': Job.make_no_whitespace(data=self.city.text),
                'zipcode': Job.make_no_whitespace(data=self.zipcode.text),
                'concierge_name': self.concierge_name.text,
                'concierge_number': Job.make_numeric(data=self.concierge_number.text),
                'special_instructions': self.special_instructions.text if self.special_instructions.text else None,
                'account': 1 if self.is_account.active else 0
            }

            # if self.is_account.active:
            #
            #     # check address or else save
            #     if self.address_id:
            #         addr_where = {'id': self.address_id}
            #         addr_data = {'name': 'Home',
            #                      'street': self.street.text,
            #                      'suite': Job.make_no_whitespace(data=self.suite.text),
            #                      'city': Job.make_no_whitespace(data=self.city.text),
            #                      'zipcode': Job.make_no_whitespace(data=self.zipcode.text),
            #                      'concierge_name': self.concierge_name.text,
            #                      'special_instructions': self.special_instructions.text if self.special_instructions.text else None
            #                      }
            #         Address().put(where=addr_where, data=addr_data)
            if customers.put(where=where, data=data):
                # create the customer mark
                # marks = Custid()
                #
                # updated_mark = marks.create_customer_mark(last_name=self.last_name.text,
                #                                           customer_id=str(vars.CUSTOMER_ID),
                #                                           starch=customers.get_starch(self.shirt_preference))
                # where = {'customer_id': vars.CUSTOMER_ID}
                # data = {'mark': updated_mark}
                # marks.put(where=where, data=data)
                run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
                try:
                    run_sync.start()
                finally:
                    run_sync.join()
                    self.reset()
                    self.customer_select(vars.CUSTOMER_ID)
                    # create popup
                    content = KV.popup_alert("You have successfully edited this customer.")
                    popup.content = Builder.load_string(content)
                    popup.open()

            customers.close_connection()
        else:
            popup = Popup()
            popup.title = 'Edit Error'
            content = KV.popup_alert(
                '{} Errors in your form. Please check to see if account or delivery is improperly set.'.format(errors))
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()

    def customer_select(self, customer_id, *args, **kwargs):
        vars.SEARCH_RESULTS_STATUS = True
        vars.ROW_CAP = 0
        vars.CUSTOMER_ID = customer_id
        vars.INVOICE_ID = None
        vars.ROW_SEARCH = 0, 9
        self.parent.current = 'search'
        # last 10 setup
        vars.update_last_10()


class EmployeesScreen(Screen):
    employees_table = ObjectProperty(None)
    employee_id = None
    employee_popup = Popup()
    username = None
    first_name = None
    last_name = None
    phone = None
    email = None
    role_id = None
    password = None

    def reset(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
        self.create_table()
        self.employee_id = None
        self.username = None
        self.first_name = None
        self.last_name = None
        self.phone = None
        self.email = None
        self.role_id = None
        self.password = None
        pass

    pass

    def create_table(self):
        self.employees_table.clear_widgets()
        h1 = KV.invoice_tr(0, 'Role')
        h2 = KV.invoice_tr(0, 'User')
        h3 = KV.invoice_tr(0, 'First')
        h4 = KV.invoice_tr(0, 'Last')
        h5 = KV.invoice_tr(0, 'Phone')
        h6 = KV.invoice_tr(0, 'Email')
        h7 = KV.invoice_tr(0, 'A')

        self.employees_table.add_widget(Builder.load_string(h1))
        self.employees_table.add_widget(Builder.load_string(h2))
        self.employees_table.add_widget(Builder.load_string(h3))
        self.employees_table.add_widget(Builder.load_string(h4))
        self.employees_table.add_widget(Builder.load_string(h5))
        self.employees_table.add_widget(Builder.load_string(h6))
        self.employees_table.add_widget(Builder.load_string(h7))

        users = User()
        employees = users.where({'company_id': vars.COMPANY_ID,
                                 'role_id': {'<': 5}})

        if employees:
            for employee in employees:
                c1 = Label(text=str(employee['role_id']))
                c2 = Label(text=str(employee['username']))
                c3 = Label(text=str(employee['first_name']))
                c4 = Label(text=str(employee['last_name']))
                c5 = Label(text=str(employee['phone']))
                c6 = Label(text=str(employee['email']))
                c7 = BoxLayout(orientation='horizontal')
                edit_button = Button(text='edit',
                                     on_press=partial(self.set_employee, employee['user_id']),
                                     on_release=self.edit_employee_popup)
                remove_button = Button(markup=True,
                                       text='[color=ff0000][b]delete[/b][/color]',
                                       on_press=partial(self.set_employee, employee['user_id']),
                                       on_release=self.delete_employee_confirm)
                c7.add_widget(edit_button)
                c7.add_widget(remove_button)
                self.employees_table.add_widget(c1)
                self.employees_table.add_widget(c2)
                self.employees_table.add_widget(c3)
                self.employees_table.add_widget(c4)
                self.employees_table.add_widget(c5)
                self.employees_table.add_widget(c6)
                self.employees_table.add_widget(c7)

    def set_employee(self, id, *args, **kwargs):
        self.employee_id = id

    def add_employee_popup(self):
        self.employee_popup.title = 'Add Employee Info'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='vertical')
        add_table = GridLayout(size_hint=(1, 0.9),
                               cols=2,
                               rows=7,
                               row_force_default=True,
                               row_default_height='50sp',
                               spacing='5sp')
        add_table.add_widget(Factory.CenteredFormLabel(text='Username:'))
        self.username = Factory.CenterVerticalTextInput()
        add_table.add_widget(self.username)
        add_table.add_widget(Factory.CenteredFormLabel(text='First Name:'))
        self.first_name = Factory.CenterVerticalTextInput()
        add_table.add_widget(self.first_name)
        add_table.add_widget(Factory.CenteredFormLabel(text='Last Name:'))
        self.last_name = Factory.CenterVerticalTextInput()
        add_table.add_widget(self.last_name)
        add_table.add_widget(Factory.CenteredFormLabel(text='Phone:'))
        self.phone = Factory.CenterVerticalTextInput()
        add_table.add_widget(self.phone)
        add_table.add_widget(Factory.CenteredFormLabel(text='Email:'))
        self.email = Factory.CenterVerticalTextInput()
        add_table.add_widget(self.email)
        add_table.add_widget(Factory.CenteredFormLabel(text='Password:'))
        self.password = Factory.CenterVerticalTextInput()
        add_table.add_widget(self.password)
        inner_layout_1.add_widget(add_table)
        inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                   orientation='horizontal')
        inner_layout_2.add_widget(Button(text='cancel',
                                         on_release=self.employee_popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=00ff00][b]add[/b][/color]',
                                         on_release=self.add_employee))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.employee_popup.content = layout
        self.employee_popup.open()

    def edit_employee_popup(self, *args, **kwargs):
        username = ''
        first_name = ''
        last_name = ''
        phone = ''
        email = ''
        password = ''
        users = User()
        employees = users.where({'user_id': self.employee_id})
        if employees:
            for employee in employees:
                username = employee['username']
                first_name = employee['first_name']
                last_name = employee['last_name']
                phone = employee['phone']
                email = employee['email']
                password = employee['password']
        self.employee_popup.title = 'Edit Employee Info'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='vertical')
        edit_table = GridLayout(size_hint=(1, 0.9),
                                cols=2,
                                rows=7,
                                row_force_default=True,
                                row_default_height='50sp',
                                spacing='5sp')
        edit_table.add_widget(Factory.CenteredFormLabel(text='Username:'))
        self.username = Factory.CenterVerticalTextInput(text=str(username))
        edit_table.add_widget(self.username)
        edit_table.add_widget(Factory.CenteredFormLabel(text='First Name:'))
        self.first_name = Factory.CenterVerticalTextInput(text=str(first_name))
        edit_table.add_widget(self.first_name)
        edit_table.add_widget(Factory.CenteredFormLabel(text='Last Name:'))
        self.last_name = Factory.CenterVerticalTextInput(text=str(last_name))
        edit_table.add_widget(self.last_name)
        edit_table.add_widget(Factory.CenteredFormLabel(text='Phone:'))
        self.phone = Factory.CenterVerticalTextInput(text=str(phone))
        edit_table.add_widget(self.phone)
        edit_table.add_widget(Factory.CenteredFormLabel(text='Email:'))
        self.email = Factory.CenterVerticalTextInput(text=str(email))
        edit_table.add_widget(self.email)
        edit_table.add_widget(Factory.CenteredFormLabel(text='New Password:'))
        self.password = Factory.CenterVerticalTextInput(text=str(password),
                                                        hint_text='Optional')
        edit_table.add_widget(self.password)
        inner_layout_1.add_widget(edit_table)
        inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                   orientation='horizontal')
        inner_layout_2.add_widget(Button(text='cancel',
                                         on_release=self.employee_popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=00ff00][b]edit[/b][/color]',
                                         on_release=self.edit_employee))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.employee_popup.content = layout
        self.employee_popup.open()
        pass

    def add_employee(self, *args, **kwargs):

        errors = 0

        if self.username.text is None:
            errors += 1
            self.username.hint_text_color = ERROR_COLOR
            self.username.hint_text = 'Cannot be empty'
        else:
            self.username.hint_text_color = DEFAULT_COLOR
            self.username.hint_text = ''

        if self.first_name.text is None:
            errors += 1
            self.first_name.hint_text_color = ERROR_COLOR
            self.first_name.hint_text = 'Cannot be empty'
        else:
            self.first_name.hint_text_color = DEFAULT_COLOR
            self.first_name.hint_text = ''

        if self.last_name.text is None:
            errors += 1
            self.last_name.hint_text_color = ERROR_COLOR
            self.last_name.hint_text = 'Cannot be empty'
        else:
            self.last_name.hint_text_color = DEFAULT_COLOR
            self.last_name.hint_text = ''

        if self.phone.text is None:
            errors += 1
            self.phone.hint_text_color = ERROR_COLOR
            self.phone.hint_text = 'Cannot be empty'
        else:
            self.phone.hint_text_color = DEFAULT_COLOR
            self.phone.hint_text = ''

        if self.email.text is None:
            errors += 1
            self.email.hint_text_color = ERROR_COLOR
            self.email.hint_text = 'Cannot be empty'
        else:
            self.email.hint_text_color = DEFAULT_COLOR
            self.email.hint_text = ''

        if self.password.text is None:
            errors += 1
            self.password.hint_text_color = ERROR_COLOR
            self.password.hint_text = 'Cannot be empty'
        else:
            self.password.hint_text_color = DEFAULT_COLOR
            self.password.hint_text = ''

        if errors == 0:
            users = User()
            users.company_id = vars.COMPANY_ID
            users.username = self.username.text
            users.first_name = self.first_name.text
            users.last_name = self.last_name.text
            users.phone = self.phone.text
            users.email = self.email.text
            users.password = self.password.text
            users.role_id = 3  # employees

            if users.add():
                popup = Popup()
                popup.title = 'Add Employee'
                popup.content = Builder.load_string(KV.popup_alert('Successfully Added employee!'))
                popup.open()
        else:
            popup = Popup()
            popup.title = 'Add Employee'
            popup.content = Builder.load_string(KV.popup_alert('{} errors. Please fix then continue.'.format(errors)))
            popup.open()
        self.employee_popup.dismiss()
        self.reset()

    def edit_employee(self, *args, **kwargs):

        errors = 0

        if self.username.text is None:
            errors += 1
            self.username.hint_text_color = ERROR_COLOR
            self.username.hint_text = 'Cannot be empty'
        else:
            self.username.hint_text_color = DEFAULT_COLOR
            self.username.hint_text = ''

        if self.first_name.text is None:
            errors += 1
            self.first_name.hint_text_color = ERROR_COLOR
            self.first_name.hint_text = 'Cannot be empty'
        else:
            self.first_name.hint_text_color = DEFAULT_COLOR
            self.first_name.hint_text = ''

        if self.last_name.text is None:
            errors += 1
            self.last_name.hint_text_color = ERROR_COLOR
            self.last_name.hint_text = 'Cannot be empty'
        else:
            self.last_name.hint_text_color = DEFAULT_COLOR
            self.last_name.hint_text = ''

        if self.phone.text is None:
            errors += 1
            self.phone.hint_text_color = ERROR_COLOR
            self.phone.hint_text = 'Cannot be empty'
        else:
            self.phone.hint_text_color = DEFAULT_COLOR
            self.phone.hint_text = ''

        if self.email.text is None:
            errors += 1
            self.email.hint_text_color = ERROR_COLOR
            self.email.hint_text = 'Cannot be empty'
        else:
            self.email.hint_text_color = DEFAULT_COLOR
            self.email.hint_text = ''

        if errors == 0:
            users = User()
            if self.password.text is None:
                put = users.put(where={'user_id': self.employee_id},
                                data={'username': self.username.text,
                                      'first_name': self.first_name.text,
                                      'last_name': self.last_name.text,
                                      'phone': self.phone.text,
                                      'email': self.email.text})
            else:
                put = users.put(where={'user_id': self.employee_id},
                                data={'username': self.username.text,
                                      'first_name': self.first_name.text,
                                      'last_name': self.last_name.text,
                                      'phone': self.phone.text,
                                      'email': self.email.text,
                                      'password': self.password.text})
            if put:
                popup = Popup()
                popup.title = 'Edit Employee'
                popup.content = Builder.load_string(KV.popup_alert('Successfully edited employee!'))
                popup.open()
        else:
            popup = Popup()
            popup.title = 'Edit Employee'
            popup.content = Builder.load_string(KV.popup_alert('{} errors. Please fix then continue.'.format(errors)))
            popup.open()
        self.employee_popup.dismiss()
        self.reset()

    def delete_employee_confirm(self, *args, **kwargs):
        popup = Popup()
        popup.title = 'Delete Confirmation'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='vertical',
                                   size_hint=(1, 0.9))
        inner_layout_1.add_widget(Label(text='Are you sure you wish to delete employee?'))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(text='cancel',
                                         on_release=popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=00ff00][b]Delete[/b][/color]',
                                         on_release=self.delete_employee))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def delete_employee(self, *args, **kwargs):
        users = User()
        employees = users.where({'user_id': self.employee_id})
        count = 0
        if employees:
            for employee in employees:
                e_id = employee['id']
                users.id = e_id
                if users.delete():
                    count += 1

        popup = Popup()
        popup.title = 'Employee Deleted'
        popup.content = Builder.load_string(KV.popup_alert('{} employee(s) deleted.'.format(count)))
        popup.open()

        self.reset()


class HistoryScreen(Screen):
    invoices_table = ObjectProperty(None)
    invoice_table_body = ObjectProperty(None)
    item_image = ObjectProperty(None)
    items_table = ObjectProperty(None)
    invs_results_label = ObjectProperty(None)
    history_popup = ObjectProperty(None)
    status_spinner = ObjectProperty(None)
    starch = None
    selected_tags_list = []
    tags_grid = ObjectProperty(None)
    row_set = 0
    row_increment = 10
    up_btn = ObjectProperty(None)
    down_btn = ObjectProperty(None)

    def reset(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
        # check if an invoice was previously selected
        self.items_table.clear_widgets()

        # set any necessary variables
        customers = User().where({'user_id': vars.CUSTOMER_ID})
        if customers:
            for customer in customers:
                self.starch = vars.get_starch_by_code(customer['starch'])
        else:
            self.starch = vars.get_starch_by_code(None)

        # create the invoice count list

        invoices = Invoice()
        data = {'customer_id': vars.CUSTOMER_ID}
        vars.ROW_CAP = len(invoices.where(data=data, deleted_at=False))
        if vars.ROW_CAP < 10 and vars.ROW_CAP <= self.row_set:
            self.row_set = 0

        row_end = self.row_set + 9
        self.invs_results_label.text = '[color=000000]Showing rows [b]{}[/b] - [b]{}[/b] out of [b]{}[/b][/color]'.format(
            self.row_set,
            row_end,
            vars.ROW_CAP
        )
        data = {
            'customer_id': '"%{}%"'.format(vars.CUSTOMER_ID),
            'ORDER_BY': 'id DESC',
            'LIMIT': '{},{}'.format(self.row_set, self.row_increment)
        }
        invoices = Invoice()
        invs = invoices.like(data=data, deleted_at=False)
        vars.SEARCH_RESULTS = invs
        # get invoice rows and display them to the table

        # create Tbody TR
        self.invoice_table_body.clear_widgets()
        if len(vars.SEARCH_RESULTS) > 0:
            for cust in vars.SEARCH_RESULTS:
                self.create_invoice_row(cust)

        vars.SEARCH_RESULTS = []

        if vars.INVOICE_ID:
            self.items_table_update()

        SYNC_POPUP.dismiss()

    def open_popup(self, *args, **kwargs):
        SYNC_POPUP.title = "Loading"
        content = KV.popup_alert("Please wait while the page is loading")
        SYNC_POPUP.content = Builder.load_string(content)
        SYNC_POPUP.open()

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
        invoice_items = InvoiceItem().where({'invoice_id': invoice_id})
        count_invoice_items = len(invoice_items)
        deleted_at = row['deleted_at']
        transaction_id = row['transaction_id']
        try:
            dt = datetime.datetime.strptime(due, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = datetime.datetime.strptime('1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
        due_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        dow = vars.dow(dt.replace(tzinfo=datetime.timezone.utc).weekday())
        due_date = dt.strftime('%m/%d {}').format(dow)
        try:
            dt = datetime.datetime.strptime(NOW, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = datetime.datetime.strptime('1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")

        now_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        invoice_status = row['status']
        selected = True if invoice_id == check_invoice_id else False
        if deleted_at:
            state = 4
        else:
            if invoice_status is 5:
                state = 5
            elif invoice_status is 4:
                state = 4
            elif invoice_status is 3:
                state = 4
            elif invoice_status is 2:
                state = 3
            else:
                if due_strtotime < now_strtotime:  # overdue
                    state = 2
                elif count_invoice_items == 0:  # #quick drop
                    state = 6
                else:
                    state = 1

        if state is 1:
            text_color = [0.898, 0.898, 0.898, 1] if selected else [0, 0, 0, 1]
            background_rgba = [0.369, 0.369, 0.369, 0.1] if selected else [0.826, 0.826, 0.826, 0.1]
            background_color = [0.369, 0.369, 0.369, 1] if selected else [0.826, 0.826, 0.826, 1]
        elif state is 2:
            text_color = [0.8157, 0.847, 0.961, 1] if selected else [0.059, 0.278, 1, 1]
            background_rgba = [0.059, 0.278, 1, 0.1] if selected else [0.816, 0.847, 0.961, 0.1]
            background_color = [0.059, 0.278, 1, 1] if selected else [0.816, 0.847, 0.961, 1]
        elif state is 3:
            text_color = [0.847, 0.967, 0.847, 1] if selected else [0, 0.639, 0.149, 1]
            background_rgba = [0, 0.64, 0.149, 0.1] if selected else [0.847, 0.968, 0.847, 0.1]
            background_color = [0, 0.64, 0.149, 1] if selected else [0.847, 0.968, 0.847, 1]
        elif state is 4:
            text_color = [1, 0.8, 0.8, 1] if selected else [1, 0, 0, 1]
            background_rgba = [1, 0, 0, 0.1] if selected else [1, 0.717, 0.717, 0.1]
            background_color = [1, 0, 0, 1] if selected else [1, 0.717, 0.717, 1]
        elif state is 5:
            text_color = [0.898, 0.898, 0.898, 1] if selected else [0, 0, 0, 1]
            background_rgba = [0.369, 0.369, 0.369, 0.1] if selected else [0.826, 0.826, 0.826, 0.1]
            background_color = [0.369, 0.369, 0.369, 1] if selected else [0.826, 0.826, 0.826, 1]
        else:
            text_color = [0, 0, 0, 1] if selected else [0, 0, 0, 1]
            background_rgba = [0.98431373, 1, 0, 0.1] if selected else [0.9960784314, 1, 0.7176470588, 1]
            background_color = [0.98431373, 1, 0, 1] if selected else [0.9960784314, 1, 0.7176470588, 1]
        tr = Factory.InvoiceTr(on_release=partial(self.select_invoice, invoice_id),
                               group="tr")
        tr.status = state
        tr.set_color = background_color
        tr.background_color = background_rgba
        label_1 = Label(markup=True,
                        color=text_color,
                        text="{}".format('{0:06d}'.format(invoice_id)))
        tr.ids.invoice_table_row_td.add_widget(label_1)
        label_2 = Label(markup=True,
                        color=text_color,
                        text='{}'.format(company_id))
        tr.ids.invoice_table_row_td.add_widget(label_2)
        label_3 = Label(markup=True,
                        color=text_color,
                        text='{}'.format(due_date))
        tr.ids.invoice_table_row_td.add_widget(label_3)
        label_4 = Label(markup=True,
                        color=text_color,
                        text='{}'.format(rack))
        tr.ids.invoice_table_row_td.add_widget(label_4)
        label_5 = Label(markup=True,
                        color=text_color,
                        text='{}'.format(quantity))
        tr.ids.invoice_table_row_td.add_widget(label_5)
        label_6 = Label(markup=True,
                        color=text_color,
                        text='{}'.format(total))
        tr.ids.invoice_table_row_td.add_widget(label_6)

        self.invoice_table_body.add_widget(tr)

        return True

    def reprint(self):
        pass

    def undo(self):
        pass

    def set_result_status(self):
        vars.SEARCH_RESULTS_STATUS = True
        # update db with current changes
        t1 = Thread(target=SYNC.db_sync, args=[vars.COMPANY_ID])
        t1.start()
        t1.join()
        # vars.WORKLIST.append("Sync")
        # threads_start()

    def select_invoice(self, invoice_id, *args, **kwargs):
        # set selected invoice and update the table to show it
        vars.INVOICE_ID = invoice_id

        # check state of button and update rows
        for child in self.invoice_table_body.children:
            if child.state is 'down':
                # find status and change the background color

                if child.status is 1:
                    text_color = [0.898, 0.898, 0.898, 1]
                    child.background_color = [0.369, 0.369, 0.369, 0.1]
                    child.set_color = [0.369, 0.369, 0.369, 1]
                elif child.status is 2:
                    text_color = [0.8156, 0.847, 0.961, 1]
                    child.background_color = [0.059, 0.278, 1, 0.1]
                    child.set_color = [0.059, 0.278, 1, 1]
                elif child.status is 3:
                    text_color = [0.847, 0.969, 0.847, 1]
                    child.background_color = [0, 0.64, 0.149, 0.1]
                    child.set_color = [0, 0.64, 0.149, 1]
                elif child.status is 4:
                    text_color = [1, 0.8, 0.8, 1]
                    child.background_color = [1, 0, 0, 0.1]
                    child.set_color = [1, 0, 0, 1]
                elif child.status is 5:
                    text_color = [0.898, 0.898, 0.898, 1]
                    child.background_color = [0.369, 0.369, 0.369, 0.1]
                    child.set_color = [0.369, 0.369, 0.369, 1]
                else:
                    text_color = [0, 0, 0, 1]
                    child.background_color = [0.98431373, 1, 0, 0.1]
                    child.set_color = [0.98431373, 1, 0, 1]
            else:
                if child.status is 1:
                    text_color = [0, 0, 0, 1]
                    child.background_color = [0.826, 0.826, 0.826, 0.1]
                    child.set_color = [0.826, 0.826, 0.826, 1]
                elif child.status is 2:
                    text_color = [0.059, 0.278, 1, 1]
                    child.background_color = [0.816, 0.847, 0.961, 0.1]
                    child.set_color = [0.816, 0.847, 0.961, 1]
                elif child.status is 3:
                    text_color = [0, 0.639, 0.149, 1]
                    child.background_color = [0.847, 0.968, 0.847, 0.1]
                    child.set_color = [0.847, 0.968, 0.847, 1]
                elif child.status is 4:
                    text_color = [1, 0, 0, 1]
                    child.background_color = [1, 0.717, 0.717, 0.1]
                    child.set_color = [1, 0.717, 0.717, 1]
                elif child.status is 5:
                    text_color = [0, 0, 0, 1]
                    child.background_color = [0.826, 0.826, 0.826, 0.1]
                    child.set_color = [0.826, 0.826, 0.826, 1]
                else:
                    text_color = [0, 0, 0, 1]
                    child.background_color = [0.9960784314, 1, 0.7176470588, 0.1]
                    child.set_color = [0.9960784314, 1, 0.7176470588, 1]
            for grandchild in child.children:
                for ggc in grandchild.children:
                    ggc.color = text_color
        # self.reset()
        self.items_table_update()

    def invoice_next(self):
        self.row_set += self.row_increment
        self.down_btn.disabled = True if (self.row_set + 10) > vars.ROW_CAP else False
        # if vars.ROW_SEARCH[1] + 10 >= vars.ROW_CAP:
        #     vars.ROW_SEARCH = vars.ROW_CAP - 10, vars.ROW_CAP
        # else:
        #     vars.ROW_SEARCH = vars.ROW_SEARCH[1] + 1, vars.ROW_SEARCH[1] + 10

        self.reset()
        self.up_btn.disabled = True if self.row_set <= 0 else False

    def invoice_prev(self):
        row_prev = self.row_set - self.row_increment
        self.up_btn.disabled = True if self.row_set - self.row_increment <= 0 else False

        self.row_set = 0 if self.row_set - self.row_increment <= 0 else row_prev
        # if vars.ROW_SEARCH[0] - 10 < 10:
        #     vars.ROW_SEARCH = 0, 10
        # else:
        #     vars.ROW_SEARCH = vars.ROW_SEARCH[0] - 10, vars.ROW_SEARCH[1] - 10

        self.reset()
        self.down_btn.disabled = False if self.row_set < vars.ROW_CAP else True

    def items_table_update(self):
        self.items_table.clear_widgets()
        invoices = Invoice().where({'invoice_id': vars.INVOICE_ID}, deleted_at=False)
        if invoices:
            for invoice in invoices:
                invoice_deleted = True if invoice['deleted_at'] else False
        else:
            invoice_deleted = False

        iitems = InvoiceItem()
        data = {'invoice_id': vars.INVOICE_ID}
        inv_items = iitems.where(data,
                                 deleted_at=False if invoice_deleted else True)
        if inv_items:
            # create headers
            # create TH
            h1 = KV.sized_invoice_tr(0, 'Qty', size_hint_x=0.2)
            h2 = KV.sized_invoice_tr(0, 'Item', size_hint_x=0.6)
            h3 = KV.sized_invoice_tr(0, 'Subtotal', size_hint_x=0.2)
            self.items_table.add_widget(Builder.load_string(h1))
            self.items_table.add_widget(Builder.load_string(h2))
            self.items_table.add_widget(Builder.load_string(h3))
            items = {}

            for invoice_item in inv_items:
                item_id = invoice_item['item_id']
                items_search = InventoryItem()
                itm_srch = items_search.where({'item_id': item_id})
                if itm_srch:
                    for itm in itm_srch:
                        item_name = itm['name']
                        inventory_id = itm['inventory_id']
                else:
                    item_name = ''
                    inventory_id = None

                inventories = Inventory().where({'inventory_id': inventory_id})
                if inventories:
                    for inventory in inventories:
                        laundry = inventory['laundry']
                else:
                    laundry = 0

                items[item_id] = {
                    'id': invoice_item['id'],
                    'name': '{} ({})'.format(item_name, self.starch) if laundry else item_name,
                    'total': 0,
                    'quantity': 0,
                    'color': {},
                    'memo': []
                }
            # populate correct item totals
            if items:
                for key, value in items.items():
                    item_id = key
                    data = {
                        'invoice_id': vars.INVOICE_ID,
                        'item_id': item_id
                    }
                    iinv_items = InvoiceItem().where(data)
                    if iinv_items:
                        for inv_item in iinv_items:
                            items[item_id]['quantity'] += int(inv_item['quantity']) if inv_item['quantity'] else 1
                            items[item_id]['total'] += float(inv_item['pretax']) if inv_item['pretax'] else 0
                            if inv_item['color'] in items[item_id]['color']:
                                items[item_id]['color'][inv_item['color']] += 1
                            else:
                                items[item_id]['color'][inv_item['color']] = 1
                            if inv_item['memo']:
                                items[item_id]['memo'].append(inv_item['memo'])
            # print out the items into the table
            if items:
                for key, value in items.items():
                    tr1 = KV.sized_invoice_tr(1,
                                              value['quantity'],
                                              size_hint_x=0.2,
                                              on_release='app.root.current="item_details"',
                                              on_press='self.parent.parent.parent.parent.item_details({})'.format(key))
                    color_string = []
                    for color_name, color_qty in value['color'].items():
                        if color_name:
                            color_string.append('{count}-{name}'.format(count=str(color_qty), name=color_name))

                    item_string = "[b]{item}[/b]:\\n {color_s} {memo_s}".format(item=value['name'],
                                                                                color_s=', '.join(color_string),
                                                                                memo_s='/ '.join(value['memo']))
                    tr2 = KV.sized_invoice_tr(1,
                                              item_string,
                                              text_wrap=True,
                                              size_hint_x=0.6,
                                              on_release='app.root.current="item_details"',
                                              on_press='self.parent.parent.parent.parent.item_details({})'.format(key))

                    tr3 = KV.sized_invoice_tr(1,
                                              '${:,.2f}'.format(value['total']),
                                              size_hint_x=0.2,
                                              on_release='app.root.current="item_details"',
                                              on_press='self.parent.parent.parent.parent.item_details({})'.format(key))
                    self.items_table.add_widget(Builder.load_string(tr1))
                    self.items_table.add_widget(Builder.load_string(tr2))
                    self.items_table.add_widget(Builder.load_string(tr3))

    def item_details(self, item_id):
        vars.ITEM_ID = item_id

    def delete_invoice_confirm(self):
        self.history_popup = Popup()
        self.history_popup.auto_dismiss = False
        self.history_popup.title = 'Delete Confirmation'
        self.history_popup.size_hint = (None, None)
        self.history_popup.size = ('800sp', '400sp')
        invoice_id = vars.INVOICE_ID
        if invoice_id:
            layout = BoxLayout(orientation='vertical')
            inner_content_1 = BoxLayout(size_hint=(1, 0.8))
            inner_content_1.add_widget(Label(text="Are you sure you want to delete #{}?".format(invoice_id)))
            inner_content_2 = BoxLayout(size_hint=(1, 0.2),
                                        orientation='horizontal')
            inner_content_2.add_widget(Button(markup=True,
                                              text='Cancel',
                                              on_release=self.history_popup.dismiss))
            inner_content_2.add_widget(Button(markup=True,
                                              text='[color=0FFF00]Confirm[/color]',
                                              on_press=self.delete_invoice))
            layout.add_widget(inner_content_1)
            layout.add_widget(inner_content_2)

        else:
            layout = BoxLayout(orientation='vertical')
            inner_content_1 = BoxLayout(size_hint=(1, 0.8))
            inner_content_1.add_widget(Label(text="No such invoice. Please select an invoice".format(invoice_id)))
            inner_content_2 = BoxLayout(size_hint=(1, 0.2),
                                        orientation='horizontal')
            inner_content_2.add_widget(Button(markup=True,
                                              text='Cancel',
                                              on_press=self.history_popup.dismiss))
            layout.add_widget(inner_content_1)
            layout.add_widget(inner_content_2)
        self.history_popup.content = layout
        self.history_popup.open()

    def delete_invoice(self, *args, **kwargs):
        popup = Popup()
        popup.title = 'Deleted Invoice'
        popup.size_hint = (None, None)
        popup.size = (600, 400)
        if vars.INVOICE_ID:
            inv = Invoice()
            invoices = inv.where({'invoice_id': vars.INVOICE_ID}, deleted_at=False)
            if invoices:
                for invoice in invoices:
                    inv.id = invoice['id']
                    inv.delete()
            invoice_items = InvoiceItem()
            iis = invoice_items.where({'invoice_id': vars.INVOICE_ID}, deleted_at=False)
            if iis:
                for invoice_item in iis:
                    del_ii = InvoiceItem()
                    del_ii.id = invoice_item['id']
                    del_ii.delete()
                t1 = Thread(target=SYNC.db_sync, args=[vars.COMPANY_ID])
                t1.start()

            msg = KV.popup_alert(msg="Successfully deleted invoice #{}!".format(vars.INVOICE_ID))
        else:
            msg = KV.popup_alert(msg="Could not locate the invoice_id. Please try again.")
            pass

        popup.content = Builder.load_string(msg)
        popup.open()
        self.history_popup.dismiss()
        self.reset()

    def undo_invoice_confirm(self):
        self.history_popup = Popup()
        self.history_popup.auto_dismiss = False
        self.history_popup.title = 'Undo Status Selection #{}'.format(vars.INVOICE_ID)
        self.history_popup.size_hint = (None, None)
        self.history_popup.size = ('800sp', '400sp')
        invoice_id = vars.INVOICE_ID
        if invoice_id:
            layout = BoxLayout(orientation='vertical')
            inner_content_1 = GridLayout(size_hint=(1, 0.8),
                                         cols=1,
                                         rows=3,
                                         row_force_default=True,
                                         row_default_height='50sp')
            inner_content_1.add_widget(
                Label(markup=True,
                      text="[b]Change #{} Status To[b]".format(invoice_id)))
            self.status_spinner = Spinner(text='Select Status',
                                          values=('Not Ready', 'Racked', 'Prepaid', 'Gone Np', 'Picked Up'),
                                          size_hint_y=None,
                                          height='48sp')
            inner_content_1.add_widget(self.status_spinner)

            inner_content_2 = BoxLayout(size_hint=(1, 0.2),
                                        orientation='horizontal')
            inner_content_2.add_widget(Button(markup=True,
                                              text='Cancel',
                                              on_press=self.history_popup.dismiss))
            inner_content_2.add_widget(Button(markup=True,
                                              text='[color=0FFF00]Confirm[/color]',
                                              on_press=self.undo_invoice))
            layout.add_widget(inner_content_1)
            layout.add_widget(inner_content_2)

        else:
            layout = BoxLayout(orientation='vertical')
            inner_content_1 = BoxLayout(size_hint=(1, 0.8))
            inner_content_1.add_widget(Label(text="No such invoice. Please select an invoice".format(invoice_id)))
            inner_content_2 = BoxLayout(size_hint=(1, 0.2),
                                        orientation='horizontal')
            inner_content_2.add_widget(Button(markup=True,
                                              text='Cancel',
                                              on_press=self.history_popup.dismiss))
            layout.add_widget(inner_content_1)
            layout.add_widget(inner_content_2)
        self.history_popup.content = layout
        self.history_popup.open()

    def undo_invoice(self, *args, **kwargs):
        print(self.status_spinner.text)
        if self.status_spinner.text == 'Not Ready':
            status = 1
        elif self.status_spinner.text == "Racked":
            status = 2
        elif self.status_spinner.text == "Prepaid":
            status = 3
        elif self.status_spinner.text == "Gone Np":
            status = 4
        else:  # picked up
            status = 5
        print(status)
        popup = Popup()
        popup.title = 'Undo Invoice'
        popup.size_hint = (None, None)
        popup.size = (600, 400)
        if vars.INVOICE_ID:
            if status > 0:
                inv = Invoice()
                invoices = inv.where({'invoice_id': vars.INVOICE_ID}, deleted_at=False)
                if invoices:
                    for invoice in invoices:
                        inv.id = invoice['id']
                        original_status = invoice['status']
                        transaction_id = invoice['transaction_id']
                        if status < 5 and original_status is 5 and transaction_id:  # remove transaction_id and delete
                            # get all invoices with the same transaction_id
                            all_invoices = inv.where({'transaction_id': transaction_id})
                            if all_invoices:
                                for ainv in all_invoices:
                                    remove_trans_inv = Invoice()
                                    data = {'deleted_at': None,
                                            'status': status,
                                            'transaction_id': None}
                                    remove_trans_inv.put(where={'id': ainv['id']},
                                                         data=data)

                            transactions = Transaction()
                            trans = transactions.where({'transaction_id': transaction_id})
                            if trans:
                                for transaction in trans:
                                    tr_id = transaction['id']
                                    transactions.id = tr_id
                                    transactions.delete()
                        else:
                            data = {'deleted_at': None,
                                    'status': status}
                        where = {'id': invoice['id']}
                        inv.put(where=where, data=data)

                        data = {'deleted_at': None}
                        where = {'invoice_id': invoice['invoice_id']}
                        InvoiceItem().put(where=where, data=data)

                msg = KV.popup_alert(msg="Successfully updated invoice #{}!".format(vars.INVOICE_ID))
                # sync the database
                vars.WORKLIST.append("Sync")
                threads_start()
            else:
                msg = KV.popup_alert(msg="Please select a valid status.")

        else:
            msg = KV.popup_alert(msg="Could not locate the invoice_id. Please try again.")

        popup.content = Builder.load_string(msg)
        popup.open()
        self.history_popup.dismiss()
        self.reset()

    def reprint_popup(self):
        popup = Popup()
        popup.title = 'Reprint Invoice #{}'.format(vars.INVOICE_ID)
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.9))
        inner_layout_1.add_widget(Button(markup=True,
                                         text='Store Copy',
                                         on_release=partial(self.reprint_invoice, 1)))
        inner_layout_1.add_widget(Button(markup=True,
                                         text='Customer Copy',
                                         on_release=partial(self.reprint_invoice, 2)))
        inner_layout_1.add_widget(Button(markup=True,
                                         text='Tags',
                                         on_release=self.reprint_tags))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_release=popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def reprint_invoice(self, type, *args, **kwargs):
        if vars.INVOICE_ID:
            # print invoices
            if vars.EPSON:
                pr = Printer()
                companies = Company()
                comps = companies.where({'company_id': vars.COMPANY_ID}, set=True)

                if comps:
                    for company in comps:
                        companies.id = company['id']
                        companies.company_id = company['company_id']
                        companies.name = company['name']
                        companies.street = company['street']
                        companies.suite = company['suite']
                        companies.city = company['city']
                        companies.state = company['state']
                        companies.zip = company['zip']
                        companies.email = company['email']
                        companies.phone = Job.make_us_phone(company['phone'])
                customers = User()
                custs = customers.where({'user_id': vars.CUSTOMER_ID}, set=True)
                if custs:
                    for user in custs:
                        customers.id = user['id']
                        customers.user_id = user['user_id']
                        customers.company_id = user['company_id']
                        customers.username = user['username']
                        customers.first_name = user['first_name'].upper() if user['first_name'] else ''
                        customers.last_name = user['last_name']
                        customers.street = user['street']
                        customers.suite = user['suite']
                        customers.city = user['city']
                        customers.state = user['state']
                        customers.zipcode = user['zipcode']
                        customers.email = user['email']
                        customers.phone = Job.make_us_phone(user['phone'])
                        customers.intercom = user['intercom']
                        customers.concierge_name = user['concierge_name']
                        customers.concierge_number = user['concierge_number']
                        customers.special_instructions = user['special_instructions']
                        customers.shirt_old = user['shirt_old']
                        customers.shirt = user['shirt']
                        customers.delivery = user['delivery']
                        customers.profile_id = user['profile_id']
                        customers.payment_status = user['payment_status']
                        customers.payment_id = user['payment_id']
                        customers.token = user['token']
                        customers.api_token = user['api_token']
                        customers.reward_status = user['reward_status']
                        customers.reward_points = user['reward_points']
                        customers.account = user['account']
                        customers.starch = user['starch']
                        customers.important_memo = user['important_memo']
                        customers.invoice_memo = user['invoice_memo']
                        customers.password = user['password']
                        customers.role_id = user['role_id']
                        customers.remember_token = user['remember_token']
                invoices = Invoice()
                invs = invoices.where({'invoice_id': vars.INVOICE_ID})
                invoice_discount_id = None
                if invs:
                    for invoice in invs:
                        invoice_quantity = invoice['quantity']
                        invoice_discount_id = invoice['discount_id']
                        invoice_subtotal = invoice['pretax']
                        invoice_tax = invoice['tax']
                        invoice_total = invoice['total']
                        invoice_due_date = datetime.datetime.strptime(invoice['due_date'], "%Y-%m-%d %H:%M:%S")
                discount_amount = 0
                if invoice_discount_id is not None:
                    discounts = Discount();
                    discs = discounts.where({'discount_id',invoice_discount_id})
                    if discs:
                        for disc in discs:
                            discount_rate = disc['rate']
                            discount_price = disc['discount']
                            discount_type = disc['type']
                            if discount_type is 1:
                                discount_amount = (invoice_subtotal * discount_rate)
                            else:
                                discount_amount = invoice_subtotal - discount_price

                discount_amount = vars.us_dollar(discount_amount)
                invoice_items = InvoiceItem()
                inv_items = invoice_items.where({'invoice_id': vars.INVOICE_ID})

                print_sync_invoice = {vars.INVOICE_ID: {}}
                if inv_items:
                    colors = {}
                    for invoice_item in inv_items:
                        item_id = invoice_item['item_id']
                        colors[item_id] = {}
                    for invoice_item in inv_items:
                        item_id = invoice_item['item_id']
                        items = InventoryItem().where({'item_id': item_id})
                        if items:
                            for item in items:
                                item_name = item['name']
                                inventory_id = item['inventory_id']
                        else:
                            item_name = None
                            inventory_id = None

                        inventories = Inventory()
                        invs = inventories.where({'inventory_id': inventory_id})
                        if invs:
                            if invs:
                                for inventory in invs:
                                    inventory_init = inventory['name'][:1].capitalize()
                                    laundry = inventory['laundry']
                            else:
                                inventory_init = ''
                                laundry = 0

                        display_name = '{} ({})'.format(item_name, vars.get_starch_by_code(
                            customers.starch)) if laundry else item_name

                        item_color = invoice_item['color']
                        if item_id in colors:
                            if item_color in colors[item_id]:
                                colors[item_id][item_color] += 1
                            else:
                                colors[item_id][item_color] = 1
                        item_memo = invoice_item['memo']
                        item_subtotal = invoice_item['pretax']
                        if vars.INVOICE_ID in print_sync_invoice:
                            if item_id in print_sync_invoice[vars.INVOICE_ID]:
                                print_sync_invoice[vars.INVOICE_ID][item_id]['item_price'] += item_subtotal
                                print_sync_invoice[vars.INVOICE_ID][item_id]['qty'] += 1
                                if item_memo:
                                    print_sync_invoice[vars.INVOICE_ID][item_id]['memos'].append(item_memo)
                                if item_id in colors:
                                    print_sync_invoice[vars.INVOICE_ID][item_id]['colors'] = colors[item_id]
                                else:
                                    print_sync_invoice[vars.INVOICE_ID][item_id]['colors'] = []
                            else:
                                print_sync_invoice[vars.INVOICE_ID][item_id] = {
                                    'item_id': item_id,
                                    'type': inventory_init,
                                    'name': display_name,
                                    'item_price': item_subtotal,
                                    'qty': 1,
                                    'memos': [item_memo] if item_memo else [],
                                    'colors': {item_color: 1}
                                }
                now = datetime.datetime.now()
                if type == 2:
                    vars.EPSON.write(pr.pcmd('TXT_ALIGN_CT'))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                    density=5, invert=False, smooth=False, flip=False))
                    vars.EPSON.write("::CUSTOMER::\n")
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write("{}\n".format(companies.name))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write("{}\n".format(companies.street))
                    vars.EPSON.write("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                    invert=False, smooth=False, flip=False))

                    vars.EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
                    vars.EPSON.write("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write("READY BY: {}\n\n".format(invoice_due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                    invert=False, smooth=False, flip=False))
                    padded_customer_id = '{0:05d}'.format(vars.CUSTOMER_ID)
                    vars.EPSON.write("{}\n".format(padded_customer_id))

                    # Print barcode
                    vars.EPSON.write(pr.pcmd_barcode(str(padded_customer_id)))

                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write("{}\n".format(Job.make_us_phone(customers.phone)))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('-----------------------------------------\n')

                    if vars.INVOICE_ID in print_sync_invoice:
                        for item_id, invoice_item in print_sync_invoice[vars.INVOICE_ID].items():
                            item_name = invoice_item['name']
                            item_price = invoice_item['item_price']
                            item_qty = invoice_item['qty']
                            item_color_string = []
                            item_memo = invoice_item['memos']
                            item_type = invoice_item['type']
                            if 'colors' in invoice_item:
                                for color_name, color_qty in invoice_item['colors'].items():
                                    if color_name:
                                        item_color_string.append('{}-{}'.format(color_qty, color_name))
                            vars.EPSON.write('{} {}   {}\n'.format(item_type, item_qty, item_name))

                            if len(item_memo) > 0:
                                vars.EPSON.write(pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                             height=1,
                                                             density=5, invert=False, smooth=False, flip=False))
                                vars.EPSON.write('     {}\n'.format('/ '.join(item_memo)))
                            if len(item_color_string) > 0:
                                vars.EPSON.write(pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                             height=1,
                                                             density=5, invert=False, smooth=False, flip=False))
                                vars.EPSON.write('     {}\n'.format(', '.join(item_color_string)))

                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('-----------------------------------------\n')
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('{} PCS\n'.format(invoice_quantity))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('-----------------------------------------\n')

                    if customers.invoice_memo:
                        vars.EPSON.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('{}\n'.format(customers.invoice_memo))
                    # Cut paper
                    vars.EPSON.write('\n\n\n\n\n\n')
                    vars.EPSON.write(pr.pcmd('PARTIAL_CUT'))

                if type == 1:
                    # Print store copies
                    if print_sync_invoice:  # if invoices synced
                        for invoice_id, item_id in print_sync_invoice.items():

                            # start invoice
                            vars.EPSON.write(pr.pcmd('TXT_ALIGN_CT'))
                            vars.EPSON.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=5,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write("::COPY::\n")
                            vars.EPSON.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write("{}\n".format(companies.name))
                            vars.EPSON.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=5,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
                            vars.EPSON.write("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))
                            vars.EPSON.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2,
                                            density=5,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write(
                                "READY BY: {}\n\n".format(invoice_due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                            vars.EPSON.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write("{}\n".format('{0:06d}'.format(invoice_id)))
                            # Print barcode
                            vars.EPSON.write(pr.pcmd_barcode('{}'.format('{0:06d}'.format(invoice_id))))

                            vars.EPSON.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3,
                                            density=6,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write(
                                '{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                            vars.EPSON.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=2,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write("{}\n".format(Job.make_us_phone(customers.phone)))
                            vars.EPSON.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=1,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write('-----------------------------------------\n')

                            if invoice_id in print_sync_invoice:
                                for item_id, invoice_item in print_sync_invoice[invoice_id].items():
                                    item_name = invoice_item['name']
                                    item_price = invoice_item['item_price']
                                    item_qty = invoice_item['qty']
                                    item_color_string = []
                                    item_memo = invoice_item['memos']
                                    item_type = invoice_item['type']
                                    if 'colors' in invoice_item:
                                        for color_name, color_qty in invoice_item['colors'].items():
                                            if color_name:
                                                item_color_string.append('{}-{}'.format(color_qty, color_name))
                                    string_length = len(item_type) + len(str(item_qty)) + len(item_name) + len(
                                        vars.us_dollar(item_price)) + 4
                                    string_offset = 42 - string_length if 42 - string_length > 0 else 0
                                    vars.EPSON.write('{} {}   {}{}{}\n'.format(item_type,
                                                                               item_qty,
                                                                               item_name,
                                                                               ' ' * string_offset,
                                                                               vars.us_dollar(item_price)))

                                    if len(item_memo) > 0:
                                        vars.EPSON.write(
                                            pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                        height=1,
                                                        density=5, invert=False, smooth=False, flip=False))
                                        vars.EPSON.write('     {}\n'.format('/ '.join(item_memo)))
                                    if len(item_color_string) > 0:
                                        vars.EPSON.write(
                                            pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                        height=1,
                                                        density=5, invert=False, smooth=False, flip=False))
                                        vars.EPSON.write('     {}\n'.format(', '.join(item_color_string)))

                            vars.EPSON.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=1,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write('-----------------------------------------\n')
                            vars.EPSON.write(
                                pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write('{} PCS\n'.format(invoice_quantity))
                            vars.EPSON.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=1,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write('-----------------------------------------\n')
                            vars.EPSON.write(
                                pr.pcmd_set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write('    SUBTOTAL:')
                            vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                            string_length = len(vars.us_dollar(invoice_subtotal))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.write('{}{}\n'.format(' ' * string_offset, vars.us_dollar(invoice_subtotal)))
                            vars.EPSON.write('    DISCOUNT:')
                            vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                            string_length = len(vars.us_dollar(discount_amount))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.write('{}({})\n'.format(' ' * string_offset, vars.us_dollar(discount_amount)))
                            vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                            vars.EPSON.write('         TAX:')
                            string_length = len(vars.us_dollar(invoice_tax))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                            vars.EPSON.write('{}{}\n'.format(' ' * string_offset, vars.us_dollar(invoice_tax)))
                            vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                            vars.EPSON.write('       TOTAL:')
                            vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                            string_length = len(vars.us_dollar(invoice_total))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.write('{}{}\n'.format(' ' * string_offset,
                                                             vars.us_dollar(invoice_total)))
                            vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                            vars.EPSON.write('     BALANCE:')
                            string_length = len(vars.us_dollar(invoice_total))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.write('{}{}\n\n'.format(' ' * string_offset, vars.us_dollar(invoice_total)))
                            if customers.invoice_memo:
                                vars.EPSON.write(
                                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                                invert=False, smooth=False, flip=False))
                                vars.EPSON.write('{}\n'.format(customers.invoice_memo))
                            if item_type == 'L':
                                # get customer mark
                                marks = Custid()
                                marks_list = marks.where({'customer_id': vars.CUSTOMER_ID, 'status': 1})
                                if marks_list:
                                    m_list = []
                                    for mark in marks_list:
                                        m_list.append(mark['mark'])
                                    vars.EPSON.write(
                                        pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=3, height=4,
                                                    density=8, invert=False, smooth=False, flip=False))
                                    vars.EPSON.write('{}\n\n'.format(', '.join(m_list)))

                            # Cut paper
                            vars.EPSON.write('\n\n\n\n\n\n')
                            vars.EPSON.write(pr.pcmd('PARTIAL_CUT'))

            else:
                popup = Popup()
                popup.title = 'Printer Error'
                content = KV.popup_alert('No printer found. Please try again.')
                popup.content = Builder.load_string(content)
                popup.open()
                # Beep Sound
                sys.stdout.write('\a')
                sys.stdout.flush()
        else:
            popup = Popup()
            popup.title = 'Reprint Error'
            content = KV.popup_alert('Please select an invoice.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()

    def reprint_tags(self, *args, **kwargs):
        popup = Popup()
        popup.title = 'Tag Reprint'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='vertical',
                                   size_hint=(1, 0.9))
        self.tags_grid = Factory.TagsGrid()
        invitems = InvoiceItem().where({'invoice_id': vars.INVOICE_ID})
        if invitems:
            for ii in invitems:
                invoice_items_id = ii['invoice_items_id']
                iitem_id = ii['item_id']
                tags_to_print = InventoryItem().tagsToPrint(iitem_id)
                item_name = InventoryItem().getItemName(iitem_id)
                item_color = ii['color']
                item_memo = ii['memo']
                trtd1 = Button(text=str(invoice_items_id),
                               on_release=partial(self.select_tag, invoice_items_id))
                trtd2 = Button(text=str(item_name),
                               on_release=partial(self.select_tag, invoice_items_id))
                trtd3 = Button(text=str(item_color),
                               on_release=partial(self.select_tag, invoice_items_id))
                trtd4 = Button(text=str(item_memo),
                               on_release=partial(self.select_tag, invoice_items_id))
                trtd5 = Button(text=str(tags_to_print),
                               on_release=partial(self.select_tag, invoice_items_id))
                self.tags_grid.ids.tags_table.add_widget(trtd1)
                self.tags_grid.ids.tags_table.add_widget(trtd2)
                self.tags_grid.ids.tags_table.add_widget(trtd3)
                self.tags_grid.ids.tags_table.add_widget(trtd4)
                self.tags_grid.ids.tags_table.add_widget(trtd5)
        inner_layout_1.add_widget(self.tags_grid)
        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="Cancel",
                               on_release=popup.dismiss)
        print_all_button = Button(text="Print All",
                                  on_press=popup.dismiss,
                                  on_release=self.print_all_tags)
        print_selected_button = Button(text="Print Selected",
                                       on_press=popup.dismiss,
                                       on_release=self.print_selected_tags)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(print_all_button)
        inner_layout_2.add_widget(print_selected_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def select_tag(self, item_id, *args, **kwargs):

        if item_id in self.selected_tags_list:
            # remove the tag
            self.selected_tags_list.remove(item_id)
        else:
            # add the tag
            self.selected_tags_list.append(item_id)

        self.tags_grid.ids.tags_table.clear_widgets()
        th1 = Factory.TagsGridHeaders(text="[color=#000000]ID[/color]")
        th2 = Factory.TagsGridHeaders(text="[color=#000000]Item[/color]")
        th3 = Factory.TagsGridHeaders(text="[color=#000000]Color[/color]")
        th4 = Factory.TagsGridHeaders(text="[color=#000000]Memo[/color]")
        th5 = Factory.TagsGridHeaders(text="[color=#000000]Tags[/color]")
        self.tags_grid.ids.tags_table.add_widget(th1)
        self.tags_grid.ids.tags_table.add_widget(th2)
        self.tags_grid.ids.tags_table.add_widget(th3)
        self.tags_grid.ids.tags_table.add_widget(th4)
        self.tags_grid.ids.tags_table.add_widget(th5)
        invitems = InvoiceItem().where({'invoice_id': vars.INVOICE_ID})
        if invitems:
            for ii in invitems:
                invoice_items_id = ii['invoice_items_id']
                iitem_id = ii['item_id']
                tags_to_print = InventoryItem().tagsToPrint(iitem_id)
                item_name = InventoryItem().getItemName(iitem_id)
                item_color = ii['color']
                item_memo = ii['memo']
                if invoice_items_id in self.selected_tags_list:
                    trtd1 = Factory.TagsSelectedButton(text=str(invoice_items_id),
                                                       on_release=partial(self.select_tag, invoice_items_id))
                    trtd2 = Factory.TagsSelectedButton(text=str(item_name),
                                                       on_release=partial(self.select_tag, invoice_items_id))
                    trtd3 = Factory.TagsSelectedButton(text=str(item_color),
                                                       on_release=partial(self.select_tag, invoice_items_id))
                    trtd4 = Factory.TagsSelectedButton(text=str(item_memo),
                                                       on_release=partial(self.select_tag, invoice_items_id))
                    trtd5 = Factory.TagsSelectedButton(text=str(tags_to_print),
                                                       on_release=partial(self.select_tag, invoice_items_id))
                else:
                    trtd1 = Button(text=str(invoice_items_id),
                                   on_release=partial(self.select_tag, invoice_items_id))
                    trtd2 = Button(text=str(item_name),
                                   on_release=partial(self.select_tag, invoice_items_id))
                    trtd3 = Button(text=str(item_color),
                                   on_release=partial(self.select_tag, invoice_items_id))
                    trtd4 = Button(text=str(item_memo),
                                   on_release=partial(self.select_tag, invoice_items_id))
                    trtd5 = Button(text=str(tags_to_print),
                                   on_release=partial(self.select_tag, invoice_items_id))
                self.tags_grid.ids.tags_table.add_widget(trtd1)
                self.tags_grid.ids.tags_table.add_widget(trtd2)
                self.tags_grid.ids.tags_table.add_widget(trtd3)
                self.tags_grid.ids.tags_table.add_widget(trtd4)
                self.tags_grid.ids.tags_table.add_widget(trtd5)

        pass

    def print_all_tags(self, *args, **kwargs):
        if vars.INVOICE_ID:
            customers = User()
            custs = customers.where({'user_id': vars.CUSTOMER_ID}, set=True)
            if custs:
                for user in custs:
                    customers.id = user['id']
                    customers.user_id = user['user_id']
                    customers.company_id = user['company_id']
                    customers.username = user['username']
                    customers.first_name = user['first_name'].upper() if user['first_name'] else ''
                    customers.last_name = user['last_name']
                    customers.street = user['street']
                    customers.suite = user['suite']
                    customers.city = user['city']
                    customers.state = user['state']
                    customers.zipcode = user['zipcode']
                    customers.email = user['email']
                    customers.phone = user['phone']
                    customers.intercom = user['intercom']
                    customers.concierge_name = user['concierge_name']
                    customers.concierge_number = user['concierge_number']
                    customers.special_instructions = user['special_instructions']
                    customers.shirt_old = user['shirt_old']
                    customers.shirt = user['shirt']
                    customers.delivery = user['delivery']
                    customers.profile_id = user['profile_id']
                    customers.payment_status = user['payment_status']
                    customers.payment_id = user['payment_id']
                    customers.token = user['token']
                    customers.api_token = user['api_token']
                    customers.reward_status = user['reward_status']
                    customers.reward_points = user['reward_points']
                    customers.account = user['account']
                    customers.starch = user['starch']
                    customers.important_memo = user['important_memo']
                    customers.invoice_memo = user['invoice_memo']
                    customers.password = user['password']
                    customers.role_id = user['role_id']
                    customers.remember_token = user['remember_token']
            invoice_id_str = str(vars.INVOICE_ID)
            invs = Invoice().where({'invoice_id': vars.INVOICE_ID})
            due_date = 'SUN'
            if invs:
                for inv in invs:
                    dt = datetime.datetime.strptime(inv['due_date'], "%Y-%m-%d %H:%M:%S")
                    due_date = dt.strftime('%a').upper()
            invoice_last_four = '{0:04d}'.format(int(invoice_id_str[-4:]))
            text_left = "{} {}".format(invoice_last_four,
                                       due_date)
            text_right = "{} {}".format(due_date,
                                        invoice_last_four)
            text_name = "{}, {}".format(customers.last_name.upper(),
                                        customers.first_name.upper()[:1])
            phone_number = Job.make_us_phone(customers.phone)
            total_length = 32
            text_offset = total_length - len(text_name) - len(phone_number)
            name_number_string = '{}{}{}'.format(text_name, ' ' * text_offset,
                                                 phone_number)

            print('next step')
            invoice_items = InvoiceItem().where({'invoice_id': vars.INVOICE_ID})
            vars.BIXOLON.write('\x1b\x40')
            vars.BIXOLON.write('\x1b\x6d')
            laundry_to_print = []
            if invoice_items:

                for ii in invoice_items:

                    iitem_id = ii['item_id']
                    tags_to_print = InventoryItem().tagsToPrint(iitem_id)
                    item_name = InventoryItem().getItemName(iitem_id)
                    item_color = ii['color']
                    invoice_item_id = ii['invoice_items_id']
                    laundry_tag = InventoryItem().getLaundry(iitem_id)
                    memo_string = ii['memo']
                    if laundry_tag:
                        laundry_to_print.append(invoice_item_id)
                    else:
                        for _ in range(tags_to_print):

                            vars.BIXOLON.write('\x1b!\x30')  # QUAD SIZE
                            vars.BIXOLON.write('{}{}\n'.format(text_left, text_right))
                            vars.BIXOLON.write('\x1b!\x00')
                            vars.BIXOLON.write(name_number_string)
                            vars.BIXOLON.write('\n')
                            vars.BIXOLON.write('{0:06d}'.format(int(invoice_item_id)))
                            vars.BIXOLON.write(' {} {}'.format(item_name, item_color))
                            if memo_string:
                                vars.BIXOLON.write('\n{}'.format(memo_string))
                                memo_len = '\n\n\n' if len(
                                    memo_string) <= 32 else '\n\n\n' + '\n' * int(
                                    (len(memo_string)) / 32)
                                vars.BIXOLON.write(memo_len)
                                vars.BIXOLON.write('\x1b\x6d')
                            else:
                                vars.BIXOLON.write('\n\n\n')
                                vars.BIXOLON.write('\x1b\x6d')
                # FINAL CUT
                vars.BIXOLON.write('\n\n\n\n\n\n')
                vars.BIXOLON.write('\x1b\x6d')

            if len(laundry_to_print) > 0:
                laundry_count = len(laundry_to_print)
                shirt_mark = Custid().getCustomerMark(vars.CUSTOMER_ID)
                name_text_offset = total_length - len(text_name) - len(text_name)
                shirt_mark_length = len(shirt_mark)
                mark_text_offset = 16 - (shirt_mark_length * 2)
                for i in range(0, laundry_count, 2):
                    start = i
                    end = i + 1

                    invoice_item_id_start = '{0:06d}'.format(int(laundry_to_print[start]))

                    id_offset = total_length - 12

                    try:
                        invoice_item_id_end = '{0:06d}'.format(int(laundry_to_print[end]))
                        name_name_string = '{}{}{}'.format(text_name, ' ' * name_text_offset, text_name)
                        mark_mark_string = '{}{}{}'.format(shirt_mark, ' ' * mark_text_offset, shirt_mark)
                        id_id_string = '{}{}{}'.format(invoice_item_id_start, ' ' * id_offset, invoice_item_id_end)

                    except IndexError:
                        name_name_string = '{}'.format(text_name)
                        mark_mark_string = '{}'.format(shirt_mark)
                        id_id_string = '{}'.format(invoice_item_id_start)

                    vars.BIXOLON.write('\x1b!\x30')  # QUAD SIZE
                    vars.BIXOLON.write(mark_mark_string)
                    vars.BIXOLON.write('\n')
                    vars.BIXOLON.write('\x1b!\x00')
                    vars.BIXOLON.write(name_name_string)
                    vars.BIXOLON.write('\n')
                    vars.BIXOLON.write(id_id_string)

                    vars.BIXOLON.write('\n\n\n\x1b\x6d')

                # FINAL CUT
                vars.BIXOLON.write('\n\n\n\n\n\n')
                vars.BIXOLON.write('\x1b\x6d')


        else:
            popup = Popup()
            popup.title = 'Reprint Error'
            content = KV.popup_alert('Please select an invoice.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()
        pass

    def print_selected_tags(self, *args, **kwargs):
        print(self.selected_tags_list)
        if self.selected_tags_list:
            customers = User()
            custs = customers.where({'user_id': vars.CUSTOMER_ID}, set=True)
            if custs:
                for user in custs:
                    customers.id = user['id']
                    customers.user_id = user['user_id']
                    customers.company_id = user['company_id']
                    customers.username = user['username']
                    customers.first_name = user['first_name'].upper() if user['first_name'] else ''
                    customers.last_name = user['last_name']
                    customers.street = user['street']
                    customers.suite = user['suite']
                    customers.city = user['city']
                    customers.state = user['state']
                    customers.zipcode = user['zipcode']
                    customers.email = user['email']
                    customers.phone = user['phone']
                    customers.intercom = user['intercom']
                    customers.concierge_name = user['concierge_name']
                    customers.concierge_number = user['concierge_number']
                    customers.special_instructions = user['special_instructions']
                    customers.shirt_old = user['shirt_old']
                    customers.shirt = user['shirt']
                    customers.delivery = user['delivery']
                    customers.profile_id = user['profile_id']
                    customers.payment_status = user['payment_status']
                    customers.payment_id = user['payment_id']
                    customers.token = user['token']
                    customers.api_token = user['api_token']
                    customers.reward_status = user['reward_status']
                    customers.reward_points = user['reward_points']
                    customers.account = user['account']
                    customers.starch = user['starch']
                    customers.important_memo = user['important_memo']
                    customers.invoice_memo = user['invoice_memo']
                    customers.password = user['password']
                    customers.role_id = user['role_id']
                    customers.remember_token = user['remember_token']
            invoice_id_str = str(vars.INVOICE_ID)
            invs = Invoice().where({'invoice_id': vars.INVOICE_ID})
            due_date = 'SUN'
            if invs:
                for inv in invs:
                    dt = datetime.datetime.strptime(inv['due_date'], "%Y-%m-%d %H:%M:%S")
                    due_date = dt.strftime('%a').upper()
            invoice_last_four = '{0:04d}'.format(int(invoice_id_str[-4:]))
            text_left = "{} {}".format(invoice_last_four,
                                       due_date)
            text_right = "{} {}".format(due_date,
                                        invoice_last_four)
            text_name = "{}, {}".format(customers.last_name.upper(),
                                        customers.first_name.upper()[:1])
            phone_number = Job.make_us_phone(customers.phone)
            total_length = 32
            text_offset = total_length - len(text_name) - len(phone_number)
            name_number_string = '{}{}{}'.format(text_name, ' ' * text_offset,
                                                 phone_number)
            if vars.BIXOLON:
                vars.BIXOLON.write('\x1b\x40')
                vars.BIXOLON.write('\x1b\x6d')
                print('next step')
                laundry_to_print = []
                for item_id in self.selected_tags_list:

                    inv_items = InvoiceItem().where({'invoice_items_id': item_id})
                    if inv_items:
                        for ii in inv_items:
                            iitem_id = ii['item_id']
                            tags_to_print = InventoryItem().tagsToPrint(iitem_id)
                            item_name = InventoryItem().getItemName(iitem_id)
                            item_color = ii['color']
                            invoice_item_id = ii['invoice_items_id']
                            laundry_tag = InventoryItem().getLaundry(iitem_id)
                            memo_string = ii['memo']
                            if laundry_tag:
                                laundry_to_print.append(invoice_item_id)
                            else:

                                for _ in range(tags_to_print):

                                    vars.BIXOLON.write('\x1b!\x30')  # QUAD SIZE
                                    vars.BIXOLON.write('{}{}\n'.format(text_left, text_right))
                                    vars.BIXOLON.write('\x1b!\x00')
                                    vars.BIXOLON.write(name_number_string)
                                    vars.BIXOLON.write('\n')
                                    vars.BIXOLON.write('{0:06d}'.format(int(invoice_item_id)))
                                    vars.BIXOLON.write(' {} {}'.format(item_name, item_color))
                                    if memo_string:
                                        vars.BIXOLON.write('\n{}'.format(memo_string))
                                        memo_len = '\n\n\n' if len(
                                            memo_string) <= 32 else '\n\n\n' + '\n' * int(
                                            (len(memo_string)) / 32)
                                        vars.BIXOLON.write(memo_len)
                                        vars.BIXOLON.write('\x1b\x6d')

                                    else:

                                        vars.BIXOLON.write('\n\n\n')
                                        vars.BIXOLON.write('\x1b\x6d')
            if len(laundry_to_print) is 0:
                # FINAL CUT
                vars.BIXOLON.write('\n\n\n\n\n\n')
                vars.BIXOLON.write('\x1b\x6d')

            else:
                laundry_count = len(laundry_to_print)
                shirt_mark = Custid().getCustomerMark(vars.CUSTOMER_ID)
                name_text_offset = total_length - len(text_name) - len(text_name)
                shirt_mark_length = len(shirt_mark)
                mark_text_offset = 16 - (shirt_mark_length * 2)
                for i in range(0, laundry_count, 2):
                    start = i
                    end = i + 1

                    invoice_item_id_start = '{0:06d}'.format(int(laundry_to_print[start]))

                    id_offset = total_length - 12

                    try:
                        invoice_item_id_end = '{0:06d}'.format(int(laundry_to_print[end]))
                        name_name_string = '{}{}{}'.format(text_name, ' ' * name_text_offset, text_name)
                        mark_mark_string = '{}{}{}'.format(shirt_mark, ' ' * mark_text_offset, shirt_mark)
                        id_id_string = '{}{}{}'.format(invoice_item_id_start, ' ' * id_offset, invoice_item_id_end)

                    except IndexError:
                        name_name_string = '{}'.format(text_name)
                        mark_mark_string = '{}'.format(shirt_mark)
                        id_id_string = '{}'.format(invoice_item_id_start)

                    vars.BIXOLON.write('\x1b!\x30')  # QUAD SIZE
                    vars.BIXOLON.write(mark_mark_string)
                    vars.BIXOLON.write('\n')
                    vars.BIXOLON.write('\x1b!\x00')
                    vars.BIXOLON.write(name_name_string)
                    vars.BIXOLON.write('\n')
                    vars.BIXOLON.write(id_id_string)

                    vars.BIXOLON.write('\n\n\n\x1b\x6d')

                # FINAL CUT
                vars.BIXOLON.write('\n\n\n\n\n\n')
                vars.BIXOLON.write('\x1b\x6d')

        else:
            popup = Popup()
            popup.title = 'Reprint Error'
            content = KV.popup_alert('Please select an invoice item to print tag.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()


class InventoriesScreen(Screen):
    inventory_table = ObjectProperty(None)
    inventory_name = ObjectProperty(None)
    inventory_desc = ObjectProperty(None)
    inventory_order = ObjectProperty(None)
    inventory_laundry = 0
    inventory_id = None
    edit_popup = Popup()
    add_popup = Popup()

    def reset(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
        self.inventory_id = None
        self.inventory_laundry = 0
        self.update_inventory_table()

    def update_inventory_table(self):
        self.inventory_table.clear_widgets()
        h1 = KV.sized_invoice_tr(0, 'ID', 0.1)
        h2 = KV.sized_invoice_tr(0, 'Name', 0.4)
        h3 = KV.sized_invoice_tr(0, 'Order', 0.1)
        h4 = KV.sized_invoice_tr(0, 'Laundry', 0.1)
        h5 = KV.sized_invoice_tr(0, 'Action', 0.1)
        h6 = KV.sized_invoice_tr(0, 'Move', 0.1)
        h7 = KV.sized_invoice_tr(0, 'Move', 0.1)
        self.inventory_table.add_widget(Builder.load_string(h1))
        self.inventory_table.add_widget(Builder.load_string(h2))
        self.inventory_table.add_widget(Builder.load_string(h3))
        self.inventory_table.add_widget(Builder.load_string(h4))
        self.inventory_table.add_widget(Builder.load_string(h5))
        self.inventory_table.add_widget(Builder.load_string(h6))
        self.inventory_table.add_widget(Builder.load_string(h7))

        inventories = Inventory().where({'company_id': vars.COMPANY_ID, 'ORDER_BY': 'ordered asc'})
        if inventories:
            for inventory in inventories:
                c1 = KV.sized_invoice_tr(1, inventory['id'], 0.1)
                c2 = KV.sized_invoice_tr(state=1,
                                         data='{}\\n{}'.format(inventory['name'], inventory['description']),
                                         size_hint_x=0.4,
                                         text_wrap=True)
                c3 = KV.sized_invoice_tr(1, inventory['ordered'], 0.1)
                c4 = KV.sized_invoice_tr(1, 'True' if inventory['laundry'] else 'False', 0.1)
                c5 = Button(text="Edit",
                            size_hint_x=0.1,
                            on_release=partial(self.edit_invoice_popup, inventory['id']))
                c6 = Factory.CenterGlyphUpButton(size_hint_x=0.1,
                                                 on_release=partial(self.inventory_move, 'up', inventory['id']))
                c7 = Factory.CenterGlyphDownButton(size_hint_x=0.1,
                                                   on_release=partial(self.inventory_move, 'down', inventory['id']))
                self.inventory_table.add_widget(Builder.load_string(c1))
                self.inventory_table.add_widget(Builder.load_string(c2))
                self.inventory_table.add_widget(Builder.load_string(c3))
                self.inventory_table.add_widget(Builder.load_string(c4))
                self.inventory_table.add_widget(c5)
                self.inventory_table.add_widget(c6)
                self.inventory_table.add_widget(c7)

    def inventory_move(self, pos, id, *args, **kwargs):
        orders = []
        inventories = Inventory().where({'company_id': vars.COMPANY_ID, 'ORDER_BY': 'ordered asc'})
        row_selected = False
        if inventories:
            idx = -1
            for inventory in inventories:
                idx += 1
                inventory_id = inventory['id']
                inventory_order = inventory['ordered']
                orders.append({'id': inventory_id, 'ordered': inventory_order})
                if inventory_id == id:
                    row_selected = idx

        if row_selected:
            row_previous = row_selected - 1
            row_next = row_selected + 1
            if pos == 'up':
                try:
                    alist = orders[row_previous]
                    blist = orders[row_selected]
                    orders[row_previous] = blist
                    orders[row_selected] = alist
                except IndexError:
                    pass


            else:
                try:
                    alist = orders[row_next]
                    blist = orders[row_selected]
                    orders[row_next] = blist
                    orders[row_selected] = alist
                except IndexError:
                    pass
        idx = -1
        if orders:
            ordered = 0
            for order in orders:
                idx += 1
                ordered += 1
                orders[idx]['ordered'] = ordered

        # save new order
        if orders:
            for order in orders:
                Inventory().put(where={'id': order['id']}, data={'ordered': order['ordered']})
            self.reset()

    def edit_invoice_popup(self, id, *args, **kwargs):
        self.inventory_id = id
        self.edit_popup.title = 'Edit Invoice'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = GridLayout(size_hint=(1, 0.9),
                                    cols=2,
                                    rows=4,
                                    row_force_default=True,
                                    row_default_height='50sp',
                                    spacing='2sp')
        inventories = Inventory().where({'id': id})
        if inventories:
            for inventory in inventories:
                inventory_name = inventory['name']
                inventory_desc = inventory['description']
                inventory_order = inventory['ordered']
                inventory_laundry = inventory['laundry']
        else:
            inventory_name = ''
            inventory_desc = ''
            inventory_order = ''
            inventory_laundry = False
        inv_laundry_display = 'True' if inventory_laundry else 'False'
        self.inventory_name = Factory.CenterVerticalTextInput(text=inventory_name)
        self.inventory_desc = Factory.CenterVerticalTextInput(text=inventory_desc)
        self.inventory_order = Factory.CenterVerticalTextInput(text='{}'.format(str(inventory_order)))
        laundry = ['False', 'True']
        c4 = Spinner(text='{}'.format(inv_laundry_display),
                     values=laundry)
        c4.bind(text=self.set_laundry)
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Name:'))
        inner_layout_1.add_widget(self.inventory_name)
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Description:'))
        inner_layout_1.add_widget(self.inventory_desc)
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Order:'))
        inner_layout_1.add_widget(self.inventory_order)
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Laundry:'))
        inner_layout_1.add_widget(c4)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_release=self.edit_popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=0AAC00][b]Save[/b][/color]',
                                         on_release=self.edit_inventory))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.edit_popup.content = layout
        self.edit_popup.open()

    def edit_inventory(self, *args, **kwargs):
        inventories = Inventory()
        put = inventories.put(where={'id': self.inventory_id},
                              data={'name': self.inventory_name.text,
                                    'description': self.inventory_desc.text,
                                    'ordered': self.inventory_order.text,
                                    'laundry': self.inventory_laundry})
        if put:
            self.edit_popup.dismiss()
            vars.WORKLIST.append("Sync")
            threads_start()
            popup = Popup()
            popup.title = 'Inventory Update'
            content = KV.popup_alert('Successfully updated inventory!')
            popup.content = Builder.load_string(content)
            popup.open()
            self.edit_popup.dismiss()
            self.reset()

    def set_laundry(self, item, value, *args, **kwargs):
        if value == 'True':
            self.inventory_laundry = 1
        else:
            self.inventory_laundry = 0
        print(self.inventory_laundry)

    def add_inventory_popup(self):
        self.add_popup.title = 'Add Inventory'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = GridLayout(size_hint=(1, 0.9),
                                    cols=2,
                                    rows=4,
                                    row_force_default=True,
                                    row_default_height='50sp')
        self.inventory_name = Factory.CenterVerticalTextInput(text='')
        self.inventory_desc = Factory.CenterVerticalTextInput(text='')
        self.inventory_order = Factory.CenterVerticalTextInput(text='')
        laundry = ['False', 'True']
        c4 = Spinner(text='{}'.format('True' if self.inventory_laundry else 'False'),
                     values=laundry)
        c4.bind(text=self.set_laundry)
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Name:'))
        inner_layout_1.add_widget(self.inventory_name)
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Description:'))
        inner_layout_1.add_widget(self.inventory_desc)
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Order:'))
        inner_layout_1.add_widget(self.inventory_order)
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Laundry:'))
        inner_layout_1.add_widget(c4)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_release=self.add_popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=0AAC00][b]Add[/b][/color]',
                                         on_release=self.add_inventory))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.add_popup.content = layout
        self.add_popup.open()

    def add_inventory(self, *args, **kwargs):
        inventories = Inventory()
        inventories.company_id = vars.COMPANY_ID
        inventories.name = self.inventory_name.text
        inventories.description = self.inventory_desc.text
        inventories.ordered = self.inventory_order.text
        inventories.laundry = self.inventory_laundry
        inventories.status = 1

        if inventories.add():
            # set invoice_items data to save
            vars.WORKLIST.append("Sync")
            threads_start()

            popup = Popup()
            popup.title = 'Added Inventory'
            popup.content = Builder.load_string(KV.popup_alert('Successfully created a new inventory!'))
            popup.open()
            self.add_popup.dismiss()
            self.reset()


class InventoryItemsScreen(Screen):
    img_address = ObjectProperty(None)
    items_panel = ObjectProperty(None)
    fc = ObjectProperty(None)
    inventory_id = None
    item_id = None
    inventory_image = Image()
    r1c2 = ObjectProperty(None)
    r2c2 = ObjectProperty(None)
    r3c2 = ObjectProperty(None)
    r4c2 = ObjectProperty(None)
    r5c2 = ObjectProperty(None)
    r6c2 = ObjectProperty(None)
    add_popup = Popup()
    edit_popup = Popup()
    from_id = None
    reorder_list = {}

    def loading(self):
        popup = Popup()
        popup.title = 'Loading Screen'
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Loading Screen...'))
        popup.content = layout
        run_page = Thread(target=self.reset)
        run_page.start()
        # run_page.join()
        # popup.dismiss

    def reset(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
        self.inventory_id = None
        self.get_inventory()
        self.item_id = None
        self.inventory_image.source = ''
        self.from_id = None
        self.reorder_list = {}

    def get_inventory(self):
        inventories = Inventory().where({'company_id': '{}'.format(vars.COMPANY_ID),
                                         'ORDER_BY': 'ordered ASC'})
        if inventories:
            idx = 0
            self.items_panel.clear_tabs()
            self.items_panel.clear_widgets()
            for inventory in inventories:
                idx += 1
                inventory_id = inventory['inventory_id']
                self.reorder_list[inventory_id] = []
                if not self.inventory_id and idx == 1:
                    self.inventory_id = inventory_id
                inventory_name = inventory['name']
                iitems = InventoryItem()
                inventory_items = iitems.where({'inventory_id': inventory_id, 'ORDER_BY': 'ordered ASC'})
                tph = TabbedPanelHeader(text='{}'.format(inventory_name),
                                        on_release=partial(self.set_inventory, inventory_id))
                layout = ScrollView()
                content = Factory.GridLayoutForScrollView()

                if inventory_items:
                    for item in inventory_items:
                        item_id = item['item_id']
                        item_price = '${:,.2f}'.format(item['price'])
                        self.reorder_list[inventory_id].append(item_id)

                        if self.item_id is item_id:
                            items_button = Factory.ItemsFromButton(text='[b]{}[/b]\n[i]{}[/i]'.format(item['name'],
                                                                                                      item_price),
                                                                   on_release=partial(self.set_item, item_id))
                            self.from_id = self.item_id
                        else:
                            items_button = Factory.ItemsButton(text='[b]{}[/b]\n[i]{}[/i]'.format(item['name'],
                                                                                                  item_price),
                                                               on_release=partial(self.set_item, item_id))
                        content.add_widget(items_button)
                layout.add_widget(content)
                tph.content = layout
                self.items_panel.add_widget(tph)
                if self.inventory_id is inventory_id:
                    self.items_panel.switch_to(tph)

    def set_inventory(self, inventory_id, *args, **kwargs):
        self.inventory_id = inventory_id

    def set_item(self, item_id, *args, **kwargs):
        self.item_id = item_id
        if self.from_id:
            if self.inventory_id in self.reorder_list:
                idx = -1
                for list_id in self.reorder_list[self.inventory_id]:
                    idx += 1
                    if list_id is self.item_id:
                        self.reorder_list[self.inventory_id][idx] = self.from_id
                    if list_id is self.from_id:
                        self.reorder_list[self.inventory_id][idx] = self.item_id
                row = 0
                inv_items = InventoryItem()
                for list_id in self.reorder_list[self.inventory_id]:
                    row += 1
                    inv_items.put(where={'company_id': vars.COMPANY_ID,
                                         'item_id': list_id},
                                  data={'ordered': row})
            self.from_id = None
            self.item_id = None
            self.reorder_list = {}
            self.get_inventory()
        else:
            self.add_popup.size_hint = (None, None)
            self.add_popup.size = (800, 400)
            self.add_popup.title = 'Select Inventory Method'
            layout = BoxLayout(orientation='vertical')
            inner_layout_1 = BoxLayout(orientation='horizontal',
                                       size_hint=(1, 0.6))
            inner_layout_1.add_widget(Button(text='Reorder',
                                             on_release=self.reorder_item))
            inner_layout_1.add_widget(Button(text='Edit',
                                             on_release=self.edit_show))
            inner_layout_1.add_widget(Button(text='Delete',
                                             on_release=self.delete_confirm))
            inner_layout_2 = BoxLayout(orientation='horizontal',
                                       size_hint=(1, 0.3))
            inner_layout_2.add_widget(Button(text='Cancel',
                                             on_release=self.add_popup.dismiss))
            layout.add_widget(inner_layout_1)
            layout.add_widget(inner_layout_2)
            self.add_popup.content = layout
            self.add_popup.open()

    def reorder_item(self, *args, **kwargs):
        self.get_inventory()
        self.add_popup.dismiss()

    def edit_show(self, *args, **kwargs):
        self.add_popup.dismiss()

        self.edit_popup.title = 'Edit Item'
        inventory_items = InventoryItem()
        invitems = inventory_items.where({'company_id': vars.COMPANY_ID,
                                          'item_id': self.item_id})
        if invitems:
            for item in invitems:
                ordered = item['ordered']
                name = item['name']
                description = item['description']
                tags = item['tags']
                quantity = item['quantity']
                price = item['price']
                image_src = inventory_items.get_image_src(item['item_id'])
        else:
            name = ''
            description = ''
            tags = ''
            quantity = ''
            price = ''
            image_src = ''

        layout = BoxLayout(orientation='vertical',
                           pos_hint={'top': 1})
        inner_layout_1 = BoxLayout(orientation='horizontal')
        inner_group_1 = BoxLayout(orientation='vertical',
                                  size_hint=(0.5, 0.9))
        inner_form = GridLayout(cols=2,
                                rows=7,
                                row_force_default=True,
                                row_default_height='50sp',
                                spacing='3dp')
        r1c1 = Factory.CenteredFormLabel(text='Name')
        self.r1c2 = Factory.CenterVerticalTextInput(text=str(name))
        r2c1 = Factory.CenteredFormLabel(text='Description')
        self.r2c2 = Factory.CenterVerticalTextInput(text=str(description))
        r3c1 = Factory.CenteredFormLabel(text='Tags')
        self.r3c2 = Factory.CenterVerticalTextInput(text=str(tags))
        r4c1 = Factory.CenteredFormLabel(text='Quantity')
        self.r4c2 = Factory.CenterVerticalTextInput(text=str(quantity))
        r5c1 = Factory.CenteredFormLabel(text='Ordered')
        self.r5c2 = Factory.CenterVerticalTextInput(text=str(ordered))
        r6c1 = Factory.CenteredFormLabel(text='Price')
        self.r6c2 = Factory.CenterVerticalTextInput(text='{0:0>2}'.format(price))
        inner_form.add_widget(r1c1)
        inner_form.add_widget(self.r1c2)
        inner_form.add_widget(r2c1)
        inner_form.add_widget(self.r2c2)
        inner_form.add_widget(r3c1)
        inner_form.add_widget(self.r3c2)
        inner_form.add_widget(r4c1)
        inner_form.add_widget(self.r4c2)
        inner_form.add_widget(r5c1)
        inner_form.add_widget(self.r5c2)
        inner_form.add_widget(r6c1)
        inner_form.add_widget(self.r6c2)
        inner_group_1.add_widget(inner_form)
        inner_layout_1.add_widget(inner_group_1)
        inner_layout_1_2 = BoxLayout(orientation='vertical',
                                     size_hint=(0.5, 0.9))
        self.fc = Factory.ImageFileChooser()
        inner_layout_1_2.add_widget(self.fc)
        self.fc.ids.inventory_image.source = '{}'.format(image_src)
        inner_layout_1.add_widget(inner_layout_1_2)
        inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                   orientation='horizontal')
        cancel_button = Button(markup=True,
                               text='Cancel',
                               on_release=self.edit_popup.dismiss)
        add_button = Button(markup=True,
                            text='[color=0AAC00][b]Edit[/b][/color]',
                            on_release=self.edit_item)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(add_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.edit_popup.content = layout
        self.edit_popup.open()

    def delete_confirm(self, *args, **kwargs):
        popup = Popup()
        popup.size_hint = (None, None)
        popup.size = (800, 600)
        popup.title = 'Delete Confirmation'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = Label(size_hint=(1, 0.7),
                               markup=True,
                               text='Are you sure you wish to delete this inventory item (#{})?'.format(self.item_id))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.3))
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_release=popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=FF0000][b]Delete[/b][/color]',
                                         on_press=self.delete_item,
                                         on_release=popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def delete_item(self, *args, **kwargs):
        self.add_popup.dismiss()

        inventory_items = InventoryItem()
        deleted = inventory_items.where({'company_id': vars.COMPANY_ID,
                                         'item_id': self.item_id})
        if deleted:
            for deleted_items in deleted:
                inventory_items.id = deleted_items['id']
                if inventory_items.delete():
                    popup = Popup()
                    popup.title = 'Deleted Item Notification'
                    popup.size_hint = (None, None)
                    popup.size = (800, 600)
                    content = KV.popup_alert('Successfully deleted item')
                    popup.content = Builder.load_string(content)
                    popup.open()
        else:
            popup = Popup()
            popup.title = 'Deleted Item Notification'
            popup.size_hint = (None, None)
            popup.size = (800, 600)
            content = KV.popup_alert('Could not delete item. Try again.')
            popup.content = Builder.load_string(content)
            popup.open()

    def add_item_popup(self):
        inventory_items = InventoryItem()
        invitems = inventory_items.where({'company_id': vars.COMPANY_ID,
                                          'inventory_id': self.inventory_id,
                                          'ORDER_BY': 'ordered desc',
                                          'LIMIT': 1})
        next_ordered = 1
        if invitems:
            for item in invitems:
                ordered = item['ordered']
                next_ordered += ordered

        self.add_popup.title = 'Add A New Item'
        layout = BoxLayout(orientation='vertical',
                           pos_hint={'top': 1})
        inner_layout_1 = BoxLayout(orientation='horizontal')
        inner_group_1 = BoxLayout(orientation='vertical',
                                  size_hint=(0.5, 0.9))
        inner_form = GridLayout(cols=2,
                                rows=7,
                                row_force_default=True,
                                row_default_height='50sp',
                                spacing='3dp')
        r1c1 = Factory.CenteredFormLabel(text='Name')
        self.r1c2 = Factory.CenterVerticalTextInput()
        r2c1 = Factory.CenteredFormLabel(text='Description')
        self.r2c2 = Factory.CenterVerticalTextInput()
        r3c1 = Factory.CenteredFormLabel(text='Tags')
        self.r3c2 = Factory.CenterVerticalTextInput()
        r4c1 = Factory.CenteredFormLabel(text='Quantity')
        self.r4c2 = Factory.CenterVerticalTextInput()
        r5c1 = Factory.CenteredFormLabel(text='Ordered')
        self.r5c2 = Factory.CenterVerticalTextInput()
        r6c1 = Factory.CenteredFormLabel(text='Price')
        self.r6c2 = Factory.CenterVerticalTextInput()
        inner_form.add_widget(r1c1)
        inner_form.add_widget(self.r1c2)
        inner_form.add_widget(r2c1)
        inner_form.add_widget(self.r2c2)
        inner_form.add_widget(r3c1)
        inner_form.add_widget(self.r3c2)
        inner_form.add_widget(r4c1)
        inner_form.add_widget(self.r4c2)
        inner_form.add_widget(r5c1)
        inner_form.add_widget(self.r5c2)
        inner_form.add_widget(r6c1)
        inner_form.add_widget(self.r6c2)
        inner_group_1.add_widget(inner_form)
        inner_layout_1.add_widget(inner_group_1)
        self.r5c2.text = '{}'.format(str(next_ordered))
        inner_layout_1_2 = BoxLayout(orientation='vertical',
                                     size_hint=(0.5, 0.9))
        self.fc = Factory.ImageFileChooser()
        inner_layout_1_2.add_widget(self.fc)
        inner_layout_1.add_widget(inner_layout_1_2)
        inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                   orientation='horizontal')
        cancel_button = Button(markup=True,
                               text='Cancel',
                               on_release=self.add_popup.dismiss)
        add_button = Button(markup=True,
                            text='[color=0AAC00][b]Add[/b][/color]',
                            on_release=self.add_item)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(add_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.add_popup.content = layout
        self.add_popup.open()

    def add_item(self, *args, **kwargs):
        # validate
        errors = 0

        if not self.r1c2.text:
            errors += 1

        if not self.r2c2.text:
            errors += 1

        if not self.r3c2.text:
            errors += 1

        if not self.r4c2.text:
            errors += 1

        if not self.r5c2.text:
            errors += 1

        if not self.r6c2.text:
            errors += 1

        img = self.fc.ids.inventory_image.source.replace('/', ' ').split() if self.fc.ids.inventory_image.source else [
            'question.png']
        img_name = img[-1]
        if errors == 0:
            inventory_items = InventoryItem()
            inventory_items.company_id = vars.COMPANY_ID
            inventory_items.inventory_id = self.inventory_id
            inventory_items.name = self.r1c2.text
            inventory_items.description = self.r2c2.text
            inventory_items.tags = self.r3c2.text
            inventory_items.quantity = self.r4c2.text
            inventory_items.ordered = self.r5c2.text
            inventory_items.price = self.r6c2.text
            inventory_items.image = img_name
            if inventory_items.add():
                popup = Popup()
                popup.title = 'Form Success'
                content = KV.popup_alert('Successfully created a new inventory item!')
                popup.content = Builder.load_string(content)
                popup.open()
                self.add_popup.dismiss()
                self.reset()
        else:
            popup = Popup()
            popup.title = 'Form Error'
            content = KV.popup_alert('{} form errors'.format(errors))
            popup.content = Builder.load_string(content)
            popup.open()

    def edit_item(self, *args, **kwargs):
        # validate
        errors = 0

        if not self.r1c2.text:
            errors += 1

        if not self.r2c2.text:
            errors += 1

        if not self.r3c2.text:
            errors += 1

        if not self.r4c2.text:
            errors += 1

        if not self.r5c2.text:
            errors += 1

        if not self.r6c2.text:
            errors += 1

        img = self.fc.ids.inventory_image.source.replace('/', ' ').split() if self.fc.ids.inventory_image.source else [
            'question.png']
        img_name = img[-1]
        if errors == 0:
            inventory_items = InventoryItem()
            put = inventory_items.put(where={'company_id': vars.COMPANY_ID,
                                             'item_id': self.item_id},
                                      data={'name': self.r1c2.text,
                                            'description': self.r2c2.text,
                                            'tags': self.r3c2.text,
                                            'quantity': self.r4c2.text,
                                            'ordered': self.r5c2.text,
                                            'price': self.r6c2.text,
                                            'image': img_name})
            if put:
                popup = Popup()
                popup.title = 'Form Success'
                content = KV.popup_alert('Successfully updated item!')
                popup.content = Builder.load_string(content)
                popup.open()
                self.edit_popup.dismiss()
                self.from_id = None
                self.item_id = None
                self.reorder_list = {}
                self.get_inventory()
        else:
            popup = Popup()
            popup.title = 'Form Error'
            content = KV.popup_alert('{} form errors'.format(errors))
            popup.content = Builder.load_string(content)
            popup.open()


class ItemDetailsScreen(Screen):
    name = ObjectProperty(None)
    items_table = ObjectProperty(None)
    inventory_name_label = ObjectProperty(None)
    inventory_item_name = ObjectProperty(None)

    def get_details(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
        # reset invoice_items_id
        vars.INVOICE_ITEMS_ID = None
        # make the items
        self.item_image.source = ''
        self.inventory_name_label.text = ''
        self.inventory_item_name.text = ''
        self.items_table_update()
        pass

    def items_table_update(self):
        self.items_table.clear_widgets()
        iitems = InvoiceItem()
        data = {'item_id': vars.ITEM_ID, 'invoice_id': vars.INVOICE_ID}
        inv_items = iitems.where(data)
        if inv_items:
            # create headers
            # create TH
            h1 = KV.sized_invoice_tr(0, 'ID', size_hint_x=0.1)
            h2 = KV.sized_invoice_tr(0, 'Qty', size_hint_x=0.1)
            h3 = KV.sized_invoice_tr(0, 'Item', size_hint_x=0.6)
            h4 = KV.sized_invoice_tr(0, 'Subtotal', size_hint_x=0.2)
            self.items_table.add_widget(Builder.load_string(h1))
            self.items_table.add_widget(Builder.load_string(h2))
            self.items_table.add_widget(Builder.load_string(h3))
            self.items_table.add_widget(Builder.load_string(h4))

            for invoice_item in inv_items:
                invoice_items_id = invoice_item['invoice_items_id']
                selected = True if invoice_items_id == vars.INVOICE_ITEMS_ID else False
                item_id = invoice_item['item_id']
                items_search = InventoryItem()
                itm_srch = items_search.where({'item_id': item_id})

                if itm_srch:
                    for itm in itm_srch:
                        item_name = itm['name']
                else:
                    item_name = ''
                tr1 = KV.sized_invoice_tr(1,
                                          invoice_item['id'],
                                          size_hint_x=0.1,
                                          selected=selected,
                                          on_release='app.root.current="item_details"',
                                          on_press='self.parent.parent.parent.parent.item_details({})'.format(
                                              invoice_items_id))

                tr2 = KV.sized_invoice_tr(1,
                                          invoice_item['quantity'],
                                          size_hint_x=0.1,
                                          selected=selected,
                                          on_release='app.root.current="item_details"',
                                          on_press='self.parent.parent.parent.parent.item_details({})'.format(
                                              invoice_items_id))
                color_name = invoice_item['color']

                item_string = "[b]{item}[/b]:\\n {color_s} {memo_s}".format(item=item_name,
                                                                            color_s='{}'.format(color_name),
                                                                            memo_s='{}'.format(invoice_item['memo']))
                # print(item_string)
                tr3 = KV.sized_invoice_tr(1,
                                          item_string,
                                          text_wrap=True,
                                          size_hint_x=0.6,
                                          selected=selected,
                                          on_release='app.root.current="item_details"',
                                          on_press='self.parent.parent.parent.parent.item_details({})'.format(
                                              invoice_items_id))

                tr4 = KV.sized_invoice_tr(1,
                                          '${:,.2f}'.format(invoice_item['pretax']),
                                          size_hint_x=0.2,
                                          selected=selected,
                                          on_release='app.root.current="item_details"',
                                          on_press='self.parent.parent.parent.parent.item_details({})'.format(
                                              invoice_items_id))
                self.items_table.add_widget(Builder.load_string(tr1))
                self.items_table.add_widget(Builder.load_string(tr2))
                self.items_table.add_widget(Builder.load_string(tr3))
                self.items_table.add_widget(Builder.load_string(tr4))

    def item_details(self, item_id):
        # highlight the selected invoice items
        vars.INVOICE_ITEMS_ID = item_id
        self.items_table_update()
        # get item details and display them to item_detail_history_table
        invoice_items = InvoiceItem().where({'id': item_id})
        if invoice_items:
            for invoice_item in invoice_items:
                inventory_item_id = invoice_item['item_id']
                items = InventoryItem()
                iitems = items.where({'item_id': inventory_item_id})
                if iitems:
                    for iitem in iitems:
                        inventory_id = iitem['inventory_id']
                        inventories = Inventory().where({'inventory_id': inventory_id})
                        if inventories:
                            for inventory in inventories:
                                inventory_name = inventory['name']
                        else:
                            inventory_name = ''
                        items.image = items.get_image_src(invoice_item['item_id'])
                        items.name = iitem['name']
                    self.item_image.source = items.image if items.image else ''
                    self.inventory_item_name.text = items.name if items.name else ''
                    self.inventory_name_label.text = inventory_name if inventory_name else ''

                    # update the rfid table history

        pass


class InvoiceDetailsScreen(Screen):
    invoice_number_label = ObjectProperty(None)
    customer_type_label = ObjectProperty(None)
    full_name_label = ObjectProperty(None)
    last4_label = ObjectProperty(None)
    phone_label = ObjectProperty(None)
    dropoff_label = ObjectProperty(None)
    payment_id_label = ObjectProperty(None)
    payment_type_label = ObjectProperty(None)
    pickup_label = ObjectProperty(None)
    profile_id_label = ObjectProperty(None)
    rack_label = ObjectProperty(None)
    rack_date_label = ObjectProperty(None)
    items_table = ObjectProperty(None)
    quantity_label = ObjectProperty(None)
    subtotal_label = ObjectProperty(None)
    tax_label = ObjectProperty(None)
    total_label = ObjectProperty(None)
    discount_label = ObjectProperty(None)
    credit_label = ObjectProperty(None)
    tendered_label = ObjectProperty(None)
    due_label = ObjectProperty(None)

    def get_details(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
        invoices = Invoice().where({'invoice_id': vars.INVOICE_ID})
        if invoices:
            # reset the page first
            self.invoice_number_label.text = ''
            self.customer_type_label.text = ''
            self.full_name_label.text = ''
            self.phone_label.text = ''
            self.dropoff_label.text = ''
            self.pickup_label.text = ''
            self.rack_label.text = ''
            self.rack_date_label.text = ''
            self.total_label.text = '$0.00'
            self.quantity_label.text = '0'
            self.subtotal_label.text = '$0.00'
            self.tax_label.text = '$0.00'
            self.credit_label.text = '$0.00'
            self.discount_label.text = '$0.00'
            self.tendered_label.text = '$0.00'
            self.due_label.text = '0.00'
            for invoice in invoices:
                # get the invoice information
                base_invoice_id = invoice['id']
                company_id = invoice['company_id']
                quantity = invoice['quantity']
                subtotal = '${:,.2f}'.format(invoice['pretax']) if invoice['pretax'] else '$0.00'
                tax = '${:,.2f}'.format(invoice['tax']) if invoice['tax'] else '$0.00'
                total = '${:,.2f}'.format(invoice['total']) if invoice['total'] else '$0.00'
                rack = invoice['rack'] if invoice['rack'] else ''
                rack_date = invoice['rack_date'] if invoice['rack_date'] else ''
                dropoff_date = invoice['created_at'] if invoice['created_at'] else ''
                due_date = invoice['due_date'] if invoice['due_date'] else ''
                memo = invoice['memo']
                status = invoice['status']
                self.invoice_number_label.text = '[color=000000]#{}[/color]'.format(
                    vars.INVOICE_ID) if vars.INVOICE_ID else ''
                self.dropoff_label.text = '[color=000000]{}[/color]'.format(dropoff_date)
                self.rack_label.text = '[color=000000]{}[/color]'.format(rack)
                self.rack_date_label.text = '[color=000000]{}[/color]'.format(rack_date)
                self.quantity_label.text = '[color=000000]{}[/color]'.format(quantity)
                self.subtotal_label.text = '[color=000000]{}[/color]'.format(subtotal)
                self.tax_label.text = '[color=000000]{}[/color]'.format(tax)
                self.total_label.text = '[color=000000]{}[/color]'.format(total)

                # get the customer information
                customer_id = invoice['customer_id']
                users = User().where({'user_id': customer_id})
                if users:
                    for user in users:
                        last_name = user['last_name']
                        first_name = user['first_name']
                        full_name = '{}, {}'.format(last_name.capitalize(), first_name.capitalize())
                        phone = user['phone']
                        payment_id = user['payment_id']
                        profile_id = user['profile_id']
                        delivery = 'Delivery' if user['delivery'] == 1 else False
                        account = 'Account' if user['account'] == 1 else False
                        if delivery:
                            customer_type = delivery
                        elif account:
                            customer_type = account
                        else:
                            customer_type = 'General'
                        self.full_name_label.text = '[color=000000]{}[/color]'.format(full_name)
                        self.phone_label.text = '[color=000000]{}[/color]'.format(phone)
                        self.customer_type_label.text = '[color=000000]{}[/color]'.format(customer_type)
                        self.payment_id_label.text = '[color=000000]{}[/color]'.format(payment_id)
                        self.profile_id_label.text = '[color=000000]{}[/color]'.format(profile_id)

                # update the items table
                self.items_table_update()

                # get the transaction information
                transaction_id = invoice['transaction_id']
                transactions = Transaction().where({'transaction_id': transaction_id})
                if transactions:
                    for transaction in transactions:
                        payment_type = transaction['type']
                        discount_pre = transaction['discount'] if transaction['discount'] else 0
                        discount_total = discount_pre + 0
                        tendered_total = transaction['tendered'] if transaction['tendered'] else 0
                        if payment_type == 1:
                            transaction_type = 'Credit'
                            tendered = invoice['total'] - discount_total

                        elif payment_type == 2:
                            transaction_type = 'Cash'
                        elif payment_type == 3:
                            transaction_type = 'Check'
                            tendered_total = invoice['total'] - discount_total
                        else:
                            transaction_type = ''

                        last4 = transaction['last_four']
                        pickup_date = transaction['created_at'] if transaction['created_at'] else ''

                        discount = '${:,.2f}'.format(transaction['discount']) if transaction['discount'] else '$0.00'
                        # need to add in credits
                        credit = '$0.00'
                        due_amt = invoice['total'] - discount_total - tendered_total
                        due = '${:,.2f}'.format(due_amt)

                        self.pickup_label.text = '[color=000000]{}[/color]'.format(pickup_date)
                        self.payment_type_label.text = '[color=000000]{}[/color]'.format(transaction_type)
                        self.last4_label.text = '[color=000000]{}[/color]'.format(last4)
                        self.discount_label.text = '[color=000000]{}[/color]'.format(discount)
                        self.credit_label.text = '[color=000000]{}[/color]'.format(credit)
                        self.due_label.text = '[color=000000][b]{}[/b][/color]'.format(due)
                        self.tendered_label.text = '[color=000000]{}[/color]'.format('${:,.2f}'.format(tendered_total))
                else:
                    self.pickup_label.text = '[color=000000]{}[/color]'.format('')
                    self.payment_type_label.text = '[color=000000]{}[/color]'.format('')
                    self.last4_label.text = '[color=000000]{}[/color]'.format('')
                    self.discount_label.text = '[color=000000]{}[/color]'.format('$0.00')
                    self.credit_label.text = '[color=000000]{}[/color]'.format('$0.00')
                    self.due_label.text = '[color=000000][b]{}[/b][/color]'.format(total)
                    self.tendered_label.text = '[color=000000]{}[/color]'.format('$0.00')

    def items_table_update(self):
        self.items_table.clear_widgets()
        iitems = InvoiceItem()
        data = {'invoice_id': vars.INVOICE_ID}
        inv_items = iitems.where(data)
        if inv_items:
            # create headers
            # create TH
            h1 = KV.sized_invoice_tr(0, 'Qty', size_hint_x=0.2)
            h2 = KV.sized_invoice_tr(0, 'Item', size_hint_x=0.6)
            h3 = KV.sized_invoice_tr(0, 'Subtotal', size_hint_x=0.2)
            self.items_table.add_widget(Builder.load_string(h1))
            self.items_table.add_widget(Builder.load_string(h2))
            self.items_table.add_widget(Builder.load_string(h3))
            items = {}

            for invoice_item in inv_items:
                item_id = invoice_item['item_id']
                items_search = InventoryItem()
                itm_srch = items_search.where({'item_id': item_id})

                if itm_srch:
                    for itm in itm_srch:
                        item_name = itm['name']
                else:
                    item_name = ''

                items[item_id] = {
                    'name': item_name,
                    'total': 0,
                    'quantity': 0,
                    'color': {},
                    'memo': []
                }
            # populate correct item totals
            if items:
                for key, value in items.items():
                    item_id = key
                    data = {
                        'invoice_id': vars.INVOICE_ID,
                        'item_id': item_id
                    }
                    iinv_items = InvoiceItem().where(data)
                    if iinv_items:
                        for inv_item in iinv_items:
                            items[item_id]['quantity'] += int(inv_item['quantity']) if inv_item['quantity'] else 1
                            items[item_id]['total'] += float(inv_item['pretax']) if inv_item['pretax'] else 0
                            if inv_item['color'] in items[item_id]['color']:
                                items[item_id]['color'][inv_item['color']] += 1
                            else:
                                items[item_id]['color'][inv_item['color']] = 1
                            if inv_item['memo']:
                                items[item_id]['memo'].append(inv_item['memo'])
            # print out the items into the table
            if items:
                for key, value in items.items():
                    tr1 = KV.sized_invoice_tr(1, value['quantity'], size_hint_x=0.2)
                    color_string = []
                    for name, color_qty in value['color'].items():
                        if name:
                            color_string.append('{count}-{name}'.format(count=str(color_qty),
                                                                        name=name))

                    item_string = "[b]{item}[/b]:\\n {color_s} {memo_s}".format(item=value['name'],
                                                                                color_s=', '.join(color_string),
                                                                                memo_s='/ '.join(value['memo']))
                    # print(item_string)
                    tr2 = KV.sized_invoice_tr(1,
                                              item_string,
                                              text_wrap=True,
                                              size_hint_x=0.6)

                    tr3 = KV.sized_invoice_tr(1, '${:,.2f}'.format(value['total']), size_hint_x=0.2)
                    self.items_table.add_widget(Builder.load_string(tr1))
                    self.items_table.add_widget(Builder.load_string(tr2))
                    self.items_table.add_widget(Builder.load_string(tr3))


class Last10Screen(Screen):
    last10_table = ObjectProperty(None)
    last10_footer = ObjectProperty(None)

    def get_last10(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
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
                text_color = 'e5e5e5' if even_odd % 2 == 0 else '000000'
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
                        tr6 = KV.widget_item(type='Label', data=Job.make_us_phone(cust['phone']), rgba=rgba,
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


class MemosScreen(Screen):
    popup_memo = Popup()
    memo_id = None
    memos_table = ObjectProperty(None)
    reorder_start_id = None
    reorder_end_id = None
    msg = None

    def reset(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
        self.memo_id = None
        self.create_memo_table()
        pass

    def create_memo_table(self):
        self.memos_table.clear_widgets()
        mmos = Memo()
        memos = mmos.where({'company_id': vars.COMPANY_ID,
                            'ORDER_BY': 'ordered asc'})
        if memos:
            for memo in memos:
                m_id = memo['id']
                memo_msg = memo['memo']
                if self.reorder_start_id is None:
                    memo_item = Factory.LongButton(text='{}'.format(memo_msg),
                                                   on_press=partial(self.set_memo_id, m_id),
                                                   on_release=self.memo_actions_popup)
                elif self.reorder_start_id is m_id:
                    memo_item = Factory.LongButton(text='{}'.format(memo_msg),
                                                   markup=True,
                                                   on_press=partial(self.set_memo_id, m_id),
                                                   on_release=self.memo_actions_popup,
                                                   background_normal='',
                                                   background_color=(0, 0.64, 0.149, 1))
                elif self.reorder_start_id != None and self.reorder_start_id != m_id:
                    memo_item = Factory.LongButton(text='{}'.format(memo_msg),
                                                   on_release=partial(self.set_reorder_end_id, m_id))

                self.memos_table.add_widget(memo_item)

    def memo_actions_popup(self, *args, **kwargs):
        popup = Popup()
        popup.title = 'Memo Actions'
        popup.size_hint = (None, None)
        popup.size = (800, 600)
        content = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.9))
        inner_layout_1.add_widget(Button(text='reorder',
                                         on_press=self.reorder_start,
                                         on_release=popup.dismiss))
        inner_layout_1.add_widget(Button(text='edit',
                                         on_press=popup.dismiss,
                                         on_release=self.popup_memos_edit))
        inner_layout_1.add_widget(Button(text='delete',
                                         on_press=self.delete_confirm))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(text='cancel',
                                         on_release=popup.dismiss))
        content.add_widget(inner_layout_1)
        content.add_widget(inner_layout_2)
        popup.content = content
        popup.open()

    def set_memo_id(self, id, *args, **kwargs):
        self.memo_id = id

    def reorder_start(self, *args, **kwargs):
        self.reorder_start_id = self.memo_id
        self.reset()

    def set_reorder_end_id(self, id, *args, **kwargs):
        print('end set')
        self.reorder_end_id = id
        self.reorder()

    def reorder(self, *args, **kwargs):
        mmos = Memo()
        memo_start = mmos.where({'id': self.reorder_start_id})
        order_start = None
        if memo_start:
            for memo in memo_start:
                order_start = memo['ordered']
        memo_end = mmos.where({'id': self.reorder_end_id})
        order_end = None
        if memo_end:
            for memo in memo_end:
                order_end = memo['ordered']

        put_start = mmos.put(where={'id': self.reorder_start_id},
                             data={'ordered': order_end})

        put_end = mmos.put(where={'id': self.reorder_end_id},
                           data={'ordered': order_start})
        if put_start and put_end:
            self.reorder_start_id = None
            self.reorder_end_id = None
            self.reset()

        else:
            popup = Popup()
            popup.title = 'Reorder Status'
            popup.content = Builder.load_string(KV.popup_alert('Could not reorder. Try again.'))
            popup.open()
        pass

    def popup_memos_add(self):
        self.popup_memo.title = 'Add A Memo'
        content = BoxLayout(orientation='vertical')
        inner_layout_1 = GridLayout(cols=2,
                                    size_hint=(1, 0.9),
                                    row_force_default=True,
                                    row_default_height='50sp')
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Memo'))
        self.msg = Factory.CenterVerticalTextInput()
        inner_layout_1.add_widget(self.msg)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(text='cancel',
                                         on_release=self.popup_memo.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=00ff00][b]Add[/b][/color]',
                                         on_release=self.add_memo))
        content.add_widget(inner_layout_1)
        content.add_widget(inner_layout_2)
        self.popup_memo.content = content
        self.popup_memo.open()

    def add_memo(self, *args, **kwargs):
        mmos = Memo()
        search = mmos.where({'company_id': vars.COMPANY_ID,
                             'ORDER_BY': 'ordered desc',
                             'LIMIT': 1})
        next_ordered = 1
        if search:
            for memo in search:
                next_ordered = int(memo['ordered']) + 1

        if self.msg.text is not None:
            mmos.company_id = vars.COMPANY_ID
            mmos.memo = self.msg.text
            mmos.ordered = next_ordered
            mmos.status = 1

            if mmos.add():
                popup = Popup()
                popup.title = 'Memo'
                popup.content = Builder.load_string(KV.popup_alert('Successfully added new memo'))
                popup.open()
                self.popup_memo.dismiss()
                self.memo_id = None
                self.reorder_start_id = None
                self.reorder_end_id = None
                self.reset()

    def delete_confirm(self, *args, **kwargs):
        popup = Popup()
        popup.title = 'Delete Confirmation'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='vertical',
                                   size_hint=(1, 0.9))
        inner_layout_1.add_widget(Label(text='Are you sure?'))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(text='cancel',
                                         on_release=popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=00ff00][b]cancel[/b][/color]',
                                         on_press=popup.dismiss,
                                         on_release=self.delete_memo))
        popup.content = layout
        popup.open()

    def delete_memo(self, *args, **kwargs):
        mmos = Memo()
        mmos.id = self.memo_id
        if mmos.delete():
            popup = Popup()
            popup.title = 'Deleted Memo'
            popup.content = Builder.load_string(KV.popup_alert('Successfully removed memo'))
            popup.open()
            self.reset()

    def popup_memos_edit(self, *args, **kwargs):

        mmos = Memo()
        memos = mmos.where({'id': self.memo_id})
        msg = ''
        if memos:
            for memo in memos:
                msg = memo['memo']
        self.popup_memo.title = 'Edit Memo'
        content = BoxLayout(orientation='vertical')
        inner_layout_1 = GridLayout(cols=2,
                                    size_hint=(1, 0.9),
                                    row_force_default=True,
                                    row_default_height='50sp')
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Memo'))
        self.msg = Factory.CenterVerticalTextInput(text=str(msg))
        inner_layout_1.add_widget(self.msg)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(text='cancel',
                                         on_release=self.popup_memo.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=00ff00][b]Edit[/b][/color]',
                                         on_release=self.edit_memo))
        content.add_widget(inner_layout_1)
        content.add_widget(inner_layout_2)
        self.popup_memo.content = content
        self.popup_memo.open()

    def edit_memo(self, *args, **kwargs):
        mmos = Memo()
        mmos.memo = self.msg.text
        put = mmos.put(where={'id': self.memo_id},
                       data={'memo': self.msg.text})
        if put:
            popup = Popup()
            popup.title = 'Updated Memo'
            popup.content = Builder.load_string(KV.popup_alert('Successfully updated memo'))
            popup.open()

            self.popup_memo.dismiss()
            self.reset()
            self.memo_id = None
            self.reorder_start_id = None
            self.reorder_end_id = None
        else:
            popup = Popup()
            popup.title = 'Updated Memo'
            popup.content = Builder.load_string(KV.popup_alert('Could not edit memo. Please try again.'))
            popup.open()


class NewCustomerScreen(Screen):
    last_name = ObjectProperty(None)
    first_name = ObjectProperty(None)
    phone = ObjectProperty(None)
    email = ObjectProperty(None)
    important_memo = ObjectProperty(None)
    invoice_memo = ObjectProperty(None)
    shirts_finish = ObjectProperty(None)
    shirts_preference = ObjectProperty(None)
    # default_shirts_finish = ObjectProperty(None)
    is_delivery = ObjectProperty(None)
    is_account = ObjectProperty(None)
    street = ObjectProperty(None)
    suite = ObjectProperty(None)
    city = ObjectProperty(None)
    zipcode = ObjectProperty(None)
    concierge_name = ObjectProperty(None)
    concierge_number = ObjectProperty(None)
    special_instructions = ObjectProperty(None)
    new_customer_panel = ObjectProperty(None)
    tab_new_customer = ObjectProperty(None)

    main_grid = ObjectProperty(None)

    def reset(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
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
        self.is_account.active = False
        self.main_grid.clear_widgets()
        self.main_grid.add_widget(Factory.BottomLeftFormLabel(text="Phone"))
        self.phone = Factory.CenterVerticalTextInput()
        self.main_grid.add_widget(self.phone)
        self.main_grid.add_widget(Factory.BottomLeftFormLabel(text="Last Name"))
        self.last_name = Factory.CenterVerticalTextInput()
        self.main_grid.add_widget(self.last_name)
        self.main_grid.add_widget(Factory.BottomLeftFormLabel(text="First Name"))
        self.first_name = Factory.CenterVerticalTextInput()
        self.main_grid.add_widget(self.first_name)
        self.main_grid.add_widget(Factory.BottomLeftFormLabel(text="Email"))
        self.email = Factory.CenterVerticalTextInput()
        self.main_grid.add_widget(self.email)
        self.main_grid.add_widget(Factory.BottomLeftFormLabel(text="Important Memo"))
        self.important_memo = Factory.CenterVerticalTextInput()
        self.main_grid.add_widget(self.important_memo)
        self.main_grid.add_widget(Factory.BottomLeftFormLabel(text="Invoice Memo"))
        self.invoice_memo = Factory.CenterVerticalTextInput()
        self.main_grid.add_widget(self.invoice_memo)
        self.main_grid.add_widget(Factory.BottomLeftFormLabel(text="Shirts Finish"))
        self.shirts_finish = Spinner(
            # default value shown
            text='Hanger',
            # available values
            values=["Hanger", "Box"],
            # just for positioning in our example
            size_hint_x=1,
            size_hint_y=0.5,
            pos_hint={'center_x': .5, 'center_y': .5})
        self.shirts_finish.bind(text=self.select_shirts_finish)
        self.main_grid.add_widget(self.shirts_finish)
        self.main_grid.add_widget(Factory.BottomLeftFormLabel(text="Shirts Preference"))
        self.shirts_preference = Spinner(
            # default value shown
            text='None',
            # available values
            values=["None", "Light", "Medium", "Heavy"],
            # just for positioning in our example
            size_hint_x=1,
            size_hint_y=0.5,
            pos_hint={'center_x': .5, 'center_y': .5})
        self.shirts_preference.bind(text=self.select_shirts_preference)
        self.main_grid.add_widget(self.shirts_preference)
        self.main_grid.add_widget(Label(text=" "))
        self.main_grid.add_widget(Label(text=" "))
        # reset tab cursor
        self.new_customer_panel.switch_to(self.tab_new_customer)
        self.phone.focus = True

    def select_shirts_finish(self, *args, **kwargs):
        selected_value = self.shirts_finish.text
        print(selected_value)

    def select_shirts_preference(self, *args, **kwargs):
        selected_value = self.shirts_preference.text
        print(selected_value)

    def set_delivery(self):
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

    def set_account(self):
        self.street.text = ''
        self.street.hint_text = 'Street Address'
        self.street.hint_text_color = DEFAULT_COLOR
        self.street.disabled = False if self.is_account.active else True
        self.suite.text = ''
        self.suite.hint_text = 'Suite'
        self.suite.hint_text_color = DEFAULT_COLOR
        self.suite.disabled = False if self.is_account.active else True
        self.city.text = ''
        self.city.hint_text = 'City'
        self.city.hint_text_color = DEFAULT_COLOR
        self.city.disabled = False if self.is_account.active else True
        self.zipcode.text = ''
        self.zipcode.hint_text = 'Zipcode'
        self.zipcode.hint_text_color = DEFAULT_COLOR
        self.zipcode.disabled = False if self.is_account.active else True

    def validate(self):
        customers = User()
        popup = Popup()
        popup.size_hint = (None, None)
        popup.size = '600sp', '300sp'

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

        if self.last_name.text is '':
            errors += 1
            self.last_name.hint_text = "required"
            self.last_name.hint_text_color = ERROR_COLOR
        else:
            self.last_name.hint_text = "Last Name"
            self.last_name.hint_text_color = DEFAULT_COLOR

        if self.first_name.text is '':
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
            customers.company_id = vars.COMPANY_ID
            customers.role_id = 5
            customers.phone = Job.make_numeric(data=self.phone.text)
            customers.last_name = Job.make_no_whitespace(data=self.last_name.text)
            customers.first_name = Job.make_no_whitespace(data=self.first_name.text)
            customers.email = self.email.text if Job.check_valid_email(email=self.email.text) else None
            customers.important_memo = self.important_memo.text if self.important_memo.text else None
            customers.invoice_memo = self.invoice_memo.text if self.invoice_memo.text else None
            customers.shirt = '1' if self.shirts_finish.text is "Hanger" else '2'
            shirts_preference = '0'
            if self.shirts_preference.text is 'None':
                shirts_preference = '1'
            elif self.shirts_preference.text is 'Light':
                shirts_preference = '2'
            elif self.shirts_preference.text is 'Medium':
                shirts_preference = '3'
            elif self.shirts_preference.text is 'Heavy':
                shirts_preference = '4'

            customers.starch = shirts_preference
            if self.is_delivery.active:
                customers.concierge_name = self.concierge_name.text
                customers.concierge_number = Job.make_numeric(data=self.concierge_number.text)
                customers.special_instructions = self.special_instructions.text if self.special_instructions.text else None
            if self.is_account.active:
                customers.street = Job.make_no_whitespace(data=self.street.text)
                customers.suite = Job.make_no_whitespace(data=self.suite.text)
                customers.city = Job.make_no_whitespace(data=self.city.text)
                customers.zipcode = Job.make_no_whitespace(data=self.zipcode.text)
            if customers.add():
                run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
                run_sync_2 = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
                try:
                    run_sync.start()
                finally:
                    run_sync.join()
                    print('sync now finished')
                    # send user to search
                    last_row = customers.get_last_inserted_row()
                    customers.id = last_row
                    new_customer = customers.first({'id': customers.id})
                    customers.user_id = new_customer['user_id']
                    if customers.user_id:
                        if self.is_delivery.active:
                            addresses = Address()
                            addresses.user_id = customers.user_id
                            addresses.name = 'Home'
                            addresses.street = self.street.text
                            addresses.suite = Job.make_no_whitespace(data=self.suite.text)
                            addresses.city = Job.make_no_whitespace(data=self.city.text)
                            addresses.state = 'WA'
                            addresses.zipcode = Job.make_no_whitespace(data=self.zipcode.text)
                            addresses.primary_address = 1
                            addresses.concierge_name = self.concierge_name.text
                            addresses.concierge_number = Job.make_numeric(data=self.concierge_number.text)
                            addresses.special_instructions = self.special_instructions.text if self.special_instructions.text else None
                            addresses.status = 1
                            addresses.add()
                        # create the customer mark
                        marks = Custid()
                        marks.customer_id = customers.user_id
                        marks.company_id = vars.COMPANY_ID
                        marks.mark = marks.create_customer_mark(last_name=customers.last_name,
                                                                customer_id=str(customers.user_id),
                                                                starch=customers.get_starch(customers.starch))
                        marks.status = 1
                        if marks.mark:
                            if marks.add():
                                try:
                                    run_sync_2.start()
                                finally:
                                    run_sync_2.join()
                                    self.reset()
                                    self.customer_select(customers.user_id)
                                    # create popup
                                    popup = Popup()
                                    popup.title = 'Saved Customer'
                                    content = KV.popup_alert(
                                        'Saved new customer and created a new shirt mark.')
                                    popup.content = Builder.load_string(content)
                                    popup.open()
                                    # Beep Sound
                                    sys.stdout.write('\a')
                                    sys.stdout.flush()
                        else:
                            popup = Popup()
                            popup.title = 'Saved Customer'
                            content = KV.popup_alert('Saved new customer but could not write a new mark. Add Later.')
                            popup.content = Builder.load_string(content)
                            popup.open()
                            # Beep Sound
                            sys.stdout.write('\a')
                            sys.stdout.flush()
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
    status_popup = Popup()
    invoice_table = ObjectProperty(None)
    quantity_label = ObjectProperty(None)
    subtotal_label = ObjectProperty(None)
    tax_label = ObjectProperty(None)
    total_label = ObjectProperty(None)
    calc_total = ObjectProperty(None)
    credit_card_data_layout = ObjectProperty(None)
    instore_button = ObjectProperty(None)
    online_button = ObjectProperty(None)
    due_label = ObjectProperty(None)
    check_number = ObjectProperty(None)
    payment_panel = ObjectProperty(None)
    credit_card_header = ObjectProperty(None)
    payment_account_header = ObjectProperty(None)
    discount_label = ObjectProperty(None)
    total_discount = ObjectProperty(None)
    main_popup = Popup()
    calc_amount = []
    amount_tendered = 0
    selected_invoices = []
    total_subtotal = 0
    total_quantity = 0
    total_tax = 0
    total_amount = 0
    total_credit = ObjectProperty(None)
    credits = 0
    credits_spent = 0
    discount_total = 0
    total_due = 0
    change_due = 0
    payment_type = 'cc'
    card_location = 1
    finish_popup = Popup()
    card_id_spinner = Spinner()
    cards = None
    card_id = None
    root_payment_id = None
    edit_card_number = None
    edit_card_exp_month = None
    edit_card_exp_year = None
    edit_card_billing_street = None
    edit_card_billing_suite = None
    edit_card_billing_city = None
    edit_card_billing_state = None
    edit_card_billing_zipcode = None
    edit_card_billing_first_name = None
    edit_card_billing_last_name = None
    card_box = None
    discount_id = None

    def reset(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
        # get credit total
        self.credits = 0
        self.credits_spent = 0
        account_status = False
        customers = User().where({'user_id': vars.CUSTOMER_ID})
        if customers:
            for customer in customers:
                self.credits = customer['credits'] if customer['credits'] is not None else 0
                account_status = customer['account']

        if account_status:
            self.payment_panel.switch_to(header=self.payment_account_header)
            self.payment_type = 'ac'
        else:
            self.payment_panel.switch_to(header=self.credit_card_header)
            self.payment_type = 'cc'

        self.total_credit.text = '[color=0AAC00]{}[/color]'.format('${:,.2f}'.format(self.credits))
        self.selected_invoices = []
        # setup invoice table
        self.invoice_table.clear_widgets()

        # make headers
        self.invoice_create_rows()

        # reset payment values
        self.calc_total.text = '[color=000000][b]$0.00[/b][/color]'
        self.calc_amount = []
        self.amount_tendered = 0
        self.selected_invoices = []
        self.total_subtotal = 0
        self.total_quantity = 0
        self.total_tax = 0
        self.total_amount = 0

        self.discount_total = 0
        self.total_due = 0
        self.change_due = 0

        self.card_location = 1
        self.due_label.text = '[color=000000][b]$0.00[/b][/color]'
        self.check_number.text = ''
        self.card_id_spinner = Spinner()
        self.card_id = None
        self.root_payment_id = None
        self.edit_card_number = None
        self.edit_card_exp_month = None
        self.edit_card_exp_year = None
        self.edit_card_billing_street = None
        self.edit_card_billing_suite = None
        self.edit_card_billing_city = None
        self.edit_card_billing_state = None
        self.edit_card_billing_zipcode = None
        self.edit_card_billing_first_name = None
        self.edit_card_billing_last_name = None
        self.card_box = None
        self.discount_id = None
        # reset states
        self.instore_button.state = 'down'
        self.online_button.state = 'normal'

        self.quantity_label.text = '[color=000000][b]$0.00[/b][/color]'
        self.subtotal_label.text = '[color=000000][b]$0.00[/b][/color]'
        self.tax_label.text = '[color=000000][b]$0.00[/b][/color]'
        self.total_label.text = '[color=000000][b]$0.00[/b][/color]'
        self.total_discount.text = '[color=FF0000][b]($0.00)[/b][/color]'

        # reset cards on file ids
        vars.PROFILE_ID = None
        vars.PAYMENT_ID = None
        pro = Profile()
        profiles = pro.where({'user_id': vars.CUSTOMER_ID,
                              'company_id': vars.COMPANY_ID})
        if profiles:
            for profile in profiles:
                vars.PROFILE_ID = profile['profile_id']

            cards_db = Card()
            self.cards = cards_db.collect(vars.COMPANY_ID, vars.PROFILE_ID)
        else:
            self.cards = False
        self.select_card_location('1')

        self.discount_label.bind(on_ref_press=self.discount_popup)
        SYNC_POPUP.dismiss()

    def discount_popup(self, *args, **kwargs):
        self.main_popup.title = 'Discount Selection'
        layout = BoxLayout(orientation="vertical")
        inner_layout_1 = Factory.ScrollGrid()
        inner_layout_1.ids.main_table.cols = 7
        h1 = KV.invoice_tr(0, '#')
        h2 = KV.invoice_tr(0, 'Name')
        h3 = KV.invoice_tr(0, 'Type')
        h4 = KV.invoice_tr(0, 'Discount')
        h5 = KV.invoice_tr(0, 'Group')
        h6 = KV.invoice_tr(0, 'Start')
        h7 = KV.invoice_tr(0, 'End')
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(h1))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(h2))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(h3))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(h4))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(h5))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(h6))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(h7))
        discounts = Discount().where({'company_id': vars.COMPANY_ID,
                                      'ORDER_BY': 'discount_id desc'})
        if discounts:
            for discount in discounts:
                discount_id = discount['discount_id']
                type = 'Rate' if discount['type'] is 1 else 'Price'
                rate = discount['rate']
                price = discount['discount']
                discount_display = rate if discount['type'] is 1 else price
                start = datetime.datetime.strptime(discount['start_date'], "%Y-%m-%d %H:%M:%S") if discount[
                    'start_date'] else None
                end = datetime.datetime.strptime(discount['end_date'], "%Y-%m-%d %H:%M:%S") if discount[
                    'end_date'] else None
                start_formatted = start.strftime('%m/%d/%Y')
                end_formatted = end.strftime('%m/%d/%Y')
                inventory_id = discount['inventory_id']
                inventory_name = None
                if inventory_id:
                    inventories = Inventory().where({'inventory_id': inventory_id})

                    if inventories:
                        for inventory in inventories:
                            inventory_name = inventory['name']
                item_name = None
                inventory_item_id = discount['inventory_item_id']
                if inventory_item_id:
                    inventory_items = InventoryItem().where({'item_id': inventory_item_id})
                    if inventory_items:
                        for inventory_item in inventory_items:
                            item_name = inventory_item['name']

                group = None
                if inventory_name and item_name:
                    group = '{} - {}'.format(inventory_name, item_name)
                elif inventory_name and not item_name:
                    group = str(inventory_name)
                elif item_name and not inventory_name:
                    group = str(item_name)

                if discount_id is self.discount_id:
                    id_button = Factory.TagsSelectedButton(text=str(discount_id))
                    name_button = Factory.TagsSelectedButton(text=str(discount['name']))
                    type_button = Factory.TagsSelectedButton(text=str(type))
                    discount_button = Factory.TagsSelectedButton(text=str(discount_display))
                    group_button = Factory.TagsSelectedButton(text=str(group))
                    start_button = Factory.TagsSelectedButton(text=str(start_formatted))
                    end_button = Factory.TagsSelectedButton(text=str(end_formatted))
                else:
                    id_button = Button(text=str(discount_id),
                                       on_release=partial(self.select_discount, discount_id))

                    name_button = Button(text=str(discount['name']),
                                         on_release=partial(self.select_discount, discount_id))
                    type_button = Button(text=str(type),
                                         on_release=partial(self.select_discount, discount_id))
                    discount_button = Button(text=str(discount_display),
                                             on_release=partial(self.select_discount, discount_id))
                    group_button = Button(text=str(group),
                                          on_release=partial(self.select_discount, discount_id))
                    start_button = Button(text=str(start_formatted),
                                          on_release=partial(self.select_discount, discount_id))
                    end_button = Button(text=str(end_formatted),
                                        on_release=partial(self.select_discount, discount_id))

                inner_layout_1.ids.main_table.add_widget(id_button)
                inner_layout_1.ids.main_table.add_widget(name_button)
                inner_layout_1.ids.main_table.add_widget(type_button)
                inner_layout_1.ids.main_table.add_widget(discount_button)
                inner_layout_1.ids.main_table.add_widget(group_button)
                inner_layout_1.ids.main_table.add_widget(start_button)
                inner_layout_1.ids.main_table.add_widget(end_button)

        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="cancel",
                               on_release=self.main_popup.dismiss)

        inner_layout_2.add_widget(cancel_button)

        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.main_popup.content = layout
        self.main_popup.open()

    def select_discount(self, discount_id, *args, **kwargs):
        self.discount_id = discount_id
        self.invoice_selected(None)
        self.main_popup.dismiss()

    def invoice_create_rows(self):
        self.invoice_table.clear_widgets()
        h1 = KV.sized_invoice_tr(0, '#', size_hint_x=0.2)
        h2 = KV.sized_invoice_tr(0, 'Qty', size_hint_x=0.2)
        h3 = KV.sized_invoice_tr(0, 'Due', size_hint_x=0.2)
        h4 = KV.sized_invoice_tr(0, 'Rack', size_hint_x=0.2)
        h5 = KV.sized_invoice_tr(0, 'Subtotal', size_hint_x=0.2)
        self.invoice_table.add_widget(Builder.load_string(h1))
        self.invoice_table.add_widget(Builder.load_string(h2))
        self.invoice_table.add_widget(Builder.load_string(h3))
        self.invoice_table.add_widget(Builder.load_string(h4))
        self.invoice_table.add_widget(Builder.load_string(h5))
        invoices = Invoice()
        invoice_data = invoices.where({'customer_id': vars.CUSTOMER_ID,
                                       'status': {'<': 3}})
        if invoice_data:
            for invoice in invoice_data:
                invoice_id = invoice['invoice_id']
                quantity = 1
                try:
                    quantity = int(invoice['quantity'])
                except ValueError:
                    quantity = 1

                subtotal = vars.us_dollar(invoice['pretax'])
                tax = vars.us_dollar(invoice['tax'])
                total = vars.us_dollar(invoice['total'])
                rack = invoice['rack']
                due = invoice['due_date']
                try:
                    dt = datetime.datetime.strptime(due, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    dt = datetime.datetime.strptime('1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
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

                selected = True if invoice_id in self.selected_invoices else False

                tr_1 = KV.invoice_tr(state, invoice_id, selected=selected, invoice_id=invoice_id,
                                     callback='self.parent.parent.parent.parent.parent.parent.invoice_selected({})'.format(
                                         invoice_id))
                tr_2 = KV.invoice_tr(state, quantity, selected=selected, invoice_id=invoice_id,
                                     callback='self.parent.parent.parent.parent.parent.parent.invoice_selected({})'.format(
                                         invoice_id))
                tr_3 = KV.invoice_tr(state, due_date, selected=selected, invoice_id=invoice_id,
                                     callback='self.parent.parent.parent.parent.parent.parent.invoice_selected({})'.format(
                                         invoice_id))
                tr_4 = KV.invoice_tr(state, rack, selected=selected, invoice_id=invoice_id,
                                     callback='self.parent.parent.parent.parent.parent.parent.invoice_selected({})'.format(
                                         invoice_id))
                tr_5 = KV.invoice_tr(state, subtotal, selected=selected, invoice_id=invoice_id,
                                     callback='self.parent.parent.parent.parent.parent.parent.invoice_selected({})'.format(
                                         invoice_id))

                self.invoice_table.add_widget(Builder.load_string(tr_1))
                self.invoice_table.add_widget(Builder.load_string(tr_2))
                self.invoice_table.add_widget(Builder.load_string(tr_3))
                self.invoice_table.add_widget(Builder.load_string(tr_4))
                self.invoice_table.add_widget(Builder.load_string(tr_5))

    def set_result_status(self):
        vars.SEARCH_RESULTS_STATUS = True

    def invoice_selected(self, invoice_id, *args, **kwargs):
        if invoice_id:
            if invoice_id in self.selected_invoices:

                self.selected_invoices.remove(invoice_id)

            else:
                self.selected_invoices.append(invoice_id)

        total = 0
        quantity = 0
        subtotal = 0
        tax = 0
        self.discount_total = 0
        if self.selected_invoices:
            for invoice_id in self.selected_invoices:
                # get invoice total
                invoices = Invoice().where({'invoice_id': invoice_id})
                if invoices:
                    for invoice in invoices:
                        total += invoice['total']
                        quantity += invoice['quantity']
                        subtotal += invoice['pretax']
                        tax += invoice['tax']
                        if invoice['discount_id'] is not None:
                            self.discount_id = invoice['discount_id']

                # get discounted totals
                if self.discount_id:
                    discount_invoice_total = 0
                    discounts = Discount().where({'discount_id': self.discount_id})
                    if discounts:
                        for discount in discounts:
                            discount_type = discount['type']
                            discount_inventory_id = discount['inventory_id']
                            discount_item_id = discount['inventory_item_id']
                            if discount_inventory_id:
                                invoice_items = InvoiceItem().where({'invoice_id': invoice_id,
                                                                     'inventory_id': discount_inventory_id})
                            elif discount_item_id:
                                invoice_items = InvoiceItem().where({'invoice_id': invoice_id,
                                                                     'item_id': discount_item_id})
                            if invoice_items:
                                for invoice_item in invoice_items:
                                    discount_invoice_total += invoice_item['pretax']
                            if discount_type is 1:
                                discount_rate = discount['rate']
                                self.discount_total += float(discount_invoice_total) * float(discount_rate)
                            else:
                                self.discount_total += float('%0.2f' % discount['price'])
        self.discount_total = float('%0.2f' % self.discount_total)
        self.amount_tendered = total
        self.total_amount = total
        self.total_subtotal = subtotal
        self.total_quantity = quantity
        self.total_tax = tax
        if self.credits or self.discount_total:

            self.total_due = 0 if self.credits >= self.total_amount else float("%0.2f" % (
                self.total_amount - self.credits))
        else:
            self.total_due = float('%0.2f' % (self.total_amount))

        fix = 0 if self.total_amount <= 0 else self.total_amount
        fix_qty = 0 if self.total_quantity <= 0 else self.total_quantity
        fix_tax = 0 if self.total_tax <= 0 else self.total_tax
        fix_subtotal = 0 if self.total_subtotal <= 0 else self.total_subtotal
        fix_due = 0 if self.total_due <= 0 else self.total_due
        self.total_amount = float('%0.2f' % (fix))
        self.amount_tendered = float('%0.2f' % (fix))
        self.total_quantity = fix_qty
        self.total_subtotal = float('%0.2f' % (fix_subtotal))
        self.total_tax = float('%0.2f' % (fix_tax))
        self.total_due = float('%0.2f' % (fix_due))

        # update the subtotal label
        self.quantity_label.text = '[color=000000][b]{}[/b][/color]'.format(self.total_quantity)
        self.subtotal_label.text = '[color=000000][b]{}[/b][/color]'.format(vars.us_dollar(self.total_subtotal))
        self.tax_label.text = '[color=000000][b]{}[/b][/color]'.format(vars.us_dollar(self.total_tax))
        self.total_label.text = '[color=000000][b]{}[/b][/color]'.format(vars.us_dollar(self.total_amount))
        self.total_discount.text = '[color=FF0000][b]({})[/b][/color]'.format(vars.us_dollar(self.discount_total))

        self.due_label.text = '[color=000000][b]{}[/b][/color]'.format(vars.us_dollar(self.total_due))

        # update the calculator total
        self.calc_amount = ['{}'.format(int(self.total_due * 100))]
        self.calc_total.text = '[color=000000][b]{}[/b][/color]'.format(vars.us_dollar(self.total_due))

        # calculate change due
        self.change_due = float("%0.2f" % (self.amount_tendered - self.total_due))

        # clear table and update selected rows
        self.invoice_table.clear_widgets()
        self.invoice_create_rows()

    def calculator_amounts(self, num):
        if num == '7':
            self.calc_amount.append('7')
        elif num == '8':
            self.calc_amount.append('8')
        elif num == '9':
            self.calc_amount.append('9')
        elif num == '4':
            self.calc_amount.append('4')
        elif num == '5':
            self.calc_amount.append('5')
        elif num == '6':
            self.calc_amount.append('6')
        elif num == '1':
            self.calc_amount.append('1')
        elif num == '2':
            self.calc_amount.append('2')
        elif num == '3':
            self.calc_amount.append('3')
        elif num == '0':
            self.calc_amount.append('0')
        elif num == '00':
            self.calc_amount.append('00')
        else:
            self.calc_amount = ['0']

        total = vars.us_dollar(int(''.join(self.calc_amount)) / 100)
        self.amount_tendered = int(''.join(self.calc_amount)) / 100
        if self.payment_type == 'ca':
            self.change_due = self.amount_tendered - self.total_due
        self.calc_total.text = '[color=000000][b]{}[/b][/color]'.format(total)

    def select_payment_type(self, type):
        if type == 'cc':
            self.payment_type = 'cc'
        elif type == 'ca':
            self.payment_type = 'ca'
        elif type == 'ch':
            self.payment_type = 'ch'
        else:
            self.payment_type = 'ac'
        self.amount_tendered = self.total_due
        self.calc_total.text = '[color=000000][b]{}[/b][/color]'.format(vars.us_dollar(self.total_due))

    def select_card_location(self, loc):
        self.credit_card_data_layout.clear_widgets()
        if loc == '1':
            self.card_location = 1
            self.instore_button.state = 'down'
            self.online_button.state = 'normal'
        else:
            self.card_location = 2
            self.instore_button.state = 'normal'
            self.online_button.state = 'down'
            inner_layout_1 = BoxLayout(orientation='vertical',
                                       size_hint=(1, 1))
            card_string = []
            if self.cards:
                for card in self.cards:
                    card_string.append("{} {} {}/{}".format(card['card_type'],
                                                            card['last_four'],
                                                            card['exp_month'],
                                                            card['exp_year']))
            self.card_id_spinner = Spinner(
                # default value shown
                text='Select Card',
                # available values
                values=card_string,
                # just for positioning in our example
                size_hint_x=1,
                size_hint_y=0.5,
                pos_hint={'center_x': .5, 'center_y': .5})
            self.card_id_spinner.bind(text=self.select_online_card)
            inner_layout_1.add_widget(self.card_id_spinner)

            # make the update and add buttons and send it to screen
            credit_card_action_box = BoxLayout(orientation="horizontal",
                                               size_hint=(1, 0.5))
            credit_card_action_box.add_widget(Button(text="Update", on_release=self.update_card))
            credit_card_action_box.add_widget(Button(text="Add", on_release=self.add_card_popup))
            inner_layout_1.add_widget(credit_card_action_box)
            self.credit_card_data_layout.add_widget(inner_layout_1)

    def select_online_card(self, *args, **kwargs):
        card_string = self.card_id_spinner.text
        if self.cards:
            for card in self.cards:
                check_string = "{} {} {}/{}".format(card['card_type'],
                                                    card['last_four'],
                                                    card['exp_month'],
                                                    card['exp_year'])
                if check_string == card_string:
                    self.card_id = card['card_id']
                    print(self.card_id)
        pass

    def update_card(self, *args, **kwargs):
        self.finish_popup.title = 'Update Credit Card'
        if self.card_id is None:
            popup = Popup()
            popup.title = 'Card Error'
            content = KV.popup_alert('Credit Card Not Selected. Please select card and try again.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()
        else:

            if self.cards:
                for card in self.cards:
                    if self.card_id == card['card_id']:
                        # setup card form
                        edit_card_label = Factory.CenteredFormLabel(text="Card #")
                        self.edit_card_number = Factory.CenterVerticalTextInput(hint_text=card['last_four'])
                        edit_card_exp_month_label = Factory.CenteredFormLabel(text="Exp Month")
                        self.edit_card_exp_month = Factory.CenterVerticalTextInput(text=card['exp_month'])
                        edit_card_exp_year_label = Factory.CenteredFormLabel(text="Exp Year")
                        self.edit_card_exp_year = Factory.CenterVerticalTextInput(text=card['exp_year'])
                        edit_card_billing_street_label = Factory.CenteredFormLabel(text="Street")
                        self.edit_card_billing_street = Factory.CenterVerticalTextInput(text=card['street'])
                        edit_card_billing_suite_label = Factory.CenteredFormLabel(text="Suite")
                        self.edit_card_billing_suite = Factory.CenterVerticalTextInput(text=card['suite'])
                        edit_card_billing_city_label = Factory.CenteredFormLabel(text="City")
                        self.edit_card_billing_city = Factory.CenterVerticalTextInput(text=card['city'])
                        edit_card_billing_state_label = Factory.CenteredFormLabel(text="State")
                        self.edit_card_billing_state = Factory.CenterVerticalTextInput(text=card['state'])
                        edit_card_billing_zipcode_label = Factory.CenteredFormLabel(text="Zipcode")
                        self.edit_card_billing_zipcode = Factory.CenterVerticalTextInput(text=card['zipcode'])
                        edit_card_billing_first_name_label = Factory.CenteredFormLabel(text="First Name")
                        self.edit_card_billing_first_name = Factory.CenterVerticalTextInput(text=card['first_name'])
                        edit_card_billing_last_name_label = Factory.CenteredFormLabel(text="Last Name")
                        self.edit_card_billing_last_name = Factory.CenterVerticalTextInput(text=card['last_name'])
                        base_layout = BoxLayout(orientation='vertical',
                                                size_hint=(1, 1))
                        inner_layout_1 = GridLayout(size_hint=(1, 0.9),
                                                    cols=2,
                                                    rows=10)
                        inner_layout_1.add_widget(edit_card_label)
                        inner_layout_1.add_widget(self.edit_card_number)
                        inner_layout_1.add_widget(edit_card_exp_month_label)
                        inner_layout_1.add_widget(self.edit_card_exp_month)
                        inner_layout_1.add_widget(edit_card_exp_year_label)
                        inner_layout_1.add_widget(self.edit_card_exp_year)
                        inner_layout_1.add_widget(edit_card_billing_first_name_label)
                        inner_layout_1.add_widget(self.edit_card_billing_first_name)
                        inner_layout_1.add_widget(edit_card_billing_last_name_label)
                        inner_layout_1.add_widget(self.edit_card_billing_last_name)
                        inner_layout_1.add_widget(edit_card_billing_street_label)
                        inner_layout_1.add_widget(self.edit_card_billing_street)
                        inner_layout_1.add_widget(edit_card_billing_suite_label)
                        inner_layout_1.add_widget(self.edit_card_billing_suite)
                        inner_layout_1.add_widget(edit_card_billing_city_label)
                        inner_layout_1.add_widget(self.edit_card_billing_city)
                        inner_layout_1.add_widget(edit_card_billing_state_label)
                        inner_layout_1.add_widget(self.edit_card_billing_state)
                        inner_layout_1.add_widget(edit_card_billing_zipcode_label)
                        inner_layout_1.add_widget(self.edit_card_billing_zipcode)

                        inner_layout_2 = BoxLayout(orientation='horizontal',
                                                   size_hint=(1, 0.1))
                        cancel_button = Button(text="cancel",
                                               on_release=self.finish_popup.dismiss)
                        save_button = Button(text="save",
                                             on_release=self.edit_card)
                        inner_layout_2.add_widget(cancel_button)
                        inner_layout_2.add_widget(save_button)
                        base_layout.add_widget(inner_layout_1)
                        base_layout.add_widget(inner_layout_2)
                        self.finish_popup.content = base_layout
                        self.finish_popup.open()
            else:
                popup = Popup()
                popup.title = 'Card Error'
                content = KV.popup_alert(
                    'Card selected but could not locate card in local db. Please add a new card instead')
                popup.content = Builder.load_string(content)
                popup.open()
                # Beep Sound
                sys.stdout.write('\a')
                sys.stdout.flush()

        pass

    def edit_card(self, *args, **kwargs):
        # validate
        errors = 0
        if not self.edit_card_number.text:
            errors += 1
            self.edit_card_number.text_color = ERROR_COLOR
            self.edit_card_number.hint_text = 'Must enter card number'
        else:
            self.edit_card_number.text_color = DEFAULT_COLOR
            self.edit_card_number.hint_text = ""

        if not self.edit_card_exp_month.text:
            errors += 1
            self.edit_card_exp_month.text_color = ERROR_COLOR
            self.edit_card_exp_month.hint_text = 'Must enter expired month'
        else:
            self.edit_card_exp_month.text_color = DEFAULT_COLOR
            self.edit_card_exp_month.hint_text = ""

        if not self.edit_card_exp_year.text:
            errors += 1
            self.edit_card_exp_year.text_color = ERROR_COLOR
            self.edit_card_exp_year.hint_text = 'Must enter expired year'
        else:
            self.edit_card_exp_year.text_color = DEFAULT_COLOR
            self.edit_card_exp_year.hint_text = ""

        if not self.edit_card_billing_first_name.text:
            errors += 1
            self.edit_card_billing_first_name.text_color = ERROR_COLOR
            self.edit_card_billing_first_name.hint_text = 'Must enter first name'
        else:
            self.edit_card_billing_first_name.text_color = DEFAULT_COLOR
            self.edit_card_billing_first_name.hint_text = ""

        if not self.edit_card_billing_last_name.text:
            errors += 1
            self.edit_card_billing_last_name.text_color = ERROR_COLOR
            self.edit_card_billing_last_name.hint_text = 'Must enter last name'
        else:
            self.edit_card_billing_last_name.text_color = DEFAULT_COLOR
            self.edit_card_billing_last_name.hint_text = ""

        if not self.edit_card_billing_street.text:
            errors += 1
            self.edit_card_billing_street.text_color = ERROR_COLOR
            self.edit_card_billing_street.hint_text = 'Must enter street address'
        else:
            self.edit_card_billing_street.text_color = DEFAULT_COLOR
            self.edit_card_billing_street.hint_text = ""

        if not self.edit_card_billing_city.text:
            errors += 1
            self.edit_card_billing_city.text_color = ERROR_COLOR
            self.edit_card_billing_city.hint_text = 'Must enter city'
        else:
            self.edit_card_billing_city.text_color = DEFAULT_COLOR
            self.edit_card_billing_city.hint_text = ""

        if not self.edit_card_billing_state.text:
            errors += 1
            self.edit_card_billing_state.text_color = ERROR_COLOR
            self.edit_card_billing_state.hint_text = 'Must enter state'
        else:
            self.edit_card_billing_state.text_color = DEFAULT_COLOR
            self.edit_card_billing_state.hint_text = ""

        if not self.edit_card_billing_zipcode.text:
            errors += 1
            self.edit_card_billing_zipcode.text_color = ERROR_COLOR
            self.edit_card_billing_zipcode.hint_text = 'Must enter zipcode'
        else:
            self.edit_card_billing_zipcode.text_color = DEFAULT_COLOR
            self.edit_card_billing_zipcode.hint_text = ""

        if errors == 0:
            # prepare for saving into db

            cards = Card()
            get_original_card = cards.where({'card_id': self.card_id})

            if get_original_card:
                for card in get_original_card:
                    root_payment_id = card['root_payment_id']
            get_root_payment = cards.where({'root_payment_id': root_payment_id})
            if get_root_payment:

                for grp in get_root_payment:
                    self.run_edit_task(grp)

            # save to server
            run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
            try:
                run_sync.start()
            finally:
                run_sync.join()
                print('sync now finished')
            # finish and reset
            popup = Popup()
            popup.title = 'Card Update Successful'
            content = KV.popup_alert(
                'Successfully updated card. Please reselect your card and invoices before making the online payment.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()
            self.finish_popup.dismiss()
            self.reset()
            self.select_card_location('1')

        pass

    def run_edit_task(self, grp):
        save_data = {
            'customer_type': 'individual',
            'card_number': str(self.edit_card_number.text.rstrip()),
            'expiration_month': str(self.edit_card_exp_month.text.rstrip()),
            'expiration_year': str(self.edit_card_exp_year.text.rstrip()),
            'billing': {
                'first_name': str(self.edit_card_billing_first_name.text),
                'last_name': str(self.edit_card_billing_last_name.text),
                'company': '',
                'address': str(self.edit_card_billing_street.text),
                'city': str(self.edit_card_billing_city.text),
                'state': str(self.edit_card_billing_state.text),
                'zip': str(self.edit_card_billing_zipcode.text),
                'country': 'US'
            },
        }
        suite = self.edit_card_billing_suite.text if self.edit_card_billing_suite.text else ''
        result = Card().card_update(grp['company_id'], grp['profile_id'], grp['payment_id'], save_data)
        Card().put(where={'card_id': grp['card_id']},
                   data={
                       'street': self.edit_card_billing_street.text,
                       'suite': suite,
                       'city': self.edit_card_billing_city.text,
                       'state': self.edit_card_billing_state.text,
                       'exp_month': self.edit_card_exp_month.text,
                       'exp_year': self.edit_card_exp_year.text
                   })

    def add_card_popup(self, *args, **kwargs):
        self.finish_popup.title = 'Add Credit Card'
        # setup card form
        edit_card_label = Factory.CenteredFormLabel(text="Card #")
        self.edit_card_number = Factory.CenterVerticalTextInput(hint_text="XXXXXXXXXXXXXXXX")
        edit_card_exp_month_label = Factory.CenteredFormLabel(text="Exp Month")
        self.edit_card_exp_month = Factory.CenterVerticalTextInput(hint_text="XX")
        edit_card_exp_year_label = Factory.CenteredFormLabel(text="Exp Year")
        self.edit_card_exp_year = Factory.CenterVerticalTextInput(hint_text="XXXX")
        edit_card_billing_street_label = Factory.CenteredFormLabel(text="Street")
        self.edit_card_billing_street = Factory.CenterVerticalTextInput()
        edit_card_billing_suite_label = Factory.CenteredFormLabel(text="Suite")
        self.edit_card_billing_suite = Factory.CenterVerticalTextInput()
        edit_card_billing_city_label = Factory.CenteredFormLabel(text="City")
        self.edit_card_billing_city = Factory.CenterVerticalTextInput()
        edit_card_billing_state_label = Factory.CenteredFormLabel(text="State")
        self.edit_card_billing_state = Factory.CenterVerticalTextInput()
        edit_card_billing_zipcode_label = Factory.CenteredFormLabel(text="Zipcode")
        self.edit_card_billing_zipcode = Factory.CenterVerticalTextInput()
        edit_card_billing_first_name_label = Factory.CenteredFormLabel(text="First Name")
        self.edit_card_billing_first_name = Factory.CenterVerticalTextInput()
        edit_card_billing_last_name_label = Factory.CenteredFormLabel(text="Last Name")
        self.edit_card_billing_last_name = Factory.CenterVerticalTextInput()
        base_layout = BoxLayout(orientation='vertical',
                                size_hint=(1, 1))
        inner_layout_1 = GridLayout(size_hint=(1, 0.9),
                                    cols=2,
                                    rows=10)
        inner_layout_1.add_widget(edit_card_label)
        inner_layout_1.add_widget(self.edit_card_number)
        inner_layout_1.add_widget(edit_card_exp_month_label)
        inner_layout_1.add_widget(self.edit_card_exp_month)
        inner_layout_1.add_widget(edit_card_exp_year_label)
        inner_layout_1.add_widget(self.edit_card_exp_year)
        inner_layout_1.add_widget(edit_card_billing_first_name_label)
        inner_layout_1.add_widget(self.edit_card_billing_first_name)
        inner_layout_1.add_widget(edit_card_billing_last_name_label)
        inner_layout_1.add_widget(self.edit_card_billing_last_name)
        inner_layout_1.add_widget(edit_card_billing_street_label)
        inner_layout_1.add_widget(self.edit_card_billing_street)
        inner_layout_1.add_widget(edit_card_billing_suite_label)
        inner_layout_1.add_widget(self.edit_card_billing_suite)
        inner_layout_1.add_widget(edit_card_billing_city_label)
        inner_layout_1.add_widget(self.edit_card_billing_city)
        inner_layout_1.add_widget(edit_card_billing_state_label)
        inner_layout_1.add_widget(self.edit_card_billing_state)
        inner_layout_1.add_widget(edit_card_billing_zipcode_label)
        inner_layout_1.add_widget(self.edit_card_billing_zipcode)

        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="cancel",
                               on_release=self.finish_popup.dismiss)
        save_button = Button(text="save",
                             on_release=self.add_card)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(save_button)
        base_layout.add_widget(inner_layout_1)
        base_layout.add_widget(inner_layout_2)
        self.finish_popup.content = base_layout
        self.finish_popup.open()
        pass

    def add_card(self, *args, **kwargs):
        # validate
        errors = 0
        if not self.edit_card_number.text:
            errors += 1
            self.edit_card_number.text_color = ERROR_COLOR
            self.edit_card_number.hint_text = 'Must enter card number'
        else:
            self.edit_card_number.text_color = DEFAULT_COLOR
            self.edit_card_number.hint_text = ""

        if not self.edit_card_exp_month.text:
            errors += 1
            self.edit_card_exp_month.text_color = ERROR_COLOR
            self.edit_card_exp_month.hint_text = 'Must enter expired month'
        else:
            self.edit_card_exp_month.text_color = DEFAULT_COLOR
            self.edit_card_exp_month.hint_text = ""

        if not self.edit_card_exp_year.text:
            errors += 1
            self.edit_card_exp_year.text_color = ERROR_COLOR
            self.edit_card_exp_year.hint_text = 'Must enter expired year'
        else:
            self.edit_card_exp_year.text_color = DEFAULT_COLOR
            self.edit_card_exp_year.hint_text = ""

        if not self.edit_card_billing_first_name.text:
            errors += 1
            self.edit_card_billing_first_name.text_color = ERROR_COLOR
            self.edit_card_billing_first_name.hint_text = 'Must enter first name'
        else:
            self.edit_card_billing_first_name.text_color = DEFAULT_COLOR
            self.edit_card_billing_first_name.hint_text = ""

        if not self.edit_card_billing_last_name.text:
            errors += 1
            self.edit_card_billing_last_name.text_color = ERROR_COLOR
            self.edit_card_billing_last_name.hint_text = 'Must enter last name'
        else:
            self.edit_card_billing_last_name.text_color = DEFAULT_COLOR
            self.edit_card_billing_last_name.hint_text = ""

        if not self.edit_card_billing_street.text:
            errors += 1
            self.edit_card_billing_street.text_color = ERROR_COLOR
            self.edit_card_billing_street.hint_text = 'Must enter street address'
        else:
            self.edit_card_billing_street.text_color = DEFAULT_COLOR
            self.edit_card_billing_street.hint_text = ""

        if not self.edit_card_billing_city.text:
            errors += 1
            self.edit_card_billing_city.text_color = ERROR_COLOR
            self.edit_card_billing_city.hint_text = 'Must enter city'
        else:
            self.edit_card_billing_city.text_color = DEFAULT_COLOR
            self.edit_card_billing_city.hint_text = ""

        if not self.edit_card_billing_state.text:
            errors += 1
            self.edit_card_billing_state.text_color = ERROR_COLOR
            self.edit_card_billing_state.hint_text = 'Must enter state'
        else:
            self.edit_card_billing_state.text_color = DEFAULT_COLOR
            self.edit_card_billing_state.hint_text = ""

        if not self.edit_card_billing_zipcode.text:
            errors += 1
            self.edit_card_billing_zipcode.text_color = ERROR_COLOR
            self.edit_card_billing_zipcode.hint_text = 'Must enter zipcode'
        else:
            self.edit_card_billing_zipcode.text_color = DEFAULT_COLOR
            self.edit_card_billing_zipcode.hint_text = ""

        if errors == 0:
            # loop through each company and save
            companies = Company().where({'id': {'>': 0}})
            save_success = 0
            if companies:
                for company in companies:
                    company_id = company['id']
                    cards = Card()
                    cards.company_id = company_id
                    cards.user_id = vars.CUSTOMER_ID
                    # search for a profile
                    profiles = Profile().where({'company_id': company_id, 'user_id': vars.CUSTOMER_ID})
                    profile_id = False
                    if profiles:
                        for profile in profiles:
                            profile_id = profile['profile_id']
                        cards.profile_id = profile_id
                        # make just payment_id
                        new_card = {
                            'customer_type': 'individual',
                            'card_number': str(self.edit_card_number.text.rstrip()),
                            'expiration_month': str(self.edit_card_exp_month.text.rstrip()),
                            'expiration_year': str(self.edit_card_exp_year.text.rstrip()),
                            'billing': {
                                'first_name': str(self.edit_card_billing_first_name.text),
                                'last_name': str(self.edit_card_billing_last_name.text),
                                'company': '',
                                'address': str(self.edit_card_billing_street.text),
                                'city': str(self.edit_card_billing_city.text),
                                'state': str(self.edit_card_billing_state.text),
                                'zip': str(self.edit_card_billing_zipcode.text),
                                'country': 'USA'
                            }
                        }
                        result = Card().create_card(company_id, profile_id, new_card)
                        if 'status' in result:
                            save_success += 1
                            payment_id = result['payment_id']

                            cards.payment_id = payment_id
                            if company_id is 1:
                                self.root_payment_id = payment_id
                            cards.root_payment_id = self.root_payment_id
                            cards.street = self.edit_card_billing_street.text
                            cards.suite = self.edit_card_billing_suite.text
                            cards.city = self.edit_card_billing_city.text
                            cards.state = self.edit_card_billing_state.text
                            cards.zipcode = self.edit_card_billing_zipcode.text
                            cards.exp_month = self.edit_card_exp_month.text
                            cards.exp_year = self.edit_card_exp_year.text
                            cards.status = 1
                            cards.add()
                        else:
                            popup = Popup()
                            popup.title = 'Card Error'
                            content = KV.popup_alert(result['message'])
                            popup.content = Builder.load_string(content)
                            popup.open()
                            # Beep Sound
                            sys.stdout.write('\a')
                            sys.stdout.flush()
                    else:
                        # make profile_id and payment_id
                        customers = User().where({'user_id': vars.CUSTOMER_ID})
                        if customers:
                            for customer in customers:
                                first_name = customer['first_name']
                                last_name = customer['last_name']
                        new_data = {
                            'merchant_id': str(vars.CUSTOMER_ID),
                            'description': '{}, {}'.format(last_name, first_name),
                            'customer_type': 'individual',
                            'billing': {
                                'first_name': str(self.edit_card_billing_first_name.text),
                                'last_name': str(self.edit_card_billing_last_name.text),
                                'company': '',
                                'address': '{}'.format(self.edit_card_billing_street.text),
                                'city': str(self.edit_card_billing_city.text),
                                'state': str(self.edit_card_billing_state.text),
                                'zip': str(self.edit_card_billing_zipcode.text),
                                'country': 'USA'
                            },
                            'credit_card': {
                                'card_number': str(self.edit_card_number.text.rstrip()),
                                'card_code': '',
                                'expiration_month': str(self.edit_card_exp_month.text.rstrip()),
                                'expiration_year': str(self.edit_card_exp_year.text.rstrip()),
                            }
                        }
                        make_profile = Card().create_profile(company_id, new_data)

                        if 'status' in make_profile:
                            save_success += 1
                            profile_id = make_profile['profile_id']
                            payment_id = make_profile['payment_id']
                            new_profiles = Profile()
                            new_profiles.company_id = company_id
                            new_profiles.user_id = vars.CUSTOMER_ID
                            new_profiles.profile_id = profile_id
                            new_profiles.status = 1
                            new_profiles.add()

                            cards.profile_id = profile_id
                            cards.payment_id = payment_id
                            cards.street = self.edit_card_billing_street.text
                            cards.suite = self.edit_card_billing_suite.text
                            cards.city = self.edit_card_billing_city.text
                            cards.state = self.edit_card_billing_state.text
                            cards.zipcode = self.edit_card_billing_zipcode.text
                            cards.exp_month = self.edit_card_exp_month.text
                            cards.exp_year = self.edit_card_exp_year.text
                            if company_id is 1:
                                self.root_payment_id = payment_id
                            cards.root_payment_id = self.root_payment_id
                            cards.status = 1
                            cards.add()

                        else:
                            popup = Popup()
                            popup.title = 'Add Card Error'
                            content = KV.popup_alert(make_profile['message'])
                            popup.content = Builder.load_string(content)
                            popup.open()
                            # Beep Sound
                            sys.stdout.write('\a')
                            sys.stdout.flush()
            if save_success > 0:
                # finish and reset
                popup = Popup()
                popup.title = 'Card Add Successful'
                content = KV.popup_alert('Successfully added a card.')
                popup.content = Builder.load_string(content)
                popup.open()
                # Beep Sound
                sys.stdout.write('\a')
                sys.stdout.flush()
                self.send_to_db()
                self.finish_popup.dismiss()
                self.reset()
                self.select_card_location('1')
            else:
                popup = Popup()
                popup.title = 'Card Add Unsuccessful'
                content = KV.popup_alert('There were problems saving your card. Please try again')
                popup.content = Builder.load_string(content)
                popup.open()

        pass

    def send_to_db(self):
        # save to server
        vars.WORKLIST.append("Sync")
        threads_start()

    def cash_tendered(self, amount):
        if len(self.selected_invoices) > 0:
            total = vars.us_dollar(int(''.join(amount)))
            self.amount_tendered = int(''.join(amount))
            self.change_due = float("%0.2f" % (self.amount_tendered - self.total_due))
            self.calc_total.text = '[color=000000][b]{}[/b][/color]'.format(total)
        else:
            # finish and reset
            popup = Popup()
            popup.title = 'Transaction Error'
            content = KV.popup_alert(
                'Please select an invoice before processing.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()

    def pay_popup_create(self):

        self.finish_popup.title = 'Finish Payment'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.9))
        button_1 = Factory.PrintButton(text='Finish + Receipt',
                                       on_release=partial(self.finish_transaction, 1),
                                       on_press=self.please_wait)
        button_2 = Factory.PrintButton(text='Finish + No Receipt',
                                       on_release=partial(self.finish_transaction, 2),
                                       on_press=self.please_wait)
        if self.payment_type == 'cc':
            self.amount_tendered = self.total_amount
            if self.card_location == 1:
                inner_layout_1.add_widget(button_1)
                inner_layout_1.add_widget(button_2)
            else:
                validate_layout = BoxLayout(orientation='vertical')
                validate_inner_layout_1 = BoxLayout(orientation="horizontal",
                                                    size_hint=(1, 0.8))
                self.card_box = Factory.ValidateBox()
                self.card_box.ids.validate_button.bind(on_release=self.validate_card)
                # get card information
                if self.cards:
                    for card in self.cards:
                        if self.card_id == card['card_id']:
                            card_first_name = card['first_name']
                            card_last_name = card['last_name']
                            card_street = card['street']
                            card_suite = card['suite']
                            card_city = card['city']
                            card_state = card['state']
                            card_zipcode = card['zipcode']
                            card_last_four = card['last_four']
                            card_type = card['card_type']
                            card_exp_month = card['exp_month']
                            card_exp_year = card['exp_year']
                            if card_suite:
                                card_billing_address = '[color=000000]{} {} {},{} {}[/color]'.format(card_street,
                                                                                                     card_suite,
                                                                                                     card_city,
                                                                                                     card_state,
                                                                                                     card_zipcode)
                            else:
                                card_billing_address = '[color=000000]{} {},{} {}[/color]'.format(card_street,
                                                                                                  card_city,
                                                                                                  card_state,
                                                                                                  card_zipcode)
                            self.card_box.ids.credit_card_number.text = '[color=000000]{}[/color]'.format(
                                card_last_four)
                            self.card_box.ids.credit_card_type.text = '[color]{}[/color]'.format(card_type)
                            self.card_box.ids.credit_card_full_name.text = '[color="000000"]{} {}[/color]'.format(
                                card_first_name,
                                card_last_name)
                            self.card_box.ids.credit_card_exp_date.text = '[color="000000"]{}/{}[/color]'.format(
                                card_exp_month,
                                card_exp_year)
                            self.card_box.ids.credit_billing_address.text = card_billing_address

                validate_inner_layout_1.add_widget(self.card_box)
                validate_inner_layout_2 = BoxLayout(orientation='horizontal',
                                                    size_hint=(1, 0.2))
                validate_inner_layout_2.add_widget(button_1)
                validate_inner_layout_2.add_widget(button_2)
                validate_layout.add_widget(validate_inner_layout_1)
                validate_layout.add_widget(validate_inner_layout_2)
                inner_layout_1.add_widget(validate_layout)

        elif self.payment_type == 'ca':
            cash_layout = BoxLayout(orientation='vertical')
            cash_inner_layout_1 = GridLayout(cols=2,
                                             rows=1,
                                             size_hint=(1, 0.1))
            cash_inner_layout_1.add_widget(Label(text='change due: '))
            # results from validation
            if self.change_due > 0:
                change_due_text = '[color=0AAC00][b]{}[/b][/color]'.format(vars.us_dollar(self.change_due))
            elif self.change_due == 0:
                change_due_text = '[b]$0.00[/b]'
            elif self.change_due < 0:
                change_due_text = '[color=FF0000][b][i]Remaining Due: {}[/i][/b][/color]'.format(
                    vars.us_dollar(self.change_due))
            cash_change = Factory.CenteredLabel(markup=True,
                                                text=change_due_text)
            cash_inner_layout_1.add_widget(cash_change)
            cash_inner_layout_2 = BoxLayout(orientation='horizontal',
                                            size_hint=(1, 0.9))
            cash_inner_layout_2.add_widget(button_1)
            cash_inner_layout_2.add_widget(button_2)
            cash_layout.add_widget(cash_inner_layout_1)
            cash_layout.add_widget(cash_inner_layout_2)
            inner_layout_1.add_widget(cash_layout)
            pass
        elif self.payment_type == 'ch':
            self.amount_tendered = self.total_amount
            inner_layout_1.add_widget(button_1)
            inner_layout_1.add_widget(button_2)
        else:
            inner_layout_1.add_widget(button_1)
            inner_layout_1.add_widget(button_2)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(markup=True,
                                         font_size='20sp',
                                         text='[color=FF0000]Cancel[/color]',
                                         on_release=self.finish_popup.dismiss))

        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.finish_popup.content = layout
        self.finish_popup.open()

    def validate_card(self, *args, **kwargs):
        if self.cards:
            for card in self.cards:
                if self.card_id == card['card_id']:
                    profile_id = card['profile_id']
                    payment_id = card['payment_id']
                    result = Card().validate_card(vars.COMPANY_ID, profile_id, payment_id)
                    self.card_box.ids.card_status.text = "Passed" if result['status'] else "Failed"
                    self.card_box.ids.card_message.text = result['message']
        else:
            self.card_box.ids.card_status.text = "Failed"
            self.card_box.ids.card_message = "Could not locate card on file. Please try again."

        pass

    def please_wait(self, *args, **kwargs):
        self.status_popup.title = 'System Message'
        content = KV.popup_alert('Syncing data to server please wait...')
        self.status_popup.content = Builder.load_string(content)
        self.status_popup.open()

    def finish_transaction(self, print, *args, **kwargs):

        transaction = Transaction()
        transaction.company_id = vars.COMPANY_ID
        transaction.customer_id = vars.CUSTOMER_ID
        transaction.schedule_id = None
        transaction.pretax = self.total_subtotal
        transaction.tax = self.total_tax
        transaction.aftertax = self.total_amount
        transaction.discount = self.discount_total

        last_four = None
        if self.payment_type == 'cc' and self.card_location == 1:
            type = 1
        elif self.payment_type == 'cc' and self.card_location == 2:
            type = 2
        elif self.payment_type == 'ca':
            type = 3
        elif self.payment_type == 'ch':
            type = 4
            last_four = self.check_number.text
        else:
            type = 5

        transaction.type = type
        transaction.last_four = last_four
        transaction.tendered = self.amount_tendered
        if self.credits:
            credits_spent = self.total_amount if (self.credits - self.total_amount) >= 0 else self.credits
            self.credits_spent = credits_spent
            transaction.credit = credits_spent
        else:
            credits_spent = 0
            transaction.credit = 0
        transaction.total = self.total_due

        # check to see if account status 3 exists else create a new one
        check_account = Transaction()
        checks = check_account.where({'status': 3,
                                      'customer_id': vars.CUSTOMER_ID})
        standard_save = False
        if type is 5 and len(checks) > 0:
            transaction_id = None
            for ca in checks:
                transaction_id = ca['transaction_id']
                old_subtotal = ca['pretax']
                old_tax = ca['tax']
                old_aftertax = ca['aftertax']
                old_credit = ca['credit']
                old_discount = ca['discount']
                old_total = ca['total']
                new_subtotal = old_subtotal + self.total_subtotal
                new_tax = old_tax + self.total_tax
                new_aftertax = old_aftertax + self.total_amount
                new_credits = old_credit + credits_spent
                new_discount = old_discount + self.discount_total
                new_total = old_total + self.total_due
                check_account.put(where={'customer_id': vars.CUSTOMER_ID, 'status': 3}, data={'pretax': new_subtotal,
                                                                                              'tax': new_tax,
                                                                                              'aftertax': new_aftertax,
                                                                                              'credit': new_credits,
                                                                                              'discount': new_discount,
                                                                                              'total': new_total})
            # update any credited amount

            old_credits = 0
            customers = User()
            custs = customers.where({'user_id': vars.CUSTOMER_ID})
            if custs:
                for customer in custs:
                    old_credits = customer['credits'] if customer['credits'] is not None else 0
                    old_account_total = customer['account_total']
            new_credits = float("%0.2f" % (old_credits - credits_spent))
            new_account_total = float("%0.2f" % (old_account_total + self.total_due))
            customers.put(where={'user_id': vars.CUSTOMER_ID}, data={'credits': new_credits,
                                                                     'account_total': new_account_total})

            run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
            try:
                run_sync.start()
            finally:
                run_sync.join()
                time.sleep(3)

                # save transaction_id to Transaction and each invoice
                if self.selected_invoices:
                    invoices = Invoice()
                    for invoice_id in self.selected_invoices:
                        invoices.put(where={'invoice_id': invoice_id},
                                     data={'status': 5, 'transaction_id': transaction_id})
                    run_sync_2 = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
                    time.sleep(1)
                    try:
                        run_sync_2.start()
                    finally:
                        run_sync_2.join()
                        self.set_result_status()
                        self.finish_popup.dismiss()

        elif type is 5 and len(checks) is 0:
            transaction.status = 3
            standard_save = True
            customers = User()
            custs = customers.where({'user_id': vars.CUSTOMER_ID})
            if custs:
                for customer in custs:
                    old_account_total = customer['account_total'] if customer['account_total'] else 0
            new_account_total = float("%0.2f" % (float(old_account_total) + float(self.total_due)))
            customers.put(where={'user_id': vars.CUSTOMER_ID}, data={'account_total': new_account_total})
        else:
            transaction.status = 1
            standard_save = True

        if standard_save:
            if transaction.add():
                # update any discounts or credits
                if self.credits:
                    old_credits = 0
                    customers = User()
                    custs = customers.where({'user_id': vars.CUSTOMER_ID})
                    if custs:
                        for customer in custs:
                            old_credits = customer['credits']
                    new_credits = float("%0.2f" % (old_credits - credits_spent))
                    customers.put(where={'user_id': vars.CUSTOMER_ID}, data={'credits': new_credits})

                # update to server
                run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])

                try:
                    run_sync.start()

                finally:
                    run_sync.join()
                    # last transaction _id
                    time.sleep(3)
                    transaction_id = 0
                    last_transaction = transaction.where({'id': {'>': 0}, 'ORDER_BY': 'id desc', 'LIMIT': 1})
                    if last_transaction:
                        for trans in last_transaction:
                            transaction_id = trans['trans_id']
                    if transaction_id > 0:

                        # save transaction_id to Transaction and each invoice
                        if self.selected_invoices:
                            invoices = Invoice()
                            for invoice_id in self.selected_invoices:
                                invoices.put(where={'invoice_id': invoice_id},
                                             data={'status': 5, 'transaction_id': int(transaction_id)})
                            time.sleep(1)
                            run_sync_2 = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
                            try:
                                run_sync_2.start()
                            finally:
                                run_sync_2.join()
                                self.set_result_status()
                                self.finish_popup.dismiss()

        if print == 1:  # customer copy of invoice and finish
            if vars.EPSON:
                pr = Printer()
                companies = Company()
                comps = companies.where({'company_id': vars.COMPANY_ID}, set=True)

                if comps:
                    for company in comps:
                        companies.id = company['id']
                        companies.company_id = company['company_id']
                        companies.name = company['name']
                        companies.street = company['street']
                        companies.suite = company['suite']
                        companies.city = company['city']
                        companies.state = company['state']
                        companies.zip = company['zip']
                        companies.email = company['email']
                        companies.phone = company['phone']
                customers = User()
                custs = customers.where({'user_id': vars.CUSTOMER_ID}, set=True)
                if custs:
                    for user in custs:
                        customers.id = user['id']
                        customers.user_id = user['user_id']
                        customers.company_id = user['company_id']
                        customers.username = user['username']
                        customers.first_name = user['first_name'].upper() if user['first_name'] else ''
                        customers.last_name = user['last_name']
                        customers.street = user['street']
                        customers.suite = user['suite']
                        customers.city = user['city']
                        customers.state = user['state']
                        customers.zipcode = user['zipcode']
                        customers.email = user['email']
                        customers.phone = user['phone']
                        customers.intercom = user['intercom']
                        customers.concierge_name = user['concierge_name']
                        customers.concierge_number = user['concierge_number']
                        customers.special_instructions = user['special_instructions']
                        customers.shirt_old = user['shirt_old']
                        customers.shirt = user['shirt']
                        customers.delivery = user['delivery']
                        customers.profile_id = user['profile_id']
                        customers.payment_status = user['payment_status']
                        customers.payment_id = user['payment_id']
                        customers.token = user['token']
                        customers.api_token = user['api_token']
                        customers.reward_status = user['reward_status']
                        customers.reward_points = user['reward_points']
                        customers.account = user['account']
                        customers.starch = user['starch']
                        customers.important_memo = user['important_memo']
                        customers.invoice_memo = user['invoice_memo']
                        customers.password = user['password']
                        customers.role_id = user['role_id']
                        customers.remember_token = user['remember_token']
                if self.selected_invoices:
                    # invoices = Invoice()
                    print_sync_invoice = {}

                    for invoice_id in self.selected_invoices:
                        print_sync_invoice[invoice_id] = {}
                        invoice_items = InvoiceItem()
                        inv_items = invoice_items.where({'invoice_id': invoice_id})
                        colors = {}

                        if inv_items:
                            for invoice_item in inv_items:
                                item_id = invoice_item['item_id']
                                colors[item_id] = {}
                            for invoice_item in inv_items:
                                item_id = invoice_item['item_id']
                                items = InventoryItem().where({'item_id': item_id})
                                if items:
                                    for item in items:
                                        item_name = item['name']
                                        inventory_id = item['inventory_id']
                                else:
                                    item_name = None
                                    inventory_id = None

                                inventories = Inventory()
                                invs = inventories.where({'inventory_id': inventory_id})
                                if invs:
                                    if invs:
                                        for inventory in invs:
                                            inventory_init = inventory['name'][:1].capitalize()
                                            laundry = inventory['laundry']
                                    else:
                                        inventory_init = ''
                                        laundry = 0

                                display_name = '{} ({})'.format(item_name, vars.get_starch_by_code(
                                    customers.starch)) if laundry else item_name

                                item_color = invoice_item['color']
                                if item_id in colors:
                                    if item_color in colors[item_id]:
                                        colors[item_id][item_color] += 1
                                    else:
                                        colors[item_id][item_color] = 1
                                item_memo = invoice_item['memo']
                                item_subtotal = invoice_item['pretax']
                                if invoice_id in print_sync_invoice:
                                    if item_id in print_sync_invoice[invoice_id]:
                                        print_sync_invoice[invoice_id][item_id]['item_price'] += item_subtotal
                                        print_sync_invoice[invoice_id][item_id]['qty'] += 1
                                        if item_memo:
                                            print_sync_invoice[invoice_id][item_id]['memos'].append(item_memo)
                                        if item_id in colors:
                                            print_sync_invoice[invoice_id][item_id]['colors'] = colors[item_id]
                                        else:
                                            print_sync_invoice[invoice_id][item_id]['colors'] = []
                                    else:
                                        print_sync_invoice[invoice_id][item_id] = {
                                            'item_id': item_id,
                                            'type': inventory_init,
                                            'name': display_name,
                                            'item_price': item_subtotal,
                                            'qty': 1,
                                            'memos': [item_memo] if item_memo else [],
                                            'colors': {item_color: 1}
                                        }
                        now = datetime.datetime.now()
                # Print payment copies
                if print_sync_invoice:  # if invoices synced

                    # start invoice
                    vars.EPSON.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                 density=5,
                                                 invert=False, smooth=False, flip=False))
                    vars.EPSON.write("::Payment Copy::\n")
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write("{}\n".format(companies.name))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write("{}\n".format(companies.street))
                    vars.EPSON.write("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                    invert=False, smooth=False, flip=False))

                    vars.EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
                    vars.EPSON.write("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))

                    vars.EPSON.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3,
                                                 density=6,
                                                 invert=False, smooth=False, flip=False))
                    vars.EPSON.write(
                        '{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                    vars.EPSON.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                 density=2,
                                                 invert=False, smooth=False, flip=False))
                    vars.EPSON.write('{}\n'.format(Job.make_us_phone(customers.phone)))
                    vars.EPSON.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                 density=1,
                                                 invert=False, smooth=False, flip=False))
                    vars.EPSON.write('-----------------------------------------\n')
                    for invoice_id, item_id in print_sync_invoice.items():

                        if invoice_id in print_sync_invoice:
                            for item_id, invoice_item in print_sync_invoice[invoice_id].items():
                                item_name = invoice_item['name']
                                item_price = invoice_item['item_price']
                                item_qty = invoice_item['qty']
                                item_color_string = []
                                item_memo = invoice_item['memos']
                                item_type = invoice_item['type']
                                if 'colors' in invoice_item:
                                    for color_name, color_qty in invoice_item['colors'].items():
                                        if color_name:
                                            item_color_string.append('{}-{}'.format(color_qty, color_name))
                                string_length = len(item_type) + len(str(item_qty)) + len(item_name) + len(
                                    vars.us_dollar(item_price)) + 4
                                string_offset = 42 - string_length if 42 - string_length > 0 else 0
                                vars.EPSON.write('{} {}   {}{}{}\n'.format(item_type,
                                                                           item_qty,
                                                                           item_name,
                                                                           ' ' * string_offset,
                                                                           vars.us_dollar(item_price)))

                                if len(item_memo) > 0:
                                    vars.EPSON.write(pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                                 height=1,
                                                                 density=5, invert=False, smooth=False, flip=False))
                                    vars.EPSON.write('     {}\n'.format('/ '.join(item_memo)))
                                if len(item_color_string) > 0:
                                    vars.EPSON.write(pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                                 height=1,
                                                                 density=5, invert=False, smooth=False, flip=False))
                                    vars.EPSON.write('     {}\n'.format(', '.join(item_color_string)))

                    vars.EPSON.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                 density=1,
                                                 invert=False, smooth=False, flip=False))
                    vars.EPSON.write('-----------------------------------------\n')
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('{} PCS\n'.format(self.total_quantity))
                    vars.EPSON.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                 density=1,
                                                 invert=False, smooth=False, flip=False))
                    vars.EPSON.write('-----------------------------------------\n')
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('    SUBTOTAL:')
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    string_length = len(vars.us_dollar(self.total_subtotal))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write('{}{}\n'.format(' ' * string_offset, vars.us_dollar(self.total_subtotal)))
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    vars.EPSON.write('         TAX:')
                    string_length = len(vars.us_dollar(self.total_tax))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    vars.EPSON.write('{}{}\n'.format(' ' * string_offset, vars.us_dollar(self.total_tax)))

                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    vars.EPSON.write('   After Tax:')
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    string_length = len(vars.us_dollar(self.total_amount))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write('{}{}\n'.format(' ' * string_offset, vars.us_dollar(self.total_amount)))

                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    vars.EPSON.write('      Credit:')
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    string_length = len(vars.us_dollar(self.credits_spent))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write('{}{}\n'.format(' ' * string_offset, vars.us_dollar(self.credits_spent)))

                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    vars.EPSON.write('    Discount:')
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    string_length = len(vars.us_dollar(self.discount_total))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write('{}{}\n'.format(' ' * string_offset, vars.us_dollar(self.discount_total)))

                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    vars.EPSON.write('         Due:')
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    string_length = len(vars.us_dollar(self.total_due))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write('{}{}\n'.format(' ' * string_offset, vars.us_dollar(self.total_due)))
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    vars.EPSON.write('     TENDERED:')
                    string_length = len(vars.us_dollar(self.amount_tendered))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write('{}{}\n\n'.format(' ' * string_offset, vars.us_dollar(self.amount_tendered)))
                    vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    vars.EPSON.write('     BALANCE:')
                    balance = 0 if (
                                       self.amount_tendered - self.total_due) < 0  else self.amount_tendered - self.total_due
                    string_length = len(vars.us_dollar(balance))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.write('{}{}\n\n'.format(' ' * string_offset, vars.us_dollar(balance)))
                    # Cut paper
                    vars.EPSON.write('\n\n\n\n\n\n')
                    vars.EPSON.write(pr.pcmd('PARTIAL_CUT'))

            else:
                popup = Popup()
                popup.title = 'Printer Error'
                content = KV.popup_alert('Usb device not found')
                popup.content = Builder.load_string(content)
                popup.open()
                # Beep Sound
                sys.stdout.write('\a')
                sys.stdout.flush()
        self.status_popup.dismiss()

    def set_result_status(self):
        vars.SEARCH_RESULTS_STATUS = True


class PrinterScreen(Screen):
    printer_name = ObjectProperty(None)
    printer_model_number = ObjectProperty(None)
    printer_nick_name = ObjectProperty(None)
    printer_vendor = ObjectProperty(None)
    printer_product = ObjectProperty(None)
    printer_type = ObjectProperty(None)
    printer_table = ObjectProperty(None)
    r1c2 = ObjectProperty(None)
    r2c2 = ObjectProperty(None)
    r3c2 = ObjectProperty(None)
    r4c2 = ObjectProperty(None)
    r5c2 = ObjectProperty(None)
    r6c2 = ObjectProperty(None)
    edit_popup = Popup()
    validated = 0
    edit_printer_id = None

    def reset(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
        self.printer_name.text = ''
        self.printer_model_number.text = ''
        self.printer_nick_name.text = ''
        self.printer_vendor.text = ''
        self.printer_product.text = ''
        self.printer_type.text = ''
        self.printer_table.clear_widgets()
        self.validated = 0

        self.update_printer_table()
        self.edit_printer_id = None

    def update_printer_table(self):
        h1 = KV.sized_invoice_tr(0, '[color=000000][b]#[/b][/color]', 0.1)
        h2 = KV.sized_invoice_tr(0, '[color=000000][b]Name[/b][/color]', 0.7)
        h3 = KV.sized_invoice_tr(0, '[color=000000][b]Type[/b][/color]', 0.2)

        self.printer_table.add_widget(Builder.load_string(h1))
        self.printer_table.add_widget(Builder.load_string(h2))
        self.printer_table.add_widget(Builder.load_string(h3))

        # update saved printers
        printers = Printer()
        prs = printers.where({'company_id': vars.COMPANY_ID})
        if prs:
            idx = 0
            for printer in prs:
                printer_id = printer['id']
                idx += 1
                col1 = Button(markup=True,
                              size_hint_x=0.1,
                              size_hint_y=None,
                              text='[color=ffffff]{}[/color]'.format(idx),
                              on_release=partial(self.edit_printer_popup, printer_id))
                col2 = Button(markup=True,
                              size_hint_x=0.7,
                              size_hint_y=None,
                              text='[color=ffffff]{}[/color]'.format(printer['name']),
                              on_release=partial(self.edit_printer_popup, printer_id))
                col3 = Button(markup=True,
                              size_hint_x=0.2,
                              size_hint_y=None,
                              text='[color=ffffff]{}[/color]'.format(printer['type']),
                              on_release=partial(self.edit_printer_popup, printer_id))
                self.printer_table.add_widget(col1)
                self.printer_table.add_widget(col2)
                self.printer_table.add_widget(col3)

    def edit_printer_popup(self, id, *args, **kwargs):
        self.edit_printer_id = id
        self.edit_popup = Popup()
        self.edit_popup.title = 'Edit Printer'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='vertical',
                                   size_hint=(1, 0.9))
        edit_table = GridLayout(cols=2,
                                rows=7,
                                row_force_default=True,
                                row_default_height='50sp',
                                spacing='2sp')
        printers = Printer()
        prs = printers.where({'id': id})
        if prs:
            for printer in prs:
                r1c1 = Factory.CenteredFormLabel(text='Name:')
                self.r1c2 = Factory.CenterVerticalTextInput(padding='10cp',
                                                            text='{}'.format(printer['name']))
                edit_table.add_widget(r1c1)
                edit_table.add_widget(self.r1c2)
                r2c1 = Factory.CenteredFormLabel(text='Model #:')
                self.r2c2 = Factory.CenterVerticalTextInput(padding='10cp',
                                                            text='{}'.format(printer['model']))
                edit_table.add_widget(r2c1)
                edit_table.add_widget(self.r2c2)
                r3c1 = Factory.CenteredFormLabel(text=' Nick Name:')
                self.r3c2 = Factory.CenterVerticalTextInput(padding='10cp',
                                                            text='{}'.format(printer['nick_name']))
                edit_table.add_widget(r3c1)
                edit_table.add_widget(self.r3c2)
                r4c1 = Factory.CenteredFormLabel(text=' Vendor ID:')
                self.r4c2 = Factory.CenterVerticalTextInput(padding='10cp',
                                                            text='{}'.format(printer['vendor_id']))
                edit_table.add_widget(r4c1)
                edit_table.add_widget(self.r4c2)
                r5c1 = Factory.CenteredFormLabel(text=' Product ID:')
                self.r5c2 = Factory.CenterVerticalTextInput(padding='10cp',
                                                            text='{}'.format(printer['product_id']))
                edit_table.add_widget(r5c1)
                edit_table.add_widget(self.r5c2)
                r6c1 = Factory.CenteredFormLabel(text=' Type:')
                self.r6c2 = Factory.CenterVerticalTextInput(padding='10cp',
                                                            text='{}'.format(printer['type']))
                edit_table.add_widget(r6c1)
                edit_table.add_widget(self.r6c2)
        inner_layout_1.add_widget(edit_table)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        cancel_button = Button(markup=True,
                               text="Cancel",
                               on_release=self.edit_popup.dismiss)
        edit_button = Button(markup=True,
                             text="Edit",
                             on_release=self.validate_edit)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(edit_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.edit_popup.content = layout
        self.edit_popup.open()

    def validate_edit(self, *args, **kwargs):
        self.validated = 0
        if self.r1c2.text == '':
            self.validated += 1
            self.r1c2.hint_text_color = ERROR_COLOR
            self.r1c2.hint_text = "Please enter a printer name"
        else:
            self.r1c2.hint_text_color = DEFAULT_COLOR
            self.r1c2.hint_text = ""

        if self.r2c2.text == '':
            self.validated += 1
            self.r2c2.hint_text_color = ERROR_COLOR
            self.r2c2.hint_text = "Please enter a model number"
        else:
            self.r2c2.hint_text_color = DEFAULT_COLOR
            self.r2c2.hint_text = ""

        if self.r3c2.text == '':
            self.validated += 1
            self.r3c2.hint_text_color = ERROR_COLOR
            self.r3c2.hint_text = "Please enter a printer nick name"
        else:
            self.r3c2.hint_text_color = DEFAULT_COLOR
            self.r3c2.hint_text = ""

        if self.r4c2.text == '':
            self.validated += 1
            self.r4c2.hint_text_color = ERROR_COLOR
            self.r4c2.hint_text = "Please enter a vendor id"
        else:
            self.r4c2.hint_text_color = DEFAULT_COLOR
            self.r4c2.hint_text = ""

        if self.r5c2.text == '':
            self.validated += 1
            self.r5c2.hint_text_color = ERROR_COLOR
            self.r5c2.hint_text = "Please enter a product id"
        else:

            self.r5c2.hint_text_color = DEFAULT_COLOR
            self.r5c2.hint_text = ""

        if self.r6c2.text == '':
            self.validated += 0  # todo
            self.r6c2.hint_text_color = ERROR_COLOR
            self.r6c2.hint_text = "Please enter a printer name"
        else:
            self.r6c2.hint_text_color = DEFAULT_COLOR
            self.r6c2.hint_text = ""

        if self.validated == 0:
            self.edit_printer()
            self.reset()
        else:
            self.reset()
            popup = Popup()
            popup.title = "Printer Setting"
            content = KV.popup_alert("There are some errors with your printer edit form! Please review and try again.")
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()

    def validate(self):
        self.validated = 0
        if self.printer_name.text == '':
            self.validated += 1
            self.printer_name.hint_text_color = ERROR_COLOR
            self.printer_name.hint_text = "Please enter a printer name"
        else:
            self.printer_name.hint_text_color = DEFAULT_COLOR
            self.printer_name.hint_text = ""

        if self.printer_model_number.text == '':
            self.validated += 1
            self.printer_model_number.hint_text_color = ERROR_COLOR
            self.printer_model_number.hint_text = "Please enter a model number"
        else:
            self.printer_model_number.hint_text_color = DEFAULT_COLOR
            self.printer_model_number.hint_text = ""

        if self.printer_nick_name.text == '':
            self.validated += 1
            self.printer_nick_name.hint_text_color = ERROR_COLOR
            self.printer_nick_name.hint_text = "Please enter a printer nick name"
        else:
            self.printer_nick_name.hint_text_color = DEFAULT_COLOR
            self.printer_nick_name.hint_text = ""

        if self.printer_vendor.text == '':
            self.validated += 1
            self.printer_vendor.hint_text_color = ERROR_COLOR
            self.printer_vendor.hint_text = "Please enter a vendor id"
        else:
            self.printer_vendor.hint_text_color = DEFAULT_COLOR
            self.printer_vendor.hint_text = ""

        if self.printer_product.text == '':
            self.validated += 1
            self.printer_product.hint_text_color = ERROR_COLOR
            self.printer_product.hint_text = "Please enter a product id"
        else:

            self.printer_product.hint_text_color = DEFAULT_COLOR
            self.printer_product.hint_text = ""

        if self.printer_type.text == '':
            self.validated += 0  # todo
            self.printer_type.hint_text_color = ERROR_COLOR
            self.printer_type.hint_text = "Please enter a printer name"
        else:
            self.printer_type.hint_text_color = DEFAULT_COLOR
            self.printer_type.hint_text = ""

        if self.validated == 0:
            self.add_printer()
            self.reset()
        else:
            self.reset()
            popup = Popup()
            popup.title = "Printer Setting"
            content = KV.popup_alert("There are some errors with your printer form! Please review and try again.")
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()

    def add_printer(self):
        printer = Printer()
        printer.company_id = vars.COMPANY_ID
        printer.name = self.printer_name.text
        printer.model = self.printer_model_number.text
        printer.nick_name = self.printer_nick_name.text
        printer.vendor_id = self.printer_vendor.text
        printer.product_id = self.printer_product.text
        printer.type = self.printer_type.text
        printer.status = 1
        if printer.add():
            # set invoice_items data to save
            run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
            try:
                run_sync.start()
            finally:
                run_sync.join()
                print('successfully synced a printer')
                popup = Popup()
                popup.title = "Printer Setting"
                content = KV.popup_alert("Successfully added a printer!")
                popup.content = Builder.load_string(content)
                popup.open()

    def edit_printer(self):
        printer = Printer()
        print(self.edit_printer_id)
        printer.put(where={'id': self.edit_printer_id}, data={'name': self.r1c2.text,
                                                              'model': self.r2c2.text,
                                                              'nick_name': self.r3c2.text,
                                                              'vendor_id': self.r4c2.text,
                                                              'product_id': self.r5c2.text,
                                                              'type': self.r6c2.text})

        # set invoice_items data to save
        run_sync = threading.Thread(target=SYNC.db_sync, args=[vars.COMPANY_ID])
        try:
            run_sync.start()
        finally:
            run_sync.join()
            print('successfully edited a printer')
        popup = Popup()
        popup.title = "Printer Setting"
        content = KV.popup_alert("Successfully edited printer - {}!".format(self.r1c2.text))
        popup.content = Builder.load_string(content)
        popup.open()
        self.edit_popup.dismiss()


class RackScreen(Screen):
    invoice_number = ObjectProperty(None)
    rack_number = ObjectProperty(None)
    rack_table = ObjectProperty(None)
    racks = OrderedDict()
    parent_scroll = ObjectProperty(None)
    marked_invoice_number = None
    edited_rack = False

    def reset(self):
        # Pause sync scheduler
        SCHEDULER.remove_all_jobs()

        self.racks = OrderedDict()
        self.rack_number.text = ''
        self.invoice_number.text = ''
        self.invoice_number.focus = True
        self.marked_invoice_number = None
        self.edited_rack = False
        self.update_rack_table()

    def open_popup(self, *args, **kwargs):
        SYNC_POPUP.title = "Sync In Progress"
        content = KV.popup_alert("Please wait while we sync the database.")
        SYNC_POPUP.content = Builder.load_string(content)
        SYNC_POPUP.open()

    def set_result_status(self):
        vars.SEARCH_RESULTS_STATUS = True
        self.reset()

    def update_rack_table(self):
        self.rack_table.clear_widgets()
        h1 = KV.invoice_tr(0, '#')
        h2 = KV.invoice_tr(0, 'Invoice #')
        h3 = KV.invoice_tr(0, 'Rack #')
        h4 = KV.invoice_tr(0, 'Action')
        self.rack_table.add_widget(Builder.load_string(h1))
        self.rack_table.add_widget(Builder.load_string(h2))
        self.rack_table.add_widget(Builder.load_string(h3))
        self.rack_table.add_widget(Builder.load_string(h4))
        if self.racks:
            idx = 0
            marked_tr4 = False
            for invoice_number, rack_number in self.racks.items():
                idx += 1
                if invoice_number == self.marked_invoice_number:
                    tr1 = Factory.CenteredHighlightedLabel(text='[color=000000]{}[/color]'.format(idx))
                    tr2 = Factory.CenteredHighlightedLabel(text='[color=000000]{}[/color]'.format(invoice_number))
                    tr3 = Factory.CenteredHighlightedLabel(
                        text='[color=000000]{}[/color]'.format(rack_number if rack_number else ''))
                    tr4 = Button(markup=True,
                                 text='Edit')
                    marked_tr4 = tr4
                else:
                    tr1 = Factory.CenteredLabel(text='[color=000000]{}[/color]'.format(idx))
                    tr2 = Factory.CenteredLabel(text='[color=000000]{}[/color]'.format(invoice_number))
                    tr3 = Factory.CenteredLabel(
                        text='[color=000000]{}[/color]'.format(rack_number if rack_number else ''))
                    tr4 = Button(markup=True,
                                 text='Edit')
                    marked_tr4 = False
                self.rack_table.add_widget(tr1)
                self.rack_table.add_widget(tr2)
                self.rack_table.add_widget(tr3)
                self.rack_table.add_widget(tr4)
            if marked_tr4:
                self.parent_scroll.scroll_to(marked_tr4)
            else:
                self.parent_scroll.scroll_to(tr4)

    def set_invoice_number(self):
        invoices = Invoice()
        search = None if not self.invoice_number.text else self.invoice_number.text
        found_invoices = invoices.where({'invoice_id': search})
        if not self.invoice_number.text:
            popup = Popup()
            popup.title = 'Error: Rack process error'
            popup.size_hint = None, None
            popup.size = 800, 600
            body = KV.popup_alert(
                msg='Invoice number cannot be left empty.')
            popup.content = Builder.load_string(body)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()
        elif not found_invoices:
            # check to see if invoice is in server or on local
            check_current = invoices.where({'invoice_id': self.invoice_number.text})
            if not check_current:
                t1 = Thread(SYNC.sync_rackable_invoice(self.invoice_number.text))
                t1.start()
                t1.join()
            check_current = invoices.where({'invoice_id': self.invoice_number.text})
            if not check_current:
                popup = Popup()
                popup.title = 'Error: Rack process error'
                popup.size_hint = None, None
                popup.size = 800, 600
                body = KV.popup_alert(
                    msg='No such invoice number.')
                popup.content = Builder.load_string(body)
                popup.open()
                # Beep Sound
                sys.stdout.write('\a')
                sys.stdout.flush()
        elif self.invoice_number.text in self.racks:
            self.edited_rack = self.racks[self.invoice_number.text]
            self.racks[self.invoice_number.text] = False
            self.rack_number.focus = True
        else:
            self.edited_rack = False
            self.racks[self.invoice_number.text] = False
            self.rack_number.focus = True
            self.marked_invoice_number = self.invoice_number.text

        self.update_rack_table()

    def set_rack_number(self):
        invoices = Invoice()
        now = datetime.datetime.now()
        rack_date = datetime.datetime.strftime(now, "%Y-%m-%d %H:%M:%S")
        if not self.invoice_number.text:
            popup = Popup()
            popup.title = 'Error: Rack process error'
            popup.size_hint = None, None
            popup.size = 800, 600
            body = KV.popup_alert(
                msg='Please provide an invoice number.')
            popup.content = Builder.load_string(body)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()

        else:
            formatted_rack = self.rack_number.text.replace("%R", "")
            if vars.EPSON:
                pr = Printer()
                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=3,
                                invert=False, smooth=False, flip=False))
                if self.edited_rack:
                    vars.EPSON.write('EDITED: {} - (OLD {}) -> (NEW {})\n'.format(
                        self.invoice_number.text,
                        self.edited_rack,
                        formatted_rack))
                    self.edited_rack = False
                else:
                    vars.EPSON.write('{} - {}\n'.format(self.invoice_number.text, formatted_rack))


            invoices.put(where={'invoice_id': self.invoice_number.text},
                         data={'rack': formatted_rack,
                               'rack_date': rack_date,
                               'status': 2})  # rack and update status

            self.racks[self.invoice_number.text] = formatted_rack
            self.invoice_number.text = ''
            self.rack_number.text = ''
            self.update_rack_table()
            self.marked_invoice_number = self.invoice_number.text

        self.invoice_number.focus = True

    def save_racks(self):
        # save rows
        if self.racks:
            # invoices = Invoice()
            # for invoice_id, rack in self.racks.items():
            #     invoices.put(where={'invoice_id': invoice_id},
            #                  data={'rack': rack,
            #                        'rack_date': rack_date,
            #                        'status': 2})  # rack and update status

            # update db
            run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
            try:
                run_sync.start()
            finally:
                run_sync.join()
                print('sync now finished')

        # set user to go back to search screen
        if vars.CUSTOMER_ID:
            self.set_result_status()

        # Cut paper
        if vars.EPSON:
            pr = Printer()
            vars.EPSON.write(pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                         invert=False, smooth=False, flip=False))
            vars.EPSON.write('{}'.format((datetime.datetime.now().strftime('%a %m/%d/%Y %I:%M %p'))))
            vars.EPSON.write('\n\n\n\n\n\n')
            vars.EPSON.write(pr.pcmd('PARTIAL_CUT'))


class ReportsScreen(Screen):
    pass


class SearchScreen(Screen):
    id = ObjectProperty(None)
    cust_mark_label = ObjectProperty(None)
    invoice_table = ObjectProperty(None)
    invoice_table_body = ObjectProperty(None)
    search = ObjectProperty(None)
    cust_last_name = ObjectProperty(None)
    cust_first_name = ObjectProperty(None)
    cust_phone = ObjectProperty(None)
    cust_last_drop = ObjectProperty(None)
    cust_starch = ObjectProperty(None)
    cust_credit_label = ObjectProperty(None)
    cust_credit = ObjectProperty(None)
    cust_account_label = ObjectProperty(None)
    cust_account = ObjectProperty(None)
    cust_invoice_memo = ObjectProperty(None)
    cust_important_memo = ObjectProperty(None)
    customer_id_ti = ObjectProperty(None)
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
    view_deliveries_btn = ObjectProperty(None)
    main_popup = Popup()
    date_picker = ObjectProperty(None)
    due_date = None
    due_date_string = None
    now = datetime.datetime.now()
    month = now.month
    year = now.year
    day = now.day
    calendar_layout = ObjectProperty(None)
    month_button = ObjectProperty(None)
    year_button = ObjectProperty(None)
    payment_popup = Popup()
    print_popup = ObjectProperty(None)
    calendar_layout = ObjectProperty(None)
    create_calendar_table = ObjectProperty(None)
    quick_box = None
    display_input = ObjectProperty(None)
    calculator_control_table = ObjectProperty(None)
    calc_history = []
    calc_amount = []
    tags_grid = ObjectProperty(None)
    cust_info_label = ObjectProperty(None)
    selected_tags_list = []
    cards = None
    card_id = None
    card_id_spinner = None
    card_string = None
    address_string = None
    addresses = None
    address_id = None
    address_id_spinner = None
    pickup_switch = None
    dropoff_switch = None
    dropoff_date = False
    dropoff_date_btn = None
    pickup_date = False
    pickup_date_btn = None
    pickup_time_spinner = None
    dropoff_time_spinner = None
    pickup_delivery_id = None
    dropoff_delivery_id = None
    pickup_time_group = None
    special_instructions = None
    delivery_popup = Popup()
    repopup = Popup()
    name_input = None
    street_input = None
    suite_input = None
    city_input = None
    state_input = None
    zipcode_input = None
    concierge_name_input = None
    concierge_number_input = None
    root_payment_id = None
    credit_reason = None
    credit_amount = None
    selected_account_tr = None
    inner_layout_1 = None
    change_input = None
    total_input = None
    tendered_input = None
    payment_type = None
    label_input = None
    tag_input = None
    background_color = None
    background_rgba = None
    status = None
    barcode_layout = ObjectProperty(None)
    barcode_save_data = None
    barcode_input = ObjectProperty(None)

    def scheduler_stop(self):
        try:
            SCHEDULER.remove_all_jobs()
            print('Auto Sync Stopped')
        except SchedulerNotRunningError:
            print('Auto Sync Already Stopped')

    def scheduler_restart(self):
        try:
            SCHEDULER.remove_all_jobs()
            SCHEDULER.add_job(partial(SYNC.db_sync,vars.COMPANY_ID), 'interval', seconds=30)
            print('Auto Sync Resumed')
        except SchedulerNotRunningError:
            SCHEDULER.add_job(partial(SYNC.db_sync,vars.COMPANY_ID), 'interval', seconds=30)
            SCHEDULER.start()
            print('Auto Sync failed to launch starting again')


    def reset(self, *args, **kwargs):
        # Resume auto sync
        self.scheduler_restart()

        # reset member variables
        vars.ROW_SEARCH = 0, 10
        vars.ROW_CAP = 0
        vars.SEARCH_TEXT = None
        self.quick_box = None
        self.calc_history = []
        self.calc_amount = []
        self.selected_tags_list = []
        self.selected_account_tr = []
        self.inner_layout_1 = None
        self.cards = False
        self.card_id = None
        self.card_id_spinner = None
        self.card_string = None
        self.address_string = None
        self.addresses = None
        self.address_id = None
        self.address_id_spinner = None
        self.pickup_switch = None
        self.dropoff_switch = None
        self.pickup_date = False
        self.pickup_date_btn = None
        self.dropoff_date = False
        self.dropoff_date_btn = None
        self.pickup_time_spinner = None
        self.dropoff_time_spinner = None
        self.pickup_delivery_id = None
        self.dropoff_delivery_id = None
        self.dropoff_time_group = None
        self.special_instructions = None
        self.name_input = None
        self.street_input = None
        self.suite_input = None
        self.city_input = None
        self.state_input = None
        self.zipcode_input = None
        self.concierge_name_input = None
        self.concierge_number_input = None
        self.view_deliveries_btn.text = 'View Delivery Schedule'
        self.root_payment_id = None
        self.credit_reason = None
        self.credit_amount = None
        self.change_input = None
        self.total_input = None
        self.tendered_input = None
        self.payment_type = None
        self.label_input = None
        self.tag_input = None
        self.background_color = None
        self.background_rgba = None
        self.status = None
        self.barcode_save_data = {}
        if vars.SEARCH_RESULTS_STATUS:
            self.edit_invoice_btn.disabled = False if vars.INVOICE_ID is not None else True
            data = {'user_id': vars.CUSTOMER_ID}
            customers = User()
            results = customers.where(data)
            print('Search results are set getting customer #{}'.format(vars.CUSTOMER_ID))
            Clock.schedule_once(partial(self.customer_results,results),1)


        else:
            vars.CUSTOMER_ID = None
            vars.INVOICE_ID = None
            self.search.text = ''
            self.customer_mark_l.text = ''
            self.customer_id_ti.text = ''
            self.cust_last_name.text = ''
            self.cust_first_name.text = ''
            self.cust_phone.text = ''
            self.cust_last_drop.text = ''
            self.cust_starch.text = ''
            self.cust_credit.text = ''
            self.cust_account.text = ''
            self.cust_invoice_memo.text = ''
            self.cust_important_memo.text = ''
            self.cust_info_label.text = 'Customer Info:'
            # show the proper buttons
            self.history_btn.disabled = True
            self.edit_invoice_btn.disabled = True
            self.edit_customer_btn.disabled = True
            self.delivery_btn.disabled = True
            self.reprint_btn.disabled = True
            self.quick_btn.disabled = True
            self.pickup_btn.disabled = True
            self.dropoff_btn.disabled = True
            # clear the search text input
            self.search.text = ''
            # clear the inventory table
            self.invoice_table_body.clear_widgets()
            self.due_date = None
            self.due_date_string = None
            vars.SEARCH_RESULTS_STATUS = False

        Clock.schedule_once(self.focus_input)
        SYNC_POPUP.dismiss()

    def focus_input(self, *args, **kwargs):
        self.search.focus = True

    def sync_db(self):
        run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
        try:
            run_sync.start()
        finally:
            run_sync.join()
            print('sync now finished')
            vars.SEARCH_RESULTS_STATUS = True if vars.CUSTOMER_ID else False
            self.reset()
        self.search.focus = True

    def open_popup(self, *args, **kwargs):
        SYNC_POPUP.title = "Loading"
        content = KV.popup_alert("Please wait while the page is loading")
        SYNC_POPUP.content = Builder.load_string(content)
        SYNC_POPUP.open()

    def search_customer(self, *args, **kwargs):
        popup = Popup()
        search_text = self.search.text
        customers = User()
        vars.INVOICE_ID = None
        if "ID%" in search_text.upper():
            # search for id
            new_search_text = search_text.upper().replace("ID%", "")
            users = customers.where({'user_id': new_search_text})
            if users:
                self.customer_results(users)

        elif "INV%" in search_text.upper():
            new_search_text = search_text.upper().replace("INV%", "")
            data = {
                'invoice_id': str(new_search_text)
            }
            inv = Invoice()
            inv_1 = inv.where(data)
            if len(inv_1) > 0:
                for invoice in inv_1:
                    vars.INVOICE_ID = new_search_text
                    vars.CUSTOMER_ID = invoice['customer_id']
                    self.invoice_selected(invoice_id=vars.INVOICE_ID)

            else:
                popup.title = 'No such invoice'
                popup.size_hint = None, None
                popup.size = 800, 600
                content = KV.popup_alert(msg="Could not find an invoice with this invoice id. Please try again")
                popup.content = Builder.load_string(content)
                popup.open()

        elif "#%" in search_text.upper():
            new_search_text = search_text.replace("#%", "")
            # search for phone
            data = {'phone': '{}'.format(new_search_text)}
            cust1 = customers.where(data)
            vars.INVOICE_ID = None
            self.customer_results(cust1)
        elif "I%" in search_text.upper():
            new_search_text = search_text.upper().replace("I%", "")
            # search for item
            data = {
                'invoice_items_id': str(new_search_text)
            }
            inv = InvoiceItem()
            inv_1 = inv.where(data)
            if len(inv_1) > 0:
                for invoice in inv_1:
                    vars.INVOICE_ID = invoice['invoice_id']
                    vars.CUSTOMER_ID = invoice['customer_id']
                    self.invoice_selected(invoice_id=vars.INVOICE_ID)

            else:
                popup.title = 'No such invoice item'
                popup.size_hint = None, None
                popup.size = 800, 600
                content = KV.popup_alert(msg="Could not find an invoice item with this id. Please try again")
                popup.content = Builder.load_string(content)
                popup.open()
        else:

            if len(self.search.text) > 0:
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
                        print('searching for invoice')
                        data = {
                            'invoice_id': '"{}"'.format(int(self.search.text))
                        }
                        inv = Invoice()
                        inv_1 = inv.where(data)

                        if len(inv_1) > 0:
                            for invoice in inv_1:
                                vars.INVOICE_ID = self.search.text
                                vars.CUSTOMER_ID = invoice['customer_id']
                                data = {'user_id': '"{}"'.format(vars.CUSTOMER_ID)}
                                cust1 = customers.where(data)

                                self.customer_results(cust1)
                                self.invoice_selected(invoice_id=vars.INVOICE_ID)

                        else:
                            popup.title = 'No such invoice'
                            popup.size_hint = None, None
                            popup.size = 800, 600
                            content = KV.popup_alert(
                                msg="Could not find an invoice with this invoice id. Please try again")
                            popup.content = Builder.load_string(content)
                            popup.open()

                    else:  # look for a customer id
                        data = {'user_id': self.search.text}
                        cust1 = customers.where(data)

                        self.customer_results(cust1)

                else:  # Lookup by last name || mark
                    # turn search into list
                    full_name = self.search.text.split()
                    last_name = full_name[0]
                    try:
                        first_name = full_name[1] if full_name[1] is not None else None
                    except IndexError:
                        first_name = None
                    data = {
                        'last_name': '"%{}%"'.format(last_name),
                        'ORDER_BY': 'last_name ASC',
                        'LIMIT': '{},{}'.format(vars.ROW_SEARCH[0], 10)
                    }
                    if first_name is not None:
                        data = {'last_name': '"%{}%"'.format(last_name),
                                'first_name': '"%{}%"'.format(first_name),
                                'ORDER_BY': 'last_name ASC',
                                'LIMIT': '{},{}'.format(vars.ROW_SEARCH[0], 10)}

                    vars.ROW_CAP = len(customers.like(data))
                    vars.SEARCH_TEXT = self.search.text

                    cust1 = customers.like(data)
                    self.customer_results(cust1)
            else:
                popup = Popup()
                popup.title = 'Search Error'
                popup.content = Builder.load_string(
                    KV.popup_alert('Search cannot be an empty value. Please try again.'))
                popup.open()
        customers.close_connection()

    def create_invoice_row(self, row, *args, **kwargs):
        """ Creates invoice table row and displays it to screen """
        check_invoice_id = False
        try:
            check_invoice_id = True if (int(vars.INVOICE_ID) - int(row['invoice_id']) == 0) else False
        except ValueError:
            pass
        except TypeError:
            pass

        print('{} - {} - {}'.format(vars.INVOICE_ID,row['invoice_id'],check_invoice_id))
        invoice_id = row['invoice_id']
        company_id = row['company_id']
        company_name = 'R' if company_id is 1 else 'M'
        quantity = row['quantity']
        rack = row['rack']
        total = vars.us_dollar(row['total'])
        due = row['due_date']
        invoice_items = InvoiceItem().where({'invoice_id': invoice_id})
        count_invoice_items = len(invoice_items)
        try:
            dt = datetime.datetime.strptime(due, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = datetime.datetime.strptime('1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
        except TypeError:
            dt = datetime.datetime.strptime('1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
        due_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        dow = vars.dow(dt.replace(tzinfo=datetime.timezone.utc).weekday())
        due_date = dt.strftime('%m/%d {}').format(dow)
        dt = datetime.datetime.strptime(NOW,
                                        "%Y-%m-%d %H:%M:%S") if NOW is not None else datetime.datetime.strptime(
            '1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
        now_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        # check to see if invoice is overdue

        invoice_status = row['status']
        if invoice_status is 5:  # state 5
            text_color = [0, 0, 0, 1] if not check_invoice_id else [0.898, 0.898, 0.898, 1]
            self.background_rgba = [0.826, 0.826, 0.826, 0.1] if not check_invoice_id else [0.369, 0.369, 0.369, 0.1]
            self.background_color = [0.826, 0.826, 0.826, 1] if not check_invoice_id else [0.369, 0.369, 0.369, 1]
            self.status = 5

        elif invoice_status is 4 or invoice_status is 3:  # state 4
            text_color = [1, 0, 0, 1] if check_invoice_id else [1, 0.8, 0.8, 1]
            self.background_rgba = [1, 0.717, 0.717, 0.1] if not check_invoice_id else [1, 0, 0, 0.1]
            self.background_color = [1, 0.717, 0.717, 1] if not check_invoice_id else [1, 0, 0, 1]
            self.status = 4

        elif invoice_status is 2:  # state 3
            text_color = [0, 0.639, 0.149, 1] if check_invoice_id else [0.847, 0.969, 0.847, 1]
            self.background_rgba = [0.847, 0.968, 0.847, 0.1] if not check_invoice_id else [0, 0.64, 0.149, 0.1]
            self.background_color = [0.847, 0.968, 0.847, 1] if not check_invoice_id else [0, 0.64, 0.149, 1]
            self.status = 3

        else:
            if due_strtotime < now_strtotime:  # overdue state 2
                text_color = [0.059, 0.278, 1, 1] if check_invoice_id else [0.8156, 0.847, 0.961, 1]
                self.background_rgba = [0.816, 0.847, 0.961, 0.1] if not check_invoice_id else [0.059, 0.278, 1, 0.1]
                self.background_color = [0.816, 0.847, 0.961, 1] if not check_invoice_id else [0.059, 0.278, 1, 1]
                self.status = 2

            elif count_invoice_items == 0:  # #quick drop state 6
                text_color = [0, 0, 0, 1] if not check_invoice_id else [0, 0, 0, 1]
                self.background_rgba = [0.9960784314, 1, 0.7176470588, 0.1] if not check_invoice_id else [0.98431373, 1, 0, 0.1]
                self.background_color = [0.9960784314, 1, 0.7176470588, 1] if not check_invoice_id else [0.98431373, 1, 0, 1]
                self.status = 6
            else:  # state 1
                text_color = [0, 0, 0, 1] if not check_invoice_id else [0.898, 0.898, 0.898, 1]
                self.background_rgba = [0.826, 0.826, 0.826, 0.1] if not check_invoice_id else [0.369, 0.369, 0.369, 0.1]
                self.background_color = [0.826, 0.826, 0.826, 1] if not check_invoice_id else [0.369, 0.369, 0.369, 1]
                self.status = 1
        tr_1 = Factory.InvoiceTr(on_release=partial(self.invoice_selected, invoice_id),
                                 group="tr")
        tr_1.status = self.status
        tr_1.set_color = self.background_color
        tr_1.background_color = self.background_rgba
        label_1 = Label(markup=True,
                        color=text_color,
                        text="[b]{}[/b]".format('{0:06d}'.format(invoice_id)))
        tr_1.ids.invoice_table_row_td.add_widget(label_1)
        label_2 = Label(markup=True,
                        color=text_color,
                        text='[b]{}[/b]'.format(company_name))
        tr_1.ids.invoice_table_row_td.add_widget(label_2)
        label_3 = Label(markup=True,
                        color=text_color,
                        text='[b]{}[/b]'.format(due_date))
        tr_1.ids.invoice_table_row_td.add_widget(label_3)
        label_4 = Label(markup=True,
                        color=text_color,
                        text='[b]{}[/b]'.format(rack))
        tr_1.ids.invoice_table_row_td.add_widget(label_4)
        label_5 = Label(markup=True,
                        color=text_color,
                        text='[b]{}[/b]'.format(quantity))
        tr_1.ids.invoice_table_row_td.add_widget(label_5)
        label_6 = Label(markup=True,
                        color=text_color,
                        text='[b]{}[/b]'.format(total))
        tr_1.ids.invoice_table_row_td.add_widget(label_6)
        if check_invoice_id:
            tr_1.state = 'down'
        self.invoice_table_body.add_widget(tr_1)
        return True

    def invoice_selected(self, invoice_id, *args, **kwargs):
        vars.INVOICE_ID = invoice_id
        print('found customer = {} and invoice id = {}'.format(vars.CUSTOMER_ID, invoice_id))
        data = {
            'user_id': '"{}"'.format(vars.CUSTOMER_ID)
        }
        customers = User()

        cust1 = customers.where(data)
        # self.customer_results(cust1)
        for child in self.invoice_table_body.children:
            if child.state is 'down':
                # find status and change the background color

                if child.status is 1:
                    text_color = [0.898, 0.898, 0.898, 1]
                    child.background_color = [0.369, 0.369, 0.369, 0.1]
                    child.set_color = [0.369, 0.369, 0.369, 1]
                elif child.status is 2:
                    text_color = [0.8156, 0.847, 0.961, 1]
                    child.background_color = [0.059, 0.278, 1, 0.1]
                    child.set_color = [0.059, 0.278, 1, 1]
                elif child.status is 3:
                    text_color = [0.847, 0.969, 0.847, 1]
                    child.background_color = [0, 0.64, 0.149, 0.1]
                    child.set_color = [0, 0.64, 0.149, 1]
                elif child.status is 4:
                    text_color = [1, 0.8, 0.8, 1]
                    child.background_color = [1, 0, 0, 0.1]
                    child.set_color = [1, 0, 0, 1]
                elif child.status is 5:
                    text_color = [0.898, 0.898, 0.898, 1]
                    child.background_color = [0.369, 0.369, 0.369, 0.1]
                    child.set_color = [0.369, 0.369, 0.369, 1]
                else:
                    text_color = [0, 0, 0, 1]
                    child.background_color = [0.98431373, 1, 0, 0.1]
                    child.set_color = [0.98431373, 1, 0, 1]


            else:
                if child.status is 1:
                    text_color = [0, 0, 0, 1]
                    child.background_color = [0.826, 0.826, 0.826, 0.1]
                    child.set_color = [0.826, 0.826, 0.826, 1]
                elif child.status is 2:
                    text_color = [0.059, 0.278, 1, 1]
                    child.background_color = [0.816, 0.847, 0.961, 0.1]
                    child.set_color = [0.816, 0.847, 0.961, 1]
                elif child.status is 3:
                    text_color = [0, 0.639, 0.149, 1]
                    child.background_color = [0.847, 0.968, 0.847, 0.1]
                    child.set_color = [0.847, 0.968, 0.847, 1]
                elif child.status is 4:
                    text_color = [1, 0, 0, 1]
                    child.background_color = [1, 0.717, 0.717, 0.1]
                    child.set_color = [1, 0.717, 0.717, 1]
                elif child.status is 5:
                    text_color = [0, 0, 0, 1]
                    child.background_color = [0.826, 0.826, 0.826, 0.1]
                    child.set_color = [0.826, 0.826, 0.826, 1]
                else:
                    text_color = [0, 0, 0, 1]
                    child.background_color = [0.9960784314, 1, 0.7176470588, 0.1]
                    child.set_color = [0.9960784314, 1, 0.7176470588, 1]
            for grandchild in child.children:
                for ggc in grandchild.children:
                    ggc.color = text_color

        # show the edit button
        self.edit_invoice_btn.disabled = False
        customers.close_connection()

    def customer_sync(self):
        try:
            SCHEDULER.remove_all_jobs()
            SCHEDULER.add_job(SYNC.sync_customer, 'date', run_date=None, args=[vars.CUSTOMER_ID])
            SCHEDULER.add_job(partial(SYNC.db_sync, vars.COMPANY_ID), 'interval', seconds=30)
            print('Syncing Customer Data 1st attempt')
        except SchedulerNotRunningError:
            SCHEDULER.add_job(SYNC.sync_customer, 'date', run_date=None, args=[vars.CUSTOMER_ID])
            SCHEDULER.add_job(partial(SYNC.db_sync, vars.COMPANY_ID), 'interval', seconds=30)
            SCHEDULER.start()
            print('Auto Sync not running, syncing customer data now.')

    def customer_select(self, customer_id):
        users = User()
        data = {'user_id': customer_id}
        customers = users.where(data)
        self.customer_results(customers)
        # vars.INVOICE_ID = None
        vars.CUSTOMER_ID = customer_id
        vars.SEARCH_RESULTS_STATUS = True
        users.close_connection()
        Clock.schedule_once(self.focus_input)

    def customer_results(self, data, *args, **kwargs):
        # stop scheduler to get only customer data

        # Found customer via where, now display data to screen
        if len(data) == 1:
            Clock.schedule_once(self.focus_input)
            for result in data:
                vars.CUSTOMER_ID = result['user_id']
                vars.SEARCH_RESULTS_STATUS = True if vars.CUSTOMER_ID else False
                # start syncing in background
                t1 = Thread(target=self.customer_sync, args=())
                t1.start()
                t1.join()
                # last 10 setup
                vars.update_last_10()
                # clear the current widget
                self.invoice_table_body.clear_widgets()
                # add the table headers
                # self.create_invoice_headers()
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

                Clock.schedule_once(partial(self.invoice_selected, vars.INVOICE_ID))


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
                self.cust_info_label.text = 'Customer Info: [color=FF0000]Account[/color]' if result[
                    'account'] else 'Customer Info:'
                self.cust_mark_label.text = custid_string
                self.customer_id_ti.text = str(vars.CUSTOMER_ID) if vars.CUSTOMER_ID else ''
                self.cust_last_name.text = result['last_name'] if result['last_name'] else ''
                self.cust_first_name.text = result['first_name'] if result['first_name'] else ''
                self.cust_phone.text = Job.make_us_phone(result['phone']) if result['phone'] else ''
                self.cust_last_drop.text = last_drop
                self.cust_starch.text = self.get_starch_by_id(result['starch'])
                self.cust_credit_label.bind(on_ref_press=self.credit_history)
                self.cust_account_label.bind(on_ref_press=self.account_history_popup)
                self.cust_credit.text = '${:,.2f}'.format(result['credits']) if result['credits'] else '$0.00'
                self.cust_account.text = '${:,.2f}'.format(result['account_total']) if result[
                    'account_total'] else '$0.00'
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
            self.delivery_btn.disabled = False
            self.reprint_btn.disabled = False
            self.quick_btn.disabled = False
            self.pickup_btn.disabled = False
            self.dropoff_btn.disabled = False
            # clear the search text input
            self.search.focus = True
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
        self.search.focus = True

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

    def reprint_popup(self):
        self.repopup = Popup()
        self.repopup.title = 'Reprint Invoice #{}'.format(vars.INVOICE_ID)
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.9))
        inner_layout_1.add_widget(Button(markup=True,
                                         text="Print Card",
                                         on_release=self.print_card))
        inner_layout_1.add_widget(Button(markup=True,
                                         text='Store Copy',
                                         on_release=partial(self.reprint_invoice, 1)))
        inner_layout_1.add_widget(Button(markup=True,
                                         text='Customer Copy',
                                         on_release=partial(self.reprint_invoice, 2)))
        inner_layout_1.add_widget(Button(markup=True,
                                         text='Tags',
                                         on_release=self.reprint_tags))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_release=self.close_reprint_popup))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.repopup.content = layout
        self.repopup.open()

    def close_reprint_popup(self, *args, **kwargs):
        self.repopup.dismiss()
        vars.SEARCH_RESULTS_STATUS = True
        self.reset()

    def quick_popup(self, *args, **kwargs):
        # setup calendar default date
        store_hours = Company().get_store_hours(vars.COMPANY_ID)
        today = datetime.datetime.today()
        dow = int(datetime.datetime.today().strftime("%w"))

        turn_around_day = int(store_hours[dow]['turnaround']) if 'turnaround' in store_hours[dow] else 0
        turn_around_hour = store_hours[dow]['due_hour'] if 'due_hour' in store_hours[dow] else '4'
        turn_around_minutes = store_hours[dow]['due_minutes'] if 'due_minutes' in store_hours[dow] else '00'
        turn_around_ampm = store_hours[dow]['due_ampm'] if 'due_ampm' in store_hours[dow] else 'pm'
        new_date = today + datetime.timedelta(days=turn_around_day)
        date_string = '{} {}:{}:00'.format(new_date.strftime("%Y-%m-%d"),
                                           turn_around_hour if turn_around_ampm == 'am' else int(
                                               turn_around_hour) + 12,
                                           turn_around_minutes)
        self.due_date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        self.due_date_string = '{}'.format(self.due_date.strftime('%a %m/%d %I:%M%p'))

        # create popup
        self.main_popup.title = 'Quick Ticket'
        base_layout = BoxLayout(orientation="vertical",
                                size_hint=(1, 1))
        self.quick_box = Factory.QuickBox()
        # add due date
        self.quick_box.ids.quick_due_date.text = self.due_date_string
        self.quick_box.ids.quick_due_date.bind(on_release=self.make_calendar)
        inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                   orientation="horizontal")
        cancel_button = Button(text="Cancel",
                               markup=True,
                               on_release=self.main_popup.dismiss)
        print_button = Button(text="Print",
                              markup=True,
                              on_release=self.quick_print)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(print_button)
        base_layout.add_widget(self.quick_box)
        base_layout.add_widget(inner_layout_2)

        self.main_popup.content = base_layout
        self.main_popup.open()

        pass

    def make_calendar(self, *args, **kwargs):

        store_hours = Company().get_store_hours(vars.COMPANY_ID)
        today = datetime.datetime.today()
        dow = int(datetime.datetime.today().strftime("%w"))
        turn_around_day = int(store_hours[dow]['turnaround']) if 'turnaround' in store_hours[dow] else 0
        turn_around_hour = store_hours[dow]['due_hour'] if 'due_hour' in store_hours[dow] else '4'
        turn_around_minutes = store_hours[dow]['due_minutes'] if 'due_minutes' in store_hours[dow] else '00'
        turn_around_ampm = store_hours[dow]['due_ampm'] if 'due_ampm' in store_hours[dow] else 'pm'
        new_date = today + datetime.timedelta(days=turn_around_day)
        date_string = '{} {}:{}:00'.format(new_date.strftime("%Y-%m-%d"),
                                           turn_around_hour if turn_around_ampm == 'am' else int(turn_around_hour) + 12,
                                           turn_around_minutes)
        due_date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        self.month = int(due_date.strftime('%m'))

        popup = Popup()
        popup.title = 'Calendar'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(size_hint=(1, 0.9),
                                   orientation='vertical')
        calendar_selection = GridLayout(cols=4,
                                        rows=1,
                                        size_hint=(1, 0.1))
        prev_month = Button(markup=True,
                            text="<",
                            font_size="30sp",
                            on_release=self.prev_month)
        next_month = Button(markup=True,
                            text=">",
                            font_size="30sp",
                            on_release=self.next_month)
        select_month = Factory.SelectMonth()
        self.month_button = Button(text='{}'.format(vars.month_by_number(self.month)),
                                   on_release=select_month.open)
        for index in range(12):
            month_options = Button(text='{}'.format(vars.month_by_number(index)),
                                   size_hint_y=None,
                                   height=40,
                                   on_release=partial(self.select_calendar_month, index))
            select_month.add_widget(month_options)

        select_month.on_select = lambda instance, x: setattr(self.month_button, 'text', x)
        select_year = Factory.SelectMonth()

        self.year_button = Button(text="{}".format(self.year),
                                  on_release=select_year.open)
        for index in range(10):
            year_options = Button(text='{}'.format(int(self.year) + index),
                                  size_hint_y=None,
                                  height=40,
                                  on_release=partial(self.select_calendar_year, index))
            select_year.add_widget(year_options)

        select_year.bind(on_select=lambda instance, x: setattr(self.year_button, 'text', x))
        calendar_selection.add_widget(prev_month)
        calendar_selection.add_widget(self.month_button)
        calendar_selection.add_widget(self.year_button)
        calendar_selection.add_widget(next_month)
        self.calendar_layout = GridLayout(cols=7,
                                          rows=8,
                                          size_hint=(1, 0.9))
        store_hours = Company().get_store_hours(vars.COMPANY_ID)
        today_date = datetime.datetime.today()
        today_string = today_date.strftime('%Y-%m-%d 00:00:00')
        check_today = datetime.datetime.strptime(today_string, "%Y-%m-%d %H:%M:%S").timestamp()
        due_date_string = self.due_date.strftime('%Y-%m-%d 00:00:00')
        check_due_date = datetime.datetime.strptime(due_date_string, "%Y-%m-%d %H:%M:%S").timestamp()

        self.create_calendar_table()

        inner_layout_1.add_widget(calendar_selection)
        inner_layout_1.add_widget(self.calendar_layout)
        inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                   orientation='horizontal')
        inner_layout_2.add_widget(Button(markup=True,
                                         text="Okay",
                                         on_release=popup.dismiss))

        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def create_calendar_table(self):
        # set the variables

        store_hours = Company().get_store_hours(vars.COMPANY_ID)
        today_date = datetime.datetime.today()
        today_string = today_date.strftime('%Y-%m-%d 00:00:00')
        check_today = datetime.datetime.strptime(today_string, "%Y-%m-%d %H:%M:%S").timestamp()
        due_date_string = self.due_date.strftime('%Y-%m-%d 00:00:00')
        check_due_date = datetime.datetime.strptime(due_date_string, "%Y-%m-%d %H:%M:%S").timestamp()

        self.calendar_layout.clear_widgets()
        calendars = Calendar()
        calendars.setfirstweekday(calendar.SUNDAY)
        selected_month = self.month - 1
        year_dates = calendars.yeardays2calendar(year=self.year, width=1)
        th1 = KV.invoice_tr(0, 'Su')
        th2 = KV.invoice_tr(0, 'Mo')
        th3 = KV.invoice_tr(0, 'Tu')
        th4 = KV.invoice_tr(0, 'We')
        th5 = KV.invoice_tr(0, 'Th')
        th6 = KV.invoice_tr(0, 'Fr')
        th7 = KV.invoice_tr(0, 'Sa')
        self.calendar_layout.add_widget(Builder.load_string(th1))
        self.calendar_layout.add_widget(Builder.load_string(th2))
        self.calendar_layout.add_widget(Builder.load_string(th3))
        self.calendar_layout.add_widget(Builder.load_string(th4))
        self.calendar_layout.add_widget(Builder.load_string(th5))
        self.calendar_layout.add_widget(Builder.load_string(th6))
        self.calendar_layout.add_widget(Builder.load_string(th7))
        if year_dates[selected_month]:
            for month in year_dates[selected_month]:
                for week in month:
                    for day in week:
                        if day[0] > 0:
                            check_date_string = '{}-{}-{} 00:00:00'.format(self.year,
                                                                           Job.date_leading_zeroes(self.month),
                                                                           Job.date_leading_zeroes(day[0]))
                            today_base = datetime.datetime.strptime(check_date_string, "%Y-%m-%d %H:%M:%S")
                            check_date = today_base.timestamp()
                            dow_check = today_base.strftime("%w")
                            # rule #1 remove all past dates so users cannot set a due date previous to today
                            if check_date < check_today:
                                item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                              disabled=True)
                            elif int(store_hours[int(dow_check)]['status']) > 1:  # check to see if business is open
                                if check_date == check_today:
                                    item = Factory.CalendarButton(text="[color=37FDFC][b]{}[/b][/color]".format(day[0]),
                                                                  background_color=(0, 0.50196078, 0.50196078, 1),
                                                                  background_normal='',
                                                                  on_release=partial(self.select_due_date, today_base))
                                elif check_date == check_due_date:
                                    item = Factory.CalendarButton(text="[color=008080][b]{}[/b][/color]".format(day[0]),
                                                                  background_color=(
                                                                      0.2156862, 0.9921568, 0.98823529, 1),
                                                                  background_normal='',
                                                                  on_release=partial(self.select_due_date, today_base))
                                elif check_today < check_date < check_due_date:
                                    item = Factory.CalendarButton(text="[color=008080][b]{}[/b][/color]".format(day[0]),
                                                                  background_color=(0.878431372549020, 1, 1, 1),
                                                                  background_normal='',
                                                                  on_release=partial(self.select_due_date, today_base))
                                else:
                                    item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                                  on_release=partial(self.select_due_date, today_base))
                            else:  # store is closed
                                item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                              disabled=True)
                        else:
                            item = Factory.CalendarButton(disabled=True)
                        self.calendar_layout.add_widget(item)

    def prev_month(self, *args, **kwargs):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.month_button.text = '{}'.format(vars.month_by_number(self.month))
        self.year_button.text = '{}'.format(self.year)
        self.create_calendar_table()

    def next_month(self, *args, **kwargs):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.month_button.text = '{}'.format(vars.month_by_number(self.month))
        self.year_button.text = '{}'.format(self.year)
        self.create_calendar_table()

    def select_calendar_month(self, month, *args, **kwargs):
        self.month = month
        self.create_calendar_table()

    def select_calendar_year(self, year, *args, **kwargs):
        self.year = year
        self.create_calendar_table()

    def select_due_date(self, selected_date, *args, **kwargs):
        store_hours = Company().get_store_hours(vars.COMPANY_ID)

        dow = int(selected_date.strftime("%w"))
        turn_around_hour = store_hours[dow]['due_hour'] if 'due_hour' in store_hours[dow] else '4'
        turn_around_minutes = store_hours[dow]['due_minutes'] if 'due_minutes' in store_hours[dow] else '00'
        turn_around_ampm = store_hours[dow]['due_ampm'] if 'due_ampm' in store_hours[dow] else 'pm'
        date_string = '{} {}:{}:00'.format(selected_date.strftime("%Y-%m-%d"),
                                           turn_around_hour if turn_around_ampm == 'am' else int(turn_around_hour) + 12,
                                           turn_around_minutes)
        self.due_date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        self.due_date_string = '{}'.format(self.due_date.strftime('%a %m/%d %I:%M%p'))
        self.quick_box.ids.quick_due_date.text = self.due_date_string
        self.create_calendar_table()

    def quick_print(self, *args, **kwargs):
        popup = Popup()
        popup.size_hint = (None, None)
        popup.size = (800, 600)
        popup.title = 'Quick Drop Print Selection'
        layout = BoxLayout(orientation="vertical",
                           size_hint=(1, 1))
        inner_layout_1 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.7))
        no_copy = Button(text="Store Copy Only",
                         on_press=self.quick_print_store_copy,
                         on_release=popup.dismiss)
        both = Button(text="Print Both",
                      on_press=self.quick_print_both,
                      on_release=popup.dismiss)
        inner_layout_1.add_widget(no_copy)
        inner_layout_1.add_widget(both)
        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.3))
        cancel = Button(text="cancel",
                        on_release=popup.dismiss)
        inner_layout_2.add_widget(cancel)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()
        pass

    def quick_print_store_copy(self, *args, **kwargs):
        # save the invoice
        invoices = Invoice()
        invoices.company_id = vars.COMPANY_ID
        invoices.quantity = self.quick_box.ids.quick_count.text
        invoices.pretax = 0
        invoices.tax = 0
        invoices.total = 0
        invoices.customer_id = vars.CUSTOMER_ID
        invoices.status = 1
        invoices.due_date = self.due_date.strftime('%Y-%m-%d %H:%M:%S')
        invoices.memo = self.quick_box.ids.quick_invoice_memo.text
        if invoices.add():
            # save the invoices to the db and return the proper invoice_ids
            run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
            try:
                run_sync.start()
            finally:
                run_sync.join()
                print('sync now finished')

            # print invoices
            if vars.EPSON:
                pr = Printer()
                companies = Company()
                comps = companies.where({'company_id': vars.COMPANY_ID}, set=True)

                if comps:
                    for company in comps:
                        companies.id = company['id']
                        companies.company_id = company['company_id']
                        companies.name = company['name']
                        companies.street = company['street']
                        companies.suite = company['suite']
                        companies.city = company['city']
                        companies.state = company['state']
                        companies.zip = company['zip']
                        companies.email = company['email']
                        companies.phone = company['phone']
                customers = User()
                custs = customers.where({'user_id': vars.CUSTOMER_ID}, set=True)
                if custs:
                    for user in custs:
                        customers.id = user['id']
                        customers.user_id = user['user_id']
                        customers.company_id = user['company_id']
                        customers.username = user['username']
                        customers.first_name = user['first_name'].upper() if user['first_name'] else ''
                        customers.last_name = user['last_name']
                        customers.street = user['street']
                        customers.suite = user['suite']
                        customers.city = user['city']
                        customers.state = user['state']
                        customers.zipcode = user['zipcode']
                        customers.email = user['email']
                        customers.phone = user['phone']
                        customers.intercom = user['intercom']
                        customers.concierge_name = user['concierge_name']
                        customers.concierge_number = user['concierge_number']
                        customers.special_instructions = user['special_instructions']
                        customers.shirt_old = user['shirt_old']
                        customers.shirt = user['shirt']
                        customers.delivery = user['delivery']
                        customers.profile_id = user['profile_id']
                        customers.payment_status = user['payment_status']
                        customers.payment_id = user['payment_id']
                        customers.token = user['token']
                        customers.api_token = user['api_token']
                        customers.reward_status = user['reward_status']
                        customers.reward_points = user['reward_points']
                        customers.account = user['account']
                        customers.starch = user['starch']
                        customers.important_memo = user['important_memo']
                        customers.invoice_memo = user['invoice_memo']
                        customers.password = user['password']
                        customers.role_id = user['role_id']
                        customers.remember_token = user['remember_token']
                vars.EPSON.write(pr.pcmd('TXT_ALIGN_CT'))
                vars.EPSON.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                             invert=False, smooth=False, flip=False))
                vars.EPSON.write("QUICK DROP - STORE COPY\n")
                vars.EPSON.write("{}\n".format(companies.name))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write("{}\n".format(companies.street))
                vars.EPSON.write("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))

                vars.EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
                vars.EPSON.write("{}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                vars.EPSON.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                             invert=False, smooth=False, flip=False))
                padded_customer_id = '{0:05d}'.format(vars.CUSTOMER_ID)
                vars.EPSON.write("{}\n".format(padded_customer_id))

                # Print barcode
                vars.EPSON.write(pr.pcmd_barcode(str(padded_customer_id)))

                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('{}\n'.format(Job.make_us_phone(customers.phone)))
                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('-----------------------------------------\n')

                vars.EPSON.write(pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                             invert=False, smooth=False, flip=False))
                vars.EPSON.write(
                    '{} PCS\n'.format(
                        self.quick_box.ids.quick_count.text if self.quick_box.ids.quick_count.text else '0'))
                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('-----------------------------------------\n')
                if self.quick_box.ids.quick_invoice_memo.text:
                    vars.EPSON.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                                 invert=False, smooth=False, flip=False))
                    vars.EPSON.write('{}\n'.format(self.quick_box.ids.quick_invoice_memo.text))

                vars.EPSON.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=1, density=1,
                                             invert=False, smooth=False, flip=False))
                # Cut paper
                vars.EPSON.write('\n\n\n\n\n\n')
                vars.EPSON.write(pr.pcmd('PARTIAL_CUT'))


            else:
                popup = Popup()
                popup.title = 'Printer Error'
                content = KV.popup_alert('Could not find usb.')
                popup.content = Builder.load_string(content)
                popup.open()
                # Beep Sound
                sys.stdout.write('\a')
                sys.stdout.flush()


        else:
            popup = Popup()
            popup.title = 'Error!'
            popup.size_hint = None, None
            popup.size = 800, 600
            content = KV.popup_alert(msg="Could not save quick drop! Please try again!")
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()

            pass

        self.main_popup.dismiss()
        self.customer_select(vars.CUSTOMER_ID)

    def quick_print_both(self, *args, **kwargs):
        # save the invoice
        invoices = Invoice()
        invoices.company_id = vars.COMPANY_ID
        invoices.quantity = self.quick_box.ids.quick_count.text
        invoices.pretax = 0
        invoices.tax = 0
        invoices.total = 0
        invoices.customer_id = vars.CUSTOMER_ID
        invoices.status = 1
        invoices.due_date = self.due_date.strftime('%Y-%m-%d %H:%M:%S')
        invoices.memo = self.quick_box.ids.quick_invoice_memo.text
        if invoices.add():
            # save the invoices to the db and return the proper invoice_ids
            run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
            try:
                run_sync.start()
            finally:
                run_sync.join()
                print('sync now finished')

            # print invoices
            if vars.EPSON:
                pr = Printer()
                companies = Company()
                comps = companies.where({'company_id': vars.COMPANY_ID}, set=True)

                if comps:
                    for company in comps:
                        companies.id = company['id']
                        companies.company_id = company['company_id']
                        companies.name = company['name']
                        companies.street = company['street']
                        companies.suite = company['suite']
                        companies.city = company['city']
                        companies.state = company['state']
                        companies.zip = company['zip']
                        companies.email = company['email']
                        companies.phone = company['phone']
                customers = User()
                custs = customers.where({'user_id': vars.CUSTOMER_ID}, set=True)
                if custs:
                    for user in custs:
                        customers.id = user['id']
                        customers.user_id = user['user_id']
                        customers.company_id = user['company_id']
                        customers.username = user['username']
                        customers.first_name = user['first_name'].upper() if user['first_name'] else ''
                        customers.last_name = user['last_name']
                        customers.street = user['street']
                        customers.suite = user['suite']
                        customers.city = user['city']
                        customers.state = user['state']
                        customers.zipcode = user['zipcode']
                        customers.email = user['email']
                        customers.phone = user['phone']
                        customers.intercom = user['intercom']
                        customers.concierge_name = user['concierge_name']
                        customers.concierge_number = user['concierge_number']
                        customers.special_instructions = user['special_instructions']
                        customers.shirt_old = user['shirt_old']
                        customers.shirt = user['shirt']
                        customers.delivery = user['delivery']
                        customers.profile_id = user['profile_id']
                        customers.payment_status = user['payment_status']
                        customers.payment_id = user['payment_id']
                        customers.token = user['token']
                        customers.api_token = user['api_token']
                        customers.reward_status = user['reward_status']
                        customers.reward_points = user['reward_points']
                        customers.account = user['account']
                        customers.starch = user['starch']
                        customers.important_memo = user['important_memo']
                        customers.invoice_memo = user['invoice_memo']
                        customers.password = user['password']
                        customers.role_id = user['role_id']
                        customers.remember_token = user['remember_token']
                vars.EPSON.write(pr.pcmd('TXT_ALIGN_CT'))
                vars.EPSON.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                             invert=False, smooth=False, flip=False))
                vars.EPSON.write("QUICK DROP\n")
                vars.EPSON.write("{}\n".format(companies.name))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write("{}\n".format(companies.street))
                vars.EPSON.write("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))

                vars.EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
                vars.EPSON.write("{}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                vars.EPSON.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                             invert=False, smooth=False, flip=False))
                padded_customer_id = '{0:05d}'.format(vars.CUSTOMER_ID)
                vars.EPSON.write("{}\n".format(padded_customer_id))

                # Print barcode
                vars.EPSON.write(pr.pcmd_barcode(str(padded_customer_id)))

                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('{}\n'.format(Job.make_us_phone(customers.phone)))
                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('-----------------------------------------\n')

                vars.EPSON.write(pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                             invert=False, smooth=False, flip=False))
                vars.EPSON.write('{} PCS\n'.format(
                    self.quick_box.ids.quick_count.text if self.quick_box.ids.quick_count.text else '0'))
                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('-----------------------------------------\n')
                if self.quick_box.ids.quick_invoice_memo.text:
                    vars.EPSON.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                                 invert=False, smooth=False, flip=False))
                    vars.EPSON.write('{}\n'.format(self.quick_box.ids.quick_invoice_memo.text))

                vars.EPSON.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=1, density=1,
                                             invert=False, smooth=False, flip=False))
                # Cut paper
                vars.EPSON.write('\n\n\n\n\n\n')
                vars.EPSON.write(pr.pcmd('PARTIAL_CUT'))

                # SECOND Copy
                vars.EPSON.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                             invert=False, smooth=False, flip=False))
                vars.EPSON.write("QUICK DROP - STORE COPY\n")
                vars.EPSON.write("{}\n".format(companies.name))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write("{}\n".format(companies.street))
                vars.EPSON.write("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))

                vars.EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
                vars.EPSON.write("{}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                vars.EPSON.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                vars.EPSON.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                             invert=False, smooth=False, flip=False))
                padded_customer_id = '{0:05d}'.format(vars.CUSTOMER_ID)
                vars.EPSON.write("{}\n".format(padded_customer_id))

                # Print barcode
                vars.EPSON.write(pr.pcmd_barcode(str(padded_customer_id)))

                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('{}\n'.format(Job.make_us_phone(customers.phone)))
                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('-----------------------------------------\n')

                vars.EPSON.write(pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                             invert=False, smooth=False, flip=False))
                vars.EPSON.write(
                    '{} PCS\n'.format(
                        self.quick_box.ids.quick_count.text if self.quick_box.ids.quick_count.text else '0'))
                vars.EPSON.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                vars.EPSON.write('-----------------------------------------\n')
                if self.quick_box.ids.quick_invoice_memo.text:
                    vars.EPSON.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                                 invert=False, smooth=False, flip=False))
                    vars.EPSON.write('{}\n'.format(self.quick_box.ids.quick_invoice_memo.text))

                vars.EPSON.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=1, density=1,
                                             invert=False, smooth=False, flip=False))
                # Cut paper
                vars.EPSON.write('\n\n\n\n\n\n')
                vars.EPSON.write(pr.pcmd('PARTIAL_CUT'))

            else:
                popup = Popup()
                popup.title = 'Printer Error'
                content = KV.popup_alert('Could not find usb.')
                popup.content = Builder.load_string(content)
                popup.open()
                # Beep Sound
                sys.stdout.write('\a')
                sys.stdout.flush()

        else:
            popup = Popup()
            popup.title = 'Error!'
            popup.size_hint = None, None
            popup.size = 800, 600
            content = KV.popup_alert(msg="Could not save quick drop! Please try again!")
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()

        self.main_popup.dismiss()
        self.customer_select(vars.CUSTOMER_ID)

    def reprint_invoice(self, type, *args, **kwargs):
        if vars.INVOICE_ID:
            # print invoices
            if vars.EPSON:
                pr = Printer()
                companies = Company()
                comps = companies.where({'company_id': vars.COMPANY_ID}, set=True)

                if comps:
                    for company in comps:
                        companies.id = company['id']
                        companies.company_id = company['company_id']
                        companies.name = company['name']
                        companies.street = company['street']
                        companies.suite = company['suite']
                        companies.city = company['city']
                        companies.state = company['state']
                        companies.zip = company['zip']
                        companies.email = company['email']
                        companies.phone = Job.make_us_phone(company['phone'])
                customers = User()
                custs = customers.where({'user_id': vars.CUSTOMER_ID}, set=True)
                if custs:
                    for user in custs:
                        customers.id = user['id']
                        customers.user_id = user['user_id']
                        customers.company_id = user['company_id']
                        customers.username = user['username']
                        customers.first_name = user['first_name'].upper() if user['first_name'] else ''
                        customers.last_name = user['last_name']
                        customers.street = user['street']
                        customers.suite = user['suite']
                        customers.city = user['city']
                        customers.state = user['state']
                        customers.zipcode = user['zipcode']
                        customers.email = user['email']
                        customers.phone = Job.make_us_phone(user['phone'])
                        customers.intercom = user['intercom']
                        customers.concierge_name = user['concierge_name']
                        customers.concierge_number = user['concierge_number']
                        customers.special_instructions = user['special_instructions']
                        customers.shirt_old = user['shirt_old']
                        customers.shirt = user['shirt']
                        customers.delivery = user['delivery']
                        customers.profile_id = user['profile_id']
                        customers.payment_status = user['payment_status']
                        customers.payment_id = user['payment_id']
                        customers.token = user['token']
                        customers.api_token = user['api_token']
                        customers.reward_status = user['reward_status']
                        customers.reward_points = user['reward_points']
                        customers.account = user['account']
                        customers.starch = user['starch']
                        customers.important_memo = user['important_memo']
                        customers.invoice_memo = user['invoice_memo']
                        customers.password = user['password']
                        customers.role_id = user['role_id']
                        customers.remember_token = user['remember_token']
                invoices = Invoice()
                invs = invoices.where({'invoice_id': vars.INVOICE_ID})
                if invs:
                    for invoice in invs:
                        invoice_quantity = invoice['quantity']
                        invoice_subtotal = invoice['pretax']
                        invoice_tax = invoice['tax']
                        invoice_total = invoice['total']

                        try:
                            invoice_due_date = datetime.datetime.strptime(invoice['due_date'], "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            invoice_due_date = datetime.datetime.now()

                invoice_items = InvoiceItem()
                inv_items = invoice_items.where({'invoice_id': vars.INVOICE_ID})
                colors = {}
                if inv_items:
                    for invoice_item in inv_items:
                        item_id = invoice_item['item_id']
                        colors[item_id] = {}
                print_sync_invoice = {vars.INVOICE_ID: {}}
                if inv_items:
                    for invoice_item in inv_items:
                        item_id = invoice_item['item_id']
                        items = InventoryItem().where({'item_id': item_id})
                        if items:
                            for item in items:
                                item_name = item['name']
                                inventory_id = item['inventory_id']
                        else:
                            item_name = None
                            inventory_id = None

                        inventories = Inventory()
                        invs = inventories.where({'inventory_id': inventory_id})
                        if invs:
                            if invs:
                                for inventory in invs:
                                    inventory_init = inventory['name'][:1].capitalize()
                                    laundry = inventory['laundry']
                            else:
                                inventory_init = ''
                                laundry = 0

                        display_name = '{} ({})'.format(item_name, vars.get_starch_by_code(
                            customers.starch)) if laundry else item_name

                        item_color = invoice_item['color']
                        if item_id in colors:
                            if item_color in colors[item_id]:
                                colors[item_id][item_color] += 1
                            else:
                                colors[item_id][item_color] = 1
                        item_memo = invoice_item['memo']
                        item_subtotal = invoice_item['pretax']
                        if vars.INVOICE_ID in print_sync_invoice:
                            if item_id in print_sync_invoice[vars.INVOICE_ID]:
                                print_sync_invoice[vars.INVOICE_ID][item_id]['item_price'] += item_subtotal
                                print_sync_invoice[vars.INVOICE_ID][item_id]['qty'] += 1
                                if item_memo:
                                    print_sync_invoice[vars.INVOICE_ID][item_id]['memos'].append(item_memo)

                                if item_id in colors:
                                    print_sync_invoice[vars.INVOICE_ID][item_id]['colors'] = colors[item_id]
                                else:
                                    print_sync_invoice[vars.INVOICE_ID][item_id]['colors'] = []
                            else:
                                print_sync_invoice[vars.INVOICE_ID][item_id] = {
                                    'item_id': item_id,
                                    'type': inventory_init,
                                    'name': display_name,
                                    'item_price': item_subtotal,
                                    'qty': 1,
                                    'memos': [item_memo] if item_memo else [],
                                    'colors': {item_color: 1}
                                }
                now = datetime.datetime.now()
                if type == 2:
                    vars.EPSON.write(pr.pcmd('TXT_ALIGN_CT'))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                    density=5, invert=False, smooth=False, flip=False))
                    vars.EPSON.write("::CUSTOMER::\n")
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write("{}\n".format(companies.name))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write("{}\n".format(companies.street))
                    vars.EPSON.write("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                    invert=False, smooth=False, flip=False))

                    vars.EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
                    vars.EPSON.write("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write("READY BY: {}\n\n".format(invoice_due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                    vars.EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                    invert=False, smooth=False, flip=False))
                    padded_customer_id = '{0:05d}'.format(vars.CUSTOMER_ID)
                    vars.EPSON.write("{}\n".format(padded_customer_id))

                    # Print barcode
                    vars.EPSON.write(pr.pcmd_barcode(str(padded_customer_id)))

                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write("{}\n".format(Job.make_us_phone(customers.phone)))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('-----------------------------------------\n')

                    if vars.INVOICE_ID in print_sync_invoice:
                        item_type = 'D'
                        for item_id, invoice_item in print_sync_invoice[vars.INVOICE_ID].items():
                            item_name = invoice_item['name']
                            item_price = invoice_item['item_price']
                            item_qty = invoice_item['qty']
                            item_color_string = []
                            item_memo = invoice_item['memos']
                            item_type = invoice_item['type']
                            if 'colors' in invoice_item:
                                for color_name, color_qty in invoice_item['colors'].items():
                                    if color_name:
                                        item_color_string.append('{}-{}'.format(color_qty, color_name))
                            vars.EPSON.write('{} {}   {}\n'.format(item_type, item_qty, item_name))

                            if len(item_memo) > 0:
                                vars.EPSON.write(pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                             height=1,
                                                             density=5, invert=False, smooth=False, flip=False))
                                vars.EPSON.write('     {}\n'.format('/ '.join(item_memo)))
                            if len(item_color_string) > 0:
                                vars.EPSON.write(pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                             height=1,
                                                             density=5, invert=False, smooth=False, flip=False))
                                vars.EPSON.write('     {}\n'.format(', '.join(item_color_string)))

                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('-----------------------------------------\n')
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('{} PCS\n'.format(invoice_quantity))
                    vars.EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                    invert=False, smooth=False, flip=False))
                    vars.EPSON.write('-----------------------------------------\n')

                    if customers.invoice_memo:
                        vars.EPSON.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                        invert=False, smooth=False, flip=False))
                        vars.EPSON.write('{}\n'.format(customers.invoice_memo))
                    # Cut paper
                    vars.EPSON.write('\n\n\n\n\n\n')
                    vars.EPSON.write(pr.pcmd('PARTIAL_CUT'))

                if type == 1:
                    # Print store copies
                    if print_sync_invoice:  # if invoices synced
                        for invoice_id, item_id in print_sync_invoice.items():
                            item_type = 'D'
                            if isinstance(invoice_id, str):
                                invoice_id = int(invoice_id)

                            # start invoice
                            vars.EPSON.write(pr.pcmd('TXT_ALIGN_CT'))
                            vars.EPSON.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=5, invert=False, smooth=False, flip=False))
                            vars.EPSON.write("::COPY::\n")
                            vars.EPSON.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write("{}\n".format(companies.name))
                            vars.EPSON.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=5,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
                            vars.EPSON.write("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))
                            vars.EPSON.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2,
                                            density=5,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write(
                                "READY BY: {}\n\n".format(invoice_due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                            vars.EPSON.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write("{}\n".format('{0:06d}'.format(invoice_id)))
                            # Print barcode
                            vars.EPSON.write(pr.pcmd_barcode('{}'.format(str('{0:06d}'.format(invoice_id)))))

                            vars.EPSON.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3,
                                            density=6,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write(
                                '{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                            vars.EPSON.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=2,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write("{}\n".format(Job.make_us_phone(customers.phone)))
                            vars.EPSON.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=1,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write('-----------------------------------------\n')

                            if invoice_id in print_sync_invoice:
                                for item_id, invoice_item in print_sync_invoice[invoice_id].items():
                                    item_name = invoice_item['name']
                                    item_price = invoice_item['item_price']
                                    item_qty = invoice_item['qty']
                                    item_color_string = []
                                    item_memo = invoice_item['memos']
                                    item_type = invoice_item['type']
                                    if 'colors' in invoice_item:
                                        for color_name, color_qty in invoice_item['colors'].items():
                                            if color_name:
                                                item_color_string.append('{}-{}'.format(color_qty, color_name))
                                    string_length = len(item_type) + len(str(item_qty)) + len(item_name) + len(
                                        vars.us_dollar(item_price)) + 4
                                    string_offset = 42 - string_length if 42 - string_length > 0 else 0
                                    vars.EPSON.write('{} {}   {}{}{}\n'.format(item_type,
                                                                               item_qty,
                                                                               item_name,
                                                                               ' ' * string_offset,
                                                                               vars.us_dollar(item_price)))

                                    if len(item_memo) > 0:
                                        vars.EPSON.write(
                                            pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                        height=1,
                                                        density=5, invert=False, smooth=False, flip=False))
                                        vars.EPSON.write('     {}\n'.format('/ '.join(item_memo)))
                                    if len(item_color_string) > 0:
                                        vars.EPSON.write(
                                            pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                        height=1,
                                                        density=5, invert=False, smooth=False, flip=False))
                                        vars.EPSON.write('     {}\n'.format(', '.join(item_color_string)))

                            vars.EPSON.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=1,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write('-----------------------------------------\n')
                            vars.EPSON.write(
                                pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write('{} PCS\n'.format(invoice_quantity))
                            vars.EPSON.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=1,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write('-----------------------------------------\n')
                            vars.EPSON.write(
                                pr.pcmd_set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                            invert=False, smooth=False, flip=False))
                            vars.EPSON.write('    SUBTOTAL:')
                            vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                            string_length = len(vars.us_dollar(invoice_subtotal))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.write('{}{}\n'.format(' ' * string_offset, vars.us_dollar(invoice_subtotal)))
                            vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                            vars.EPSON.write('         TAX:')
                            string_length = len(vars.us_dollar(invoice_tax))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                            vars.EPSON.write('{}{}\n'.format(' ' * string_offset, vars.us_dollar(invoice_tax)))
                            vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                            vars.EPSON.write('       TOTAL:')
                            vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                            string_length = len(vars.us_dollar(invoice_total))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.write('{}{}\n'.format(' ' * string_offset,
                                                             vars.us_dollar(invoice_total)))
                            vars.EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                            vars.EPSON.write('     BALANCE:')
                            string_length = len(vars.us_dollar(invoice_total))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.write('{}{}\n\n'.format(' ' * string_offset, vars.us_dollar(invoice_total)))
                            if customers.invoice_memo:
                                vars.EPSON.write(
                                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                                invert=False, smooth=False, flip=False))
                                vars.EPSON.write('{}\n'.format(customers.invoice_memo))
                            if item_type == 'L':
                                # get customer mark
                                marks = Custid()
                                marks_list = marks.where({'customer_id': vars.CUSTOMER_ID, 'status': 1})
                                if marks_list:
                                    m_list = []
                                    for mark in marks_list:
                                        m_list.append(mark['mark'])
                                    vars.EPSON.write(
                                        pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=3, height=4,
                                                    density=8, invert=False, smooth=False, flip=False))
                                    vars.EPSON.write('{}\n\n'.format(', '.join(m_list)))

                            # Cut paper
                            vars.EPSON.write('\n\n\n\n\n\n')
                            vars.EPSON.write(pr.pcmd('PARTIAL_CUT'))
            else:
                popup = Popup()
                popup.title = 'Printer Error'
                content = KV.popup_alert('No printer found. Please try again.')
                popup.content = Builder.load_string(content)
                popup.open()
        else:
            popup = Popup()
            popup.title = 'Reprint Error'
            content = KV.popup_alert('Please select an invoice.')
            popup.content = Builder.load_string(content)
            popup.open()

    def print_card(self, *args, **kwargs):

        if vars.EPSON:
            pr = Printer()
            companies = Company()
            comps = companies.where({'company_id': vars.COMPANY_ID}, set=True)

            if comps:
                for company in comps:
                    companies.id = company['id']
                    companies.company_id = company['company_id']
                    companies.name = company['name']
                    companies.street = company['street']
                    companies.suite = company['suite']
                    companies.city = company['city']
                    companies.state = company['state']
                    companies.zip = company['zip']
                    companies.email = company['email']
                    companies.phone = Job.make_us_phone(company['phone'])
            customers = User()
            custs = customers.where({'user_id': vars.CUSTOMER_ID}, set=True)
            if custs:
                for user in custs:
                    customers.id = user['id']
                    customers.user_id = user['user_id']
                    customers.company_id = user['company_id']
                    customers.username = user['username']
                    customers.first_name = user['first_name'].upper() if user['first_name'] else ''
                    customers.last_name = user['last_name']
                    customers.street = user['street']
                    customers.suite = user['suite']
                    customers.city = user['city']
                    customers.state = user['state']
                    customers.zipcode = user['zipcode']
                    customers.email = user['email']
                    customers.phone = Job.make_us_phone(user['phone'])
                    customers.intercom = user['intercom']
                    customers.concierge_name = user['concierge_name']
                    customers.concierge_number = user['concierge_number']
                    customers.special_instructions = user['special_instructions']
                    customers.shirt_old = user['shirt_old']
                    customers.shirt = user['shirt']
                    customers.delivery = user['delivery']
                    customers.profile_id = user['profile_id']
                    customers.payment_status = user['payment_status']
                    customers.payment_id = user['payment_id']
                    customers.token = user['token']
                    customers.api_token = user['api_token']
                    customers.reward_status = user['reward_status']
                    customers.reward_points = user['reward_points']
                    customers.account = user['account']
                    customers.starch = user['starch']
                    customers.important_memo = user['important_memo']
                    customers.invoice_memo = user['invoice_memo']
                    customers.password = user['password']
                    customers.role_id = user['role_id']
                    customers.remember_token = user['remember_token']

            now = datetime.datetime.now()
            vars.EPSON.write(pr.pcmd('TXT_ALIGN_CT'))
            vars.EPSON.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                         invert=False, smooth=False, flip=False))
            vars.EPSON.write("{}\n".format(companies.name))
            vars.EPSON.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                         invert=False, smooth=False, flip=False))
            vars.EPSON.write("{}\n".format(companies.street))
            vars.EPSON.write("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
            vars.EPSON.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                         invert=False, smooth=False, flip=False))

            vars.EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
            vars.EPSON.write("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))

            vars.EPSON.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                         invert=False, smooth=False, flip=False))
            # Print barcode
            padded_customer_id = '{0:05d}'.format(vars.CUSTOMER_ID)
            vars.EPSON.write("{}\n".format(padded_customer_id))
            vars.EPSON.write(pr.pcmd_barcode(str(padded_customer_id)))
            vars.EPSON.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                         invert=False, smooth=False, flip=False))
            vars.EPSON.write('{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

            vars.EPSON.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                         invert=False, smooth=False, flip=False))
            vars.EPSON.write("{}\n".format(Job.make_us_phone(customers.phone)))
            vars.EPSON.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                         invert=False, smooth=False, flip=False))

            vars.EPSON.write('-----------------------------------------\n')
            # Cut paper
            vars.EPSON.write('\n\n\n\n\n\n')
            vars.EPSON.write(pr.pcmd('PARTIAL_CUT'))

        else:
            popup = Popup()
            popup.title = 'Printer Error'
            content = KV.popup_alert('No printer found. Please try again.')
            popup.content = Builder.load_string(content)
            popup.open()

    def reprint_tags(self, *args, **kwargs):
        popup = Popup()
        popup.title = 'Tag Reprint'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='vertical',
                                   size_hint=(1, 0.9))
        self.tags_grid = Factory.TagsGrid()
        invitems = InvoiceItem().where({'invoice_id': vars.INVOICE_ID})
        if invitems:
            for ii in invitems:
                invoice_items_id = ii['invoice_items_id']
                iitem_id = ii['item_id']
                tags_to_print = 1
                try:
                    tags_to_print = InventoryItem().tagsToPrint(iitem_id)
                except TypeError:
                    tags_to_print = 1
                item_name = InventoryItem().getItemName(iitem_id)
                item_color = ii['color']
                item_memo = ii['memo']
                trtd1 = Button(text=str(invoice_items_id),
                               on_release=partial(self.select_tag, invoice_items_id))
                trtd2 = Button(text=str(item_name),
                               on_release=partial(self.select_tag, invoice_items_id))
                trtd3 = Button(text=str(item_color),
                               on_release=partial(self.select_tag, invoice_items_id))
                trtd4 = Button(text=str(item_memo),
                               on_release=partial(self.select_tag, invoice_items_id))
                trtd5 = Button(text=str(tags_to_print),
                               on_release=partial(self.select_tag, invoice_items_id))
                self.tags_grid.ids.tags_table.add_widget(trtd1)
                self.tags_grid.ids.tags_table.add_widget(trtd2)
                self.tags_grid.ids.tags_table.add_widget(trtd3)
                self.tags_grid.ids.tags_table.add_widget(trtd4)
                self.tags_grid.ids.tags_table.add_widget(trtd5)
        inner_layout_1.add_widget(self.tags_grid)
        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="Cancel",
                               on_release=popup.dismiss)
        print_all_button = Button(text="Print All",
                                  on_press=popup.dismiss,
                                  on_release=self.print_all_tags)
        print_selected_button = Button(text="Print Selected",
                                       on_press=popup.dismiss,
                                       on_release=self.print_selected_tags)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(print_all_button)
        inner_layout_2.add_widget(print_selected_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def select_tag(self, item_id, *args, **kwargs):

        if item_id in self.selected_tags_list:
            # remove the tag
            self.selected_tags_list.remove(item_id)
        else:
            # add the tag
            self.selected_tags_list.append(item_id)

        self.tags_grid.ids.tags_table.clear_widgets()
        th1 = Factory.TagsGridHeaders(text="[color=#000000]ID[/color]")
        th2 = Factory.TagsGridHeaders(text="[color=#000000]Item[/color]")
        th3 = Factory.TagsGridHeaders(text="[color=#000000]Color[/color]")
        th4 = Factory.TagsGridHeaders(text="[color=#000000]Memo[/color]")
        th5 = Factory.TagsGridHeaders(text="[color=#000000]Tags[/color]")
        self.tags_grid.ids.tags_table.add_widget(th1)
        self.tags_grid.ids.tags_table.add_widget(th2)
        self.tags_grid.ids.tags_table.add_widget(th3)
        self.tags_grid.ids.tags_table.add_widget(th4)
        self.tags_grid.ids.tags_table.add_widget(th5)
        invitems = InvoiceItem().where({'invoice_id': vars.INVOICE_ID})
        if invitems:
            for ii in invitems:
                invoice_items_id = ii['invoice_items_id']
                iitem_id = ii['item_id']
                tags_to_print = InventoryItem().tagsToPrint(iitem_id)
                item_name = InventoryItem().getItemName(iitem_id)
                item_color = ii['color']
                item_memo = ii['memo']
                if invoice_items_id in self.selected_tags_list:
                    trtd1 = Factory.TagsSelectedButton(text=str(invoice_items_id),
                                                       on_release=partial(self.select_tag, invoice_items_id))
                    trtd2 = Factory.TagsSelectedButton(text=str(item_name),
                                                       on_release=partial(self.select_tag, invoice_items_id))
                    trtd3 = Factory.TagsSelectedButton(text=str(item_color),
                                                       on_release=partial(self.select_tag, invoice_items_id))
                    trtd4 = Factory.TagsSelectedButton(text=str(item_memo),
                                                       on_release=partial(self.select_tag, invoice_items_id))
                    trtd5 = Factory.TagsSelectedButton(text=str(tags_to_print),
                                                       on_release=partial(self.select_tag, invoice_items_id))
                else:
                    trtd1 = Button(text=str(invoice_items_id),
                                   on_release=partial(self.select_tag, invoice_items_id))
                    trtd2 = Button(text=str(item_name),
                                   on_release=partial(self.select_tag, invoice_items_id))
                    trtd3 = Button(text=str(item_color),
                                   on_release=partial(self.select_tag, invoice_items_id))
                    trtd4 = Button(text=str(item_memo),
                                   on_release=partial(self.select_tag, invoice_items_id))
                    trtd5 = Button(text=str(tags_to_print),
                                   on_release=partial(self.select_tag, invoice_items_id))
                self.tags_grid.ids.tags_table.add_widget(trtd1)
                self.tags_grid.ids.tags_table.add_widget(trtd2)
                self.tags_grid.ids.tags_table.add_widget(trtd3)
                self.tags_grid.ids.tags_table.add_widget(trtd4)
                self.tags_grid.ids.tags_table.add_widget(trtd5)

        pass

    def print_all_tags(self, *args, **kwargs):
        if vars.INVOICE_ID:
            customers = User()
            custs = customers.where({'user_id': vars.CUSTOMER_ID}, set=True)
            if custs:
                for user in custs:
                    customers.id = user['id']
                    customers.user_id = user['user_id']
                    customers.company_id = user['company_id']
                    customers.username = user['username']
                    customers.first_name = user['first_name'].upper() if user['first_name'] else ''
                    customers.last_name = user['last_name']
                    customers.street = user['street']
                    customers.suite = user['suite']
                    customers.city = user['city']
                    customers.state = user['state']
                    customers.zipcode = user['zipcode']
                    customers.email = user['email']
                    customers.phone = user['phone']
                    customers.intercom = user['intercom']
                    customers.concierge_name = user['concierge_name']
                    customers.concierge_number = user['concierge_number']
                    customers.special_instructions = user['special_instructions']
                    customers.shirt_old = user['shirt_old']
                    customers.shirt = user['shirt']
                    customers.delivery = user['delivery']
                    customers.profile_id = user['profile_id']
                    customers.payment_status = user['payment_status']
                    customers.payment_id = user['payment_id']
                    customers.token = user['token']
                    customers.api_token = user['api_token']
                    customers.reward_status = user['reward_status']
                    customers.reward_points = user['reward_points']
                    customers.account = user['account']
                    customers.starch = user['starch']
                    customers.important_memo = user['important_memo']
                    customers.invoice_memo = user['invoice_memo']
                    customers.password = user['password']
                    customers.role_id = user['role_id']
                    customers.remember_token = user['remember_token']
            invoice_id_str = str(vars.INVOICE_ID)
            invs = Invoice().where({'invoice_id': vars.INVOICE_ID})
            due_date = 'SUN'
            if invs:
                for inv in invs:
                    dt = datetime.datetime.strptime(inv['due_date'], "%Y-%m-%d %H:%M:%S")
                    due_date = dt.strftime('%a').upper()
            invoice_last_four = '{0:04d}'.format(int(invoice_id_str[-4:]))
            text_left = "{} {}".format(invoice_last_four,
                                       due_date)
            text_right = "{} {}".format(due_date,
                                        invoice_last_four)
            text_name = "{}, {}".format(customers.last_name.upper(),
                                        customers.first_name.upper()[:1])
            phone_number = Job.make_us_phone(customers.phone)
            total_length = 32
            text_offset = total_length - len(text_name) - len(phone_number)
            name_number_string = '{}{}{}'.format(text_name, ' ' * text_offset,
                                                 phone_number)

            print('next step')
            invoice_items = InvoiceItem().where({'invoice_id': vars.INVOICE_ID})
            if vars.BIXOLON:

                laundry_to_print = []
                if invoice_items:
                    # vars.BIXOLON.write('\x1b\x40')
                    # vars.BIXOLON.write('\x1b\x6d')
                    for ii in invoice_items:

                        iitem_id = ii['item_id']
                        tags_to_print = InventoryItem().tagsToPrint(iitem_id)
                        item_name = InventoryItem().getItemName(iitem_id)
                        item_color = ii['color']
                        invoice_item_id = ii['invoice_items_id']
                        laundry_tag = InventoryItem().getLaundry(iitem_id)
                        memo_string = ii['memo']
                        if laundry_tag:
                            laundry_to_print.append(invoice_item_id)
                        else:
                            for _ in range(tags_to_print):

                                vars.BIXOLON.write('\x1b!\x30')  # QUAD SIZE
                                vars.BIXOLON.write('{}{}\n'.format(text_left, text_right))
                                vars.BIXOLON.write('\x1b!\x00')
                                vars.BIXOLON.write(name_number_string)
                                vars.BIXOLON.write('\n')
                                vars.BIXOLON.write('{0:06d}'.format(int(invoice_item_id)))
                                vars.BIXOLON.write(' {} {}'.format(item_name, item_color))
                                if memo_string:
                                    vars.BIXOLON.write('\n{}'.format(memo_string))
                                    memo_len = '\n\n\n' if len(
                                        memo_string) <= 32 else '\n\n\n' + '\n' * int(
                                        (len(memo_string)) / 32)
                                    vars.BIXOLON.write(memo_len)
                                    vars.BIXOLON.write('\x1b\x6d')

                                else:

                                    vars.BIXOLON.write('\n\n\n')
                                    vars.BIXOLON.write('\x1b\x6d')


                if len(laundry_to_print) > 0:
                    # vars.BIXOLON.write('\x1b\x40')
                    # vars.BIXOLON.write('\x1b\x6d')
                    laundry_count = len(laundry_to_print)
                    shirt_mark = Custid().getCustomerMark(vars.CUSTOMER_ID)
                    name_text_offset = total_length - len(text_name) - len(text_name)
                    shirt_mark_length = len(shirt_mark)
                    mark_text_offset = 16 - (shirt_mark_length * 2)
                    for i in range(0, laundry_count, 2):
                        start = i
                        end = i + 1

                        invoice_item_id_start = '{0:06d}'.format(int(laundry_to_print[start]))

                        id_offset = total_length - 12

                        try:
                            invoice_item_id_end = '{0:06d}'.format(int(laundry_to_print[end]))
                            name_name_string = '{}{}{}'.format(text_name, ' ' * name_text_offset, text_name)
                            mark_mark_string = '{}{}{}'.format(shirt_mark, ' ' * mark_text_offset, shirt_mark)
                            id_id_string = '{}{}{}'.format(invoice_item_id_start, ' ' * id_offset, invoice_item_id_end)

                        except IndexError:
                            name_name_string = '{}'.format(text_name)
                            mark_mark_string = '{}'.format(shirt_mark)
                            id_id_string = '{}'.format(invoice_item_id_start)

                        vars.BIXOLON.write('\x1b!\x30')  # QUAD SIZE
                        vars.BIXOLON.write(mark_mark_string)
                        vars.BIXOLON.write('\n')
                        vars.BIXOLON.write('\x1b!\x00')
                        vars.BIXOLON.write(name_name_string)
                        vars.BIXOLON.write('\n')
                        vars.BIXOLON.write(id_id_string)

                        vars.BIXOLON.write('\n\n\n\x1b\x6d')

                # FINAL CUT
                vars.BIXOLON.write('\n\n\n\n\n\n')
                vars.BIXOLON.write('\x1b\x6d')

        else:
            popup = Popup()
            popup.title = 'Reprint Error'
            content = KV.popup_alert('Please select an invoice.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()
        pass

    def print_selected_tags(self, *args, **kwargs):
        print(self.selected_tags_list)
        if self.selected_tags_list:
            customers = User()
            custs = customers.where({'user_id': vars.CUSTOMER_ID}, set=True)
            if custs:
                for user in custs:
                    customers.id = user['id']
                    customers.user_id = user['user_id']
                    customers.company_id = user['company_id']
                    customers.username = user['username']
                    customers.first_name = user['first_name'].upper() if user['first_name'] else ''
                    customers.last_name = user['last_name']
                    customers.street = user['street']
                    customers.suite = user['suite']
                    customers.city = user['city']
                    customers.state = user['state']
                    customers.zipcode = user['zipcode']
                    customers.email = user['email']
                    customers.phone = user['phone']
                    customers.intercom = user['intercom']
                    customers.concierge_name = user['concierge_name']
                    customers.concierge_number = user['concierge_number']
                    customers.special_instructions = user['special_instructions']
                    customers.shirt_old = user['shirt_old']
                    customers.shirt = user['shirt']
                    customers.delivery = user['delivery']
                    customers.profile_id = user['profile_id']
                    customers.payment_status = user['payment_status']
                    customers.payment_id = user['payment_id']
                    customers.token = user['token']
                    customers.api_token = user['api_token']
                    customers.reward_status = user['reward_status']
                    customers.reward_points = user['reward_points']
                    customers.account = user['account']
                    customers.starch = user['starch']
                    customers.important_memo = user['important_memo']
                    customers.invoice_memo = user['invoice_memo']
                    customers.password = user['password']
                    customers.role_id = user['role_id']
                    customers.remember_token = user['remember_token']
            invoice_id_str = str(vars.INVOICE_ID)
            invs = Invoice().where({'invoice_id': vars.INVOICE_ID})
            due_date = 'SUN'
            if invs:
                for inv in invs:
                    dt = datetime.datetime.strptime(inv['due_date'], "%Y-%m-%d %H:%M:%S")
                    due_date = dt.strftime('%a').upper()
            invoice_last_four = '{0:04d}'.format(int(invoice_id_str[-4:]))
            text_left = "{} {}".format(invoice_last_four,
                                       due_date)
            text_right = "{} {}".format(due_date,
                                        invoice_last_four)
            text_name = "{}, {}".format(customers.last_name.upper(),
                                        customers.first_name.upper()[:1])
            phone_number = Job.make_us_phone(customers.phone)
            total_length = 32
            text_offset = total_length - len(text_name) - len(phone_number)
            name_number_string = '{}{}{}'.format(text_name, ' ' * text_offset,
                                                 phone_number)
            laundry_to_print = []
            if vars.BIXOLON:
                vars.BIXOLON.write('\x1b\x40')
                vars.BIXOLON.write('\x1b\x6d')
                print('next step')

                for item_id in self.selected_tags_list:

                    inv_items = InvoiceItem().where({'invoice_items_id': item_id})
                    if inv_items:
                        for ii in inv_items:
                            iitem_id = ii['item_id']
                            tags_to_print = InventoryItem().tagsToPrint(iitem_id)
                            item_name = InventoryItem().getItemName(iitem_id)
                            item_color = ii['color']
                            invoice_item_id = ii['invoice_items_id']
                            laundry_tag = InventoryItem().getLaundry(iitem_id)
                            memo_string = ii['memo']
                            if laundry_tag:
                                laundry_to_print.append(invoice_item_id)
                            else:

                                for _ in range(tags_to_print):

                                    vars.BIXOLON.write('\x1b!\x30')  # QUAD SIZE
                                    vars.BIXOLON.write('{}{}\n'.format(text_left, text_right))
                                    vars.BIXOLON.write('\x1b!\x00')
                                    vars.BIXOLON.write(name_number_string)
                                    vars.BIXOLON.write('\n')
                                    vars.BIXOLON.write('{0:06d}'.format(int(invoice_item_id)))
                                    vars.BIXOLON.write(' {} {}'.format(item_name, item_color))
                                    if memo_string:
                                        vars.BIXOLON.write('\n{}'.format(memo_string))
                                        memo_len = '\n\n\n' if len(
                                            memo_string) <= 32 else '\n\n\n' + '\n' * int(
                                            (len(memo_string)) / 32)
                                        vars.BIXOLON.write(memo_len)
                                        vars.BIXOLON.write('\x1b\x6d')

                                    else:

                                        vars.BIXOLON.write('\n\n\n')
                                        vars.BIXOLON.write('\x1b\x6d')
                if len(laundry_to_print) is 0:
                    # FINAL CUT
                    vars.BIXOLON.write('\n\n\n\n\n\n')
                    vars.BIXOLON.write('\x1b\x6d')
                else:

                    laundry_count = len(laundry_to_print)
                    shirt_mark = Custid().getCustomerMark(vars.CUSTOMER_ID)
                    name_text_offset = total_length - len(text_name) - len(text_name)
                    shirt_mark_length = len(shirt_mark)
                    mark_text_offset = 16 - (shirt_mark_length * 2)
                    for i in range(0, laundry_count, 2):
                        start = i
                        end = i + 1

                        invoice_item_id_start = '{0:06d}'.format(int(laundry_to_print[start]))

                        id_offset = total_length - 12

                        try:
                            invoice_item_id_end = '{0:06d}'.format(int(laundry_to_print[end]))
                            name_name_string = '{}{}{}'.format(text_name, ' ' * name_text_offset, text_name)
                            mark_mark_string = '{}{}{}'.format(shirt_mark, ' ' * mark_text_offset, shirt_mark)
                            id_id_string = '{}{}{}'.format(invoice_item_id_start, ' ' * id_offset, invoice_item_id_end)

                        except IndexError:
                            name_name_string = '{}'.format(text_name)
                            mark_mark_string = '{}'.format(shirt_mark)
                            id_id_string = '{}'.format(invoice_item_id_start)

                        vars.BIXOLON.write('\x1b!\x30')  # QUAD SIZE
                        vars.BIXOLON.write(mark_mark_string)
                        vars.BIXOLON.write('\n')
                        vars.BIXOLON.write('\x1b!\x00')
                        vars.BIXOLON.write(name_name_string)
                        vars.BIXOLON.write('\n')
                        vars.BIXOLON.write(id_id_string)

                        vars.BIXOLON.write('\n\n\n\x1b\x6d')

                    # FINAL CUT
                    vars.BIXOLON.write('\n\n\n\n\n\n')
                    vars.BIXOLON.write('\x1b\x6d')
            else:
                popup = Popup()
                popup.title = 'Reprint Error'
                content = KV.popup_alert('Tag Printer is not available.')
                popup.content = Builder.load_string(content)
                popup.open()
                # Beep Sound
                sys.stdout.write('\a')
                sys.stdout.flush()

        else:
            popup = Popup()
            popup.title = 'Reprint Error'
            content = KV.popup_alert('Please select an invoice item to print tag.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()

    def barcode_popup(self):
        #reset data
        self.barcode_save_data = {}

        # Pause Schedule
        SCHEDULER.remove_all_jobs()
        if vars.INVOICE_ID is not None and vars.INVOICE_ID > 0:
            self.main_popup.title = "Setup Barcode to Items"
            layout = BoxLayout(orientation="vertical")

            self.barcode_layout = Factory.ScrollGrid(size_hint=(1,0.8))
            self.barcode_layout.ids.main_table.cols = 2
            th1 = Factory.TagsGridHeaders(text="[color=#000000]Item[/color]")
            th2 = Factory.TagsGridHeaders(text="[color=#000000]Barcode[/color]")
            #create table headers
            self.barcode_layout.ids.main_table.add_widget(th1)
            self.barcode_layout.ids.main_table.add_widget(th2)
            #create tbody rows
            tags = InvoiceItem().get_tags(vars.INVOICE_ID)
            if tags:
                idx = 0
                for tag in tags:
                    idx += 1
                    if tag['color'] is not None and tag['memo'] is not None:
                        color_description = "{} - {}".format(tag['color'],tag['memo'])
                    elif tag['color'] is not None and tag['memo'] is None:
                        color_description = "{}".format(tag['color'])
                    elif tag['color'] is None and tag['memo'] is not None:
                        color_description = "{}".format(tag['memo'])
                    else:
                        color_description = ""
                    item_description = "{} - {}".format(tag['id'],tag['item_name'])

                    td1 = Factory.ReadOnlyLabel(text="{} : {}".format(item_description,color_description))
                    self.barcode_layout.ids.main_table.add_widget(td1)
                    barcode_input = TextForm(multiline= False,
                                             write_tab=False,
                                             text= '' if tag['barcode'] is '' else "{}".format(tag['barcode']))

                    barcode_input.bind(on_text_validate=partial(self.update_barcode,tag['id']))
                    if idx is 1:
                        barcode_input.focus=True
                    self.barcode_layout.ids.main_table.add_widget(barcode_input)
            inner_layout_3 = BoxLayout(orientation="horizontal",
                                       size_hint=(1,0.1))
            cancel_button = Button(text="cancel",
                                   on_release=self.main_popup.dismiss)
            save_button = Button(text="save",
                                 on_release=self.save_barcodes)
            inner_layout_3.add_widget(cancel_button)
            inner_layout_3.add_widget(save_button)

            layout.add_widget(self.barcode_layout)
            layout.add_widget(inner_layout_3)
            self.main_popup.content = layout
            self.main_popup.open()



    def update_barcode(self, item_id, barcode, *args, **kwargs):
        self.barcode_save_data[item_id] = barcode.text

    def save_barcodes(self, *args, **kwargs):
        # save
        t1 = Thread(target=InvoiceItem().set_barcodes, args=[vars.INVOICE_ID,vars.COMPANY_ID,self.barcode_save_data])
        t1.start()

        self.main_popup.dismiss()
        self.barcode_save_data = {}
        vars.SEARCH_RESULTS_STATUS = True
        self.reset()

    def label_popup(self):
        popup = Popup()
        popup.title = "Label Management"
        layout = BoxLayout(orientation="vertical")
        inner_layout_1 = Factory.ScrollGrid()
        inner_layout_1.ids.main_table.cols = 1
        label_form = Factory.BottomLeftFormLabel(text="Label Count")
        self.label_input = Factory.CenterVerticalTextInput()
        tag_form = Factory.BottomLeftFormLabel(text="Tag ID")
        self.tag_input = Factory.CenterVerticalTextInput()
        inner_layout_1.ids.main_table.add_widget(label_form)
        inner_layout_1.ids.main_table.add_widget(self.label_input)
        inner_layout_1.ids.main_table.add_widget(tag_form)
        inner_layout_1.ids.main_table.add_widget(self.tag_input)
        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="cancel",
                               on_release=popup.dismiss)
        print_button = Button(text="Print",
                              on_release=self.print_label)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(print_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def print_label(self, *args, **kwargs):
        if vars.CUSTOMER_ID:
            count = int(self.label_input.text)
            row_mark = (count / 4)
            rows = math.ceil(row_mark) if row_mark > 0 else 0
            labels = []
            users = User().where({'user_id': vars.CUSTOMER_ID})
            name = ''
            if users:
                for user in users:
                    first_name = user['first_name'][1:].capitalize()
                    last_name = user['last_name'].capitalize()
                    name = '{}.{}'.format(first_name,
                                          last_name)

            if rows > 0:
                idx = 0
                for i in range(rows):
                    idx += 1
                    if idx <= count:
                        labels.append([1, 2, 3, 4])
            midx = 0
            for label in labels:
                inititate = '''
    N
    D15
    '''
                content = ''
                a = 345
                b = 330
                c = 310
                close = '''
P1
'''
                for lidx in label:
                    midx += 1
                    if midx <= count:
                        a_horizontal = a - (lidx * 65)
                        b_horizontal = b - (lidx * 65)
                        c_horizontal = c - (lidx * 65)
                        content = '''
A{a},20,1,1,1,1,N,"{name}"
B{b},1,1,1,2,1,20,N,"{cust_id}"
A{c},20,1,1,1,1,N,"{tag}"
'''.format(a=a_horizontal,
           b=b_horizontal,
           c=c_horizontal,
           name=name,
           cust_id=vars.CUSTOMER_ID,
           tag=str(self.tag_input.text))
                    else:

                        final_content = '''
{a}
{b}
{c}
'''.format(a=inititate,
           b=content,
           c=close)
                        vars.ZEBRA.write(final_content)
                        break

                final_content = '''
{a}
{b}
{c}
'''.format(a=inititate,
           b=content,
           c=close)
            vars.ZEBRA.write(final_content)
        else:
            popup = Popup()
            popup.title = 'Label Error'
            content = KV.popup_alert('Please select a customer before printing out a label')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()

    def calculator_popup(self):
        popup = Popup()
        popup.title = 'Calculator'
        layout = BoxLayout(orientation="vertical",
                           size_hint=(1, 1))

        inner_layout_1 = BoxLayout(orientation="vertical",
                                   size_hint=(1, 0.9))
        displays = GridLayout(rows=1,
                              cols=1,
                              size_hint=(1, 0.1))
        self.display_input = Factory.ReadOnlyLabel(text="0",
                                                   markup=True)

        displays.add_widget(self.display_input)
        controls = BoxLayout(orientation="horizontal",
                             size_hint=(1, 0.9))
        control_buttons = GridLayout(rows=4,
                                     cols=4,
                                     size_hint=(0.7, 1))
        btn_9 = Button(text="9",
                       on_release=partial(self.calc_button, '9'))
        btn_8 = Button(text="8",
                       on_release=partial(self.calc_button, '8'))
        btn_7 = Button(text="7",
                       on_release=partial(self.calc_button, '7'))
        btn_6 = Button(text="6",
                       on_release=partial(self.calc_button, '6'))
        btn_5 = Button(text="5",
                       on_release=partial(self.calc_button, '5'))
        btn_4 = Button(text="4",
                       on_release=partial(self.calc_button, '4'))
        btn_3 = Button(text="3",
                       on_release=partial(self.calc_button, '3'))
        btn_2 = Button(text="2",
                       on_release=partial(self.calc_button, '2'))
        btn_1 = Button(text="1",
                       on_release=partial(self.calc_button, '1'))
        btn_0 = Button(text="0",
                       on_release=partial(self.calc_button, '0'))
        btn_00 = Button(text="00",
                        on_release=partial(self.calc_button, '00'))
        btn_dot = Button(text=".",
                         on_release=partial(self.calc_button, '.'))
        btn_add = Button(text="+",
                         on_release=partial(self.calc_button, '+'))
        btn_subtract = Button(text="-",
                              on_release=partial(self.calc_button, '-'))
        btn_multiply = Button(text="*",
                              on_release=partial(self.calc_button, '*'))
        btn_divide = Button(text="/",
                            on_release=partial(self.calc_button, '/'))
        control_buttons.add_widget(btn_7)
        control_buttons.add_widget(btn_8)
        control_buttons.add_widget(btn_9)
        control_buttons.add_widget(btn_add)
        control_buttons.add_widget(btn_4)
        control_buttons.add_widget(btn_5)
        control_buttons.add_widget(btn_6)
        control_buttons.add_widget(btn_subtract)
        control_buttons.add_widget(btn_1)
        control_buttons.add_widget(btn_2)
        control_buttons.add_widget(btn_3)
        control_buttons.add_widget(btn_multiply)
        control_buttons.add_widget(btn_0)
        control_buttons.add_widget(btn_00)
        control_buttons.add_widget(btn_dot)
        control_buttons.add_widget(btn_divide)

        controls.add_widget(control_buttons)

        self.calculator_control_table = Factory.CalculatorGrid()
        controls.add_widget(self.calculator_control_table)

        inner_layout_1.add_widget(displays)
        inner_layout_1.add_widget(controls)

        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="Cancel",
                               on_release=popup.dismiss)
        clear_button = Button(markup=True,
                              text="[color=#FF0000]C[/color]",
                              on_release=self.calc_clear)
        equals_button = Button(markup=True,
                               text="[color=#e5e5e5][b]=[/b][/color]",
                               on_release=self.calc_equals)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(clear_button)
        inner_layout_2.add_widget(equals_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)

        popup.content = layout
        popup.open()

    def calc_button(self, data, *args, **kwargs):

        # process as normal
        if data is '+' or data is '-' or data is '*' or data is '/':

            self.calc_history.append(''.join(self.calc_amount))
            self.calc_history.append(data)
            if self.calc_history[-2] is '' or self.calc_history[-2] is '0':
                del self.calc_history[-1]
                del self.calc_history[-1]
                try:
                    del self.calc_history[-1]
                    self.calc_history.append(data)
                except IndexError:
                    pass

            self.calc_amount = []
            self.calc_update()

        else:
            self.calc_amount.append(data)
            total_base = ''.join(self.calc_amount)
            self.display_input.text = total_base

        total_calculation = ' '.join(self.calc_history)
        print(total_calculation)
        pass

    def calc_equals(self, *args, **kwargs):
        self.calc_history.append(str(self.display_input.text))
        self.calc_amount = []
        self.calc_update()
        self.calc_history = []
        pass

    def calc_update(self, *args, **kwargs):
        # last element in list
        operand = '+'
        # value = 0
        total = 0

        if self.calc_history:
            self.calculator_control_table.ids.summary_table.clear_widgets()
            for data in self.calc_history:
                value = 0
                if data is '+':
                    operand = '+'

                elif data is '-':
                    operand = '-'
                elif data is '*':
                    operand = '*'
                elif data is '/':
                    operand = '/'
                else:
                    value = Decimal(data)
                if operand is '+':
                    total += value
                elif operand is '-':
                    total -= value
                elif operand is '*':
                    total *= value
                else:
                    total /= value if value > 0 else 1

                self.calculator_control_table.ids.summary_table.add_widget(Label(text=str(data)))

                self.display_input.text = str(total)

        pass

    def calc_clear(self, *args, **kwargs):
        self.calc_amount = []
        self.calc_history = []
        self.display_input.text = '0'
        self.calculator_control_table.ids.summary_table.clear_widgets()
        pass

    def delivery_setup(self, *args, **kwargs):
        self.delivery_popup = Popup()
        self.delivery_popup.title = 'Delivery Setup'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = Factory.DeliveryGrid()
        cards_label = Factory.BottomLeftFormLabel(text="[b](1)[/b] Select Card On File",
                                                  markup=True)
        # create cards spinner
        vars.PROFILE_ID = None
        vars.PAYMENT_ID = None
        pro = Profile()
        profiles = pro.where({'user_id': vars.CUSTOMER_ID,
                              'company_id': vars.COMPANY_ID})
        if profiles:
            for profile in profiles:
                vars.PROFILE_ID = profile['profile_id']

            cards_db = Card()
            self.cards = cards_db.collect(vars.COMPANY_ID, vars.PROFILE_ID)
        else:
            self.cards = False
        self.card_string = []
        if self.cards:
            for card in self.cards:
                self.card_string.append("{} {} {}/{}".format(card['card_type'],
                                                             card['last_four'],
                                                             card['exp_month'],
                                                             card['exp_year']))
        self.card_id_spinner = Spinner(
            # default value shown
            text='Select Card',
            # available values
            values=self.card_string,
            # just for positioning in our example
            size_hint_x=1,
            size_hint_y=0.5,
            pos_hint={'center_x': .5, 'center_y': .5})
        self.card_id_spinner.bind(text=self.select_online_card)

        # reset cards on file ids
        self.addresses = Address().where({'user_id': vars.CUSTOMER_ID})
        self.address_string = []
        if self.addresses:
            for address in self.addresses:
                self.address_string.append("{} - {} {}, {} {}".format(address['name'],
                                                                      address['street'],
                                                                      address['city'],
                                                                      address['state'],
                                                                      address['zipcode']))

        self.address_id_spinner = Spinner(
            # default value shown
            text='Select Address',
            # available values
            values=self.address_string,
            # just for positioning in our example
            size_hint_x=1,
            size_hint_y=0.5,
            pos_hint={'center_x': .5, 'center_y': .5})
        self.address_id_spinner.bind(text=self.select_address)

        inner_layout_1.ids.delivery_table.add_widget(cards_label)
        inner_layout_1.ids.delivery_table.add_widget(self.card_id_spinner)
        address_label = Factory.BottomLeftFormLabel(text="[b](2)[/b] Select Delivery Address",
                                                    markup=True)
        inner_layout_1.ids.delivery_table.add_widget(address_label)
        inner_layout_1.ids.delivery_table.add_widget(self.address_id_spinner)
        pickup_label = Factory.BottomLeftFormLabel(text="[b](3)[/b] Pickup?",
                                                   markup=True)
        self.pickup_switch = Switch(active=False)
        self.pickup_switch.bind(active=self.pickup_status)
        inner_layout_1.ids.delivery_table.add_widget(pickup_label)
        inner_layout_1.ids.delivery_table.add_widget(self.pickup_switch)
        pickup_date_label = Factory.BottomLeftFormLabel(text="[b](3a)[/b] Pickup Delivery Date",
                                                        markup=True)
        self.pickup_date_btn = Button(text="Set Pickup Date",
                                      on_release=self.get_pickup_dates,
                                      disabled=True)
        inner_layout_1.ids.delivery_table.add_widget(pickup_date_label)
        inner_layout_1.ids.delivery_table.add_widget(self.pickup_date_btn)

        pickup_time_label = Factory.BottomLeftFormLabel(text="[b](3b)[/b] Pickup Delivery Time",
                                                        markup=True)
        self.pickup_time_spinner = Spinner(
            # default value shown
            text='Select Time',
            # available values
            values=[],
            # just for positioning in our example
            size_hint_x=1,
            size_hint_y=0.5,
            disabled=True,
            pos_hint={'center_x': .5, 'center_y': .5})
        self.pickup_time_spinner.bind(text=self.select_pickup_time)
        inner_layout_1.ids.delivery_table.add_widget(pickup_time_label)
        inner_layout_1.ids.delivery_table.add_widget(self.pickup_time_spinner)

        dropoff_label = Factory.BottomLeftFormLabel(text="[b](4)[/b] Dropoff?",
                                                    markup=True)
        self.dropoff_switch = Switch(active=False)
        self.dropoff_switch.bind(active=self.dropoff_status)
        inner_layout_1.ids.delivery_table.add_widget(dropoff_label)
        inner_layout_1.ids.delivery_table.add_widget(self.dropoff_switch)
        dropoff_date_label = Factory.BottomLeftFormLabel(text="[b](4a)[/b] Dropoff Delivery Date",
                                                         markup=True)
        self.dropoff_date_btn = Button(text="Set Dropoff Date",
                                       on_release=self.get_dropoff_dates,
                                       disabled=True)
        inner_layout_1.ids.delivery_table.add_widget(dropoff_date_label)
        inner_layout_1.ids.delivery_table.add_widget(self.dropoff_date_btn)

        dropoff_time_label = Factory.BottomLeftFormLabel(text="[b](4b[/b] Dropoff Delivery Time",
                                                         markup=True)
        self.dropoff_time_spinner = Spinner(
            # default value shown
            text='Select Time',
            # available values
            values=[],
            # just for positioning in our example
            size_hint_x=1,
            size_hint_y=0.5,
            disabled=True,
            pos_hint={'center_x': .5, 'center_y': .5})
        self.dropoff_time_spinner.bind(text=self.select_dropoff_time)
        inner_layout_1.ids.delivery_table.add_widget(dropoff_time_label)
        inner_layout_1.ids.delivery_table.add_widget(self.dropoff_time_spinner)

        special_instructions_label = Factory.BottomLeftFormLabel(text="[b](5)[/b] Special Instructions",
                                                                 markup=True)
        self.special_instructions = Factory.CenterVerticalTextInput(multiline=True)
        inner_layout_1.ids.delivery_table.add_widget(special_instructions_label)
        inner_layout_1.ids.delivery_table.add_widget(self.special_instructions)
        inner_layout_1.ids.delivery_table.add_widget(Label(text=' '))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        cancel_button = Button(markup=True,
                               text="Cancel",
                               on_release=self.delivery_popup.dismiss)
        add_card_button = Button(markup=True,
                                 text="Add Card",
                                 on_release=self.add_card_setup)
        add_address_button = Button(markup=True,
                                    text="Add Address",
                                    on_release=self.add_address_setup)
        setup_button = Button(markup=True,
                              text="Set Delivery",
                              on_release=self.set_delivery)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(add_card_button)
        inner_layout_2.add_widget(add_address_button)
        inner_layout_2.add_widget(setup_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.delivery_popup.content = layout
        self.delivery_popup.open()

    def select_online_card(self, *args, **kwargs):
        card_string = self.card_id_spinner.text
        if self.cards:
            for card in self.cards:
                check_string = "{} {} {}/{}".format(card['card_type'],
                                                    card['last_four'],
                                                    card['exp_month'],
                                                    card['exp_year'])
                if check_string == card_string:
                    self.card_id = card['card_id']
                    print(self.card_id)
        pass

    def select_address(self, *args, **kwargs):
        address_string = self.address_id_spinner.text
        if self.addresses:
            for address in self.addresses:
                check_string = "{} - {} {}, {} {}".format(address['name'],
                                                          address['street'],
                                                          address['city'],
                                                          address['state'],
                                                          address['zipcode'])
                if check_string == address_string:
                    self.address_id = address['address_id']
                    print(self.address_id)
        pass

    def select_dropoff_time(self, instance, value, *args, **kwargs):
        if value in self.dropoff_time_group:
            self.dropoff_delivery_id = self.dropoff_time_group[value]

        print(self.dropoff_delivery_id)
        pass

    def select_pickup_time(self, instance, value, *args, **kwargs):
        if value in self.pickup_time_group:
            self.pickup_delivery_id = self.pickup_time_group[value]

        print(self.pickup_delivery_id)
        pass

    def pickup_status(self, instance, value, *args, **kwargs):
        self.pickup_date_btn.disabled = True if value is False else False
        self.pickup_time_spinner.disabled = True if value is False else False
        pass

    def dropoff_status(self, instance, value, *args, **kwargs):
        self.dropoff_date_btn.disabled = True if value is False else False
        self.dropoff_time_spinner.disabled = True if value is False else False
        pass

    def get_dropoff_dates(self, *args, **kwargs):
        if self.address_id:
            store_hours = Company().get_store_hours(vars.COMPANY_ID)
            today = datetime.datetime.today()
            dow = int(datetime.datetime.today().strftime("%w"))
            turn_around_day = int(store_hours[dow]['turnaround']) if store_hours[dow]['turnaround'] else 0
            turn_around_hour = store_hours[dow]['due_hour'] if store_hours[dow]['due_hour'] else '4'
            turn_around_minutes = store_hours[dow]['due_minutes'] if store_hours[dow]['due_minutes'] else '00'
            turn_around_ampm = store_hours[dow]['due_ampm'] if store_hours[dow]['due_ampm'] else 'pm'
            new_date = today + datetime.timedelta(days=turn_around_day)
            date_string = '{} {}:{}:00'.format(new_date.strftime("%Y-%m-%d"),
                                               turn_around_hour if turn_around_ampm == 'am' else int(
                                                   turn_around_hour) + 12,
                                               turn_around_minutes)

            self.month = int(today.strftime('%m'))

            self.main_popup = Popup()
            self.main_popup.title = 'Calendar'
            layout = BoxLayout(orientation='vertical')
            inner_layout_1 = BoxLayout(size_hint=(1, 0.9),
                                       orientation='vertical')
            calendar_selection = GridLayout(cols=4,
                                            rows=1,
                                            size_hint=(1, 0.1))
            prev_month = Button(markup=True,
                                text="<",
                                font_size="30sp",
                                on_release=self.prev_dropoff_month)
            next_month = Button(markup=True,
                                text=">",
                                font_size="30sp",
                                on_release=self.next_dropoff_month)
            select_month = Factory.SelectMonth()
            self.month_button = Button(text='{}'.format(vars.month_by_number(self.month)),
                                       on_release=select_month.open)
            for index in range(12):
                month_options = Button(text='{}'.format(vars.month_by_number(index)),
                                       size_hint_y=None,
                                       height=40,
                                       on_release=partial(self.select_dropoff_calendar_month, index))
                select_month.add_widget(month_options)

            select_month.on_select = lambda instance, x: setattr(self.month_button, 'text', x)
            select_year = Factory.SelectMonth()

            self.year_button = Button(text="{}".format(self.year),
                                      on_release=select_year.open)
            for index in range(10):
                year_options = Button(text='{}'.format(int(self.year) + index),
                                      size_hint_y=None,
                                      height=40,
                                      on_release=partial(self.select_dropoff_calendar_year, index))
                select_year.add_widget(year_options)

            select_year.bind(on_select=lambda instance, x: setattr(self.year_button, 'text', x))
            calendar_selection.add_widget(prev_month)
            calendar_selection.add_widget(self.month_button)
            calendar_selection.add_widget(self.year_button)
            calendar_selection.add_widget(next_month)
            self.calendar_layout = GridLayout(cols=7,
                                              rows=8,
                                              size_hint=(1, 0.9))
            today_date = datetime.datetime.today()
            today_string = today_date.strftime('%Y-%m-%d 00:00:00')

            self.create_dropoff_calendar_table()

            inner_layout_1.add_widget(calendar_selection)
            inner_layout_1.add_widget(self.calendar_layout)
            inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                       orientation='horizontal')
            inner_layout_2.add_widget(Button(markup=True,
                                             text="Okay",
                                             on_release=self.main_popup.dismiss))

            layout.add_widget(inner_layout_1)
            layout.add_widget(inner_layout_2)
            self.main_popup.content = layout
            self.main_popup.open()
        else:
            popup = Popup()
            popup.title = 'Delivery Error'
            content = KV.popup_alert('You must first select an address before selecting a dropoff date.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()
        pass

    def get_pickup_dates(self, *args, **kwargs):
        if self.address_id:
            store_hours = Company().get_store_hours(vars.COMPANY_ID)
            today = datetime.datetime.today()
            dow = int(datetime.datetime.today().strftime("%w"))
            turn_around_day = int(store_hours[dow]['turnaround']) if store_hours[dow]['turnaround'] else 0
            turn_around_hour = store_hours[dow]['due_hour'] if store_hours[dow]['due_hour'] else '4'
            turn_around_minutes = store_hours[dow]['due_minutes'] if store_hours[dow]['due_minutes'] else '00'
            turn_around_ampm = store_hours[dow]['due_ampm'] if store_hours[dow]['due_ampm'] else 'pm'
            new_date = today + datetime.timedelta(days=turn_around_day)
            date_string = '{} {}:{}:00'.format(new_date.strftime("%Y-%m-%d"),
                                               turn_around_hour if turn_around_ampm == 'am' else int(
                                                   turn_around_hour) + 12,
                                               turn_around_minutes)

            self.month = int(today.strftime('%m'))

            self.main_popup = Popup()
            self.main_popup.title = 'Calendar'
            layout = BoxLayout(orientation='vertical')
            inner_layout_1 = BoxLayout(size_hint=(1, 0.9),
                                       orientation='vertical')
            calendar_selection = GridLayout(cols=4,
                                            rows=1,
                                            size_hint=(1, 0.1))
            prev_month = Button(markup=True,
                                text="<",
                                font_size="30sp",
                                on_release=self.prev_pickup_month)
            next_month = Button(markup=True,
                                text=">",
                                font_size="30sp",
                                on_release=self.next_pickup_month)
            select_month = Factory.SelectMonth()
            self.month_button = Button(text='{}'.format(vars.month_by_number(self.month)),
                                       on_release=select_month.open)
            for index in range(12):
                month_options = Button(text='{}'.format(vars.month_by_number(index)),
                                       size_hint_y=None,
                                       height=40,
                                       on_release=partial(self.select_pickup_calendar_month, index))
                select_month.add_widget(month_options)

            select_month.on_select = lambda instance, x: setattr(self.month_button, 'text', x)
            select_year = Factory.SelectMonth()

            self.year_button = Button(text="{}".format(self.year),
                                      on_release=select_year.open)
            for index in range(10):
                year_options = Button(text='{}'.format(int(self.year) + index),
                                      size_hint_y=None,
                                      height=40,
                                      on_release=partial(self.select_pickup_calendar_year, index))
                select_year.add_widget(year_options)

            select_year.bind(on_select=lambda instance, x: setattr(self.year_button, 'text', x))
            calendar_selection.add_widget(prev_month)
            calendar_selection.add_widget(self.month_button)
            calendar_selection.add_widget(self.year_button)
            calendar_selection.add_widget(next_month)
            self.calendar_layout = GridLayout(cols=7,
                                              rows=8,
                                              size_hint=(1, 0.9))
            today_date = datetime.datetime.today()
            today_string = today_date.strftime('%Y-%m-%d 00:00:00')

            self.create_pickup_calendar_table()

            inner_layout_1.add_widget(calendar_selection)
            inner_layout_1.add_widget(self.calendar_layout)
            inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                       orientation='horizontal')
            inner_layout_2.add_widget(Button(markup=True,
                                             text="Okay",
                                             on_release=self.main_popup.dismiss))

            layout.add_widget(inner_layout_1)
            layout.add_widget(inner_layout_2)
            self.main_popup.content = layout
            self.main_popup.open()
        else:
            popup = Popup()
            popup.title = 'Delivery Error'
            content = KV.popup_alert('You must first select an address before selecting a dropoff date.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()
        pass

    def set_delivery(self, *args, **kwargs):
        # validate
        if self.card_id is None:

            popup = Popup()
            popup.title = 'Schedule Error'
            content = KV.popup_alert('You have not selected a credit card on file')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()
        elif self.address_id is None:

            popup = Popup()
            popup.title = 'Schedule Error'
            content = KV.popup_alert('You must first select an address.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()
        elif self.pickup_status is True and self.pickup_delivery_id is None:

            popup = Popup()
            popup.title = 'Schedule Error'
            content = KV.popup_alert('Please select a proper pickup date and time')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()
        elif self.dropoff_status is True and self.dropoff_delivery_id is None:

            popup = Popup()
            popup.title = 'Schedule Error'
            content = KV.popup_alert('Please select a proper dropoff date and time.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()
        elif self.dropoff_status is False and self.pickup_status is False:
            popup = Popup()
            popup.title = 'Schedule Error'
            content = KV.popup_alert('You must choose at least a dropoff or a pickup.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()
        else:
            # create a new schedule instance
            schedules = Schedule()
            schedules.company_id = vars.COMPANY_ID
            schedules.customer_id = vars.CUSTOMER_ID
            schedules.card_id = self.card_id
            schedules.pickup_delivery_id = self.pickup_delivery_id
            schedules.pickup_date = self.pickup_date
            schedules.pickup_address = self.address_id
            schedules.dropoff_delivery_id = self.dropoff_delivery_id
            schedules.dropoff_date = self.dropoff_date
            schedules.dropoff_address = self.address_id
            schedules.special_instructions = self.special_instructions.text
            schedules.type = 2
            status = 1
            if self.pickup_delivery_id:
                status = 1
            elif not self.pickup_delivery_id and self.dropoff_delivery_id:
                status = 4

            schedules.status = status

            if schedules.add():
                self.delivery_popup.dismiss()
                # sync db
                run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
                try:
                    run_sync.start()
                finally:
                    run_sync.join()
                    # show alert
                    popup = Popup()
                    popup.title = 'Schedule Successfully Made'
                    content = KV.popup_alert('Delivery has been succesfully scheduled.')
                    popup.content = Builder.load_string(content)
                    popup.open()
                    # Beep Sound
                    sys.stdout.write('\a')
                    sys.stdout.flush()

        pass

    def add_card_setup(self, *args, **kwargs):
        self.main_popup.title = 'Add Card Setup'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = Factory.DeliveryGrid()
        card_number_label = Factory.BottomLeftFormLabel(text="Card Number")
        self.card_number_input = Factory.CenterVerticalTextInput()
        exp_month_label = Factory.BottomLeftFormLabel(text="Expiration Month")
        self.exp_month_input = Factory.CenterVerticalTextInput()
        exp_year_label = Factory.BottomLeftFormLabel(text="Expiration Year")
        self.exp_year_input = Factory.CenterVerticalTextInput()
        first_name_label = Factory.BottomLeftFormLabel(text="First Name")
        self.first_name_input = Factory.CenterVerticalTextInput()
        last_name_label = Factory.BottomLeftFormLabel(text="Last Name")
        self.last_name_input = Factory.CenterVerticalTextInput()
        street_label = Factory.BottomLeftFormLabel(text="Street")
        self.street_input = Factory.CenterVerticalTextInput()
        suite_label = Factory.BottomLeftFormLabel(text="Suite")
        self.suite_input = Factory.CenterVerticalTextInput()
        city_label = Factory.BottomLeftFormLabel(text="City")
        self.city_input = Factory.CenterVerticalTextInput()
        state_label = Factory.BottomLeftFormLabel(text="State")
        self.state_input = Factory.CenterVerticalTextInput(text="WA")
        zipcode_label = Factory.BottomLeftFormLabel(text="Zipcode")
        self.zipcode_input = Factory.CenterVerticalTextInput()
        inner_layout_1.ids.delivery_table.add_widget(card_number_label)
        inner_layout_1.ids.delivery_table.add_widget(self.card_number_input)
        inner_layout_1.ids.delivery_table.add_widget(exp_month_label)
        inner_layout_1.ids.delivery_table.add_widget(self.exp_month_input)
        inner_layout_1.ids.delivery_table.add_widget(exp_year_label)
        inner_layout_1.ids.delivery_table.add_widget(self.exp_year_input)
        inner_layout_1.ids.delivery_table.add_widget(first_name_label)
        inner_layout_1.ids.delivery_table.add_widget(self.first_name_input)
        inner_layout_1.ids.delivery_table.add_widget(last_name_label)
        inner_layout_1.ids.delivery_table.add_widget(self.last_name_input)
        inner_layout_1.ids.delivery_table.add_widget(street_label)
        inner_layout_1.ids.delivery_table.add_widget(self.street_input)
        inner_layout_1.ids.delivery_table.add_widget(suite_label)
        inner_layout_1.ids.delivery_table.add_widget(self.suite_input)
        inner_layout_1.ids.delivery_table.add_widget(city_label)
        inner_layout_1.ids.delivery_table.add_widget(self.city_input)
        inner_layout_1.ids.delivery_table.add_widget(state_label)
        inner_layout_1.ids.delivery_table.add_widget(self.state_input)
        inner_layout_1.ids.delivery_table.add_widget(zipcode_label)
        inner_layout_1.ids.delivery_table.add_widget(self.zipcode_input)
        inner_layout_1.ids.delivery_table.add_widget(Label(text=' '))
        inner_layout_1.ids.delivery_table.add_widget(Label(text=' '))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        cancel_button = Button(markup=True,
                               text="Cancel",
                               on_release=self.main_popup.dismiss)
        add_button = Button(markup=True,
                            text="Add",
                            on_release=self.add_new_card)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(add_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.main_popup.content = layout
        self.main_popup.open()
        pass

    def add_new_card(self, *args, **kwargs):
        errors = 0
        if not self.card_number_input.text:
            errors += 1
            self.card_number_input.text_color = ERROR_COLOR
            self.card_number_input.hint_text = 'Must enter card number'
        else:
            self.card_number_input.text_color = DEFAULT_COLOR
            self.card_number_input.hint_text = ""

        if not self.exp_month_input.text:
            errors += 1
            self.exp_month_input.text_color = ERROR_COLOR
            self.exp_month_input.hint_text = 'Must enter expired month'
        else:
            self.exp_month_input.text_color = DEFAULT_COLOR
            self.exp_month_input.hint_text = ""

        if not self.exp_year_input.text:
            errors += 1
            self.exp_year_input.text_color = ERROR_COLOR
            self.exp_year_input.hint_text = 'Must enter expired year'
        else:
            self.exp_year_input.text_color = DEFAULT_COLOR
            self.exp_year_input.hint_text = ""

        if not self.first_name_input.text:
            errors += 1
            self.first_name_input.text_color = ERROR_COLOR
            self.first_name_input.hint_text = 'Must enter first name'
        else:
            self.first_name_input.text_color = DEFAULT_COLOR
            self.first_name_input.hint_text = ""

        if not self.last_name_input.text:
            errors += 1
            self.last_name_input.text_color = ERROR_COLOR
            self.last_name_input.hint_text = 'Must enter last name'
        else:
            self.last_name_input.text_color = DEFAULT_COLOR
            self.last_name_input.hint_text = ""

        if not self.street_input.text:
            errors += 1
            self.street_input.text_color = ERROR_COLOR
            self.street_input.hint_text = 'Must enter street address'
        else:
            self.street_input.text_color = DEFAULT_COLOR
            self.street_input.hint_text = ""

        if not self.city_input.text:
            errors += 1
            self.city_input.text_color = ERROR_COLOR
            self.city_input.hint_text = 'Must enter city'
        else:
            self.city_input.text_color = DEFAULT_COLOR
            self.city_input.hint_text = ""

        if not self.state_input.text:
            errors += 1
            self.state_input.text_color = ERROR_COLOR
            self.state_input.hint_text = 'Must enter state'
        else:
            self.state_input.text_color = DEFAULT_COLOR
            self.state_input.hint_text = ""

        if not self.zipcode_input.text:
            errors += 1
            self.zipcode_input.text_color = ERROR_COLOR
            self.zipcode_input.hint_text = 'Must enter zipcode'
        else:
            self.zipcode_input.text_color = DEFAULT_COLOR
            self.zipcode_input.hint_text = ""

        if errors == 0:
            # loop through each company and save
            companies = Company().where({'id': {'>': 0}})
            save_success = 0
            if companies:
                for company in companies:
                    company_id = company['id']
                    cards = Card()
                    cards.company_id = company_id
                    cards.user_id = vars.CUSTOMER_ID
                    # search for a profile
                    profiles = Profile().where({'company_id': company_id, 'user_id': vars.CUSTOMER_ID})
                    profile_id = False
                    if profiles:
                        for profile in profiles:
                            profile_id = profile['profile_id']
                        cards.profile_id = profile_id
                        # make just payment_id
                        new_card = {
                            'customer_type': 'individual',
                            'card_number': str(self.card_number_input.text.rstrip()),
                            'expiration_month': str(self.exp_month_input.text.rstrip()),
                            'expiration_year': str(self.exp_year_input.text.rstrip()),
                            'billing': {
                                'first_name': str(self.first_name_input.text),
                                'last_name': str(self.last_name_input.text),
                                'company': '',
                                'address': str(self.street_input.text),
                                'city': str(self.city_input.text),
                                'state': str(self.state_input.text),
                                'zip': str(self.zipcode_input.text),
                                'country': 'USA'
                            }
                        }
                        result = Card().create_card(company_id, profile_id, new_card)
                        if result['status']:
                            save_success += 1
                            payment_id = result['payment_id']

                            cards.payment_id = payment_id
                            if company_id is 1:
                                self.root_payment_id = payment_id
                            cards.root_payment_id = self.root_payment_id
                            cards.street = self.street_input.text
                            cards.suite = self.suite_input.text
                            cards.city = self.city_input.text
                            cards.state = self.state_input.text
                            cards.zipcode = self.zipcode_input.text
                            cards.exp_month = self.exp_month_input.text
                            cards.exp_year = self.exp_year_input.text
                            cards.status = 1
                            cards.add()
                        else:
                            popup = Popup()
                            popup.title = 'Card Error'
                            content = KV.popup_alert(result['message'])
                            popup.content = Builder.load_string(content)
                            popup.open()
                            # Beep Sound
                            sys.stdout.write('\a')
                            sys.stdout.flush()
                    else:
                        # make profile_id and payment_id
                        customers = User().where({'user_id': vars.CUSTOMER_ID})
                        if customers:
                            for customer in customers:
                                first_name = customer['first_name']
                                last_name = customer['last_name']
                        new_data = {
                            'merchant_id': str(vars.CUSTOMER_ID),
                            'description': '{}, {}'.format(last_name, first_name),
                            'customer_type': 'individual',
                            'billing': {
                                'first_name': str(self.first_name_input.text),
                                'last_name': str(self.last_name_input.text),
                                'company': '',
                                'address': '{}'.format(self.street_input.text),
                                'city': str(self.city_input.text),
                                'state': str(self.state_input.text),
                                'zip': str(self.zipcode_input.text),
                                'country': 'USA'
                            },
                            'credit_card': {
                                'card_number': str(self.card_number_input.text.rstrip()),
                                'card_code': '',
                                'expiration_month': str(self.exp_month_input.text.rstrip()),
                                'expiration_year': str(self.exp_year_input.text.rstrip()),
                            }
                        }
                        make_profile = Card().create_profile(company_id, new_data)

                        if make_profile['status']:
                            save_success += 1
                            profile_id = make_profile['profile_id']
                            payment_id = make_profile['payment_id']
                            new_profiles = Profile()
                            new_profiles.company_id = company_id
                            new_profiles.user_id = vars.CUSTOMER_ID
                            new_profiles.profile_id = profile_id
                            new_profiles.status = 1
                            new_profiles.add()

                            cards.profile_id = profile_id
                            cards.payment_id = payment_id
                            cards.street = self.street_input.text
                            cards.suite = self.suite_input.text
                            cards.city = self.city_input.text
                            cards.state = self.state_input.text
                            cards.zipcode = self.zipcode_input.text
                            cards.exp_month = self.exp_month_input.text
                            cards.exp_year = self.exp_year_input.text
                            if company_id is 1:
                                self.root_payment_id = payment_id
                            cards.root_payment_id = self.root_payment_id
                            cards.status = 1
                            cards.add()

                        else:
                            popup = Popup()
                            popup.title = 'Add Card Error'
                            content = KV.popup_alert(make_profile['message'])
                            popup.content = Builder.load_string(content)
                            popup.open()
                            # Beep Sound
                            sys.stdout.write('\a')
                            sys.stdout.flush()
            if save_success > 0:
                # finish and reset
                popup = Popup()
                popup.title = 'Card Add Successful'
                content = KV.popup_alert('Successfully added a card.')
                popup.content = Builder.load_string(content)
                popup.open()
                # Beep Sound
                sys.stdout.write('\a')
                sys.stdout.flush()
                run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
                try:
                    run_sync.start()
                finally:
                    run_sync.join()
                    self.main_popup.dismiss()
                    pro = Profile()
                    profiles = pro.where({'user_id': vars.CUSTOMER_ID,
                                          'company_id': vars.COMPANY_ID})
                    if profiles:
                        for profile in profiles:
                            vars.PROFILE_ID = profile['profile_id']

                        cards_db = Card()
                        self.cards = cards_db.collect(vars.COMPANY_ID, vars.PROFILE_ID)
                    else:
                        self.cards = False
                    self.card_string = []
                    if self.cards:
                        for card in self.cards:
                            self.card_string.append("{} {} {}/{}".format(card['card_type'],
                                                                         card['last_four'],
                                                                         card['exp_month'],
                                                                         card['exp_year']))

                    self.card_id_spinner.values = self.card_string

            else:
                popup = Popup()
                popup.title = 'Card Add Unsuccessful'
                content = KV.popup_alert('There were problems saving your card. Please try again')
                popup.content = Builder.load_string(content)
                popup.open()

        pass

    def add_address_setup(self, *args, **kwargs):
        self.main_popup.title = 'Add Address Setup'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = Factory.DeliveryGrid()
        name_label = Factory.BottomLeftFormLabel(text="Address Nick Name")
        self.name_input = Factory.CenterVerticalTextInput()
        street_label = Factory.BottomLeftFormLabel(text="Street")
        self.street_input = Factory.CenterVerticalTextInput()
        suite_label = Factory.BottomLeftFormLabel(text="Suite")
        self.suite_input = Factory.CenterVerticalTextInput()
        city_label = Factory.BottomLeftFormLabel(text="City")
        self.city_input = Factory.CenterVerticalTextInput()
        state_label = Factory.BottomLeftFormLabel(text="State")
        self.state_input = Factory.CenterVerticalTextInput(text="WA")
        zipcode_label = Factory.BottomLeftFormLabel(text="Zipcode")
        self.zipcode_input = Factory.CenterVerticalTextInput()
        concierge_name_label = Factory.BottomLeftFormLabel(text="Contact Name")
        self.concierge_name_input = Factory.CenterVerticalTextInput()
        concierge_number_label = Factory.BottomLeftFormLabel(text="Contact Number")
        self.concierge_number_input = Factory.CenterVerticalTextInput()
        inner_layout_1.ids.delivery_table.add_widget(name_label)
        inner_layout_1.ids.delivery_table.add_widget(self.name_input)
        inner_layout_1.ids.delivery_table.add_widget(street_label)
        inner_layout_1.ids.delivery_table.add_widget(self.street_input)
        inner_layout_1.ids.delivery_table.add_widget(suite_label)
        inner_layout_1.ids.delivery_table.add_widget(self.suite_input)
        inner_layout_1.ids.delivery_table.add_widget(city_label)
        inner_layout_1.ids.delivery_table.add_widget(self.city_input)
        inner_layout_1.ids.delivery_table.add_widget(state_label)
        inner_layout_1.ids.delivery_table.add_widget(self.state_input)
        inner_layout_1.ids.delivery_table.add_widget(zipcode_label)
        inner_layout_1.ids.delivery_table.add_widget(self.zipcode_input)
        inner_layout_1.ids.delivery_table.add_widget(concierge_name_label)
        inner_layout_1.ids.delivery_table.add_widget(self.concierge_name_input)
        inner_layout_1.ids.delivery_table.add_widget(concierge_number_label)
        inner_layout_1.ids.delivery_table.add_widget(self.concierge_number_input)
        inner_layout_1.ids.delivery_table.add_widget(Label(text=' '))
        inner_layout_1.ids.delivery_table.add_widget(Label(text=' '))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        cancel_button = Button(markup=True,
                               text="Cancel",
                               on_release=self.main_popup.dismiss)
        add_button = Button(markup=True,
                            text="Add",
                            on_release=self.add_new_address)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(add_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.main_popup.content = layout
        self.main_popup.open()
        pass

    def add_new_address(self, *args, **kwargs):
        addresses = Address()
        addresses.company_id = vars.COMPANY_ID
        addresses.user_id = vars.CUSTOMER_ID
        addresses.name = self.name_input.text
        addresses.street = self.street_input.text
        addresses.suite = self.suite_input.text
        addresses.city = self.city_input.text
        addresses.state = self.state_input.text
        addresses.zipcode = self.zipcode_input.text
        addresses.primary_address = 0
        addresses.concierge_name = self.concierge_name_input.text
        addresses.concierge_number = self.concierge_number_input.text
        addresses.status = 1
        if addresses.add():
            run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
            try:
                run_sync.start()
            finally:
                run_sync.join()
                # update the form with a new address list
                self.addresses = Address().where({'user_id': vars.CUSTOMER_ID})
                self.address_string = []
                if self.addresses:
                    for address in self.addresses:
                        self.address_string.append("{} - {} {}, {} {}".format(address['name'],
                                                                              address['street'],
                                                                              address['city'],
                                                                              address['state'],
                                                                              address['zipcode']))
                self.address_id_spinner.values = self.address_string
                self.main_popup.dismiss()
                popup = Popup()
                popup.title = 'Address Added'
                content = KV.popup_alert('Successfully added a new address to delivery setup')
                popup.content = Builder.load_string(content)
                popup.open()
                # Beep Sound
                sys.stdout.write('\a')
                sys.stdout.flush()

        pass

    def create_dropoff_calendar_table(self):
        # set the variables

        store_hours = Company().get_store_hours(vars.COMPANY_ID)
        # schedule dates
        addresses = Address().where({'address_id': self.address_id})
        zipcode = False
        if addresses:
            for address in addresses:
                zipcode = address['zipcode']
        delivery_ids = []
        if zipcode:
            zips = Zipcode().where({'zipcode': zipcode})
            if zips:
                for zip in zips:
                    delivery_ids.append(zip['delivery_id'])

        # day of the week
        dow = {}
        # blackout dates
        blackout_dates = []
        if delivery_ids:
            for delivery_id in delivery_ids:
                deliveries = Delivery().where({'delivery_id': delivery_id})
                if deliveries:
                    for delivery in deliveries:
                        dow[delivery['day']] = delivery_id
                        try:
                            blackouts = json.loads(delivery['blackout']) if delivery['blackout'] else False
                            if blackouts:
                                for blackout in blackouts:
                                    if blackout:
                                        blackout_dates.append(blackout)
                        except ValueError as e:
                            print('no blackout dates')
        if self.pickup_date:
            pickup_date = datetime.datetime.strptime(str(self.pickup_date), "%Y-%m-%d %H:%M:%S")
            today_date = pickup_date if self.pickup_date else datetime.datetime.today()
            today_string = today_date.strftime('%Y-%m-%d 00:00:00')
            check_today = datetime.datetime.strptime(today_string, "%Y-%m-%d %H:%M:%S").timestamp()
        else:
            today_date = datetime.datetime.today()
            today_string = today_date.strftime('%Y-%m-%d 00:00:00')
            check_today = datetime.datetime.strptime(today_string, "%Y-%m-%d %H:%M:%S").timestamp()

        self.calendar_layout.clear_widgets()
        calendars = Calendar()
        calendars.setfirstweekday(calendar.SUNDAY)
        selected_month = self.month - 1
        year_dates = calendars.yeardays2calendar(year=self.year, width=1)
        th1 = KV.invoice_tr(0, 'Su')
        th2 = KV.invoice_tr(0, 'Mo')
        th3 = KV.invoice_tr(0, 'Tu')
        th4 = KV.invoice_tr(0, 'We')
        th5 = KV.invoice_tr(0, 'Th')
        th6 = KV.invoice_tr(0, 'Fr')
        th7 = KV.invoice_tr(0, 'Sa')
        self.calendar_layout.add_widget(Builder.load_string(th1))
        self.calendar_layout.add_widget(Builder.load_string(th2))
        self.calendar_layout.add_widget(Builder.load_string(th3))
        self.calendar_layout.add_widget(Builder.load_string(th4))
        self.calendar_layout.add_widget(Builder.load_string(th5))
        self.calendar_layout.add_widget(Builder.load_string(th6))
        self.calendar_layout.add_widget(Builder.load_string(th7))
        if year_dates[selected_month]:
            for month in year_dates[selected_month]:
                for week in month:
                    for day in week:
                        if day[0] > 0:
                            check_date_string = '{}-{}-{} 00:00:00'.format(self.year,
                                                                           Job.date_leading_zeroes(self.month),
                                                                           Job.date_leading_zeroes(day[0]))

                            today_base = datetime.datetime.strptime(check_date_string, "%Y-%m-%d %H:%M:%S")
                            check_date = today_base.timestamp()
                            dow_check = today_base.strftime("%w")
                            today_day = today_base.strftime("%A")
                            # rule #1 remove all past dates so users cannot set a due date previous to today
                            if check_date < check_today:
                                item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                              disabled=True)
                            elif int(store_hours[int(dow_check)]['status']) > 1:  # check to see if business is open
                                if check_date == check_today:
                                    item = Factory.CalendarButton(text="[color=37FDFC][b]{}[/b][/color]".format(day[0]),
                                                                  background_color=(0, 0.50196078, 0.50196078, 1),
                                                                  background_normal='')
                                elif today_day in dow and check_date_string not in blackout_dates:
                                    item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                                  on_release=partial(self.select_dropoff_date,
                                                                                     today_base, dow[today_day]))
                                else:
                                    item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                                  disabled=True)
                            else:  # store is closed
                                item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                              disabled=True)
                        else:
                            item = Factory.CalendarButton(disabled=True)
                        self.calendar_layout.add_widget(item)

    def create_pickup_calendar_table(self):
        # set the variables

        store_hours = Company().get_store_hours(vars.COMPANY_ID)
        # schedule dates
        addresses = Address().where({'address_id': self.address_id})
        zipcode = False
        if addresses:
            for address in addresses:
                zipcode = address['zipcode']
        delivery_ids = []
        if zipcode:
            zips = Zipcode().where({'zipcode': zipcode})
            if zips:
                for zip in zips:
                    delivery_ids.append(zip['delivery_id'])
        # day of the week
        dow = {}
        # blackout dates
        blackout_dates = []
        if delivery_ids:
            for delivery_id in delivery_ids:
                deliveries = Delivery().where({'delivery_id': delivery_id})
                if deliveries:
                    for delivery in deliveries:
                        dow[delivery['day']] = delivery_id
                        try:
                            blackouts = json.loads(delivery['blackout']) if delivery['blackout'] else False
                            if blackouts:
                                for blackout in blackouts:
                                    if blackout:
                                        blackout_dates.append(blackout)
                        except ValueError as e:
                            print('no blackout dates')

        today_date = datetime.datetime.today()
        today_string = today_date.strftime('%Y-%m-%d 00:00:00')
        check_today = datetime.datetime.strptime(today_string, "%Y-%m-%d %H:%M:%S").timestamp()

        self.calendar_layout.clear_widgets()
        calendars = Calendar()
        calendars.setfirstweekday(calendar.SUNDAY)
        selected_month = self.month - 1
        year_dates = calendars.yeardays2calendar(year=self.year, width=1)
        th1 = KV.invoice_tr(0, 'Su')
        th2 = KV.invoice_tr(0, 'Mo')
        th3 = KV.invoice_tr(0, 'Tu')
        th4 = KV.invoice_tr(0, 'We')
        th5 = KV.invoice_tr(0, 'Th')
        th6 = KV.invoice_tr(0, 'Fr')
        th7 = KV.invoice_tr(0, 'Sa')
        self.calendar_layout.add_widget(Builder.load_string(th1))
        self.calendar_layout.add_widget(Builder.load_string(th2))
        self.calendar_layout.add_widget(Builder.load_string(th3))
        self.calendar_layout.add_widget(Builder.load_string(th4))
        self.calendar_layout.add_widget(Builder.load_string(th5))
        self.calendar_layout.add_widget(Builder.load_string(th6))
        self.calendar_layout.add_widget(Builder.load_string(th7))
        if year_dates[selected_month]:
            for month in year_dates[selected_month]:
                for week in month:
                    for day in week:
                        if day[0] > 0:
                            check_date_string = '{}-{}-{} 00:00:00'.format(self.year,
                                                                           Job.date_leading_zeroes(self.month),
                                                                           Job.date_leading_zeroes(day[0]))

                            today_base = datetime.datetime.strptime(check_date_string, "%Y-%m-%d %H:%M:%S")
                            check_date = today_base.timestamp()
                            dow_check = today_base.strftime("%w")
                            today_day = today_base.strftime("%A")
                            # rule #1 remove all past dates so users cannot set a due date previous to today
                            if check_date < check_today:
                                item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                              disabled=True)
                            elif int(store_hours[int(dow_check)]['status']) > 1:  # check to see if business is open
                                if check_date == check_today:
                                    item = Factory.CalendarButton(text="[color=37FDFC][b]{}[/b][/color]".format(day[0]),
                                                                  background_color=(0, 0.50196078, 0.50196078, 1),
                                                                  background_normal='')
                                elif today_day in dow and check_date_string not in blackout_dates:
                                    item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                                  on_release=partial(self.select_pickup_date,
                                                                                     today_base, dow[today_day]))
                                else:
                                    item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                                  disabled=True)
                            else:  # store is closed
                                item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                              disabled=True)
                        else:
                            item = Factory.CalendarButton(disabled=True)
                        self.calendar_layout.add_widget(item)

    def select_pickup_date(self, pickup_date, delivery_id, *args, **kwargs):
        self.pickup_date = pickup_date
        dd = datetime.datetime.strptime(str(pickup_date), "%Y-%m-%d %H:%M:%S")
        dd_string = dd.strftime('%a %m/%d/%Y')
        self.pickup_date_btn.text = str(dd_string)
        print(self.pickup_date)
        # get delivery times
        deliveries = Delivery().where({'delivery_id': delivery_id})

        time_display = []
        self.pickup_time_group = {}
        if deliveries:
            for delivery in deliveries:
                start_time = delivery['start_time']
                end_time = delivery['end_time']
                time_string = '{} - {}'.format(start_time, end_time)
                time_display.append(time_string)
                self.pickup_time_group[time_string] = delivery_id
        self.pickup_delivery_id = delivery_id
        self.pickup_time_spinner.values = time_display
        self.main_popup.dismiss()

    def select_dropoff_date(self, dropoff_date, delivery_id, *args, **kwargs):
        self.dropoff_date = dropoff_date
        pu = datetime.datetime.strptime(str(dropoff_date), "%Y-%m-%d %H:%M:%S")
        pu_string = pu.strftime('%a %m/%d/%Y')
        self.dropoff_date_btn.text = str(pu_string)
        print(self.dropoff_date)

        # get delivery times
        deliveries = Delivery().where({'delivery_id': delivery_id})

        time_display = []
        self.dropoff_time_group = {}
        if deliveries:
            for delivery in deliveries:
                start_time = delivery['start_time']
                end_time = delivery['end_time']
                time_string = '{} - {}'.format(start_time, end_time)
                time_display.append(time_string)
                self.dropoff_time_group[time_string] = delivery_id
        self.dropoff_time_spinner.values = time_display
        self.dropoff_delivery_id = delivery_id
        self.main_popup.dismiss()

    def prev_dropoff_month(self, *args, **kwargs):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.month_button.text = '{}'.format(vars.month_by_number(self.month))
        self.year_button.text = '{}'.format(self.year)
        self.create_dropoff_calendar_table()

    def next_dropoff_month(self, *args, **kwargs):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.month_button.text = '{}'.format(vars.month_by_number(self.month))
        self.year_button.text = '{}'.format(self.year)
        self.create_dropoff_calendar_table()

    def select_dropoff_calendar_month(self, month, *args, **kwargs):
        self.month = month
        self.create_dropoff_calendar_table()

    def select_dropoff_calendar_year(self, year, *args, **kwargs):
        self.year = year
        self.create_dropoff_calendar_table()

    def prev_pickup_month(self, *args, **kwargs):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.month_button.text = '{}'.format(vars.month_by_number(self.month))
        self.year_button.text = '{}'.format(self.year)
        self.create_pickup_calendar_table()

    def next_pickup_month(self, *args, **kwargs):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.month_button.text = '{}'.format(vars.month_by_number(self.month))
        self.year_button.text = '{}'.format(self.year)
        self.create_pickup_calendar_table()

    def select_pickup_calendar_month(self, month, *args, **kwargs):
        self.month = month
        self.create_pickup_calendar_table()

    def select_pickup_calendar_year(self, year, *args, **kwargs):
        self.year = year
        self.create_pickup_calendar_table()

    def view_deliveries(self):
        self.main_popup.title = 'View Deliveries'
        layout = BoxLayout(orientation="vertical")
        inner_layout_1 = Factory.ScrollGrid(size_hint=(1, 0.9))
        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        inner_layout_1.ids.main_table.cols = 6
        inner_layout_1.ids.main_table.row_default_height = '75sp'
        schedules = Schedule().where({'customer_id': vars.CUSTOMER_ID,
                                      'status': {'<': 12}})
        th1 = KV.invoice_tr(0, 'ID')
        th2 = KV.invoice_tr(0, 'P. Date')
        th3 = KV.invoice_tr(0, 'P. Time')
        th4 = KV.invoice_tr(0, 'D. Date')
        th5 = KV.invoice_tr(0, 'D. Time')
        th6 = KV.invoice_tr(0, 'Status')
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th1))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th2))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th3))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th4))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th5))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th6))
        if schedules:
            for schedule in schedules:
                try:
                    pickup_date = datetime.datetime.strptime(str(schedule['pickup_date']), "%Y-%m-%d %H:%M:%S")
                except ValueError as e:
                    pickup_date = False
                try:
                    dropoff_date = datetime.datetime.strptime(str(schedule['dropoff_date']), "%Y-%m-%d %H:%M:%S")
                except ValueError as e:
                    dropoff_date = False
                pickup_address_id = schedule['pickup_address']
                dropoff_address_id = schedule['dropoff_address']
                pickup_delivery_id = schedule['pickup_delivery_id']
                dropoff_delivery_id = schedule['dropoff_delivery_id']
                status = schedule['status']
                special_instructions = schedule['special_instructions'] if schedule['special_instructions'] else ''
                pickup_date_formatted = pickup_date.strftime('%a %m/%d/%Y') if pickup_date else 'No Date'
                dropoff_date_formatted = dropoff_date.strftime('%a %m/%d/%Y') if dropoff_date else 'No Date'
                pickup_time_string = ''
                if dropoff_delivery_id:
                    deliveries = Delivery().where({'delivery_id': dropoff_delivery_id})

                    if deliveries:
                        for delivery in deliveries:
                            pickup_time_string = '{} - {}'.format(delivery['start_time'], delivery['end_time'])
                dropoff_time_string = ''
                if pickup_delivery_id:
                    deliveries = Delivery().where({'delivery_id': pickup_delivery_id})

                    if deliveries:
                        for delivery in deliveries:
                            dropoff_time_string = '{} - {}'.format(delivery['start_time'], delivery['end_time'])
                address_string = ''
                concierge_name = ''
                concierge_number = ''
                if pickup_address_id:
                    addresses = Address().where({'address_id': pickup_address_id})
                    if addresses:
                        for address in addresses:
                            address_name = address['name']
                            street = address['street']
                            address_string = '{}: {}'.format(address_name, street)
                            concierge_name = address['concierge_name']
                            concierge_number = Job.make_us_phone(address['concierge_number'])
                else:
                    addresses = Address().where({'address_id': dropoff_address_id})
                    if addresses:
                        for address in addresses:
                            address_name = address['name']
                            street = address['street']
                            address_string = '{}: {}'.format(address_name, street)

                            concierge_name = address['concierge_name']
                            concierge_number = Job.make_us_phone(address['concierge_number'])

                status_formatted = Schedule().getStatus(status)

                pickup_date_label = Factory.TopLeftFormButton(text=pickup_date_formatted,
                                                              on_release=partial(self.view_delivery, schedule['id']))
                dropoff_date_label = Factory.TopLeftFormButton(text=dropoff_date_formatted,
                                                               on_release=partial(self.view_delivery, schedule['id']))
                pickup_time_label = Factory.TopLeftFormButton(text=pickup_time_string,
                                                              on_release=partial(self.view_delivery, schedule['id']))
                dropoff_time_label = Factory.TopLeftFormButton(text=dropoff_time_string,
                                                               on_release=partial(self.view_delivery, schedule['id']))
                # address_label = Factory.TopLeftFormButton(text=address_string)
                # special_instructions_label = Factory.TopLeftFormButton(text=special_instructions)
                # concierge_name_label = Factory.TopLeftFormButton(text=concierge_name)
                # concierge_number_label = Factory.TopLeftFormButton(text=concierge_number)
                status_label = Factory.TopLeftFormButton(text=status_formatted,
                                                         on_release=partial(self.view_delivery, schedule['id']))
                inner_layout_1.ids.main_table.add_widget(Button(text=str(schedule['schedule_id']),
                                                                on_release=partial(self.view_delivery, schedule['id'])))
                inner_layout_1.ids.main_table.add_widget(pickup_date_label)
                inner_layout_1.ids.main_table.add_widget(pickup_time_label)
                inner_layout_1.ids.main_table.add_widget(dropoff_date_label)
                inner_layout_1.ids.main_table.add_widget(dropoff_time_label)
                inner_layout_1.ids.main_table.add_widget(status_label)

        cancel_button = Button(text='cancel',
                               on_release=self.main_popup.dismiss)
        inner_layout_2.add_widget(cancel_button)

        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)

        self.main_popup.content = layout
        self.main_popup.open()

    def view_delivery(self, schedule_id, *args, **kwargs):
        popup = Popup()
        popup.title = 'View Delivery #{}'.format(schedule_id)
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = Factory.ScrollGrid(size_hint=(1, 0.9))
        inner_layout_1.ids.main_table.cols = 1
        schedules = Schedule()
        get_schedules = schedules.where({'id': schedule_id})
        if get_schedules:
            for schedule in get_schedules:
                try:
                    pickup_date = datetime.datetime.strptime(str(schedule['pickup_date']), "%Y-%m-%d %H:%M:%S")
                except ValueError as e:
                    pickup_date = False
                try:
                    dropoff_date = datetime.datetime.strptime(str(schedule['dropoff_date']), "%Y-%m-%d %H:%M:%S")
                except ValueError as e:
                    dropoff_date = False
                pickup_address_id = schedule['pickup_address']
                dropoff_address_id = schedule['dropoff_address']
                pickup_delivery_id = schedule['pickup_delivery_id']
                dropoff_delivery_id = schedule['dropoff_delivery_id']
                status = schedule['status']
                special_instructions = schedule['special_instructions'] if schedule['special_instructions'] else ''
                pickup_date_formatted = pickup_date.strftime('%a %m/%d/%Y') if pickup_date else 'No Date'
                dropoff_date_formatted = dropoff_date.strftime('%a %m/%d/%Y') if dropoff_date else 'No Date'
                pickup_time_string = ''
                if dropoff_delivery_id:
                    deliveries = Delivery().where({'delivery_id': dropoff_delivery_id})

                    if deliveries:
                        for delivery in deliveries:
                            pickup_time_string = '{} - {}'.format(delivery['start_time'], delivery['end_time'])
                dropoff_time_string = ''
                if pickup_delivery_id:
                    deliveries = Delivery().where({'delivery_id': pickup_delivery_id})

                    if deliveries:
                        for delivery in deliveries:
                            dropoff_time_string = '{} - {}'.format(delivery['start_time'], delivery['end_time'])
                address_string = ''
                concierge_name = ''
                concierge_number = ''
                if pickup_address_id:
                    addresses = Address().where({'address_id': pickup_address_id})
                    if addresses:
                        for address in addresses:
                            address_name = address['name']
                            street = address['street']
                            address_string = '{}: {}'.format(address_name, street)
                            concierge_name = address['concierge_name']
                            concierge_number = Job.make_us_phone(address['concierge_number'])

                elif not pickup_address_id and dropoff_address_id:
                    addresses = Address().where({'address_id': dropoff_address_id})
                    if addresses:
                        for address in addresses:
                            address_name = address['name']
                            street = address['street']
                            address_string = '{}: {}'.format(address_name, street)

                            concierge_name = address['concierge_name']
                            concierge_number = Job.make_us_phone(address['concierge_number'])
                else:
                    users = User().where({'user_id': vars.CUSTOMER_ID})
                    if users:
                        for user in users:
                            suite = user['suite']
                            street = user['street'] if not suite else '{} {}'.format(user['street'], suite)
                            city = user['city']
                            state = user['state']
                            zipcode = user['zipcode']
                            address_string = '{} {}, {} {}'.format(street, city, state, zipcode)
                            concierge_name = '{} {}'.format(user['first_name'].capitalize(),
                                                            user['last_name'].capitalize())
                            concierge_number = Job.make_us_phone(user['phone'])

                status_formatted = Schedule().getStatus(status)
                id_label = Factory.BottomLeftFormLabel(text="Schedule ID")
                id_input = Factory.CenterVerticalTextInput(text=str(schedule['schedule_id']),
                                                           readonly=True)
                pickup_date_label = Factory.BottomLeftFormLabel(text="Pickup Date")
                pickup_date_input = Factory.CenterVerticalTextInput(text=pickup_date_formatted,
                                                                    readonly=True)
                dropoff_date_label = Factory.BottomLeftFormLabel(text="Dropoff Date")
                dropoff_date_input = Factory.CenterVerticalTextInput(text=dropoff_date_formatted,
                                                                     readonly=True)
                pickup_time_label = Factory.BottomLeftFormLabel(text="Pickup Time")
                pickup_time_input = Factory.CenterVerticalTextInput(text=pickup_time_string,
                                                                    readonly=True)
                dropoff_time_label = Factory.BottomLeftFormLabel(text="Dropoff Time")
                dropoff_time_input = Factory.CenterVerticalTextInput(text=dropoff_time_string,
                                                                     readonly=True)
                address_label = Factory.BottomLeftFormLabel(text="Address")
                address_input = Factory.CenterVerticalTextInput(text=address_string,
                                                                readonly=True)
                special_instructions_label = Factory.BottomLeftFormLabel(text="Special Instructions")
                special_instructions_input = Factory.CenterVerticalTextInput(text=special_instructions,
                                                                             readonly=True)
                concierge_name_label = Factory.BottomLeftFormLabel(text="Contact Name")
                concierge_name_input = Factory.CenterVerticalTextInput(text=concierge_name,
                                                                       readonly=True)
                concierge_number_label = Factory.BottomLeftFormLabel(text="Contact Number")
                concierge_number_input = Factory.CenterVerticalTextInput(text=concierge_number,
                                                                         readonly=True)
                status_label = Factory.BottomLeftFormLabel(text="Status")
                status_input = Factory.CenterVerticalTextInput(text=status_formatted,
                                                               readonly=True)
                inner_layout_1.ids.main_table.add_widget(id_label)
                inner_layout_1.ids.main_table.add_widget(id_input)
                inner_layout_1.ids.main_table.add_widget(pickup_date_label)
                inner_layout_1.ids.main_table.add_widget(pickup_date_input)
                inner_layout_1.ids.main_table.add_widget(pickup_time_label)
                inner_layout_1.ids.main_table.add_widget(pickup_time_input)
                inner_layout_1.ids.main_table.add_widget(dropoff_date_label)
                inner_layout_1.ids.main_table.add_widget(dropoff_date_input)
                inner_layout_1.ids.main_table.add_widget(dropoff_time_label)
                inner_layout_1.ids.main_table.add_widget(dropoff_time_input)
                inner_layout_1.ids.main_table.add_widget(address_label)
                inner_layout_1.ids.main_table.add_widget(address_input)
                inner_layout_1.ids.main_table.add_widget(special_instructions_label)
                inner_layout_1.ids.main_table.add_widget(special_instructions_input)
                inner_layout_1.ids.main_table.add_widget(concierge_name_label)
                inner_layout_1.ids.main_table.add_widget(concierge_name_input)
                inner_layout_1.ids.main_table.add_widget(concierge_number_label)
                inner_layout_1.ids.main_table.add_widget(concierge_number_input)
                inner_layout_1.ids.main_table.add_widget(status_label)
                inner_layout_1.ids.main_table.add_widget(status_input)

        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="cancel",
                               on_release=popup.dismiss)
        inner_layout_2.add_widget(cancel_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def add_store_credit_popup(self):
        self.main_popup.title = 'Add Store Credit'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = Factory.ScrollGrid()
        inner_layout_1.ids.main_table.cols = 1
        credit_amount_label = Factory.BottomLeftFormLabel(text="Credit Amount")
        self.credit_amount = Factory.CenterVerticalTextInput()
        inner_layout_1.ids.main_table.add_widget(credit_amount_label)
        inner_layout_1.ids.main_table.add_widget(self.credit_amount)
        credit_reason_label = Factory.BottomLeftFormLabel(text="Credit Reason")
        credit_reason = Spinner(text='Select Reason',
                                values=[
                                    'Customer Dissatisfaction',
                                    'Gift Certificate',
                                    'Human Error',
                                    'Other'])
        credit_reason.bind(text=self.select_credit_reason)
        inner_layout_1.ids.main_table.add_widget(credit_reason_label)
        inner_layout_1.ids.main_table.add_widget(credit_reason)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        cancel_button = Button(text='cancel',
                               on_release=self.main_popup.dismiss)
        save_button = Button(text='Add Credit',
                             on_release=self.add_credit)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(save_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.main_popup.content = layout
        self.main_popup.open()

    def select_credit_reason(self, instance, value, *args, **kwargs):
        self.credit_reason = value

    def add_credit(self, *args, **kwargs):
        print(vars.CUSTOMER_ID)
        credits = Credit()
        credits.employee_id = str(auth_user.user_id)
        credits.customer_id = str(vars.CUSTOMER_ID)
        credits.amount = str(self.credit_amount.text)
        credits.reason = self.credit_reason
        credits.status = str(1)

        if credits.add():
            customers = User()
            # update user with new balance
            custs = customers.where({'user_id': vars.CUSTOMER_ID})
            old_credit = 0
            if custs:
                for customer in custs:
                    old_credit = customer['credits'] if customer['credits'] is not None else 0
            added_credits = float(self.credit_amount.text) if self.credit_amount.text else 0
            new_credits = old_credit + added_credits
            if customers.put(where={'user_id': vars.CUSTOMER_ID}, data={'credits': new_credits}):
                run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
                try:
                    run_sync.start()
                finally:
                    run_sync.join()
                    vars.SEARCH_RESULTS_STATUS = True
                    vars.ROW_CAP = 0
                    vars.INVOICE_ID = None
                    vars.ROW_SEARCH = 0, 9
                    self.reset()
                    # last 10 setup
                    vars.update_last_10()
                    self.main_popup.dismiss()
                    popup = Popup()
                    popup.title = 'Store Credit'
                    content = KV.popup_alert('Successfully added store credit.')
                    popup.content = Builder.load_string(content)
                    popup.open()
                    # Beep Sound
                    sys.stdout.write('\a')
                    sys.stdout.flush()
            else:

                popup = Popup()
                popup.title = 'Store Credit'
                content = KV.popup_alert('Could not update store credit. Please try again.')
                popup.content = Builder.load_string(content)
                popup.open()
                # Beep Sound
                sys.stdout.write('\a')
                sys.stdout.flush()
        pass

    def credit_history(self, *args, **kwargs):
        self.main_popup.title = 'Credit History'
        layout = BoxLayout(orientation="vertical")
        inner_layout_1 = Factory.ScrollGrid(size_hint=(1, 0.9))
        inner_layout_1.ids.main_table.cols = 6
        credits = Credit().where({'customer_id': vars.CUSTOMER_ID})
        th1 = KV.invoice_tr(0, '#')
        th2 = KV.invoice_tr(0, 'Employee')
        th3 = KV.invoice_tr(0, 'Customer')
        th4 = KV.invoice_tr(0, 'Amount')
        th5 = KV.invoice_tr(0, 'Reason')
        th6 = KV.invoice_tr(0, 'Created')
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th1))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th2))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th3))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th4))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th5))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th6))
        if credits:
            for credit in credits:
                credit_id = credit['credit_id']
                employee_id = credit['employee_id']
                customer_id = credit['customer_id']
                amount = '${:,.2f}'.format(credit['amount'])
                reason = credit['reason']
                created = datetime.datetime.strptime(credit['created_at'], "%Y-%m-%d %H:%M:%S")
                created_formatted = created.strftime('%a %m/%d %I:%M%p')
                td1 = Button(text=str(credit_id))
                td2 = Button(text=str(employee_id))
                td3 = Button(text=str(customer_id))
                td4 = Button(text=str(amount))
                td5 = Factory.TopLeftFormButton(text=str(reason))
                td6 = Factory.TopLeftFormButton(text=str(created_formatted))
                inner_layout_1.ids.main_table.add_widget(td1)
                inner_layout_1.ids.main_table.add_widget(td2)
                inner_layout_1.ids.main_table.add_widget(td3)
                inner_layout_1.ids.main_table.add_widget(td4)
                inner_layout_1.ids.main_table.add_widget(td5)
                inner_layout_1.ids.main_table.add_widget(td6)

        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="cancel",
                               on_release=self.main_popup.dismiss)
        inner_layout_2.add_widget(cancel_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.main_popup.content = layout
        self.main_popup.open()

    def pay_account_popup(self):
        self.main_popup.title = 'Pay Account'
        layout = BoxLayout(orientation="vertical")
        self.inner_layout_1 = Factory.ScrollGrid()
        self.inner_layout_1.ids.main_table.cols = 6
        self.make_pay_account_popup_table()

        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="cancel",
                               on_release=self.main_popup.dismiss)
        payment_button = Button(text="payment options",
                                on_release=self.payment_options_popup)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(payment_button)
        layout.add_widget(self.inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.main_popup.content = layout
        self.main_popup.open()

    def make_pay_account_popup_table(self):
        self.inner_layout_1.ids.main_table.clear_widgets()
        th1 = KV.invoice_tr(0, 'ID')
        th2 = KV.invoice_tr(0, 'Date')
        th3 = KV.invoice_tr(0, 'Due')
        th4 = KV.invoice_tr(0, 'Paid')
        th5 = KV.invoice_tr(0, 'Paid On')
        th6 = KV.invoice_tr(0, 'Status')
        self.inner_layout_1.ids.main_table.add_widget(Builder.load_string(th1))
        self.inner_layout_1.ids.main_table.add_widget(Builder.load_string(th2))
        self.inner_layout_1.ids.main_table.add_widget(Builder.load_string(th3))
        self.inner_layout_1.ids.main_table.add_widget(Builder.load_string(th4))
        self.inner_layout_1.ids.main_table.add_widget(Builder.load_string(th5))
        self.inner_layout_1.ids.main_table.add_widget(Builder.load_string(th6))
        transactions = Transaction()
        trans = transactions.where({'status': {'>': 1},
                                    'customer_id': vars.CUSTOMER_ID,
                                    'ORDER_BY': 'id desc'})
        if (len(trans) > 0):
            for tran in trans:
                billing_period_format = datetime.datetime.strptime(tran['created_at'], "%Y-%m-%d %H:%M:%S")
                billing_period = billing_period_format.strftime("%b %Y")
                due_amount = str('$%.2f' % (tran['total']))
                account_paid_format = tran['account_paid'] if tran['account_paid'] else False
                account_paid = str('$%.2f' % (account_paid_format)) if account_paid_format else 'Not Paid'
                if tran['status'] is 1:
                    status = 'Paid'

                elif tran['status'] is 2:
                    status = 'Bill Sent'
                else:
                    status = 'Current'

                if tran['account_paid_on']:
                    account_paid_on_format = datetime.datetime.strptime(tran['account_paid_on'], "%Y-%m-%d %H:%M:%S")
                    account_paid_on = account_paid_on_format.strftime("%m/%d/%Y %I:%M %p")
                else:
                    account_paid_on = 'Not Paid'

                if tran['trans_id'] in self.selected_account_tr:
                    tr1 = Factory.TagsSelectedButton(text=str(tran['trans_id']),
                                                     on_release=partial(self.select_account_tr, tran['trans_id']))
                    tr2 = Factory.TagsSelectedButton(text=str(billing_period),
                                                     on_release=partial(self.select_account_tr, tran['trans_id']))
                    tr3 = Factory.TagsSelectedButton(text=due_amount,
                                                     on_release=partial(self.select_account_tr, tran['trans_id']))
                    tr4 = Factory.TagsSelectedButton(text=str(account_paid),
                                                     on_release=partial(self.select_account_tr, tran['trans_id']))
                    tr5 = Factory.TagsSelectedButton(text=str(account_paid_on),
                                                     on_release=partial(self.select_account_tr, tran['trans_id']))
                    tr6 = Factory.TagsSelectedButton(text=str(status),
                                                     on_release=partial(self.select_account_tr, tran['trans_id']))
                else:
                    tr1 = Button(text=str(tran['trans_id']),
                                 on_release=partial(self.select_account_tr, tran['trans_id']))
                    tr2 = Button(text=str(billing_period),
                                 on_release=partial(self.select_account_tr, tran['trans_id']))
                    tr3 = Button(text=due_amount,
                                 on_release=partial(self.select_account_tr, tran['trans_id']))
                    tr4 = Button(text=str(account_paid),
                                 on_release=partial(self.select_account_tr, tran['trans_id']))
                    tr5 = Button(text=str(account_paid_on),
                                 on_release=partial(self.select_account_tr, tran['trans_id']))
                    tr6 = Button(text=str(status),
                                 on_release=partial(self.select_account_tr, tran['trans_id']))
                self.inner_layout_1.ids.main_table.add_widget(tr1)
                self.inner_layout_1.ids.main_table.add_widget(tr2)
                self.inner_layout_1.ids.main_table.add_widget(tr3)
                self.inner_layout_1.ids.main_table.add_widget(tr4)
                self.inner_layout_1.ids.main_table.add_widget(tr5)
                self.inner_layout_1.ids.main_table.add_widget(tr6)

    def payment_options_popup(self, *args, **kwargs):
        self.payment_type = 1  # set initial payment type if user does not select a value
        self.payment_popup.title = 'Account Payment Options'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = Factory.ScrollGrid()
        inner_layout_1.ids.main_table.cols = 1
        subtotal = 0
        tax = 0
        aftertax = 0
        credits = 0
        discounts = 0
        due = 0
        if len(self.selected_account_tr) > 0:
            for transaction_id in self.selected_account_tr:
                transactions = Transaction().where({'trans_id': transaction_id})
                if transactions:
                    for transaction in transactions:
                        subtotal += transaction['pretax']
                        tax += transaction['tax']
                        aftertax += transaction['aftertax']
                        credits += transaction['credit']
                        discounts += transaction['discount']
                        due += transaction['total']

        # compare with customer data account running balance total check to see if customer overpaid from last trans
        customers = User().where({'user_id': vars.CUSTOMER_ID})
        account_running_balance = 0
        if customers:
            for customer in customers:
                account_running_balance = customer['account_total']

        if account_running_balance < due:
            due = account_running_balance

        subtotal_label = Factory.BottomLeftFormLabel(text="Subtotal")
        subtotal_input = Factory.CenterVerticalTextInput(text=str('%.2f' % (subtotal)),
                                                         disabled=True)
        tax_label = Factory.BottomLeftFormLabel(text="Tax")
        tax_input = Factory.CenterVerticalTextInput(text=str('%.2f' % (tax)),
                                                    disabled=True)
        aftertax_label = Factory.BottomLeftFormLabel(text="After Tax")
        aftertax_input = Factory.CenterVerticalTextInput(text=str('%.2f' % (aftertax)),
                                                         disabled=True)
        credits_label = Factory.BottomLeftFormLabel(text="Credit")
        credits_input = Factory.CenterVerticalTextInput(text=str('%.2f' % (credits)),
                                                        disabled=True)
        discounts_label = Factory.BottomLeftFormLabel(text="Discount")
        discounts_input = Factory.CenterVerticalTextInput(text=str('%.2f' % (discounts)),
                                                          disabled=True)
        total_label = Factory.BottomLeftFormLabel(text="Total Due")
        self.total_input = Factory.CenterVerticalTextInput(text=str('%.2f' % (due)),
                                                           disabled=True)
        tendered_label = Factory.BottomLeftFormLabel(text="Tendered")
        self.tendered_input = Factory.CenterVerticalTextInput(text=str('%.2f' % (due)),
                                                              on_text_validate=self.calculate_account_change)
        change_label = Factory.BottomLeftFormLabel(text="Change Due")
        self.change_input = Factory.CenterVerticalTextInput(text=str('0.00'))
        payment_type = Factory.BottomLeftFormLabel(text="Payment Type")
        values = ['Check', 'Credit', 'Cash']
        payment_spinner = Spinner(text="Check",
                                  values=values)
        payment_spinner.bind(text=self.set_expected_value)
        last_four_label = Factory.BottomLeftFormLabel(text="Last Four / Check #")
        last_four_input = Factory.CenterVerticalTextInput()
        inner_layout_1.ids.main_table.add_widget(subtotal_label)
        inner_layout_1.ids.main_table.add_widget(subtotal_input)
        inner_layout_1.ids.main_table.add_widget(tax_label)
        inner_layout_1.ids.main_table.add_widget(tax_input)
        inner_layout_1.ids.main_table.add_widget(aftertax_label)
        inner_layout_1.ids.main_table.add_widget(aftertax_input)
        inner_layout_1.ids.main_table.add_widget(credits_label)
        inner_layout_1.ids.main_table.add_widget(credits_input)
        inner_layout_1.ids.main_table.add_widget(discounts_label)
        inner_layout_1.ids.main_table.add_widget(discounts_input)
        inner_layout_1.ids.main_table.add_widget(total_label)
        inner_layout_1.ids.main_table.add_widget(self.total_input)
        inner_layout_1.ids.main_table.add_widget(tendered_label)
        inner_layout_1.ids.main_table.add_widget(self.tendered_input)
        inner_layout_1.ids.main_table.add_widget(change_label)
        inner_layout_1.ids.main_table.add_widget(self.change_input)
        inner_layout_1.ids.main_table.add_widget(payment_type)
        inner_layout_1.ids.main_table.add_widget(payment_spinner)
        inner_layout_1.ids.main_table.add_widget(last_four_label)
        inner_layout_1.ids.main_table.add_widget(last_four_input)
        inner_layout_1.ids.main_table.add_widget(Label(text=""))  # spacing
        inner_layout_1.ids.main_table.add_widget(Label(text=""))  # spacing
        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="cancel",
                               on_release=self.payment_popup.dismiss)
        pay_button = Button(text="Finish",
                            on_release=self.finish_account_payment)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(pay_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.payment_popup.content = layout
        self.payment_popup.open()

        pass

    def set_expected_value(self, value, *args, **kwargs):

        if value is 'Check':
            payment_type = 3
        elif value is 'Credit':
            payment_type = 1
        else:
            payment_type = 2
        self.payment_type = payment_type

    def calculate_account_change(self, *args, **kwargs):
        change_due = str('%.2f' % (Decimal(self.tendered_input.text) - Decimal(self.total_input.text)))
        self.change_input.text = change_due
        pass

    def select_account_tr(self, transaction_id, *args, **kwargs):
        if transaction_id not in self.selected_account_tr:
            self.selected_account_tr.append(transaction_id)
        else:
            self.selected_account_tr.remove(transaction_id)

        self.make_pay_account_popup_table()

    def finish_account_payment(self, *args, **kwargs):
        errors = 0
        # validate data
        if self.tendered_input.text is '':
            self.tendered_input.hint_text = "Tendered Amount Required"
            self.tendered_input.hint_text_color = ERROR_COLOR
            errors += 1
        else:
            self.tendered_input.hint_text = ""
            self.tendered_input.hint_text_color = DEFAULT_COLOR

        if len(self.selected_account_tr) is 0:
            errors += 1
            popup = Popup()
            popup.title = 'Form Error'
            content = KV.popup_alert('Please select an account invoice and try again.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()

        # save data
        if errors is 0:
            saved = 0
            for transaction_id in self.selected_account_tr:
                trans = Transaction().where({'trans_id': transaction_id})
                previous_total = 0;
                if trans:
                    for tran in trans:
                        previous_total = tran['total']
                account_paid_on = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
                where = {'trans_id': transaction_id}
                data = {'tendered': self.tendered_input.text,
                        'account_paid': previous_total,
                        'account_paid_on': account_paid_on,
                        'status': 1,
                        'type': self.payment_type}
                if Transaction().put(where=where, data=data):
                    saved += 1
            if saved > 0:
                customers = User()
                custs = customers.where({'user_id': vars.CUSTOMER_ID})
                previous_account_total = 0
                if custs:
                    for cust in custs:
                        previous_account_total = cust['account_total']

                new_account_total = '%.2f' % (Decimal(previous_account_total) - Decimal(self.total_input.text))

                update = customers.put(where={'user_id': vars.CUSTOMER_ID}, data={'account_total': new_account_total})
                if update:
                    run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
                    try:
                        run_sync.start()
                    finally:
                        run_sync.join()

                        popup = Popup()
                        popup.title = 'Account Transaction Paid!'
                        content = KV.popup_alert('Successfully paid account transaction.')
                        popup.content = Builder.load_string(content)
                        popup.open()
                        # Beep Sound
                        sys.stdout.write('\a')
                        sys.stdout.flush()
                        self.payment_popup.dismiss()
                        self.main_popup.dismiss()
                        vars.SEARCH_RESULTS_STATUS = True
                        self.reset()
                else:
                    popup = Popup()
                    popup.title = 'Could not save user data'
                    content = KV.popup_alert('User table error, could not save. Please contact administrator')
                    popup.content = Builder.load_string(content)
                    popup.open()
                    # Beep Sound
                    sys.stdout.write('\a')
                    sys.stdout.flush()
                    self.payment_popup.dismiss()
                    self.main_popup.dismiss()
                    vars.SEARCH_RESULTS_STATUS = True
                    self.reset()

        # update server
        pass

    def account_history_popup(self, *args, **kwargs):
        self.main_popup.title = 'Account History'
        layout = BoxLayout(orientation="vertical")
        inner_layout_1 = Factory.ScrollGrid()
        inner_layout_1.ids.main_table.cols = 6
        th1 = KV.invoice_tr(0, 'ID')
        th2 = KV.invoice_tr(0, 'Date')
        th3 = KV.invoice_tr(0, 'Due')
        th4 = KV.invoice_tr(0, 'Paid')
        th5 = KV.invoice_tr(0, 'Paid On')
        th6 = KV.invoice_tr(0, 'Status')
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th1))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th2))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th3))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th4))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th5))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th6))
        transactions = Transaction()
        trans = transactions.where({'customer_id': vars.CUSTOMER_ID,
                                    'ORDER_BY': 'id desc'})
        if (len(trans) > 0):
            for tran in trans:
                billing_period_format = datetime.datetime.strptime(tran['created_at'], "%Y-%m-%d %H:%M:%S")
                billing_period = billing_period_format.strftime("%b %Y")
                due_amount = str('$%.2f' % (tran['total']))
                account_paid_format = tran['account_paid'] if tran['account_paid'] else False
                account_paid = str('$%.2f' % (account_paid_format)) if account_paid_format else 'Not Paid'
                if tran['status'] is 1:
                    status = 'Paid'

                elif tran['status'] is 2:
                    status = 'Bill Sent'
                else:
                    status = 'Current'

                if tran['account_paid_on']:
                    account_paid_on_format = datetime.datetime.strptime(tran['account_paid_on'], "%Y-%m-%d %H:%M:%S")
                    account_paid_on = account_paid_on_format.strftime("%m/%d/%y %I:%M %p")
                else:
                    account_paid_on = 'Not Paid'

                if tran['trans_id'] in self.selected_account_tr:
                    tr1 = Factory.TagsSelectedButton(text=str(tran['trans_id']),
                                                     on_release=partial(self.show_invoice_details, tran['trans_id']))
                    tr2 = Factory.TagsSelectedButton(text=str(billing_period),
                                                     on_release=partial(self.show_invoice_details, tran['trans_id']))
                    tr3 = Factory.TagsSelectedButton(text=due_amount,
                                                     on_release=partial(self.show_invoice_details, tran['trans_id']))
                    tr4 = Factory.TagsSelectedButton(text=str(account_paid),
                                                     on_release=partial(self.show_invoice_details, tran['trans_id']))
                    tr5 = Factory.TagsSelectedButton(text=str(account_paid_on),
                                                     on_release=partial(self.show_invoice_details, tran['trans_id']))
                    tr6 = Factory.TagsSelectedButton(text=str(status),
                                                     on_release=partial(self.show_invoice_details, tran['trans_id']))
                else:
                    tr1 = Button(text=str(tran['trans_id']),
                                 on_release=partial(self.show_invoice_details, tran['trans_id']))
                    tr2 = Button(text=str(billing_period),
                                 on_release=partial(self.show_invoice_details, tran['trans_id']))
                    tr3 = Button(text=due_amount,
                                 on_release=partial(self.show_invoice_details, tran['trans_id']))
                    tr4 = Button(text=str(account_paid),
                                 on_release=partial(self.show_invoice_details, tran['trans_id']))
                    tr5 = Button(text=str(account_paid_on),
                                 on_release=partial(self.show_invoice_details, tran['trans_id']))
                    tr6 = Button(text=str(status),
                                 on_release=partial(self.show_invoice_details, tran['trans_id']))
                inner_layout_1.ids.main_table.add_widget(tr1)
                inner_layout_1.ids.main_table.add_widget(tr2)
                inner_layout_1.ids.main_table.add_widget(tr3)
                inner_layout_1.ids.main_table.add_widget(tr4)
                inner_layout_1.ids.main_table.add_widget(tr5)
                inner_layout_1.ids.main_table.add_widget(tr6)

        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="cancel",
                               on_release=self.main_popup.dismiss)
        inner_layout_2.add_widget(cancel_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.main_popup.content = layout
        self.main_popup.open()

    def show_invoice_details(self, transaction_id, *args, **kwargs):
        popup = Popup()
        popup.title = 'Account Transaction Invoice Details'
        layout = BoxLayout(orientation="vertical")
        inner_layout_1 = Factory.ScrollGrid()
        inner_layout_1.ids.main_table.cols = 7
        th1 = KV.invoice_tr(0, 'ID')
        th2 = KV.invoice_tr(0, 'Drop')
        th3 = KV.invoice_tr(0, 'Due')
        th4 = KV.invoice_tr(0, 'Qty')
        th5 = KV.invoice_tr(0, 'Subtotal')
        th6 = KV.invoice_tr(0, 'Tax')
        th7 = KV.invoice_tr(0, 'Total')

        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th1))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th2))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th3))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th4))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th5))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th6))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th7))

        invoices = Invoice().where({'transaction_id': transaction_id})
        if invoices:
            for invoice in invoices:
                drop_date_format = datetime.datetime.strptime(invoice['created_at'], "%Y-%m-%d %H:%M:%S")
                due_date_format = datetime.datetime.strptime(invoice['due_date'], "%Y-%m-%d %H:%M:%S")
                drop_date = drop_date_format.strftime('%m/%d/%y')
                due_date = due_date_format.strftime('%m/%d/%y')
                td1 = Button(text=str(invoice['invoice_id']),
                             on_release=partial(self.account_view_items, invoice['invoice_id']))
                td2 = Factory.TopLeftFormButton(text=str(drop_date),
                                                on_release=partial(self.account_view_items, invoice['invoice_id']))
                td3 = Factory.TopLeftFormButton(text=str(due_date),
                                                on_release=partial(self.account_view_items, invoice['invoice_id']))
                td4 = Button(text=str(invoice['quantity']),
                             on_release=partial(self.account_view_items, invoice['invoice_id']))
                td5 = Button(text=str('$%.2f' % invoice['pretax']),
                             on_release=partial(self.account_view_items, invoice['invoice_id']))
                td6 = Button(text=str('$%.2f' % invoice['tax']),
                             on_release=partial(self.account_view_items, invoice['invoice_id']))
                td7 = Button(text=str('$%.2f' % invoice['total']),
                             on_release=partial(self.account_view_items, invoice['invoice_id']))
                inner_layout_1.ids.main_table.add_widget(td1)
                inner_layout_1.ids.main_table.add_widget(td2)
                inner_layout_1.ids.main_table.add_widget(td3)
                inner_layout_1.ids.main_table.add_widget(td4)
                inner_layout_1.ids.main_table.add_widget(td5)
                inner_layout_1.ids.main_table.add_widget(td6)
                inner_layout_1.ids.main_table.add_widget(td7)

        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="cancel",
                               on_release=popup.dismiss)
        inner_layout_2.add_widget(cancel_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

        pass

    def account_view_items(self, invoice_id, *args, **kwargs):
        popup = Popup()
        popup.title = 'Account Transaction Invoice Details'
        layout = BoxLayout(orientation="vertical")
        inner_layout_1 = Factory.ScrollGrid()
        inner_layout_1.ids.main_table.cols = 6
        th1 = KV.invoice_tr(0, 'ID')
        th2 = KV.invoice_tr(0, 'Name')
        th3 = KV.invoice_tr(0, 'Color')
        th4 = KV.invoice_tr(0, 'Memo')
        th5 = KV.invoice_tr(0, 'Qty')
        th6 = KV.invoice_tr(0, 'Subtotal')

        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th1))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th2))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th3))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th4))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th5))
        inner_layout_1.ids.main_table.add_widget(Builder.load_string(th6))

        invoice_items = InvoiceItem().where({'invoice_id': invoice_id})
        if invoice_items:
            for ii in invoice_items:
                item_id = ii['item_id']
                inventory_items = InventoryItem().where({'item_id': item_id})
                item_name = None
                if inventory_items:
                    for iitem in inventory_items:
                        item_name = iitem['name']
                td1 = Button(text=str(ii['invoice_id']))
                td2 = Button(text=str(item_name))
                td3 = Button(text=str(ii['color']))
                td4 = Factory.TopLeftFormButton(text=str(ii['memo']))
                td5 = Button(text=str(ii['quantity']))
                td6 = Button(text=str('$%.2f' % ii['pretax']))

                inner_layout_1.ids.main_table.add_widget(td1)
                inner_layout_1.ids.main_table.add_widget(td2)
                inner_layout_1.ids.main_table.add_widget(td3)
                inner_layout_1.ids.main_table.add_widget(td4)
                inner_layout_1.ids.main_table.add_widget(td5)
                inner_layout_1.ids.main_table.add_widget(td6)

        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="cancel",
                               on_release=popup.dismiss)
        inner_layout_2.add_widget(cancel_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()


class SearchResultsScreen(Screen):
    """Takes in a customer searched dictionary and gives a table to select which customer we want to find
    once the user selects the customer gives an action to go back to the search screen with the correct
    customer id"""
    search_results_table = ObjectProperty(None)
    search_results_footer = ObjectProperty(None)
    search_results_label = ObjectProperty(None)

    def get_results(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
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
                text_color = 'e5e5e5' if even_odd % 2 == 0 else '000000'
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

    def open_popup(self, *args, **kwargs):
        SYNC_POPUP.title = "Loading"
        content = KV.popup_alert("Please wait while gather information on the selected customer..")
        SYNC_POPUP.content = Builder.load_string(content)
        SYNC_POPUP.open()

    def next(self):
        if vars.ROW_SEARCH[1] + 10 >= vars.ROW_CAP:
            vars.ROW_SEARCH = vars.ROW_CAP - 10, vars.ROW_CAP
        else:
            vars.ROW_SEARCH = vars.ROW_SEARCH[1] + 1, vars.ROW_SEARCH[1] + 10
        data = {
            'last_name': '"%{}%"'.format(vars.SEARCH_TEXT),
            'ORDER_BY': 'last_name ASC',
            'LIMIT': '{},{}'.format(vars.ROW_SEARCH[0], 10)
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
            'LIMIT': '{},{}'.format(vars.ROW_SEARCH[0], 10)
        }
        customers = User()
        cust1 = customers.like(data)
        vars.SEARCH_RESULTS = cust1
        self.search_results_label.text = "[color=000000]Showing rows [b]{}[/b] - [b]{}[/b] out of [b]{}[/b][/color]".format(
            vars.ROW_SEARCH[0], vars.ROW_SEARCH[1], vars.ROW_CAP
        )
        self.get_results()

    def customer_select(self, customer_id, *args, **kwargs):
        SYNC_POPUP.title = "Loading"
        content = KV.popup_alert("Gathering information on selected customer. Please wait...")
        SYNC_POPUP.content = Builder.load_string(content)
        SYNC_POPUP.open()
        Clock.schedule_once(partial(self.customer_select_sync, customer_id))
        print(customer_id)

    def customer_select_sync(self, customer_id, *args, **kwargs):
        # sync db
        run_sync = threading.Thread(target=SYNC.db_sync,args=[vars.COMPANY_ID])
        try:
            run_sync.start()
        finally:
            run_sync.join()
            print('sync now finished')
            vars.SEARCH_RESULTS_STATUS = True
            vars.ROW_CAP = 0
            vars.CUSTOMER_ID = customer_id
            vars.INVOICE_ID = None
            vars.ROW_SEARCH = 0, 10
            self.parent.current = 'search'
            # last 10 setup
            vars.update_last_10()
            SYNC_POPUP.dismiss()


class SettingsScreen(Screen):
    def accounts_page(self):
        webbrowser.open("https://www.jayscleaners.com/accounts")

    pass

    def inventories_page(self):
        webbrowser.open("https://www.jayscleaners.com/inventories")

    pass


class TaxesScreen(Screen):
    tax_rate_input = ObjectProperty(None)

    def reset(self):
        # Pause Schedule
        SCHEDULER.remove_all_jobs()
        taxes = Tax()
        tax_rate = None
        tax_data = taxes.where({'company_id': vars.COMPANY_ID, 'ORDER_BY': 'id asc', 'LIMIT': 1})
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
                popup = Popup()
                popup.title = 'Update Taxes'
                popup.size_hint = (None, None)
                popup.size = (800, 600)
                popup.content = Builder.load_string(KV.popup_alert('Successfully updated tax!'))
                popup.open()
            else:
                popup = Popup()
                popup.title = 'Error On Update'
                popup.size_hint = (None, None)
                popup.size = (800, 600)
                popup.content = Builder.load_string(KV.popup_alert('Could not update tax rate! Please try again.'))
                popup.open()
        else:
            self.tax_rate_input.hint_text = "Enter Tax Rate"
            self.tax_rate_input.hint_text_color = ERROR_COLOR


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
        SCHEDULER.remove_all_jobs()
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
        invitems = InvoiceItem().where({'invoice_items_id': self.search_input.text})
        if invitems:
            for invitem in invitems:
                item_id = invitem['item_id']
                company_id = invitem['company_id']
                self.invoice_id = invitem['invoice_id']
                self.company_id = company_id
                companies = Company().where({'company_id': company_id})
                if companies:
                    for company in companies:
                        company_name = company['name']
                else:
                    company_name = 'Store Name'
                location = int(invitem['status']) - 1
                locations = InvoiceItem().prepareLocationList()
                location_name = locations[location]
                item_name = InventoryItem().getItemName(item_id)
                self.company_select.text = company_name
                self.company_select.values = Company().prepareCompanyList()
                self.location_select.text = location_name
                self.location_select.values = locations
                self.item_name.text = item_name
                self.item_color.text = invitem['color'] if invitem['color'] else ''
                self.item_memo.text = invitem['memo'] if invitem['memo'] else ''
                self.item_pretax.text = str('{:,.2f}'.format(invitem['pretax']))
                self.new_pretax = list(str(int(invitem['pretax'] * 100)))
                self.item_tax.text = str('{:,.2f}'.format(invitem['tax']))
                self.item_total.text = str('{:,.2f}'.format(invitem['total']))
                self.new_total = list(str(int(invitem['total'] * 100)))
        else:
            popup = Popup()
            popup.title = 'No Such Invoice Item'
            content = KV.popup_alert('Could not find any invoice item with that id. Please try again')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()
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
                    vars.WORKLIST.append("Sync")
                    threads_start()
                    # alert the user
                    popup = Popup()
                    popup.title = 'Update Invoice Item Success'
                    content = KV.popup_alert('Successfully updated the invoice item.')
                    popup.content = Builder.load_string(content)
                    popup.open()
                    # Beep Sound
                    sys.stdout.write('\a')
                    sys.stdout.flush()

        pass


class TextForm(TextInput):

    def __init__(self, **kwargs):
        super(TextForm, self).__init__(**kwargs)
        self.bind(on_text_validate=self.next_on_validate)

    @staticmethod
    def next_on_validate(instance):
        """Change the focus when Enter is pressed.
        """
        next  = instance._get_focus_next('focus_next')
        if next:
            instance.focus = False
            next.focus = True


class ScreenManagement(ScreenManager):
    pass


presentation = Builder.load_file("./kv/main.kv")


class MainApp(App):
    def build(self):
        self.title = 'Jays POS'
        return presentation


if __name__ == "__main__":
    MainApp().run()
