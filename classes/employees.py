from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ObjectProperty, partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from classes.popups import Popups
from models.kv_generator import KvString
from models.sync import Sync
# from main import   DEFAULT_COLOR
from models.users import User
from models.sessions import sessions

ERROR_COLOR = 0.94, 0.33, 0.33, 1
DEFAULT_COLOR = 0.5, 0.5, 0.5, 1.0
SYNC = Sync()
KV = KvString()


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
        # 
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
        employees = users.where({'company_id': sessions.get('_companyId')['value'],
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
                                         on_press=self.employee_popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=00ff00][b]add[/b][/color]',
                                         on_press=self.add_employee))
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
                                         on_press=self.employee_popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=00ff00][b]edit[/b][/color]',
                                         on_press=self.edit_employee))
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
            users.company_id = sessions.get('_companyId')['value']
            users.username = self.username.text
            users.first_name = self.first_name.text
            users.last_name = self.last_name.text
            users.phone = self.phone.text
            users.email = self.email.text
            users.password = self.password.text
            users.role_id = 3  # employees

            if users.add():
                Popups.modal_msg('Add Employee', 'Successfully Added employee!')
        else:
            Popups.modal_msg('Add Employee', '{} errors. Please fix then continue.'.format(errors))

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
                Popups.modal_msg('Edit Employee', 'Successfully edited employee!')

        else:
            Popups.modal_msg('Edit Employee', '{} errors. Please fix then continue.'.format(errors))

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
                                         on_press=popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=00ff00][b]Delete[/b][/color]',
                                         on_press=self.delete_employee))
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
        Popups.modal_msg('Employee Deleted', '{} employee(s) deleted.'.format(count))

        self.reset()
