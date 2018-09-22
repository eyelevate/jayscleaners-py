from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from models.inventories import Inventory
from models.inventory_items import InventoryItem
from models.invoice_items import InvoiceItem
from models.kv_generator import KvString
from models.sessions import sessions
KV = KvString()

class ItemDetailsScreen(Screen):
    name = ObjectProperty(None)
    items_table = ObjectProperty(None)
    inventory_name_label = ObjectProperty(None)
    inventory_item_name = ObjectProperty(None)

    def get_details(self):
        # Pause Schedule
        #
        # reset invoice_items_id
        sessions.get('_invoiceItemsId')['value'] = None
        # make the items
        self.item_image.source = ''
        self.inventory_name_label.text = ''
        self.inventory_item_name.text = ''
        self.items_table_update()
        pass

    def items_table_update(self):
        self.items_table.clear_widgets()
        iitems = InvoiceItem()
        data = {'item_id': sessions.get('_itemId')['value'], 'invoice_id': sessions.get('_invoiceId')['value']}
        inv_items = iitems.where(data)
        if inv_items:
            # create headers
            # create TH
            h1 = KV.sized_invoice_tr(0, 'ID', size_hint_x=0.1)
            h2 = KV.sized_invoice_tr(0, 'Qty', size_hint_x=0.1)
            h3 = KV.sized_invoice_tr(0, 'Item', size_hint_x=0.6)
            h4 = KV.sized_invoice_tr(0, 'Subtotal', size_hint_x=0.2)
            self.items_table.add_widget(Builder.load_string(h1))
            self.items_table.add_widget(Builder.load_string(h2))
            self.items_table.add_widget(Builder.load_string(h3))
            self.items_table.add_widget(Builder.load_string(h4))

            for invoice_item in inv_items:
                invoice_items_id = invoice_item['invoice_items_id']
                selected = True if invoice_items_id == sessions.get('_invoiceItemsId')['value'] else False
                item_id = invoice_item['item_id']
                items_search = InventoryItem()
                itm_srch = items_search.where({'item_id': item_id})

                if itm_srch:
                    for itm in itm_srch:
                        item_name = itm['name']
                else:
                    item_name = ''
                tr1 = KV.sized_invoice_tr(1,
                                          invoice_item['id'],
                                          size_hint_x=0.1,
                                          selected=selected,
                                          on_release='app.root.current="item_details"',
                                          on_press='self.parent.parent.parent.parent.item_details({})'.format(
                                              invoice_items_id))

                tr2 = KV.sized_invoice_tr(1,
                                          invoice_item['quantity'],
                                          size_hint_x=0.1,
                                          selected=selected,
                                          on_release='app.root.current="item_details"',
                                          on_press='self.parent.parent.parent.parent.item_details({})'.format(
                                              invoice_items_id))
                color_name = invoice_item['color']

                item_string = "[b]{item}[/b]:\\n {color_s} {memo_s}".format(item=item_name,
                                                                            color_s='{}'.format(color_name),
                                                                            memo_s='{}'.format(invoice_item['memo']))
                # print(item_string)
                tr3 = KV.sized_invoice_tr(1,
                                          item_string,
                                          text_wrap=True,
                                          size_hint_x=0.6,
                                          selected=selected,
                                          on_release='app.root.current="item_details"',
                                          on_press='self.parent.parent.parent.parent.item_details({})'.format(
                                              invoice_items_id))

                tr4 = KV.sized_invoice_tr(1,
                                          '${:,.2f}'.format(invoice_item['pretax']),
                                          size_hint_x=0.2,
                                          selected=selected,
                                          on_release='app.root.current="item_details"',
                                          on_press='self.parent.parent.parent.parent.item_details({})'.format(
                                              invoice_items_id))
                self.items_table.add_widget(Builder.load_string(tr1))
                self.items_table.add_widget(Builder.load_string(tr2))
                self.items_table.add_widget(Builder.load_string(tr3))
                self.items_table.add_widget(Builder.load_string(tr4))

    def item_details(self, item_id):
        # highlight the selected invoice items
        sessions.put('_invoiceItemsId', value=item_id)
        self.items_table_update()
        # get item details and display them to item_detail_history_table
        invoice_items = InvoiceItem().where({'id': item_id})
        if invoice_items:
            for invoice_item in invoice_items:
                inventory_item_id = invoice_item['item_id']
                items = InventoryItem()
                iitems = items.where({'item_id': inventory_item_id})
                if iitems:
                    for iitem in iitems:
                        inventory_id = iitem['inventory_id']
                        inventories = Inventory().where({'inventory_id': inventory_id})
                        if inventories:
                            for inventory in inventories:
                                inventory_name = inventory['name']
                        else:
                            inventory_name = ''
                        items.image = items.get_image_src(invoice_item['item_id'])
                        items.name = iitem['name']
                    self.item_image.source = items.image if items.image else ''
                    self.inventory_item_name.text = items.name if items.name else ''
                    self.inventory_name_label.text = inventory_name if inventory_name else ''

                    # update the rfid table history

        pass