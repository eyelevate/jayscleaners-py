from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from models.custids import Custid
# from main import vars, KV, SYNC, Job
from models.users import User
from models.kv_generator import KvString
from models.sync import Sync
from models.jobs import Job
from models.sessions import sessions
from models.static import Static
SYNC = Sync()
KV = KvString()
Job = Job()

class Last10Screen(Screen):
    last10_table = ObjectProperty(None)
    last10_footer = ObjectProperty(None)

    def get_last10(self):
        # Pause Schedule
        sessions.put('_searchResultsStatus', value= True)
        self.last10_table.clear_widgets()
        self.last10_footer.clear_widgets()

        # create TH
        h1 = KV.widget_item(type='Label', data='#', text_color='000000', rgba=(1, 1, 1, 1))
        h2 = KV.widget_item(type='Label', data='ID', text_color='000000', rgba=(1, 1, 1, 1))
        h3 = KV.widget_item(type='Label', data='Mark', text_color='000000', rgba=(1, 1, 1, 1))
        h4 = KV.widget_item(type='Label', data='Last', text_color='000000', rgba=(1, 1, 1, 1))
        h5 = KV.widget_item(type='Label', data='First', text_color='000000', rgba=(1, 1, 1, 1))
        h6 = KV.widget_item(type='Label', data='Phone', text_color='000000', rgba=(1, 1, 1, 1))
        h7 = KV.widget_item(type='Label', data='Action', text_color='000000', rgba=(1, 1, 1, 1))
        self.last10_table.add_widget(Builder.load_string(h1))
        self.last10_table.add_widget(Builder.load_string(h2))
        self.last10_table.add_widget(Builder.load_string(h3))
        self.last10_table.add_widget(Builder.load_string(h4))
        self.last10_table.add_widget(Builder.load_string(h5))
        self.last10_table.add_widget(Builder.load_string(h6))
        self.last10_table.add_widget(Builder.load_string(h7))
        customers = User()
        # create Tbody TR
        even_odd = 0
        if len(sessions.get('_last10')['value']) > 0:
            for customer_id in sessions.get('_last10')['value']:
                even_odd += 1
                rgba = '0.369,0.369,0.369,1' if even_odd % 2 == 0 else '0.826, 0.826, 0.826, 1'
                background_rgba = '0.369,0.369,0.369,0.1' if even_odd % 2 == 0 else '0.826, 0.826, 0.826, 0.1'
                text_color = 'e5e5e5' if even_odd % 2 == 0 else '000000'
                # data = {'user_id': customer_id}
                cust1 = SYNC.customers_grab(customer_id)
                # cust1 = customers.where(data)
                if len(cust1) > 0:
                    for cust in cust1:
                        marks = Custid()
                        mark = ''
                        custids = cust['custids']
                        if custids:
                            for custid in custids:
                                mark = custid['mark']
                        tr1 = KV.widget_item(type='Label', data=even_odd, rgba=rgba,
                                             background_rgba=background_rgba, text_color=text_color)
                        tr2 = KV.widget_item(type='Label', data=customer_id, rgba=rgba,
                                             background_rgba=background_rgba, text_color=text_color)
                        tr3 = KV.widget_item(type='Label', data=mark, rgba=rgba,
                                             background_rgba=background_rgba, text_color=text_color)
                        tr4 = KV.widget_item(type='Label', data=cust['last_name'], rgba=rgba,
                                             background_rgba=background_rgba, text_color=text_color)
                        tr5 = KV.widget_item(type='Label', data=cust['first_name'], rgba=rgba,
                                             background_rgba=background_rgba, text_color=text_color)
                        tr6 = KV.widget_item(type='Label', data=Job.make_us_phone(cust['phone']), rgba=rgba,
                                             background_rgba=background_rgba, text_color=text_color)
                        tr7 = KV.widget_item(type='Button', data='View',
                                             callback='self.parent.parent.parent.customer_select({})'
                                             .format(customer_id))
                        self.last10_table.add_widget(Builder.load_string(tr1))
                        self.last10_table.add_widget(Builder.load_string(tr2))
                        self.last10_table.add_widget(Builder.load_string(tr3))
                        self.last10_table.add_widget(Builder.load_string(tr4))
                        self.last10_table.add_widget(Builder.load_string(tr5))
                        self.last10_table.add_widget(Builder.load_string(tr6))
                        self.last10_table.add_widget(Builder.load_string(tr7))
        fc_cancel = KV.widget_item(type='Button', data='Cancel', callback='app.root.current = "search"')
        self.last10_footer.add_widget(Builder.load_string(fc_cancel))

    def customer_select(self, customer_id, *args, **kwargs):
        sessions.put('_searchResultsStatus', value= True)
        sessions.put('_rowCap',value= 0)
        sessions.put('_customerId', value=customer_id)
        sessions.put('_invoiceId', value= None)
        sessions.put('_rowSearch', value=(0,9))

        self.parent.current = 'search'
        # last 10 setup
        Static.update_last_10(sessions.get('_customerId')['value'], sessions.get('_last10')['value'])