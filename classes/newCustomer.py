from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.spinner import Spinner
from models.users import User
from models.sync import Sync
from models.jobs import Job
from models.kv_generator import KvString
from models.sessions import sessions
from models.static import Static
auth_user = User()
Job = Job()
ERROR_COLOR = 0.94, 0.33, 0.33, 1
DEFAULT_COLOR = 0.5, 0.5, 0.5, 1.0
KV = KvString()
SYNC = Sync()

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
        #
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
            users = SYNC.customers_grab(phone)
            check_customers = True if len(users) > 0 else False

            if check_customers:
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
            concierge_name = ''
            concierge_number = ''
            special_instructions = ''
            suite = ''
            street = ''
            city = ''
            zipcode = ''
            if self.is_delivery.active:
                concierge_name = self.concierge_name.text
                concierge_number = Job.make_numeric(data=self.concierge_number.text)
                special_instructions = self.special_instructions.text if self.special_instructions.text else None
            if self.is_account.active:
                street = Job.make_no_whitespace(data=self.street.text)
                suite = Job.make_no_whitespace(data=self.suite.text)
                city = Job.make_no_whitespace(data=self.city.text)
                zipcode = Job.make_no_whitespace(data=self.zipcode.text)

            data = {
                'company_id': sessions.get('_companyId')['value'],
                'phone': Job.make_numeric(data=self.phone.text),
                'last_name': Job.make_no_whitespace(data=self.last_name.text),
                'first_name': Job.make_no_whitespace(data=self.first_name.text),
                'email': self.email.text if Job.check_valid_email(email=self.email.text) else None,
                'invoice_memo': self.invoice_memo.text if self.invoice_memo.text else None,
                'important_memo': self.important_memo.text if self.important_memo.text else None,
                'shirt': str('1' if self.shirts_finish.text is "Hanger" else '2'),
                'starch': shirts_preference,
                'street': self.street.text,
                'suite': suite,
                'city': city,
                'zipcode': zipcode,
                'concierge_name': concierge_name,
                'concierge_number': concierge_number,
                'special_instructions': special_instructions,
                'account': 1 if self.is_account.active else '',
                'role_id': 5
            }

            new_customer = SYNC.customer_add(data)
            if new_customer is not False:
                sessions.put('_customerId',value=new_customer['id'])
                self.reset()
                self.customer_select(sessions.get('_customerId')['value'])
                # create popup
                content = KV.popup_alert("You have successfully edited this customer.")
                popup.content = Builder.load_string(content)
                popup.open()

    def customer_select(self, customer_id, *args, **kwargs):
        sessions.put('_searchResultsStatus', value=True)
        sessions.put('_rowCap', value=0)
        sessions.put('_customerId', value=customer_id)
        sessions.put('_invoiceId', value=None)
        sessions.put('_rowSearch', value=(0,9))

        self.parent.current = 'search'
        # last 10 setup
        Static.update_last_10(sessions.get('_customerId')['value'], sessions.get('_last10')['value'])