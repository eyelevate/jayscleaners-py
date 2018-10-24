from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from models.custids import Custid
# from main import vars, KV, SYNC, Job
from models.users import User
from models.kv_generator import KvString
from models.sync import Sync
from models.jobs import Job
from pubsub import pub
from models.sessions import sessions
from models.static import Static
SYNC = Sync()
KV = KvString()
Job = Job()

class Last10Screen(Screen):
    last10_table = ObjectProperty(None)
    last10_footer = ObjectProperty(None)

    def attach(self):
        pub.subscribe(self.customer_select, "customer_select")

    def detach(self):
        pub.unsubscribe(self.customer_select, "customer_select")

    def get_last10(self):
        # Pause Schedule
        sessions.put('_searchResultsStatus', value= True)
        # clean up

        customer_ids = sessions.get('_last10')['value']
        for key, value in enumerate(customer_ids):
            if value is None:
                del customer_ids[key]
        custs = SYNC.customers_in(customer_ids)
        last = []
        if custs:
            for key, cust in enumerate(custs):
                row = key + 1
                cust_id = cust['id']
                last_name = cust['last_name']
                first_name = cust['first_name']
                phone = Job.make_us_phone(cust['phone'])
                mark = ''
                if 'custids' in cust:
                    all_marks = []
                    for marks in cust['custids']:
                        all_marks.append(marks['mark'])

                    mark = ', '.join(all_marks)
                last.append({
                    'text': '{}'.format(row),
                    'column': 1,
                    'customer_id': cust_id
                })
                last.append({
                    'text': '{}'.format(cust_id),
                    'column': 2,
                    'customer_id': cust_id
                })
                last.append({
                    'text': '{}'.format(mark),
                    'column': 3,
                    'customer_id': cust_id
                })
                last.append({
                    'text': '{}'.format(last_name),
                    'column': 4,
                    'customer_id': cust_id
                })
                last.append({
                    'text': '{}'.format(first_name),
                    'column': 5,
                    'customer_id': cust_id
                })
                last.append({
                    'text': '{}'.format(phone),
                    'column': 6,
                    'customer_id': cust_id
                })
        self.last10_table.data = last

    def customer_select(self, customer_id, *args, **kwargs):
        sessions.put('_searchResultsStatus', value= True)
        sessions.put('_customerId', value=customer_id)
        sessions.put('_invoiceId', value= None)

        self.parent.current = 'search'
        # last 10 setup
        Static.update_last_10(customer_id, sessions.get('_last10')['value'])