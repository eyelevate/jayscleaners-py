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

from classes.popups import Popups
from models.companies import Company
from models.custids import Custid
from models.discounts import Discount
from models.inventory_items import InventoryItem
from models.invoices import Invoice
from models.jobs import Job
from models.kv_generator import KvString
from models.printers import Printer
from models.sync import Sync
from models.transactions import Transaction
from models.users import User
from models.sessions import sessions
from models.static import Static
from pubsub import pub

SYNC = Sync()
SYNC_POPUP = Popup()
KV = KvString()
Job = Job()
unix = time.time()
NOW = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
EPSON = sessions.get('_epson')['value']
BIXOLON = sessions.get('_bixolon')['value']

class HistoryScreen(Screen):
    invoices_table = ObjectProperty(None)
    invoice_table_body = ObjectProperty(None)
    item_image = ObjectProperty(None)
    items_table = ObjectProperty(None)
    invs_results_label = ObjectProperty(None)
    history_popup = ObjectProperty(None)
    status_spinner = ObjectProperty(None)
    starch = None
    selected_tags_list = []
    tags_grid = ObjectProperty(None)
    row_set = 0
    row_increment = 10
    up_btn = ObjectProperty(None)
    down_btn = ObjectProperty(None)

    def reset_base(self):
        t1 = Thread(target=self.reset)
        t1.start()

    def reset(self):
        # Pause Schedule

        # check if an invoice was previously selected
        self.items_table.clear_widgets()

        # set any necessary variables
        customers = SYNC.customers_grab(sessions.get('_customerId')['value'])
        if customers:
            for customer in customers:
                self.starch = Static.get_starch_by_code(customer['starch'])
        else:
            self.starch = Static.get_starch_by_code(None)

        # create the invoice count list
        sessions.get('_rowCap')['value'] = SYNC.invoices_grab_count(sessions.get('_customerId')['value'])
        if sessions.get('_rowCap')['value'] < 10 and sessions.get('_rowCap')['value'] <= self.row_set:
            self.row_set = 0

        row_end = self.row_set + 9
        self.invs_results_label.text = '[color=000000]Showing rows [b]{}[/b] - [b]{}[/b] out of [b]{}[/b][/color]'.format(
            self.row_set,
            row_end,
            sessions.get('_rowCap')['value']
        )
        invs = SYNC.invoice_search_history(sessions.get('_customerId')['value'], self.row_set, row_end)
        sessions.put('_searchResults', value= invs)
        # get invoice rows and display them to the table

        # create Tbody TR
        self.invoice_table_body.clear_widgets()
        if sessions.get('_searchResults')['value'] is not False:
            for cust in sessions.get('_searchResults')['value']:
                self.create_invoice_row(cust)

        sessions.get('_searchResults')['value'] = []

        if sessions.get('_invoiceId')['value']:
            self.items_table_update()


    def open_popup(self, *args, **kwargs):
        SYNC_POPUP.title = "Loading"
        content = KV.popup_alert("Please wait while the page is loading")
        SYNC_POPUP.content = Builder.load_string(content)
        SYNC_POPUP.open()
        # send event
        pub.sendMessage('close_loading_popup', popup=SYNC_POPUP)

    def create_invoice_row(self, row, *args, **kwargs):
        """ Creates invoice table row and displays it to screen """
        check_invoice_id = sessions.get('_invoiceId')['value']
        invoice_id = row['id']
        company_id = row['company_id']
        quantity = row['quantity']
        rack = row['rack']
        total = '${:,.2f}'.format(Decimal(row['total']))
        due = row['due_date']
        status = row['status']
        invoices = SYNC.invoice_grab_id(invoice_id)
        invoice_items = []
        if invoices is not False:
            invoice_items = invoices['invoice_items']

        count_invoice_items = len(invoice_items)
        deleted_at = row['deleted_at']
        transaction_id = row['transaction_id']
        try:
            dt = datetime.datetime.strptime(due, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = datetime.datetime.strptime('1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
        due_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        dow = Static.dow(dt.replace(tzinfo=datetime.timezone.utc).weekday())
        due_date = dt.strftime('%m/%d {}').format(dow)
        try:
            dt = datetime.datetime.strptime(NOW, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = datetime.datetime.strptime('1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")

        now_strtotime = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        invoice_status = row['status']
        selected = True if invoice_id == check_invoice_id else False
        if deleted_at:
            state = 4
        else:
            if invoice_status is 5:
                state = 5
            elif invoice_status is 4:
                state = 4
            elif invoice_status is 3:
                state = 4
            elif invoice_status is 2:
                state = 3
            else:
                if due_strtotime < now_strtotime:  # overdue
                    state = 2
                elif count_invoice_items == 0:  # #quick drop
                    state = 6
                else:
                    state = 1

        if state is 1:
            text_color = [0.898, 0.898, 0.898, 1] if selected else [0, 0, 0, 1]
            background_rgba = [0.369, 0.369, 0.369, 0.1] if selected else [0.826, 0.826, 0.826, 0.1]
            background_color = [0.369, 0.369, 0.369, 1] if selected else [0.826, 0.826, 0.826, 1]
        elif state is 2:
            text_color = [0.8157, 0.847, 0.961, 1] if selected else [0.059, 0.278, 1, 1]
            background_rgba = [0.059, 0.278, 1, 0.1] if selected else [0.816, 0.847, 0.961, 0.1]
            background_color = [0.059, 0.278, 1, 1] if selected else [0.816, 0.847, 0.961, 1]
        elif state is 3:
            text_color = [0.847, 0.967, 0.847, 1] if selected else [0, 0.639, 0.149, 1]
            background_rgba = [0, 0.64, 0.149, 0.1] if selected else [0.847, 0.968, 0.847, 0.1]
            background_color = [0, 0.64, 0.149, 1] if selected else [0.847, 0.968, 0.847, 1]
        elif state is 4:
            text_color = [1, 0.8, 0.8, 1] if selected else [1, 0, 0, 1]
            background_rgba = [1, 0, 0, 0.1] if selected else [1, 0.717, 0.717, 0.1]
            background_color = [1, 0, 0, 1] if selected else [1, 0.717, 0.717, 1]
        elif state is 5:
            text_color = [0.898, 0.898, 0.898, 1] if selected else [0, 0, 0, 1]
            background_rgba = [0.369, 0.369, 0.369, 0.1] if selected else [0.826, 0.826, 0.826, 0.1]
            background_color = [0.369, 0.369, 0.369, 1] if selected else [0.826, 0.826, 0.826, 1]
        else:
            text_color = [0, 0, 0, 1] if selected else [0, 0, 0, 1]
            background_rgba = [0.98431373, 1, 0, 0.1] if selected else [0.9960784314, 1, 0.7176470588, 1]
            background_color = [0.98431373, 1, 0, 1] if selected else [0.9960784314, 1, 0.7176470588, 1]
        tr = Factory.InvoiceTr(on_press=partial(self.select_invoice, invoice_id),
                               group="tr")
        tr.status = state
        tr.set_color = background_color
        tr.background_color = background_rgba
        label_1 = Label(markup=True,
                        color=text_color,
                        text="{}".format('{0:06d}'.format(invoice_id)))
        tr.ids.invoice_table_row_td.add_widget(label_1)
        label_2 = Label(markup=True,
                        color=text_color,
                        text='{}'.format(company_id))
        tr.ids.invoice_table_row_td.add_widget(label_2)
        label_3 = Label(markup=True,
                        color=text_color,
                        text='{}'.format(due_date))
        tr.ids.invoice_table_row_td.add_widget(label_3)
        label_4 = Label(markup=True,
                        color=text_color,
                        text='{}'.format(rack))
        tr.ids.invoice_table_row_td.add_widget(label_4)
        label_5 = Label(markup=True,
                        color=text_color,
                        text='{}'.format(quantity))
        tr.ids.invoice_table_row_td.add_widget(label_5)
        label_6 = Label(markup=True,
                        color=text_color,
                        text='{}'.format(total))
        tr.ids.invoice_table_row_td.add_widget(label_6)

        self.invoice_table_body.add_widget(tr)

        return True

    def reprint(self):
        pass

    def undo(self):
        pass

    def set_result_status(self):
        sessions.put('_searchResultsStatus', value= True)
        # update db with current changes

    def select_invoice(self, invoice_id, *args, **kwargs):
        # set selected invoice and update the table to show it
        sessions.put('_invoiceId',value= invoice_id)

        # check state of button and update rows
        for child in self.invoice_table_body.children:
            if child.state is 'down':
                # find status and change the background color

                if child.status is 1:
                    text_color = [0.898, 0.898, 0.898, 1]
                    child.background_color = [0.369, 0.369, 0.369, 0.1]
                    child.set_color = [0.369, 0.369, 0.369, 1]
                elif child.status is 2:
                    text_color = [0.8156, 0.847, 0.961, 1]
                    child.background_color = [0.059, 0.278, 1, 0.1]
                    child.set_color = [0.059, 0.278, 1, 1]
                elif child.status is 3:
                    text_color = [0.847, 0.969, 0.847, 1]
                    child.background_color = [0, 0.64, 0.149, 0.1]
                    child.set_color = [0, 0.64, 0.149, 1]
                elif child.status is 4:
                    text_color = [1, 0.8, 0.8, 1]
                    child.background_color = [1, 0, 0, 0.1]
                    child.set_color = [1, 0, 0, 1]
                elif child.status is 5:
                    text_color = [0.898, 0.898, 0.898, 1]
                    child.background_color = [0.369, 0.369, 0.369, 0.1]
                    child.set_color = [0.369, 0.369, 0.369, 1]
                else:
                    text_color = [0, 0, 0, 1]
                    child.background_color = [0.98431373, 1, 0, 0.1]
                    child.set_color = [0.98431373, 1, 0, 1]
            else:
                if child.status is 1:
                    text_color = [0, 0, 0, 1]
                    child.background_color = [0.826, 0.826, 0.826, 0.1]
                    child.set_color = [0.826, 0.826, 0.826, 1]
                elif child.status is 2:
                    text_color = [0.059, 0.278, 1, 1]
                    child.background_color = [0.816, 0.847, 0.961, 0.1]
                    child.set_color = [0.816, 0.847, 0.961, 1]
                elif child.status is 3:
                    text_color = [0, 0.639, 0.149, 1]
                    child.background_color = [0.847, 0.968, 0.847, 0.1]
                    child.set_color = [0.847, 0.968, 0.847, 1]
                elif child.status is 4:
                    text_color = [1, 0, 0, 1]
                    child.background_color = [1, 0.717, 0.717, 0.1]
                    child.set_color = [1, 0.717, 0.717, 1]
                elif child.status is 5:
                    text_color = [0, 0, 0, 1]
                    child.background_color = [0.826, 0.826, 0.826, 0.1]
                    child.set_color = [0.826, 0.826, 0.826, 1]
                else:
                    text_color = [0, 0, 0, 1]
                    child.background_color = [0.9960784314, 1, 0.7176470588, 0.1]
                    child.set_color = [0.9960784314, 1, 0.7176470588, 1]
            for grandchild in child.children:
                for ggc in grandchild.children:
                    ggc.color = text_color
        # self.reset()
        t1 = Thread(target=self.items_table_update)
        t1.start()

        # self.items_table_update()

    def invoice_next(self):
        self.row_set += self.row_increment
        self.down_btn.disabled = True if (self.row_set + 10) > sessions.get('_rowCap')['value'] else False

        t1 = Thread(target=self.reset)
        t1.start()
        # self.reset()
        self.up_btn.disabled = True if self.row_set <= 0 else False

    def invoice_prev(self):
        row_prev = self.row_set - self.row_increment
        self.up_btn.disabled = True if self.row_set - self.row_increment <= 0 else False

        self.row_set = 0 if self.row_set - self.row_increment <= 0 else row_prev


        t1 = Thread(target=self.reset)
        t1.start()
        self.down_btn.disabled = False if self.row_set < sessions.get('_rowCap')['value'] else True

    def items_table_update(self):
        self.items_table.clear_widgets()

        invoices = SYNC.invoice_grab_id(sessions.get('_invoiceId')['value'])
        inv_items = []
        invoice_deleted = False
        if invoices is not False:
            invoice_deleted = True if invoices['deleted_at'] else False
            inv_items = invoices['invoice_items']

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

                itm_srch = SYNC.inventory_items_grab(item_id)
                item_name = itm_srch['name'] if itm_srch is not False else ''
                inventory_id = itm_srch['inventory_id'] if itm_srch is not False else None

                inventories = SYNC.inventory_grab(inventory_id)
                laundry = inventories['laundry'] if inventories is not False else 0

                items[item_id] = {
                    'id': invoice_item['id'],
                    'name': '{} ({})'.format(item_name, self.starch) if laundry else item_name,
                    'total': 0,
                    'quantity': 0,
                    'color': {},
                    'memo': []
                }
            # populate correct item totals
            if items:
                for key, value in items.items():
                    item_id = key
                    iinv_items = SYNC.invoice_item_discount_find_item_id(sessions.get('_invoiceId')['value'], item_id)
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
                    t1 = Thread(target=self.items_table.add_widget, args=[Builder.load_string(tr1)])
                    t2 = Thread(target=self.items_table.add_widget, args=[Builder.load_string(tr2)])
                    t3 = Thread(target=self.items_table.add_widget, args=[Builder.load_string(tr3)])
                    t1.start()
                    t2.start()
                    t3.start()
                    # self.items_table.add_widget(Builder.load_string(tr1))
                    # self.items_table.add_widget(Builder.load_string(tr2))
                    # self.items_table.add_widget(Builder.load_string(tr3))

    def item_details(self, item_id):
        sessions.put('_itemId',value= item_id)

    def delete_invoice_confirm(self):
        self.history_popup = Popup()
        self.history_popup.auto_dismiss = False
        self.history_popup.title = 'Delete Confirmation'
        self.history_popup.size_hint = (None, None)
        self.history_popup.size = ('800sp', '400sp')
        invoice_id = sessions.get('_invoiceId')['value']
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
        if sessions.get('_invoiceId')['value']:
            inv = Invoice()
            invoices = SYNC.invoice_grab_id(sessions.get('_invoiceId')['value'])
            if invoices:
                invoice_delete = SYNC.delete_invoice(sessions.get('_invoiceId')['value'])
                if invoice_delete is not False:
                    print('invoice deleted on server')

            msg = KV.popup_alert(msg="Successfully deleted invoice #{}!".format(sessions.get('_invoiceId')['value']))
        else:
            msg = KV.popup_alert(msg="Could not locate the invoice_id. Please try again.")
            pass

        popup.content = Builder.load_string(msg)
        popup.open()
        self.history_popup.dismiss()
        self.reset()

    def undo_invoice_confirm(self):
        self.history_popup = Popup()
        self.history_popup.auto_dismiss = False
        self.history_popup.title = 'Undo Status Selection #{}'.format(sessions.get('_invoiceId')['value'])
        self.history_popup.size_hint = (None, None)
        self.history_popup.size = ('800sp', '400sp')
        invoice_id = sessions.get('_invoiceId')['value']
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
                                          values=('Not Ready', 'Racked', 'Prepaid', 'Gone Np', 'Picked Up'),
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
        print(self.status_spinner.text)
        if self.status_spinner.text == 'Not Ready':
            status = 1
        elif self.status_spinner.text == "Racked":
            status = 2
        elif self.status_spinner.text == "Prepaid":
            status = 3
        elif self.status_spinner.text == "Gone Np":
            status = 4
        else:  # picked up
            status = 5
        print(status)
        popup = Popup()
        popup.title = 'Undo Invoice'
        popup.size_hint = (None, None)
        popup.size = (600, 400)
        if sessions.get('_invoiceId')['value']:
            if status > 0:
                inv = Invoice()
                invoices = SYNC.invoice_grab_id_with_trashed(sessions.get('_invoiceId')['value'])
                if invoices:
                    for invoice in invoices:
                        inv.id = invoice['id']
                        original_status = invoice['status']
                        transaction_id = invoice['transaction_id']
                        if status < 5 and original_status is 5 and transaction_id:  # remove transaction_id and delete
                            # get all invoices with the same transaction_id
                            all_invoices = SYNC.invoice_query_transaction_id(transaction_id)
                            if all_invoices:
                                for ainv in all_invoices:
                                    SYNC.remove_invoice_by_transaction(ainv['id'], status)

                            transactions = Transaction()
                            trans = SYNC.transaction_grab(transaction_id)
                            if trans:
                                tr_id = trans['id']
                                transactions.id = tr_id
                                transactions.delete()

                        SYNC.restore_invoice(invoice['id'], status)

                msg = KV.popup_alert(msg="Successfully updated invoice #{}!".format(sessions.get('_invoiceId')['value']))
                # sync the database
            else:
                msg = KV.popup_alert(msg="Please select a valid status.")

        else:
            msg = KV.popup_alert(msg="Could not locate the invoice_id. Please try again.")

        popup.content = Builder.load_string(msg)
        popup.open()
        self.history_popup.dismiss()
        self.reset()

    def reprint_popup(self):
        popup = Popup()
        popup.title = 'Reprint Invoice #{}'.format(sessions.get('_invoiceId')['value'])
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.9))
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
                                         on_press=popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def reprint_invoice(self, type, *args, **kwargs):
        if sessions.get('_invoiceId')['value']:
            # print invoices
            if EPSON:
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

                invoices = Invoice()
                invoice = SYNC.invoice_grab_id(sessions.get('_invoiceId')['value'])
                invoice_discount_id = None
                inv_items = []
                if invoice:
                    invoice_quantity = invoice['quantity']
                    invoice_discount_id = invoice['discount_id']
                    invoice_subtotal = invoice['pretax']
                    invoice_tax = invoice['tax']
                    invoice_total = invoice['total']
                    invoice_due_date = datetime.datetime.strptime(invoice['due_date'], "%Y-%m-%d %H:%M:%S")
                    inv_items = invoice['invoice_items']
                discount_amount = 0
                if invoice_discount_id is not None:
                    discounts = Discount()
                    discs = SYNC.discount_grab(invoice_discount_id)
                    if discs:
                        discount_rate = discs['rate']
                        discount_price = discs['discount']
                        discount_type = discs['type']
                        if discount_type is 1:
                            discount_amount = (invoice_subtotal * discount_rate)
                        else:
                            discount_amount = invoice_subtotal - discount_price

                discount_amount = Static.us_dollar(discount_amount)

                print_sync_invoice = {sessions.get('_invoiceId')['value']: {}}
                if inv_items:
                    colors = {}
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
                    EPSON.write(pr.pcmd('TXT_ALIGN_CT'))
                    EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                    density=5, invert=False, smooth=False, flip=False))
                    EPSON.write("::CUSTOMER::\n")
                    EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                    invert=False, smooth=False, flip=False))
                    EPSON.write("{}\n".format(companies.name))
                    EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                    invert=False, smooth=False, flip=False))
                    EPSON.write("{}\n".format(companies.street))
                    EPSON.write("{}, {} {}\n".format(companies.city, companies.state, companies.zip))
                    EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                    invert=False, smooth=False, flip=False))

                    EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
                    EPSON.write("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))
                    EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2, density=5,
                                    invert=False, smooth=False, flip=False))
                    EPSON.write("READY BY: {}\n\n".format(invoice_due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                    EPSON.write(
                        pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                    invert=False, smooth=False, flip=False))
                    padded_customer_id = '{0:05d}'.format(sessions.get('_customerId')['value'])
                    EPSON.write("{}\n".format(padded_customer_id))

                    # Print barcode
                    EPSON.write(pr.pcmd_barcode(str(padded_customer_id)))

                    EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3, density=6,
                                    invert=False, smooth=False, flip=False))
                    EPSON.write('{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                    EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=2,
                                    invert=False, smooth=False, flip=False))
                    EPSON.write("{}\n".format(Job.make_us_phone(customers.phone)))
                    EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                    invert=False, smooth=False, flip=False))
                    EPSON.write('-----------------------------------------\n')

                    if sessions.get('_invoiceId')['value'] in print_sync_invoice:
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
                            EPSON.write('{} {}   {}\n'.format(item_type, item_qty, item_name))

                            if len(item_memo) > 0:
                                EPSON.write(pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                             height=1,
                                                             density=5, invert=False, smooth=False, flip=False))
                                EPSON.write('     {}\n'.format('/ '.join(item_memo)))
                            if len(item_color_string) > 0:
                                EPSON.write(pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                             height=1,
                                                             density=5, invert=False, smooth=False, flip=False))
                                EPSON.write('     {}\n'.format(', '.join(item_color_string)))

                    EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                    invert=False, smooth=False, flip=False))
                    EPSON.write('-----------------------------------------\n')
                    EPSON.write(
                        pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                    invert=False, smooth=False, flip=False))
                    EPSON.write('{} PCS\n'.format(invoice_quantity))
                    EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=1,
                                    invert=False, smooth=False, flip=False))
                    EPSON.write('-----------------------------------------\n')

                    if customers.invoice_memo:
                        EPSON.write(
                            pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                        invert=False, smooth=False, flip=False))
                        EPSON.write('{}\n'.format(customers.invoice_memo))
                    # Cut paper
                    EPSON.write('\n\n\n\n\n\n')
                    EPSON.write(pr.pcmd('PARTIAL_CUT'))

                if type == 1:
                    # Print store copies
                    if print_sync_invoice:  # if invoices synced
                        for invoice_id, item_id in print_sync_invoice.items():

                            # start invoice
                            EPSON.write(pr.pcmd('TXT_ALIGN_CT'))
                            EPSON.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=5,
                                            invert=False, smooth=False, flip=False))
                            EPSON.write("::COPY::\n")
                            EPSON.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=1, height=2, density=5,
                                            invert=False, smooth=False, flip=False))
                            EPSON.write("{}\n".format(companies.name))
                            EPSON.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=5,
                                            invert=False, smooth=False, flip=False))
                            EPSON.write("{}\n".format(Job.make_us_phone(companies.phone)))
                            EPSON.write("{}\n\n".format(now.strftime('%a %m/%d/%Y %I:%M %p')))
                            EPSON.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'NORMAL', width=1, height=2,
                                            density=5,
                                            invert=False, smooth=False, flip=False))
                            EPSON.write(
                                "READY BY: {}\n\n".format(invoice_due_date.strftime('%a %m/%d/%Y %I:%M %p')))

                            EPSON.write(
                                pr.pcmd_set(align=u'CENTER', font=u'A', text_type=u'B', width=4, height=4, density=5,
                                            invert=False, smooth=False, flip=False))
                            EPSON.write("{}\n".format('{0:06d}'.format(invoice_id)))
                            # Print barcode
                            EPSON.write(pr.pcmd_barcode('{}'.format('{0:06d}'.format(invoice_id))))

                            EPSON.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=2, height=3,
                                            density=6,
                                            invert=False, smooth=False, flip=False))
                            EPSON.write(
                                '{}, {}\n'.format(customers.last_name.upper(), customers.first_name))

                            EPSON.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=2,
                                            invert=False, smooth=False, flip=False))
                            EPSON.write("{}\n".format(Job.make_us_phone(customers.phone)))
                            EPSON.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=1,
                                            invert=False, smooth=False, flip=False))
                            EPSON.write('-----------------------------------------\n')

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
                                    EPSON.write('{} {}   {}{}{}\n'.format(item_type,
                                                                               item_qty,
                                                                               item_name,
                                                                               ' ' * string_offset,
                                                                               Static.us_dollar(item_price)))

                                    if len(item_memo) > 0:
                                        EPSON.write(
                                            pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                        height=1,
                                                        density=5, invert=False, smooth=False, flip=False))
                                        EPSON.write('     {}\n'.format('/ '.join(item_memo)))
                                    if len(item_color_string) > 0:
                                        EPSON.write(
                                            pr.pcmd_set(align=u'LEFT', font=u'A', text_type=u'NORMAL', width=1,
                                                        height=1,
                                                        density=5, invert=False, smooth=False, flip=False))
                                        EPSON.write('     {}\n'.format(', '.join(item_color_string)))

                            EPSON.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=1,
                                            invert=False, smooth=False, flip=False))
                            EPSON.write('-----------------------------------------\n')
                            EPSON.write(
                                pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                            invert=False, smooth=False, flip=False))
                            EPSON.write('{} PCS\n'.format(invoice_quantity))
                            EPSON.write(
                                pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1,
                                            density=1,
                                            invert=False, smooth=False, flip=False))
                            EPSON.write('-----------------------------------------\n')
                            EPSON.write(
                                pr.pcmd_set(align=u"RIGHT", font=u'A', text_type=u'B', width=1, height=1, density=5,
                                            invert=False, smooth=False, flip=False))
                            EPSON.write('    SUBTOTAL:')
                            EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                            string_length = len(Static.us_dollar(invoice_subtotal))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            EPSON.write('{}{}\n'.format(' ' * string_offset, Static.us_dollar(invoice_subtotal)))
                            EPSON.write('    DISCOUNT:')
                            EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                            string_length = len(Static.us_dollar(discount_amount))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            EPSON.write('{}({})\n'.format(' ' * string_offset, Static.us_dollar(discount_amount)))
                            EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                            EPSON.write('         TAX:')
                            string_length = len(Static.us_dollar(invoice_tax))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                            EPSON.write('{}{}\n'.format(' ' * string_offset, Static.us_dollar(invoice_tax)))
                            EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                            EPSON.write('       TOTAL:')
                            EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'NORMAL'))
                            string_length = len(Static.us_dollar(invoice_total))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            EPSON.write('{}{}\n'.format(' ' * string_offset,
                                                             Static.us_dollar(invoice_total)))
                            EPSON.write(pr.pcmd_set(align=u"RIGHT", text_type=u'B'))
                            EPSON.write('     BALANCE:')
                            string_length = len(Static.us_dollar(invoice_total))
                            string_offset = 20 - string_length if 20 - string_length >= 0 else 1
                            EPSON.write('{}{}\n\n'.format(' ' * string_offset, Static.us_dollar(invoice_total)))
                            if customers.invoice_memo:
                                EPSON.write(
                                    pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'B', width=1, height=3, density=5,
                                                invert=False, smooth=False, flip=False))
                                EPSON.write('{}\n'.format(customers.invoice_memo))
                            if item_type == 'L':
                                # get customer mark
                                marks = Custid()
                                marks = SYNC.marks_query(sessions.get('_customerId')['value'], 1)
                                if marks is not False:
                                    m_list = []
                                    for mark in marks:
                                        m_list.append(mark['mark'])
                                    EPSON.write(
                                        pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'B', width=3, height=4,
                                                    density=8, invert=False, smooth=False, flip=False))
                                    EPSON.write('{}\n\n'.format(', '.join(m_list)))

                            # Cut paper
                            EPSON.write('\n\n\n\n\n\n')
                            EPSON.write(pr.pcmd('PARTIAL_CUT'))

            else:
                Popups.dialog_msg('Printer Error', 'No printer found. Please try again.')

        else:
            Popups.dialog_msg('Reprint Error', 'Please select an invoice.')

    def reprint_tags(self, *args, **kwargs):
        popup = Popup()
        popup.title = 'Tag Reprint'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='vertical',
                                   size_hint=(1, 0.9))
        self.tags_grid = Factory.TagsGrid()
        invoices = SYNC.invoice_grab_id(sessions.get('_invoiceId')['value'])
        if invoices is not False:
            invitems = invoices['invoice_items']

            if invitems:
                for ii in invitems:
                    invoice_items_id = ii['id']
                    iitem_id = ii['item_id']
                    tags_to_print = InventoryItem().tagsToPrint(iitem_id)
                    item_name = InventoryItem().getItemName(iitem_id)
                    item_color = ii['color']
                    item_memo = ii['memo']
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
                    self.tags_grid.ids.tags_table.add_widget(trtd1)
                    self.tags_grid.ids.tags_table.add_widget(trtd2)
                    self.tags_grid.ids.tags_table.add_widget(trtd3)
                    self.tags_grid.ids.tags_table.add_widget(trtd4)
                    self.tags_grid.ids.tags_table.add_widget(trtd5)
        inner_layout_1.add_widget(self.tags_grid)
        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.1))
        cancel_button = Button(text="Cancel",
                               on_press=popup.dismiss)
        print_all_button = Button(text="Print All",
                                  on_release=popup.dismiss,
                                  on_press=self.print_all_tags)
        print_selected_button = Button(text="Print Selected",
                                       on_release=popup.dismiss,
                                       on_press=self.print_selected_tags)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(print_all_button)
        inner_layout_2.add_widget(print_selected_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def select_tag(self, item_id, *args, **kwargs):

        if item_id in self.selected_tags_list:
            # remove the tag
            self.selected_tags_list.remove(item_id)
        else:
            # add the tag
            self.selected_tags_list.append(item_id)

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

            invitems = invoices['invoice_items']
            if len(invitems) > 0:
                for ii in invitems:
                    invoice_items_id = ii['id']
                    iitem_id = ii['item_id']
                    tags_to_print = InventoryItem().tagsToPrint(iitem_id)
                    item_name = InventoryItem().getItemName(iitem_id)
                    item_color = ii['color']
                    item_memo = ii['memo']
                    if invoice_items_id in self.selected_tags_list:
                        trtd1 = Factory.TagsSelectedButton(text=str(invoice_items_id),
                                                           on_press=partial(self.select_tag, invoice_items_id))
                        trtd2 = Factory.TagsSelectedButton(text=str(item_name),
                                                           on_press=partial(self.select_tag, invoice_items_id))
                        trtd3 = Factory.TagsSelectedButton(text=str(item_color),
                                                           on_press=partial(self.select_tag, invoice_items_id))
                        trtd4 = Factory.TagsSelectedButton(text=str(item_memo),
                                                           on_press=partial(self.select_tag, invoice_items_id))
                        trtd5 = Factory.TagsSelectedButton(text=str(tags_to_print),
                                                           on_press=partial(self.select_tag, invoice_items_id))
                    else:
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
                    self.tags_grid.ids.tags_table.add_widget(trtd1)
                    self.tags_grid.ids.tags_table.add_widget(trtd2)
                    self.tags_grid.ids.tags_table.add_widget(trtd3)
                    self.tags_grid.ids.tags_table.add_widget(trtd4)
                    self.tags_grid.ids.tags_table.add_widget(trtd5)

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
            if invs:
                dt = datetime.datetime.strptime(invs['due_date'], "%Y-%m-%d %H:%M:%S")
                due_date = dt.strftime('%a').upper()
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
            invoice_items = []
            if invs:
                invoice_items = invs['invoice_items']

            BIXOLON.write('\x1b\x40')
            BIXOLON.write('\x1b\x6d')
            laundry_to_print = []
            if len(invoice_items) > 0:

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

                            BIXOLON.write('\x1b!\x30')  # QUAD SIZE
                            BIXOLON.write('{}{}\n'.format(text_left, text_right))
                            BIXOLON.write('\x1b!\x00')
                            BIXOLON.write(name_number_string)
                            BIXOLON.write('\n')
                            BIXOLON.write('{0:06d}'.format(int(invoice_item_id)))
                            BIXOLON.write(' {} {}'.format(item_name, item_color))
                            if memo_string:
                                BIXOLON.write('\n{}'.format(memo_string))
                                memo_len = '\n\n\n' if len(
                                    memo_string) <= 32 else '\n\n\n' + '\n' * int(
                                    (len(memo_string)) / 32)
                                BIXOLON.write(memo_len)
                                BIXOLON.write('\x1b\x6d')
                            else:
                                BIXOLON.write('\n\n\n')
                                BIXOLON.write('\x1b\x6d')
                # FINAL CUT
                BIXOLON.write('\n\n\n\n\n\n')
                BIXOLON.write('\x1b\x6d')

            if len(laundry_to_print) > 0:
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

                    BIXOLON.write('\x1b!\x30')  # QUAD SIZE
                    BIXOLON.write(mark_mark_string)
                    BIXOLON.write('\n')
                    BIXOLON.write('\x1b!\x00')
                    BIXOLON.write(name_name_string)
                    BIXOLON.write('\n')
                    BIXOLON.write(id_id_string)

                    BIXOLON.write('\n\n\n\x1b\x6d')

                # FINAL CUT
                BIXOLON.write('\n\n\n\n\n\n')
                BIXOLON.write('\x1b\x6d')


        else:
            Popups.dialog_msg('Reprint Error', 'Please select an invoice.')
        pass

    def print_selected_tags(self, *args, **kwargs):
        print(self.selected_tags_list)
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
            if invs:
                dt = datetime.datetime.strptime(invs['due_date'], "%Y-%m-%d %H:%M:%S")
                due_date = dt.strftime('%a').upper()

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
            if BIXOLON:
                BIXOLON.write('\x1b\x40')
                BIXOLON.write('\x1b\x6d')
                laundry_to_print = []
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

                                BIXOLON.write('\x1b!\x30')  # QUAD SIZE
                                BIXOLON.write('{}{}\n'.format(text_left, text_right))
                                BIXOLON.write('\x1b!\x00')
                                BIXOLON.write(name_number_string)
                                BIXOLON.write('\n')
                                BIXOLON.write('{0:06d}'.format(int(invoice_item_id)))
                                BIXOLON.write(' {} {}'.format(item_name, item_color))
                                if memo_string:
                                    BIXOLON.write('\n{}'.format(memo_string))
                                    memo_len = '\n\n\n' if len(
                                        memo_string) <= 32 else '\n\n\n' + '\n' * int(
                                        (len(memo_string)) / 32)
                                    BIXOLON.write(memo_len)
                                    BIXOLON.write('\x1b\x6d')

                                else:

                                    BIXOLON.write('\n\n\n')
                                    BIXOLON.write('\x1b\x6d')
            if len(laundry_to_print) is 0:
                # FINAL CUT
                BIXOLON.write('\n\n\n\n\n\n')
                BIXOLON.write('\x1b\x6d')

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

                    BIXOLON.write('\x1b!\x30')  # QUAD SIZE
                    BIXOLON.write(mark_mark_string)
                    BIXOLON.write('\n')
                    BIXOLON.write('\x1b!\x00')
                    BIXOLON.write(name_name_string)
                    BIXOLON.write('\n')
                    BIXOLON.write(id_id_string)

                    BIXOLON.write('\n\n\n\x1b\x6d')

                # FINAL CUT
                BIXOLON.write('\n\n\n\n\n\n')
                BIXOLON.write('\x1b\x6d')

        else:
            Popups.dialog_msg('Reprint Error', 'Please select an invoice item to print tag.')