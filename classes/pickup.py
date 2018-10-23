import datetime
import time
from _pydecimal import Decimal
from threading import Thread

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
from pubsub import pub

from models.cards import Card
from classes.popups import Popups
from models.companies import Company
from models.inventories import Inventory
from models.invoice_items import InvoiceItem
from models.invoices import Invoice
from models.printers import Printer
from models.profiles import Profile
from models.transactions import Transaction
from models.users import User
from models.sync import Sync
from models.jobs import Job
from models.kv_generator import KvString
from models.static import Static
from models.sessions import sessions
Job = Job()
ERROR_COLOR = 0.94, 0.33, 0.33, 1
DEFAULT_COLOR = 0.5, 0.5, 0.5, 1.0
KV = KvString()
SYNC = Sync()
SYNC_POPUP = Popup()
unix = time.time()
NOW = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))


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
    epson = None
    pickup_table_rv = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PickupScreen, self).__init__(**kwargs)
        pub.subscribe(self.set_epson_printer, "set_epson_printer")

    def attach(self):
        pub.subscribe(self.invoice_selected, "invoice_selected")


    def detach(self):
        pub.unsubscribe(self.invoice_selected, "invoice_selected")


    def set_epson_printer(self, device):
        self.epson = device
        print(self.epson)

    def reset(self):
        # Pause Schedule

        # get credit total
        self.credits = 0
        self.credits_spent = 0
        account_status = False

        customers = SYNC.customers_grab(sessions.get('_customerId')['value'])
        if customers:
            for customer in customers:
                self.credits = customer['credits'] if customer['credits'] is not None else 0
                account_status = True if customer['account'] is '1' or customer['account'] is True or customer[
                    'account'] is 1 else False
        print(account_status)
        if account_status is not False:
            print('in here')
            self.payment_panel.switch_to(header=self.payment_account_header)
            self.payment_type = 'ac'
        else:
            self.payment_panel.switch_to(header=self.credit_card_header)
            self.payment_type = 'cc'

        self.total_credit.text = '[color=0AAC00]{}[/color]'.format('${:,.2f}'.format(Decimal(self.credits)))
        self.selected_invoices = []

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
        sessions.put('_profileId', value= None)
        sessions.put('_paymentId', value= None)
        pro = Profile()
        profiles = SYNC.profiles_query(sessions.get('_customerId')['value'], sessions.get('_companyId')['value'])
        if profiles:
            for profile in profiles:
                sessions.put('_profileId', value=profile['profile_id'])

            cards_db = Card()
            self.cards = cards_db.collect(sessions.get('_companyId')['value'], sessions.get('_profileId')['value'])
        else:
            self.cards = False
        self.select_card_location('1')

        self.discount_label.bind(on_ref_press=self.discount_popup)


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

        discounts = SYNC.discount_grab_by_company(sessions.get('_companyId')['value'])
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
                inventory_items = []
                if inventory_id:
                    inventories = SYNC.inventory_grab(inventory_id)
                    if inventories is not False:
                        inventory_name = inventories['name']
                        inventory_items = inventories['inventory_items']
                item_name = None
                inventory_item_id = discount['inventory_item_id']
                if inventory_item_id:
                    if len(inventory_items) > 0:
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
                                       on_press=partial(self.select_discount, discount_id))

                    name_button = Button(text=str(discount['name']),
                                         on_press=partial(self.select_discount, discount_id))
                    type_button = Button(text=str(type),
                                         on_press=partial(self.select_discount, discount_id))
                    discount_button = Button(text=str(discount_display),
                                             on_press=partial(self.select_discount, discount_id))
                    group_button = Button(text=str(group),
                                          on_press=partial(self.select_discount, discount_id))
                    start_button = Button(text=str(start_formatted),
                                          on_press=partial(self.select_discount, discount_id))
                    end_button = Button(text=str(end_formatted),
                                        on_press=partial(self.select_discount, discount_id))

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
                               on_press=self.main_popup.dismiss)

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
        table_data = []
        invoices = Invoice()
        invoice_data = SYNC.invoices_grab_pickup(sessions.get('_customerId')['value'])
        if invoice_data:
            for invoice in invoice_data:

                invoice_id = invoice['id']
                quantity = 1
                try:
                    quantity = int(invoice['quantity'])
                except ValueError:
                    quantity = 1

                subtotal = Static.us_dollar(invoice['pretax'])
                tax = Static.us_dollar(invoice['tax'])
                total = Static.us_dollar(invoice['total'])
                rack = invoice['rack']
                due = invoice['due_date']
                count_invoice_items = 0
                if 'invoice_items' in invoice:
                    iitems = invoice['invoice_items']
                    if len(iitems) > 0:
                        count_invoice_items = len(iitems)
                try:
                    dt = datetime.datetime.strptime(due, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    dt = datetime.datetime.strptime('1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
                due_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
                dow = Static.dow(dt.replace(tzinfo=datetime.timezone.utc).weekday())
                due_date = dt.strftime('%m/%d {}').format(dow)
                dt = datetime.datetime.strptime(NOW,
                                                "%Y-%m-%d %H:%M:%S") if NOW is not None else datetime.datetime.strptime(
                    '1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
                now_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
                # check to see if invoice is overdue

                selected = True if invoice_id in self.selected_invoices else False
                invoice_status = int(invoice['status'])
                row_settings = self._make_row_settings(invoice_status, selected, due_strtotime, now_strtotime,
                                                       count_invoice_items)
                if invoice_status < 5:
                    table_data.append({
                        'column': 1,
                        'invoice_id': invoice_id,
                        'text': '[color={}][b]{}[/b][/color]'.format(row_settings['text_color'], '{0:06d}'.format(invoice_id)),
                        'background_color': row_settings['background_color'],
                        'background_normal': ''
                    })
                    table_data.append({
                        'column': 2,
                        'invoice_id': invoice_id,
                        'text': '[color={}][b]{}[/b][/color]'.format(row_settings['text_color'], quantity),
                        'background_color': row_settings['background_color'],
                        'background_normal': ''
                    })

                    table_data.append({
                        'column': 3,
                        'invoice_id': invoice_id,
                        'text': '[color={}][b]{}[/b][/color]'.format(row_settings['text_color'], due_date),
                        'background_color': row_settings['background_color'],
                        'background_normal': ''
                    })
                    table_data.append({
                        'column': 4,
                        'invoice_id': invoice_id,
                        'text': '[color={}][b]{}[/b][/color]'.format(row_settings['text_color'], rack),
                        'background_color': row_settings['background_color'],
                        'background_normal': ''
                    })
                    table_data.append({
                        'column': 4,
                        'invoice_id': invoice_id,
                        'text': '[color={}][b]${}[/b][/color]'.format(row_settings['text_color'],total),
                        'background_color': row_settings['background_color'],
                        'background_normal': ''
                    })
        self.pickup_table_rv.data = table_data

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

    def set_result_status(self):
        sessions.put('_searchResultsStatus', value= True)

    def invoice_selected(self, invoice_id, *args, **kwargs):

        if invoice_id:
            if invoice_id in self.selected_invoices:

                self.selected_invoices.remove(invoice_id)

            else:
                self.selected_invoices.append(invoice_id)
        self.discount_total = 0
        self.amount_tendered = 0
        self.total_amount = 0
        self.total_subtotal = 0
        self.total_quantity = 0
        self.total_tax = 0
        self.discount_total = 0
        if self.selected_invoices:
            invoice_totals = SYNC.invoice_get_totals(self.selected_invoices)
            print(invoice_totals)
            if invoice_totals is not False:
                self.discount_total = Decimal(invoice_totals['discount'])
                self.amount_tendered = Decimal(invoice_totals['total'])
                self.total_amount = Decimal(invoice_totals['total'])
                self.total_subtotal = Decimal(invoice_totals['pretax'])
                self.total_quantity = int(invoice_totals['quantity'])
                self.total_tax = Decimal(invoice_totals['tax'])

        if self.credits or self.discount_total:

            self.total_due = 0 if float(self.credits) >= float(self.total_amount) else float("%0.2f" % (
                    float(self.total_amount) - float(self.credits)))
            print(self.total_due)
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
        self.subtotal_label.text = '[color=000000][b]{}[/b][/color]'.format(Static.us_dollar(self.total_subtotal))
        self.tax_label.text = '[color=000000][b]{}[/b][/color]'.format(Static.us_dollar(self.total_tax))
        self.total_label.text = '[color=000000][b]{}[/b][/color]'.format(Static.us_dollar(self.total_amount))
        self.total_discount.text = '[color=FF0000][b]({})[/b][/color]'.format(Static.us_dollar(self.discount_total))

        self.due_label.text = '[color=000000][b]{}[/b][/color]'.format(Static.us_dollar(self.total_due))

        # update the calculator total
        self.calc_amount = ['{}'.format(int(self.total_due * 100))]
        self.calc_total.text = '[color=000000][b]{}[/b][/color]'.format(Static.us_dollar(self.total_due))

        # calculate change due
        self.change_due = float("%0.2f" % (self.amount_tendered - self.total_due))

        # clear table and update selected rows

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

        total = Static.us_dollar(int(''.join(self.calc_amount)) / 100)
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
        self.calc_total.text = '[color=000000][b]{}[/b][/color]'.format(Static.us_dollar(self.total_due))

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
            credit_card_action_box.add_widget(Button(text="Update", on_press=self.update_card))
            credit_card_action_box.add_widget(Button(text="Add", on_press=self.add_card_popup))
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
            Popups.dialog_msg('Card Error', 'Credit Card Not Selected. Please select card and try again.')
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
                                               on_press=self.finish_popup.dismiss)
                        save_button = Button(text="save",
                                             on_press=self.edit_card)
                        inner_layout_2.add_widget(cancel_button)
                        inner_layout_2.add_widget(save_button)
                        base_layout.add_widget(inner_layout_1)
                        base_layout.add_widget(inner_layout_2)
                        self.finish_popup.content = base_layout
                        self.finish_popup.open()
            else:
                Popups.dialog_msg('Card Error', 'Card selected but could not locate card in local db. Please add a new card instead')

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
            card = SYNC.card_grab(self.card_id)

            if card is not False:
                root_payment_id = card['root_payment_id']

            card_root = SYNC.card_grab_root(root_payment_id)
            if card_root is not False:
                self.run_edit_task(card_root)

            # finish and reset
            Popups.modal_msg('Card Update Successful', 'Successfully updated card. Please reselect your card and invoices before making the online payment.')

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

        data = {
            'street': self.edit_card_billing_street.text,
            'suite': suite,
            'city': self.edit_card_billing_city.text,
            'state': self.edit_card_billing_state.text,
            'exp_month': self.edit_card_exp_month.text,
            'exp_year': self.edit_card_exp_year.text
        }
        card_save = SYNC.update_card(grp['card_id'], data)
        if card_save is not False:
            print('card updated')

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
                               on_press=self.finish_popup.dismiss)
        save_button = Button(text="save",
                             on_press=self.add_card)
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

                            if company_id is 1:
                                self.root_payment_id = payment_id

                            data = {
                                'payment_id': payment_id,
                                'root_payment_id': self.root_payment_id,
                                'street': self.edit_card_billing_street.text,
                                'suite': self.edit_card_billing_suite.text,
                                'city': self.edit_card_billing_city.text,
                                'state': self.edit_card_billing_state.text,
                                'zipcode': self.edit_card_billing_zipcode.text,
                                'exp_month': self.edit_card_exp_month.text,
                                'exp_year': self.edit_card_exp_year.text,
                                'status': 1
                            }
                            cards_create = SYNC.create_card(data)
                            if cards_create is not False:
                                print('card saved')
                        else:
                            Popups.modal_msg('Card Error', result['message'])

                    else:
                        # make profile_id and payment_id

                        customers = SYNC.customers_grab(sessions.get('_customerId')['value'])
                        if customers:
                            for customer in customers:
                                first_name = customer['first_name']
                                last_name = customer['last_name']
                        new_data = {
                            'merchant_id': str(sessions.get('_customerId')['value']),
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

                            data = {
                                'company_id': company_id,
                                'user_id': sessions.get('_customerId')['value'],
                                'profile_id': profile_id,
                                'status': 1
                            }
                            profile_create = SYNC.create_profile(data)
                            if profile_create is False:
                                print('saved profile')

                            if company_id is 1:
                                self.root_payment_id = payment_id
                            data = {
                                'payment_id': payment_id,
                                'root_payment_id': self.root_payment_id,
                                'street': self.edit_card_billing_street.text,
                                'suite': self.edit_card_billing_suite.text,
                                'city': self.edit_card_billing_city.text,
                                'state': self.edit_card_billing_state.text,
                                'zipcode': self.edit_card_billing_zipcode.text,
                                'exp_month': self.edit_card_exp_month.text,
                                'exp_year': self.edit_card_exp_year.text,
                                'status': 1
                            }
                            cards_create = SYNC.create_card(data)
                            if cards_create is not False:
                                print('card saved')


                        else:
                            Popups.modal_msg('Add Card error', make_profile['message'])

            if save_success > 0:
                # finish and reset
                Popups.modal_msg('Card Add Successful', 'Successfully added a card.')

                self.send_to_db()
                self.finish_popup.dismiss()
                self.reset()
                self.select_card_location('1')
            else:
                Popups.modal_msg('Card Add Unsuccessful', 'There were problems saving your card. Please try again')

        pass

    def send_to_db(self):
        # save to server
        t1 = Thread(target=SYNC.db_sync, args=[sessions.get('_companyId')['value']])
        t1.start()
        t1.join()

    def cash_tendered(self, amount):
        if len(self.selected_invoices) > 0:
            total = Static.us_dollar(int(''.join(amount)))
            self.amount_tendered = int(''.join(amount))
            self.change_due = float("%0.2f" % (self.amount_tendered - self.total_due))
            self.calc_total.text = '[color=000000][b]{}[/b][/color]'.format(total)
        else:
            # finish and reset
            Popups.dialog_msg('Transaction Error', 'Please select an invoice before processing.')

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
                self.card_box.ids.validate_button.bind(on_press=self.validate_card)
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
                change_due_text = '[color=0AAC00][b]{}[/b][/color]'.format(Static.us_dollar(self.change_due))
            elif self.change_due == 0:
                change_due_text = '[b]$0.00[/b]'
            elif self.change_due < 0:
                change_due_text = '[color=FF0000][b][i]Remaining Due: {}[/i][/b][/color]'.format(
                    Static.us_dollar(self.change_due))
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
                                         on_press=self.finish_popup.dismiss))

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
                    result = Card().validate_card(sessions.get('_companyId')['value'], profile_id, payment_id)
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

    def finish_transaction(self, _print, *args, **kwargs):
        print('start transaction')
        transaction = Transaction()
        transaction.company_id = sessions.get('_companyId')['value']
        transaction.customer_id = sessions.get('_customerId')['value']
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
            credits_spent = self.total_amount if (Decimal(self.credits) - Decimal(self.total_amount)) >= 0 else Decimal(
                self.credits)
            self.credits_spent = credits_spent
            transaction.credit = credits_spent
        else:
            credits_spent = 0
            transaction.credit = 0
        transaction.total = self.total_due

        # check to see if account status 3 exists else create a new one
        check_account = Transaction()
        checks = SYNC.check_account(sessions.get('_customerId')['value'])
        print('checking transaction account - {}'.format(checks))
        standard_save = False
        if type is 5 and checks is not False:
            print('account customer')
            transaction_id = None
            for ca in checks:
                transaction_id = ca['id']
                old_subtotal = Decimal(ca['pretax'])
                old_tax = Decimal(ca['tax'])
                old_aftertax = Decimal(ca['aftertax'])
                old_credit = Decimal(ca['credit'])
                old_discount = Decimal(ca['discount'])
                old_total = Decimal(ca['total'])
                new_subtotal = old_subtotal + Decimal(self.total_subtotal)
                new_tax = old_tax + Decimal(self.total_tax)
                new_aftertax = old_aftertax + Decimal(self.total_amount)
                new_credits = old_credit + credits_spent
                new_discount = old_discount + Decimal(self.discount_total)
                new_total = old_total + Decimal(self.total_due)
                data = {
                    'pretax': str(self.total_subtotal),
                    'tax': str(self.total_tax),
                    'aftertax': str(self.total_amount),
                    'credit': str(credits_spent),
                    'discount': str(self.discount_total),
                    'total': str(self.total_due)
                }
                check_account = SYNC.update_transaction(sessions.get('_customerId')['value'], data)
                if check_account is not False:
                    print('saved transaction - account')
            # update any credited amount

            old_credits = 0
            old_account_total = 0
            custs = SYNC.customers_grab(sessions.get('_customerId')['value'])
            if custs is not False:
                for customer in custs:
                    if customer['credits'] is not None:
                        old_credits = customer['credits'] if customer['credits'] is not None else 0
                    if customer['account_total'] is not None:
                        old_account_total = Decimal(customer['account_total'])
            new_credits = float("%0.2f" % (float(old_credits) - float(credits_spent)))
            new_account_total = float("%0.2f" % (float(old_account_total) + float(self.total_due)))
            data = {
                'credits': str(credits_spent)
            }
            customer_pickup_update = SYNC.update_customer_pickup(sessions.get('_customerId')['value'], data)
            if customer_pickup_update is not False:
                print('saved account credits info for customer')

            # save transaction_id to Transaction and each invoice
            if self.selected_invoices:
                invoices = Invoice()
                account_trans_id = transaction_id

                for invoice_id in self.selected_invoices:
                    data = {
                        'status': 5,
                        'transaction_id': str(account_trans_id)
                    }
                    invoices_update = SYNC.update_invoice_pickup(invoice_id, data)
                    if invoices_update is not False:
                        print('invoice updated from pickup')

                self.set_result_status()
                self.finish_popup.dismiss()

        elif type is 5 and checks is False:
            transaction.status = 3
            standard_save = True
            customers = User()
            custs = SYNC.customers_grab(sessions.get('_customerId')['value'])
            old_account_total = 0
            if custs is not False:
                for customer in custs:
                    if customer['account_total'] is None or customer['account_total'] is '' or customer[
                        'account_total'] is False:
                        old_account_total = customer['account_total'] if customer['account_total'] else 0

            new_account_total = float("%0.2f" % (float(old_account_total) + float(self.total_due)))
            customer_account_total_update = SYNC.update_customer_account_total(sessions.get('_customerId')['value'], new_account_total)
            if customer_account_total_update is not False:
                print('account total updated')
        else:
            transaction.status = 1
            standard_save = True
        print('transaction status should be 3 - {}'.format(transaction.status))
        if standard_save:
            print('this is a standard save attempting to save data')
            data = {
                'company_id': sessions.get('_companyId')['value'],
                'customer_id': sessions.get('_customerId')['value'],
                'pretax': str(transaction.pretax),
                'tax': str(transaction.tax),
                'aftertax': str(transaction.aftertax),
                'credit': str(transaction.credit),
                'discount': str(transaction.discount),
                'total': str(transaction.total),
                'account_paid': transaction.account_paid,
                'account_paid_on': transaction.account_paid_on,
                'type': transaction.type,
                'last_four': transaction.last_four,
                'tendered': str(transaction.tendered),
                'status': transaction.status
            }
            transaction_create = SYNC.create_transaction(sessions.get('_customerId')['value'], data)
            if transaction_create is not False:
                print('created new transaction')

                # update any discounts or credits
                if self.credits:
                    old_credits = 0
                    customers = User()
                    custs = SYNC.customers_grab(sessions.get('_customerId')['value'])
                    if custs:
                        for customer in custs:
                            old_credits = Decimal(customer['credits'])
                    new_credits = float("%0.2f" % (old_credits - Decimal(credits_spent)))
                    update_customer_credits = SYNC.update_customer_credits(sessions.get('_customerId')['value'], new_credits)
                    if update_customer_credits is not False:
                        print('customer credit has been updated')

                transaction_id = 0

                last_transaction = SYNC.last_transaction_grab(sessions.get('_customerId')['value'])
                if last_transaction is not False:
                    for trans in last_transaction:
                        transaction_id = int(trans['id'])
                if transaction_id > 0:
                    # save transaction_id to Transaction and each invoice
                    if self.selected_invoices:
                        invoices = Invoice()
                        for invoice_id in self.selected_invoices:
                            data = {
                                'status': 5,
                                'transaction_id': transaction_id
                            }
                            update_invoices_pickup = SYNC.update_invoice_pickup(invoice_id, data)
                            if update_invoices_pickup is not False:
                                print('invoices pickedup on cloud')
                        self.set_result_status()
                        self.finish_popup.dismiss()

        if _print == 1:  # customer copy of invoice and finish
            if self.epson:
                pr = Printer()
                companies = Company()
                comps = SYNC.company_grab(sessions.get('_companyId')['value'])
                if comps is not False:
                    companies.id = comps['id']
                    companies.company_id = comps['id']
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
                        customers.user_id = user['id']
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

                if self.selected_invoices:
                    # invoices = Invoice()
                    print_sync_invoice = {}

                    for invoice_id in self.selected_invoices:
                        print_sync_invoice[invoice_id] = {}
                        invoices = SYNC.invoice_grab_id(invoice_id)
                        inv_items = []
                        if invoices is not False:
                            inv_items = invoices['invoice_items']
                        invoice_items = InvoiceItem()

                        colors = {}

                        if len(inv_items) > 0:
                            for invoice_item in inv_items:
                                item_id = invoice_item['item_id']
                                colors[item_id] = {}
                            for invoice_item in inv_items:
                                item_id = invoice_item['item_id']
                                items = SYNC.inventory_items_grab(item_id)
                                if items:
                                    item_name = items['name']
                                    inventory_id = items['inventory_id']
                                else:
                                    item_name = None
                                    inventory_id = None

                                inventories = Inventory()

                                invs = SYNC.inventory_grab(inventory_id)
                                if invs:
                                    inventory_init = invs['name'][:1].capitalize()
                                    laundry = invs['laundry']
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
                    self.epson.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                 density=5,
                                                 invert=False, smooth=False, flip=False))
                    self.epson.write("::Payment Copy::\n")
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

                    self.epson.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3,
                                                 density=6,
                                                 invert=False, smooth=False, flip=False))
                    self.epson.write(
                        '{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                    self.epson.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                 density=2,
                                                 invert=False, smooth=False, flip=False))
                    self.epson.write('{}\n'.format(Job.make_us_phone(customers.phone)))
                    self.epson.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                 density=1,
                                                 invert=False, smooth=False, flip=False))
                    self.epson.write('-----------------------------------------\n')
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
                                    Static.us_dollar(item_price)) + 4
                                string_offset = 42 - string_length if 42 - string_length > 0 else 0
                                self.epson.write('{} {}   {}{}{}\n'.format(item_type,
                                                                           item_qty,
                                                                           item_name,
                                                                           ' ' * string_offset,
                                                                           Static.us_dollar(item_price)))

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

                    self.epson.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                 density=1,
                                                 invert=False, smooth=False, flip=False))
                    self.epson.write('-----------------------------------------\n')
                    self.epson.write(
                        pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                    invert=False, smooth=False, flip=False))
                    self.epson.write('{} PCS\n'.format(self.total_quantity))
                    self.epson.write(pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                 density=1,
                                                 invert=False, smooth=False, flip=False))
                    self.epson.write('-----------------------------------------\n')
                    self.epson.write(
                        pr.pcmd_set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                    invert=False, smooth=False, flip=False))
                    self.epson.write('    SUBTOTAL:')
                    self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    string_length = len(Static.us_dollar(self.total_subtotal))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    self.epson.write('{}{}\n'.format(' ' * string_offset, Static.us_dollar(self.total_subtotal)))
                    self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    self.epson.write('         TAX:')
                    string_length = len(Static.us_dollar(self.total_tax))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    self.epson.write('{}{}\n'.format(' ' * string_offset, Static.us_dollar(self.total_tax)))

                    self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    self.epson.write('   After Tax:')
                    self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    string_length = len(Static.us_dollar(self.total_amount))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    self.epson.write('{}{}\n'.format(' ' * string_offset, Static.us_dollar(self.total_amount)))

                    self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    self.epson.write('      Credit:')
                    self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    string_length = len(Static.us_dollar(self.credits_spent))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    self.epson.write('{}{}\n'.format(' ' * string_offset, Static.us_dollar(self.credits_spent)))

                    self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    self.epson.write('    Discount:')
                    self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    string_length = len(Static.us_dollar(self.discount_total))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    self.epson.write('{}{}\n'.format(' ' * string_offset, Static.us_dollar(self.discount_total)))

                    self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    self.epson.write('         Due:')
                    self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                    string_length = len(Static.us_dollar(self.total_due))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    self.epson.write('{}{}\n'.format(' ' * string_offset, Static.us_dollar(self.total_due)))
                    self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    self.epson.write('     TENDERED:')
                    string_length = len(Static.us_dollar(self.amount_tendered))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    self.epson.write('{}{}\n\n'.format(' ' * string_offset, Static.us_dollar(self.amount_tendered)))
                    self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                    self.epson.write('     BALANCE:')
                    balance = 0 if (
                                           self.amount_tendered - self.total_due) < 0 else self.amount_tendered - self.total_due
                    string_length = len(Static.us_dollar(balance))
                    string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                    self.epson.write('{}{}\n\n'.format(' ' * string_offset, Static.us_dollar(balance)))
                    # Cut paper
                    self.epson.write('\n\n\n\n\n\n')
                    self.epson.write(pr.pcmd('PARTIAL_CUT'))

            else:
                Popups.dialog_msg('Printer Error', 'Usb Device not found')

        self.status_popup.dismiss()

    def set_result_status(self):
        sessions.put('_searchResultsStatus', value= True)