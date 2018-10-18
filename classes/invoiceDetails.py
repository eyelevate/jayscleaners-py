from threading import Thread

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from models.inventory_items import InventoryItem
from models.kv_generator import KvString
from models.sync import Sync
from kivy.uix.popup import Popup
from models.sessions import sessions
from pubsub import pub
from models.jobs import Job
from datetime import datetime
SYNC_POPUP = Popup()
KV = KvString()
SYNC = Sync()


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
    quantity_label = ObjectProperty(None)
    subtotal_label = ObjectProperty(None)
    tax_label = ObjectProperty(None)
    total_label = ObjectProperty(None)
    discount_label = ObjectProperty(None)
    credit_label = ObjectProperty(None)
    tendered_label = ObjectProperty(None)
    due_label = ObjectProperty(None)
    details_table_rv: ObjectProperty(None)
    invoices = []

    def open_popup(self, *args, **kwargs):
        print('ter')
        SYNC_POPUP.title = "Loading"
        content = KV.popup_alert("Please wait while the page is loading")
        SYNC_POPUP.content = Builder.load_string(content)
        SYNC_POPUP.open()
        pub.sendMessage('close_history_popup', popup=SYNC_POPUP)

    def get_details_base(self):
        t1 = Thread(target=self.get_details)
        t1.start()
        # t1.join()

    def get_details(self):
        # Pause Schedule

        invoices = SYNC.invoice_grab_id(sessions.get('_invoiceId')['value'])
        self.invoices = invoices
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

            # get the invoice information
            base_invoice_id = invoices['id']
            company_id = invoices['company_id']
            quantity = invoices['quantity']
            subtotal = '${:,.2f}'.format(float(invoices['pretax'])) if invoices['pretax'] else '$0.00'
            tax = '${:,.2f}'.format(float(invoices['tax'])) if invoices['tax'] else '$0.00'
            total = '${:,.2f}'.format(float(invoices['total'])) if invoices['total'] else '$0.00'
            rack = invoices['rack'] if invoices['rack'] else ''
            rack_date = datetime.strftime(datetime.strptime(invoices['rack_date'], '%Y-%m-%d %H:%M:%S'), '%a %m/%d %I:%M%p') \
                if invoices['rack_date'] else ''

            dropoff_date = datetime.strftime(datetime.strptime(invoices['created_at'], '%Y-%m-%d %H:%M:%S'), '%a %m/%d %I:%M%p') \
                if invoices['created_at'] else ''
            due_date =  datetime.strftime(datetime.strptime(invoices['due_date'], '%Y-%m-%d %H:%M:%S'), '%a %m/%d %I:%M%p') \
                if invoices['due_date'] else ''

            memo = invoices['memo']
            status = invoices['status']
            self.invoice_number_label.text = '[color=000000]#{}[/color]'.format(
                sessions.get('_invoiceId')['value']) if sessions.get('_invoiceId')['value'] else ''
            self.dropoff_label.text = '[color=000000]{}[/color]'.format(dropoff_date)
            self.rack_label.text = '[color=000000]{}[/color]'.format(rack)
            self.rack_date_label.text = '[color=000000]{}[/color]'.format(rack_date)
            self.quantity_label.text = '[color=000000]{}[/color]'.format(quantity)
            self.subtotal_label.text = '[color=000000]{}[/color]'.format(subtotal)
            self.tax_label.text = '[color=000000]{}[/color]'.format(tax)
            self.total_label.text = '[color=000000]{}[/color]'.format(total)

            # get the customer information
            customer_id = invoices['customer_id']
            users = SYNC.customers_grab(customer_id)
            account_check = False
            if users:
                for user in users:
                    account_check = user['account']
                    last_name = user['last_name']
                    first_name = user['first_name']
                    full_name = '{}, {}'.format(last_name.capitalize(), first_name.capitalize())
                    phone = Job.make_us_phone(user['phone'])
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

            # get the transaction information
            transaction_id = invoices['transaction_id']
            # transactions = Transaction().where({'transaction_id': transaction_id})
            transactions = SYNC.transaction_grab(transaction_id)
            if transactions:
                payment_type = transactions['type']
                discount_pre = float(transactions['discount']) if transactions['discount'] else 0
                discount_total = discount_pre + 0
                if not account_check:
                    tendered_total = transactions['tendered'] if transactions['tendered'] else 0
                else:
                    tendered_total = 'account'
                if payment_type == 1:
                    transaction_type = 'Credit'
                    tendered = invoices['total'] - discount_total if not account_check else 0

                elif payment_type == 2:
                    transaction_type = 'Cash'
                elif payment_type == 3:
                    transaction_type = 'Check'
                    tendered_total = invoices['total'] - discount_total if not account_check else 0
                else:
                    transaction_type = ''

                last4 = transactions['last_four']
                pickup_date = datetime.strftime(datetime.strptime(transactions['created_at'], '%Y-%m-%d %H:%M:%S'), '%a %m/%d %I:%M%p') \
                    if transactions['created_at'] else ''

                discount = '${:,.2f}'.format(float(transactions['discount'])) if transactions['discount'] else '$0.00'
                # need to add in credits
                credit = '$0.00'
                if not account_check:
                    due_amt = float(invoices['total']) - float(discount_total) - float(tendered_total)
                    due = '${:,.2f}'.format(float(due_amt))

                else:
                    due = 'account'

                self.pickup_label.text = '[color=000000]{}[/color]'.format(pickup_date)
                self.payment_type_label.text = '[color=000000]{}[/color]'.format(transaction_type)
                self.last4_label.text = '[color=000000]{}[/color]'.format(last4)
                self.discount_label.text = '[color=000000]{}[/color]'.format(discount)
                self.credit_label.text = '[color=000000]{}[/color]'.format(credit)
                self.due_label.text = '[color=000000][b]{}[/b][/color]'.format(due)
                tendered_label = '${:,.2f}'.format(float(tendered_total)) if not account_check else 'account'
                self.tendered_label.text = '[color=000000]{}[/color]'.format(tendered_label)
            else:
                self.pickup_label.text = '[color=000000]{}[/color]'.format('')
                self.payment_type_label.text = '[color=000000]{}[/color]'.format('')
                self.last4_label.text = '[color=000000]{}[/color]'.format('')
                self.discount_label.text = '[color=000000]{}[/color]'.format('$0.00')
                self.credit_label.text = '[color=000000]{}[/color]'.format('$0.00')
                self.due_label.text = '[color=000000][b]{}[/b][/color]'.format(total)
                self.tendered_label.text = '[color=000000]{}[/color]'.format('$0.00')
        self.items_table_update()

    def items_table_update(self):
        self.details_table_rv.data = []
        inv_items = self.invoices['invoice_items']
        item_rows = []
        if inv_items:

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
            for invoice_item in inv_items:
                item_id = invoice_item['item_id']
                items[item_id]['quantity'] += int(invoice_item['quantity']) if invoice_item['quantity'] else 1
                items[item_id]['total'] += float(invoice_item['pretax']) if invoice_item['pretax'] else 0
                if invoice_item['color'] in items[item_id]['color']:
                    items[item_id]['color'][invoice_item['color']] += 1
                else:
                    items[item_id]['color'][invoice_item['color']] = 1
                if invoice_item['memo']:
                    items[item_id]['memo'].append(invoice_item['memo'])

            # print out the items into the table
            if items:
                for key, value in items.items():
                    item_rows.append({
                        'text':'[color=000000]{}[/color]'.format(value['quantity']),
                        'size_hint_x': 0.2
                    })
                    color_string = []
                    for name, color_qty in value['color'].items():
                        if name:
                            color_string.append('{count}-{name}'.format(count=str(color_qty),
                                                                        name=name))
                    item_string = "[b]{item}[/b]:\n{color_s}\n{memo_s}".format(item=value['name'],
                                                                                color_s=', '.join(color_string),
                                                                                memo_s='/ '.join(value['memo']))
                    item_rows.append({
                        'text': '[color=000000]{}[/color]'.format(item_string),
                        'text_wrap': True,
                        'valign': 'top',
                        'halign': 'left',
                        'size_hint_x':0.6
                    })

                    item_rows.append({
                        'text': '[color=000000]${:,.2f}[/color]'.format(value['total']),
                        'size_hint_x':0.2
                    })

        self.details_table_rv.data = item_rows