import datetime
import queue
import threading
import time

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from classes.popups import Popups
from models.custids import Custid
from models.jobs import Job
from models.kv_generator import KvString
# Helpers
from models.sync import Sync
from models.users import User
from models.static import Static
from models.sessions import sessions

auth_user = User()

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
Job = Job()


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
        print(sessions.get("_companyId")["value"])
        # Pause Schedule
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
        if sessions.get('_customerId')['value']:

            customers = User()
            customers.user_id = sessions.get('_customerId')['value']
            customer = SYNC.customers_grab(sessions.get('_customerId')['value'])
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

                    if cust['account'] is True or cust['account'] is '1' or cust['account'] is 1:
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
                            on_press=self.popup.dismiss)
            delete_btn = Button(markup=True,
                                text="[color=FF0000]Delete[/color]",
                                on_press=self.delete_final)
            inner_layout_2.add_widget(cancel)
            inner_layout_2.add_widget(delete_btn)
            content.add_widget(inner_layout_1)
            content.add_widget(inner_layout_2)
            self.popup.content = content
            self.popup.open()

        pass

    def delete_final(self, *args, **kwargs):
        delete_status = SYNC.customer_delete(sessions.get('_customerId')['value'])
        if delete_status:
            self.parent.current = 'search'
            self.popup.dismiss()
            popup = Popup()
            popup.content = Builder.load_string(KV.popup_alert("Sucessfully deleted customer from system"))
            popup.open()
            # last 10 setup
            Static.update_last_10(sessions.get('_customerId')['value'], sessions.get('_last10')['value'])

    def set_result_status(self):
        sessions.put('_searchResultsStatus', value=True)

    def create_mark(self):
        popup = Popup()
        popup.size = 900, 600
        # check for previous marks set
        check_mark = SYNC.check_mark(self.mark_text.text)
        marks = Custid()

        if check_mark is 1:

            popup.title = 'Customer Mark Error'

            popup.content = Builder.load_string(
                KV.popup_alert('{} has already been taken. Please select another.'.format(self.mark_text.text)
                               )
            )
            popup.open()
        else:

            # save the mark
            save_mark = SYNC.create_mark(self.mark_text.text, sessions.get('_companyId')['value'], sessions.get('_customerId')['value'])
            if save_mark is True:
                # update the marks table
                self.mark_text.text = ''
                self.update_marks_table()
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
        # custids = marks.where({'mark': '"{}"'.format(mark)})
        delete_mark = SYNC.delete_mark(mark)
        if delete_mark:
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

        users = SYNC.customers_grab(sessions.get('_customerId')['value'])
        custids = []
        if len(users) > 0:
            for user in users:
                custids = user['custids']

        even_odd = 0
        if len(custids) > 0:
            for custid in custids:
                status = 'Active' if custid['status'] == 1 else 'Not Active'
                even_odd += 1
                rgba = '0.369,0.369,0.369,1' if even_odd % 2 == 0 else '0.826, 0.826, 0.826, 1'
                background_rgba = '0.369,0.369,0.369,0.1' if even_odd % 2 == 0 else '0.826, 0.826, 0.826, 0.1'
                text_color = 'e5e5e5' if even_odd % 2 == 0 else '000000'
                tr1 = KV.widget_item(type='Label', data=even_odd, rgba=rgba,
                                     background_rgba=background_rgba, text_color=text_color)
                tr2 = KV.widget_item(type='Label', data=sessions.get('_customerId')['value'], rgba=rgba,
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

            check_duplicate = SYNC.customers_grab(sessions.get('_customerId')['value'])
            if len(check_duplicate) > 0:
                for cd in check_duplicate:
                    check_phone = cd['phone']
                    if cd['user_id'] != sessions.get('_customerId')['value'] and check_phone is phone:
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
            data = {
                'company_id': sessions.get('_companyId')['value'],
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

            if SYNC.customer_edit(sessions.get('_customerId')['value'], data):
                self.reset()
                self.customer_select(sessions.get('_customerId')['value'])
                # create popup
                Popups.modal_msg('Customer Update', 'You have successfully edited this customer.')

        else:
            Popups.dialog_msg('Edit Error',
                              "{} Errors in your form. Please check to see if account or delivery is improperly set.".format(errors))

    def customer_select(self, customer_id, *args, **kwargs):
        sessions.put('_searchResultsStatus', value= True)
        sessions.put('_rowCap',value=0)
        sessions.put('_customerId',value=customer_id)
        sessions.put('_invoiceid',value=None)
        sessions.put('_rowSearch',value=(0,9))
        self.parent.current = 'search'
        # last 10 setup
        Static.update_last_10(sessions.get('_customerId')['value'],sessions.get('_last10')['value'])