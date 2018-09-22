import json
import re

from kivy.properties import ObjectProperty, partial
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.screenmanager import Screen
from classes.popups import *
from models.companies import Company
from models.sessions import sessions
from models.sync import Sync
from models.static import Static
SYNC = Sync()

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
        # 

        companies = SYNC.company_grab(sessions.get('_companyId')['value'])
        if companies:
            self.company_name.text = companies['name'] if companies['name'] else ''
            self.company_phone.text = companies['phone'] if companies['phone'] else ''
            self.company_email.text = companies['email'] if companies['email'] else ''
            self.company_street.text = companies['street'] if companies['street'] else ''
            self.company_city.text = companies['city'] if companies['city'] else ''
            self.company_state.text = companies['state'] if companies['state'] else ''
            self.company_zipcode.text = companies['zip'] if companies['zip'] else ''
            self.company_payment_gateway_id.text = companies['payment_gateway_id'] if companies[
                'payment_gateway_id'] else ''
            self.company_payment_api_login.text = companies['payment_api_login'] if companies[
                'payment_api_login'] else ''
            self.store_hours = json.loads(companies['store_hours'])

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
                    dow = Static.dow_schedule(idx)
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
        put = companies.put(where={'company_id': sessions.get('_companyId')['value']},
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
            Popups.modal_msg('Company Update', 'Successfully updated company!')