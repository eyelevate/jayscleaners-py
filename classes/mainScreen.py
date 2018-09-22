import json
import urllib
import webbrowser
import time
import datetime
from threading import Thread
from urllib import parse, request
#!/usr/bin/python
import sys
import usb.core
import usb.util
import usb.backend.libusb1
from kivy.clock import Clock

from models.kv_generator import KvString
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen
from kivy.uix.checkbox import CheckBox
from pubsub import pub

from kivy.uix.popup import Popup
from classes.popups import Popups
from models.invoice_items import InvoiceItem
from models.invoices import Invoice
from models.printers import Printer
from models.sync import Sync
from models.users import User
from models.sessions import sessions

KV = KvString()
SYNC = Sync()
auth_user = User()
ERROR_COLOR = 0.94, 0.33, 0.33, 1
DEFAULT_COLOR = 0.5, 0.5, 0.5, 1.0
unix = time.time()
NOW = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
SYNC_POPUP = Popup()


class MainScreen(Screen):
    update_label = ObjectProperty(None)
    login_button = ObjectProperty(None)
    settings_button = ObjectProperty(None)
    reports_button = ObjectProperty(None)
    delivery_button = ObjectProperty(None)
    dropoff_button = ObjectProperty(None)
    # update_button = ObjectProperty(None)
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
    checkbox = CheckBox()

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        SYNC.migrate()
        remember_me = sessions.get('_rememberMe')['value']
        user_id = sessions.get('_userId')['value']
        if remember_me and user_id is not None:
            Clock.schedule_once(lambda *args: self.isRemembered())
            pass
        else:
            Clock.schedule_once(lambda *args: self.isNotRemembered())
            pass

    def isRemembered(self):
        self.active_state()
        SYNC_POPUP.title = 'Welcome back!'
        content = KV.popup_alert(
            msg='You are now logged in as {}!'.format(sessions.get('_username')['value']))
        SYNC_POPUP.content = Builder.load_string(content)
        SYNC_POPUP.open()


    def isNotRemembered(self):
        self.logout_state()

    def checkIfPassedRememberMe(self):
        now = datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S')
        # start = datetime.datetime.f

    def update_info(self):
        info = "Last updated {}".format("today")
        return info

    def reconnect_printers(self):
        # find USB devices
        dev = usb.core.find(find_all=True)
        # loop through devices, printing vendor and product ids in decimal and hex
        for cfg in dev:
            sys.stdout.write('Decimal VendorID=' + str(cfg.idVendor) + ' & ProductID=' + str(cfg.idProduct) + '\n')
            sys.stdout.write(
                'Hexadecimal VendorID=' + hex(cfg.idVendor) + ' & ProductID=' + hex(cfg.idProduct) + '\n\n')

    def login_show(self):

        self.login_popup = Popup()
        self.login_popup.size_hint = (None, None)
        self.login_popup.size = '400sp', '250sp'
        self.login_popup.title = 'Login Screen'
        layout = BoxLayout(orientation='vertical')
        inner_content_1 = GridLayout(rows=3,
                                     cols=2,
                                     row_force_default=True,
                                     row_default_height='40sp',
                                     size_hint=(1, 0.6))
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
        self.checkbox = Factory.Remember()
        self.checkbox.bind(active=self.on_remember_active)

        inner_content_1.add_widget(Factory.MiddleLeftFormLabel(text="remember me",
                                                               size_hint_y=None,
                                                               font_size='20sp'))
        inner_content_1.add_widget(self.checkbox)
        inner_content_2 = BoxLayout(orientation='horizontal',
                                    size_hint=(1, 0.2))
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

    def on_remember_active(self, obj, value):
        now = datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S')
        sessions.put('_rememberMe', value=value)
        sessions.put('_rememberMeTimestamp', value=now)

    def login(self, *args, **kwargs):

        user = User()
        user.username = self.username.text
        user.password = self.password.text  # cipher and salt later
        data = SYNC.server_login(username=user.username, password=user.password)
        SYNC_POPUP.title = 'Login Screen'
        # validate the form data
        if not user.username:
            self.username.hint_text = "Username must exist"
            self.username.hint_text_color = ERROR_COLOR
        elif not user.password:
            self.password.hint_text = "Password cannot be left empty"
            self.password.hint_text_color = ERROR_COLOR

        # authenticate
        elif user.username and user.password:
            self.username.hint_text = "Enter username"
            self.username.hint_text_color = DEFAULT_COLOR
            self.password.hint_text = "Enter password"
            self.password.hint_text_color = DEFAULT_COLOR
            # first check to see if you can authenticate locally
            if data['status']:
                self.active_state()

                auth_user.username = user.username
                auth_user.user_id = data['user_id']
                sessions.put('_userId', value=data['user_id'])
                sessions.put('_username', value=user.username)
                auth_user.company_id = data['company_id']
                sessions.put('_companyId', value=data['company_id'])
                if not sessions.get('_rememberMe')['value']:
                    sessions.put('remembeMe', value=True)
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
            elif not data['status'] and user.auth(username=user.username,
                                                  password=user.password):  # found user register variables, sync data, and show links
                self.active_state()
                auth_user.id = user.id
                auth_user.user_id = user.user_id
                sessions.put('_userId', value=user.user_id)
                auth_user.username = user.username
                sessions.put('_username', value=user.username)
                auth_user.company_id = user.company_id
                sessions.put('_companyId', value=user.company_id)
                if not sessions.get('_rememberMe')['value']:
                    sessions.put('remembeMe', value=True)
                SYNC.company_id = user.company_id
                print_data = Printer().where({'company_id': user.company_id, 'type': 1})
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

            else:
                SYNC_POPUP.title = 'Authentication Failed!'
                SYNC_POPUP.content = Builder.load_string(
                    KV.popup_alert(msg='Could not find any user with these credentials. '
                                       'Please try again!!'))
                SYNC_POPUP.open()

        else:
            self.username.hint_text = "Username must exist"
            self.username.hint_text_color = ERROR_COLOR
            self.password.hint_text = "Password cannot be left empty"
            self.password.hint_text_color = ERROR_COLOR

    def active_state(self):
        self.login_button.text = "Logout"
        self.login_button.bind(on_release=self.logout)
        # self.update_button.disabled = False
        self.settings_button.disabled = False
        self.reports_button.disabled = False
        self.dropoff_button.disabled = False
        self.delivery_button.disabled = False
        # self.item_search_button.disabled = False

    def logout(self, *args, **kwargs):
        if self.username:
            self.username.text = ''
        if self.password:
            self.password.text = ''
        auth_user.company_id = None
        auth_user.user_id = None
        auth_user.username = None
        self.login_button.text = "Login"
        self.login_button.bind(on_release=self.login)
        self.logout_state()

    def logout_state(self):
        self.settings_button.disabled = True
        self.reports_button.disabled = True
        self.dropoff_button.disabled = True
        self.delivery_button.disabled = True
        sessions.put('_companyId', value=None)
        sessions.put('_userId', value=None)
        sessions.put('_username', value=None)
        sessions.put('_rememberMe', value=False)
        sessions.put('_rememberMeTimestamp', value=None)
        sessions.put('_epson', value=None)
        sessions.put('_bixolon', value=None)

    def db_sync(self, *args, **kwargs):

        # quick sync

        t1 = Thread(target=SYNC.db_sync, args=[sessions.get('_companyId')['value']])
        t1.start()
        t1.join()
        SYNC_POPUP.dismiss()
        # print('initializing auto-sync every 20 seconds')

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
                    self.set_pb_desc("Updating Invoice Table {} of {}".format(str(idx), str(len(data_1))))
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

                    count_invoice = SYNC.invoice_grab_id(invoice.invoice_id)
                    if len(count_invoice) > 0 or invoice.deleted_at:
                        for data in count_invoice:
                            invoice.id = data['id']
                            if invoice.deleted_at:
                                invoice.delete()
                    else:
                        invoice.add_special()

                    # extra loop through invoice items to delete or check for data
                    if 'invoice_items' in invoices:

                        iitems = invoices['invoice_items']
                        self.set_pb_items_max(len(iitems))
                        if len(iitems) > 0:
                            itdx = 0
                            for iitem in iitems:
                                itdx += 1
                                self.set_pb_items_value(itdx)
                                self.set_pb_items_desc(
                                    "Updating Invoice Items Table {} of {}".format(str(itdx), str(len(iitems))))
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
                                count_invoice_item = SYNC.invoice_item_grab(iitem['id'])
                                if len(count_invoice_item) > 0 or invoice_item.deleted_at:
                                    for data in count_invoice_item:
                                        invoice_item.id = data['id']
                                        if invoice_item.deleted_at:
                                            invoice_item.delete()
                                else:
                                    invoice_item.add_special()

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
            zebra = usb.util.find_descriptor(
                intf,
                # match the first OUT endpoint
                custom_match= \
                    lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_OUT)
            sessions.put('_zebra', value=zebra)


        else:
            sessions.put('_zebra', value=False)
            Popups.dialog_msg('Printer Error', 'Tag printer not found.')

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
        self.pb_table.max = int(value)

    def set_pb_items_desc(self, description, *args, **kwargs):
        self.item_description.text = description

    def set_pb_items_value(self, value, *args, **kwargs):
        self.pb_items.value = int(value)

    def set_pb_items_max(self, value, *args, **kwargs):
        self.pb_items.max = int(value)

    def sync_db(self, *args, **kwargs):
        # Pause Schedule
        pass

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
        backend = usb.backend.libusb1.get_backend(find_library=lambda x: "./lib/libusb-1.0.so")
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
            bixolon = usb.util.find_descriptor(
                intf,
                # match the first OUT endpoint
                custom_match= \
                    lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_OUT)

            sessions.put('_bixolon', value=bixolon)

        else:
            sessions.put('_bixolon', value=False)
            Popups.dialog_msg('Printer Error', 'Tag printer not found. Please check settings and try again')

    def print_setup(self, vendor_id, product_id):
        vendor_int = int(vendor_id, 16)
        product_int = int(product_id, 16)
        # find our device
        backend = usb.backend.libusb1.get_backend(find_library=lambda x: "./lib/libusb-1.0.so")
        dev = usb.core.find(idVendor=vendor_int, idProduct=product_int, backend=backend)

        # was it found?
        if dev is not None:
            print('Receipt Device Found')

            # set the active configuration. With no arguments, the first
            # configuration will be the active one
            dev.set_configuration()

            # get an endpoint instance
            cfg = dev.get_active_configuration()
            intf = cfg[(0, 0)]
            epson = usb.util.find_descriptor(
                intf,
                # match the first OUT endpoint
                custom_match= \
                    lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_OUT)
            sessions.put('_epson', value=epson)


        else:
            sessions.put('_epson', value=False)
            Popups.dialog_msg('Printer Error', 'Receipt printer not found. Please check settings and try again')

    def reports_page(self):
        webbrowser.open("https://www.jayscleaners.com/reports")

    def settings_page(self):
        webbrowser.open("https://jayscleaners.com/admins/settings")

    def delivery_page(self):
        webbrowser.open("https://www.jayscleaners.com/delivery/overview")
