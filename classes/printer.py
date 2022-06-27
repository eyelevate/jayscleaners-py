from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ObjectProperty, partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from classes.popups import Popups
# from main import KV, vars, ERROR_COLOR, DEFAULT_COLOR
from models.printers import Printer
from models.kv_generator import KvString
from models.sessions import sessions
ERROR_COLOR = 0.94, 0.33, 0.33, 1
DEFAULT_COLOR = 0.5, 0.5, 0.5, 1.0
KV = KvString()


class PrinterScreen(Screen):
    printer_name = ObjectProperty(None)
    printer_model_number = ObjectProperty(None)
    printer_nick_name = ObjectProperty(None)
    printer_vendor = ObjectProperty(None)
    printer_product = ObjectProperty(None)
    printer_type = ObjectProperty(None)
    printer_table = ObjectProperty(None)
    r1c2 = ObjectProperty(None)
    r2c2 = ObjectProperty(None)
    r3c2 = ObjectProperty(None)
    r4c2 = ObjectProperty(None)
    r5c2 = ObjectProperty(None)
    r6c2 = ObjectProperty(None)
    edit_popup = Popup()
    validated = 0
    edit_printer_id = None

    def reset(self):
        # Pause Schedule

        self.printer_name.text = ''
        self.printer_model_number.text = ''
        self.printer_nick_name.text = ''
        self.printer_vendor.text = ''
        self.printer_product.text = ''
        self.printer_type.text = ''
        self.printer_table.clear_widgets()
        self.validated = 0

        self.update_printer_table()
        self.edit_printer_id = None

    def update_printer_table(self):
        h1 = KV.sized_invoice_tr(0, '[color=000000][b]#[/b][/color]', 0.1)
        h2 = KV.sized_invoice_tr(0, '[color=000000][b]Name[/b][/color]', 0.7)
        h3 = KV.sized_invoice_tr(0, '[color=000000][b]Type[/b][/color]', 0.2)

        self.printer_table.add_widget(Builder.load_string(h1))
        self.printer_table.add_widget(Builder.load_string(h2))
        self.printer_table.add_widget(Builder.load_string(h3))

        # update saved printers
        printers = Printer()
        prs = printers.where({'company_id': sessions.get('_companyId')['value']})
        if prs:
            idx = 0
            for printer in prs:
                printer_id = printer['id']
                idx += 1
                col1 = Button(markup=True,
                              size_hint_x=0.1,
                              size_hint_y=None,
                              text='[color=ffffff]{}[/color]'.format(idx),
                              on_press=partial(self.edit_printer_popup, printer_id))
                col2 = Button(markup=True,
                              size_hint_x=0.7,
                              size_hint_y=None,
                              text='[color=ffffff]{}[/color]'.format(printer['name']),
                              on_press=partial(self.edit_printer_popup, printer_id))
                col3 = Button(markup=True,
                              size_hint_x=0.2,
                              size_hint_y=None,
                              text='[color=ffffff]{}[/color]'.format(printer['type']),
                              on_press=partial(self.edit_printer_popup, printer_id))
                self.printer_table.add_widget(col1)
                self.printer_table.add_widget(col2)
                self.printer_table.add_widget(col3)

    def edit_printer_popup(self, id, *args, **kwargs):
        self.edit_printer_id = id
        self.edit_popup = Popup()
        self.edit_popup.title = 'Edit Printer'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='vertical',
                                   size_hint=(1, 0.9))
        edit_table = GridLayout(cols=2,
                                rows=7,
                                row_force_default=True,
                                row_default_height='50sp',
                                spacing='2sp')
        printers = Printer()
        prs = printers.where({'id': id})
        if prs:
            for printer in prs:
                r1c1 = Factory.CenteredFormLabel(text='Name:')
                self.r1c2 = Factory.CenterVerticalTextInput(padding='10cp',
                                                            text='{}'.format(printer['name']))
                edit_table.add_widget(r1c1)
                edit_table.add_widget(self.r1c2)
                r2c1 = Factory.CenteredFormLabel(text='Model #:')
                self.r2c2 = Factory.CenterVerticalTextInput(padding='10cp',
                                                            text='{}'.format(printer['model']))
                edit_table.add_widget(r2c1)
                edit_table.add_widget(self.r2c2)
                r3c1 = Factory.CenteredFormLabel(text=' Nick Name:')
                self.r3c2 = Factory.CenterVerticalTextInput(padding='10cp',
                                                            text='{}'.format(printer['nick_name']))
                edit_table.add_widget(r3c1)
                edit_table.add_widget(self.r3c2)
                r4c1 = Factory.CenteredFormLabel(text=' Vendor ID:')
                self.r4c2 = Factory.CenterVerticalTextInput(padding='10cp',
                                                            text='{}'.format(printer['vendor_id']))
                edit_table.add_widget(r4c1)
                edit_table.add_widget(self.r4c2)
                r5c1 = Factory.CenteredFormLabel(text=' Product ID:')
                self.r5c2 = Factory.CenterVerticalTextInput(padding='10cp',
                                                            text='{}'.format(printer['product_id']))
                edit_table.add_widget(r5c1)
                edit_table.add_widget(self.r5c2)
                r6c1 = Factory.CenteredFormLabel(text=' Type:')
                self.r6c2 = Factory.CenterVerticalTextInput(padding='10cp',
                                                            text='{}'.format(printer['type']))
                edit_table.add_widget(r6c1)
                edit_table.add_widget(self.r6c2)
        inner_layout_1.add_widget(edit_table)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        cancel_button = Button(markup=True,
                               text="Cancel",
                               on_press=self.edit_popup.dismiss)
        edit_button = Button(markup=True,
                             text="Edit",
                             on_press=self.validate_edit)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(edit_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.edit_popup.content = layout
        self.edit_popup.open()

    def validate_edit(self, *args, **kwargs):
        self.validated = 0
        if self.r1c2.text == '':
            self.validated += 1
            self.r1c2.hint_text_color = ERROR_COLOR
            self.r1c2.hint_text = "Please enter a printer name"
        else:
            self.r1c2.hint_text_color = DEFAULT_COLOR
            self.r1c2.hint_text = ""

        if self.r2c2.text == '':
            self.validated += 1
            self.r2c2.hint_text_color = ERROR_COLOR
            self.r2c2.hint_text = "Please enter a model number"
        else:
            self.r2c2.hint_text_color = DEFAULT_COLOR
            self.r2c2.hint_text = ""

        if self.r3c2.text == '':
            self.validated += 1
            self.r3c2.hint_text_color = ERROR_COLOR
            self.r3c2.hint_text = "Please enter a printer nick name"
        else:
            self.r3c2.hint_text_color = DEFAULT_COLOR
            self.r3c2.hint_text = ""

        if self.r4c2.text == '':
            self.validated += 1
            self.r4c2.hint_text_color = ERROR_COLOR
            self.r4c2.hint_text = "Please enter a vendor id"
        else:
            self.r4c2.hint_text_color = DEFAULT_COLOR
            self.r4c2.hint_text = ""

        if self.r5c2.text == '':
            self.validated += 1
            self.r5c2.hint_text_color = ERROR_COLOR
            self.r5c2.hint_text = "Please enter a product id"
        else:

            self.r5c2.hint_text_color = DEFAULT_COLOR
            self.r5c2.hint_text = ""

        if self.r6c2.text == '':
            self.validated += 0  # todo
            self.r6c2.hint_text_color = ERROR_COLOR
            self.r6c2.hint_text = "Please enter a printer name"
        else:
            self.r6c2.hint_text_color = DEFAULT_COLOR
            self.r6c2.hint_text = ""

        if self.validated == 0:
            self.edit_printer()
            self.reset()
        else:
            self.reset()
            Popups.dialog_msg('Printer Setting', "There are some errors with your printer edit form! Please review and try again.")

    def validate(self):
        self.validated = 0
        if self.printer_name.text == '':
            self.validated += 1
            self.printer_name.hint_text_color = ERROR_COLOR
            self.printer_name.hint_text = "Please enter a printer name"
        else:
            self.printer_name.hint_text_color = DEFAULT_COLOR
            self.printer_name.hint_text = ""

        if self.printer_model_number.text == '':
            self.validated += 1
            self.printer_model_number.hint_text_color = ERROR_COLOR
            self.printer_model_number.hint_text = "Please enter a model number"
        else:
            self.printer_model_number.hint_text_color = DEFAULT_COLOR
            self.printer_model_number.hint_text = ""

        if self.printer_nick_name.text == '':
            self.validated += 1
            self.printer_nick_name.hint_text_color = ERROR_COLOR
            self.printer_nick_name.hint_text = "Please enter a printer nick name"
        else:
            self.printer_nick_name.hint_text_color = DEFAULT_COLOR
            self.printer_nick_name.hint_text = ""

        if self.printer_vendor.text == '':
            self.validated += 1
            self.printer_vendor.hint_text_color = ERROR_COLOR
            self.printer_vendor.hint_text = "Please enter a vendor id"
        else:
            self.printer_vendor.hint_text_color = DEFAULT_COLOR
            self.printer_vendor.hint_text = ""

        if self.printer_product.text == '':
            self.validated += 1
            self.printer_product.hint_text_color = ERROR_COLOR
            self.printer_product.hint_text = "Please enter a product id"
        else:

            self.printer_product.hint_text_color = DEFAULT_COLOR
            self.printer_product.hint_text = ""

        if self.printer_type.text == '':
            self.validated += 0  # todo
            self.printer_type.hint_text_color = ERROR_COLOR
            self.printer_type.hint_text = "Please enter a printer name"
        else:
            self.printer_type.hint_text_color = DEFAULT_COLOR
            self.printer_type.hint_text = ""

        if self.validated == 0:
            self.add_printer()
            self.reset()
        else:
            self.reset()
            Popups.modal_msg('Printer Setting', 'There are some errors with your printer form! Please review and try again.')

    def add_printer(self):
        printer = Printer()
        printer.company_id = sessions.get('_companyId')['value']
        printer.name = self.printer_name.text
        printer.model = self.printer_model_number.text
        printer.nick_name = self.printer_nick_name.text
        printer.vendor_id = self.printer_vendor.text
        printer.product_id = self.printer_product.text
        printer.type = self.printer_type.text
        printer.status = 1

        if printer.add():
            Popups.modal_msg('Printer Setting', 'Successfully added a printer.')

    def edit_printer(self):
        printer = Printer()
        print(self.edit_printer_id)
        printer.put(where={'id': self.edit_printer_id}, data={'name': self.r1c2.text,
                                                              'model': self.r2c2.text,
                                                              'nick_name': self.r3c2.text,
                                                              'vendor_id': self.r4c2.text,
                                                              'product_id': self.r5c2.text,
                                                              'type': self.r6c2.text})

        # set invoice_items data to save
        Popups.modal_msg('Printer Setting', "Successfully edited printer - {}!".format(self.r1c2.text))
        self.edit_popup.dismiss()