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
    rack_table = ObjectProperty(None)
    racks = OrderedDict()
    parent_scroll = ObjectProperty(None)
    marked_invoice_number = None
    edited_rack = False

    def reset(self):
        # Pause sync scheduler

        self.racks = OrderedDict()
        self.rack_number.text = ''
        self.invoice_number.text = ''
        self.invoice_number.focus = True
        self.marked_invoice_number = None
        self.edited_rack = False
        self.update_rack_table()

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
        self.rack_table.clear_widgets()
        h1 = KV.invoice_tr(0, '#')
        h2 = KV.invoice_tr(0, 'Invoice #')
        h3 = KV.invoice_tr(0, 'Rack #')
        h4 = KV.invoice_tr(0, 'Action')
        self.rack_table.add_widget(Builder.load_string(h1))
        self.rack_table.add_widget(Builder.load_string(h2))
        self.rack_table.add_widget(Builder.load_string(h3))
        self.rack_table.add_widget(Builder.load_string(h4))
        if self.racks:
            idx = 0
            marked_tr4 = False
            for invoice_number, rack_number in self.racks.items():
                idx += 1
                if invoice_number == self.marked_invoice_number:
                    tr1 = Factory.CenteredHighlightedLabel(text='[color=000000]{}[/color]'.format(idx))
                    tr2 = Factory.CenteredHighlightedLabel(text='[color=000000]{}[/color]'.format(invoice_number))
                    tr3 = Factory.CenteredHighlightedLabel(
                        text='[color=000000]{}[/color]'.format(rack_number if rack_number else ''))
                    tr4 = Button(markup=True,
                                 text='Edit')
                    marked_tr4 = tr4
                else:
                    tr1 = Factory.CenteredLabel(text='[color=000000]{}[/color]'.format(idx))
                    tr2 = Factory.CenteredLabel(text='[color=000000]{}[/color]'.format(invoice_number))
                    tr3 = Factory.CenteredLabel(
                        text='[color=000000]{}[/color]'.format(rack_number if rack_number else ''))
                    tr4 = Button(markup=True,
                                 text='Edit')
                    marked_tr4 = False
                self.rack_table.add_widget(tr1)
                self.rack_table.add_widget(tr2)
                self.rack_table.add_widget(tr3)
                self.rack_table.add_widget(tr4)
            if marked_tr4:
                self.parent_scroll.scroll_to(marked_tr4)
            else:
                self.parent_scroll.scroll_to(tr4)

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