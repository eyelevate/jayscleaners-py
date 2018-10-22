import calendar
import datetime
import json
import sys
import threading
import time
from _pydecimal import Decimal
from calendar import Calendar
from collections.__init__ import OrderedDict
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
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.uix.textinput import TextInput
from kivy.uix.widget import WidgetException
from pubsub import pub
from classes.popups import Popups
from models.colors import Colored
from models.companies import Company
from models.custids import Custid
from models.discounts import Discount
from models.inventory_items import InventoryItem
from models.invoice_items import InvoiceItem
from models.jobs import Job
from models.kv_generator import KvString
from models.memos import Memo
from models.printers import Printer
from models.sync import Sync
from models.users import User
from models.sessions import sessions
from models.static import Static

SYNC = Sync()
KV = KvString()
SYNC_POPUP = Popup()
Job = Job()


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
    dryclean_tab = ObjectProperty(None)
    items_table_rv = ObjectProperty(None)
    dryclean_rv = ObjectProperty(None)
    laundry_rv = ObjectProperty(None)
    alterations_rv = ObjectProperty(None)
    household_rv = ObjectProperty(None)
    other_rv = ObjectProperty(None)
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
    starch = None
    colors_table_main = ObjectProperty(None)
    customer_id_backup = None
    final_total = 0
    invoice_id = None
    discount_id = None
    memo_list = []
    invoice_items_id = None
    item_rows = {}
    invoice_company_id = sessions.get('_companyId')['value']
    btn_memos_list = []
    company_ids = []
    epson = None
    bixolon = None

    def __init__(self, **kwargs):
        super(EditInvoiceScreen, self).__init__(**kwargs)
        pub.subscribe(self.set_epson_printer, "set_epson_printer")
        pub.subscribe(self.set_bixolon_printer, "set_bixolon_printer")

    def attach(self):
        pub.subscribe(self.set_item, "set_item")
        pub.subscribe(self.remove_item_row, "remove_item_row")
        pub.subscribe(self.select_item, "select_item")

    def detach(self):
        pub.unsubscribe(self.set_item, "set_item")
        pub.unsubscribe(self.remove_item_row, "remove_item_row")
        pub.unsubscribe(self.select_item, "select_item")

    def set_epson_printer(self, device):
        self.epson = device
        print(self.epson)

    def set_bixolon_printer(self, device):
        self.bixolon = device
        print(self.bixolon)

    def reset(self):
        # Pause Schedule
        # self.sync_inventory_items()
        # reset the inventory table
        sessions.put('_discounts',value=[])
        self.customer_id_backup = sessions.get('_customerId')['value']
        self.invoice_id = sessions.get('_invoiceId')['value']
        self.inventory_panel.clear_widgets()
        self.colors_table_main.clear_widgets()
        self.final_total = 0
        self.discount_id = None
        self.invoice_items_id = None
        self.memo_list = []
        self.company_ids = []
        self.item_rows = {}

        today = datetime.datetime.today()
        dow = int(datetime.datetime.today().strftime("%w"))
        company = SYNC.company_grab(company_id=sessions.get('_companyId')['value'])
        if company:
            store_hours = json.loads(company['store_hours']) if company['store_hours'] else None
            if store_hours:

                turn_around_day = int(store_hours[dow]['turnaround']) if 'turnaround' in store_hours[dow] else 0
                turn_around_hour = store_hours[dow]['due_hour'] if 'due_hour' in store_hours[dow] else '4'
                turn_around_minutes = store_hours[dow]['due_minutes'] if 'due_minutes' in store_hours[dow] else '00'
                turn_around_ampm = store_hours[dow]['due_ampm'] if 'due_ampm' in store_hours[dow] else 'pm'
                new_date = today + datetime.timedelta(days=turn_around_day)
                date_string = '{} {}:{}:00'.format(new_date.strftime("%Y-%m-%d"),
                                                   turn_around_hour if turn_around_ampm == 'am' else int(turn_around_hour) + 12,
                                                   turn_around_minutes)

                total_tags = InvoiceItem().total_tags(self.invoice_id)
                invoice_items = []
                invoices = SYNC.invoice_grab_id(self.invoice_id)
                if invoices is not False:
                    invoice_items = invoices['invoice_items']
                self.invoice_list = OrderedDict()
                self.invoice_list_copy = OrderedDict()

                customers = SYNC.customers_grab(self.customer_id_backup)
                if customers:
                    for customer in customers:
                        self.starch = Static.get_starch_by_code(customer['starch'])
                else:
                    self.starch = Static.get_starch_by_code(None)
                if invoice_items:
                    for invoice_item in invoice_items:
                        invoice_items_id = invoice_item['id']
                        item_id = int(invoice_item['item_id'])
                        items = SYNC.inventory_items_grab(item_id)
                        if invoice_item['company_id'] not in self.company_ids:
                            self.company_ids.append(invoice_item['company_id'])
                        self.invoice_company_id = invoice_item['company_id']

                        if items is not False:
                            inventory_id = items['inventory_id']
                            self.inventory_id = inventory_id

                            inventories = SYNC.inventory_grab(self.inventory_id)
                            tags = items['tags']
                            if inventories:

                                inventory_init = inventories['name'][:1].capitalize()
                                laundry = inventories['laundry']
                            else:
                                inventory_init = ''
                                laundry = 0

                            item_name = '{} ({})'.format(items['name'], self.starch) if laundry else items['name']
                            if int(item_id) in self.invoice_list:
                                self.invoice_list[item_id].append({
                                    'invoice_items_id': invoice_items_id,
                                    'type': inventory_init,
                                    'inventory_id': inventory_id,
                                    'item_id': item_id,
                                    'item_name': item_name,
                                    'item_price': Decimal(invoice_item['pretax']),
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
                                    'item_name': item_name,
                                    'item_price': Decimal(invoice_item['pretax']),
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
                                    'item_name': item_name,
                                    'item_price': Decimal(invoice_item['pretax']),
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
                                    'item_name': item_name,
                                    'item_price': Decimal(invoice_item['pretax']),
                                    'color': invoice_item['color'],
                                    'memo': invoice_item['memo'],
                                    'qty': int(invoice_item['quantity']),
                                    'tags': int(tags) if tags else 1,
                                    'deleted': False
                                }]
                        for key, values in OrderedDict(reversed(list(self.invoice_list.items()))).items():
                            sessions.put('_itemId',value=int(key))
                            break

                if invoices is not False:

                    self.due_date = datetime.datetime.strptime(invoices['due_date'], "%Y-%m-%d %H:%M:%S")
                    self.due_date_string = '{}'.format(self.due_date.strftime('%a %m/%d %I:%M%p'))
                    self.summary_quantity_label.text = '[color=000000]{}[/color]'.format(invoices['quantity'])
                    self.summary_tags_label.text = '[color=000000]{}[/color]'.format(total_tags)
                    self.summary_subtotal_label.text = '[color=000000]{}[/color]'.format(Static.us_dollar(invoices['pretax']))
                    self.summary_tax_label.text = '[color=000000]{}[/color]'.format(Static.us_dollar(invoices['tax']))
                    self.summary_discount_label.text = '[color=000000]($0.00)[/color]'
                    self.summary_total_label.text = '[color=000000]{}[/color]'.format(Static.us_dollar(invoices['total']))
                    self.quantity = invoices['quantity']
                    self.tags = total_tags
                    self.subtotal = float(invoices['pretax'])
                    self.tax = float(invoices['tax'])
                    self.discount = 0
                    self.total = float(invoices['total'])
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

                self.memo_color_popup.dismiss()
                self.qty_clicks = 0
                self.inv_qty = 1
                self.inv_qty_list = ['1']
                self.qty_count_label.text = '1'
                self.memo_text_input.text = ''
                self.adjust_price = 0
                self.adjust_price_list = []
                self.get_inventory()
                q = threading.Thread(target=self.get_colors_main)
                r = threading.Thread(target=self.calculate_totals)
                try:
                    r.start()
                    q.start()

                except RuntimeError as e:
                    pass

                taxes = SYNC.taxes_query(self.invoice_company_id, 1)
                if taxes:
                    for tax in taxes:
                        sessions.put('_taxRate', value=float(tax['rate']))
                else:
                    sessions.put('_taxRate', value=0.096)

                self.deleted_rows = []
                self.calculate_totals()

    def set_result_status(self):
        sessions.put('_customerId', value=self.customer_id_backup)
        sessions.put('_invoiceId', value=self.invoice_id)
        sessions.put('_searchResultsStatus', value=True)

    def get_colors_main(self):
        colors = SYNC.colors_query(self.invoice_company_id)
        if colors is not False:
            for color in colors:
                if color['name'] == 'White':
                    color_btn = Button(markup=True,
                                       text='[color="#000000"][b]{color_name}[/b][/color]'.format(color_name=color['name']),
                                       on_release=partial(self.color_selected_main, color['name']))
                else:
                    color_btn = Button(markup=True,
                                       text='[b]{color_name}[/b]'.format(color_name=color['name']),
                                       on_release=partial(self.color_selected_main, color['name']))
                color_btn.background_normal = ''
                color_btn.background_color = Static.color_rgba(color['name'])
                self.colors_table_main.add_widget(color_btn)

    def color_selected_main(self, color_name, *args, **kwargs):
        # quantity

        qty = self.inv_qty

        if sessions.get('_itemId')['value'] in self.invoice_list_copy:
            # loop through the invoice list and see how many colors are set and which is the last row to be set
            total_colors_usable = 0
            rows_updatable = []
            row_to_update = -1
            for row in self.invoice_list_copy[sessions.get('_itemId')['value']]:
                row_to_update += 1

                if 'color' in self.invoice_list_copy[sessions.get('_itemId')['value']][row_to_update]:
                    if self.invoice_list_copy[sessions.get('_itemId')['value']][row_to_update]['color'] is '':
                        total_colors_usable += 1
                        rows_updatable.append(row_to_update)

            if total_colors_usable >= qty:
                qty_countdown = qty
                for row in rows_updatable:

                    if 'color' in self.invoice_list_copy[sessions.get('_itemId')['value']][row]:
                        if self.invoice_list_copy[sessions.get('_itemId')['value']][row]['color'] is '':
                            qty_countdown -= 1
                            if qty_countdown >= 0:
                                self.invoice_list_copy[sessions.get('_itemId')['value']][row]['color'] = color_name

                # save rows and continue

                self.save_memo_color()
            else:
                Popups.dialog_msg('Color Quantity Error',
                                  'Color quantity does not match invoice item quantity. Please try again.')

        # reset qty
        self.set_qty('C')

        pass

    def get_inventory(self):
        iitems = InventoryItem()
        inventories = self.set_inventories()

        if inventories:
            idx = 0
            invitems = {}

            for inventory in inventories:
                idx += 1
                inventory_items = inventory['inventory_items']
                inventory_id = inventory['id']
                invitems[inventory_id] = None
                new = []
                for x in inventory_items:

                    new.append({
                        'text': '[b]{}[/b]\n[i]{}[/i]'.format(x['name'], '${:,.2f}'.format(Decimal(x['price']))),
                        'item_id': x['id'],
                        'Image': {
                            'source': '{}'.format(iitems.get_image_src(x['image'])),
                            'size': '(sp(50),sp(50))',
                            'center_x': 'self.parent.center_x',
                            'center_y': 'self.parent.center_y',
                            'allow_stretch': 'True'
                        }})
                    invitems[inventory_id]= new
                if idx == 1:
                    self.dryclean_rv.data = new
                elif idx == 2:
                    self.laundry_rv.data = new
                elif idx == 3:
                    self.alterations_rv.data = new
                elif idx == 4:
                    self.household_rv.data = new
                else:
                    self.other_rv.data = new

            sessions.put('_inventoryItems', value=invitems)
        self.inventory_panel.switch_to(self.dryclean_tab)

    def set_inventories(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        dt = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
        now_timestamp = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        inventories = SYNC.inventories_by_company(self.invoice_company_id)
        sessions.put('_inventories', value=inventories)
        sessions.put('_inventoryTimestamp', value=now_timestamp)
        # update discounts on each inventory row
        self._update_discounts_by_inventory()

        return inventories

    def _update_discounts_by_inventory(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        discounts = {}
        if len(sessions.get('_discounts')['value']) == 0:
            if self.company_ids:
                for company_id in self.company_ids:
                    inventories = SYNC.inventories_by_company(company_id)
                    for x in inventories:
                        inventory_id = x['id']
                        row = SYNC.discount_query(company_id, now, now, inventory_id)
                        discounts[inventory_id] = row
            self.discounts = discounts
            sessions.put('_discounts', value=discounts)

    def sync_inventory_items(self):
        SYNC.get_chunk('inventory_items', 0, 1000)

    def set_qty(self, qty):

        if qty is 'C':
            self.qty_clicks = 0
            self.inv_qty_list = ['1']
        elif self.qty_clicks is 0 and qty is 0:
            self.qty_clicks += 0
            self.inv_qty_list = ['0']
        elif self.qty_clicks == 0 and qty is 1:
            self.qty_clicks += 1
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
        item_id = int(item_id)
        sessions.put('_itemId', value=int(item_id))
        items = SYNC.inventory_items_grab(item_id)
        if items:
            inventory_id = items['inventory_id']
            item_price = items['price']

            item_tags = items['tags'] if items['tags'] else 1
            item_quantity = items['quantity'] if items['quantity'] else 1
            inventories = SYNC.inventory_grab(inventory_id)
            if inventories:
                inventory_init = inventories['name'][:1].capitalize()
                laundry = inventories['laundry']
            else:
                inventory_init = ''
                laundry = 0

            starch = self.starch if laundry else ''
            item_name = '{} ({})'.format(items['name'], starch) if laundry else items['name']

            for x in range(0, self.inv_qty):

                if int(item_id) in self.invoice_list:
                    self.invoice_list[int(item_id)].append({
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
        row = self.invoice_list[int(sessions.get('_itemId')['value'])]
        del self.invoice_list[int(sessions.get('_itemId')['value'])]
        self.invoice_list[int(item_id)] = row

        self.set_qty('C')
        self.calculate_totals()

    def create_summary_table(self):
        self.items_table_rv.data = []
        if self.invoice_list:
            tr = []
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
                        item_price += float(item['item_price']) if item['item_price'] else 0
                        if item['color']:
                            if item_color in colors:
                                colors[item_color] += 1
                            else:
                                colors[item_color] = 1
                        if item_memo:
                            regexed_memo = item_memo.replace('"', '**Inch(es)')
                            memo_string.append(regexed_memo)
                    if colors:
                        for color_name, color_amount in colors.items():
                            if color_name:
                                color_string.append('{}-{}'.format(color_amount, color_name))

                    item_string = '[b]{}[/b] \n{}\n{}'.format(item_name, ', '.join(color_string),
                                                              '/ '.join(memo_string))
                    selected = True if sessions.get('_itemId')['value'] == item_id else False
                    text_color = 'e5e5e5' if selected else '000000'
                    background_rgba = (0.369, 0.369, 0.369, 1) if selected else (0.826, 0.826, 0.826, 1)
                    tr.append({
                        'column': 1,
                        'item_id': item_id,
                        'text': '[color={}]{}[/color]'.format(text_color, item_type),
                        'size_hint': (0.1,1),
                        'height': 100,
                        'background_color': background_rgba,
                        'background_normal': '',
                        'selected': selected
                    })
                    tr.append({
                        'column': 2,
                        'item_id': item_id,
                        'text': '[color={}]{}[/color]'.format(text_color, total_qty),
                        'size_hint':(0.1,1),
                        'background_color': background_rgba,
                        'background_normal': '',
                        'selected': selected
                    })
                    tr.append({
                        'column': 3,
                        'item_id': item_id,
                        'text': '[color={}]{}[/color]'.format(text_color, item_string),
                        'valign': 'top',
                        'halign': 'left',
                        'size_hint':(0.5,1),
                        'background_color': background_rgba,
                        'background_normal': '',
                        'selected': selected
                    })
                    tr.append({
                        'column': 4,
                        'item_id': item_id,
                        'text': '[color={}]{}[/color]'.format(text_color, str(Static.us_dollar(item_price))),
                        'size_hint': (0.2,1),
                        'background_color': background_rgba,
                        'background_normal': '',
                        'selected': selected
                    })
                    tr.append({
                        'column': 5,
                        'item_id': item_id,
                        'size_hint':(0.1,1),
                        'text': '[color=ffffff][b]-[/b][/color]',
                        'background_color': (1, 0, 0, 1),
                        'background_normal': '',
                        'selected': selected
                    })

            self.items_table_rv.data = tr

    def select_item(self, item_id, *args, **kwargs):
        sessions.put('_itemId', value=int(item_id))
        self.calculate_totals()

    def remove_item_row(self, item_id, *args, **kwargs):
        item_id = int(item_id)
        remove_row = False
        sessions.put('_itemId', value=int(item_id))
        if item_id in self.item_rows:
            del self.item_rows[item_id]

        if item_id in self.invoice_list:
            for x in self.invoice_list[item_id]:
                if 'invoice_items_id' in x:
                    self.deleted_rows.append(x['invoice_items_id'])
                    print('here2')
            del self.invoice_list[item_id]

        if item_id in self.invoice_list_copy:
            del self.invoice_list_copy[item_id]

        if bool(self.invoice_list):
            idx = 0
            for row_key, row_value in self.invoice_list.items():
                idx += 1
                if idx == 1:
                    sessions.put('_itemId', value=int(row_key))
                    break
        else:
            self.invoice_list = {}

        self.calculate_totals()

    def calculate_totals(self):
        self.quantity = 0
        self.subtotal = 0
        self.tags = 0

        self.tax = 0
        self.total = 0
        sum_list = []
        if self.invoice_list:
            for key, values in OrderedDict(reversed(list(self.invoice_list.items()))).items():
                for x in values:
                    sum_list.append(x)
        self.quantity = sum(int(item['qty']) for item in sum_list)
        self.subtotal = sum(float(item['item_price']) for item in sum_list)
        self.tags = sum(int(item['tags']) for item in sum_list)
        self._calc_discount(sum_list)
        self.tax = (self.subtotal - self.discount) * float(sessions.get('_taxRate')['value'])
        self.total = (self.subtotal - self.discount) + self.tax
        self.create_summary_table()
        self.create_summary_totals()

    def _calc_discount(self, list):
        self.discount = 0

        for x in list:
            inventory_id = int(x['inventory_id'])
            disc = sessions.get('_discounts')['value']
            if disc[inventory_id] is not False and inventory_id in disc:
                for discount in disc[inventory_id]:
                    discount_rate = float(discount['rate'])
                    discount_price = float(discount['discount'])
                    self.discount_id = discount['discount_id']
                    if discount_rate > 0:
                        self.discount += (float(x['item_price'] * discount_rate))
                    elif discount_rate is 0 and discount_price > 0:
                        self.discount += (float(x['item_price']) - discount_price)
                    else:
                        self.discount += 0

    def create_summary_totals(self):

        self.summary_quantity_label.text = '[color=000000]{}[/color] pcs'.format(self.quantity)
        self.summary_tags_label.text = '[color=000000]{} tags'.format(self.tags)
        self.summary_subtotal_label.text = '[color=000000]{}[/color]'.format(Static.us_dollar(self.subtotal))
        self.summary_tax_label.text = '[color=000000]{}[/color]'.format(Static.us_dollar(self.tax))
        self.summary_discount_label.text = '[color=000000]({})[/color]'.format(Static.us_dollar(self.discount))
        self.summary_total_label.text = '[color=000000][b]{}[/b][/color]'.format(Static.us_dollar(self.total))

    def make_memo_color(self):

        self.btn_memos_list = []

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
        colors = SYNC.colors_query(sessions.get('_companyId')['value'])
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
                color_btn.background_color = Static.color_rgba(color['name'])
                color_grid.add_widget(color_btn)
        color_layout.add_widget(color_grid)
        # memo section
        memo_layout = BoxLayout(orientation='vertical',
                                size_hint=(1, 0.5))
        memo_inner_layout_1 = BoxLayout(orientation='vertical',
                                        size_hint=(1, 0.8))
        memo_scroll_view = ScrollView()
        memo_grid_layout = Factory.GridLayoutForScrollView(row_default_height='50sp',
                                                           cols=4)
        # check memo button statuses
        memos = SYNC.memos_query(sessions.get('_companyId')['value'])
        if memos:
            for memo in memos:
                btn_memo = Factory.LongButton(text=str(memo['memo']),
                                              background_normal='',
                                              background_color=(0.369, 0.369, 0.369, 1))
                btn_memo.bind(on_press=partial(self.append_memo, btn_memo, memo['memo']))
                self.btn_memos_list.append(btn_memo)
                memo_grid_layout.add_widget(btn_memo)

        memo_scroll_view.add_widget(memo_grid_layout)

        memo_inner_layout_2 = BoxLayout(orientation='horizontal',
                                        size_hint=(1, 0.2))
        memo_title = Label(markup=True,
                           pos_hint={'top': 1},
                           text='[b]Create Memo[/b]',
                           size_hint=(1, 0.1))
        memo_text_input = Factory.CenterVerticalTextInput(text='',
                                                          size_hint=(0.7, 1),
                                                          multiline=False)
        memo_inner_layout_1.add_widget(memo_title)
        memo_inner_layout_1.add_widget(memo_scroll_view)

        try:
            memo_inner_layout_2.add_widget(memo_text_input)
        except WidgetException:
            memo_inner_layout_2.remove_widget(memo_text_input)
            memo_inner_layout_2.add_widget(memo_text_input)
        memo_layout.add_widget(memo_inner_layout_1)
        memo_layout.add_widget(memo_inner_layout_2)
        self.memo_text_input = memo_text_input
        memo_add_button = Button(text='Update',
                                 size_hint=(0.3, 1),
                                 on_press=self.add_memo)
        memo_inner_layout_2.add_widget(memo_add_button)

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
        self.item_row_selected(row=0)

    def append_memo(self, btn, msg, *args, **kwargs):
        self.memo_list = self._update_memo_btn_statuses()
        self.memo_text_input.text = ''
        # check if memo is in the memo_list
        if msg in self.memo_list[self.item_selected_row]:
            self.memo_list[self.item_selected_row].remove(msg)
            self._change_memo_btn_state(btn, False)
        else:
            self.memo_list[self.item_selected_row].append(msg)
            self._change_memo_btn_state(btn, True)
        # memo_string = ', '.join(self.memo_list)
        # self.memo_text_input.text = ''
        return

    def _change_memo_btn_state(self, btn, state, *args, **kwargs):
        background_rgba = (0.369, 0.369, 0.369, 1) if not state else (0.826, 0.826, 0.826, 1)
        btn.background_color = background_rgba
        self.memo_text_input.text = ''
        self.add_memo(self.item_selected_row)
        pass

    def _update_memo_btn_statuses(self):
        memo_list = []
        if sessions.get('_itemId')['value'] in self.invoice_list_copy:

            for x in self.invoice_list_copy[sessions.get('_itemId')['value']]:

                if 'memo' in x:
                    if x['memo'] is '' or x['memo'] is None or not x['memo']:
                        memo_list.append([])
                    else:
                        memo_list.append(str(x['memo']).split(', ') if ',' in x['memo'] else [x['memo']])
        return memo_list

    def _redo_memo_btn_states(self):
        # set the states of buttons based on row and item previously picked
        filtered_list = self.memo_list[self.item_selected_row] if self.memo_list[self.item_selected_row ] else []
        if filtered_list:
            if self.btn_memos_list:
                for btns in self.btn_memos_list:
                    if filtered_list:
                        for memo in filtered_list:
                            if str(btns.text) == str(memo):
                                filtered_list.remove(memo)
                                btns.background_color = (0.826, 0.826, 0.826, 1)

                                break
                            else:
                                btns.background_color = (0.369, 0.369, 0.369, 1)
                                continue

                remaining_items = ''
                if filtered_list and len(filtered_list) == 1:
                    remaining_items = filtered_list[0]
                self.memo_text_input.text = str(remaining_items)

    def _reset_memo_btn_states_to_default(self):
        for btns in self.btn_memos_list:
            btns.background_color = (0.369, 0.369, 0.369, 1)
        pass

    def add_memo(self, *args, **kwargs):
        if sessions.get('_itemId')['value'] in self.invoice_list_copy:
            # loop through to check if we are updating the text only
            temp_memos = []
            if self.memo_text_input.text != '':
                memo_string = self.memo_text_input.text
                if self.btn_memos_list:
                    for btns in self.btn_memos_list:
                        if btns.background_color == [0.826, 0.826, 0.826, 1]:
                            temp_memos.append(btns.text)

                temp_memos.append(memo_string)
                self.memo_list[self.item_selected_row] = temp_memos

            memo_string = ''.join(self.memo_list[self.item_selected_row]) if \
                len(self.memo_list[self.item_selected_row]) == 1 else ', '.join(self.memo_list[self.item_selected_row])

            self.invoice_list_copy[sessions.get('_itemId')['value']][self.item_selected_row][
                'memo'] = memo_string
            self.make_items_table()
            self.memo_text_input.text = ''

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

        try:
            self.invoice_list_copy[sessions.get('_itemId')['value']]
            idx = -1
            for items in self.invoice_list_copy[sessions.get('_itemId')['value']]:
                idx += 1
                background_color = (0.36862745, 0.36862745, 0.36862745, 1) if idx == self.item_selected_row else (
                    0.89803922, 0.89803922, 0.89803922, 1)
                background_normal = ''
                text_color = 'e5e5e5' if idx == self.item_selected_row else '000000'
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
                                               font_size='12sp',
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
        except KeyError as e:
            Popups.dialog_msg('Selection Error', 'Please select an item before attempting an edit.')

            return False
        self.items_grid.bind(minimum_height=self.items_grid.setter('height'))

    def color_selected(self, color=False, *args, **kwargs):
        if sessions.get('_itemId')['value'] in self.invoice_list_copy:
            self.invoice_list_copy[sessions.get('_itemId')['value']][self.item_selected_row]['color'] = color
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
        if sessions.get('_itemId')['value'] in self.invoice_list_copy:
            self.invoice_list_copy[sessions.get('_itemId')['value']][self.item_selected_row]['color'] = ''
            self.make_items_table()

    def remove_memo(self, *args, **kwargs):
        if sessions.get('_itemId')['value'] in self.invoice_list_copy:
            self.invoice_list_copy[sessions.get('_itemId')['value']][self.item_selected_row]['memo'] = ''
            self.make_items_table()

    def item_row_selected(self, row, *args, **kwargs):
        self.item_selected_row = row
        self.make_items_table()
        self.memo_list = self._update_memo_btn_statuses()
        self._reset_memo_btn_states_to_default()
        self._redo_memo_btn_states()

    def save_memo_color(self, *args, **kwargs):
        if sessions.get('_itemId')['value'] in self.invoice_list_copy:
            idx = -1

            for items in self.invoice_list_copy[sessions.get('_itemId')['value']]:
                idx += 1

                text_color = 'e5e5e5' if idx == self.item_selected_row else '000000'
                color = items['color']
                memo = items['memo']

                # update colors in text

                self.invoice_list[sessions.get('_itemId')['value']][idx]['color'] = color
                self.invoice_list[sessions.get('_itemId')['value']][idx]['memo'] = memo
        self.calculate_totals()

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

        if sessions.get('_itemId')['value'] in self.invoice_list_copy:
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

                for key, values in self.invoice_list_copy.items():
                    if key == sessions.get('_itemId')['value']:
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
                                item_price += float(item['item_price']) if item['item_price'] else 0
                                if item['color']:
                                    if item_color in colors:
                                        colors[item_color] += 1
                                    else:
                                        colors[item_color] = 1
                                if item_memo:
                                    regexed_memo = item_memo.replace('"', '**Inch(es)')
                                    memo_string.append(regexed_memo)
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
                                         text='{}'.format(Static.us_dollar(item_price)),
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

        if self.invoice_list is not False:
            for key, values in self.invoice_list_copy.items():
                if key == sessions.get('_itemId')['value']:
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
                        text_color = 'e5e5e5' if idx == self.item_selected_row else '000000'
                        invoice_items_id = item['invoice_items_id'] if 'invoice_items_id' in item else None

                        tr1 = Button(size_hint_x=0.1,
                                     markup=True,
                                     text='[color={text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                     msg=item_type),
                                     on_press=partial(self.item_row_adjusted_selected, 2, item_price, idx),
                                     background_color=background_color,
                                     background_normal=background_normal)
                        tr2 = Button(size_hint_x=0.1,
                                     markup=True,
                                     text='[color={text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                     msg=1),
                                     on_press=partial(self.item_row_adjusted_selected, 2, item_price, idx),
                                     background_color=background_color,
                                     background_normal=background_normal)
                        tr3 = Factory.LongButton(size_hint_x=0.6,
                                                 size_hint_y=None,
                                                 markup=True,
                                                 text='[color={text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                                 msg=item_string),
                                                 on_press=partial(self.item_row_adjusted_selected, 2, item_price, idx),
                                                 background_color=background_color,
                                                 background_normal=background_normal)
                        tr4 = Button(size_hint_x=0.2,
                                     markup=True,
                                     text='[color={text_color}]{msg}[/color]'.format(text_color=text_color,
                                                                                     msg=Static.us_dollar(item_price)),
                                     on_press=partial(self.item_row_adjusted_selected, 2, item_price, idx),
                                     background_color=background_color,
                                     background_normal=background_normal)

                        tr5 = Button(size_hint_x=0.1,
                                     markup=True,
                                     text='[color=ffffff][b]-[/b][/color]',
                                     on_release=partial(self.item_row_delete_selected, idx, invoice_items_id),
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
        self.calculator_text = Factory.CenteredLabel(text="[color=000000][b]{}[/b][/color]".format(Static.us_dollar(0)))
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
        original_price = Factory.ReadOnlyLabel(text='[color=e5e5e5]{}[/color]'.format(Static.us_dollar(price)))
        summary_grid.add_widget(original_price)
        summary_grid.add_widget(Label(markup=True,
                                      text="Adjusted Price"))
        self.adjusted_price = Factory.ReadOnlyLabel(
            text='[color=e5e5e5]{}[/color]'.format(Static.us_dollar(self.adjust_price)))
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
        self.calculator_text.text = '[color=000000][b]{}[/b][/color]'.format(Static.us_dollar(self.adjust_price))
        self.adjusted_price.text = '[color=e5e5e5][b]{}[/b][/color]'.format(Static.us_dollar(self.adjust_price))

    def set_price_adjustment_sum_correct_individual(self, row, *args, **kwargs):
        if sessions.get('_itemId')['value'] in self.invoice_list_copy:
            total_count = len(self.invoice_list_copy[sessions.get('_itemId')['value']])
            new_avg_price = round(self.adjust_price / total_count, 2)
            minus_total = self.adjust_price
            idx = -1
            for items in self.invoice_list_copy[sessions.get('_itemId')['value']]:
                idx += 1
                minus_total -= new_avg_price
                if idx < len(self.invoice_list_copy[sessions.get('_itemId')['value']]) - 1:
                    self.invoice_list_copy[sessions.get('_itemId')['value']][idx]['item_price'] = new_avg_price
                else:
                    self.invoice_list_copy[sessions.get('_itemId')['value']][idx]['item_price'] = round(
                        new_avg_price + minus_total, 2)
            self.make_adjustment_sum_table()
            self.make_adjustment_individual_table()

    def set_price_adjustment_individual_correct_sum(self, row, *args, **kwargs):
        if sessions.get('_itemId')['value'] in self.invoice_list_copy:
            self.invoice_list_copy[sessions.get('_itemId')['value']][row]['item_price'] = self.adjust_price
            self.make_adjustment_sum_table()
            self.make_adjustment_individual_table()

    def save_price_adjustment(self, *args, **kwargs):

        if sessions.get('_itemId')['value'] in self.invoice_list_copy:
            idx = -1
            for items in self.invoice_list_copy[sessions.get('_itemId')['value']]:
                idx += 1
                new_price = items['item_price']
                self.invoice_list[sessions.get('_itemId')['value']][idx]['item_price'] = new_price
            self.calculate_totals()

    def item_row_delete_selected(self, row, invoice_items_id, *args, **kwargs):
        if sessions.get('_itemId')['value'] in self.invoice_list:
            print('test1')
            for item_row in self.invoice_list[int(sessions.get('_itemId')['value'])]:
                if 'invoice_items_id' in item_row:
                    if item_row['invoice_items_id'] is invoice_items_id:
                        self.deleted_rows.append(item_row['invoice_items_id'])
        del self.invoice_list[sessions.get('_itemId')['value']][row]
        del self.invoice_list_copy[sessions.get('_itemId')['value']][row]
        self.item_selected_row = 0
        self.make_adjustment_sum_table()
        self.make_adjustment_individual_table()
        self.calculate_totals()

    def item_row_adjusted_selected(self, type=None, price=0, row=None, *args, **kwargs):
        self.item_selected_row = row
        self.adjust_individual_grid.clear_widgets()
        self.make_adjustment_individual_table()

        self.adjustment_calculator(type=type, price=price, row=row)

    def make_calendar(self):

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
                self.month_button = Button(text='{}'.format(Static.month_by_number(self.month)),
                                           on_release=select_month.open)
                for index in range(12):
                    month_options = Button(text='{}'.format(Static.month_by_number(index)),
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
        button_1 = Factory.PrintButton(text='Cust. + Store',
                                       on_release=partial(self.wait_popup, 'both'))

        inner_layout_1.add_widget(button_1)
        button_2 = Factory.PrintButton(text='Store Only',
                                       on_release=partial(self.wait_popup, 'store'))

        inner_layout_1.add_widget(button_2)
        button_3 = Factory.PrintButton(text='No Print',
                                       on_release=partial(self.wait_popup, 'none'))

        inner_layout_1.add_widget(button_3)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.3))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='Cancel',
                                         on_release=self.print_popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.print_popup.content = layout
        self.print_popup.open()

    def wait_popup(self, type, *args, **kwargs):
        SYNC_POPUP.title = 'Syncing Data'
        content = KV.popup_alert("Syncing data to server, please wait...")
        SYNC_POPUP.content = Builder.load_string(content)
        SYNC_POPUP.open()
        Clock.schedule_once(partial(self.finish_invoice, type))
        # send event
        pub.sendMessage('close_loading_popup', popup=SYNC_POPUP)

    def finish_invoice(self, type, *args, **kwargs):

        # determine the types of invoices we need to print
        self.create_summary_totals()
        self.now = datetime.datetime.now()
        # set the printer data
        tax_rate = sessions.get('_taxRate')['value']

        if len(self.deleted_rows) > 0:
            check_deleted_rows = SYNC.delete_invoice_items(self.deleted_rows)
            if check_deleted_rows is not False:
                print('successfully deleted rows from server')

        if self.invoice_list:
            invoice_items = InvoiceItem()
            print_invoice = {}
            print_invoice[self.invoice_id] = {}

            for invoice_item_key, invoice_item_value in self.invoice_list.items():
                colors = {}
                for iivalue in invoice_item_value:
                    item_id = iivalue['item_id']
                    colors[item_id] = {}
                for iivalue in invoice_item_value:
                    qty = iivalue['qty']
                    pretax = "{0:.2f}".format(float(iivalue['item_price'])) if iivalue['item_price'] else 0
                    tax = "{0:.2f}".format(float(iivalue['item_price']) * float(tax_rate))
                    total = "{0:.2f}".format(float(iivalue['item_price']) * (1 + float(tax_rate)))
                    item_id = iivalue['item_id']
                    inventory_id = InventoryItem().getInventoryId(item_id)
                    item_name = iivalue['item_name']
                    item_price = Decimal(iivalue['item_price'])
                    item_type = iivalue['type']
                    item_color = iivalue['color']
                    item_memo = iivalue['memo']
                    if item_id in colors:
                        if item_color in colors[item_id]:
                            colors[item_id][item_color] += 1
                        else:
                            colors[item_id][item_color] = 1
                    if self.invoice_id in print_invoice:
                        if item_id in print_invoice[self.invoice_id]:
                            print_invoice[self.invoice_id][item_id]['item_price'] += item_price
                            print_invoice[self.invoice_id][item_id]['qty'] += 1
                            if item_id in colors:
                                print_invoice[self.invoice_id][item_id]['colors'] = colors[item_id]
                            else:
                                print_invoice[self.invoice_id][item_id]['colors'] = []
                            if item_memo:
                                print_invoice[self.invoice_id][item_id]['memos'].append(item_memo)
                        else:

                            print_invoice[self.invoice_id][item_id] = {
                                'item_id': item_id,
                                'type': item_type,
                                'name': item_name,
                                'item_price': item_price,
                                'qty': 1,
                                'memos': [item_memo] if item_memo else [],
                                'colors': colors[item_id] if item_id in colors else []
                            }
                    if 'invoice_items_id' in iivalue:
                        data = {
                            'quantity': iivalue['qty'],
                            'color': iivalue['color'] if iivalue['color'] else '',
                            'memo': item_memo if item_memo is not None else '',
                            'pretax': pretax,
                            'tax': tax,
                            'total': total
                        }
                        invoice_items_edit = SYNC.edit_invoice_item(iivalue['invoice_items_id'], data)
                        if invoice_items_edit is not False:
                            print('invoice item updated')

                    else:
                        print('Here...')

                        data = {
                            'company_id': self.invoice_company_id,
                            'customer_id': sessions.get('_customerId')['value'],
                            'invoice_id': self.invoice_id,
                            'item_id': item_id,
                            'inventory_id': inventory_id,
                            'quantity': qty,
                            'color': str(item_color) if item_color else None,
                            'memo': str(item_memo) if item_memo else None,
                            'pretax': pretax,
                            'tax': tax,
                            'total': total,
                            'status': 1
                        }
                        invoice_items_create = SYNC.create_invoice_item(data)
                        if invoice_items_create is not False:
                            print('created new invoice item')
            self.update_invoice()
        time.sleep(1)

        # print invoices
        if self.epson:
            pr = Printer()
            companies = Company()
            comps = SYNC.company_grab(self.invoice_company_id)
            if comps:
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

            if type is 'none':
                self.set_result_status()
                self.print_popup.dismiss()
                pass
            elif type is 'both':
                print('Customer & Store Copy')
                self.epson.write(pr.pcmd('TXT_ALIGN_CT'))
                self.epson.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                density=5, invert=False, smooth=False, flip=False))
                self.epson.write("::CUSTOMER::\n")
                self.epson.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
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
                self.epson.write("edited on: {}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                self.epson.write(
                    pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                invert=False, smooth=False, flip=False))
                self.epson.write("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                self.epson.write(pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                        invert=False, smooth=False, flip=False))
                padded_customer_id = '{0:05d}'.format(self.customer_id_backup)
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

                # display invoice details
                if self.invoice_list:

                    for key, values in OrderedDict(reversed(list(self.invoice_list.items()))).items():
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
                                item_price += float(item['item_price']) if item['item_price'] else 0
                                if item['color']:
                                    if item_color in colors:
                                        colors[item_color] += 1
                                    else:
                                        colors[item_color] = 1
                                if item_memo:
                                    regexed_memo = item_memo.replace('"', '**Inch(es)')
                                    memo_string.append(regexed_memo)
                            if colors:
                                for color_name, color_amount in colors.items():
                                    if color_name:
                                        color_string.append('{}-{}'.format(color_amount, color_name))

                            self.epson.write(
                                pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=5, invert=False, smooth=False, flip=False))
                            self.epson.write('{} {}    '.format(item_type, total_qty, item_name))
                            self.epson.write(pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'B', width=1, height=1,
                                                    density=5, invert=False, smooth=False, flip=False))
                            self.epson.write('{}\n'.format(item_name))
                            if len(memo_string) > 0:
                                self.epson.write(
                                    pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                density=5, invert=False, smooth=False, flip=False))
                                self.epson.write('  {}\n'.format('/ '.join(memo_string)))
                            if len(color_string):
                                self.epson.write(
                                    pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                density=5, invert=False, smooth=False, flip=False))
                                self.epson.write('{}\n'.format(', '.join(color_string)))

                self.epson.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                self.epson.write('-----------------------------------------\n')
                self.epson.write(pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                        invert=False, smooth=False, flip=False))
                self.epson.write('{} PCS\n'.format(self.quantity))
                self.epson.write(
                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                invert=False, smooth=False, flip=False))
                self.epson.write('-----------------------------------------\n')
                # Cut paper
                self.epson.write('\n\n\n\n\n\n')
                self.epson.write(pr.pcmd('PARTIAL_CUT'))

                # Print store copies
                if print_invoice:  # if invoices synced
                    for invoice_id, item_id in print_invoice.items():
                        if isinstance(invoice_id, str):
                            invoice_id = int(invoice_id)
                        # start invoice
                        self.epson.write(pr.pcmd('TXT_ALIGN_CT'))
                        self.epson.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write("::COPY::\n")
                        self.epson.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write("{}\n".format(companies.name))
                        self.epson.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write("{}\n".format(Job.make_us_phone(companies.phone)))
                        self.epson.write("edited: {}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                        self.epson.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                        self.epson.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write("{}\n".format('{0:06d}'.format(invoice_id)))
                        # Print barcode
                        self.epson.write(pr.pcmd_barcode('{}'.format('{0:06d}'.format(invoice_id))))

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
                        if invoice_id in print_invoice:
                            for item_id, invoice_item in print_invoice[invoice_id].items():
                                item_name = invoice_item['name']
                                item_price = Decimal(invoice_item['item_price'])
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

                                # self.epson.write('\r\x1b@\x1b\x61\x02{}\n'.format(Static.us_dollar(item_price)))
                                if len(item_memo) > 0:
                                    self.epson.write(
                                        pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                    density=5, invert=False, smooth=False, flip=False))
                                    self.epson.write('     {}\n'.format('/ '.join(item_memo)))
                                if len(item_color_string) > 0:
                                    self.epson.write(
                                        pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                    density=5, invert=False, smooth=False, flip=False))
                                    self.epson.write('     {}\n'.format(', '.join(item_color_string)))

                        self.epson.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write('-----------------------------------------\n')
                        self.epson.write(
                            pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write('{} PCS\n'.format(self.quantity))
                        self.epson.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write('-----------------------------------------\n')
                        self.epson.write(
                            pr.pcmd_set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write('    SUBTOTAL:')
                        self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                        string_length = len(Static.us_dollar(self.subtotal))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        self.epson.write('{}{}\n'.format(' ' * string_offset,
                                                    Static.us_dollar(self.subtotal)))
                        self.epson.write('    DISCOUNT:')
                        self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                        string_length = len(Static.us_dollar(self.discount))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        self.epson.write('{}({})\n'.format(' ' * string_offset,
                                                      Static.us_dollar(self.discount)))
                        self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                        self.epson.write('         TAX:')
                        string_length = len(Static.us_dollar(self.tax))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                        self.epson.write('{}{}\n'.format(' ' * string_offset,
                                                    Static.us_dollar(self.tax)))
                        self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                        self.epson.write('       TOTAL:')
                        self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                        string_length = len(Static.us_dollar(self.total))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        self.epson.write('{}{}\n'.format(' ' * string_offset,
                                                    Static.us_dollar(self.total)))
                        self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                        self.epson.write('     BALANCE:')
                        string_length = len(Static.us_dollar(self.total))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        self.epson.write('{}{}\n\n'.format(' ' * string_offset,
                                                      Static.us_dollar(self.total)))
                        if item_type == 'L':
                            # get customer mark
                            marks = Custid()
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
            elif type is 'store':
                print('Store Copy Only')
                # Print store copies
                if print_invoice:  # if invoices synced
                    for invoice_id, item_id in print_invoice.items():
                        if isinstance(invoice_id, str):
                            invoice_id = int(invoice_id) if invoice_id else 0
                        # start invoice
                        self.epson.write(pr.pcmd('TXT_ALIGN_CT'))
                        self.epson.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write("::COPY::\n")
                        self.epson.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write("{}\n".format(companies.name))
                        self.epson.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write("{}\n".format(Job.make_us_phone(companies.phone)))
                        self.epson.write("edited: {}\n\n".format(self.now.strftime('%a %m/%d/%Y %I:%M %p')))
                        self.epson.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write("READY BY: {}\n\n".format(self.due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                        self.epson.write(
                            pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write("{}\n".format('{0:06d}'.format(invoice_id)))
                        # Print barcode
                        self.epson.write(pr.pcmd_barcode('{0:06d}'.format(invoice_id)))

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

                        if invoice_id in print_invoice:
                            for item_id, invoice_item in print_invoice[invoice_id].items():
                                item_name = invoice_item['name']
                                item_price = Decimal(invoice_item['item_price'])
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

                                # self.epson.write('\r\x1b@\x1b\x61\x02{}\n'.format(Static.us_dollar(item_price)))
                                if len(item_memo) > 0:
                                    self.epson.write(
                                        pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                    density=5, invert=False, smooth=False, flip=False))
                                    self.epson.write('     {}\n'.format('/ '.join(item_memo)))
                                if len(item_color_string) > 0:
                                    self.epson.write(
                                        pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                                    density=5, invert=False, smooth=False, flip=False))
                                    self.epson.write('     {}\n'.format(', '.join(item_color_string)))

                        self.epson.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write('-----------------------------------------\n')
                        self.epson.write(
                            pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write('{} PCS\n'.format(self.quantity))
                        self.epson.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write('-----------------------------------------\n')
                        self.epson.write(
                            pr.pcmd_set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                        invert=False, smooth=False, flip=False))
                        self.epson.write('    SUBTOTAL:')
                        self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                        string_length = len(Static.us_dollar(self.subtotal))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        self.epson.write('{}{}\n'.format(' ' * string_offset,
                                                    Static.us_dollar(self.subtotal)))
                        self.epson.write('    DISCOUNT:')
                        self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                        string_length = len(Static.us_dollar(self.discount))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        self.epson.write('{}({})\n'.format(' ' * string_offset,
                                                      Static.us_dollar(self.discount)))
                        self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                        self.epson.write('         TAX:')
                        string_length = len(Static.us_dollar(self.tax))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                        self.epson.write('{}{}\n'.format(' ' * string_offset,
                                                    Static.us_dollar(self.tax)))
                        self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                        self.epson.write('       TOTAL:')
                        self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                        string_length = len(Static.us_dollar(self.total))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        self.epson.write('{}{}\n'.format(' ' * string_offset,
                                                    Static.us_dollar(self.total)))
                        self.epson.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                        self.epson.write('     BALANCE:')
                        string_length = len(Static.us_dollar(self.total))
                        string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                        self.epson.write('{}{}\n\n'.format(' ' * string_offset,
                                                      Static.us_dollar(self.total)))
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
            popup = Popup()
            popup.title = 'Printer Error'
            content = KV.popup_alert('Unable to locate usb printer.')
            popup.content = Builder.load_string(content)
            popup.open()
            sys.stdout.write('\a')
            sys.stdout.flush()
            time.sleep(2)
            popup.dismiss()

        sessions.put('_customerId', value=self.customer_id_backup)
        self.set_result_status()

        self.print_popup.dismiss()
        SYNC_POPUP.dismiss()

    def update_invoice(self, *arkgs, **kwargs):
        print('starting update on invoice - {}'.format(self.invoice_id))

        data = {
            'company_id': self.invoice_company_id,
            'customer_id': sessions.get('_customerId')['value'],
            'quantity': self.tags,
            'pretax': '{0:.2f}'.format(float(self.subtotal)),
            'tax': '{0:.2f}'.format(float(self.tax)),
            'discount_id': self.discount_id if self.discount_id is not None else '',
            'due_date': '{}'.format(self.due_date.strftime("%Y-%m-%d %H:%M:%S")),
            'total': '{0:.2f}'.format(float(self.total))
        }
        invoice_check = SYNC.edit_invoice(self.invoice_id, data)
        if invoice_check is not False:
            print('updated invoice')
            sessions.put('_customerId', value=self.customer_id_backup)
            sessions.put('_searchResultsStatus', value=True)
