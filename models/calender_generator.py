import time
import datetime
import os

os.environ['TZ'] = 'US/Pacific'
time.tzset()

# Models
from models.users import User

# Helpers
import calendar
from calendar import Calendar
from models.kv_generator import KvString
from models.jobs import Job
from models.static import Static

from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, partial
from kivy.uix.popup import Popup

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


class CalendarGenerator:
    now = datetime.datetime.now()
    month = now.month
    year = now.year
    day = now.day
    calendar_layout = ObjectProperty(None)
    month_button = ObjectProperty(None)
    year_button = ObjectProperty(None)

    def make_calendar(self):
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
            month_options.on_press = select_month.select(self.month_button.text)
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
            year_options.on_press = select_year.select(self.year_button.text)

        select_month.bind(on_select=lambda instance, x: setattr(self.month_button, 'text', x))
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
                            item = Factory.CalendarButton(text="[b]{}[/b]".format(day[0]))
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
        self.make_calendar()

    def select_calendar_year(self, year, *args, **kwargs):
        self.year = year
        self.create_calendar_table()
