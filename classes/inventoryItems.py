from _pydecimal import Decimal
from threading import Thread

from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ObjectProperty, partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanelHeader

from classes.popups import Popups
from models.inventory_items import InventoryItem
from models.kv_generator import KvString
from models.sync import Sync
from models.sessions import sessions
KV = KvString()
SYNC = Sync()

class InventoryItemsScreen(Screen):
    img_address = ObjectProperty(None)
    items_panel = ObjectProperty(None)
    fc = ObjectProperty(None)
    inventory_id = None
    item_id = None
    inventory_image = Image()
    r1c2 = ObjectProperty(None)
    r2c2 = ObjectProperty(None)
    r3c2 = ObjectProperty(None)
    r4c2 = ObjectProperty(None)
    r5c2 = ObjectProperty(None)
    r6c2 = ObjectProperty(None)
    add_popup = Popup()
    edit_popup = Popup()
    from_id = None
    reorder_list = {}

    def loading(self):
        popup = Popup()
        popup.title = 'Loading Screen'
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Loading Screen...'))
        popup.content = layout
        run_page = Thread(target=self.reset)
        run_page.start()
        # run_page.join()
        # popup.dismiss

    def reset(self):
        # Pause Schedule
        #
        self.inventory_id = None
        self.get_inventory()
        self.item_id = None
        self.inventory_image.source = ''
        self.from_id = None
        self.reorder_list = {}

    def get_inventory(self):

        inventories = SYNC.inventories_by_company(sessions.get('_companyId')['value'])
        if inventories:
            idx = 0
            self.items_panel.clear_tabs()
            self.items_panel.clear_widgets()
            for inventory in inventories:
                idx += 1
                inventory_id = inventory['inventory_id']
                self.reorder_list[inventory_id] = []
                if not self.inventory_id and idx == 1:
                    self.inventory_id = inventory_id
                inventory_name = inventory['name']
                iitems = InventoryItem()
                inventory_items = inventory['inventory_items']
                tph = TabbedPanelHeader(text='{}'.format(inventory_name),
                                        on_press=partial(self.set_inventory, inventory_id))
                layout = ScrollView()
                content = Factory.GridLayoutForScrollView()

                if inventory_items:
                    for item in inventory_items:
                        item_id = item['item_id']
                        item_price = '${:,.2f}'.format(Decimal(item['price']))
                        self.reorder_list[inventory_id].append(item_id)

                        if self.item_id is item_id:
                            items_button = Factory.ItemsFromButton(text='[b]{}[/b]\n[i]{}[/i]'.format(item['name'],
                                                                                                      item_price),
                                                                   on_press=partial(self.set_item, item_id))
                            self.from_id = self.item_id
                        else:
                            items_button = Factory.ItemsButton(text='[b]{}[/b]\n[i]{}[/i]'.format(item['name'],
                                                                                                  item_price),
                                                               on_press=partial(self.set_item, item_id))
                        content.add_widget(items_button)
                layout.add_widget(content)
                tph.content = layout
                self.items_panel.add_widget(tph)
                if self.inventory_id is inventory_id:
                    self.items_panel.switch_to(tph)

    def set_inventory(self, inventory_id, *args, **kwargs):
        self.inventory_id = inventory_id

    def set_item(self, item_id, *args, **kwargs):
        self.item_id = item_id
        if self.from_id:
            if self.inventory_id in self.reorder_list:
                idx = -1
                for list_id in self.reorder_list[self.inventory_id]:
                    idx += 1
                    if list_id is self.item_id:
                        self.reorder_list[self.inventory_id][idx] = self.from_id
                    if list_id is self.from_id:
                        self.reorder_list[self.inventory_id][idx] = self.item_id
                row = 0
                inv_items = InventoryItem()
                for list_id in self.reorder_list[self.inventory_id]:
                    row += 1
                    inv_items.put(where={'company_id': sessions.get('_companyId')['value'],
                                         'item_id': list_id},
                                  data={'ordered': row})
            self.from_id = None
            self.item_id = None
            self.reorder_list = {}
            self.get_inventory()
        else:
            self.add_popup.size_hint = (None, None)
            self.add_popup.size = (800, 400)
            self.add_popup.title = 'Select Inventory Method'
            layout = BoxLayout(orientation='vertical')
            inner_layout_1 = BoxLayout(orientation='horizontal',
                                       size_hint=(1, 0.6))
            inner_layout_1.add_widget(Button(text='Reorder',
                                             on_press=self.reorder_item))
            inner_layout_1.add_widget(Button(text='Edit',
                                             on_press=self.edit_show))
            inner_layout_1.add_widget(Button(text='Delete',
                                             on_press=self.delete_confirm))
            inner_layout_2 = BoxLayout(orientation='horizontal',
                                       size_hint=(1, 0.3))
            inner_layout_2.add_widget(Button(text='Cancel',
                                             on_press=self.add_popup.dismiss))
            layout.add_widget(inner_layout_1)
            layout.add_widget(inner_layout_2)
            self.add_popup.content = layout
            self.add_popup.open()

    def reorder_item(self, *args, **kwargs):
        self.get_inventory()
        self.add_popup.dismiss()

    def edit_show(self, *args, **kwargs):
        self.add_popup.dismiss()

        self.edit_popup.title = 'Edit Item'
        inventory_items = InventoryItem()
        invs = SYNC.inventories_by_company(sessions.get('_companyId')['value'])
        if invs is not False:
            for inv in invs:
                invitems = inv['inventory_items']
                if len(invitems) > 0:
                    for item in invitems:
                        if self.item_id is item['id']:
                            ordered = item['ordered']
                            name = item['name']
                            description = item['description']
                            tags = item['tags']
                            quantity = item['quantity']
                            price = item['price']
                            image_src = inventory_items.get_image_src(item['item_id'])
        else:
            name = ''
            description = ''
            tags = ''
            quantity = ''
            price = ''
            image_src = ''

        layout = BoxLayout(orientation='vertical',
                           pos_hint={'top': 1})
        inner_layout_1 = BoxLayout(orientation='horizontal')
        inner_group_1 = BoxLayout(orientation='vertical',
                                  size_hint=(0.5, 0.9))
        inner_form = GridLayout(cols=2,
                                rows=7,
                                row_force_default=True,
                                row_default_height='50sp',
                                spacing='3dp')
        r1c1 = Factory.CenteredFormLabel(text='Name')
        self.r1c2 = Factory.CenterVerticalTextInput(text=str(name))
        r2c1 = Factory.CenteredFormLabel(text='Description')
        self.r2c2 = Factory.CenterVerticalTextInput(text=str(description))
        r3c1 = Factory.CenteredFormLabel(text='Tags')
        self.r3c2 = Factory.CenterVerticalTextInput(text=str(tags))
        r4c1 = Factory.CenteredFormLabel(text='Quantity')
        self.r4c2 = Factory.CenterVerticalTextInput(text=str(quantity))
        r5c1 = Factory.CenteredFormLabel(text='Ordered')
        self.r5c2 = Factory.CenterVerticalTextInput(text=str(ordered))
        r6c1 = Factory.CenteredFormLabel(text='Price')
        self.r6c2 = Factory.CenterVerticalTextInput(text='{0:0>2}'.format(price))
        inner_form.add_widget(r1c1)
        inner_form.add_widget(self.r1c2)
        inner_form.add_widget(r2c1)
        inner_form.add_widget(self.r2c2)
        inner_form.add_widget(r3c1)
        inner_form.add_widget(self.r3c2)
        inner_form.add_widget(r4c1)
        inner_form.add_widget(self.r4c2)
        inner_form.add_widget(r5c1)
        inner_form.add_widget(self.r5c2)
        inner_form.add_widget(r6c1)
        inner_form.add_widget(self.r6c2)
        inner_group_1.add_widget(inner_form)
        inner_layout_1.add_widget(inner_group_1)
        inner_layout_1_2 = BoxLayout(orientation='vertical',
                                     size_hint=(0.5, 0.9))
        self.fc = Factory.ImageFileChooser()
        inner_layout_1_2.add_widget(self.fc)
        self.fc.ids.inventory_image.source = '{}'.format(image_src)
        inner_layout_1.add_widget(inner_layout_1_2)
        inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                   orientation='horizontal')
        cancel_button = Button(markup=True,
                               text='Cancel',
                               on_press=self.edit_popup.dismiss)
        add_button = Button(markup=True,
                            text='[color=0AAC00][b]Edit[/b][/color]',
                            on_press=self.edit_item)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(add_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.edit_popup.content = layout
        self.edit_popup.open()

    def delete_confirm(self, *args, **kwargs):
        popup = Popup()
        popup.size_hint = (None, None)
        popup.size = (800, 600)
        popup.title = 'Delete Confirmation'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = Label(size_hint=(1, 0.7),
                               markup=True,
                               text='Are you sure you wish to delete this inventory item (#{})?'.format(self.item_id))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.3))
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_press=popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=FF0000][b]Delete[/b][/color]',
                                         on_press=self.delete_item,
                                         on_release=popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def delete_item(self, *args, **kwargs):
        self.add_popup.dismiss()

        inventory_items = InventoryItem()

        inventories = SYNC.inventories_by_company(sessions.get('_companyId')['value'])
        if inventories is not False:
            for inventory in inventories:
                inventory_items = inventory['invoice_items']
                if len(inventory_items) > 0:
                    for inventory_item in inventory_items:
                        if self.item_id is inventory_item['id']:
                            check_delete = SYNC.delete_inventory_item(inventory_item['id'])
                            if check_delete is not False:
                                popup = Popup()
                                popup.title = 'Deleted Item Notification'
                                popup.size_hint = (None, None)
                                popup.size = (800, 600)
                                content = KV.popup_alert('Successfully deleted item')
                                popup.content = Builder.load_string(content)
                                popup.open()

        else:
            Popups.modal_msg('Deleted Item Notification', 'Could not delete item. Try again.')

    def add_item_popup(self):
        inventory_items = InventoryItem()
        inventories = SYNC.inventories_by_company(sessions.get('_companyId')['value'])
        invitems = []
        if inventories is not False:
            for inventory in inventories:
                invitems = inventory['inventory_items']

        next_ordered = 1
        if invitems:
            for item in invitems:
                ordered = item['ordered']
                next_ordered += ordered

        self.add_popup.title = 'Add A New Item'
        layout = BoxLayout(orientation='vertical',
                           pos_hint={'top': 1})
        inner_layout_1 = BoxLayout(orientation='horizontal')
        inner_group_1 = BoxLayout(orientation='vertical',
                                  size_hint=(0.5, 0.9))
        inner_form = GridLayout(cols=2,
                                rows=7,
                                row_force_default=True,
                                row_default_height='50sp',
                                spacing='3dp')
        r1c1 = Factory.CenteredFormLabel(text='Name')
        self.r1c2 = Factory.CenterVerticalTextInput()
        r2c1 = Factory.CenteredFormLabel(text='Description')
        self.r2c2 = Factory.CenterVerticalTextInput()
        r3c1 = Factory.CenteredFormLabel(text='Tags')
        self.r3c2 = Factory.CenterVerticalTextInput()
        r4c1 = Factory.CenteredFormLabel(text='Quantity')
        self.r4c2 = Factory.CenterVerticalTextInput()
        r5c1 = Factory.CenteredFormLabel(text='Ordered')
        self.r5c2 = Factory.CenterVerticalTextInput()
        r6c1 = Factory.CenteredFormLabel(text='Price')
        self.r6c2 = Factory.CenterVerticalTextInput()
        inner_form.add_widget(r1c1)
        inner_form.add_widget(self.r1c2)
        inner_form.add_widget(r2c1)
        inner_form.add_widget(self.r2c2)
        inner_form.add_widget(r3c1)
        inner_form.add_widget(self.r3c2)
        inner_form.add_widget(r4c1)
        inner_form.add_widget(self.r4c2)
        inner_form.add_widget(r5c1)
        inner_form.add_widget(self.r5c2)
        inner_form.add_widget(r6c1)
        inner_form.add_widget(self.r6c2)
        inner_group_1.add_widget(inner_form)
        inner_layout_1.add_widget(inner_group_1)
        self.r5c2.text = '{}'.format(str(next_ordered))
        inner_layout_1_2 = BoxLayout(orientation='vertical',
                                     size_hint=(0.5, 0.9))
        self.fc = Factory.ImageFileChooser()
        inner_layout_1_2.add_widget(self.fc)
        inner_layout_1.add_widget(inner_layout_1_2)
        inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                   orientation='horizontal')
        cancel_button = Button(markup=True,
                               text='Cancel',
                               on_press=self.add_popup.dismiss)
        add_button = Button(markup=True,
                            text='[color=0AAC00][b]Add[/b][/color]',
                            on_press=self.add_item)
        inner_layout_2.add_widget(cancel_button)
        inner_layout_2.add_widget(add_button)
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.add_popup.content = layout
        self.add_popup.open()

    def add_item(self, *args, **kwargs):
        # validate
        errors = 0

        if not self.r1c2.text:
            errors += 1

        if not self.r2c2.text:
            errors += 1

        if not self.r3c2.text:
            errors += 1

        if not self.r4c2.text:
            errors += 1

        if not self.r5c2.text:
            errors += 1

        if not self.r6c2.text:
            errors += 1

        img = self.fc.ids.inventory_image.source.replace('/', ' ').split() if self.fc.ids.inventory_image.source else [
            'question.png']
        img_name = img[-1]
        if errors == 0:
            inventory_items = InventoryItem()
            inventory_items.company_id = sessions.get('_companyId')['value']
            inventory_items.inventory_id = self.inventory_id
            inventory_items.name = self.r1c2.text
            inventory_items.description = self.r2c2.text
            inventory_items.tags = self.r3c2.text
            inventory_items.quantity = self.r4c2.text
            inventory_items.ordered = self.r5c2.text
            inventory_items.price = self.r6c2.text
            inventory_items.image = img_name
            if inventory_items.add():
                Popups.modal_msg('Form Success', 'Successfully created a new inventory item!')

                self.add_popup.dismiss()
                self.reset()
        else:
            Popups.modal_msg('Form Error', '{} form errors'.format(errors))

    def edit_item(self, *args, **kwargs):
        # validate
        errors = 0

        if not self.r1c2.text:
            errors += 1

        if not self.r2c2.text:
            errors += 1

        if not self.r3c2.text:
            errors += 1

        if not self.r4c2.text:
            errors += 1

        if not self.r5c2.text:
            errors += 1

        if not self.r6c2.text:
            errors += 1

        img = self.fc.ids.inventory_image.source.replace('/', ' ').split() if self.fc.ids.inventory_image.source else [
            'question.png']
        img_name = img[-1]
        if errors == 0:
            inventory_items = InventoryItem()
            put = inventory_items.put(where={'company_id': sessions.get('_companyId')['value'],
                                             'item_id': self.item_id},
                                      data={'name': self.r1c2.text,
                                            'description': self.r2c2.text,
                                            'tags': self.r3c2.text,
                                            'quantity': self.r4c2.text,
                                            'ordered': self.r5c2.text,
                                            'price': self.r6c2.text,
                                            'image': img_name})
            if put:
                Popups.modal_msg('Form Success', 'Successfully updated item!')
                self.edit_popup.dismiss()
                self.from_id = None
                self.item_id = None
                self.reorder_list = {}
                self.get_inventory()
        else:
            Popups.modal_msg('Form Error', '{} form errors'.format(errors))