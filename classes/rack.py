import datetime
import time
from collections.__init__ import OrderedDict

from escpos.exceptions import USBNotFoundError
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
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


class RackScreen(Screen):
    invoice_number = ObjectProperty(None)
    rack_number = ObjectProperty(None)
    racks = OrderedDict()
    marked_invoice_number = None
    edited_rack = False
    rack_table_rv = ObjectProperty(None)
    rack_rows = []
    remove_list = []
    epson = None


    def __init__(self, **kwargs):
        super(RackScreen, self).__init__(**kwargs)
        pub.subscribe(self.set_epson_printer, "set_epson_printer")

    def attach(self):
        pub.subscribe(self._edit_row, "edit_row")
        pub.subscribe(self._remove_row, 'remove_row')

    def detach(self):
        pub.unsubscribe(self._edit_row, "edit_row")
        pub.unsubscribe(self._remove_row, 'remove_row')

    def set_epson_printer(self, device):
        self.epson = device
        print(self.epson)

    def reset(self):
        # Pause sync scheduler

        self.racks = sessions.get('_racks')['value']
        self.rack_number.text = ''
        self.invoice_number.text = ''
        self.invoice_number.focus = True
        self.marked_invoice_number = sessions.get('_invoiceId')['value']
        self.edited_rack = False
        self.rack_table_rv.data = []
        self.rack_rows = []
        self.remove_list = []
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
        self.rack_rows = []
        if self.racks:
            idx = 0
            for invoice_number, rack_number in self.racks.items():
                idx += 1
                selected = invoice_number == self.marked_invoice_number
                selected_color = 'FFFFFF' if selected else '000000'
                selected_background = ''
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
        search = None if not self.invoice_number.text else self.invoice_number.text

        found_invoices = SYNC.invoice_grab_id(search)
        if not self.invoice_number.text:
            Popups.dialog_msg('Error: Rack process error','Invoice number cannot be left empty.')

        elif found_invoices is False:
            Popups.dialog_msg('Error: Rack process error', 'No such invoice number.')

        elif self.invoice_number.text in self.racks and found_invoices is False:
            self.edited_rack = self.racks[self.invoice_number.text]
            self.racks[self.invoice_number.text] = False
            self.rack_number.focus = True
        else:
            self.edited_rack = False
            self.racks[self.invoice_number.text] = False
            self.rack_number.focus = True
            self.marked_invoice_number = self.invoice_number.text
            if found_invoices['rack']:
                self.rack_number.text = found_invoices['rack']
                self.racks[self.invoice_number.text] = found_invoices['rack']
                self._hightlight_input('rack')

        sessions.put('racks', value=self.racks)
        self.update_rack_table()

    def set_rack_number(self):
        now = datetime.datetime.now()
        if not self.invoice_number.text:
            Popups.dialog_msg(title_string='Error: Rack Process error', msg_string='Please provide an invoice number.')
        else:
            formatted_rack = self.rack_number.text.replace("%R", "")

            if self.epson:
                try:
                    pr = Printer()
                    self.epson.write(
                        pr.pcmd_set(align=u"LEFT", font=u'A', text_type=u'NORMAL', width=1, height=1, density=3,
                                    invert=False, smooth=False, flip=False))
                    if self.edited_rack:
                        self.epson.write('EDITED: {} - (OLD {}) -> (NEW {})\n'.format(
                            self.invoice_number.text,
                            self.edited_rack,
                            formatted_rack))
                        self.edited_rack = False
                    else:
                        self.epson.write('{} - {}\n'.format(self.invoice_number.text, formatted_rack))
                except USBNotFoundError:
                    Popups.dialog_msg('Error: usb not found',
                                    'Could not print rack number due to usb fault. However, rack has been successfully saved in the system. ')
            self.racks[self.invoice_number.text] = formatted_rack
            sessions.put('racks', value=self.racks)
            self.invoice_number.text = ''
            self.rack_number.text = ''
            self.update_rack_table()
            self.marked_invoice_number = self.invoice_number.text

        self.invoice_number.focus = True

    def save_racks(self):
        # remove listed racks first before adding in
        if len(self.remove_list) > 0:
            remove_list = []
            # check if removed items are now added back in with racks if so then remove from this list
            for invoice_id in self.remove_list:
                if invoice_id not in self.racks:
                    remove_list.append(str(int(invoice_id)))
            # send remove list to be removed
            if remove_list:
                SYNC.remove_racks_from_list(remove_list)

        # update all racks according to list
        if len(self.racks) > 0:

            enter_rack = SYNC.rack_invoice(self.racks)
            if enter_rack is False:
                print('The following racks could not be saved. Please re-enter the racks')
                print(enter_rack)
            else:
                print('Successfully racked invoices')
                sessions.put('racks', value={})

            # Cut paper
            if self.epson:
                pr = Printer()
                self.epson.write(
                    pr.pcmd_set(align=u"CENTER", font=u'A', text_type=u'NORMAL', width=1, height=1, density=5,
                                invert=False, smooth=False, flip=False))
                self.epson.write('{}'.format((datetime.datetime.now().strftime('%a %m/%d/%Y %I:%M %p'))))
                self.epson.write('\n\n\n\n\n\n')
                self.epson.write(pr.pcmd('PARTIAL_CUT'))
        # set user to go back to search screen
        if sessions.get('_customerId')['value']:
            self.set_result_status()
            sessions.put('_racks', value=OrderedDict())

    def open_reset_popup(self, *args, **kwargs):
        popup = Popup()
        popup.size_hint = (None, None)
        popup.size = (800, 600)
        popup.title = 'Hard Reset Rack Session'
        layout = BoxLayout(orientation="vertical",
                           size_hint=(1, 1))
        inner_layout_1 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.7))
        text = Label(text="Are you sure you want to reset current session?\nDoing so will cause you to lose your current rack session.")

        inner_layout_1.add_widget(text)
        inner_layout_2 = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.3))
        cancel = Button(text="Cancel",
                        on_press=popup.dismiss)
        yes = Button(text="[color=32CD32][b]Yes, Hard Reset[/b][/color]",
                     markup=True,
                     on_press=self._hard_reset,
                     on_release=popup.dismiss)
        inner_layout_2.add_widget(cancel)
        inner_layout_2.add_widget(yes)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def _hard_reset(self, *args, **kwargs):
        sessions.put('_racks',value=OrderedDict())
        self.reset()

    def _edit_row(self, invoice_id):
        index = '{0:06d}'.format(int(invoice_id))
        self.marked_invoice_number = index
        self.invoice_number.text = index
        self.rack_number.text = self.racks[index]
        self._hightlight_input('invoice')
        self.update_rack_table()

    def _remove_row(self, invoice_id):
        index = '{0:06d}'.format(int(invoice_id))
        if index in self.racks:
            del self.racks[index]
            self.remove_list.append(index)
        sessions.put('racks',value=self.racks)
        self._reset_inputs()
        self.update_rack_table()

    def _hightlight_input(self, type):
        time.sleep(0.1)
        if (type == 'invoice'):
            self.invoice_number.focus = True
            self.invoice_number.select_all()
        else:
            self.rack_number.focus = True
            self.rack_number.select_all()


    def _reset_inputs(self):
        self.invoice_number.text = ''
        self.rack_number.text = ''
        self._hightlight_input('invoice')
