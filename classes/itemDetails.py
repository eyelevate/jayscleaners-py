from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from models.kv_generator import KvString
from models.sessions import sessions
KV = KvString()

class ItemDetailsScreen(Screen):
    name = ObjectProperty(None)

    def get_details(self):
        self.item_image.source = ''
        self.inventory_name_label.text = ''
        self.inventory_item_name.text = ''
        self.items_table_update()
        pass

    def items_table_update(self):
        invoice_id = sessions.get('_invoiceId')['value']
        item_id = sessions.get('_itemId')['value']
        invs = sessions.get('_invoices')['value']

        if invs:
            for inv in invs:
                if invoice_id == inv['id']:
                    inv_items = inv['invoice_items']
                    if inv_items:
                        for invoice_item in inv_items:
                            if item_id == invoice_item['item_id']:
                                invoice_items_id = invoice_item['id']
                                selected = True if invoice_items_id == sessions.get('_invoiceItemsId')['value'] else False
                                item_id = invoice_item['item_id']
                                item_name = ''
                                if 'inventory_item' in invoice_item:
                                    if 'name' in invoice_item['inventory_item']:
                                        item_name = invoice_item['inventory_item']['name']
                                        # tr1 = KV.sized_invoice_tr(1,
                                        #                           invoice_item['id'],
                                        #                           size_hint_x=0.1,
                                        #                           selected=selected,
                                        #                           on_release='app.root.current="item_details"',
                                        #                           on_press='self.parent.parent.parent.parent.item_details({})'.format(
                                        #                               invoice_items_id))
                                        #
                                        # tr2 = KV.sized_invoice_tr(1,
                                        #                           invoice_item['quantity'],
                                        #                           size_hint_x=0.1,
                                        #                           selected=selected,
                                        #                           on_release='app.root.current="item_details"',
                                        #                           on_press='self.parent.parent.parent.parent.item_details({})'.format(
                                        #                               invoice_items_id))
                                        # color_name = invoice_item['color']
                                        #
                                        # item_string = "[b]{item}[/b]:\\n {color_s} {memo_s}".format(item=item_name,
                                        #                                                             color_s='{}'.format(color_name),
                                        #                                                             memo_s='{}'.format(invoice_item['memo']))
                                        # # print(item_string)
                                        # tr3 = KV.sized_invoice_tr(1,
                                        #                           item_string,
                                        #                           text_wrap=True,
                                        #                           size_hint_x=0.6,
                                        #                           selected=selected,
                                        #                           on_release='app.root.current="item_details"',
                                        #                           on_press='self.parent.parent.parent.parent.item_details({})'.format(
                                        #                               invoice_items_id))
                                        #
                                        # tr4 = KV.sized_invoice_tr(1,
                                        #                           '${:,.2f}'.format(float(invoice_item['pretax'])),
                                        #                           size_hint_x=0.2,
                                        #                           selected=selected,
                                        #                           on_release='app.root.current="item_details"',
                                        #                           on_press='self.parent.parent.parent.parent.item_details({})'.format(
                                        #                               invoice_items_id))
                                        # self.items_table.add_widget(Builder.load_string(tr1))
                                        # self.items_table.add_widget(Builder.load_string(tr2))
                                        # self.items_table.add_widget(Builder.load_string(tr3))
                                        # self.items_table.add_widget(Builder.load_string(tr4))

    def item_details(self, id):
        # highlight the selected invoice items
        sessions.put('_invoiceItemsId', value=id)
        self.items_table_update()
        # get item details and display them to item_detail_history_table
        invs = sessions.get('_invoices')['value']
        if invs:
            for inv in invs:

                    inv_items = inv['invoice_items']
                    if inv_items:
                        for invoice_item in inv_items:
                            if id == invoice_item['id']:
                                if 'inventory' in invoice_item:
                                    if 'name' in invoice_item['inventory']:
                                        inventory_name = invoice_item['inventory']['name']
                                if 'inventory_item' in invoice_item:
                                    if 'name' in invoice_item['inventory_item']:
                                        item_name = invoice_item['inventory_item']['name']
                                        item_image = '{}/{}'.format('src', invoice_item['inventory_item']['image'])
                                        self.item_image.source = item_image if item_image else ''
                                        self.inventory_item_name.text = item_name if item_name else ''
                                        self.inventory_name_label.text = inventory_name if inventory_name else ''

        pass