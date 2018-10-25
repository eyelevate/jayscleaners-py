import sys
import platform
import time
import os

# !/usr/local/bin/python3
# !/usr/bin/env python3

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

# Models
from models.sync import Sync

# Helpers
from decimal import *

getcontext().prec = 3
from models.kv_generator import KvString
from models.jobs import Job
import threading
import queue


import calendar
import datetime
import json
import math
from _pydecimal import Decimal
from calendar import Calendar
from threading import Thread

from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ObjectProperty, partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch

from kivy.uix.textinput import TextInput
from models.addresses import Address
from models.cards import Card
# from classes.popups import Popups
from models.companies import Company
from models.credits import Credit
from models.custids import Custid
from models.deliveries import Delivery
from models.inventory_items import InventoryItem
from models.invoice_items import InvoiceItem
from models.printers import Printer
from models.profiles import Profile
from models.schedules import Schedule
from models.transactions import Transaction
from models.users import User
from classes.popups import Popups
from models.sessions import sessions
from models.static import Static
from models.constants import Constants
from pubsub import pub

auth_user = User()
Job = Job()

ERROR_COLOR = 0.94, 0.33, 0.33, 1
DEFAULT_COLOR = 0.5, 0.5, 0.5, 1.0
unix = time.time()
NOW = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
KV = KvString()
SYNC = Sync()
queueLock = threading.Lock()
workQueue = queue.Queue(10)
list_len = []
printer_list = {}
SYNC_POPUP = Popup()


