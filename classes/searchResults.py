from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ObjectProperty, partial
from kivy.uix.screenmanager import Screen
from classes.selectable_rv_boxlayout import SelectableRecycleBoxLayout
from models.custids import Custid
from classes.search_results_rv import SearchResultsRV
from models.sync import Sync
from models.kv_generator import KvString
from kivy.uix.popup import Popup
from models.sessions import sessions
from models.static import Static
from models.jobs import Job
from pubsub import pub
KV = KvString()
SYNC_POPUP = Popup()
SYNC = Sync()


class SearchResultsScreen(Screen):
    """Takes in a customer searched dictionary and gives a table to select which customer we want to find
    once the user selects the customer gives an action to go back to the search screen with the correct
    customer id"""
    search_results_rv = ObjectProperty(None)
    search_results_selectable_button = ObjectProperty(None)
    search_results_input = ObjectProperty(None)
    search_results_selectable_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SearchResultsScreen, self).__init__(**kwargs)


    def get_results(self):
        # Pause Schedule
        if sessions.get('_searchResults')['value'] is not False:

            self.search_results_rv.data = [{
                'text': '[b]{}, {}[/b]\n{} - {}'.format('' if not x['last_name'] else x['last_name'].upper(), '' if not x['first_name'] else x['first_name'].upper(), x['id'], Job.make_us_phone(x['phone']))
            } for x in sessions.get('_searchResults')['value']]

    def open_popup(self, *args, **kwargs):
        SYNC_POPUP.title = "Loading"
        content = KV.popup_alert("Please wait while gather information on the selected customer..")
        SYNC_POPUP.content = Builder.load_string(content)
        SYNC_POPUP.open()
        # send event
        pub.sendMessage('close_loading_popup', popup=SYNC_POPUP)

    def filter(self):
        self.search_results_rv.data = []
        filtered = []
        original_index = []
        search = self.search_results_input.text
        if search is not '':
            for k,result in enumerate(sessions.get('_searchResults')['value']):
                last = result['last_name'].upper() if result['last_name'] else ''
                first = result['first_name'].upper() if result['first_name'] else ''
                id = str(result['id'])
                phone = str(result['phone'])
                f = search.upper()
                last_check = True if str(f) in str(last) else False
                first_check = True if str(f) in str(first) else False
                id_check = True if str(f) in id else False
                phone_check = True if str(f) in phone else False
                if id_check or last_check or first_check or phone_check:
                    filtered.append(result)

            self.search_results_rv.data = [{
                'text': '[b]{}, {}[/b]\n{} - {}'.format('' if not x['last_name'] else x['last_name'].upper(),
                                                        '' if not x['first_name'] else x['first_name'].upper(), x['id'],
                                                        Job.make_us_phone(x['phone']))
            } for x in filtered]
        else:
            self.get_results()


    def customer_select(self, customer_id, *args, **kwargs):
        sessions.put('_searchResults', value=False)
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
