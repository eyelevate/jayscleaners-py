import json
import time
import datetime

# Models
from colors import Colored
from companies import Company
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
from reward_transactions import RewardTransaction
from rewards import Reward
from schedules import Schedule
from taxes import Tax
from transactions import Transaction
from users import User

import urllib
from urllib import error
from urllib import request
from urllib import parse
from urllib.parse import urlencode
from urllib.request import urlopen

ERROR_COLOR = 0.94, 0.33, 0.33, 1
DEFAULT_COLOR = 0.5, 0.5, 0.5, 1.0
unix = time.time()
NOW = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))


class Sync:
    def db_sync(self, company_id):
        # self.migrate()
        # start upload text

        # create an array of data that need to be uploaded to the server
        to_upload = {}
        to_upload_rows = 0

        colors_1 = Colored().where({'color_id': None})
        if colors_1:
            to_upload['colors'] = colors_1
            to_upload_rows += len(to_upload['colors'])

        companies_1 = Company().where({'company_id': None})
        if companies_1:
            to_upload['companies'] = companies_1
            to_upload_rows += len(to_upload['companies'])

        custids_1 = Custid().where({'cust_id': None})
        if custids_1:
            to_upload['custids'] = custids_1
            to_upload_rows += len(to_upload['custids'])

        deliveries_1 = Delivery().where({'delivery_id': None})
        if deliveries_1:
            to_upload['deliveries'] = deliveries_1
            to_upload_rows += len(to_upload['deliveries'])

        discounts_1 = Discount().where({'discount_id': None})
        if discounts_1:
            to_upload['discounts'] = discounts_1
            to_upload_rows += len(to_upload['discounts'])

        invoices_1 = Invoice().where({'invoice_id': None})
        if invoices_1:
            to_upload['invoices'] = invoices_1
            to_upload_rows += len(to_upload['invoices'])

        invoice_items_1 = InvoiceItem().where({'invoice_items_id': None})
        if invoice_items_1:
            to_upload['invoice_items'] = invoice_items_1
            to_upload_rows += len(to_upload['invoice_items']) if to_upload['invoice_items'] else 0

        inventories_1 = Inventory().where({'inventory_id': None})
        if inventories_1:
            to_upload['inventories'] = inventories_1
            to_upload_rows += len(to_upload['inventories'])

        inventory_items_1 = InventoryItem().where({'item_id': None})
        if inventory_items_1:
            to_upload['inventory_items'] = inventory_items_1
            to_upload_rows += len(to_upload['inventory_items'])

        memos_1 = Memo().where({'memo_id': None})
        if memos_1:
            to_upload['memos'] = memos_1
            to_upload_rows += len(to_upload['memos'])

        printers_1 = Printer().where({'printer_id': None})
        if printers_1:
            to_upload['printers'] = printers_1
            to_upload_rows += len(to_upload['colors'])

        reward_transactions_1 = RewardTransaction().where({'reward_id': None})
        if reward_transactions_1:
            to_upload['reward_transactions'] = reward_transactions_1
            to_upload_rows += len(to_upload['reward_transactions'])

        rewards_1 = Reward().where({'reward_id': None})
        if rewards_1:
            to_upload['rewards'] = rewards_1
            to_upload_rows += len(to_upload['rewards'])

        schedules_1 = Schedule().where({'schedule_id': None})
        if schedules_1:
            to_upload['schedules'] = schedules_1
            to_upload_rows += len(to_upload['schedules'])

        taxes_1 = Tax().where({'tax_id': None})
        if taxes_1:
            to_upload['taxes'] = taxes_1
            to_upload_rows += len(to_upload['taxes'])

        transactions_1 = Transaction().where({'transaction_id': None})
        if transactions_1:
            to_upload['transactions'] = transactions_1
            to_upload_rows += len(to_upload['transactions'])

        users_1 = User().where({'user_id': None})
        if users_1:
            to_upload['users'] = users_1
            to_upload_rows += len(to_upload['users'])

        company = Company()
        company.id = company_id
        data = {'company_id': company_id}
        c1 = company.where(data)

        if len(c1) > 0:
            for comp in c1:
                dt = datetime.datetime.strptime(comp['server_at'], "%Y-%m-%d %H:%M:%S") if comp['server_at'] is not None else datetime.datetime.strptime(
                    '1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
                company.server_at = str(dt).replace(" ", "_")
                # company.server_at = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
                company.api_token = comp['api_token']
        else:
            company.id = 1
            company.server_at = 0
            company.api_token = '2064535930-1'

        url = 'http://74.207.240.88/admins/api/update/{}/{}/{}/up={}'.format(
            company.id,
            company.api_token,
            company.server_at,
            json.dumps(to_upload).replace(" ", "")
        )

        # attempt to connect to server
        try:
            r = request.urlopen(url)
            data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))

            if data['status'] is 200:
                # Save the local data
                sync_from_server(data=data)
                # update ids with saved data & update company table with server_at timestamp
                update_database(data=data)
                # update server_at in companies with most current timestamp

                where = {'company_id': company_id}
                dt = datetime.datetime.strptime(NOW, "%Y-%m-%d %H:%M:%S") if NOW is not None else datetime.datetime.strptime(
                    '1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
                data = {'server_at': dt}
                company.put(where, data)
                company.close_connection()

        except urllib.error.URLError as e:
            print(e.reason) # could not save this time around because no internet, move on

    def get_chunk(self, table=False, start=False, end=False):
        company_id = 1
        api_token = '2064535930-1'

        url = 'http://74.207.240.88/admins/api/chunk/{}/{}/{}/{}/{}'.format(
            company_id,
            api_token,
            table,
            start,
            end
        )
        print(url)
        try:
            r = request.urlopen(url)
            data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))

            if data['status'] is True:
                # Save the local data
                sync_from_server(data=data)

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on

    def migrate(self, *args, **kwargs):
        color = Colored()
        company = Company()
        custid = Custid()
        delivery = Delivery()
        discount = Discount()
        inventory = Inventory()
        inventory_item = InventoryItem()
        invoice = Invoice()
        invoice_item = InvoiceItem()
        memo = Memo()
        printer = Printer()
        reward_transaction = RewardTransaction()
        reward = Reward()
        schedule = Schedule()
        tax = Tax()
        transaction = Transaction()
        user = User()
        color.create_table()
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
        reward_transaction.create_table()
        reward.create_table()
        schedule.create_table()
        tax.create_table()
        transaction.create_table()
        user.create_table()
        color.close_connection()
        company.close_connection()
        custid.close_connection()
        delivery.close_connection()
        discount.close_connection()
        inventory.close_connection()
        inventory_item.close_connection()
        invoice.close_connection()
        invoice_item.close_connection()
        memo.close_connection()
        printer.close_connection()
        reward.close_connection()
        reward_transaction.close_connection()
        schedule.close_connection()
        tax.close_connection()
        transaction.close_connection()
        user.close_connection()

    def server_login(self, username, password):
        users = User()
        url = 'http://74.207.240.88/admins/api/authenticate/{}/{}'.format(
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
            authenticated = users.auth(username=username,password=password)
            users.close_connection()
            return authenticated
