from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ObjectProperty, partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.spinner import Spinner

from classes.popups import Popups
from models.kv_generator import KvString
from models.sync import Sync
from models.inventories import Inventory
from models.sessions import sessions
KV = KvString()
SYNC = Sync()


class InventoriesScreen(Screen):
    inventory_table = ObjectProperty(None)
    inventory_name = ObjectProperty(None)
    inventory_desc = ObjectProperty(None)
    inventory_order = ObjectProperty(None)
    inventory_laundry = 0
    inventory_id = None
    edit_popup = Popup()
    add_popup = Popup()

    def reset(self):
        # Pause Schedule
        #
        self.inventory_id = None
        self.inventory_laundry = 0
        self.update_inventory_table()

    def update_inventory_table(self):
        self.inventory_table.clear_widgets()
        h1 = KV.sized_invoice_tr(0, 'ID', 0.1)
        h2 = KV.sized_invoice_tr(0, 'Name', 0.4)
        h3 = KV.sized_invoice_tr(0, 'Order', 0.1)
        h4 = KV.sized_invoice_tr(0, 'Laundry', 0.1)
        h5 = KV.sized_invoice_tr(0, 'Action', 0.1)
        h6 = KV.sized_invoice_tr(0, 'Move', 0.1)
        h7 = KV.sized_invoice_tr(0, 'Move', 0.1)
        self.inventory_table.add_widget(Builder.load_string(h1))
        self.inventory_table.add_widget(Builder.load_string(h2))
        self.inventory_table.add_widget(Builder.load_string(h3))
        self.inventory_table.add_widget(Builder.load_string(h4))
        self.inventory_table.add_widget(Builder.load_string(h5))
        self.inventory_table.add_widget(Builder.load_string(h6))
        self.inventory_table.add_widget(Builder.load_string(h7))

        inventories = SYNC.inventories_by_company(sessions.get('_companyId')['value'])
        if inventories is not False:
            for inventory in inventories:
                c1 = KV.sized_invoice_tr(1, inventory['id'], 0.1)
                c2 = KV.sized_invoice_tr(state=1,
                                         data='{}\\n{}'.format(inventory['name'], inventory['description']),
                                         size_hint_x=0.4,
                                         text_wrap=True)
                c3 = KV.sized_invoice_tr(1, inventory['ordered'], 0.1)
                c4 = KV.sized_invoice_tr(1, 'True' if inventory['laundry'] else 'False', 0.1)
                c5 = Button(text="Edit",
                            size_hint_x=0.1,
                            on_press=partial(self.edit_invoice_popup, inventory['id']))
                c6 = Factory.CenterGlyphUpButton(size_hint_x=0.1,
                                                 on_press=partial(self.inventory_move, 'up', inventory['id']))
                c7 = Factory.CenterGlyphDownButton(size_hint_x=0.1,
                                                   on_press=partial(self.inventory_move, 'down', inventory['id']))
                self.inventory_table.add_widget(Builder.load_string(c1))
                self.inventory_table.add_widget(Builder.load_string(c2))
                self.inventory_table.add_widget(Builder.load_string(c3))
                self.inventory_table.add_widget(Builder.load_string(c4))
                self.inventory_table.add_widget(c5)
                self.inventory_table.add_widget(c6)
                self.inventory_table.add_widget(c7)

    def inventory_move(self, pos, id, *args, **kwargs):
        orders = []
        inventories = SYNC.inventories_by_company(sessions.get('_companyId')['value'])
        row_selected = False
        if inventories:
            idx = -1
            for inventory in inventories:
                idx += 1
                inventory_id = inventory['id']
                inventory_order = inventory['ordered']
                orders.append({'id': inventory_id, 'ordered': inventory_order})
                if inventory_id == id:
                    row_selected = idx

        if row_selected:
            row_previous = row_selected - 1
            row_next = row_selected + 1
            if pos == 'up':
                try:
                    alist = orders[row_previous]
                    blist = orders[row_selected]
                    orders[row_previous] = blist
                    orders[row_selected] = alist
                except IndexError:
                    pass


            else:
                try:
                    alist = orders[row_next]
                    blist = orders[row_selected]
                    orders[row_next] = blist
                    orders[row_selected] = alist
                except IndexError:
                    pass
        idx = -1
        if orders:
            ordered = 0
            for order in orders:
                idx += 1
                ordered += 1
                orders[idx]['ordered'] = ordered

        # save new order
        if orders:
            for order in orders:
                Inventory().put(where={'id': order['id']}, data={'ordered': order['ordered']})
            self.reset()

    def edit_invoice_popup(self, id, *args, **kwargs):
        self.inventory_id = id
        self.edit_popup.title = 'Edit Invoice'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = GridLayout(size_hint=(1, 0.9),
                                    cols=2,
                                    rows=4,
                                    row_force_default=True,
                                    row_default_height='50sp',
                                    spacing='2sp')

        inventories = SYNC.inventory_grab(id)
        if inventories is not False:
            inventory_name = inventories['name']
            inventory_desc = inventories['description']
            inventory_order = inventories['ordered']
            inventory_laundry = inventories['laundry']
        else:
            inventory_name = ''
            inventory_desc = ''
            inventory_order = ''
            inventory_laundry = False
        inv_laundry_display = 'True' if inventory_laundry else 'False'
        self.inventory_name = Factory.CenterVerticalTextInput(text=inventory_name)
        self.inventory_desc = Factory.CenterVerticalTextInput(text=inventory_desc)
        self.inventory_order = Factory.CenterVerticalTextInput(text='{}'.format(str(inventory_order)))
        laundry = ['False', 'True']
        c4 = Spinner(text='{}'.format(inv_laundry_display),
                     values=laundry)
        c4.bind(text=self.set_laundry)
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Name:'))
        inner_layout_1.add_widget(self.inventory_name)
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Description:'))
        inner_layout_1.add_widget(self.inventory_desc)
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Order:'))
        inner_layout_1.add_widget(self.inventory_order)
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Laundry:'))
        inner_layout_1.add_widget(c4)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_press=self.edit_popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=0AAC00][b]Save[/b][/color]',
                                         on_press=self.edit_inventory))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.edit_popup.content = layout
        self.edit_popup.open()

    def edit_inventory(self, *args, **kwargs):
        inventories = Inventory()
        put = inventories.put(where={'id': self.inventory_id},
                              data={'name': self.inventory_name.text,
                                    'description': self.inventory_desc.text,
                                    'ordered': self.inventory_order.text,
                                    'laundry': self.inventory_laundry})
        if put:
            self.edit_popup.dismiss()
            Popups.modal_msg('Inventory Update', 'Successfully updated inventory!')
            self.edit_popup.dismiss()
            self.reset()

    def set_laundry(self, item, value, *args, **kwargs):
        if value == 'True':
            self.inventory_laundry = 1
        else:
            self.inventory_laundry = 0
        print(self.inventory_laundry)

    def add_inventory_popup(self):
        self.add_popup.title = 'Add Inventory'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = GridLayout(size_hint=(1, 0.9),
                                    cols=2,
                                    rows=4,
                                    row_force_default=True,
                                    row_default_height='50sp')
        self.inventory_name = Factory.CenterVerticalTextInput(text='')
        self.inventory_desc = Factory.CenterVerticalTextInput(text='')
        self.inventory_order = Factory.CenterVerticalTextInput(text='')
        laundry = ['False', 'True']
        c4 = Spinner(text='{}'.format('True' if self.inventory_laundry else 'False'),
                     values=laundry)
        c4.bind(text=self.set_laundry)
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Name:'))
        inner_layout_1.add_widget(self.inventory_name)
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Description:'))
        inner_layout_1.add_widget(self.inventory_desc)
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Order:'))
        inner_layout_1.add_widget(self.inventory_order)
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Laundry:'))
        inner_layout_1.add_widget(c4)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_press=self.add_popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=0AAC00][b]Add[/b][/color]',
                                         on_press=self.add_inventory))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.add_popup.content = layout
        self.add_popup.open()

    def add_inventory(self, *args, **kwargs):
        inventories = Inventory()
        inventories.company_id = sessions.get('_companyId')['value']
        inventories.name = self.inventory_name.text
        inventories.description = self.inventory_desc.text
        inventories.ordered = self.inventory_order.text
        inventories.laundry = self.inventory_laundry
        inventories.status = 1

        if inventories.add():
            # set invoice_items data to save
            Popups.modal_msg('Added Inventory', 'Successfully created a new inventory!')
            self.add_popup.dismiss()
            self.reset()