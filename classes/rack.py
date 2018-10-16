import datetime
from collections.__init__ import OrderedDict

from escpos.exceptions import USBNotFoundError
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from classes.popups import Popups
from models.invoices import Invoice
from models.printers import Printer
from models.sync import Sync
from models.kv_generator import KvString
from models.sessions import sessions
from pubsub import pub
KV = KvString()
SYNC_POPUP = Popup()
SYNC = Sync()
EPSON = sessions.get('_epson')['value']


class RackScreen(Screen):
    invoice_number = ObjectProperty(None)
    rack_number = ObjectProperty(None)
    racks = OrderedDict()
    marked_invoice_number = None
    edited_rack = False
    rack_table_rv = ObjectProperty(None)
    rack_rows = []

    def reset(self):
        # Pause sync scheduler

        self.racks = OrderedDict()
        self.rack_number.text = ''
        self.invoice_number.text = ''
        self.invoice_number.focus = True
        self.marked_invoice_number = None
        self.edited_rack = False
        self.rack_table_rv.data = []
        self.update_rack_table()
        self.rack_rows = []

    def open_popup(self, *args, **kwargs):
        SYNC_POPUP.title = "Sync In Progress"
        content = KV.popup_alert("Please wait while we sync the database.")
        SYNC_POPUP.content = Builder.load_string(content)
        SYNC_POPUP.open()
        # send event
        pub.sendMessage('close_loading_popup', popup=SYNC_POPUP)

    def set_result_status(self):

        sessions.put('_searchResultsStatus', value= True)
        self.reset()

    def update_rack_table(self):
        self.rack_rows = []
        if self.racks:
            idx = 0
            for invoice_number, rack_number in self.racks.items():
                idx += 1
                selected = invoice_number == self.marked_invoice_number
                selected_color = 'ffffff' if selected else '000000'
                selected_background = '' if selected else [.90, .90, .90, 1]
                selected_rgba = [0.369, 0.369, 0.369, 1] if selected else [0.826, 0.826, 0.826, 1]
                self.rack_rows.append({
                    'text': '[color={}]{}[/color]'.format(selected_color,idx),
                    'column': 1,
                    'invoice_id': invoice_number,
                    'background_color': selected_rgba,
                    'background_normal':  selected_background
                })
                self.rack_rows.append({
                    'text': '[color={}]{}[/color]'.format(selected_color, '{0:06d}'.format(int(invoice_number))),
                    'column': 2,
                    'invoice_id': invoice_number,
                    'background_color': selected_rgba,
                    'background_normal':  selected_background
                })
                self.rack_rows.append({
                    'text': '[color={}]{}[/color]'.format(selected_color, rack_number if rack_number else ''),
                    'column': 3,
                    'invoice_id': invoice_number,
                    'background_color': selected_rgba,
                    'background_normal':  selected_background
                })
                self.rack_rows.append({
                    'text': '[color=ffffff]remove[/color]',
                    'column': 4,
                    'invoice_id': invoice_number,
                    'background_color': [1,0,0,1],
                    'background_normal': ''
                })

        self.rack_table_rv.data = self.rack_rows

    def set_invoice_number(self):
        invoices = Invoice()
        search = None if not self.invoice_number.text else self.invoice_number.text

        found_invoices = SYNC.invoice_grab_id(search)
        if not self.invoice_number.text:
            Popups.dialog_msg('Error: Rack process error','Invoice number cannot be left empty.')

        elif found_invoices is False:
            Popups.dialog_msg('Error: Rack process error', 'No such invoice number.')

        elif self.invoice_number.text in self.racks:
            self.edited_rack = self.racks[self.invoice_number.text]
            self.racks[self.invoice_number.text] = False
            self.rack_number.focus = True
        else:
            self.edited_rack = False
            self.racks[self.invoice_number.text] = False
            self.rack_number.focus = True
            self.marked_invoice_number = self.invoice_number.text

        self.update_rack_table()

    def set_rack_number(self):
        invoices = Invoice()
        now = datetime.datetime.now()
        rack_date = datetime.datetime.strftime(now, "%Y-%m-%d %H:%M:%S")
        if not self.invoice_number.text:
            Popups.dialog_msg(title_string='Error: Rack Process error', msg_string='Please provide an invoice number.')
        else:
            formatted_rack = self.rack_number.text.replace("%R", "")

            if EPSON:
                try:
                    pr = Printer()
                    EPSON.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=3,
                                    invert=False, smooth=False, flip=False))
                    if self.edited_rack:
                        EPSON.write('EDITED: {} - (OLD {}) -> (NEW {})\n'.format(
                            self.invoice_number.text,
                            self.edited_rack,
                            formatted_rack))
                        self.edited_rack = False
                    else:
                        EPSON.write('{} - {}\n'.format(self.invoice_number.text, formatted_rack))
                except USBNotFoundError:
                    Popups.dialog_msg('Error: usb not found',
                                    'Could not print rack number due to usb fault. However, rack has been successfully saved in the system. ')
            self.racks[self.invoice_number.text] = formatted_rack
            self.invoice_number.text = ''
            self.rack_number.text = ''
            self.update_rack_table()
            self.marked_invoice_number = self.invoice_number.text

        self.invoice_number.focus = True

    def save_racks(self):

        if len(self.racks) > 0:

            enter_rack = SYNC.rack_invoice(self.racks)
            if enter_rack is False:
                print('The following racks could not be saved. Please re-enter the racks')
                print(enter_rack)
            else:
                print('Successfully racked invoices')

            # Cut paper
            if EPSON:
                pr = Printer()
                EPSON.write(
                    pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))
                EPSON.write('{}'.format((datetime.datetime.now().strftime('%a %m/%d/%Y %I:%M %p'))))
                EPSON.write('\n\n\n\n\n\n')
                EPSON.write(pr.pcmd('PARTIAL_CUT'))
        # set user to go back to search screen
        if sessions.get('_customerId')['value']:
            self.set_result_status()

    def _remove_row(self, invoice_id):
        pass