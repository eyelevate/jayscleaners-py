import json
import sys
import platform
import time
import datetime
import os
from collections import OrderedDict

os.environ['TZ'] = 'US/Pacific'
time.tzset()

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
from sync import Sync
from taxes import Tax
from transactions import Transaction
from users import User

# Helpers
import calendar
from calendar import Calendar
from kv_generator import KvString
from jobs import Job
from static import Static
import threading
import queue

# from escpos import *
# from escpos.printer import Network

from kivy.app import App
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, partial
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import FadeTransition
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.uix.tabbedpanel import TabbedPanelContent
from kivy.graphics.instructions import Canvas
from kivy.graphics import Rectangle, Color
from kivy.uix.widget import WidgetException

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
SYNC = Sync()
queueLock = threading.Lock()
workQueue = queue.Queue(10)
list_len = []


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
        self.username = TextInput(id='username',
                                  write_tab=False,
                                  font_size='20sp',
                                  hint_text='Username',
                                  on_text_validate=self.login,
                                  multiline=False,
                                  padding=[5, 5, 5, 5],
                                  text='')
        inner_content_1.add_widget(self.username)

        inner_content_1.add_widget(Label(text="password",
                                         size_hint_y=None,
                                         font_size='20sp'))
        self.password = TextInput(id='password',
                                  write_tab=False,
                                  font_size='20sp',
                                  hint_text='Password',
                                  password=True,
                                  on_text_validate=self.login,
                                  multiline=False,
                                  padding=[5, 5, 5, 5],
                                  text='')
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
                self.settings_button.disabled = False
                self.settings_button.disabled = False
                for user1 in u1:
                    auth_user.id = user1['id']
                    auth_user.user_id = user1['user_id']
                    auth_user.username = user1['username']
                    auth_user.company_id = user1['company_id']
                    SYNC.company_id = user1['company_id']

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
                    self.settings_button.disabled = False
                    self.settings_button.disabled = False

                    auth_user.username = user.username
                    auth_user.company_id = data['company_id']
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
        self.settings_button.disabled = True
        self.settings_button.disabled = True

    def db_sync(self, *args, **kwargs):

        # self.update_label.text = 'Connecting to server...
        # sync.migrate()
        # SYNC.db_sync()

        # test multithreading here
        vars.WORKLIST.append("Sync")
        threads_start()

        # sync.get_chunk(table='invoice_items',start=140001,end=150000)

        # self.update_label.text = 'Server updated at {}'.format()

    def test_time(self):
        invoices_2 = Invoice().where({'id': 43693}, deleted_at=False)
        if invoices_2:
            idx = -1
            for invoice in invoices_2:
                idx += 1
                invoices_2[idx]['due_date'] = int(datetime.datetime.strptime(invoice['due_date'],
                                                                             "%Y-%m-%d %H:%M:%S").timestamp())
                invoices_2[idx]['rack_date'] = int(datetime.datetime.strptime(invoice['rack_date'],
                                                                              "%Y-%m-%d %H:%M:%S").timestamp()) if \
                    invoice[
                        'rack_date'] else None

                print(invoices_2[idx]['due_date'])
                print(invoices_2[idx]['rack_date'])

    now = datetime.datetime.now()
    month = now.month
    year = now.year
    day = now.day
    calendar_layout = ObjectProperty(None)
    month_button = ObjectProperty(None)
    year_button = ObjectProperty(None)
    due_date = None  # tbr

    def make_calendar(self):

        # tbr
        company = Company()
        company_data = company.where({'company_id': 1})
        if company_data:
            for comp in company_data:
                store_hours = json.loads(comp['store_hours'])
        else:
            store_hours = False

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
        self.month = int(self.due_date.strftime('%m'))

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
                                         text="cancel",
                                         on_release=popup.dismiss))

        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def create_calendar_table(self):
        # set the variables

        store_hours = Company().get_store_hours(1)
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
                                elif check_date > check_today and check_date < check_due_date:
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
        self.due_date = selected_date
        self.create_calendar_table()

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
        taxes = Tax().where({'company_id': auth_user.company_id, 'status': 1})
        if taxes:
            for tax in taxes:
                vars.TAX_RATE = tax['rate']
        else:
            vars.TAX_RATE = 0.096

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
                item_name = item['name']
                item_tags = item['tags'] if item['tags'] else 1
                item_quantity = item['quantity'] if item['quantity'] else 1
                inventories = Inventory().where({'inventory_id': '{}'.format(str(inventory_id))})
                if inventories:
                    for inventory in inventories:
                        inventory_init = inventory['name'][:1].capitalize()
                else:
                    inventory_init = ''
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
                        save_invoice_items[last_insert_id] = invoice_group
                        idx = -1
                        for inv_items in save_invoice_items[last_insert_id]:
                            idx += 1
                            save_invoice_items[last_insert_id][idx]['status'] = 3
                            save_invoice_items[last_insert_id][idx]['invoice_id'] = last_insert_id
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
                            for items in save_invoice_items[id]:
                                idx += 1
                                save_invoice_items[id][idx]['invoice_id'] = new_invoice_id
                                save_invoice_items[id][idx]['status'] = 1
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
                        else:
                            inventory_init = ''

                        if item_id in self.invoice_list:
                            self.invoice_list[item_id].append({
                                'invoice_items_id': invoice_items_id,
                                'type': inventory_init,
                                'inventory_id': inventory_id,
                                'item_id': item_id,
                                'item_name': item['name'],
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
                                'item_name': item['name'],
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
                                'item_name': item['name'],
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
                                'item_name': item['name'],
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
                item_name = item['name']
                item_tags = item['tags'] if item['tags'] else 1
                item_quantity = item['quantity'] if item['quantity'] else 1
                inventories = Inventory().where({'inventory_id': '{}'.format(str(inventory_id))})
                if inventories:
                    for inventory in inventories:
                        inventory_init = inventory['name'][:1].capitalize()
                else:
                    inventory_init = ''
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

        if self.deleted_rows:
            for invoice_items_id in self.deleted_rows:
                invoice_items = InvoiceItem()
                invoice_items.id = invoice_items.get_id(invoice_items_id)
                if invoice_items.delete():
                    print('deleted row {}'.format(invoice_items.id))

        if self.invoice_list:
            invoice_items = InvoiceItem()
            for invoice_item_key, invoice_item_value in self.invoice_list.items():
                for iivalue in invoice_item_value:
                    qty = iivalue['qty']
                    pretax = float(iivalue['item_price']) if iivalue['item_price'] else 0
                    tax = float('%.2f' % (pretax * vars.TAX_RATE))
                    total = float('%.2f' % (pretax * (1 + vars.TAX_RATE)))

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
                      data={'quantity': self.quantity,
                            'pretax': '%.2f' % self.subtotal,
                            'tax': '%.2f' % self.tax,
                            'total': '%.2f' % self.total,
                            'due_date': '{}'.format(self.due_date.strftime("%Y-%m-%d %H:%M:%S"))})

        vars.WORKLIST.append("Sync")
        threads_start()

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
    item_image = ObjectProperty(None)
    items_table = ObjectProperty(None)
    invs_results_label = ObjectProperty(None)
    history_popup = ObjectProperty(None)
    status_spinner = ObjectProperty(None)

    def get_history(self):
        # check if an invoice was previously selected
        self.invoices_table.clear_widgets()
        self.items_table.clear_widgets()

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
        if deleted_at:  # deleted
            state = 4
        elif transaction_id:  # picked up and done
            state = 5
        elif rack and not transaction_id:  # racked and ready
            state = 3
        elif due_strtotime < now_strtotime:  # overdue
            state = 2
        else:  # Not ready yet
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
        print(invoice_deleted)
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
                else:
                    item_name = ''

                items[item_id] = {
                    'id': invoice_item['id'],
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
                    # print(item_string)
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
                                          values=('Not Ready', 'Racked', 'Picked Up'),
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
        if self.status_spinner.text == 'Not Ready':
            status = 1
        elif self.status_spinner.text == 'Racked':
            status = 3
        elif self.status_spinner.text == 'Picked Up':
            status = 5
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
                        transaction_id = invoice['transaction_id']
                        status = 5 if transaction_id else status
                        inv.id = invoice['id']
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

            self.edit_invoice_btn.disabled = False if vars.INVOICE_ID is not None else True
            data = {'user_id': vars.CUSTOMER_ID}
            customers = User()
            results = customers.where(data)
            self.customer_results(results)
        else:
            vars.CUSTOMER_ID = None
            vars.INVOICE_ID None
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
        total = vars.us_dollar(row['total'])
        due = row['due_date']
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

        selected = True if invoice_id == check_invoice_id else False

        tr_1 = KV.invoice_tr(state, invoice_id, selected=selected, invoice_id=invoice_id,
                             callback='self.parent.parent.parent.parent.parent.invoice_selected({})'.format(invoice_id))
        tr_2 = KV.invoice_tr(state, company_id, selected=selected, invoice_id=invoice_id,
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
        # sync db
        vars.WORKLIST.append("Sync")
        threads_start()


class SettingsScreen(Screen):
    pass


class ScreenManagement(ScreenManager):
    pass


# load kv files
presentation = Builder.load_file("./kv/main.kv")


class MainApp(App):
    def build(self):
        self.title = 'Jays POS'
        return presentation


if __name__ == "__main__":
    MainApp().run()