class SearchScreen(Screen):
    id = ObjectProperty(None)
    cust_mark_label = ObjectProperty(None)
    search_table_rv = ObjectProperty(None)
    invoice_table_rows = []
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
    get_invoices = None
    epson = None
    bixolon = None
    zebra = None
    invitems = None

    def __init__(self, **kwargs):
        super(SearchScreen, self).__init__(**kwargs)
        pub.subscribe(self.set_epson_printer, "set_epson_printer")
        pub.subscribe(self.set_bixolon_printer, "set_bixolon_printer")
        pub.subscribe(self.set_zebra_printer, "set_zebra_printer")

    def attach(self):
        pub.subscribe(self.invoice_selected, "invoice_selected")

    def detach(self):
        pub.unsubscribe(self.invoice_selected, "invoice_selected")

    def set_epson_printer(self, device):
        self.epson = device
        print(self.epson)

    def set_bixolon_printer(self, device):
        self.bixolon = device
        print(self.bixolon)

    def set_zebra_printer(self, device):
        self.zebra = device
        print(self.zebra)

    def scheduler_stop(self):
        pass

    def scheduler_restart(self):
        pass

    def reset(self, *args, **kwargs):

        # reset member variables
        sessions.put('_searchText', value=None)
        self.invitems = None
        self.quick_box = None
        self.calc_history = []
        self.calc_amount = []
        self.selected_tags_list = []
        self.selected_account_tr = []
        self.invoice_table_rows = []
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
        self.get_invoices = None
        self.search.text = ''
        if sessions.get('_searchResultsStatus')['value']:
            users = SYNC.customers_grab(sessions.get('_customerId')['value'])
            Clock.schedule_once(partial(self.customer_results, users), 1)

        else:
            sessions.put('_customerId',value=None)
            sessions.put('_invoiceId', value=None)

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
            self.reprint_btn.disabled = True
            self.quick_btn.disabled = True
            self.pickup_btn.disabled = True
            self.dropoff_btn.disabled = True
            # clear the search text input
            self.search.text = ''
            # clear the inventory table
            self.search_table_rv.data = []
            self.due_date = None
            self.due_date_string = None
            sessions.put('_searchResultsStatus',value=False)

        Clock.schedule_once(self.focus_input)
        self.close_initial_popup()

    def focus_input(self, *args, **kwargs):
        self.search.focus = True

    def sync_db(self):
        pass

    def open_popup(self, *args, **kwargs):

        SYNC_POPUP.title = "Loading"
        content = KV.popup_alert("Please wait while the page is loading")
        SYNC_POPUP.content = Builder.load_string(content)
        SYNC_POPUP.open()
        # send event
        pub.sendMessage('close_loading_popup', popup=SYNC_POPUP)

    def close_initial_popup(self, *args, **kwargs):
        SYNC_POPUP.dismiss()

    def search_customer(self, *args, **kwargs):
        sessions.put('_invoiceId', value=None)

        if len(self.search.text) > 0:
            users = SYNC.customers_grab(self.search.text)
            self.customer_results(users)

        else:
            Popups.dialog_msg(title_string='Search Error',
                              msg_string='Search cannot be an empty value. Please try again.')

    def update_invoice_rows(self):
        self.invoice_table_rows = []
        self.edit_invoice_btn.disabled = True
        if self.get_invoices is not False:
            for inv in self.get_invoices:
                """ Creates invoice table row and displays it to screen """
                check_invoice_id = False
                try:
                    check_invoice_id = True if (
                                int(sessions.get('_invoiceId')['value']) - int(inv['id']) == 0) else False
                    if check_invoice_id:
                        self.edit_invoice_btn.disabled = False
                except ValueError:
                    pass
                except TypeError:
                    pass
                # invoice_id = inv['invoice_id']
                invoice_id = inv['id']

                company_id = inv['company_id']
                company_name = 'R' if company_id is 1 else 'M'
                quantity = inv['quantity']
                rack = inv['rack']
                total = Static.us_dollar(inv['total'])
                due = inv['due_date']
                count_invoice_items = 0
                if 'invoice_items' in inv:
                    iitems = inv['invoice_items']
                    if len(iitems) > 0:
                        count_invoice_items = len(iitems)
                try:
                    dt = datetime.datetime.strptime(due, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    dt = datetime.datetime.strptime('1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
                except TypeError:
                    dt = datetime.datetime.strptime('1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
                due_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
                dow = Static.dow(dt.replace(tzinfo=datetime.timezone.utc).weekday())
                due_date = dt.strftime('%m/%d {}').format(dow)
                dt = datetime.datetime.strptime(NOW,
                                                "%Y-%m-%d %H:%M:%S") if NOW is not None else datetime.datetime.strptime(
                    '1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
                now_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
                # check to see if invoice is overdue

                invoice_status = int(inv['status'])
                row_settings = self._make_row_settings(invoice_status, check_invoice_id, due_strtotime, now_strtotime, count_invoice_items)

                self.invoice_table_rows.append({
                    'column': 1,
                    'invoice_id': invoice_id,
                    'text': '[color={}][b]{}[/b][/color]'.format(row_settings['text_color'], '{0:06d}'.format(invoice_id)),
                    'background_color': row_settings['background_color'],
                    'background_normal': ''
                })
                self.invoice_table_rows.append({
                    'column': 2,
                    'invoice_id': invoice_id,
                    'text': '[color={}][b]{}[/b][/color]'.format(row_settings['text_color'], company_name),
                    'background_color': row_settings['background_color'],
                    'background_normal': ''
                })
                self.invoice_table_rows.append({
                    'column': 3,
                    'invoice_id': invoice_id,
                    'text': '[color={}][b]{}[/b][/color]'.format(row_settings['text_color'], due_date),
                    'background_color': row_settings['background_color'],
                    'background_normal': ''
                })
                self.invoice_table_rows.append({
                    'column': 4,
                    'invoice_id': invoice_id,
                    'text': '[color={}][b]{}[/b][/color]'.format(row_settings['text_color'], rack),
                    'background_color': row_settings['background_color'],
                    'background_normal': ''
                })
                self.invoice_table_rows.append({
                    'column': 5,
                    'invoice_id': invoice_id,
                    'text': '[color={}][b]{}[/b][/color]'.format(row_settings['text_color'], quantity),
                    'background_color': row_settings['background_color'],
                    'background_normal': ''
                })
                self.invoice_table_rows.append({
                    'column': 6,
                    'invoice_id': invoice_id,
                    'text': '[color={}][b]${}[/b][/color]'.format(row_settings['text_color'],total),
                    'background_color': row_settings['background_color'],
                    'background_normal': ''
                })
        self.search_table_rv.data = self.invoice_table_rows

    def _make_row_settings(self, invoice_status, check_invoice_id, due_strtotime, now_strtotime, count_invoice_items):

        if invoice_status is 5:  # state 5
            text_color = '000000' if not check_invoice_id else 'e5e5e5'
            background_color = [0.826, 0.826, 0.826, 1] if not check_invoice_id else [0.369, 0.369, 0.369, 1]
            status = 5

        elif invoice_status is 4 or invoice_status is 3:  # state 4
            text_color = 'FF0000' if not check_invoice_id else 'FFCCCC'
            background_color = [1, 0.717, 0.717, 1] if not check_invoice_id else [1, 0, 0, 1]
            status = 4

        elif invoice_status is 2:  # state 3
            text_color = '228B22' if not check_invoice_id else 'D8F7D8'
            background_color = [0.847, 0.968, 0.847, 1] if not check_invoice_id else [0, 0.64, 0.149, 1]
            status = 3

        else:
            if due_strtotime < now_strtotime:  # overdue state 2
                text_color = '0F47FF' if not check_invoice_id else 'D0D8F5'
                background_color = [0.816, 0.847, 0.961, 1] if not check_invoice_id else [0.059, 0.278, 1, 1]
                status = 2

            elif count_invoice_items == 0:  # #quick drop state 6
                text_color = '000000'
                background_color = [0.9960784314, 1, 0.7176470588, 1] if not check_invoice_id else [
                    0.98431373, 1,
                    0, 1]
                status = 6
            else:  # state 1
                text_color = '000000' if not check_invoice_id else 'e5e5e5'
                background_color = [0.826, 0.826, 0.826, 1] if not check_invoice_id else [0.369, 0.369, 0.369, 1]
                status = 1
        return {
            'text_color': text_color,
            'background_color': background_color,
            'status': status
        }

    def invoice_selected(self, invoice_id, *args, **kwargs):
        sessions.put('_invoiceId',value=invoice_id)
        # show the edit button
        self.edit_invoice_btn.disabled = False
        self.update_invoice_rows()

    def customer_sync(self):

        search_sync = SYNC.invoices_grab(sessions.get('_customerId')['value'])
        self.get_invoices = search_sync

    def customer_select(self, customer_id):
        customers = SYNC.customers_grab(customer_id)
        self.customer_results(customers)
        sessions.put('_customerId',value=customer_id)
        sessions.put('_searchResultsStatus',value=True)
        Clock.schedule_once(self.focus_input)

    def customer_results(self, data, *args, **kwargs):
        # stop scheduler to get only customer data

        # Found customer via where, now display data to screen
        if data is not False:
            if len(data) == 1:
                if len(self.search.text) == 6:
                    sessions.put('_invoiceId',value=self.search.text)
                Clock.schedule_once(self.focus_input)
                for result in data:
                    sessions.put('_customerId',value=result['id'])
                    sessions.put('_searchResultsStatus',value=True if sessions.get('_customerId')['value'] else False)

                    # start syncing in background
                    self.customer_sync()

                    # last 10 setup

                    Static.update_last_10(sessions.get('_customerId')['value'],
                                          sessions.get('_last10')['value'])

                    self.update_invoice_rows()


                    Clock.schedule_once(partial(self.invoice_selected, sessions.get('_invoiceId')['value']))
                    last_drop = 'Not Available'

                    # get the custid data
                    custids = Custid()
                    custid_string = ''
                    if 'custids' in result:
                        cids = result['custids']
                        custid_string = custids.make_string(cids)

                    # display data
                    self.cust_info_label.text = 'Customer Info: [color=FF0000]Account[/color]' if result[
                                                                                                      'account'] is '1' or \
                                                                                                  result[
                                                                                                      'account'] is True or \
                                                                                                  result[
                                                                                                      'account'] is 1 else 'Customer Info:'
                    self.cust_mark_label.text = custid_string
                    self.customer_id_ti.text = str(sessions.get('_customerId')['value']) if sessions.get('_customerId')['value'] else ''
                    self.cust_last_name.text = result['last_name'] if result['last_name'] else ''
                    self.cust_first_name.text = result['first_name'] if result['first_name'] else ''
                    self.cust_phone.text = Job.make_us_phone(result['phone']) if result['phone'] else ''
                    self.cust_last_drop.text = last_drop
                    self.cust_starch.text = self.get_starch_by_id(result['starch'])
                    self.cust_credit_label.bind(on_ref_press=self.credit_history)
                    self.cust_account_label.bind(on_ref_press=self.account_history_popup)
                    self.cust_credit.text = '${:,.2f}'.format(Decimal(result['credits'])) if result[
                        'credits'] else '$0.00'
                    self.cust_account.text = '${:,.2f}'.format(Decimal(result['account_total'])) if result[
                        'account_total'] else '$0.00'
                    try:
                        self.cust_invoice_memo.text = result['invoice_memo']
                    except AttributeError:
                        self.cust_invoice_memo.text = ''

                    try:
                        self.cust_important_memo.text = result['important_memo']
                    except AttributeError:
                        self.cust_important_memo.text = ''

                # show the proper buttons
                self.history_btn.disabled = False
                self.edit_customer_btn.disabled = False
                self.reprint_btn.disabled = False
                self.quick_btn.disabled = False
                self.pickup_btn.disabled = False
                self.dropoff_btn.disabled = False
                # clear the search text input
                self.search.focus = True
                self.search.text = ''

            elif len(data) > 1:
                # show results in new screen search results
                self.search_results()
        else:
            Popups.dialog_msg(title_string='Search Results',
                              msg_string='No customers found! Please try again!')

    def search_results(self):
        sessions.put('_searchText',value= self.search.text)
        results = SYNC.customers_search_results(sessions.get('_searchText')['value'])
        sessions.put('_searchResults',value=results)
        if sessions.get('_searchResults')['value'] is not False:

            self.parent.current = 'search_results'
            self.search.focus = True

        else:
            Popups.dialog_msg(title_string='Search Results',
                              msg_string='No customers found! Please try again!')

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
        self.repopup.title = 'Reprint Invoice #{}'.format(sessions.get('_invoiceId')['value'])
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.9))
        inner_layout_1.add_widget(Button(markup=True,
                                         text="Print Card",
                                         on_press=self.print_card))
        inner_layout_1.add_widget(Button(markup=True,
                                         text='Store Copy',
                                         on_press=partial(self.reprint_invoice, 1)))
        inner_layout_1.add_widget(Button(markup=True,
                                         text='Customer Copy',
                                         on_press=partial(self.reprint_invoice, 2)))
        inner_layout_1.add_widget(Button(markup=True,
                                         text='Tags',
                                         on_press=self.reprint_tags))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_press=self.close_reprint_popup))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.repopup.content = layout
        self.repopup.open()

    def close_reprint_popup(self, *args, **kwargs):
        self.repopup.dismiss()
        sessions.put('_searchResultsStatus',value=True)
        self.reset()

    def quick_popup(self, *args, **kwargs):
        # setup calendar default date
        company = SYNC.company_grab(company_id=sessions.get('_companyId')['value'])
        if company:
            store_hours = json.loads(company['store_hours']) if company['store_hours'] else None
            if store_hours:
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
                self.quick_box.ids.quick_due_date.bind(on_press=self.make_calendar)
                inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                           orientation="horizontal")
                cancel_button = Button(text="Cancel",
                                       markup=True,
                                       on_press=self.main_popup.dismiss)
                print_button = Button(text="Print",
                                      markup=True,
                                      on_press=self.quick_print)
                inner_layout_2.add_widget(cancel_button)
                inner_layout_2.add_widget(print_button)
                base_layout.add_widget(self.quick_box)
                base_layout.add_widget(inner_layout_2)

                self.main_popup.content = base_layout
                self.main_popup.open()

                pass

    def make_calendar(self, *args, **kwargs):

        company = SYNC.company_grab(company_id=sessions.get('_companyId')['value'])
        if company:
            store_hours = json.loads(company['store_hours']) if company['store_hours'] else None
            if store_hours:
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
                                    on_press=self.prev_month)
                next_month = Button(markup=True,
                                    text=">",
                                    font_size="30sp",
                                    on_press=self.next_month)
                select_month = Factory.SelectMonth()
                self.month_button = Button(text='{}'.format(Static.month_by_number(self.month)),
                                           on_press=select_month.open)
                for index in range(12):
                    month_options = Button(text='{}'.format(Static.month_by_number(index)),
                                           size_hint_y=None,
                                           height=40,
                                           on_press=partial(self.select_calendar_month, index))
                    select_month.add_widget(month_options)

                select_month.on_select = lambda instance, x: setattr(self.month_button, 'text', x)
                select_year = Factory.SelectMonth()

                self.year_button = Button(text="{}".format(self.year),
                                          on_press=select_year.open)
                for index in range(10):
                    year_options = Button(text='{}'.format(int(self.year) + index),
                                          size_hint_y=None,
                                          height=40,
                                          on_press=partial(self.select_calendar_year, index))
                    select_year.add_widget(year_options)

                select_year.bind(on_select=lambda instance, x: setattr(self.year_button, 'text', x))
                calendar_selection.add_widget(prev_month)
                calendar_selection.add_widget(self.month_button)
                calendar_selection.add_widget(self.year_button)
                calendar_selection.add_widget(next_month)
                self.calendar_layout = GridLayout(cols=7,
                                                  rows=8,
                                                  size_hint=(1, 0.9))
                store_hours = Company().get_store_hours(sessions.get('_companyId')['value'])
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
                                                 on_press=popup.dismiss))

                layout.add_widget(inner_layout_1)
                layout.add_widget(inner_layout_2)
                popup.content = layout
                popup.open()

    def create_calendar_table(self):
        # set the variables

        company = SYNC.company_grab(company_id=sessions.get('_companyId')['value'])
        if company:
            store_hours = json.loads(company['store_hours']) if company['store_hours'] else None
            if store_hours:
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
                                                                          on_press=partial(self.select_due_date, today_base))
                                        elif check_date == check_due_date:
                                            item = Factory.CalendarButton(text="[color=008080][b]{}[/b][/color]".format(day[0]),
                                                                          background_color=(
                                                                              0.2156862, 0.9921568, 0.98823529, 1),
                                                                          background_normal='',
                                                                          on_press=partial(self.select_due_date, today_base))
                                        elif check_today < check_date < check_due_date:
                                            item = Factory.CalendarButton(text="[color=008080][b]{}[/b][/color]".format(day[0]),
                                                                          background_color=(0.878431372549020, 1, 1, 1),
                                                                          background_normal='',
                                                                          on_press=partial(self.select_due_date, today_base))
                                        else:
                                            item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]),
                                                                          on_press=partial(self.select_due_date, today_base))
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
        self.month_button.text = '{}'.format(Static.month_by_number(self.month))
        self.year_button.text = '{}'.format(self.year)
        self.create_calendar_table()

    def next_month(self, *args, **kwargs):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.month_button.text = '{}'.format(Static.month_by_number(self.month))
        self.year_button.text = '{}'.format(self.year)
        self.create_calendar_table()

    def select_calendar_month(self, month, *args, **kwargs):
        self.month = month
        self.create_calendar_table()

    def select_calendar_year(self, year, *args, **kwargs):
        self.year = year
        self.create_calendar_table()

    def select_due_date(self, selected_date, *args, **kwargs):
        company = SYNC.company_grab(company_id=sessions.get('_companyId')['value'])
        if company:
            store_hours = json.loads(company['store_hours']) if company['store_hours'] else None
            if store_hours:

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
                        on_press=popup.dismiss)
        inner_layout_2.add_widget(cancel)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()
        pass

    def quick_print_store_copy(self, *args, **kwargs):
        companies = Company()

        comps = SYNC.company_grab(sessions.get('_companyId')['value'])
        if comps:
            companies.id = comps['id']
            companies.name = comps['name']
            companies.street = comps['street']
            companies.city = comps['city']
            companies.state = comps['state']
            companies.zip = comps['zip']
            companies.email = comps['email']
            companies.phone = comps['phone']
        # save the invoice
        data = {
            'company_id': sessions.get('_companyId')['value'],
            'quantity': self.quick_box.ids.quick_count.text,
            'pretax': 0,
            'tax': 0,
            'total': 0,
            'customer_id': sessions.get('_customerId')['value'],
            'status': 1,
            'due_date': self.due_date.strftime('%Y-%m-%d %H:%M:%S'),
            'memo': self.quick_box.ids.quick_invoice_memo.text
        }
        items = {}

        save_invoice = SYNC.create_invoice(data, items)
        if save_invoice is not False:

            # print invoices
            if self.epson:
                pr = Printer()

                customers = User()
                custs = SYNC.customers_grab(sessions.get('_customerId')['value'])
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
                        customers.role_id = user['role_id']
                self.epson.write(pr.pcmd('TXT_ALIGN_CT'))
                self.epson.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                             invert=False, smooth=False, flip=False))
                self.epson.write("QUICK DROP - STORE COPY\n")
                self.epson.write("{}\n".format(companies.name))
                self.epson.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))
                self.epson.write("{}\n".format(companies.street))
                self.epson.write("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                self.epson.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))

                self.epson.write("{}\n".format(Job.make_us_phone(companies.phone)))
                self.epson.write("{}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                self.epson.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                invert=False, smooth=False, flip=False))
                self.epson.write("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                self.epson.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                             invert=False, smooth=False, flip=False))
                padded_customer_id = '{0:05d}'.format(sessions.get('_customerId')['value'])
                self.epson.write("{}\n".format(padded_customer_id))

                # Print barcode
                self.epson.write(pr.pcmd_barcode(str(padded_customer_id)))

                self.epson.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                invert=False, smooth=False, flip=False))
                self.epson.write('{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                self.epson.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                invert=False, smooth=False, flip=False))
                self.epson.write('{}\n'.format(Job.make_us_phone(customers.phone)))
                self.epson.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                self.epson.write('-----------------------------------------\n')

                self.epson.write(pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                             invert=False, smooth=False, flip=False))
                self.epson.write(
                    '{} PCS\n'.format(
                        self.quick_box.ids.quick_count.text if self.quick_box.ids.quick_count.text else '0'))
                self.epson.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                self.epson.write('-----------------------------------------\n')
                if self.quick_box.ids.quick_invoice_memo.text:
                    self.epson.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                                 invert=False, smooth=False, flip=False))
                    self.epson.write('{}\n'.format(self.quick_box.ids.quick_invoice_memo.text))

                self.epson.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=1, density=1,
                                             invert=False, smooth=False, flip=False))
                # Cut paper
                self.epson.write('\n\n\n\n\n\n')
                self.epson.write(pr.pcmd('PARTIAL_CUT'))


            else:
                Popups.dialog_msg(title_string='Printer Error',
                                  msg_string='Could not find usb.')

        else:
            Popups.dialog_msg(title_string='Error!',
                              msg_string='Could not save quick drop! Please try again!')

            pass

        self.main_popup.dismiss()
        self.customer_select(sessions.get('_customerId')['value'])

    def quick_print_both(self, *args, **kwargs):
        companies = Company()
        comps = SYNC.company_grab(sessions.get('_companyId')['value'])
        if comps:
            companies.id = comps['id']
            companies.name = comps['name']
            companies.street = comps['street']
            companies.city = comps['city']
            companies.state = comps['state']
            companies.zip = comps['zip']
            companies.email = comps['email']
            companies.phone = comps['phone']
        # save the invoice
        data = {
            'company_id': sessions.get('_companyId')['value'],
            'quantity': self.quick_box.ids.quick_count.text,
            'pretax': 0,
            'tax': 0,
            'total': 0,
            'customer_id': sessions.get('_customerId')['value'],
            'status': 1,
            'due_date': self.due_date.strftime('%Y-%m-%d %H:%M:%S'),
            'memo': self.quick_box.ids.quick_invoice_memo.text
        }
        items = {}

        save_invoice = SYNC.create_invoice(data, items)
        if save_invoice is not False:
            # print invoices
            if sessions.get('_self.epson')['value']:
                pr = Printer()
                customers = User()
                custs = SYNC.customers_grab(sessions.get('_customerId')['value'])
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
                        customers.role_id = user['role_id']

                self.epson.write(pr.pcmd('TXT_ALIGN_CT'))
                self.epson.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                             invert=False, smooth=False, flip=False))
                self.epson.write("QUICK DROP\n")
                self.epson.write("{}\n".format(companies.name))
                self.epson.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))
                self.epson.write("{}\n".format(companies.street))
                self.epson.write("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                self.epson.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))

                self.epson.write("{}\n".format(Job.make_us_phone(companies.phone)))
                self.epson.write("{}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                self.epson.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                invert=False, smooth=False, flip=False))
                self.epson.write("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                self.epson.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                             invert=False, smooth=False, flip=False))
                padded_customer_id = '{0:05d}'.format(sessions.get('_customerId')['value'])
                self.epson.write("{}\n".format(padded_customer_id))

                # Print barcode
                self.epson.write(pr.pcmd_barcode(str(padded_customer_id)))

                self.epson.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                invert=False, smooth=False, flip=False))
                self.epson.write('{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                self.epson.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                invert=False, smooth=False, flip=False))
                self.epson.write('{}\n'.format(Job.make_us_phone(customers.phone)))
                self.epson.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                self.epson.write('-----------------------------------------\n')

                self.epson.write(pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                             invert=False, smooth=False, flip=False))
                self.epson.write('{} PCS\n'.format(
                    self.quick_box.ids.quick_count.text if self.quick_box.ids.quick_count.text else '0'))
                self.epson.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                self.epson.write('-----------------------------------------\n')
                if self.quick_box.ids.quick_invoice_memo.text:
                    self.epson.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                                 invert=False, smooth=False, flip=False))
                    self.epson.write('{}\n'.format(self.quick_box.ids.quick_invoice_memo.text))

                self.epson.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=1, density=1,
                                             invert=False, smooth=False, flip=False))
                # Cut paper
                self.epson.write('\n\n\n\n\n\n')
                self.epson.write(pr.pcmd('PARTIAL_CUT'))

                # SECOND Copy
                self.epson.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                             invert=False, smooth=False, flip=False))
                self.epson.write("QUICK DROP - STORE COPY\n")
                self.epson.write("{}\n".format(companies.name))
                self.epson.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))
                self.epson.write("{}\n".format(companies.street))
                self.epson.write("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                self.epson.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))

                self.epson.write("{}\n".format(Job.make_us_phone(companies.phone)))
                self.epson.write("{}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                self.epson.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                invert=False, smooth=False, flip=False))
                self.epson.write("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                self.epson.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                             invert=False, smooth=False, flip=False))
                padded_customer_id = '{0:05d}'.format(sessions.get('_customerId')['value'])
                self.epson.write("{}\n".format(padded_customer_id))

                # Print barcode
                self.epson.write(pr.pcmd_barcode(str(padded_customer_id)))

                self.epson.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                invert=False, smooth=False, flip=False))
                self.epson.write('{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                self.epson.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                invert=False, smooth=False, flip=False))
                self.epson.write('{}\n'.format(Job.make_us_phone(customers.phone)))
                self.epson.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                self.epson.write('-----------------------------------------\n')

                self.epson.write(pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                             invert=False, smooth=False, flip=False))
                self.epson.write(
                    '{} PCS\n'.format(
                        self.quick_box.ids.quick_count.text if self.quick_box.ids.quick_count.text else '0'))
                self.epson.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                self.epson.write('-----------------------------------------\n')
                if self.quick_box.ids.quick_invoice_memo.text:
                    self.epson.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                                 invert=False, smooth=False, flip=False))
                    self.epson.write('{}\n'.format(self.quick_box.ids.quick_invoice_memo.text))

                self.epson.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=1, density=1,
                                             invert=False, smooth=False, flip=False))
                # Cut paper
                self.epson.write('\n\n\n\n\n\n')
                self.epson.write(pr.pcmd('PARTIAL_CUT'))

            else:
                Popups.dialog_msg(title_string='Printer Error',
                                  msg_string='Could not find usb. Please shut down system and find the proper connection via the Zadig app.')

        else:
            Popups.dialog_msg(title_string='Error!',
                              msg_string='Could not save quick drop! Please try again!')

        self.main_popup.dismiss()
        self.customer_select(sessions.get('_customerId')['value'])

    def reprint_invoice(self, type, *args, **kwargs):
        if sessions.get('_invoiceId')['value']:
            # print invoices
            if self.epson:
                pr = Printer()
                companies = Company()
                marks = []
                comps = SYNC.company_grab(sessions.get('_companyId')['value'])
                if comps:
                    companies.id = comps['id']
                    companies.name = comps['name']
                    companies.street = comps['street']
                    companies.city = comps['city']
                    companies.state = comps['state']
                    companies.zip = comps['zip']
                    companies.email = comps['email']
                    companies.phone = comps['phone']
                customers = User()
                custs = SYNC.customers_grab(sessions.get('_customerId')['value'])
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
                        customers.role_id = user['role_id']

                        marks = user['custids']
                invs = SYNC.invoice_grab_id(sessions.get('_invoiceId')['value'])
                if invs:
                    invoice_quantity = invs['quantity']
                    invoice_subtotal = invs['pretax']
                    invoice_tax = invs['tax']
                    invoice_total = invs['total']

                    try:
                        invoice_due_date = datetime.datetime.strptime(invs['due_date'], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        invoice_due_date = datetime.datetime.now()

                    inv_items = invs['invoice_items']

                    colors = {}
                    if inv_items:
                        for invoice_item in inv_items:
                            item_id = invoice_item['item_id']
                            colors[item_id] = {}
                    print_sync_invoice = {sessions.get('_invoiceId')['value']: {}}
                    if inv_items:
                        for invoice_item in inv_items:
                            item_id = invoice_item['item_id']
                            items = SYNC.inventory_items_grab(item_id)
                            if items:
                                item_name = items['name']
                                inventory_id = items['inventory_id']
                            else:
                                item_name = None
                                inventory_id = None

                            inventory = SYNC.inventory_grab(inventory_id)
                            if inventory:
                                inventory_init = inventory['name'][:1].capitalize()
                                laundry = inventory['laundry']
                            else:
                                inventory_init = ''
                                laundry = 0

                            display_name = '{} ({})'.format(item_name, Static.get_starch_by_code(
                                customers.starch)) if laundry else item_name

                            item_color = invoice_item['color']
                            if item_id in colors:
                                if item_color in colors[item_id]:
                                    colors[item_id][item_color] += 1
                                else:
                                    colors[item_id][item_color] = 1
                            item_memo = invoice_item['memo']
                            item_subtotal = Decimal(invoice_item['pretax'])
                            if sessions.get('_invoiceId')['value'] in print_sync_invoice:
                                if item_id in print_sync_invoice[sessions.get('_invoiceId')['value']]:
                                    print_sync_invoice[sessions.get('_invoiceId')['value']][item_id]['item_price'] += item_subtotal
                                    print_sync_invoice[sessions.get('_invoiceId')['value']][item_id]['qty'] += 1
                                    if item_memo:
                                        print_sync_invoice[sessions.get('_invoiceId')['value']][item_id]['memos'].append(item_memo)

                                    if item_id in colors:
                                        print_sync_invoice[sessions.get('_invoiceId')['value']][item_id]['colors'] = colors[item_id]
                                    else:
                                        print_sync_invoice[sessions.get('_invoiceId')['value']][item_id]['colors'] = []
                                else:
                                    print_sync_invoice[sessions.get('_invoiceId')['value']][item_id] = {
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
                    self.epson.write(pr.pcmd('TXT_ALIGN_CT'))
                    self.epson.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                    density=5, invert=False, smooth=False, flip=False))
                    self.epson.write("::CUSTOMER::\n")
                    self.epson.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                    invert=False, smooth=False, flip=False))
                    self.epson.write("{}\n".format(companies.name))
                    self.epson.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                    invert=False, smooth=False, flip=False))
                    self.epson.write("{}\n".format(companies.street))
                    self.epson.write("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                    self.epson.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                    invert=False, smooth=False, flip=False))

                    self.epson.write("{}\n".format(Job.make_us_phone(companies.phone)))
                    self.epson.write("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))
                    self.epson.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                    invert=False, smooth=False, flip=False))
                    self.epson.write("READY BY: {}\n\n".format(invoice_due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                    self.epson.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                    invert=False, smooth=False, flip=False))
                    padded_customer_id = '{0:05d}'.format(sessions.get('_customerId')['value'])
                    self.epson.write("{}\n".format(padded_customer_id))

                    # Print barcode
                    self.epson.write(pr.pcmd_barcode(str(padded_customer_id)))

                    self.epson.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                    invert=False, smooth=False, flip=False))
                    self.epson.write('{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                    self.epson.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                    invert=False, smooth=False, flip=False))
                    self.epson.write("{}\n".format(Job.make_us_phone(customers.phone)))
                    self.epson.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                    invert=False, smooth=False, flip=False))
                    self.epson.write('-----------------------------------------\n')

                    if sessions.get('_invoiceId')['value'] in print_sync_invoice:
                        item_type = 'D'
                        for item_id, invoice_item in print_sync_invoice[sessions.get('_invoiceId')['value']].items():
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
                            self.epson.write('{} {}   {}\n'.format(item_type, item_qty, item_name))

                            if len(item_memo) > 0:
                                self.epson.write(pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                             height=1,
                                                             density=5, invert=False, smooth=False, flip=False))
                                self.epson.write('     {}\n'.format('/ '.join(item_memo)))
                            if len(item_color_string) > 0:
                                self.epson.write(pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                             height=1,
                                                             density=5, invert=False, smooth=False, flip=False))
                                self.epson.write('     {}\n'.format(', '.join(item_color_string)))

                    self.epson.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                    invert=False, smooth=False, flip=False))
                    self.epson.write('-----------------------------------------\n')
                    self.epson.write(
                        pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                    invert=False, smooth=False, flip=False))
                    self.epson.write('{} PCS\n'.format(invoice_quantity))
                    self.epson.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                    invert=False, smooth=False, flip=False))
                    self.epson.write('-----------------------------------------\n')

                    if customers.invoice_memo:
                        self.epson.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write('{}\n'.format(customers.invoice_memo))
                    # Cut paper
                    self.epson.write('\n\n\n\n\n\n')
                    self.epson.write(pr.pcmd('PARTIAL_CUT'))

                if type == 1:
                    # Print store copies
                    if print_sync_invoice:  # if invoices synced
                        for invoice_id, item_id in print_sync_invoice.items():
                            item_type = 'D'
                            if isinstance(invoice_id, str):
                                invoice_id = int(invoice_id)

                            # start invoice
                            self.epson.write(pr.pcmd('TXT_ALIGN_CT'))
                            self.epson.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=5, invert=False, smooth=False, flip=False))
                            self.epson.write("::COPY::\n")
                            self.epson.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                            invert=False, smooth=False, flip=False))
                            self.epson.write("{}\n".format(companies.name))
                            self.epson.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=5,
                                            invert=False, smooth=False, flip=False))
                            self.epson.write("{}\n".format(Job.make_us_phone(companies.phone)))
                            self.epson.write("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))
                            self.epson.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2,
                                            density=5,
                                            invert=False, smooth=False, flip=False))
                            self.epson.write(
                                "READY BY: {}\n\n".format(invoice_due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                            self.epson.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                            invert=False, smooth=False, flip=False))
                            self.epson.write("{}\n".format('{0:06d}'.format(invoice_id)))
                            # Print barcode
                            self.epson.write(pr.pcmd_barcode('{}'.format(str('{0:06d}'.format(invoice_id)))))

                            self.epson.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3,
                                            density=6,
                                            invert=False, smooth=False, flip=False))
                            self.epson.write(
                                '{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                            self.epson.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=2,
                                            invert=False, smooth=False, flip=False))
                            self.epson.write("{}\n".format(Job.make_us_phone(customers.phone)))
                            self.epson.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=1,
                                            invert=False, smooth=False, flip=False))
                            self.epson.write('-----------------------------------------\n')

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
                                        Static.us_dollar(item_price)) + 4
                                    string_offset = 42 - string_length if 42 - string_length > 0 else 0
                                    self.epson.write('{} {}   {}{}{}\n'.format(item_type,
                                                                               item_qty,
                                                                               item_name,
                                                                               ' ' * string_offset,
                                                                               Static.us_dollar(item_price)))

                                    if len(item_memo) > 0:
                                        self.epson.write(
                                            pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                        height=1,
                                                        density=5, invert=False, smooth=False, flip=False))
                                        self.epson.write('     {}\n'.format('/ '.join(item_memo)))
                                    if len(item_color_string) > 0:
                                        self.epson.write(
                                            pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                        height=1,
                                                        density=5, invert=False, smooth=False, flip=False))
                                        self.epson.write('     {}\n'.format(', '.join(item_color_string)))

                            self.epson.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=1,
                                            invert=False, smooth=False, flip=False))
                            self.epson.write('-----------------------------------------\n')
                            self.epson.write(
                                pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                            invert=False, smooth=False, flip=False))
                            self.epson.write('{} PCS\n'.format(invoice_quantity))
                            self.epson.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=1,
                                            invert=False, smooth=False, flip=False))
                            self.epson.write('-----------------------------------------\n')
                            self.epson.write(
                                pr.pcmd_set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                            invert=False, smooth=False, flip=False))
                            self.epson.write('    SUBTOTAL:')
                            self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                            string_length = len(Static.us_dollar(invoice_subtotal))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            self.epson.write('{}{}\n'.format(' ' * string_offset, Static.us_dollar(invoice_subtotal)))
                            self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                            self.epson.write('         TAX:')
                            string_length = len(Static.us_dollar(invoice_tax))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                            self.epson.write('{}{}\n'.format(' ' * string_offset, Static.us_dollar(invoice_tax)))
                            self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                            self.epson.write('       TOTAL:')
                            self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                            string_length = len(Static.us_dollar(invoice_total))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            self.epson.write('{}{}\n'.format(' ' * string_offset,
                                                             Static.us_dollar(invoice_total)))
                            self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                            self.epson.write('     BALANCE:')
                            string_length = len(Static.us_dollar(invoice_total))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            self.epson.write('{}{}\n\n'.format(' ' * string_offset, Static.us_dollar(invoice_total)))
                            if customers.invoice_memo:
                                self.epson.write(
                                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                                invert=False, smooth=False, flip=False))
                                self.epson.write('{}\n'.format(customers.invoice_memo))
                            if item_type == 'L':
                                # get customer mark
                                marks = SYNC.marks_query(sessions.get('_customerId')['value'], 1)
                                if marks is not False:
                                    m_list = []
                                    for mark in marks:
                                        m_list.append(mark['mark'])
                                    self.epson.write(
                                        pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=3, height=4,
                                                    density=8, invert=False, smooth=False, flip=False))
                                    self.epson.write('{}\n\n'.format(', '.join(m_list)))

                            # Cut paper
                            self.epson.write('\n\n\n\n\n\n')
                            self.epson.write(pr.pcmd('PARTIAL_CUT'))
            else:
                Popups.dialog_msg(title_string='Printer Error',
                                  msg_string='No printer found. Please try again.')
        else:
            Popups.dialog_msg(title_string='Reprint Error',
                              msg_string='Please select an invoice.')

    def print_card(self, *args, **kwargs):

        if self.epson:
            pr = Printer()
            companies = Company()
            comps = SYNC.company_grab(sessions.get('_companyId')['value'])
            if comps:
                companies.id = comps['id']
                companies.name = comps['name']
                companies.street = comps['street']
                companies.city = comps['city']
                companies.state = comps['state']
                companies.zip = comps['zip']
                companies.email = comps['email']
                companies.phone = comps['phone']
            customers = User()
            custs = SYNC.customers_grab(sessions.get('_customerId')['value'])
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
                    customers.role_id = user['role_id']

            now = datetime.datetime.now()
            self.epson.write(pr.pcmd('TXT_ALIGN_CT'))
            self.epson.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                         invert=False, smooth=False, flip=False))
            self.epson.write("{}\n".format(companies.name))
            self.epson.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                         invert=False, smooth=False, flip=False))
            self.epson.write("{}\n".format(companies.street))
            self.epson.write("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
            self.epson.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                         invert=False, smooth=False, flip=False))

            self.epson.write("{}\n".format(Job.make_us_phone(companies.phone)))
            self.epson.write("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))

            self.epson.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                         invert=False, smooth=False, flip=False))
            # Print barcode
            padded_customer_id = '{0:05d}'.format(sessions.get('_customerId')['value'])
            self.epson.write("{}\n".format(padded_customer_id))
            self.epson.write(pr.pcmd_barcode(str(padded_customer_id)))
            self.epson.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                         invert=False, smooth=False, flip=False))
            self.epson.write('{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

            self.epson.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                         invert=False, smooth=False, flip=False))
            self.epson.write("{}\n".format(Job.make_us_phone(customers.phone)))
            self.epson.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                         invert=False, smooth=False, flip=False))

            self.epson.write('-----------------------------------------\n')
            # Cut paper
            self.epson.write('\n\n\n\n\n\n')
            self.epson.write(pr.pcmd('PARTIAL_CUT'))

        else:
            Popups.dialog_msg('Printer Error', 'No printer found. Please try again.')

    def reprint_tags(self, *args, **kwargs):
        popup = Popup()
        popup.title = 'Tag Reprint'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='vertical',
                                   size_hint=(1, 0.9))
        self.tags_grid = Factory.TagsGrid()
        invoices = SYNC.invoice_grab_id(sessions.get('_invoiceId')['value'])
        if invoices:
            self._make_tag_rows()
        inner_layout_1.add_widget(self.tags_grid)
        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="Cancel",
                               on_press=popup.dismiss)
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

    def _make_tag_rows(self):
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
        invoices = SYNC.invoice_grab_id(sessions.get('_invoiceId')['value'])
        if invoices:
            self.invitems = invoices['invoice_items']

        if len(self.invitems) > 0:
            for ii in self.invitems:
                invoice_items_id = ii['id']
                iitem_id = ii['item_id']
                tags_to_print = 1
                item_name = ''
                if 'inventory_item' in ii:
                    if 'tags' in ii['inventory_item']:
                        tags_to_print = int(ii['inventory_item']['tags'])
                    if 'name' in ii['inventory_item']:
                        item_name = ii['inventory_item']['name']

                item_color = ii['color']
                item_memo = ii['memo']
                selected = True if invoice_items_id in self.selected_tags_list else False
                if not selected:
                    trtd1 = Button(text=str(invoice_items_id),
                                   on_press=partial(self.select_tag, invoice_items_id))
                    trtd2 = Button(text=str(item_name),
                                   on_press=partial(self.select_tag, invoice_items_id))
                    trtd3 = Button(text=str(item_color),
                                   on_press=partial(self.select_tag, invoice_items_id))
                    trtd4 = Button(text=str(item_memo),
                                   on_press=partial(self.select_tag, invoice_items_id))
                    trtd5 = Button(text=str(tags_to_print),
                                   on_press=partial(self.select_tag, invoice_items_id))
                else:
                    trtd1 = Button(text='[color=ffffff][b]{}[/b][/color]'.format(str(invoice_items_id)),
                                   markup=True,
                                   on_press=partial(self.select_tag, invoice_items_id),
                                   background_color=Constants().colors('lime_green'))
                    trtd2 = Button(text='[color=ffffff][b]{}[/b][/color]'.format(str(item_name)),
                                   markup=True,
                                   on_press=partial(self.select_tag, invoice_items_id),
                                   background_color=Constants().colors('lime_green'))
                    trtd3 = Button(text='[color=ffffff][b]{}[/b][/color]'.format(str(item_color)),
                                   markup=True,
                                   on_press=partial(self.select_tag, invoice_items_id),
                                   background_color = Constants().colors('lime_green'))
                    trtd4 = Button(text='[color=ffffff][b]{}[/b][/color]'.format(str(item_memo)),
                                   markup=True,
                                   on_press=partial(self.select_tag, invoice_items_id),
                                   background_color=Constants().colors('lime_green'))
                    trtd5 = Button(text='[color=ffffff][b]{}[/b][/color]'.format(str(tags_to_print)),
                                   markup=True,
                                   on_press=partial(self.select_tag, invoice_items_id),
                                   background_color=Constants().colors('lime_green'))
                self.tags_grid.ids.tags_table.add_widget(trtd1)
                self.tags_grid.ids.tags_table.add_widget(trtd2)
                self.tags_grid.ids.tags_table.add_widget(trtd3)
                self.tags_grid.ids.tags_table.add_widget(trtd4)
                self.tags_grid.ids.tags_table.add_widget(trtd5)


    def select_tag(self, item_id, *args, **kwargs):

        if item_id in self.selected_tags_list:
            # remove the tag
            self.selected_tags_list.remove(item_id)
        else:
            # add the tag
            self.selected_tags_list.append(item_id)
        self._make_tag_rows()

        pass

    def print_all_tags(self, *args, **kwargs):
        if sessions.get('_invoiceId')['value']:
            customers = User()
            custs = SYNC.customers_grab(sessions.get('_customerId')['value'])
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
                    customers.role_id = user['role_id']

            invoice_id_str = str(sessions.get('_invoiceId')['value'])
            invs = SYNC.invoice_grab_id(sessions.get('_invoiceId')['value'])
            due_date = 'SUN'
            invoice_items = []
            if invs:
                dt = datetime.datetime.strptime(invs['due_date'], "%Y-%m-%d %H:%M:%S")
                due_date = dt.strftime('%a').upper()
                invoice_items = invs['invoice_items']
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

            if self.bixolon:

                laundry_to_print = []
                if invoice_items:
                    # self.bixolon.write('\x1b\x40')
                    # self.bixolon.write('\x1b\x6d')
                    for ii in invoice_items:

                        iitem_id = ii['item_id']
                        tags_to_print = InventoryItem().tagsToPrint(iitem_id)
                        item_name = InventoryItem().getItemName(iitem_id)
                        item_color = ii['color']
                        invoice_item_id = ii['id']
                        laundry_tag = InventoryItem().getLaundry(iitem_id)
                        memo_string = ii['memo']
                        if laundry_tag:
                            laundry_to_print.append(invoice_item_id)
                        else:
                            for _ in range(tags_to_print):

                                self.bixolon.write('\x1b!\x30')  # QUAD SIZE
                                self.bixolon.write('{}{}\n'.format(text_left, text_right))
                                self.bixolon.write('\x1b!\x00')
                                self.bixolon.write(name_number_string)
                                self.bixolon.write('\n')
                                self.bixolon.write('{0:06d}'.format(int(invoice_item_id)))
                                self.bixolon.write(' {} {}'.format(item_name, item_color))
                                if memo_string:
                                    self.bixolon.write('\n{}'.format(memo_string))
                                    memo_len = '\n\n\n' if len(
                                        memo_string) <= 32 else '\n\n\n' + '\n' * int(
                                        (len(memo_string)) / 32)
                                    self.bixolon.write(memo_len)
                                    self.bixolon.write('\x1b\x6d')

                                else:

                                    self.bixolon.write('\n\n\n')
                                    self.bixolon.write('\x1b\x6d')

                if len(laundry_to_print) > 0:
                    # self.bixolon.write('\x1b\x40')
                    # self.bixolon.write('\x1b\x6d')
                    laundry_count = len(laundry_to_print)
                    shirt_mark = Custid().getCustomerMark(sessions.get('_customerId')['value'])
                    marks = SYNC.marks_query(sessions.get('_customerId')['value'], 1)
                    if marks is not False:
                        for mark in marks:
                            shirt_mark = mark['mark']
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

                        self.bixolon.write('\x1b!\x30')  # QUAD SIZE
                        self.bixolon.write(mark_mark_string)
                        self.bixolon.write('\n')
                        self.bixolon.write('\x1b!\x00')
                        self.bixolon.write(name_name_string)
                        self.bixolon.write('\n')
                        self.bixolon.write(id_id_string)

                        self.bixolon.write('\n\n\n\x1b\x6d')

                # FINAL CUT
                self.bixolon.write('\n\n\n\n\n\n')
                self.bixolon.write('\x1b\x6d')

        else:
            Popups.dialog_msg('Reprint Error', 'Please select an invoice')

        pass

    def print_selected_tags(self, *args, **kwargs):

        if self.selected_tags_list:
            customers = User()
            custs = SYNC.customers_grab(sessions.get('_customerId')['value'])
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
                    customers.role_id = user['role_id']

            invoice_id_str = str(sessions.get('_invoiceId')['value'])
            invs = SYNC.invoice_grab_id(sessions.get('_invoiceId')['value'])
            due_date = 'SUN'
            inv_items = []
            if invs:
                dt = datetime.datetime.strptime(invs['due_date'], "%Y-%m-%d %H:%M:%S")
                due_date = dt.strftime('%a').upper()
                inv_items = invs['invoice_items']
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
            if self.bixolon:
                self.bixolon.write('\x1b\x40')
                self.bixolon.write('\x1b\x6d')

                for item_id in self.selected_tags_list:
                    inv_items = SYNC.invoice_item_grab(item_id)
                    if inv_items:
                        iitem_id = inv_items['item_id']
                        tags_to_print = InventoryItem().tagsToPrint(iitem_id)
                        item_name = InventoryItem().getItemName(iitem_id)
                        item_color = inv_items['color']
                        invoice_item_id = inv_items['id']
                        laundry_tag = InventoryItem().getLaundry(iitem_id)
                        memo_string = inv_items['memo']
                        if laundry_tag:
                            laundry_to_print.append(invoice_item_id)
                        else:

                            for _ in range(tags_to_print):

                                self.bixolon.write('\x1b!\x30')  # QUAD SIZE
                                self.bixolon.write('{}{}\n'.format(text_left, text_right))
                                self.bixolon.write('\x1b!\x00')
                                self.bixolon.write(name_number_string)
                                self.bixolon.write('\n')
                                self.bixolon.write('{0:06d}'.format(int(invoice_item_id)))
                                self.bixolon.write(' {} {}'.format(item_name, item_color))
                                if memo_string:
                                    self.bixolon.write('\n{}'.format(memo_string))
                                    memo_len = '\n\n\n' if len(
                                        memo_string) <= 32 else '\n\n\n' + '\n' * int(
                                        (len(memo_string)) / 32)
                                    self.bixolon.write(memo_len)
                                    self.bixolon.write('\x1b\x6d')

                                else:

                                    self.bixolon.write('\n\n\n')
                                    self.bixolon.write('\x1b\x6d')
                if len(laundry_to_print) is 0:
                    # FINAL CUT
                    self.bixolon.write('\n\n\n\n\n\n')
                    self.bixolon.write('\x1b\x6d')
                else:

                    laundry_count = len(laundry_to_print)
                    shirt_mark = Custid().getCustomerMark(sessions.get('_customerId')['value'])
                    marks = SYNC.marks_query(sessions.get('_customerId')['value'], 1)
                    if marks is not False:
                        for mark in marks:
                            shirt_mark = mark['mark']
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

                        self.bixolon.write('\x1b!\x30')  # QUAD SIZE
                        self.bixolon.write(mark_mark_string)
                        self.bixolon.write('\n')
                        self.bixolon.write('\x1b!\x00')
                        self.bixolon.write(name_name_string)
                        self.bixolon.write('\n')
                        self.bixolon.write(id_id_string)

                        self.bixolon.write('\n\n\n\x1b\x6d')

                    # FINAL CUT
                    self.bixolon.write('\n\n\n\n\n\n')
                    self.bixolon.write('\x1b\x6d')
            else:
                Popups.dialog_msg('Reprint Error', 'Tag printer is not available')

        else:
            Popups.dialog_msg('Reprint Error', 'Please select an invoice item to print tag')

    def barcode_popup(self):
        # reset data
        self.barcode_save_data = {}

        # Pause Schedule

        if sessions.get('_invoiceId')['value'] is not None and int(sessions.get('_invoiceId')['value']) > 0:
            self.main_popup.title = "Setup Barcode to Items"
            layout = BoxLayout(orientation="vertical")

            self.barcode_layout = Factory.ScrollGrid(size_hint=(1, 0.8))
            self.barcode_layout.ids.main_table.cols = 2
            th1 = Factory.TagsGridHeaders(text="[color=#000000]Item[/color]")
            th2 = Factory.TagsGridHeaders(text="[color=#000000]Barcode[/color]")
            # create table headers
            self.barcode_layout.ids.main_table.add_widget(th1)
            self.barcode_layout.ids.main_table.add_widget(th2)
            # create tbody rows
            tags = InvoiceItem().get_tags(sessions.get('_invoiceId')['value'])
            if tags:
                idx = 0
                for tag in tags:
                    idx += 1
                    if tag['color'] is not None and tag['memo'] is not None:
                        color_description = "{} - {}".format(tag['color'], tag['memo'])
                    elif tag['color'] is not None and tag['memo'] is None:
                        color_description = "{}".format(tag['color'])
                    elif tag['color'] is None and tag['memo'] is not None:
                        color_description = "{}".format(tag['memo'])
                    else:
                        color_description = ""
                    item_description = "{} - {}".format(tag['id'], tag['item_name'])

                    td1 = Factory.ReadOnlyLabel(text="{} : {}".format(item_description, color_description))
                    self.barcode_layout.ids.main_table.add_widget(td1)
                    barcode_input = TextForm(multiline=False,
                                             write_tab=False,
                                             text='' if tag['barcode'] is '' else "{}".format(tag['barcode']))

                    barcode_input.bind(on_text_validate=partial(self.update_barcode, tag['id']))
                    if idx is 1:
                        barcode_input.focus = True
                    self.barcode_layout.ids.main_table.add_widget(barcode_input)
            inner_layout_3 = BoxLayout(orientation="horizontal",
                                       size_hint=(1, 0.1))
            cancel_button = Button(text="cancel",
                                   on_press=self.main_popup.dismiss)
            save_button = Button(text="save",
                                 on_press=self.save_barcodes)
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
        t1 = Thread(target=InvoiceItem().set_barcodes, args=[sessions.get('_invoiceId')['value'],
                    sessions.get('_companyId')['value'], self.barcode_save_data])
        t1.start()

        self.main_popup.dismiss()
        self.barcode_save_data = {}
        sessions.put('_searchResultsStatus', value=True)
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
                               on_press=popup.dismiss)
        print_button = Button(text="Print",
                              on_press=self.print_label)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(print_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def print_label(self, *args, **kwargs):
        if sessions.get('_customerId')['value']:
            count = int(self.label_input.text)
            row_mark = (count / 4)
            rows = math.ceil(row_mark) if row_mark > 0 else 0
            labels = []
            users = SYNC.customers_grab(sessions.get('_customerId')['value'])
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
           cust_id=sessions.get('_customerId')['value'],
           tag=str(self.tag_input.text))
                    else:

                        final_content = '''
{a}
{b}
{c}
'''.format(a=inititate,
           b=content,
           c=close)
                        self.zebra.write(final_content)
                        break

                final_content = '''
{a}
{b}
{c}
'''.format(a=inititate,
           b=content,
           c=close)
            self.zebra.write(final_content)
        else:
            Popups.dialog_msg('Label Error', 'Please select a customer before printing out a label')

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
                       on_press=partial(self.calc_button, '9'))
        btn_8 = Button(text="8",
                       on_press=partial(self.calc_button, '8'))
        btn_7 = Button(text="7",
                       on_press=partial(self.calc_button, '7'))
        btn_6 = Button(text="6",
                       on_press=partial(self.calc_button, '6'))
        btn_5 = Button(text="5",
                       on_press=partial(self.calc_button, '5'))
        btn_4 = Button(text="4",
                       on_press=partial(self.calc_button, '4'))
        btn_3 = Button(text="3",
                       on_press=partial(self.calc_button, '3'))
        btn_2 = Button(text="2",
                       on_press=partial(self.calc_button, '2'))
        btn_1 = Button(text="1",
                       on_press=partial(self.calc_button, '1'))
        btn_0 = Button(text="0",
                       on_press=partial(self.calc_button, '0'))
        btn_00 = Button(text="00",
                        on_press=partial(self.calc_button, '00'))
        btn_dot = Button(text=".",
                         on_press=partial(self.calc_button, '.'))
        btn_add = Button(text="+",
                         on_press=partial(self.calc_button, '+'))
        btn_subtract = Button(text="-",
                              on_press=partial(self.calc_button, '-'))
        btn_multiply = Button(text="*",
                              on_press=partial(self.calc_button, '*'))
        btn_divide = Button(text="/",
                            on_press=partial(self.calc_button, '/'))
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
                               on_press=popup.dismiss)
        clear_button = Button(markup=True,
                              text="[color=#FF0000]C[/color]",
                              on_press=self.calc_clear)
        equals_button = Button(markup=True,
                               text="[color=#e5e5e5][b]=[/b][/color]",
                               on_press=self.calc_equals)
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
        sessions.put('_profileId',value = None)
        sessions.put('_paymentId', value = None)
        pro = Profile()
        profiles = pro.where({'user_id': sessions.get('_customerId')['value'],
                              'company_id': sessions.get('_companyId')['value']})
        if profiles:
            for profile in profiles:
                sessions.put('_profileId', value = profile['profile_id'])
            try:
                cards_db = Card()
                self.cards = cards_db.collect(sessions.get('_companyId')['value'], sessions.get('_profileId')['value'])
            except:
                pass
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
        self.addresses = Address().where({'user_id': sessions.get('_customerId')['value']})
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
                                      on_press=self.get_pickup_dates,
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
                                       on_press=self.get_dropoff_dates,
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
                               on_press=self.delivery_popup.dismiss)
        add_card_button = Button(markup=True,
                                 text="Add Card",
                                 on_press=self.add_card_setup)
        add_address_button = Button(markup=True,
                                    text="Add Address",
                                    on_press=self.add_address_setup)
        setup_button = Button(markup=True,
                              text="Set Delivery",
                              on_press=self.set_delivery)
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
            company = SYNC.company_grab(company_id=sessions.get('_companyId')['value'])
            if company:
                store_hours = json.loads(company['store_hours']) if company['store_hours'] else None
                if store_hours:
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
                                        on_press=self.prev_dropoff_month)
                    next_month = Button(markup=True,
                                        text=">",
                                        font_size="30sp",
                                        on_press=self.next_dropoff_month)
                    select_month = Factory.SelectMonth()
                    self.month_button = Button(text='{}'.format(Static.month_by_number(self.month)),
                                               on_press=select_month.open)
                    for index in range(12):
                        month_options = Button(text='{}'.format(Static.month_by_number(index)),
                                               size_hint_y=None,
                                               height=40,
                                               on_press=partial(self.select_dropoff_calendar_month, index))
                        select_month.add_widget(month_options)

                    select_month.on_select = lambda instance, x: setattr(self.month_button, 'text', x)
                    select_year = Factory.SelectMonth()

                    self.year_button = Button(text="{}".format(self.year),
                                              on_press=select_year.open)
                    for index in range(10):
                        year_options = Button(text='{}'.format(int(self.year) + index),
                                              size_hint_y=None,
                                              height=40,
                                              on_press=partial(self.select_dropoff_calendar_year, index))
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
                                                     on_press=self.main_popup.dismiss))

                    layout.add_widget(inner_layout_1)
                    layout.add_widget(inner_layout_2)
                    self.main_popup.content = layout
                    self.main_popup.open()
                else:
                    Popups.dialog_msg('Delivery Error', 'You must first select an address before selecting a dropoff date.')
                pass

    def get_pickup_dates(self, *args, **kwargs):
        if self.address_id:
            company = SYNC.company_grab(company_id=sessions.get('_companyId')['value'])
            if company:
                store_hours = json.loads(company['store_hours']) if company['store_hours'] else None
                if store_hours:
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
                                        on_press=self.prev_pickup_month)
                    next_month = Button(markup=True,
                                        text=">",
                                        font_size="30sp",
                                        on_press=self.next_pickup_month)
                    select_month = Factory.SelectMonth()
                    self.month_button = Button(text='{}'.format(Static.month_by_number(self.month)),
                                               on_press=select_month.open)
                    for index in range(12):
                        month_options = Button(text='{}'.format(Static.month_by_number(index)),
                                               size_hint_y=None,
                                               height=40,
                                               on_press=partial(self.select_pickup_calendar_month, index))
                        select_month.add_widget(month_options)

                    select_month.on_select = lambda instance, x: setattr(self.month_button, 'text', x)
                    select_year = Factory.SelectMonth()

                    self.year_button = Button(text="{}".format(self.year),
                                              on_press=select_year.open)
                    for index in range(10):
                        year_options = Button(text='{}'.format(int(self.year) + index),
                                              size_hint_y=None,
                                              height=40,
                                              on_press=partial(self.select_pickup_calendar_year, index))
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
                                                     on_press=self.main_popup.dismiss))

                    layout.add_widget(inner_layout_1)
                    layout.add_widget(inner_layout_2)
                    self.main_popup.content = layout
                    self.main_popup.open()
                else:
                    Popups.dialog_msg('Delivery Error', 'You must first select an address before selecting a dropoff date')
                pass

    def set_delivery(self, *args, **kwargs):
        # validate
        if self.card_id is None:
            Popups.dialog_msg('Schedule Error', 'You have not selected a credit card on file')

        elif self.address_id is None:
            Popups.dialog_msg('Schedule Error', 'You must first select an address.')

        elif self.pickup_status is True and self.pickup_delivery_id is None:
            Popups.dialog_msg('Delivery Error', 'You must first select an address before selecting a dropoff date')

        elif self.dropoff_status is True and self.dropoff_delivery_id is None:
            Popups.dialog_msg('Schedule Error', 'Please select a proper dropoff date and time')

        elif self.dropoff_status is False and self.pickup_status is False:
            Popups.dialog_msg('Schedule Error', 'You must choose at least a dropoff or a pickup')

        else:
            # create a new schedule instance

            if self.pickup_delivery_id:
                status = 1
            elif not self.pickup_delivery_id and self.dropoff_delivery_id:
                status = 4

            data = {
                'company_id': sessions.get('_companyId')['value'],
                'customer_id': sessions.get('_customerId')['value'],
                'card_id': self.card_id,
                'pickup_delivery_id': self.pickup_delivery_id,
                'pickup_date': self.pickup_date,
                'pickup_address': self.address_id,
                'dropoff_delivery_id': self.dropoff_delivery_id,
                'dropoff_date': self.dropoff_date,
                'dropoff_address': self.address_id,
                'special_instructions': self.special_instructions,
                'type': 2,
                'status': status
            }
            save_schedule = SYNC.create_schedule(data)

            if save_schedule is not False:
                self.delivery_popup.dismiss()
                Popups.dialog_msg('Schedule Successfully Made', 'Delivery has been successfully scheduled')

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
                               on_press=self.main_popup.dismiss)
        add_button = Button(markup=True,
                            text="Add",
                            on_press=self.add_new_card)
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
                    cards.user_id = sessions.get('_customerId')['value']
                    # search for a profile
                    profiles = Profile().where({'company_id': company_id, 'user_id': sessions.get('_customerId')['value']})
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
                            data = {
                                'payment_id': payment_id,
                                'root_payment_id': self.root_payment_id,
                                'street': self.street_input.text,
                                'suite': self.suite_input.text,
                                'city': self.city_input.text,
                                'state': self.state_input.text,
                                'zipcode': self.zipcode_input.text,
                                'exp_month': self.exp_month_input.text,
                                'exp_year': self.exp_year_input.text,
                                'status': 1
                            }
                            cards_add = SYNC.create_card(data)
                            if cards_add is not False:
                                print('card added')
                        else:
                            Popups.dialog_msg('Card Error', result['message'])

                    else:
                        # make profile_id and payment_id
                        customers = User().where({'user_id': sessions.get('_customerId')['value']})
                        if customers:
                            for customer in customers:
                                first_name = customer['first_name']
                                last_name = customer['last_name']
                        new_data = {
                            'merchant_id': str(sessions.get('_customerId')['value']),
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
                            new_profiles.user_id = sessions.get('_customerId')['value']
                            new_profiles.profile_id = profile_id
                            new_profiles.status = 1
                            data = {
                                'company_id': company_id,
                                'user_id': sessions.get('_customerId')['value'],
                                'profile_id': profile_id,
                                'status': 1
                            }
                            create_profile = SYNC.create_profile(data)
                            if create_profile is not False:
                                print('profile_created')

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
                                data = {
                                    'payment_id': payment_id,
                                    'root_payment_id': self.root_payment_id,
                                    'street': self.street_input.text,
                                    'suite': self.suite_input.text,
                                    'city': self.city_input.text,
                                    'state': self.state_input.text,
                                    'zipcode': self.zipcode_input.text,
                                    'exp_month': self.exp_month_input.text,
                                    'exp_year': self.exp_year_input.text,
                                    'status': 1
                                }
                                cards_add = SYNC.create_card(data)
                                if cards_add is not False:
                                    print('card added')

                        else:
                            Popups.dialog_msg('Add Card Error', make_profile['message'])

            if save_success > 0:
                # finish and reset
                Popups.dialog_msg('Card Add Successful', 'Successfully added a card')

                self.main_popup.dismiss()

                profiles = SYNC.profiles_query(sessions.get('_companyrId')['value'], sessions.get('_customerId')['value'])
                if profiles:
                    for profile in profiles:
                        sessions.put('_profileId', value = profile['profile_id'])

                    cards_db = Card()
                    self.cards = cards_db.collect(sessions.get('_companyId')['value'], sessions.get('_profileId')['value'])
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
                Popups.dialog_msg('Card Add Unsuccessful', 'There were problems saving your card. Please try again')

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
                               on_press=self.main_popup.dismiss)
        add_button = Button(markup=True,
                            text="Add",
                            on_press=self.add_new_address)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(add_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.main_popup.content = layout
        self.main_popup.open()
        pass

    def add_new_address(self, *args, **kwargs):
        addresses = Address()
        addresses.company_id = sessions.get('_companyId')['value']
        addresses.user_id = sessions.get('_customerId')['value']
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
        data = {
            'company_id': sessions.get('_companyId')['value'],
            'user_id': sessions.get('_customerId')['value'],
            'name': self.name_input.text,
            'street': self.street_input.text,
            'suite': self.suite_input.text,
            'city': self.city_input.text,
            'state': self.state_input.text,
            'zipcode': self.zipcode_input.text,
            'primary_address': 0,
            'concierge_name': self.concierge_name_input.text,
            'concierge_number': self.concierge_number_input.text,
            'status': 1
        }
        create_address = SYNC.create_address(data)
        if create_address is not False:

            # update the form with a new address list
            self.addresses = Address().where({'user_id': sessions.get('_customerId')['value']})
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
            Popups.dialog_msg('Address Added', 'Successfully added a new address to delivery setup')

        pass

    def create_dropoff_calendar_table(self):
        # set the variables

        company = SYNC.company_grab(company_id=sessions.get('_companyId')['value'])
        if company:
            store_hours = json.loads(company['store_hours']) if company['store_hours'] else None
            if store_hours:
                # schedule dates
                addresses = Address().where({'address_id': self.address_id})
                addresses = SYNC.address_grab(self.address_id)
                zipcode = addresses['zipcode'] if addresses is not False else False
                delivery_ids = []
                if zipcode is not False:
                    zips = SYNC.zipcode_query(zipcode)
                    if zips:
                        for zip in zips:
                            delivery_ids.append(zip['delivery_id'])

                # day of the week
                dow = {}
                # blackout dates
                blackout_dates = []
                if delivery_ids:
                    for delivery_id in delivery_ids:

                        deliveries = SYNC.delivery_query(delivery_id)
                        if deliveries:

                            dow[deliveries['day']] = delivery_id
                            try:
                                blackouts = json.loads(deliveries['blackout']) if deliveries['blackout'] else False
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
                                                                          on_press=partial(self.select_dropoff_date,
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

        company = SYNC.company_grab(company_id=sessions.get('_companyId')['value'])
        if company:
            store_hours = json.loads(company['store_hours']) if company['store_hours'] else None
            if store_hours:
                # schedule dates
                addresses = Address().where({'address_id': self.address_id})
                addresses = SYNC.address_grab(self.address_id)
                zipcode = False
                if addresses:
                    zipcode = addresses['zipcode']
                delivery_ids = []
                if zipcode:

                    zips = SYNC.zipcode_query(zipcode)
                    if zips:
                        for zip in zips:
                            delivery_ids.append(zip['delivery_id'])
                # day of the week
                dow = {}
                # blackout dates
                blackout_dates = []
                if delivery_ids:
                    for delivery_id in delivery_ids:

                        deliveries = SYNC.delivery_grab(delivery_id)
                        if deliveries:
                            dow[deliveries['day']] = delivery_id
                            try:
                                blackouts = json.loads(deliveries['blackout']) if deliveries['blackout'] else False
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
                                                                          on_press=partial(self.select_pickup_date,
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
        deliveries = SYNC.delivery_grab(delivery_id)
        time_display = []
        self.pickup_time_group = {}
        if deliveries is not False:
            start_time = deliveries['start_time']
            end_time = deliveries['end_time']
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

        deliveries = SYNC.delivery_grab(delivery_id)
        time_display = []
        self.dropoff_time_group = {}
        if deliveries:
            start_time = deliveries['start_time']
            end_time = deliveries['end_time']
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
        self.month_button.text = '{}'.format(Static.month_by_number(self.month))
        self.year_button.text = '{}'.format(self.year)
        self.create_dropoff_calendar_table()

    def next_dropoff_month(self, *args, **kwargs):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.month_button.text = '{}'.format(Static.month_by_number(self.month))
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
        self.month_button.text = '{}'.format(Static.month_by_number(self.month))
        self.year_button.text = '{}'.format(self.year)
        self.create_pickup_calendar_table()

    def next_pickup_month(self, *args, **kwargs):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.month_button.text = '{}'.format(Static.month_by_number(self.month))
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
        schedules = SYNC.schedule_query(sessions.get('_customerId')['value'])
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
                    deliveries = SYNC.delivery_grab(dropoff_delivery_id)
                    if deliveries:
                        pickup_time_string = '{} - {}'.format(deliveries['start_time'], deliveries['end_time'])
                dropoff_time_string = ''
                if pickup_delivery_id:
                    deliveries = SYNC.delivery_grab(pickup_delivery_id)
                    if deliveries:
                        dropoff_time_string = '{} - {}'.format(deliveries['start_time'], deliveries['end_time'])
                address_string = ''
                concierge_name = ''
                concierge_number = ''
                if pickup_address_id:
                    addresses = SYNC.address_grab(pickup_address_id)
                    if addresses is not False:
                        address_name = addresses['name']
                        street = addresses['street']
                        address_string = '{}: {}'.format(address_name, street)
                        concierge_name = addresses['concierge_name']
                        concierge_number = Job.make_us_phone(addresses['concierge_number'])
                else:
                    addresses = SYNC.address_grab(dropoff_address_id)
                    if addresses is not False:
                        address_name = addresses['name']
                        street = addresses['street']
                        address_string = '{}: {}'.format(address_name, street)

                        concierge_name = addresses['concierge_name']
                        concierge_number = Job.make_us_phone(addresses['concierge_number'])

                status_formatted = Schedule().getStatus(status)

                pickup_date_label = Factory.TopLeftFormButton(text=pickup_date_formatted,
                                                              on_press=partial(self.view_delivery, schedule['id']))
                dropoff_date_label = Factory.TopLeftFormButton(text=dropoff_date_formatted,
                                                               on_press=partial(self.view_delivery, schedule['id']))
                pickup_time_label = Factory.TopLeftFormButton(text=pickup_time_string,
                                                              on_press=partial(self.view_delivery, schedule['id']))
                dropoff_time_label = Factory.TopLeftFormButton(text=dropoff_time_string,
                                                               on_press=partial(self.view_delivery, schedule['id']))
                # address_label = Factory.TopLeftFormButton(text=address_string)
                # special_instructions_label = Factory.TopLeftFormButton(text=special_instructions)
                # concierge_name_label = Factory.TopLeftFormButton(text=concierge_name)
                # concierge_number_label = Factory.TopLeftFormButton(text=concierge_number)
                status_label = Factory.TopLeftFormButton(text=status_formatted,
                                                         on_press=partial(self.view_delivery, schedule['id']))
                inner_layout_1.ids.main_table.add_widget(Button(text=str(schedule['schedule_id']),
                                                                on_press=partial(self.view_delivery, schedule['id'])))
                inner_layout_1.ids.main_table.add_widget(pickup_date_label)
                inner_layout_1.ids.main_table.add_widget(pickup_time_label)
                inner_layout_1.ids.main_table.add_widget(dropoff_date_label)
                inner_layout_1.ids.main_table.add_widget(dropoff_time_label)
                inner_layout_1.ids.main_table.add_widget(status_label)

        cancel_button = Button(text='cancel',
                               on_press=self.main_popup.dismiss)
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

        schedule = SYNC.schedule_grab(schedule_id)
        if schedule is not False:

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
                delivery = SYNC.delivery_grab(dropoff_delivery_id)
                if delivery is not False:
                    pickup_time_string = '{} - {}'.format(delivery['start_time'], delivery['end_time'])
            dropoff_time_string = ''
            if pickup_delivery_id:
                delivery = SYNC.delivery_grab(pickup_delivery_id)

                if delivery is not False:
                    dropoff_time_string = '{} - {}'.format(delivery['start_time'], delivery['end_time'])
            address_string = ''
            concierge_name = ''
            concierge_number = ''
            if pickup_address_id:

                address = SYNC.address_grab(pickup_address_id)
                if address is not False:
                    address_name = address['name']
                    street = address['street']
                    address_string = '{}: {}'.format(address_name, street)
                    concierge_name = address['concierge_name']
                    concierge_number = Job.make_us_phone(address['concierge_number'])

            elif not pickup_address_id and dropoff_address_id:
                address = SYNC.address_grab(dropoff_address_id)
                if address is not False:
                    address_name = address['name']
                    street = address['street']
                    address_string = '{}: {}'.format(address_name, street)

                    concierge_name = address['concierge_name']
                    concierge_number = Job.make_us_phone(address['concierge_number'])
            else:
                users = User().where({'user_id': sessions.get('_customerId')['value']})
                users = SYNC.customers_grab(sessions.get('_customerId')['value'])
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
                               on_press=popup.dismiss)
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
                               on_press=self.main_popup.dismiss)
        save_button = Button(text='Add Credit',
                             on_press=self.add_credit)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(save_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.main_popup.content = layout
        self.main_popup.open()

    def select_credit_reason(self, instance, value, *args, **kwargs):
        self.credit_reason = value

    def add_credit(self, *args, **kwargs):
        credits = Credit()
        credits.employee_id = str(auth_user.user_id)
        credits.customer_id = str(sessions.get('_customerId')['value'])
        credits.amount = str(self.credit_amount.text)
        credits.reason = self.credit_reason
        credits.status = str(1)
        data = {
            'employee_id': auth_user.user_id,
            'customer_id': sessions.get('_customerId')['value'],
            'amount': self.credit_amount.text,
            'reason': self.credit_reason,
            'status': 1
        }
        create_credits = SYNC.create_credit(data)
        if create_credits is not False:
            customers = User()
            # update user with new balance
            custs = SYNC.customers_grab(sessions.get('_customerId')['value'])
            old_credit = 0
            if custs:
                for customer in custs:
                    old_credit = float(customer['credits']) if customer['credits'] is not None else 0
            added_credits = float(self.credit_amount.text) if self.credit_amount.text else 0
            new_credits = old_credit + added_credits
            edit_credit = SYNC.edit_credit(sessions.get('_customerId')['value'], new_credits)

            if edit_credit is not False:
                sessions.put('_searchResultsStatus', value=True)
                sessions.put('_rowCap',value=0)
                sessions.put('_invoiceId',value=None)
                sessions.put('_rowSearch',value=(0,9))
                self.reset()
                # last 10 setup
                Static.update_last_10(sessions.get('_customerId')['value'],
                                      sessions.get('_last10')['value'])
                self.main_popup.dismiss()
                Popups.dialog_msg('Store Credit', 'Successfully added store credit')

            else:
                Popups.dialog_msg('Store Credit', 'Could not update store credit. Please try again.')
        pass

    def credit_history(self, *args, **kwargs):
        self.main_popup.title = 'Credit History'
        layout = BoxLayout(orientation="vertical")
        inner_layout_1 = Factory.ScrollGrid(size_hint=(1, 0.9))
        inner_layout_1.ids.main_table.cols = 6

        credits = SYNC.credit_query(sessions.get('_customerId')['value'])
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
        if credits is not False:
            for credit in credits:
                credit_id = credit['id']
                employee_id = credit['employee_id']
                customer_id = credit['customer_id']
                amount = '${:,.2f}'.format(Decimal(credit['amount']))
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
                               on_press=self.main_popup.dismiss)
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
                               on_press=self.main_popup.dismiss)
        payment_button = Button(text="payment options",
                                on_press=self.payment_options_popup)
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
        trans = SYNC.transaction_payment_query(sessions.get('_customerId')['value'])
        if trans is not False:
            for tran in trans:
                billing_period_format = datetime.datetime.strptime(tran['created_at'], "%Y-%m-%d %H:%M:%S")
                billing_period = billing_period_format.strftime("%b %Y")
                due_amount = str('$%.2f' % (float(tran['total'])))
                account_paid_format = tran['account_paid'] if tran['account_paid'] else False
                account_paid = str('$%.2f' % (float(account_paid_format))) if account_paid_format else 'Not Paid'
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

                if tran['id'] in self.selected_account_tr:
                    tr1 = Factory.TagsSelectedButton(text=str(tran['id']),
                                                     on_press=partial(self.select_account_tr, tran['id']))
                    tr2 = Factory.TagsSelectedButton(text=str(billing_period),
                                                     on_press=partial(self.select_account_tr, tran['id']))
                    tr3 = Factory.TagsSelectedButton(text=due_amount,
                                                     on_press=partial(self.select_account_tr, tran['id']))
                    tr4 = Factory.TagsSelectedButton(text=str(account_paid),
                                                     on_press=partial(self.select_account_tr, tran['id']))
                    tr5 = Factory.TagsSelectedButton(text=str(account_paid_on),
                                                     on_press=partial(self.select_account_tr, tran['id']))
                    tr6 = Factory.TagsSelectedButton(text=str(status),
                                                     on_press=partial(self.select_account_tr, tran['id']))
                else:
                    tr1 = Button(text=str(tran['id']),
                                 on_press=partial(self.select_account_tr, tran['id']))
                    tr2 = Button(text=str(billing_period),
                                 on_press=partial(self.select_account_tr, tran['id']))
                    tr3 = Button(text=due_amount,
                                 on_press=partial(self.select_account_tr, tran['id']))
                    tr4 = Button(text=str(account_paid),
                                 on_press=partial(self.select_account_tr, tran['id']))
                    tr5 = Button(text=str(account_paid_on),
                                 on_press=partial(self.select_account_tr, tran['id']))
                    tr6 = Button(text=str(status),
                                 on_press=partial(self.select_account_tr, tran['id']))
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
                transaction = SYNC.transaction_grab(transaction_id)
                if transaction is not False:
                    subtotal += float(transaction['pretax'])
                    tax += float(transaction['tax'])
                    aftertax += float(transaction['aftertax'])
                    credits += float(transaction['credit'])
                    discounts += float(transaction['discount'])
                    due += float(transaction['total'])

        # compare with customer data account running balance total check to see if customer overpaid from last trans
        customers = SYNC.customers_grab(sessions.get('_customerId')['value'])
        account_running_balance = 0
        if customers:
            for customer in customers:
                account_running_balance = float(customer['account_total']) if float(
                    customer['account_total']) > 0 else 0

        if float(account_running_balance) < float(due):
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
                               on_press=self.payment_popup.dismiss)
        pay_button = Button(text="Finish",
                            on_press=self.finish_account_payment)
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
            Popups.dialog_msg('Form Error', 'Please select an account invoice and try again.')

        # save data
        if errors is 0:
            edit_transaction = SYNC.pay_account(self.selected_account_tr, self.tendered_input.text, sessions.get('_customerId')['value'])
            if edit_transaction is not False:
                Popups.dialog_msg('Account Transaction Paid!', 'Successfully paid account transaction.')

                self.payment_popup.dismiss()
                self.main_popup.dismiss()
                sessions.put('_searchResultsStatus',value=True)
                self.reset()
            else:
                Popups.dialog_msg('Could not save user data', 'User table error, could not save. Please contact administrator')

                self.payment_popup.dismiss()
                self.main_popup.dismiss()
                sessions.put('_searchResultsStatus', value=True)
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
        # transactions = Transaction()
        trans = SYNC.transaction_query(sessions.get('_customerId')['value'])
        if trans is not False:
            for tran in trans:
                billing_period_format = datetime.datetime.strptime(tran['created_at'], "%Y-%m-%d %H:%M:%S")
                billing_period = billing_period_format.strftime("%b %Y")
                due_amount = str('$%.2f' % (Decimal(tran['total'])))
                account_paid_format = tran['account_paid'] if tran['account_paid'] else False
                account_paid = str('$%.2f' % (Decimal(account_paid_format))) if account_paid_format else 'Not Paid'
                if tran['status'] is '1':
                    status = 'Paid'

                elif tran['status'] is '2':
                    status = 'Bill Sent'
                else:
                    status = 'Current'

                if tran['account_paid_on']:
                    account_paid_on_format = datetime.datetime.strptime(tran['account_paid_on'], "%Y-%m-%d %H:%M:%S")
                    account_paid_on = account_paid_on_format.strftime("%m/%d/%y %I:%M %p")
                else:
                    account_paid_on = 'Not Paid'

                if tran['id'] in self.selected_account_tr:
                    tr1 = Factory.TagsSelectedButton(text=str(tran['id']),
                                                     on_press=partial(self.show_invoice_details, tran['id']))
                    tr2 = Factory.TagsSelectedButton(text=str(billing_period),
                                                     on_press=partial(self.show_invoice_details, tran['id']))
                    tr3 = Factory.TagsSelectedButton(text=due_amount,
                                                     on_press=partial(self.show_invoice_details, tran['id']))
                    tr4 = Factory.TagsSelectedButton(text=str(account_paid),
                                                     on_press=partial(self.show_invoice_details, tran['id']))
                    tr5 = Factory.TagsSelectedButton(text=str(account_paid_on),
                                                     on_press=partial(self.show_invoice_details, tran['id']))
                    tr6 = Factory.TagsSelectedButton(text=str(status),
                                                     on_press=partial(self.show_invoice_details, tran['id']))
                else:
                    tr1 = Button(text=str(tran['id']),
                                 on_press=partial(self.show_invoice_details, tran['id']))
                    tr2 = Button(text=str(billing_period),
                                 on_press=partial(self.show_invoice_details, tran['id']))
                    tr3 = Button(text=due_amount,
                                 on_press=partial(self.show_invoice_details, tran['id']))
                    tr4 = Button(text=str(account_paid),
                                 on_press=partial(self.show_invoice_details, tran['id']))
                    tr5 = Button(text=str(account_paid_on),
                                 on_press=partial(self.show_invoice_details, tran['id']))
                    tr6 = Button(text=str(status),
                                 on_press=partial(self.show_invoice_details, tran['id']))
                inner_layout_1.ids.main_table.add_widget(tr1)
                inner_layout_1.ids.main_table.add_widget(tr2)
                inner_layout_1.ids.main_table.add_widget(tr3)
                inner_layout_1.ids.main_table.add_widget(tr4)
                inner_layout_1.ids.main_table.add_widget(tr5)
                inner_layout_1.ids.main_table.add_widget(tr6)

        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="cancel",
                               on_press=self.main_popup.dismiss)
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

        invoices = SYNC.invoice_query_transaction_id(transaction_id)
        if invoices:
            for invoice in invoices:
                drop_date_format = datetime.datetime.strptime(invoice['created_at'], "%Y-%m-%d %H:%M:%S")
                due_date_format = datetime.datetime.strptime(invoice['due_date'], "%Y-%m-%d %H:%M:%S")
                drop_date = drop_date_format.strftime('%m/%d/%y')
                due_date = due_date_format.strftime('%m/%d/%y')
                td1 = Button(text=str(invoice['id']),
                             on_press=partial(self.account_view_items, invoice['id']))
                td2 = Factory.TopLeftFormButton(text=str(drop_date),
                                                on_press=partial(self.account_view_items, invoice['id']))
                td3 = Factory.TopLeftFormButton(text=str(due_date),
                                                on_press=partial(self.account_view_items, invoice['id']))
                td4 = Button(text=str(invoice['quantity']),
                             on_press=partial(self.account_view_items, invoice['id']))
                td5 = Button(text=str('$%.2f' % Decimal(invoice['pretax'])),
                             on_press=partial(self.account_view_items, invoice['id']))
                td6 = Button(text=str('$%.2f' % Decimal(invoice['tax'])),
                             on_press=partial(self.account_view_items, invoice['id']))
                td7 = Button(text=str('$%.2f' % Decimal(invoice['total'])),
                             on_press=partial(self.account_view_items, invoice['id']))
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
                               on_press=popup.dismiss)
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

        invoice_items = []
        invoices = SYNC.invoice_grab_id(invoice_id)
        if invoices is not False:
            invoice_items = invoices['invoice_items']
        if invoice_items:
            for ii in invoice_items:
                item_id = ii['item_id']
                inventory_items = SYNC.inventory_items_grab(item_id)
                item_name = None
                if inventory_items is not False:
                    item_name = inventory_items['name']
                td1 = Button(text=str(ii['invoice_id']))
                td2 = Button(text=str(item_name))
                td3 = Button(text=str(ii['color']))
                td4 = Factory.TopLeftFormButton(text=str(ii['memo']))
                td5 = Button(text=str(ii['quantity']))
                td6 = Button(text=str('$%.2f' % Decimal(ii['pretax'])))

                inner_layout_1.ids.main_table.add_widget(td1)
                inner_layout_1.ids.main_table.add_widget(td2)
                inner_layout_1.ids.main_table.add_widget(td3)
                inner_layout_1.ids.main_table.add_widget(td4)
                inner_layout_1.ids.main_table.add_widget(td5)
                inner_layout_1.ids.main_table.add_widget(td6)

        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="cancel",
                               on_press=popup.dismiss)
        inner_layout_2.add_widget(cancel_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

class TextForm(TextInput):
    def __init__(self, **kwargs):
        super(TextForm, self).__init__(**kwargs)
        self.bind(on_text_validate=self.next_on_validate)

    @staticmethod
    def next_on_validate(instance):
        """Change the focus when Enter is pressed.
        """
        next = instance._get_focus_next('focus_next')
        if next:
            instance.focus = False
            next.focus = True