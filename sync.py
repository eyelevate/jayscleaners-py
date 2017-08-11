import json
import time
import datetime

# Models
from addresses import Address
from cards import Card
from colors import Colored
from companies import Company
from credits import Credit
from custids import Custid
from deliveries import Delivery
from discounts import Discount
from inventories import Inventory
from inventory_items import InventoryItem
from invoices import Invoice
from invoice_items import InvoiceItem
from memos import Memo
from server import sync_from_server
from server import update_database
from printers import Printer
from profiles import Profile
from reward_transactions import RewardTransaction
from rewards import Reward
from schedules import Schedule
from taxes import Tax
from transactions import Transaction
from users import User
from zipcodes import Zipcode

import urllib
from urllib import error, request, parse
from threading import Thread
from kivy.properties import partial

ERROR_COLOR = 0.94, 0.33, 0.33, 1
DEFAULT_COLOR = 0.5, 0.5, 0.5, 1.0


class Sync:
    company_id = None
    customer_id = None
    server_at = None

    #Address
    def address_grab(self, address_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/address-grab'
        # attempt to connect to server
        data = parse.urlencode({'address_id': address_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def create_address(self, address, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/create-address'
        # attempt to connect to server
        data = parse.urlencode({'address': address}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return True
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    #Card
    def card_grab(self, card_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/card-grab'
        # attempt to connect to server
        data = parse.urlencode({'card_id': card_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def card_grab_root(self, root_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/card-grab-root'
        # attempt to connect to server
        data = parse.urlencode({'root_id': root_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def update_card(self, card_id, cards, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/inventories-by-company'
        # attempt to connect to server
        data = parse.urlencode({'card_id': card_id,'cards':json.dumps(cards)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return True
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def create_card(self, cards, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/create-card'
        # attempt to connect to server
        data = parse.urlencode({'cards': json.dumps(cards)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return True
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    #Color
    def colors_query(self, company_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/colors-query'
        # attempt to connect to server
        data = parse.urlencode({'company_id': company_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is True:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    #Company
    def company_grab(self,company_id,*args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/company-grab'
        # attempt to connect to server
        data = parse.urlencode({'company_id': company_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is 0:
                return False
            else:
                return data_1['data']

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    #Credit
    def create_credit(self, credits, *args, **kwargs):

        url = 'http://www.jayscleaners.com/admins/api/create-credit'
        # attempt to connect to server
        data = parse.urlencode({'credits': json.dumps(credits)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is False:
                return False
            else:
                return True

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def edit_credit(self, customer_id, credit, *args, **kwargs):

        url = 'http://www.jayscleaners.com/admins/api/edit-credit'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id,'credits':credit}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is False:
                return False
            else:
                return True

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def credit_query(self, customer_id, *args, **kwargs):

        url = 'http://www.jayscleaners.com/admins/api/credit-query'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is False:
                return False
            else:
                return data_1['data']

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    #Custid
    def check_mark(self,mark, *args, **kwargs):

        url = 'http://www.jayscleaners.com/admins/api/check-mark'
        # attempt to connect to server
        data = parse.urlencode({'mark': mark}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is 0:
                return False
            else:
                return True

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def create_mark(self,mark, company_id, customer_id,*args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/create-mark'
        # attempt to connect to server
        data = parse.urlencode({'mark': mark,'company_id':company_id,'customer_id':customer_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is False:
                return False
            else:
                return True

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def delete_mark(self, mark, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/delete-mark'
        # attempt to connect to server
        data = parse.urlencode({'mark': mark}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is False:
                return False
            else:
                return True

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def marks_query(self, customer_id, status, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/marks-query'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id, 'status': status}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is False:
                return False
            else:
                return True

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False
    #delivery
    def delivery_grab(self, delivery_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/delivery-grab'
        # attempt to connect to server
        data = parse.urlencode({'delivery_id': delivery_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    #Discount
    def discount_grab(self, discount_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/discount-grab'
        # attempt to connect to server
        data = parse.urlencode({'discount_id': discount_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def discount_grab_by_company(self, company_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/discount-grab-by-company'
        # attempt to connect to server
        data = parse.urlencode({'comapny_id': company_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def discount_query(self,company_id, start_date, end_date,inventory_id,*args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/discount-query'
        # attempt to connect to server
        data = parse.urlencode({
            'company_id': company_id,
            'start_date': start_date,
            'end_date': end_date,
            'inventory_id': inventory_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    #Invoice
    def create_invoice(self, invoice, items, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/create-invoice'
        # attempt to connect to server
        data = parse.urlencode({'invoice': json.dumps(invoice),'items':json.dumps(items)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))

            if data_1['status'] is 0:
                return False
            else:
                return data_1['invoice']

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def edit_invoice(self, invoice_id, invoice, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/edit-invoice'
        # attempt to connect to server
        data = parse.urlencode({'invoice': json.dumps(invoice),'invoice_id':invoice_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))

            if data_1['status'] is False:
                return False
            else:
                return True

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def invoices_grab(self, customer_id, *args, **kwargs):
        self.customer_id = customer_id
        url = 'http://www.jayscleaners.com/admins/api/sync-customer'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is True:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False


    def invoices_grab_count(self, customer_id, *args, **kwargs):
        self.customer_id = customer_id
        url = 'http://www.jayscleaners.com/admins/api/invoice-grab-count'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            return data_1


        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return 0


    def invoices_grab_pickup(self, customer_id, *args, **kwargs):
        self.customer_id = customer_id
        url = 'http://www.jayscleaners.com/admins/api/invoice-grab-pickup'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is True:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def invoice_grab_id(self, invoice_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/invoice-grab'
        # attempt to connect to server
        data = parse.urlencode({'invoice_id': invoice_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def invoice_grab_id_with_trashed(self, invoice_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/invoice-grab-with-trashed'
        # attempt to connect to server
        data = parse.urlencode({'invoice_id': invoice_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def invoice_query_transaction_id(self, transaction_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/invoice-query-transaction-id'
        # attempt to connect to server
        data = parse.urlencode({'transaction_id': transaction_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def invoice_search_history(self, customer_id, start, end, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/invoice-search-history'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id,'start':start,'end':end}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def remove_invoice_by_transaction(self, invoice_id, status, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/remove-invoice-by-transaction'
        # attempt to connect to server
        data = parse.urlencode({'invoice_id': invoice_id, 'status': status}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def update_invoice_pickup(self, invoice_id, invoice, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/update-invoice-pickup'
        # attempt to connect to server
        data = parse.urlencode({'invoice_id': invoice_id, 'invoice': json.dumps(invoice)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return True
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def restore_invoice(self, invoice_id, status, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/restore-invoice'
        # attempt to connect to server
        data = parse.urlencode({'invoice_id': invoice_id, 'status': status}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def rack_invoice(self,invoice_id,rack,rack_date,*args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/rack-invoice'
        # attempt to connect to server
        data = parse.urlencode({'invoice_id':invoice_id,'rack': rack,'rack_date': rack_date}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            print(data_1)
            if data_1['status'] is 0:
                return False
            else:
                return True

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def delete_invoice(self, invoice_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/delete-invoice'
        # attempt to connect to server
        data = parse.urlencode({'invoice_id': invoice_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            print(data_1)
            if data_1['status'] is False:
                return False
            else:
                return True

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    #InvoiceItem
    def create_invoice_item(self, items, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/create-invoice-item'
        # attempt to connect to server
        data = parse.urlencode({'items':json.dumps(items)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            print(data_1)
            if data_1['status'] is 0:
                return False
            else:
                return data_1['data']

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def invoice_item_discount_find(self, invoice_id, inventory_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/invoice-item-discount-find'
        # attempt to connect to server
        data = parse.urlencode({'invoice_id': invoice_id, 'inventory_id': inventory_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is True:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def invoice_item_discount_find_item_id(self, invoice_id, item_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/invoice-item-discount-find-item-id'
        # attempt to connect to server
        data = parse.urlencode({'invoice_id': invoice_id, 'item_id': item_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is True:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False


    def invoice_item_grab(self, item_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/invoice-item-grab'
        # attempt to connect to server
        data = parse.urlencode({'item_id': item_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is 0:
                return False
            else:
                return data_1['data']

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def edit_invoice_item(self, invoice_item_id, invoice_items, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/edit-invoice-item'
        # attempt to connect to server
        data = parse.urlencode(
            {'invoice_item_id': invoice_item_id, 'invoice_items': json.dumps(invoice_items)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def delete_invoice_items(self, rows, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/delete-invoice-items'
        # attempt to connect to server
        data = parse.urlencode({'rows': json.dumps(rows)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return True
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    #Inventory
    def inventory_grab(self, inventory_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/inventory-grab'
        # attempt to connect to server
        data = parse.urlencode({'inventory_id': inventory_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is 0:
                return False
            else:
                return data_1['data']

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def inventories_by_company(self, company_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/inventories-by-company'
        # attempt to connect to server
        data = parse.urlencode({'company_id': company_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    #InventoryItem
    def inventory_items_grab(self, item_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/item-grab'
        # attempt to connect to server
        data = parse.urlencode({'item_id': item_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is 0:
                return False
            else:
                return data_1['data']

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def delete_inventory_item(self, item_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/delete-inventory-item'
        # attempt to connect to server
        data = parse.urlencode({'item_id': item_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return True
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    #Memo
    def memos_query(self, company_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/memos-query'
        # attempt to connect to server
        data = parse.urlencode({'company_id': company_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is False:
                return False
            else:
                return data_1['data']

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    #Profile
    def create_profile(self, profile, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/create-card'
        # attempt to connect to server
        data = parse.urlencode({'profile':json.dumps(profile)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return True
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def profiles_query(self, company_id, customer_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/profiles-query'
        # attempt to connect to server
        data = parse.urlencode({'company_id': company_id, 'customer_id': customer_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is False:
                return False
            else:
                return data_1['data']

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    #Schedule
    def create_schedule(self, schedule, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/create-schedule'
        # attempt to connect to server
        data = parse.urlencode({'schedule': json.dumps(schedule)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is True:
                return True
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def schedule_query(self, query, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/schedule-query'
        # attempt to connect to server
        data = parse.urlencode({'query': query}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is True:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def schedule_grab(self, id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/schedule-grab'
        # attempt to connect to server
        data = parse.urlencode({'id': id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is True:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False
    #Tax
    def taxes_query(self, company_id, status, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/taxes-query'
        # attempt to connect to server
        data = parse.urlencode({'company_id': company_id,'status': status}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is True:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    #Transaction
    def create_transaction(self, customer_id, transaction, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/create-transaction'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id,'transaction':json.dumps(transaction)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return True
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def update_transaction(self, customer_id, transaction, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/update-transaction'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id,'transaction':json.dumps(transaction)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return True
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def last_transaction_grab(self, customer_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/last-transaction-grab'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def transaction_grab(self, transaction_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/transaction-grab'
        # attempt to connect to server
        data = parse.urlencode({'transaction_id': transaction_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def transaction_query(self, customer_id, *args, **kwargs):
        print(customer_id)
        url = 'http://www.jayscleaners.com/admins/api/transaction-query'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def pay_account(self, transaction_id, trans, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/pay-account'
        # attempt to connect to server
        data = parse.urlencode({'transaction_id': transaction_id,'trans':json.dumps(trans)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return data_1['data']
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def pay_account_customer(self, customer_id, balance, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/pay-account-customer'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id, 'balance': json.dumps(balance)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return True
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    #Users
    def update_customer_pickup(self, customer_id, customer, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/update-customer-pickup'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id,'customer':json.dumps(customer)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return True
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def update_customer_account_total(self, customer_id, account_total, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/update-customer-account-total'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id,'account_total':account_total}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return True
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def update_customer_credits(self, customer_id, credits, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/update-customer-credits'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id,'credits':credits}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not False:
                return True
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def customer_delete(self, customer_id, *args, **kwargs):
        self.customer_id = customer_id
        url = 'http://www.jayscleaners.com/admins/api/delete-customer'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is False:
                return False
            else:
                return True

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def customer_add(self, users, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/add-customer'
        # attempt to connect to server
        data = parse.urlencode({'users': json.dumps(users)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is True:
                return data_1['data']
            else:
                return False


        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False


    def customer_edit(self, customer_id,users, *args, **kwargs):
        self.customer_id = customer_id
        url = 'http://www.jayscleaners.com/admins/api/edit-customer'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id,'users':json.dumps(users)}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is 0:
                return False
            else:
                return True

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def customers_grab(self, query, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/sc/{}'.format(query)
        # attempt to connect to server
        # data = parse.urlencode({'query': query}).encode('utf-8')
        # req = request.Request(url=url, data=data)  # this will make the method "POST"
        # r = request.urlopen(req)
        # data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        try:
            r = request.urlopen(url)
            # r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))

            return data_1

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def check_account(self, customer_id, *args, **kwargs):

        url = 'http://www.jayscleaners.com/admins/api/check-account'
        # attempt to connect to server
        data = parse.urlencode({'customer_id': customer_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is False:
                return False
            else:
                return data_1['data']

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False



    #Zipcode
    def zipcode_query(self, zipcode, *args, **kwargs):

        url = 'http://www.jayscleaners.com/admins/api/zipcode-query'
        # attempt to connect to server
        data = parse.urlencode({'zipcode': zipcode}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is False:
                return False
            else:
                return data_1['data']

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    #Last




    def db_sync(self, company_id, *args, **kwargs):
        self.company_id = company_id

        run_sync = Thread(target=self.run_sync)
        run_sync.start()
        run_sync.join()


    def run_sync(self, *args, **kwargs):
        # self.migrate()
        # start upload text
        unix = time.time()
        NOW = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        company = Company()
        company.id = self.company_id
        data = {'company_id': self.company_id}
        c1 = company.where(data)
        if len(c1) > 0:
            for comp in c1:
                dt = datetime.datetime.strptime(comp['server_at'], "%Y-%m-%d %H:%M:%S") if comp[
                                                                                               'server_at'] is not None else self.server_at
                server_at = dt
                company.server_at = int(datetime.datetime.strptime(comp['server_at'], "%Y-%m-%d %H:%M:%S").timestamp())
                # company.server_at = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
                company.api_token = comp['api_token']
        else:
            server_at = self.server_at
            company.id = 1
            company.server_at = 0
            company.api_token = '2064535930-1'

        # create an array of data that need to be uploaded to the server
        to_upload = {}
        to_upload_rows = 0


        companies_1 = Company().where({'company_id': None})
        if companies_1:
            to_upload['companies'] = companies_1
            to_upload_rows += len(to_upload['companies'])

        # # update columns
        to_update = {}
        to_update_rows = 0

        url = 'http://www.jayscleaners.com/admins/api/update'

        # attempt to connect to server
        data = parse.urlencode({'cid': company.id,
                                'api': company.api_token,
                                'servat': company.server_at,
                                'upload': json.dumps(to_upload),
                                'update': json.dumps(to_update)}).encode('utf-8')

        print(data)

        req = request.Request(url=url, data=data)  # this will make the method "POST"
        # r = request.urlopen(req)
        # data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        # print(data_1)
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is 200:
                # Save the local data
                sync_from_server(data=data_1)
                # update ids with saved data & update company table with server_at timestamp
                update_database(data=data_1)
                # update server_at in companies with most current timestamp
                saved_server_time = data_1['server_at']
                # where = {'company_id': self.company_id}

                dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.server_at = dt
                # data = {'server_at': dt}
                Company().server_at_update_special(saved_server_time)


        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on


    def send_chunk(self, url=False):
        if url:
            try:
                r = request.urlopen(url)
                data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
                if data_1['status'] is 200:
                    # Save the local data
                    sync_from_server(data=data_1)
                    # update ids with saved data & update company table with server_at timestamp
                    update_database(data=data_1)
                    # update server_at in companies with most current timestamp

                    where = {'company_id': self.company_id}
                    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.server_at = dt
                    data = {'server_at': dt}
                    Company().server_at_update_special(dt)

            except urllib.error.URLError as e:
                print('This is a chunk error: {}'.format(e.reason))

    def get_chunk(self, table=False, start=False, end=False, *args, **kwargs):
        company_id = 1
        api_token = '2064535930-1'

        url = 'http://www.jayscleaners.com/admins/api/chunk/{}/{}/{}/{}/{}'.format(
            company_id,
            api_token,
            table,
            start,
            end
        )
        # print(url)
        try:
            r = request.urlopen(url)
            data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))

            if data['status'] is True:
                # Save the local data
                sync_from_server(data=data)

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on

    def migrate(self, *args, **kwargs):
        address = Address()
        card = Card()
        color = Colored()
        company = Company()
        credit = Credit()
        custid = Custid()
        delivery = Delivery()
        discount = Discount()
        inventory = Inventory()
        inventory_item = InventoryItem()
        invoice = Invoice()
        invoice_item = InvoiceItem()
        memo = Memo()
        printer = Printer()
        profile = Profile()
        reward_transaction = RewardTransaction()
        reward = Reward()
        schedule = Schedule()
        tax = Tax()
        transaction = Transaction()
        user = User()
        zipcode = Zipcode()
        address.create_table()
        card.create_table()
        color.create_table()
        credit.create_table()
        company.create_table()
        custid.create_table()
        delivery.create_table()
        discount.create_table()
        inventory.create_table()
        inventory_item.create_table()
        invoice.create_table()
        invoice_item.create_table()
        memo.create_table()
        printer.create_table()
        profile.create_table()
        reward_transaction.create_table()
        reward.create_table()
        schedule.create_table()
        tax.create_table()
        transaction.create_table()
        user.create_table()
        zipcode.create_table()
        address.close_connection()
        card.close_connection()
        color.close_connection()
        company.close_connection()
        credit.close_connection()
        custid.close_connection()
        delivery.close_connection()
        discount.close_connection()
        inventory.close_connection()
        inventory_item.close_connection()
        invoice.close_connection()
        invoice_item.close_connection()
        memo.close_connection()
        printer.close_connection()
        profile.close_connection()
        reward.close_connection()
        reward_transaction.close_connection()
        schedule.close_connection()
        tax.close_connection()
        transaction.close_connection()
        user.close_connection()
        zipcode.close_connection()

    def server_login(self, username, password):
        users = User()
        url = 'http://www.jayscleaners.com/admins/api/authenticate/{}/{}'.format(
            username,
            password
        )

        try:
            req = request.urlopen(url)
            results = json.loads(req.read().decode(req.info().get_param('charset') or 'utf-8'))
            if results:
                data = {'password': str(password)}
                where = {'username': '"{}"'.format(username)}
                users.put(where=where, data=data)
                users.close_connection()
                return results
            else:
                return False

        except urllib.error.URLError as e:
            print(e.reason)
            # there is no internet connection so check the local sqlite db
            authenticated = users.auth(username=username, password=password)
            users.close_connection()
            return authenticated

    def auto_update(selfs):
        pass