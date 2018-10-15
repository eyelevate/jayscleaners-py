from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from models.kv_generator import KvString
from models.sessions import sessions
KV = KvString()

class ItemDetailsScreen(Screen):
    name = ObjectProperty(None)
    items_detail_table_rv = ObjectProperty(None)

    def get_details(self):
        self.items_detail_table_rv.data = []
        self.items_table_update()
        pass

    def items_table_update(self):
        invoice_id = sessions.get('_invoiceId')['value']
        item_id = sessions.get('_itemId')['value']
        invs = sessions.get('_invoices')['value']
        item_details = []
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
                                        item_details.append({
                                            'text': str(invoice_item['id']),
                                            'size_hint_x': 0.2,
                                            'selected': selected,
                                            'item_id': invoice_item['id']
                                        })
                                        item_details.append({
                                            'text': str(invoice_item['quantity']),
                                            'size_hint_x': 0.1,
                                            'selected': selected,
                                            'item_id': invoice_item['id']
                                        })

                                        color_name = invoice_item['color']
                                        item_string = "[b]{item}[/b]:\n{color_s}\n{memo_s}".format(item=item_name,
                                                                                                    color_s='{}'.format(color_name),
                                                                                                    memo_s='{}'.format(invoice_item['memo']))
                                        item_details.append({
                                            'text': item_string,
                                            'text_wrap': True,
                                            'halign': 'left',
                                            'valign': 'top',
                                            'size_hint_x': 0.5,
                                            'selected': selected,
                                            'item_id': invoice_item['id']
                                        })
                                        item_details.append({
                                            'text': '${:,.2f}'.format(float(invoice_item['pretax'])),
                                            'size_hint_x': 0.2,
                                            'selected': selected,
                                            'item_id': invoice_item['id']
                                        })
        self.items_detail_table_rv.data = item_details

    def item_details(self, id):
        # highlight the selected invoice items
        sessions.put('_invoiceItemsId', value=id)
        self.items_table_update()
        # get item details and display them to item_detail_history_table
        invs = sessions.get('_invoices')['value']

        pass