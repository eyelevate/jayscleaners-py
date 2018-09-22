from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, partial
from kivy.uix.screenmanager import Screen

from models.custids import Custid
from models.sync import Sync
from models.kv_generator import KvString
from kivy.uix.popup import Popup
from models.sessions import sessions
from models.static import Static
from pubsub import pub
KV = KvString()
SYNC_POPUP = Popup()
SYNC = Sync()


class SearchResultsScreen(Screen):
    """Takes in a customer searched dictionary and gives a table to select which customer we want to find
    once the user selects the customer gives an action to go back to the search screen with the correct
    customer id"""
    search_results_table = ObjectProperty(None)
    search_results_footer = ObjectProperty(None)
    search_results_label = ObjectProperty(None)

    def get_results(self):
        # Pause Schedule
        print(sessions.get('_searchText')['value'])
        sessions.put('_rowCap', value=SYNC.customers_row_cap(sessions.get('_searchText')['value']))

        self.search_results_table.clear_widgets()
        self.search_results_footer.clear_widgets()
        row_search = sessions.get('_rowSearch')['value']
        self.search_results_label.text = "[color=000000]Showing rows [b]{}[/b] - [b]{}[/b] out of [b]{}[/b][/color]".format(
            row_search[0], row_search[1], sessions.get('_rowCap')['value']

        )

        # create TH
        h1 = KV.widget_item(type='Label', data='ID', text_color='000000', rgba=(1, 1, 1, 1))
        h2 = KV.widget_item(type='Label', data='Mark', text_color='000000', rgba=(1, 1, 1, 1))
        h3 = KV.widget_item(type='Label', data='Last', text_color='000000', rgba=(1, 1, 1, 1))
        h4 = KV.widget_item(type='Label', data='First', text_color='000000', rgba=(1, 1, 1, 1))
        h5 = KV.widget_item(type='Label', data='Phone', text_color='000000', rgba=(1, 1, 1, 1))
        h6 = KV.widget_item(type='Label', data='Action', text_color='000000', rgba=(1, 1, 1, 1))
        self.search_results_table.add_widget(Builder.load_string(h1))
        self.search_results_table.add_widget(Builder.load_string(h2))
        self.search_results_table.add_widget(Builder.load_string(h3))
        self.search_results_table.add_widget(Builder.load_string(h4))
        self.search_results_table.add_widget(Builder.load_string(h5))
        self.search_results_table.add_widget(Builder.load_string(h6))

        # create Tbody TR
        even_odd = 0
        if sessions.get('_searchResults')['value'] is not False:
            for cust in sessions.get('_searchResults')['value']:
                even_odd += 1
                first_name = cust['first_name']
                last_name = cust['last_name']
                customer_id = cust['id']
                phone = cust['phone']
                rgba = '0.369,0.369,0.369,1' if even_odd % 2 == 0 else '0.826, 0.826, 0.826, 1'
                background_rgba = '0.369,0.369,0.369,0.1' if even_odd % 2 == 0 else '0.826, 0.826, 0.826, 0.1'
                text_color = 'e5e5e5' if even_odd % 2 == 0 else '000000'
                marks = Custid()
                mark = ''
                # custids = marks.where({'customer_id': cust['id']})
                custids = cust['custids']
                if custids:
                    for custid in custids:
                        mark = custid['mark']
                tr1 = KV.widget_item(type='Label', data=customer_id, rgba=rgba,
                                     background_rgba=background_rgba, text_color=text_color)
                tr2 = KV.widget_item(type='Label', data=mark, rgba=rgba,
                                     background_rgba=background_rgba, text_color=text_color)
                tr3 = KV.widget_item(type='Label', data=last_name, rgba=rgba,
                                     background_rgba=background_rgba, text_color=text_color)
                tr4 = KV.widget_item(type='Label', data=first_name, rgba=rgba,
                                     background_rgba=background_rgba, text_color=text_color)
                tr5 = KV.widget_item(type='Label', data=phone, rgba=rgba,
                                     background_rgba=background_rgba, text_color=text_color)
                tr6 = KV.widget_item(type='Button', data='View',
                                     callback='self.parent.parent.parent.customer_select({})'
                                     .format(customer_id))
                self.search_results_table.add_widget(Builder.load_string(tr1))
                self.search_results_table.add_widget(Builder.load_string(tr2))
                self.search_results_table.add_widget(Builder.load_string(tr3))
                self.search_results_table.add_widget(Builder.load_string(tr4))
                self.search_results_table.add_widget(Builder.load_string(tr5))
                self.search_results_table.add_widget(Builder.load_string(tr6))
        fc_cancel = KV.widget_item(type='Button', data='Cancel', callback='app.root.current = "search"')
        fc_up = KV.widget_item(type='Button', data='Prev', callback='self.parent.parent.parent.prev()')
        fc_down = KV.widget_item(type='Button', data='Next', callback='self.parent.parent.parent.next()')
        self.search_results_footer.add_widget(Builder.load_string(fc_cancel))
        self.search_results_footer.add_widget(Builder.load_string(fc_up))
        self.search_results_footer.add_widget(Builder.load_string(fc_down))
        sessions.put('_searchResults', value=False)

    def open_popup(self, *args, **kwargs):
        SYNC_POPUP.title = "Loading"
        content = KV.popup_alert("Please wait while gather information on the selected customer..")
        SYNC_POPUP.content = Builder.load_string(content)
        SYNC_POPUP.open()
        # send event
        pub.sendMessage('close_loading_popup', popup=SYNC_POPUP)

    def next(self):
        sessions.put('_rowCap', SYNC.customers_row_cap(sessions.get('_searchText')['value']))
        row_cap = sessions.get('_rowCap')['value']
        row_search = sessions.get('_rowSearch')['value']
        if row_search[1] + 10 >= row_cap:
            sessions.put('_rowSearch', value=(row_cap - 10, row_cap))
        else:
            sessions.put('_rowSearch', value=(row_search[1] + 1, row_search[1] + 10))

        cust1 = SYNC.customers_search_results(sessions.get('_searchText')['value'], row_search[0])
        sessions.put('_searchResults', value=cust1)
        self.search_results_label.text = "[color=000000]Showing rows [b]{}[/b] - [b]{}[/b] out of [b]{}[/b][/color]".format(
            row_search[0], row_search[1], row_cap
        )
        self.get_results()

    def prev(self):
        row_search = sessions.get('_rowSearch')['value']
        row_cap = sessions.get('_rowCap')['value']
        if row_search[0] - 10 < 10:
            sessions.put('_rowSearch', value=(0, 10))

        else:
            sessions.put('_rowSearch', value=(row_search[0] - 10, row_search[1] - 10))

        row_search = sessions.get('_rowSearch')['value']
        self.search_results_label.text = "[color=000000]Showing rows [b]{}[/b] - [b]{}[/b] out of [b]{}[/b][/color]".format(

            row_search[0], row_search[1], row_cap
        )

        cust1 = SYNC.customers_search_results(sessions.get('_searchText')['value'], row_search[0])
        sessions.put('_searchResults', value=cust1)
        self.search_results_label.text = "[color=000000]Showing rows [b]{}[/b] - [b]{}[/b] out of [b]{}[/b][/color]".format(
            row_search[0], row_search[1], row_cap
        )
        self.get_results()

    def customer_select(self, customer_id, *args, **kwargs):
        SYNC_POPUP.title = "Loading"
        content = KV.popup_alert("Gathering information on selected customer. Please wait...")
        SYNC_POPUP.content = Builder.load_string(content)
        SYNC_POPUP.open()
        Clock.schedule_once(partial(self.customer_select_sync, customer_id))
        # send event
        pub.sendMessage('close_loading_popup', popup=SYNC_POPUP)

    def customer_select_sync(self, customer_id, *args, **kwargs):
        sessions.put('_searchResultsStatus', value=True)
        sessions.put('_rowCap', value=0)
        sessions.put('_customerId', value=customer_id)
        sessions.put('_invoiceId', value=None)
        sessions.put('_rowSearch', value=(0, 10))
        self.parent.current = 'search'
        # last 10 setup

        Static.update_last_10(customer_id, sessions.get('_last10')['value'])
