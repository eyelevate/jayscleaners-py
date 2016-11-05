import json
import sys
import platform
import time
import datetime
import os
import re
from collections import OrderedDict

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
from kv_generator import KvString
from jobs import Job
from static import Static
import threading
import queue
import authorize
from escpos import *
from escpos.printer import Usb
from escpos.exceptions import USBNotFoundError
from escpos.exceptions import TextError
import phonenumbers
from threading import Thread
import usb.core
import usb.util
import webbrowser
import math

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
        popup = Popup()
        popup.size_hint = (None, None)
        popup.size = '600sp', '400sp'
        popup.title = 'Login Screen'

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
                    SYNC.company_id = user1['company_id']
                print_data = Printer().where({'company_id': auth_user.company_id, 'type': 1})
                if print_data:
                    for pr in print_data:
                        self.print_setup(hex(int(pr['vendor_id'], 16)), hex(int(pr['product_id'], 16)))

                print_data_tag = Printer().where({'company_id': auth_user.company_id, 'type': 2})
                if print_data_tag:
                    for prt in print_data_tag:
                        self.print_setup_tag(hex(int(prt['vendor_id'], 16)), hex(int(prt['product_id'], 16)))
                popup.title = 'Authentication Success!'
                popup.content = Builder.load_string(
                    KV.popup_alert('You are now logged in as {}!'.format(user.username)))
                self.login_popup.dismiss()
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
                    print_data = Printer().where({'company_id': auth_user.company_id, 'type': 1})
                    if print_data:
                        for pr in print_data:
                            self.print_setup(hex(int(pr['vendor_id'], 16)), hex(int(pr['product_id'], 16)))
                    print_data_tag = Printer().where({'company_id': auth_user.company_id, 'type': 2})
                    if print_data_tag:
                        for prt in print_data_tag:
                            self.print_setup_tag(hex(int(prt['vendor_id'], 16)), hex(int(prt['product_id'], 16)))

                    SYNC.company_id = data['company_id']
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
        self.item_search_button.disabled = True

    def db_sync(self, *args, **kwargs):

        # self.update_label.text = 'Connecting to server...
        # sync.migrate()
        # SYNC.db_sync()

        # test multithreading here
        vars.WORKLIST.append("Sync")
        threads_start()

        # sync.get_chunk(table='invoice_items',start=140001,end=150000)

        # self.update_label.text = 'Server updated at {}'.format()

    def sync_db(self):
        sync = Sync()

        # sync.migrate()

        sync.get_chunk(table='inventory_items', start=0, end=1000)

        # vars.WORKLIST.append("Sync")
        # threads_start()
    def test_sys(self):
        Sync().migrate()

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
        vendor_id = 0x0419
        product_id = 0x3c01

        # find our device
        dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)

        # was it found?
        if dev is None:
            print('No device Found')

        # set the active configuration. With no arguments, the first
        # configuration will be the active one
        dev.set_configuration()

        # get an endpoint instance
        cfg = dev.get_active_configuration()
        intf = cfg[(0, 0)]

        ep = usb.util.find_descriptor(
            intf,
            # match the first OUT endpoint
            custom_match= \
                lambda e: \
                    usb.util.endpoint_direction(e.bEndpointAddress) == \
                    usb.util.ENDPOINT_OUT)

        assert ep is not None
        print(ep)
        print('printer found')
        # write the data
        ep.write('\x1b40 test \n')

    def print_setup_tag(self, vendor_id, product_id):
        vendor_int = int(vendor_id, 16)
        vendor_id_hex = hex(vendor_int)
        product_int = int(product_id, 16)
        product_id_hex = hex(product_int)
        interface_number = 0
        in_ep = 0x81
        out_ep = 0x02

        # find our device
        dev = usb.core.find(idVendor=vendor_int, idProduct=product_int)
        print(vars.BIXOLON)
        # was it found?
        if dev:

            # set the active configuration. With no arguments, the first
            # configuration will be the active one
            dev.set_configuration()

            # get an endpoint instance
            cfg = dev.get_active_configuration()
            intf = cfg[(0, 0)]
            for cfg in dev:
                sys.stdout.write(str(cfg.bConfigurationValue) + '\n')
                for intf in cfg:
                    interface_number = intf.bInterfaceNumber
                    idx = 0
                    for ep in intf:
                        print(hex(ep.bEndpointAddress))
                        idx += 1
                        if idx is 1:
                            in_ep = ep.bEndpointAddress
                        elif idx is 2:
                            out_ep = ep.bEndpointAddress

            # vars.BIXOLON = Usb(vendor_int, product_int, interface=interface_number, in_ep=130, out_ep=1)
            try:
                vars.BIXOLON = Usb(0x0419, 0x3c01, 0, 0x82, 0x01)
            except AttributeError as e:
                print(e)

        else:
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
        vendor_id_hex = hex(vendor_int)
        product_int = int(product_id, 16)
        product_id_hex = hex(product_int)
        print('{} - {}'.format(vendor_id_hex, product_id_hex))
        interface_number = 0
        in_ep = 0x81
        out_ep = 0x02
        try:
            dev = usb.core.find(idVendor=vendor_int, idProduct=product_int)
            # was it found?
            if dev is None:
                print('Device not found')

            # set the active configuration. With no arguments, the first
            # configuration will be the active one
            dev.set_configuration()

            # get an endpoint instance
            cfg = dev.get_active_configuration()
            for cfg in dev:
                sys.stdout.write(str(cfg.bConfigurationValue) + '\n')
                for intf in cfg:
                    interface_number = intf.bInterfaceNumber
                    idx = 0
                    for ep in intf:
                        idx += 1
                        if idx is 1:
                            in_ep = ep.bEndpointAddress
                        else:
                            out_ep = ep.bEndpointAddress

        except AttributeError:
            print('Error Attribute')
        except TypeError:
            print('Type Error')

        try:
            vars.EPSON = printer.Usb(vendor_int, product_int, interface_number, in_ep, out_ep)
            print('printer set')
        except USBNotFoundError:
            vars.EPSON = False
            popup = Popup()
            popup.title = 'Printer Error'
            content = KV.popup_alert('Unable to locate usb printer.')
            popup.content = Builder.load_string(content)
            popup.open()
            # Beep Sound
            sys.stdout.write('\a')
            sys.stdout.flush()
        except TextError:
            print('Text error')

    def reports_page(self):
        webbrowser.open("http://74.207.240.88/reports")

    def delivery_page(self):
        webbrowser.open("http://74.207.240.88/delivery/overview")


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
        self.set_color_table()
        self.color_hex = ''
        self.color_id = ''
        self.reorder_end_id = False

    pass

    def set_color_table(self):
        self.colors_table.clear_widgets()

        colored = Colored()
        colorings = colored.where({'company_id': auth_user.company_id, 'ORDER_BY': 'ordered asc'})

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
        start_colors = coloreds.where({'color_id': self.reorder_start_id, 'company_id': auth_user.company_id})
        if start_colors:
            for clr in start_colors:
                swap_order[self.reorder_end_id] = clr['ordered']

        end_colors = coloreds.where({'color_id': self.reorder_end_id, 'company_id': auth_user.company_id})
        if end_colors:
            for clr in end_colors:
                swap_order[self.reorder_start_id] = clr['ordered']
        if swap_order:
            for key, index in swap_order.items():
                coloreds.put(where={'color_id': key, 'company_id': auth_user.company_id},
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
        clrds = coloreds.where({'color_id': self.color_id, 'company_id': auth_user.company_id})
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
        new_orders = coloreds.where({'company_id': auth_user.company_id, 'ORDER_BY': 'id desc', 'LIMIT': 1})
        new_order = 1
        if new_orders:
            for no in new_orders:
                ordered = no['ordered']
                new_order = ordered + 1
        coloreds.company_id = auth_user.company_id
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
        put = coloreds.put(where={'color_id': self.color_id, 'company_id': auth_user.company_id},
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
        deleted = coloreds.where({'company_id': auth_user.company_id,
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
        companies = Company().where({'company_id': auth_user.company_id})
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
        put = companies.put(where={'company_id': auth_user.company_id},
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

    def reset(self):
        # reset the inventory table
        self.inventory_panel.clear_widgets()
        self.get_inventory()
        self.summary_table.clear_widgets()
        store_hours = Company().get_store_hours(auth_user.company_id)
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
        taxes = Tax().where({'company_id': auth_user.company_id, 'status': 1})
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

    def set_result_status(self):
        vars.SEARCH_RESULTS_STATUS = True
        self.summary_table.clear_widgets()

    def get_inventory(self):
        inventories = Inventory().where({'company_id': '{}'.format(auth_user.company_id)})
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
                            memo_string.append(item_memo)
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
        # calculate totals
        if len(self.invoice_list):
            for item_key, item_values in self.invoice_list.items():
                for item in item_values:
                    self.quantity += 1
                    self.tags += int(item['tags']) if item['tags'] else 1
                    self.subtotal += float(item['item_price']) if item['item_price'] else 0
            self.tax = self.subtotal * vars.TAX_RATE
            self.discount = 0
            self.total = self.subtotal + self.tax - self.discount
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
        colors = Colored().where({'company_id': auth_user.company_id, 'ORDER_BY': 'ordered asc'})
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
        memos = mmos.where({'company_id': auth_user.company_id,
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

        if self.invoice_list_copy[vars.ITEM_ID]:
            idx = -1
            for items in self.invoice_list_copy[vars.ITEM_ID]:
                idx += 1
                background_color = (0.36862745, 0.36862745, 0.36862745, 1) if idx == self.item_selected_row else (
                    0.89803922, 0.89803922, 0.89803922, 1)
                background_normal = ''
                text_color = 'e5e5e5' if idx == self.item_selected_row else '5e5e5e'
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
        self.items_grid.bind(minimum_height=self.items_grid.setter('height'))

    def add_memo(self, *args, **kwargs):
        if self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]:
            self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]['memo'] = self.memo_text_input.text
            next_row = self.item_selected_row + 1 if (self.item_selected_row + 1) < len(
                self.invoice_list_copy[vars.ITEM_ID]) else 0
            self.item_selected_row = next_row
            self.make_items_table()
            self.memo_text_input.text = ''
            self.memo_list = []

    def color_selected(self, color=False, *args, **kwargs):
        if self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]:
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
        if self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]:
            self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]['color'] = ''
            self.make_items_table()

    def remove_memo(self, *args, **kwargs):
        if self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]:
            self.memo_list = []
            self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]['memo'] = ''
            self.make_items_table()

    def item_row_selected(self, row, *args, **kwargs):
        self.item_selected_row = row
        self.make_items_table()

    def save_memo_color(self, *args, **kwargs):
        if self.invoice_list_copy[vars.ITEM_ID]:
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
                                    memo_string.append(item_memo)
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
                        text_color = 'e5e5e5' if idx == self.item_selected_row else '5e5e5e'

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
        if self.invoice_list_copy[vars.ITEM_ID]:
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
        if self.invoice_list_copy[vars.ITEM_ID][row]:
            self.invoice_list_copy[vars.ITEM_ID][row]['item_price'] = self.adjust_price
            self.make_adjustment_sum_table()
            self.make_adjustment_individual_table()

    def save_price_adjustment(self, *args, **kwargs):

        if self.invoice_list_copy[vars.ITEM_ID]:
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

        store_hours = Company().get_store_hours(auth_user.company_id)
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

        store_hours = Company().get_store_hours(auth_user.company_id)
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
        store_hours = Company().get_store_hours(auth_user.company_id)

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

        button_1 = Factory.PrintButton(text='Customer + Store Copy',
                                       on_press=partial(self.finish_invoice, 2))

        inner_layout_1.add_widget(button_1)
        button_2 = Factory.PrintButton(text='Store Copy Only',
                                       on_press=partial(self.finish_invoice, 1))
        inner_layout_1.add_widget(button_2)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.3))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='Cancel',
                                         on_release=self.print_popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.print_popup.content = layout
        self.print_popup.open()

    def finish_invoice(self, type, *args, **kwargs):
        # determine the types of invoices we need to print
        # set the printer data
        printers = Printer()
        thermal_printers = printers.get_printer_ids(auth_user.company_id, 1)

        # splt up invoice by inventory group
        save_invoice = {}
        save_totals = {}
        save_invoice_items = {}
        inventories = Inventory().where({'company_id': auth_user.company_id})
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
                if len(save_invoice[inventory_id]) > 0:
                    tax_amount = save_totals[inventory_id]['subtotal'] * vars.TAX_RATE
                    total = save_totals[inventory_id]['subtotal'] * (1 + vars.TAX_RATE)

                    # set invoice data to save
                    new_invoice = Invoice()
                    new_invoice.company_id = auth_user.company_id
                    new_invoice.customer_id = vars.CUSTOMER_ID
                    new_invoice.quantity = save_totals[inventory_id]['quantity']
                    new_invoice.pretax = float('%.2f' % (save_totals[inventory_id]['subtotal']))
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
                            'tax': new_invoice.tax,
                            'total': new_invoice.total
                        }
                        save_invoice_items[last_insert_id] = invoice_group
                        idx = -1
                        colors = {}
                        print_invoice[last_insert_id] = {}
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
                            if item_color in colors:
                                colors[item_color] += 1
                            else:
                                colors[item_color] = 1
                            if item_id in print_invoice[last_insert_id]:
                                print_invoice[last_insert_id][item_id]['item_price'] += item_price
                                print_invoice[last_insert_id][item_id]['qty'] += 1
                                print_invoice[last_insert_id][item_id]['colors'] = colors
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
                                    'colors': colors
                                }

            # save the invoices to the db and return the proper invoice_ids
            run_sync = threading.Thread(target=SYNC.run_sync)
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
                            print_sync_totals[new_invoice_id] = {
                                'quantity': invoice['quantity'],
                                'subtotal': invoice['pretax'],
                                'tax': invoice['tax'],
                                'total': invoice['total']
                            }
                            print_sync_invoice[new_invoice_id] = {}
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
                                if item_color in colors:
                                    colors[item_color] += 1
                                else:
                                    colors[item_color] = 1
                                if item_id in print_sync_invoice[new_invoice_id]:

                                    print_sync_invoice[new_invoice_id][item_id]['item_price'] += item_price
                                    print_sync_invoice[new_invoice_id][item_id]['qty'] += 1
                                    if item_memo:
                                        print_sync_invoice[new_invoice_id][item_id]['memos'].append(item_memo)
                                    print_sync_invoice[new_invoice_id][item_id]['colors'] = colors
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
                        new_invoice_item.company_id = auth_user.company_id
                        new_invoice_item.customer_id = vars.CUSTOMER_ID
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
            run_sync2 = threading.Thread(target=SYNC.db_sync)
            try:
                run_sync2.start()
            finally:
                run_sync2.join()
                print('sync invoice items now finished')
                companies = Company()
                comps = companies.where({'company_id': auth_user.company_id}, set=True)

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
                        customers.first_name = user['first_name']
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
                # print invoices
                if vars.EPSON:
                    if type == 2:
                        vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text("{}\n".format(companies.name))
                        vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text("{}\n".format(companies.street))
                        vars.EPSON.text("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                        vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                       invert=False, smooth=False, flip=False)

                        vars.EPSON.text("{}\n".format(Job.make_us_phone(companies.phone)))
                        vars.EPSON.text("{}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                        vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                        vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text("{}\n".format(vars.CUSTOMER_ID))
                        # Print barcode
                        vars.EPSON.barcode('{}'.format(vars.CUSTOMER_ID), 'CODE39', 64, 2, 'OFF', 'B', 'B')

                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('{}, {}\n'.format(customers.last_name.upper(), customers.first_name.upper()))

                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('{}\n'.format(Job.make_us_phone(customers.phone)))
                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('------------------------------------------\n')

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
                                            memo_string.append(item_memo)
                                    if colors:
                                        for color_name, color_amount in colors.items():
                                            if color_name:
                                                color_string.append('{}-{}'.format(color_amount, color_name))

                                    vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                   density=5, invert=False, smooth=False, flip=False)
                                    vars.EPSON.text('{} {}   '.format(item_type, total_qty, item_name))
                                    vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'B', width=1, height=1,
                                                   density=5, invert=False, smooth=False, flip=False)
                                    vars.EPSON.text('{}\n'.format(item_name))
                                    if len(memo_string) > 0:
                                        vars.EPSON.control('HT')
                                        vars.EPSON.control('HT')
                                        vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                       density=5, invert=False, smooth=False, flip=False)
                                        vars.EPSON.text('  {}\n'.format('/ '.join(memo_string)))
                                    if len(color_string):
                                        vars.EPSON.control('HT')
                                        vars.EPSON.control('HT')
                                        vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                       density=5, invert=False, smooth=False, flip=False)
                                        vars.EPSON.text('  {}\n'.format(', '.join(color_string)))

                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('------------------------------------------\n')
                        vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('{} PCS\n'.format(self.quantity))
                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('------------------------------------------\n')
                        # Cut paper
                        vars.EPSON.cut(mode=u"PART")

                        # Print store copies
                        if print_sync_invoice:  # if invoices synced
                            for invoice_id, item_id in print_sync_invoice.items():

                                # start invoice
                                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                               density=5,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text("::COPY::\n")
                                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text("{}\n".format(companies.name))
                                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                               density=5,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text("{}\n".format(Job.make_us_phone(companies.phone)))
                                vars.EPSON.text("{}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2,
                                               density=5,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text(
                                    "READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text("{}\n".format('{0:06d}'.format(invoice_id)))
                                # Print barcode
                                vars.EPSON.barcode('{}'.format('{0:06d}'.format(invoice_id)), 'CODE39', 64, 2, 'OFF',
                                                   'B', 'B')

                                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3,
                                               density=6,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text(
                                    '{}, {}\n'.format(customers.last_name.upper(), customers.first_name.upper()))

                                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                               density=2,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text('{}\n'.format(Job.make_us_phone(customers.phone)))
                                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                               density=1,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text('------------------------------------------\n')

                                if print_sync_invoice[invoice_id]:
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
                                        vars.EPSON.text('{} {}   {}{}{}\n'.format(item_type,
                                                                                  item_qty,
                                                                                  item_name,
                                                                                  ' ' * string_offset,
                                                                                  vars.us_dollar(item_price)))

                                        # vars.EPSON.text('\r\x1b@\x1b\x61\x02{}\n'.format(vars.us_dollar(item_price)))
                                        if len(item_memo) > 0:
                                            vars.EPSON.control('HT')
                                            vars.EPSON.control('HT')
                                            vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                           height=1,
                                                           density=5, invert=False, smooth=False, flip=False)
                                            vars.EPSON.text('  {}\n'.format('/ '.join(item_memo)))
                                        if len(item_color_string) > 0:
                                            vars.EPSON.control('HT')
                                            vars.EPSON.control('HT')
                                            vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                           height=1,
                                                           density=5, invert=False, smooth=False, flip=False)
                                            vars.EPSON.text('  {}\n'.format(', '.join(item_color_string)))

                                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                               density=1,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text('------------------------------------------\n')
                                vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text('{} PCS\n'.format(print_sync_totals[invoice_id]['quantity']))
                                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                               density=1,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text('------------------------------------------\n')
                                vars.EPSON.set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text('    SUBTOTAL:')
                                vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                                string_length = len(vars.us_dollar(print_sync_totals[invoice_id]['subtotal']))
                                string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                                vars.EPSON.text('{}{}\n'.format(' ' * string_offset,
                                                                vars.us_dollar(
                                                                    print_sync_totals[invoice_id]['subtotal'])))
                                vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                                vars.EPSON.text('         TAX:')
                                string_length = len(vars.us_dollar(print_sync_totals[invoice_id]['tax']))
                                string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                                vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                                vars.EPSON.text('{}{}\n'.format(' ' * string_offset,
                                                                vars.us_dollar(print_sync_totals[invoice_id]['tax'])))
                                vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                                vars.EPSON.text('       TOTAL:')
                                vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                                string_length = len(vars.us_dollar(print_sync_totals[invoice_id]['total']))
                                string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                                vars.EPSON.text('{}{}\n'.format(' ' * string_offset,
                                                                vars.us_dollar(print_sync_totals[invoice_id]['total'])))
                                vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                                vars.EPSON.text('     BALANCE:')
                                string_length = len(vars.us_dollar(print_sync_totals[invoice_id]['total']))
                                string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                                vars.EPSON.text('{}{}\n\n'.format(' ' * string_offset,
                                                                  vars.us_dollar(
                                                                      print_sync_totals[invoice_id]['total'])))
                                if item_type == 'L':
                                    # get customer mark
                                    marks = Custid()
                                    marks_list = marks.where({'customer_id': vars.CUSTOMER_ID, 'status': 1})
                                    if marks_list:
                                        m_list = []
                                        for mark in marks_list:
                                            m_list.append(mark['mark'])
                                        vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=3, height=4,
                                                       density=8, invert=False, smooth=False, flip=False)
                                        vars.EPSON.text('{}\n\n'.format(', '.join(m_list)))

                                # Cut paper
                                vars.EPSON.cut(mode=u"PART")
                        else:
                            for invoice_id, item_id in print_invoice.items():

                                # start invoice
                                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text("{}\n".format(companies.name))
                                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                               density=5,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text("{}\n".format(Job.make_us_phone(companies.phone)))
                                vars.EPSON.text("{}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=2, height=3, density=5,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text(
                                    "READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text("--{}--\n".format('{0:06d}'.format(invoice_id)))
                                # Print barcode
                                vars.EPSON.barcode('{}'.format('{0:06d}'.format(invoice_id)), 'CODE39', 64, 2, 'OFF',
                                                   'B', 'B')

                                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3,
                                               density=6,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text(
                                    '{}, {}\n'.format(customers.last_name.upper(), customers.first_name.upper()))

                                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                               density=2,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text('{}\n'.format(Job.make_us_phone(customers.phone)))
                                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                               density=1,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text('------------------------------------------\n')

                                if print_sync_invoice[invoice_id][item_id]:
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
                                        vars.EPSON.text('{} {}   {}{}{}\n'.format(item_type,
                                                                                  item_qty,
                                                                                  item_name,
                                                                                  ' ' * string_offset,
                                                                                  vars.us_dollar(item_price)))

                                        if len(item_memo) > 0:
                                            vars.EPSON.control('HT')
                                            vars.EPSON.control('HT')
                                            vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                           height=1,
                                                           density=5, invert=False, smooth=False, flip=False)
                                            vars.EPSON.text('  {}\n'.format('/ '.join(item_memo)))
                                        if len(item_color_string) > 0:
                                            vars.EPSON.control('HT')
                                            vars.EPSON.control('HT')
                                            vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                           height=1,
                                                           density=5, invert=False, smooth=False, flip=False)
                                            vars.EPSON.text('  {}\n'.format(', '.join(item_color_string)))

                                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                               density=1,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text('------------------------------------------\n')
                                vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text('{} PCS\n'.format(print_sync_totals[invoice_id]['quantity']))
                                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                               density=1,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text('------------------------------------------\n')
                                vars.EPSON.set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text('    SUBTOTAL:')
                                vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                                string_length = len(vars.us_dollar(print_totals[invoice_id]['subtotal']))
                                string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                                vars.EPSON.text('{}{}\n'.format(' ' * string_offset,
                                                                vars.us_dollar(print_totals[invoice_id]['subtotal'])))
                                vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                                vars.EPSON.text('         TAX:')
                                string_length = len(vars.us_dollar(print_totals[invoice_id]['tax']))
                                string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                                vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                                vars.EPSON.text('{}{}\n'.format(' ' * string_offset,
                                                                vars.us_dollar(print_totals[invoice_id]['tax'])))
                                vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                                vars.EPSON.text('       TOTAL:')
                                vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                                string_length = len(vars.us_dollar(print_totals[invoice_id]['total']))
                                string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                                vars.EPSON.text('{}{}\n'.format(' ' * string_offset,
                                                                vars.us_dollar(print_totals[invoice_id]['total'])))
                                vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                                vars.EPSON.text('     BALANCE:')
                                string_length = len(vars.us_dollar(print_totals[invoice_id]['total']))
                                string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                                vars.EPSON.text('{}{}\n\n'.format(' ' * string_offset,
                                                                  vars.us_dollar(print_totals[invoice_id]['total'])))
                                if customers.invoice_memo:
                                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3,
                                                   density=5,
                                                   invert=False, smooth=False, flip=False)
                                    vars.EPSON.text('{}\n'.format(customers.invoice_memo))
                                if item_type == 'L':
                                    # get customer mark
                                    marks = Custid()
                                    marks_list = marks.where({'customer_id': vars.CUSTOMER_ID, 'status': 1})
                                    if marks_list:
                                        m_list = []
                                        for mark in marks_list:
                                            m_list.append(mark['mark'])
                                        vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=3, height=4,
                                                       density=8, invert=False, smooth=False, flip=False)
                                        vars.EPSON.text('{}\n\n'.format(', '.join(m_list)))

                                # Cut paper
                                vars.EPSON.cut(mode=u"PART")
                else:
                    popup = Popup()
                    popup.title = 'Printer Error'
                    content = KV.popup_alert('Could not find usb.')
                    popup.content = Builder.load_string(content)
                    popup.open()
                    # Beep Sound
                    sys.stdout.write('\a')
                    sys.stdout.flush()

                    # PRINT TAG

                if vars.BIXOLON:
                    print('Starting tag printing')
                    if len(save_invoice_items) > 0:
                        for iitems_id in save_invoice_items:
                            for item in save_invoice_items[iitems_id]:
                                invoice_id = item['invoice_id']
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
                                vars.BIXOLON.hw('RESET')
                                vars.BIXOLON.text('\x1b\x40')
                                vars.BIXOLON.text('\x1b\x6d')
                                print('next step')
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

                                                vars.BIXOLON.text('\x1b!\x30')  # QUAD SIZE
                                                vars.BIXOLON.text('{}{}\n'.format(text_left, text_right))
                                                vars.BIXOLON.hw('RESET')
                                                vars.BIXOLON.text('\x1b!\x00')
                                                vars.BIXOLON.text(name_number_string)
                                                vars.BIXOLON.text('\n')
                                                vars.BIXOLON.text('{0:06d}'.format(int(invoice_item_id)))
                                                vars.BIXOLON.text(' {} {}'.format(item_name, item_color))
                                                if memo_string:
                                                    vars.BIXOLON.text('\n{}'.format(memo_string))
                                                    memo_len = '\n\n\n' if len(
                                                        memo_string) <= 32 else '\n\n\n' + '\n' * int(
                                                        (len(memo_string)) / 32)
                                                    vars.BIXOLON.text(memo_len)
                                                    vars.BIXOLON.text('\x1b\x6d')

                                                else:

                                                    vars.BIXOLON.text('\n\n\n')
                                                    vars.BIXOLON.text('\x1b\x6d')
                    if len(laundry_to_print) is 0:
                        # FINAL CUT
                        vars.BIXOLON.hw('RESET')
                        vars.BIXOLON.cut()
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
                                id_id_string = '{}{}{}'.format(invoice_item_id_start, ' ' * id_offset,
                                                               invoice_item_id_end)

                            except IndexError:
                                name_name_string = '{}'.format(text_name)
                                mark_mark_string = '{}'.format(shirt_mark)
                                id_id_string = '{}'.format(invoice_item_id_start)

                            vars.BIXOLON.text('\x1b!\x30')  # QUAD SIZE
                            vars.BIXOLON.text(mark_mark_string)
                            vars.BIXOLON.text('\n')
                            vars.BIXOLON.hw('RESET')
                            vars.BIXOLON.text('\x1b!\x00')
                            vars.BIXOLON.text(name_name_string)
                            vars.BIXOLON.text('\n')
                            vars.BIXOLON.text(id_id_string)

                            vars.BIXOLON.text('\n\n\n\x1b\x6d')
                        # FINAL CUT
                        vars.BIXOLON.hw('RESET')
                        vars.BIXOLON.cut()

        self.set_result_status()
        self.print_popup.dismiss()


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

    def reset(self):
        # reset the inventory table
        self.inventory_panel.clear_widgets()
        self.get_inventory()
        self.summary_table.clear_widgets()
        store_hours = Company().get_store_hours(auth_user.company_id)
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

        total_tags = InvoiceItem().total_tags(vars.INVOICE_ID)
        invoice_items = InvoiceItem().where({'invoice_id': vars.INVOICE_ID})
        self.invoice_list = OrderedDict()
        self.invoice_list_copy = OrderedDict()
        customers = User().where({'user_id': vars.CUSTOMER_ID})
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

        invoices = Invoice().where({'invoice_id': vars.INVOICE_ID})
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
        taxes = Tax().where({'company_id': auth_user.company_id, 'status': 1})
        if taxes:
            for tax in taxes:
                vars.TAX_RATE = tax['rate']
        else:
            vars.TAX_RATE = 0.096
        self.create_summary_table()
        self.create_summary_totals()
        self.deleted_rows = []

    def set_result_status(self):
        vars.SEARCH_RESULTS_STATUS = True
        self.summary_table.clear_widgets()

    def get_inventory(self):
        inventories = Inventory().where({'company_id': '{}'.format(auth_user.company_id)})
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

        if qty == 'C':
            self.qty_clicks = 0
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
                            memo_string.append(item_memo)
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
            idx = -1
            for row in self.invoice_list[vars.ITEM_ID]:
                idx += 1
                if 'invoice_items_id' in row:
                    self.invoice_list[vars.ITEM_ID][idx]['delete'] = True
                    self.deleted_rows.append(row['invoice_items_id'])

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
        # calculate totals
        if len(self.invoice_list):
            for item_key, item_values in self.invoice_list.items():
                for item in item_values:
                    self.quantity += 1
                    self.tags += int(item['tags']) if item['tags'] else 1
                    self.subtotal += float(item['item_price']) if item['item_price'] else 0
            self.tax = self.subtotal * vars.TAX_RATE
            self.discount = 0
            self.total = self.subtotal + self.tax - self.discount
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
        colors = Colored().where({'company_id': auth_user.company_id, 'ORDER_BY': 'ordered asc'})
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
                color_btn.background_color = vars.color_rgba(color['color'])
                color_grid.add_widget(color_btn)
        color_layout.add_widget(color_grid)
        # memo section
        memo_layout = BoxLayout(orientation='vertical',
                                size_hint=(1, 0.5))
        memo_title = Label(markup=True,
                           pos_hint={'top': 1},
                           text='[b]Create Memo[/b]',
                           size_hint=(1, 0.1))
        memo_inner_layout = BoxLayout(orientation='horizontal',
                                      size_hint=(1, 0.4))
        memo_layout.add_widget(memo_title)
        memo_text_input = TextInput(text='',
                                    size_hint=(0.9, 1),
                                    multiline=True)
        try:
            memo_inner_layout.add_widget(memo_text_input)
        except WidgetException:
            memo_inner_layout.remove_widget(memo_text_input)
            memo_inner_layout.add_widget(memo_text_input)
        self.memo_text_input = memo_text_input
        memo_add_button = Button(text='Add',
                                 size_hint=(0.1, 1),
                                 on_press=self.add_memo)
        memo_inner_layout.add_widget(memo_add_button)
        memo_layout.add_widget(memo_inner_layout)
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

        if self.invoice_list_copy[vars.ITEM_ID]:
            idx = -1
            for items in self.invoice_list_copy[vars.ITEM_ID]:
                idx += 1
                background_color = (0.36862745, 0.36862745, 0.36862745, 1) if idx == self.item_selected_row else (
                    0.89803922, 0.89803922, 0.89803922, 1)
                background_normal = ''
                text_color = 'e5e5e5' if idx == self.item_selected_row else '5e5e5e'
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
        self.items_grid.bind(minimum_height=self.items_grid.setter('height'))

    def add_memo(self, *args, **kwargs):
        if self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]:
            self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]['memo'] = self.memo_text_input.text
            next_row = self.item_selected_row + 1 if (self.item_selected_row + 1) < len(
                self.invoice_list_copy[vars.ITEM_ID]) else 0
            self.item_selected_row = next_row
            self.make_items_table()
            self.memo_text_input.text = ''

    def color_selected(self, color=False, *args, **kwargs):
        if self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]:
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
        if self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]:
            self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]['color'] = ''
            self.make_items_table()

    def remove_memo(self, *args, **kwargs):
        if self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]:
            self.invoice_list_copy[vars.ITEM_ID][self.item_selected_row]['memo'] = ''
            self.make_items_table()

    def item_row_selected(self, row, *args, **kwargs):
        self.item_selected_row = row
        self.make_items_table()

    def save_memo_color(self, *args, **kwargs):
        if self.invoice_list_copy[vars.ITEM_ID]:
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
                                    memo_string.append(item_memo)
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
                        text_color = 'e5e5e5' if idx == self.item_selected_row else '5e5e5e'

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
        if self.invoice_list_copy[vars.ITEM_ID]:
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
        if self.invoice_list_copy[vars.ITEM_ID][row]:
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

        store_hours = Company().get_store_hours(auth_user.company_id)
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

        store_hours = Company().get_store_hours(auth_user.company_id)
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
        store_hours = Company().get_store_hours(auth_user.company_id)

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
                                       on_press=partial(self.finish_invoice, 2))

        inner_layout_1.add_widget(button_1)
        button_2 = Factory.PrintButton(text='Store Only',
                                       on_press=partial(self.finish_invoice, 1))
        inner_layout_1.add_widget(button_2)
        button_3 = Factory.PrintButton(text='No Print',
                                       on_press=partial(self.finish_invoice, False))
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

    def finish_invoice(self, type, *args, **kwargs):
        # determine the types of invoices we need to print

        # set the printer data

        if self.deleted_rows:
            for invoice_items_id in self.deleted_rows:
                invoice_items = InvoiceItem()
                invoice_items.id = invoice_items.get_id(invoice_items_id)
                if invoice_items.delete():
                    print('deleted row {}'.format(invoice_items.id))

        if self.invoice_list:
            invoice_items = InvoiceItem()
            print_invoice = {}
            print_invoice[vars.INVOICE_ID] = {}
            for invoice_item_key, invoice_item_value in self.invoice_list.items():
                colors = {}
                for iivalue in invoice_item_value:
                    qty = iivalue['qty']
                    pretax = float(iivalue['item_price']) if iivalue['item_price'] else 0
                    tax = float('%.2f' % (pretax * vars.TAX_RATE))
                    total = float('%.2f' % (pretax * (1 + vars.TAX_RATE)))
                    item_id = iivalue['item_id']
                    inventory_id = InventoryItem().getInventoryId(item_id)
                    item_name = iivalue['item_name']
                    item_price = iivalue['item_price']
                    item_type = iivalue['type']
                    item_color = iivalue['color']
                    item_memo = iivalue['memo']
                    if item_color in colors:
                        colors[item_color] += 1
                    else:
                        colors[item_color] = 1
                    if item_id in print_invoice[vars.INVOICE_ID]:
                        print_invoice[vars.INVOICE_ID][item_id]['item_price'] += item_price
                        print_invoice[vars.INVOICE_ID][item_id]['qty'] += 1
                        print_invoice[vars.INVOICE_ID][item_id]['colors'] = colors
                        if item_memo:
                            print_invoice[vars.INVOICE_ID][item_id]['memos'].append(item_memo)
                    else:

                        print_invoice[vars.INVOICE_ID][item_id] = {
                            'item_id': item_id,
                            'type': item_type,
                            'name': item_name,
                            'item_price': item_price,
                            'qty': 1,
                            'memos': [item_memo] if item_memo else [],
                            'colors': colors
                        }
                    if 'invoice_items_id' in iivalue:
                        invoice_items.put(where={'invoice_items_id': iivalue['invoice_items_id']},
                                          data={'quantity': iivalue['qty'],
                                                'color': iivalue['color'] if iivalue['color'] else None,
                                                'memo': iivalue['memo'] if iivalue['memo'] else None,
                                                'pretax': pretax,
                                                'tax': tax,
                                                'total': total})
                        print('invoice item updated')
                    else:
                        new_invoice_item = InvoiceItem()
                        new_invoice_item.company_id = auth_user.company_id
                        new_invoice_item.customer_id = vars.CUSTOMER_ID
                        new_invoice_item.invoice_id = vars.INVOICE_ID
                        new_invoice_item.item_id = iivalue['item_id']
                        new_invoice_item.inventory_id = inventory_id if inventory_id else None
                        new_invoice_item.quantity = iivalue['qty']
                        new_invoice_item.color = iivalue['color'] if iivalue['color'] else None
                        new_invoice_item.memo = iivalue['memo'] if iivalue['memo'] else None
                        new_invoice_item.pretax = pretax
                        new_invoice_item.tax = tax
                        new_invoice_item.total = total
                        new_invoice_item.status = 1
                        if new_invoice_item.add():
                            print('new item added')
                            # delete rows
        vars.WORKLIST.append("Sync")
        threads_start()

        Invoice().put(where={'invoice_id': vars.INVOICE_ID},
                      data={'quantity': self.tags,
                            'pretax': '%.2f' % self.subtotal,
                            'tax': '%.2f' % self.tax,
                            'total': '%.2f' % self.total,
                            'due_date': '{}'.format(self.due_date.strftime("%Y-%m-%d %H:%M:%S"))})

        vars.WORKLIST.append("Sync")
        threads_start()

        # print invoices
        if vars.EPSON:

            companies = Company()
            comps = companies.where({'company_id': auth_user.company_id}, set=True)
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
                    customers.first_name = user['first_name']
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

            if not type or not vars.EPSON:
                self.set_result_status()
                self.print_popup.dismiss()
                pass
            elif type == 2:
                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text("{}\n".format(companies.name))
                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text("{}\n".format(companies.street))
                vars.EPSON.text("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                               invert=False, smooth=False, flip=False)

                vars.EPSON.text("{}\n".format(Job.make_us_phone(companies.phone)))
                vars.EPSON.text("edited on: {}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text("{}\n".format(vars.CUSTOMER_ID))
                # Print barcode
                vars.EPSON.barcode('{}'.format(vars.CUSTOMER_ID), 'CODE39', 64, 2, 'OFF', 'B', 'B')

                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('{}, {}\n'.format(customers.last_name.upper(), customers.first_name.upper()))

                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('{}\n'.format(Job.make_us_phone(customers.phone)))
                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('------------------------------------------\n')

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
                                    memo_string.append(item_memo)
                            if colors:
                                for color_name, color_amount in colors.items():
                                    if color_name:
                                        color_string.append('{}-{}'.format(color_amount, color_name))

                            vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                           density=5, invert=False, smooth=False, flip=False)
                            vars.EPSON.text('{} {}    '.format(item_type, total_qty, item_name))
                            vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'B', width=1, height=1,
                                           density=5, invert=False, smooth=False, flip=False)
                            vars.EPSON.text('{}\n'.format(item_name))
                            if len(memo_string) > 0:
                                vars.EPSON.control('HT')
                                vars.EPSON.control('HT')
                                vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                               density=5, invert=False, smooth=False, flip=False)
                                vars.EPSON.text('  {}\n'.format('/ '.join(memo_string)))
                            if len(color_string):
                                vars.EPSON.control('HT')
                                vars.EPSON.control('HT')
                                vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                               density=5, invert=False, smooth=False, flip=False)
                                vars.EPSON.text('  {}\n'.format(', '.join(color_string)))

                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('------------------------------------------\n')
                vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('{} PCS\n'.format(self.quantity))
                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('------------------------------------------\n')
                # Cut paper
                vars.EPSON.cut(mode=u"PART")

                # Print store copies
                if print_invoice:  # if invoices synced
                    for invoice_id, item_id in print_invoice.items():

                        # start invoice
                        vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text("::COPY::\n")
                        vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text("{}\n".format(companies.name))
                        vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text("{}\n".format(Job.make_us_phone(companies.phone)))
                        vars.EPSON.text("edited: {}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                        vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                        vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text("{}\n".format('{0:06d}'.format(invoice_id)))
                        # Print barcode
                        vars.EPSON.barcode('{}'.format('{0:06d}'.format(invoice_id)), 'CODE39', 64, 2, 'OFF', 'B', 'B')

                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('{}, {}\n'.format(customers.last_name.upper(), customers.first_name.upper()))

                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('{}\n'.format(Job.make_us_phone(customers.phone)))
                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('------------------------------------------\n')

                        if print_invoice[invoice_id]:
                            for item_id, invoice_item in print_invoice[invoice_id].items():
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
                                vars.EPSON.text('{} {}   {}{}{}\n'.format(item_type,
                                                                          item_qty,
                                                                          item_name,
                                                                          ' ' * string_offset,
                                                                          vars.us_dollar(item_price)))

                                # vars.EPSON.text('\r\x1b@\x1b\x61\x02{}\n'.format(vars.us_dollar(item_price)))
                                if len(item_memo) > 0:
                                    vars.EPSON.control('HT')
                                    vars.EPSON.control('HT')
                                    vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                   density=5, invert=False, smooth=False, flip=False)
                                    vars.EPSON.text('  {}\n'.format('/ '.join(item_memo)))
                                if len(item_color_string) > 0:
                                    vars.EPSON.control('HT')
                                    vars.EPSON.control('HT')
                                    vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                   density=5, invert=False, smooth=False, flip=False)
                                    vars.EPSON.text('  {}\n'.format(', '.join(item_color_string)))

                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('------------------------------------------\n')
                        vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('{} PCS\n'.format(self.quantity))
                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('------------------------------------------\n')
                        vars.EPSON.set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('    SUBTOTAL:')
                        vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                        string_length = len(vars.us_dollar(self.subtotal))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.text('{}{}\n'.format(' ' * string_offset,
                                                        vars.us_dollar(self.subtotal)))
                        vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                        vars.EPSON.text('         TAX:')
                        string_length = len(vars.us_dollar(self.tax))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                        vars.EPSON.text('{}{}\n'.format(' ' * string_offset,
                                                        vars.us_dollar(self.tax)))
                        vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                        vars.EPSON.text('       TOTAL:')
                        vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                        string_length = len(vars.us_dollar(self.total))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.text('{}{}\n'.format(' ' * string_offset,
                                                        vars.us_dollar(self.total)))
                        vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                        vars.EPSON.text('     BALANCE:')
                        string_length = len(vars.us_dollar(self.total))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.text('{}{}\n\n'.format(' ' * string_offset,
                                                          vars.us_dollar(self.total)))
                        if item_type == 'L':
                            # get customer mark
                            marks = Custid()
                            marks_list = marks.where({'customer_id': vars.CUSTOMER_ID, 'status': 1})
                            if marks_list:
                                m_list = []
                                for mark in marks_list:
                                    m_list.append(mark['mark'])
                                vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=3, height=4,
                                               density=8, invert=False, smooth=False, flip=False)
                                vars.EPSON.text('{}\n\n'.format(', '.join(m_list)))

                        # Cut paper
                        vars.EPSON.cut(mode=u"PART")
            else:
                # Print store copies
                if print_invoice:  # if invoices synced
                    for invoice_id, item_id in print_invoice.items():

                        # start invoice
                        vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text("::COPY::\n")
                        vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text("{}\n".format(companies.name))
                        vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text("{}\n".format(Job.make_us_phone(companies.phone)))
                        vars.EPSON.text("edited: {}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                        vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                        vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text("{}\n".format('{0:06d}'.format(invoice_id)))
                        # Print barcode
                        vars.EPSON.barcode('{}'.format('{0:06d}'.format(invoice_id)), 'CODE39', 64, 2, 'OFF', 'B', 'B')

                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('{}, {}\n'.format(customers.last_name.upper(), customers.first_name.upper()))

                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('{}\n'.format(Job.make_us_phone(customers.phone)))
                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('------------------------------------------\n')

                        if print_invoice[invoice_id]:
                            for item_id, invoice_item in print_invoice[invoice_id].items():
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
                                vars.EPSON.text('{} {}   {}{}{}\n'.format(item_type,
                                                                          item_qty,
                                                                          item_name,
                                                                          ' ' * string_offset,
                                                                          vars.us_dollar(item_price)))

                                # vars.EPSON.text('\r\x1b@\x1b\x61\x02{}\n'.format(vars.us_dollar(item_price)))
                                if len(item_memo) > 0:
                                    vars.EPSON.control('HT')
                                    vars.EPSON.control('HT')
                                    vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                   density=5, invert=False, smooth=False, flip=False)
                                    vars.EPSON.text('  {}\n'.format('/ '.join(item_memo)))
                                if len(item_color_string) > 0:
                                    vars.EPSON.control('HT')
                                    vars.EPSON.control('HT')
                                    vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                   density=5, invert=False, smooth=False, flip=False)
                                    vars.EPSON.text('  {}\n'.format(', '.join(item_color_string)))

                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('------------------------------------------\n')
                        vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('{} PCS\n'.format(self.quantity))
                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('------------------------------------------\n')
                        vars.EPSON.set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('    SUBTOTAL:')
                        vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                        string_length = len(vars.us_dollar(self.subtotal))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.text('{}{}\n'.format(' ' * string_offset,
                                                        vars.us_dollar(self.subtotal)))
                        vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                        vars.EPSON.text('         TAX:')
                        string_length = len(vars.us_dollar(self.tax))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                        vars.EPSON.text('{}{}\n'.format(' ' * string_offset,
                                                        vars.us_dollar(self.tax)))
                        vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                        vars.EPSON.text('       TOTAL:')
                        vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                        string_length = len(vars.us_dollar(self.total))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.text('{}{}\n'.format(' ' * string_offset,
                                                        vars.us_dollar(self.total)))
                        vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                        vars.EPSON.text('     BALANCE:')
                        string_length = len(vars.us_dollar(self.total))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        vars.EPSON.text('{}{}\n\n'.format(' ' * string_offset,
                                                          vars.us_dollar(self.total)))
                        if customers.invoice_memo:
                            vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text('{}\n'.format(customers.invoice_memo))
                        if item_type == 'L':
                            # get customer mark
                            marks = Custid()
                            marks_list = marks.where({'customer_id': vars.CUSTOMER_ID, 'status': 1})
                            if marks_list:
                                m_list = []
                                for mark in marks_list:
                                    m_list.append(mark['mark'])
                                vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=3, height=4,
                                               density=8, invert=False, smooth=False, flip=False)
                                vars.EPSON.text('{}\n\n'.format(', '.join(m_list)))

                        # Cut paper
                        vars.EPSON.cut(mode=u"PART")
        else:
            popup = Popup()
            popup.title = 'Printer Error'
            content = KV.popup_alert('Unable to locate usb printer.')
            popup.content = Builder.load_string(content)
            popup.open()
            sys.stdout.write('\a')
            sys.stdout.flush()

        self.set_result_status()
        self.print_popup.dismiss()


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
        vars.WORKLIST.append("Sync")
        threads_start()
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
                    vars.WORKLIST.append("Sync")
                    threads_start()

                self.reset()
                self.customer_select(vars.CUSTOMER_ID)
                # create popup
                content = KV.popup_alert("You have successfully edited this customer.")
                popup.content = Builder.load_string(content)
                popup.open()
                marks.close_connection()

        customers.close_connection()

    def customer_select(self, customer_id, *args, **kwargs):
        print(customer_id)
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
        employees = users.where({'company_id': auth_user.company_id,
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
            users.company_id = auth_user.company_id
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
    item_image = ObjectProperty(None)
    items_table = ObjectProperty(None)
    invs_results_label = ObjectProperty(None)
    history_popup = ObjectProperty(None)
    status_spinner = ObjectProperty(None)
    starch = None
    selected_tags_list = []
    tags_grid = ObjectProperty(None)

    def get_history(self):
        # check if an invoice was previously selected
        self.invoices_table.clear_widgets()
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
        if vars.ROW_CAP < 10 and vars.ROW_CAP <= vars.ROW_SEARCH[1]:
            vars.ROW_SEARCH = 0, vars.ROW_CAP
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
        invs = invoices.like(data=data, deleted_at=False)
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

        if vars.INVOICE_ID:
            self.items_table_update()

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

        selected = True if invoice_id == check_invoice_id else False

        tr_1 = KV.invoice_tr(state, invoice_id, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.select_invoice({})'.format(invoice_id))
        tr_2 = KV.invoice_tr(state, company_id, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.select_invoice({})'.format(invoice_id))
        tr_3 = KV.invoice_tr(state, due_date, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.select_invoice({})'.format(invoice_id))
        tr_4 = KV.invoice_tr(state, rack, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.select_invoice({})'.format(invoice_id))
        tr_5 = KV.invoice_tr(state, quantity, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.select_invoice({})'.format(invoice_id))
        tr_6 = KV.invoice_tr(state, total, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.select_invoice({})'.format(invoice_id))
        self.invoices_table.add_widget(Builder.load_string(tr_1))
        self.invoices_table.add_widget(Builder.load_string(tr_2))
        self.invoices_table.add_widget(Builder.load_string(tr_3))
        self.invoices_table.add_widget(Builder.load_string(tr_4))
        self.invoices_table.add_widget(Builder.load_string(tr_5))
        self.invoices_table.add_widget(Builder.load_string(tr_6))

        return True

    def reprint(self):
        pass

    def undo(self):
        pass

    def set_result_status(self):
        vars.SEARCH_RESULTS_STATUS = True
        # update db with current changes
        vars.WORKLIST.append("Sync")
        threads_start()

    def select_invoice(self, invoice_id):
        # set selected invoice and update the table to show it
        vars.INVOICE_ID = invoice_id
        # self.invoices_table.clear_widgets()
        self.get_history()
        self.items_table_update()

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
        invs = invoices.like(data=data, deleted_at=False)
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
        invs = invoices.like(data=data, deleted_at=False)
        vars.SEARCH_RESULTS = invs
        self.invs_results_label.text = "[color=000000]Showing rows [b]{}[/b] - [b]{}[/b] out of [b]{}[/b][/color]".format(
            vars.ROW_SEARCH[0], vars.ROW_SEARCH[1], vars.ROW_CAP
        )
        self.get_history()

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
                                              on_press=self.history_popup.dismiss))
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

            msg = KV.popup_alert(msg="Successfully deleted invoice #{}!".format(vars.INVOICE_ID))
        else:
            msg = KV.popup_alert(msg="Could not locate the invoice_id. Please try again.")
            pass

        popup.content = Builder.load_string(msg)
        popup.open()
        self.history_popup.dismiss()
        self.get_history()

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
        self.get_history()

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

                companies = Company()
                comps = companies.where({'company_id': auth_user.company_id}, set=True)

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
                        customers.first_name = user['first_name']
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
                        invoice_due_date = datetime.datetime.strptime(invoice['due_date'], "%Y-%m-%d %H:%M:%S")
                invoice_items = InvoiceItem()
                inv_items = invoice_items.where({'invoice_id': vars.INVOICE_ID})

                print_sync_invoice = {vars.INVOICE_ID: {}}
                if inv_items:
                    colors = {}
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
                        if item_color in colors:
                            colors[item_color] += 1
                        else:
                            colors[item_color] = 1
                        item_memo = invoice_item['memo']
                        item_subtotal = invoice_item['pretax']
                        if item_id in print_sync_invoice[vars.INVOICE_ID]:
                            print_sync_invoice[vars.INVOICE_ID][item_id]['item_price'] += item_subtotal
                            print_sync_invoice[vars.INVOICE_ID][item_id]['qty'] += 1
                            if item_memo:
                                print_sync_invoice[vars.INVOICE_ID][item_id]['memos'].append(item_memo)
                            print_sync_invoice[vars.INVOICE_ID][item_id]['colors'] = colors
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
                    vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text("{}\n".format(companies.name))
                    vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text("{}\n".format(companies.street))
                    vars.EPSON.text("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                    vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                   invert=False, smooth=False, flip=False)

                    vars.EPSON.text("{}\n".format(companies.phone))
                    vars.EPSON.text("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))
                    vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text("READY BY: {}\n\n".format(invoice_due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                    vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text("{}\n".format(vars.CUSTOMER_ID))
                    # Print barcode
                    vars.EPSON.barcode('{}'.format(vars.CUSTOMER_ID), 'CODE39', 64, 2, 'OFF', 'B', 'B')

                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('{}, {}\n'.format(customers.last_name.upper(), customers.first_name.upper()))

                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('{}\n'.format(customers.phone))
                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('------------------------------------------\n')

                    if print_sync_invoice[vars.INVOICE_ID]:
                        for item_id, invoice_item in print_sync_invoice[vars.INVOICE_ID].items():
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
                            vars.EPSON.text('{} {}   {}\n'.format(item_type, item_qty, item_name))

                            if len(item_memo) > 0:
                                vars.EPSON.control('HT')
                                vars.EPSON.control('HT')
                                vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                               height=1,
                                               density=5, invert=False, smooth=False, flip=False)
                                vars.EPSON.text('  {}\n'.format('/ '.join(item_memo)))
                            if len(item_color_string) > 0:
                                vars.EPSON.control('HT')
                                vars.EPSON.control('HT')
                                vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                               height=1,
                                               density=5, invert=False, smooth=False, flip=False)
                                vars.EPSON.text('  {}\n'.format(', '.join(item_color_string)))

                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('------------------------------------------\n')
                    vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('{} PCS\n'.format(invoice_quantity))
                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('------------------------------------------\n')

                    if customers.invoice_memo:
                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('{}\n'.format(customers.invoice_memo))
                    # Cut paper
                    vars.EPSON.cut(mode=u"PART")

                if type == 1:
                    # Print store copies
                    if print_sync_invoice:  # if invoices synced
                        for invoice_id, item_id in print_sync_invoice.items():

                            # start invoice
                            vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                           density=5,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text("::COPY::\n")
                            vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text("{}\n".format(companies.name))
                            vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                           density=5,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text("{}\n".format(companies.phone))
                            vars.EPSON.text("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))
                            vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2,
                                           density=5,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text(
                                "READY BY: {}\n\n".format(invoice_due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                            vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text("{}\n".format('{0:06d}'.format(invoice_id)))
                            # Print barcode
                            vars.EPSON.barcode('{}'.format('{0:06d}'.format(invoice_id)), 'CODE39', 64, 2, 'OFF',
                                               'B', 'B')

                            vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3,
                                           density=6,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text(
                                '{}, {}\n'.format(customers.last_name.upper(), customers.first_name.upper()))

                            vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                           density=2,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text('{}\n'.format(customers.phone))
                            vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                           density=1,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text('------------------------------------------\n')

                            if print_sync_invoice[invoice_id]:
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
                                    vars.EPSON.text('{} {}   {}{}{}\n'.format(item_type,
                                                                              item_qty,
                                                                              item_name,
                                                                              ' ' * string_offset,
                                                                              vars.us_dollar(item_price)))

                                    if len(item_memo) > 0:
                                        vars.EPSON.control('HT')
                                        vars.EPSON.control('HT')
                                        vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                       height=1,
                                                       density=5, invert=False, smooth=False, flip=False)
                                        vars.EPSON.text('  {}\n'.format('/ '.join(item_memo)))
                                    if len(item_color_string) > 0:
                                        vars.EPSON.control('HT')
                                        vars.EPSON.control('HT')
                                        vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                       height=1,
                                                       density=5, invert=False, smooth=False, flip=False)
                                        vars.EPSON.text('  {}\n'.format(', '.join(item_color_string)))

                            vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                           density=1,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text('------------------------------------------\n')
                            vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text('{} PCS\n'.format(invoice_quantity))
                            vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                           density=1,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text('------------------------------------------\n')
                            vars.EPSON.set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text('    SUBTOTAL:')
                            vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                            string_length = len(vars.us_dollar(invoice_subtotal))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.text('{}{}\n'.format(' ' * string_offset, vars.us_dollar(invoice_subtotal)))
                            vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                            vars.EPSON.text('         TAX:')
                            string_length = len(vars.us_dollar(invoice_tax))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                            vars.EPSON.text('{}{}\n'.format(' ' * string_offset, vars.us_dollar(invoice_tax)))
                            vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                            vars.EPSON.text('       TOTAL:')
                            vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                            string_length = len(vars.us_dollar(invoice_total))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.text('{}{}\n'.format(' ' * string_offset,
                                                            vars.us_dollar(invoice_total)))
                            vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                            vars.EPSON.text('     BALANCE:')
                            string_length = len(vars.us_dollar(invoice_total))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.text('{}{}\n\n'.format(' ' * string_offset, vars.us_dollar(invoice_total)))
                            if customers.invoice_memo:
                                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text('{}\n'.format(customers.invoice_memo))
                            if item_type == 'L':
                                # get customer mark
                                marks = Custid()
                                marks_list = marks.where({'customer_id': vars.CUSTOMER_ID, 'status': 1})
                                if marks_list:
                                    m_list = []
                                    for mark in marks_list:
                                        m_list.append(mark['mark'])
                                    vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=3, height=4,
                                                   density=8, invert=False, smooth=False, flip=False)
                                    vars.EPSON.text('{}\n\n'.format(', '.join(m_list)))

                            # Cut paper
                            vars.EPSON.cut(mode=u"PART")
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
                    customers.first_name = user['first_name']
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
            # vars.BIXOLON.hw('RESET')
            vars.BIXOLON.text('\x1b\x40')
            vars.BIXOLON.text('\x1b\x6d')
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

                            vars.BIXOLON.text('\x1b!\x30')  # QUAD SIZE
                            vars.BIXOLON.text('{}{}\n'.format(text_left, text_right))
                            vars.BIXOLON.hw('RESET')
                            vars.BIXOLON.text('\x1b!\x00')
                            vars.BIXOLON.text(name_number_string)
                            vars.BIXOLON.text('\n')
                            vars.BIXOLON.text('{0:06d}'.format(int(invoice_item_id)))
                            vars.BIXOLON.text(' {} {}'.format(item_name, item_color))
                            if memo_string:
                                vars.BIXOLON.text('\n{}'.format(memo_string))
                                memo_len = '\n\n\n' if len(
                                    memo_string) <= 32 else '\n\n\n' + '\n' * int(
                                    (len(memo_string)) / 32)
                                vars.BIXOLON.text(memo_len)
                                vars.BIXOLON.text('\x1b\x6d')
                            else:
                                vars.BIXOLON.text('\n\n\n')
                                vars.BIXOLON.text('\x1b\x6d')
                        # FINAL CUT
                        # vars.BIXOLON.hw('RESET')
                        vars.BIXOLON.cut()
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

                    vars.BIXOLON.text('\x1b!\x30')  # QUAD SIZE
                    vars.BIXOLON.text(mark_mark_string)
                    vars.BIXOLON.text('\n')
                    vars.BIXOLON.hw('RESET')
                    vars.BIXOLON.text('\x1b!\x00')
                    vars.BIXOLON.text(name_name_string)
                    vars.BIXOLON.text('\n')
                    vars.BIXOLON.text(id_id_string)

                    vars.BIXOLON.text('\n\n\n\x1b\x6d')

                # FINAL CUT
                vars.BIXOLON.hw('RESET')
                vars.BIXOLON.cut()

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
                    customers.first_name = user['first_name']
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
                vars.BIXOLON.hw('RESET')
                vars.BIXOLON.text('\x1b\x40')
                vars.BIXOLON.text('\x1b\x6d')
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

                                    vars.BIXOLON.text('\x1b!\x30')  # QUAD SIZE
                                    vars.BIXOLON.text('{}{}\n'.format(text_left, text_right))
                                    vars.BIXOLON.hw('RESET')
                                    vars.BIXOLON.text('\x1b!\x00')
                                    vars.BIXOLON.text(name_number_string)
                                    vars.BIXOLON.text('\n')
                                    vars.BIXOLON.text('{0:06d}'.format(int(invoice_item_id)))
                                    vars.BIXOLON.text(' {} {}'.format(item_name, item_color))
                                    if memo_string:
                                        vars.BIXOLON.text('\n{}'.format(memo_string))
                                        memo_len = '\n\n\n' if len(
                                            memo_string) <= 32 else '\n\n\n' + '\n' * int(
                                            (len(memo_string)) / 32)
                                        vars.BIXOLON.text(memo_len)
                                        vars.BIXOLON.text('\x1b\x6d')

                                    else:

                                        vars.BIXOLON.text('\n\n\n')
                                        vars.BIXOLON.text('\x1b\x6d')
            if len(laundry_to_print) is 0:
                # FINAL CUT
                vars.BIXOLON.hw('RESET')
                vars.BIXOLON.cut()
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

                    vars.BIXOLON.text('\x1b!\x30')  # QUAD SIZE
                    vars.BIXOLON.text(mark_mark_string)
                    vars.BIXOLON.text('\n')
                    vars.BIXOLON.hw('RESET')
                    vars.BIXOLON.text('\x1b!\x00')
                    vars.BIXOLON.text(name_name_string)
                    vars.BIXOLON.text('\n')
                    vars.BIXOLON.text(id_id_string)

                    vars.BIXOLON.text('\n\n\n\x1b\x6d')

                # FINAL CUT
                vars.BIXOLON.hw('RESET')
                vars.BIXOLON.cut()
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

        inventories = Inventory().where({'company_id': auth_user.company_id, 'ORDER_BY': 'ordered asc'})
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
        inventories = Inventory().where({'company_id': auth_user.company_id, 'ORDER_BY': 'ordered asc'})
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
        inventories.company_id = auth_user.company_id
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
        self.inventory_id = None
        self.get_inventory()
        self.item_id = None
        self.inventory_image.source = ''
        self.from_id = None
        self.reorder_list = {}

    def get_inventory(self):
        inventories = Inventory().where({'company_id': '{}'.format(auth_user.company_id),
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

                        if self.item_id == item_id:
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
                if self.inventory_id == inventory_id:
                    self.items_panel.switch_to(tph)

    def set_inventory(self, inventory_id, *args, **kwargs):
        self.inventory_id = inventory_id

    def set_item(self, item_id, *args, **kwargs):
        self.item_id = item_id
        if self.from_id:
            if self.reorder_list[self.inventory_id]:
                idx = -1
                for list_id in self.reorder_list[self.inventory_id]:
                    idx += 1
                    if list_id == self.item_id:
                        self.reorder_list[self.inventory_id][idx] = self.from_id
                    if list_id == self.from_id:
                        self.reorder_list[self.inventory_id][idx] = self.item_id
                row = 0
                inv_items = InventoryItem()
                for list_id in self.reorder_list[self.inventory_id]:
                    row += 1
                    inv_items.put(where={'company_id': auth_user.company_id,
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
        invitems = inventory_items.where({'company_id': auth_user.company_id,
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
        deleted = inventory_items.where({'company_id': auth_user.company_id,
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
        invitems = inventory_items.where({'company_id': auth_user.company_id,
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
            inventory_items.company_id = auth_user.company_id
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
            put = inventory_items.put(where={'company_id': auth_user.company_id,
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
        self.memo_id = None
        self.create_memo_table()
        pass

    def create_memo_table(self):
        self.memos_table.clear_widgets()
        mmos = Memo()
        memos = mmos.where({'company_id': auth_user.company_id,
                            'ORDER_BY': 'ordered asc'})
        if memos:
            for memo in memos:
                m_id = memo['id']
                memo_msg = memo['memo']
                if self.reorder_start_id is None:
                    memo_item = Factory.LongButton(text='{}'.format(memo_msg),
                                                   on_press=partial(self.set_memo_id, m_id),
                                                   on_release=self.memo_actions_popup)
                elif self.reorder_start_id == m_id:
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
        search = mmos.where({'company_id': auth_user.company_id,
                             'ORDER_BY': 'ordered desc',
                             'LIMIT': 1})
        next_ordered = 1
        if search:
            for memo in search:
                next_ordered = int(memo['ordered']) + 1

        if self.msg.text is not None:
            mmos.company_id = auth_user.company_id
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

                if vars.WORKLIST.append("Sync"):  # send the data to the server and get back the updated user id
                    threads_start()
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
                        vars.WORKLIST.append("Sync")
                        threads_start()
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
    calc_amount = []
    amount_tendered = 0
    selected_invoices = []
    total_subtotal = 0
    total_quantity = 0
    total_tax = 0
    total_amount = 0
    total_credit = 0
    total_discount = 0
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

    def reset(self):
        self.selected_invoices = []
        # setup invoice table
        self.invoice_table.clear_widgets()

        # make headers
        self.invoice_create_rows()

        # reset payment values
        self.calc_amount = []
        self.amount_tendered = 0
        self.selected_invoices = []
        self.total_subtotal = 0
        self.total_quantity = 0
        self.total_tax = 0
        self.total_amount = 0
        self.total_credit = 0
        self.total_discount = 0
        self.total_due = 0
        self.change_due = 0
        self.payment_type = 'cc'
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

        # reset states
        self.instore_button.state = 'down'
        self.online_button.state = 'normal'

        # reset cards on file ids
        vars.PROFILE_ID = None
        vars.PAYMENT_ID = None
        pro = Profile()
        profiles = pro.where({'user_id': vars.CUSTOMER_ID,
                              'company_id': auth_user.company_id})
        if profiles:
            for profile in profiles:
                vars.PROFILE_ID = profile['profile_id']

            cards_db = Card()
            self.cards = cards_db.collect(auth_user.company_id, vars.PROFILE_ID)
        else:
            self.cards = False
        self.select_card_location('1')

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
                quantity = int(invoice['quantity'])
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

                    if invoice_id in self.selected_invoices:
                        self.total_quantity += quantity
                        self.total_subtotal += invoice['pretax']
                        self.total_tax += invoice['tax']
                        self.total_amount += invoice['total']
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
        # get invoice total
        invoices = Invoice().where({'invoice_id': invoice_id})
        if invoices:
            for invoice in invoices:
                total = invoice['total']
                quantity = invoice['quantity']
                subtotal = invoice['pretax']
                tax = invoice['tax']
        else:
            total = 0
            quantity = 0
            subtotal = 0
            tax = 0
        if invoice_id in self.selected_invoices:
            idx = -1
            for inv_id in self.selected_invoices:
                idx += 1
                if inv_id == invoice_id:
                    del self.selected_invoices[idx]
                    self.amount_tendered -= total
                    self.total_amount -= total
                    self.total_subtotal -= subtotal
                    self.total_quantity -= quantity
                    self.total_tax -= tax
        else:
            self.selected_invoices.append(invoice_id)
            self.amount_tendered += total
            self.total_amount += total
            self.total_subtotal += subtotal
            self.total_quantity += quantity
            self.total_tax += tax

        self.total_due = 0 if self.total_credit >= self.total_amount else (
            self.total_amount - self.total_credit - self.total_discount)

        fix = 0 if self.total_amount <= 0 else self.total_amount
        fix_qty = 0 if self.total_quantity <= 0 else self.total_quantity
        fix_tax = 0 if self.total_tax <= 0 else self.total_tax
        fix_subtotal = 0 if self.total_subtotal <= 0 else self.total_subtotal
        fix_due = 0 if self.total_due <= 0 else self.total_due
        self.total_amount = fix
        self.amount_tendered = fix
        self.total_quantity = fix_qty
        self.total_subtotal = fix_subtotal
        self.total_tax = fix_tax
        self.total_due = fix_due

        # update the subtotal label
        self.quantity_label.text = '[color=000000][b]{}[/b][/color]'.format(self.total_quantity)
        self.subtotal_label.text = '[color=000000][b]{}[/b][/color]'.format(vars.us_dollar(self.total_subtotal))
        self.tax_label.text = '[color=000000][b]{}[/b][/color]'.format(vars.us_dollar(self.total_tax))
        self.total_label.text = '[color=000000][b]{}[/b][/color]'.format(vars.us_dollar(self.total_amount))
        self.due_label.text = '[color=000000][b]{}[/b][/color]'.format(vars.us_dollar(self.total_due))

        # update the calculator total
        self.calc_amount = ['{}'.format(int(self.total_due * 100))]
        self.calc_total.text = '[color=000000][b]{}[/b][/color]'.format(vars.us_dollar(self.total_due))

        # calculate change due
        self.change_due = self.amount_tendered - self.total_due

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
            run_sync = threading.Thread(target=SYNC.run_sync)
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
                        if result['status']:
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
        total = vars.us_dollar(int(''.join(amount)))
        self.amount_tendered = int(''.join(amount))
        self.change_due = self.amount_tendered - self.total_due
        self.calc_total.text = '[color=000000][b]{}[/b][/color]'.format(total)

    def pay_popup_create(self):

        self.finish_popup.title = 'Finish Payment'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.9))
        button_1 = Factory.PrintButton(text='Finish + Receipt',
                                       on_press=partial(self.finish_transaction, 1))
        button_2 = Factory.PrintButton(text='Finish + No Receipt',
                                       on_press=partial(self.finish_transaction, 2))
        if self.payment_type == 'cc':
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
                                card_billing_address = '[color=5e5e5e]{} {} {},{} {}[/color]'.format(card_street,
                                                                                                     card_suite,
                                                                                                     card_city,
                                                                                                     card_state,
                                                                                                     card_zipcode)
                            else:
                                card_billing_address = '[color=5e5e5e]{} {},{} {}[/color]'.format(card_street,
                                                                                                  card_city,
                                                                                                  card_state,
                                                                                                  card_zipcode)
                            self.card_box.ids.credit_card_number.text = '[color=5e5e5e]{}[/color]'.format(
                                card_last_four)
                            self.card_box.ids.credit_card_type.text = '[color]{}[/color]'.format(card_type)
                            self.card_box.ids.credit_card_full_name.text = '[color="5e5e5e"]{} {}[/color]'.format(
                                card_first_name,
                                card_last_name)
                            self.card_box.ids.credit_card_exp_date.text = '[color="5e5e5e"]{}/{}[/color]'.format(
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
                    result = Card().validate_card(auth_user.company_id, profile_id, payment_id)
                    self.card_box.ids.card_status.text = "Passed" if result['status'] else "Failed"
                    self.card_box.ids.card_message.text = result['message']
        else:
            self.card_box.ids.card_status.text = "Failed"
            self.card_box.ids.card_message = "Could not locate card on file. Please try again."

        pass

    def finish_transaction(self, print, *args, **kwargs):

        transaction = Transaction()
        transaction.company_id = auth_user.company_id
        transaction.customer_id = vars.CUSTOMER_ID
        transaction.schedule_id = None
        transaction.pretax = self.total_subtotal
        transaction.tax = self.total_tax
        transaction.aftertax = self.total_amount
        transaction.discount = self.total_discount
        transaction.total = self.total_due
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
        transaction.status = 1
        if transaction.add():
            # update to server
            run_sync = threading.Thread(target=SYNC.run_sync)
            try:
                run_sync.start()
            finally:
                run_sync.join()
                # last transaction _id

                last_transaction = transaction.where({'id': {'>': 0}, 'ORDER_BY': 'id desc', 'LIMIT': 1})
                if last_transaction:
                    for trans in last_transaction:
                        transaction_id = trans['transaction_id']
                else:
                    transaction_id = None

                # save transaction_id to Transaction and each invoice
                if self.selected_invoices:
                    invoices = Invoice()
                    for invoice_id in self.selected_invoices:
                        invoices.put(where={'invoice_id': invoice_id},
                                     data={'status': 5, 'transaction_id': transaction_id})
                    self.set_result_status()
                    self.finish_popup.dismiss()
        if print == 1:  # customer copy of invoice and finish
            if vars.EPSON:

                companies = Company()
                comps = companies.where({'company_id': auth_user.company_id}, set=True)

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
                        customers.first_name = user['first_name']
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
                                if item_color in colors:
                                    colors[item_color] += 1
                                else:
                                    colors[item_color] = 1
                                item_memo = invoice_item['memo']
                                item_subtotal = invoice_item['pretax']
                                if item_id in print_sync_invoice[invoice_id]:
                                    print_sync_invoice[invoice_id][item_id]['item_price'] += item_subtotal
                                    print_sync_invoice[invoice_id][item_id]['qty'] += 1
                                    if item_memo:
                                        print_sync_invoice[invoice_id][item_id]['memos'].append(item_memo)
                                    print_sync_invoice[invoice_id][item_id]['colors'] = colors
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
                    vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                   density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text("::Payment Copy::\n")
                    vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text("{}\n".format(companies.name))
                    vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text("{}\n".format(companies.street))
                    vars.EPSON.text("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                    vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                   invert=False, smooth=False, flip=False)

                    vars.EPSON.text("{}\n".format(Job.make_us_phone(companies.phone)))
                    vars.EPSON.text("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))

                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3,
                                   density=6,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text(
                        '{}, {}\n'.format(customers.last_name.upper(), customers.first_name.upper()))

                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                   density=2,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('{}\n'.format(Job.make_us_phone(customers.phone)))
                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                   density=1,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('------------------------------------------\n')
                    for invoice_id, item_id in print_sync_invoice.items():

                        if print_sync_invoice[invoice_id]:
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
                                vars.EPSON.text('{} {}   {}{}{}\n'.format(item_type,
                                                                          item_qty,
                                                                          item_name,
                                                                          ' ' * string_offset,
                                                                          vars.us_dollar(item_price)))

                                if len(item_memo) > 0:
                                    vars.EPSON.control('HT')
                                    vars.EPSON.control('HT')
                                    vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                   height=1,
                                                   density=5, invert=False, smooth=False, flip=False)
                                    vars.EPSON.text('  {}\n'.format('/ '.join(item_memo)))
                                if len(item_color_string) > 0:
                                    vars.EPSON.control('HT')
                                    vars.EPSON.control('HT')
                                    vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                   height=1,
                                                   density=5, invert=False, smooth=False, flip=False)
                                    vars.EPSON.text('  {}\n'.format(', '.join(item_color_string)))

                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                   density=1,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('------------------------------------------\n')
                    vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('{} PCS\n'.format(self.total_quantity))
                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                   density=1,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('------------------------------------------\n')
                    vars.EPSON.set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('    SUBTOTAL:')
                    vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                    string_length = len(vars.us_dollar(self.total_subtotal))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.text('{}{}\n'.format(' ' * string_offset, vars.us_dollar(self.total_subtotal)))
                    vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                    vars.EPSON.text('         TAX:')
                    string_length = len(vars.us_dollar(self.total_tax))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                    vars.EPSON.text('{}{}\n'.format(' ' * string_offset, vars.us_dollar(self.total_tax)))
                    vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                    vars.EPSON.text('       TOTAL:')
                    vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                    string_length = len(vars.us_dollar(self.total_due))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.text('{}{}\n'.format(' ' * string_offset, vars.us_dollar(self.total_due)))
                    vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                    vars.EPSON.text('     TENDERED:')
                    string_length = len(vars.us_dollar(self.amount_tendered))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.text('{}{}\n\n'.format(' ' * string_offset, vars.us_dollar(self.amount_tendered)))
                    vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                    vars.EPSON.text('     BALANCE:')
                    balance = 0 if (
                                       self.amount_tendered - self.total_due) < 0  else self.amount_tendered - self.total_due
                    string_length = len(vars.us_dollar(balance))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    vars.EPSON.text('{}{}\n\n'.format(' ' * string_offset, vars.us_dollar(balance)))
                    # Cut paper
                    vars.EPSON.cut(mode=u"PART")
            else:
                popup = Popup()
                popup.title = 'Printer Error'
                content = KV.popup_alert('Usb device not found')
                popup.content = Builder.load_string(content)
                popup.open()
                # Beep Sound
                sys.stdout.write('\a')
                sys.stdout.flush()

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
        prs = printers.where({'company_id': auth_user.company_id})
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
        printer.company_id = auth_user.company_id
        printer.name = self.printer_name.text
        printer.model = self.printer_model_number.text
        printer.nick_name = self.printer_nick_name.text
        printer.vendor_id = self.printer_vendor.text
        printer.product_id = self.printer_product.text
        printer.type = self.printer_type.text
        printer.status = 1
        if printer.add():
            # set invoice_items data to save
            run_sync = threading.Thread(target=SYNC.db_sync)
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
        run_sync = threading.Thread(target=SYNC.db_sync)
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
        self.racks = OrderedDict()
        self.rack_number.text = ''
        self.invoice_number.text = ''
        self.invoice_number.focus = True
        self.marked_invoice_number = None
        self.edited_rack = False
        self.update_rack_table()

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
            if vars.EPSON:
                self.vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=3,
                                    invert=False, smooth=False, flip=False)
                if self.edited_rack:
                    self.vars.EPSON.text('EDITED: {} - (OLD {}) -> (NEW {})\n'.format(
                        self.invoice_number.text,
                        self.edited_rack,
                        self.rack_number.text))
                    self.edited_rack = False
                else:
                    self.vars.EPSON.text('{} - {}\n'.format(self.invoice_number.text, self.rack_number.text))

            self.racks[self.invoice_number.text] = self.rack_number.text
            self.invoice_number.text = ''
            self.rack_number.text = ''
            self.update_rack_table()
            self.marked_invoice_number = self.invoice_number.text

        self.invoice_number.focus = True

    def save_racks(self):
        now = datetime.datetime.now()
        rack_date = datetime.datetime.strftime(now, "%Y-%m-%d %H:%M:%S")
        # save rows
        if self.racks:
            invoices = Invoice()
            for invoice_id, rack in self.racks.items():
                invoices.put(where={'invoice_id': invoice_id},
                             data={'rack': rack,
                                   'rack_date': rack_date,
                                   'status': 2})  # rack and update status

            # update db
            run_sync = threading.Thread(target=SYNC.run_sync)
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
            self.vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False)
            self.vars.EPSON.text('{}'.format((datetime.datetime.now().strftime('%a %m/%d/%Y %I:%M %p'))))
            self.vars.EPSON.cut(mode=u"PART")


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
    print_popup = ObjectProperty(None)
    calendar_layout = ObjectProperty(None)
    create_calendar_table = ObjectProperty(None)
    quick_box = None
    display_input = ObjectProperty(None)
    calculator_control_table = ObjectProperty(None)
    calc_history = []
    calc_amount = []
    tags_grid = ObjectProperty(None)
    selected_tags_list = []

    def reset(self, *args, **kwargs):
        vars.ROW_SEARCH = 0, 10
        vars.ROW_CAP = 0
        vars.SEARCH_TEXT = None
        self.quick_box = None
        self.calc_history = []
        self.calc_amount = []
        self.selected_tags_list = []

        if vars.SEARCH_RESULTS_STATUS:

            self.edit_invoice_btn.disabled = False if vars.INVOICE_ID is not None else True
            data = {'user_id': vars.CUSTOMER_ID}
            customers = User()
            results = customers.where(data)
            self.customer_results(results)

        else:
            vars.CUSTOMER_ID = None
            vars.INVOICE_ID = None
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
            self.due_date = None
            self.due_date_string = None
        self.search.focus = True

        vars.SEARCH_RESULTS_STATUS = False

    def search_customer(self, *args, **kwargs):
        popup = Popup()
        search_text = self.search.text
        customers = User()
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
        else:
            popup = Popup()
            popup.title = 'Search Error'
            popup.content = Builder.load_string(KV.popup_alert('Search cannot be an empty value. Please try again.'))
            popup.open()
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
        due_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        dow = vars.dow(dt.replace(tzinfo=datetime.timezone.utc).weekday())
        due_date = dt.strftime('%m/%d {}').format(dow)
        dt = datetime.datetime.strptime(NOW,
                                        "%Y-%m-%d %H:%M:%S") if NOW is not None else datetime.datetime.strptime(
            '1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
        now_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        # check to see if invoice is overdue

        invoice_status = row['status']
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
        # if rack:  # racked and ready
        #     state = 3
        # elif due_strtotime < now_strtotime:  # overdue
        #     state = 2
        # else:  # Not ready yet
        #     state = 1

        selected = True if invoice_id == check_invoice_id else False

        tr_1 = KV.invoice_tr(state, '{0:06d}'.format(invoice_id), selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        tr_2 = KV.invoice_tr(state, company_name, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        tr_3 = KV.invoice_tr(state, due_date, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        tr_4 = KV.invoice_tr(state, rack, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        tr_5 = KV.invoice_tr(state, quantity, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        tr_6 = KV.invoice_tr(state, total, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.parent.invoice_selected({})'.format(invoice_id))
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
        data = {'user_id': customer_id}
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
                self.cust_last_name.text = result['last_name'] if result['last_name'] else ''
                self.cust_first_name.text = result['first_name'] if result['first_name'] else ''
                self.cust_phone.text = Job.make_us_phone(result['phone']) if result['phone'] else ''
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

    def quick_popup(self, *args, **kwargs):
        # setup calendar default date
        store_hours = Company().get_store_hours(auth_user.company_id)
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

        store_hours = Company().get_store_hours(auth_user.company_id)
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
        store_hours = Company().get_store_hours(auth_user.company_id)
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

        store_hours = Company().get_store_hours(auth_user.company_id)
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
        store_hours = Company().get_store_hours(auth_user.company_id)

        dow = int(selected_date.strftime("%w"))
        turn_around_hour = store_hours[dow]['due_hour'] if store_hours[dow]['due_hour'] else '4'
        turn_around_minutes = store_hours[dow]['due_minutes'] if store_hours[dow]['due_minutes'] else '00'
        turn_around_ampm = store_hours[dow]['due_ampm'] if store_hours[dow]['due_ampm'] else 'pm'
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
        invoices.company_id = auth_user.company_id
        invoices.quantity = self.quick_box.ids.quick_count.text
        invoices.pretax = 0
        invoices.tax = 0
        invoices.total = 0
        invoices.customer_id = vars.CUSTOMER_ID
        invoices.status = 1
        invoices.memo = self.quick_box.ids.quick_invoice_memo.text
        if invoices.add():
            # save the invoices to the db and return the proper invoice_ids
            run_sync = threading.Thread(target=SYNC.run_sync)
            try:
                run_sync.start()
            finally:
                run_sync.join()
                print('sync now finished')

            # print invoices
            if vars.EPSON:

                companies = Company()
                comps = companies.where({'company_id': auth_user.company_id}, set=True)

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
                        customers.first_name = user['first_name']
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

                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text("QUICK DROP - STORE COPY\n")
                vars.EPSON.text("{}\n".format(companies.name))
                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text("{}\n".format(companies.street))
                vars.EPSON.text("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                               invert=False, smooth=False, flip=False)

                vars.EPSON.text("{}\n".format(Job.make_us_phone(companies.phone)))
                vars.EPSON.text("{}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text("{}\n".format(vars.CUSTOMER_ID))
                # Print barcode
                vars.EPSON.barcode('{}'.format(vars.CUSTOMER_ID), 'CODE39', 64, 2, 'OFF', 'B', 'B')

                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('{}, {}\n'.format(customers.last_name.upper(), customers.first_name.upper()))

                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('{}\n'.format(Job.make_us_phone(customers.phone)))
                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('------------------------------------------\n')

                vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text(
                    '{} PCS\n'.format(
                        self.quick_box.ids.quick_count.text if self.quick_box.ids.quick_count.text else '0'))
                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('------------------------------------------\n')
                if self.quick_box.ids.quick_invoice_memo.text:
                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('{}\n'.format(self.quick_box.ids.quick_invoice_memo.text))

                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=1, density=1,
                               invert=False, smooth=False, flip=False)
                # Cut paper
                vars.EPSON.cut(mode=u"PART")

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
        invoices.company_id = auth_user.company_id
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
            run_sync = threading.Thread(target=SYNC.run_sync)
            try:
                run_sync.start()
            finally:
                run_sync.join()
                print('sync now finished')

            # print invoices
            if vars.EPSON:

                companies = Company()
                comps = companies.where({'company_id': auth_user.company_id}, set=True)

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
                        customers.first_name = user['first_name']
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

                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text("QUICK DROP\n")
                vars.EPSON.text("{}\n".format(companies.name))
                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text("{}\n".format(companies.street))
                vars.EPSON.text("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                               invert=False, smooth=False, flip=False)

                vars.EPSON.text("{}\n".format(Job.make_us_phone(companies.phone)))
                vars.EPSON.text("{}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text("{}\n".format(vars.CUSTOMER_ID))
                # Print barcode
                vars.EPSON.barcode('{}'.format(vars.CUSTOMER_ID), 'CODE39', 64, 2, 'OFF', 'B', 'B')

                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('{}, {}\n'.format(customers.last_name.upper(), customers.first_name.upper()))

                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('{}\n'.format(Job.make_us_phone(customers.phone)))
                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('------------------------------------------\n')

                vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('{} PCS\n'.format(
                    self.quick_box.ids.quick_count.text if self.quick_box.ids.quick_count.text else '0'))
                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('------------------------------------------\n')
                if self.quick_box.ids.quick_invoice_memo.text:
                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('{}\n'.format(self.quick_box.ids.quick_invoice_memo.text))

                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=1, density=1,
                               invert=False, smooth=False, flip=False)
                # Cut paper
                vars.EPSON.cut(mode=u"PART")

                # SECOND Copy
                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text("QUICK DROP - STORE COPY\n")
                vars.EPSON.text("{}\n".format(companies.name))
                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text("{}\n".format(companies.street))
                vars.EPSON.text("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                               invert=False, smooth=False, flip=False)

                vars.EPSON.text("{}\n".format(Job.make_us_phone(companies.phone)))
                vars.EPSON.text("{}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text("{}\n".format(vars.CUSTOMER_ID))
                # Print barcode
                vars.EPSON.barcode('{}'.format(vars.CUSTOMER_ID), 'CODE39', 64, 2, 'OFF', 'B', 'B')

                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('{}, {}\n'.format(customers.last_name.upper(), customers.first_name.upper()))

                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('{}\n'.format(Job.make_us_phone(customers.phone)))
                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('------------------------------------------\n')

                vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text(
                    '{} PCS\n'.format(
                        self.quick_box.ids.quick_count.text if self.quick_box.ids.quick_count.text else '0'))
                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                               invert=False, smooth=False, flip=False)
                vars.EPSON.text('------------------------------------------\n')
                if self.quick_box.ids.quick_invoice_memo.text:
                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('{}\n'.format(self.quick_box.ids.quick_invoice_memo.text))

                vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=1, density=1,
                               invert=False, smooth=False, flip=False)
                # Cut paper
                vars.EPSON.cut(mode=u"PART")

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

                companies = Company()
                comps = companies.where({'company_id': auth_user.company_id}, set=True)

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
                        customers.first_name = user['first_name']
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
                        if item_color in colors:
                            colors[item_color] += 1
                        else:
                            colors[item_color] = 1
                        item_memo = invoice_item['memo']
                        item_subtotal = invoice_item['pretax']
                        if item_id in print_sync_invoice[vars.INVOICE_ID]:
                            print_sync_invoice[vars.INVOICE_ID][item_id]['item_price'] += item_subtotal
                            print_sync_invoice[vars.INVOICE_ID][item_id]['qty'] += 1
                            if item_memo:
                                print_sync_invoice[vars.INVOICE_ID][item_id]['memos'].append(item_memo)
                            print_sync_invoice[vars.INVOICE_ID][item_id]['colors'] = colors
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
                    vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text("{}\n".format(companies.name))
                    vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text("{}\n".format(companies.street))
                    vars.EPSON.text("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                    vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                   invert=False, smooth=False, flip=False)

                    vars.EPSON.text("{}\n".format(companies.phone))
                    vars.EPSON.text("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))
                    vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text("READY BY: {}\n\n".format(invoice_due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                    vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text("{}\n".format(vars.CUSTOMER_ID))
                    # Print barcode
                    vars.EPSON.barcode('{}'.format(vars.CUSTOMER_ID), 'CODE39', 64, 2, 'OFF', 'B', 'B')

                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('{}, {}\n'.format(customers.last_name.upper(), customers.first_name.upper()))

                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('{}\n'.format(customers.phone))
                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('------------------------------------------\n')

                    if print_sync_invoice[vars.INVOICE_ID]:
                        for item_id, invoice_item in print_sync_invoice[vars.INVOICE_ID].items():
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
                            vars.EPSON.text('{} {}   {}\n'.format(item_type, item_qty, item_name))

                            if len(item_memo) > 0:
                                vars.EPSON.control('HT')
                                vars.EPSON.control('HT')
                                vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                               height=1,
                                               density=5, invert=False, smooth=False, flip=False)
                                vars.EPSON.text('  {}\n'.format('/ '.join(item_memo)))
                            if len(item_color_string) > 0:
                                vars.EPSON.control('HT')
                                vars.EPSON.control('HT')
                                vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                               height=1,
                                               density=5, invert=False, smooth=False, flip=False)
                                vars.EPSON.text('  {}\n'.format(', '.join(item_color_string)))

                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('------------------------------------------\n')
                    vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('{} PCS\n'.format(invoice_quantity))
                    vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                   invert=False, smooth=False, flip=False)
                    vars.EPSON.text('------------------------------------------\n')

                    if customers.invoice_memo:
                        vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                       invert=False, smooth=False, flip=False)
                        vars.EPSON.text('{}\n'.format(customers.invoice_memo))
                    # Cut paper
                    vars.EPSON.cut(mode=u"PART")

                if type == 1:
                    # Print store copies
                    if print_sync_invoice:  # if invoices synced
                        for invoice_id, item_id in print_sync_invoice.items():

                            # start invoice
                            vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                           density=5,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text("::COPY::\n")
                            vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text("{}\n".format(companies.name))
                            vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                           density=5,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text("{}\n".format(companies.phone))
                            vars.EPSON.text("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))
                            vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2,
                                           density=5,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text(
                                "READY BY: {}\n\n".format(invoice_due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                            vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text("{}\n".format('{0:06d}'.format(invoice_id)))
                            # Print barcode
                            vars.EPSON.barcode('{}'.format('{0:06d}'.format(invoice_id)), 'CODE39', 64, 2, 'OFF',
                                               'B', 'B')

                            vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3,
                                           density=6,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text(
                                '{}, {}\n'.format(customers.last_name.upper(), customers.first_name.upper()))

                            vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                           density=2,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text('{}\n'.format(customers.phone))
                            vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                           density=1,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text('------------------------------------------\n')

                            if print_sync_invoice[invoice_id]:
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
                                    vars.EPSON.text('{} {}   {}{}{}\n'.format(item_type,
                                                                              item_qty,
                                                                              item_name,
                                                                              ' ' * string_offset,
                                                                              vars.us_dollar(item_price)))

                                    if len(item_memo) > 0:
                                        vars.EPSON.control('HT')
                                        vars.EPSON.control('HT')
                                        vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                       height=1,
                                                       density=5, invert=False, smooth=False, flip=False)
                                        vars.EPSON.text('  {}\n'.format('/ '.join(item_memo)))
                                    if len(item_color_string) > 0:
                                        vars.EPSON.control('HT')
                                        vars.EPSON.control('HT')
                                        vars.EPSON.set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                       height=1,
                                                       density=5, invert=False, smooth=False, flip=False)
                                        vars.EPSON.text('  {}\n'.format(', '.join(item_color_string)))

                            vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                           density=1,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text('------------------------------------------\n')
                            vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text('{} PCS\n'.format(invoice_quantity))
                            vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                           density=1,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text('------------------------------------------\n')
                            vars.EPSON.set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                           invert=False, smooth=False, flip=False)
                            vars.EPSON.text('    SUBTOTAL:')
                            vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                            string_length = len(vars.us_dollar(invoice_subtotal))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.text('{}{}\n'.format(' ' * string_offset, vars.us_dollar(invoice_subtotal)))
                            vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                            vars.EPSON.text('         TAX:')
                            string_length = len(vars.us_dollar(invoice_tax))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                            vars.EPSON.text('{}{}\n'.format(' ' * string_offset, vars.us_dollar(invoice_tax)))
                            vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                            vars.EPSON.text('       TOTAL:')
                            vars.EPSON.set(align=u"RIGHT", text_type=u'NORMAL')
                            string_length = len(vars.us_dollar(invoice_total))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.text('{}{}\n'.format(' ' * string_offset,
                                                            vars.us_dollar(invoice_total)))
                            vars.EPSON.set(align=u"RIGHT", text_type=u'B')
                            vars.EPSON.text('     BALANCE:')
                            string_length = len(vars.us_dollar(invoice_total))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            vars.EPSON.text('{}{}\n\n'.format(' ' * string_offset, vars.us_dollar(invoice_total)))
                            if customers.invoice_memo:
                                vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                               invert=False, smooth=False, flip=False)
                                vars.EPSON.text('{}\n'.format(customers.invoice_memo))
                            if item_type == 'L':
                                # get customer mark
                                marks = Custid()
                                marks_list = marks.where({'customer_id': vars.CUSTOMER_ID, 'status': 1})
                                if marks_list:
                                    m_list = []
                                    for mark in marks_list:
                                        m_list.append(mark['mark'])
                                    vars.EPSON.set(align=u"CENTER", font=u'A', text_type=u'B', width=3, height=4,
                                                   density=8, invert=False, smooth=False, flip=False)
                                    vars.EPSON.text('{}\n\n'.format(', '.join(m_list)))

                            # Cut paper
                            vars.EPSON.cut(mode=u"PART")
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

    def print_card(self):

        if vars.EPSON:

            companies = Company()
            comps = companies.where({'company_id': auth_user.company_id}, set=True)

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
                    customers.first_name = user['first_name']
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

            vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                           invert=False, smooth=False, flip=False)
            vars.EPSON.text("{}\n".format(companies.name))
            vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                           invert=False, smooth=False, flip=False)
            vars.EPSON.text("{}\n".format(companies.street))
            vars.EPSON.text("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
            vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                           invert=False, smooth=False, flip=False)

            vars.EPSON.text("{}\n".format(companies.phone))
            vars.EPSON.text("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))

            vars.EPSON.set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                           invert=False, smooth=False, flip=False)
            vars.EPSON.text("{}\n".format(vars.CUSTOMER_ID))
            vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                           invert=False, smooth=False, flip=False)
            vars.EPSON.text('{}, {}\n'.format(customers.last_name.upper(), customers.first_name.upper()))

            vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                           invert=False, smooth=False, flip=False)
            vars.EPSON.text('{}\n'.format(customers.phone))
            vars.EPSON.set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                           invert=False, smooth=False, flip=False)
            # Print barcode
            vars.EPSON.barcode('{}'.format(vars.CUSTOMER_ID), 'CODE39', 64, 2, 'OFF', 'B', 'B')

            vars.EPSON.text('------------------------------------------\n')
            # Cut paper
            vars.EPSON.cut(mode=u"PART")

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
                    customers.first_name = user['first_name']
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
            # vars.BIXOLON.hw('RESET')
            vars.BIXOLON.text('\x1b\x40')
            vars.BIXOLON.text('\x1b\x6d')
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

                            vars.BIXOLON.text('\x1b!\x30')  # QUAD SIZE
                            vars.BIXOLON.text('{}{}\n'.format(text_left, text_right))
                            vars.BIXOLON.hw('RESET')
                            vars.BIXOLON.text('\x1b!\x00')
                            vars.BIXOLON.text(name_number_string)
                            vars.BIXOLON.text('\n')
                            vars.BIXOLON.text('{0:06d}'.format(int(invoice_item_id)))
                            vars.BIXOLON.text(' {} {}'.format(item_name, item_color))
                            if memo_string:
                                vars.BIXOLON.text('\n{}'.format(memo_string))
                                memo_len = '\n\n\n' if len(
                                    memo_string) <= 32 else '\n\n\n' + '\n' * int(
                                    (len(memo_string)) / 32)
                                vars.BIXOLON.text(memo_len)
                                vars.BIXOLON.text('\x1b\x6d')

                            else:

                                vars.BIXOLON.text('\n\n\n')
                                vars.BIXOLON.text('\x1b\x6d')
                        # FINAL CUT
                        # vars.BIXOLON.hw('RESET')
                        vars.BIXOLON.cut()
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

                    vars.BIXOLON.text('\x1b!\x30')  # QUAD SIZE
                    vars.BIXOLON.text(mark_mark_string)
                    vars.BIXOLON.text('\n')
                    vars.BIXOLON.hw('RESET')
                    vars.BIXOLON.text('\x1b!\x00')
                    vars.BIXOLON.text(name_name_string)
                    vars.BIXOLON.text('\n')
                    vars.BIXOLON.text(id_id_string)

                    vars.BIXOLON.text('\n\n\n\x1b\x6d')

                # FINAL CUT
                vars.BIXOLON.hw('RESET')
                vars.BIXOLON.cut()

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
                    customers.first_name = user['first_name']
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
                # vars.BIXOLON.hw('RESET')
                vars.BIXOLON.text('\x1b\x40')
                vars.BIXOLON.text('\x1b\x6d')
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

                                    vars.BIXOLON.text('\x1b!\x30')  # QUAD SIZE
                                    vars.BIXOLON.text('{}{}\n'.format(text_left, text_right))
                                    vars.BIXOLON.hw('RESET')
                                    vars.BIXOLON.text('\x1b!\x00')
                                    vars.BIXOLON.text(name_number_string)
                                    vars.BIXOLON.text('\n')
                                    vars.BIXOLON.text('{0:06d}'.format(int(invoice_item_id)))
                                    vars.BIXOLON.text(' {} {}'.format(item_name, item_color))
                                    if memo_string:
                                        vars.BIXOLON.text('\n{}'.format(memo_string))
                                        memo_len = '\n\n\n' if len(
                                            memo_string) <= 32 else '\n\n\n' + '\n' * int(
                                            (len(memo_string)) / 32)
                                        vars.BIXOLON.text(memo_len)
                                        vars.BIXOLON.text('\x1b\x6d')

                                    else:

                                        vars.BIXOLON.text('\n\n\n')
                                        vars.BIXOLON.text('\x1b\x6d')
                if len(laundry_to_print) is 0:
                    # FINAL CUT
                    # vars.BIXOLON.hw('RESET')
                    vars.BIXOLON.cut()
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

                    vars.BIXOLON.text('\x1b!\x30')  # QUAD SIZE
                    vars.BIXOLON.text(mark_mark_string)
                    vars.BIXOLON.text('\n')
                    # vars.BIXOLON.hw('RESET')
                    vars.BIXOLON.text('\x1b!\x00')
                    vars.BIXOLON.text(name_name_string)
                    vars.BIXOLON.text('\n')
                    vars.BIXOLON.text(id_id_string)

                    vars.BIXOLON.text('\n\n\n\x1b\x6d')

                # FINAL CUT
                # vars.BIXOLON.hw('RESET')
                vars.BIXOLON.cut()
        else:
            popup = Popup()
            popup.title = 'Reprint Error'
            content = KV.popup_alert('Please select an invoice item to print tag.')
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
        # sync db
        vars.WORKLIST.append("Sync")
        threads_start()


class SettingsScreen(Screen):
    pass


class TaxesScreen(Screen):
    tax_rate_input = ObjectProperty(None)

    def reset(self):
        taxes = Tax()
        tax_rate = None
        tax_data = taxes.where({'company_id': auth_user.company_id, 'ORDER_BY': 'id asc', 'LIMIT': 1})
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
            taxes.company_id = auth_user.company_id
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
                data = {'pretax':pretax,
                        'tax':tax,
                        'total':total}
                where = {'invoice_id':self.invoice_id}
                if invoices.put(where=where,data=data):
                    #reset the data form
                    self.reset()
                    # sync the database
                    vars.WORKLIST.append("Sync")
                    threads_start()
                    #alert the user
                    popup = Popup()
                    popup.title = 'Update Invoice Item Success'
                    content = KV.popup_alert('Successfully updated the invoice item.')
                    popup.content = Builder.load_string(content)
                    popup.open()
                    # Beep Sound
                    sys.stdout.write('\a')
                    sys.stdout.flush()

        pass


class ScreenManagement(ScreenManager):
    pass


presentation = Builder.load_file("./kv/main.kv")


class MainApp(App):
    def build(self):
        self.title = 'Jays POS'
        return presentation


if __name__ == "__main__":
    MainApp().run()
