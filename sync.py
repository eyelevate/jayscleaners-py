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
    server_at = None

    def db_sync(self):
        run_sync = Thread(target=self.run_sync)
        run_sync.start()
        run_sync.join()
        print('Sync finished')

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

        addresses_1 = Address().where({'address_id': None})
        if addresses_1:
            to_upload['addresses'] = addresses_1
            to_upload_rows += len(to_upload['addresses'])

        cards_1 = Card().where({'card_id': None})
        if cards_1:
            to_upload['cards'] = cards_1
            to_upload_rows += len(to_upload['cards'])

        colors_1 = Colored().where({'color_id': None})
        if colors_1:
            to_upload['colors'] = colors_1
            to_upload_rows += len(to_upload['colors'])

        companies_1 = Company().where({'company_id': None})
        if companies_1:
            to_upload['companies'] = companies_1
            to_upload_rows += len(to_upload['companies'])

        credits_1 = Credit().where({'credit_id': None})
        print(credits_1)
        if credits_1:
            to_upload['credits'] = credits_1
            to_upload_rows += len(to_upload['credits'])

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
            idx = -1
            for invoice in invoices_1:
                idx += 1
                try:
                    invoices_1[idx]['due_date'] = int(
                        datetime.datetime.strptime(invoice['due_date'], "%Y-%m-%d %H:%M:%S").timestamp())
                except TypeError:
                    invoices_1[idx]['due_date'] = None
                except ValueError:
                    invoices_1[idx]['due_date'] = None
                try:
                    invoices_1[idx]['rack_date'] = int(
                        datetime.datetime.strptime(invoice['rack_date'], "%Y-%m-%d %H:%M:%S").timestamp())
                except TypeError:
                    invoices_1[idx]['rack_date'] = None
                except ValueError:
                    invoices_1[idx]['rack_date'] = None
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
            to_upload_rows += len(to_upload['printers'])

        profiles_1 = Profile().where({'p_id': None})
        if profiles_1:
            to_upload['profiles'] = profiles_1
            to_upload_rows += len(to_upload['profiles'])

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

        transactions_1 = Transaction().where({'trans_id': None})
        if transactions_1:
            to_upload['transactions'] = transactions_1
            to_upload_rows += len(to_upload['transactions'])

        users_1 = User().where({'user_id': None})
        if users_1:
            to_upload['users'] = users_1
            to_upload_rows += len(to_upload['users'])

        zipcodes_1 = Zipcode().where({'zipcode_id': None})
        if zipcodes_1:
            to_upload['zipcodes'] = users_1
            to_upload_rows += len(to_upload['zipcodes'])
        # # update columns
        to_update = {}
        to_update_rows = 0

        addresses_2 = Address().where({'address_id': {'!=': '""'},
                                       'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if addresses_2:
            to_update['addresses'] = addresses_2
            to_update_rows += len(to_update['addresses'])

        cards_2 = Card().where({'card_id': {'!=': '""'},
                                'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if cards_2:
            to_update['cards'] = cards_2
            to_update_rows += len(to_update['cards'])

        colors_2 = Colored().where({'color_id': {'!=': '""'},
                                    'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if colors_2:
            to_update['colors'] = colors_2
            to_update_rows += len(to_update['colors'])

        companies_2 = Company().where({'company_id': {'!=': '""'},
                                       'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if companies_2:
            to_update['companies'] = companies_2
            to_update_rows += len(to_update['companies'])

        credits_2 = Credit().where({'credit_id': {'!=': '""'},
                                    'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if credits_2:
            to_update['credits'] = credits_2
            to_update_rows += len(to_update['credits'])

        custids_2 = Custid().where({'cust_id': {'!=': '""'},
                                    'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if custids_2:
            to_update['custids'] = custids_2
            to_update_rows += len(to_update['custids'])

        deliveries_2 = Delivery().where({'delivery_id': {'!=': '""'},
                                         'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if deliveries_2:
            to_update['deliveries'] = deliveries_2
            to_update_rows += len(to_update['deliveries'])

        discounts_2 = Discount().where({'discount_id': {'!=': '""'},
                                        'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if discounts_2:
            to_update['discounts'] = discounts_2
            to_update_rows += len(to_update['discounts'])

        invoices_2 = Invoice().where({'invoice_id': {'!=': '""'},
                                      'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if invoices_2:
            idx = -1
            for invoice in invoices_2:
                idx += 1
                try:
                    invoices_2[idx]['due_date'] = int(
                        datetime.datetime.strptime(invoice['due_date'], "%Y-%m-%d %H:%M:%S").timestamp())
                except TypeError:
                    invoices_2[idx]['due_date'] = None
                except ValueError:
                    invoices_2[idx]['due_date'] = None
                try:
                    invoices_2[idx]['rack_date'] = int(
                        datetime.datetime.strptime(invoice['rack_date'], "%Y-%m-%d %H:%M:%S").timestamp())
                except TypeError:
                    invoices_2[idx]['rack_date'] = None
                except ValueError:
                    invoices_2[idx]['rack_date'] = None
                except OverflowError:
                    invoices_2[idx]['rack_date'] = None
            to_update['invoices'] = invoices_2
            to_update_rows += len(to_update['invoices'])

        invoice_items_2 = InvoiceItem().where({'invoice_items_id': {'!=': '""'},
                                               'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if invoice_items_2:
            to_update['invoice_items'] = invoice_items_2
            to_update_rows += len(to_update['invoice_items']) if to_update['invoice_items'] else 0

        inventories_2 = Inventory().where({'inventory_id': {'!=': '""'},
                                           'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if inventories_2:
            to_update['inventories'] = inventories_2
            to_update_rows += len(to_update['inventories'])

        inventory_items_2 = InventoryItem().where({'item_id': {'!=': '""'},
                                                   'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if inventory_items_2:
            to_update['inventory_items'] = inventory_items_2
            to_update_rows += len(to_update['inventory_items'])

        memos_2 = Memo().where({'memo_id': {'!=': '""'},
                                'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if memos_2:
            to_update['memos'] = memos_2
            to_update_rows += len(to_update['memos'])

        printers_2 = Printer().where({'printer_id': {'!=': '""'},
                                      'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if printers_2:
            to_update['printers'] = printers_2
            to_update_rows += len(to_update['printers'])

        profiles_2 = Profile().where({'p_id': {'!=': '""'},
                                      'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if profiles_2:
            to_update['profiles'] = profiles_2
            to_update_rows += len(to_update['profiles'])

        reward_transactions_2 = RewardTransaction().where({'reward_id': {'!=': '""'},
                                                           'updated_at': {'>': '"{}"'.format(server_at)}},
                                                          deleted_at=False)
        if reward_transactions_2:
            to_update['reward_transactions'] = reward_transactions_2
            to_update_rows += len(to_update['reward_transactions'])

        rewards_2 = Reward().where({'reward_id': {'!=': '""'},
                                    'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if rewards_2:
            to_update['rewards'] = rewards_2
            to_update_rows += len(to_update['rewards'])

        schedules_2 = Schedule().where({'schedule_id': {'!=': '""'},
                                        'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if schedules_2:
            to_update['schedules'] = schedules_2
            to_update_rows += len(to_update['schedules'])

        taxes_2 = Tax().where({'tax_id': {'!=': '""'},
                               'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if taxes_2:
            to_update['taxes'] = taxes_2
            to_update_rows += len(to_update['taxes'])

        transactions_2 = Transaction().where({'trans_id': {'!=': '""'},
                                              'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if transactions_2:
            to_update['transactions'] = transactions_2
            to_update_rows += len(to_update['transactions'])

        users_2 = User().where({'user_id': {'!=': '""'},
                                'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if users_2:
            to_update['users'] = users_2
            to_update_rows += len(to_update['users'])

        zipcodes_2 = Zipcode().where({'zipcode_id': {'!=': '""'},
                                      'updated_at': {'>': '"{}"'.format(server_at)}}, deleted_at=False)
        if zipcodes_2:
            to_update['zipcodes'] = zipcodes_2
            to_update_rows += len(to_update['zipcodes'])

        error_find = 'http://www.jayscleaners.com/admins/api/update/{cid}/{api}/{servat}/up={upload}/upd={update}'.format(
            cid=company.id,
            api=company.api_token,
            servat=company.server_at,
            upload=json.dumps(to_upload).replace(" ", "__"),
            update=json.dumps(to_update).replace(" ", "__")
        )
        print(error_find)
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

                # where = {'company_id': self.company_id}
                dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.server_at = dt
                # data = {'server_at': dt}
                Company().server_at_update()


        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            # if e.reason == 'Forbidden' or e.reason == 'Request-URI Too Long':  # url is too long try breaking it down into smaller chunks then send
            #     print('Request was too large for server, sending again in chunks.')
            #     try:
            #         # break up url into smaller chunks
            #         upload_string = json.dumps(to_upload).replace(" ", "__")
            #         update_string = json.dumps(to_update).replace(" ", "__")
            #
            #         # first check the length of update
            #         url = 'http://www.jayscleaners.com/admins/api/update/{cid}/{api}/{servat}/up={upload}/upd={update}'.format(
            #             cid=company.id,
            #             api=company.api_token,
            #             servat=company.server_at,
            #             upload=upload_string,
            #             update='{}'
            #         )
            #         # upload Chunk
            #         if len(url) <= 2000:
            #             print('sending upload chunk in whole')
            #             run_page = Thread(target=partial(self.send_chunk, url))
            #             run_page.start()
            #         else:
            #             print('starting upload in chunks')
            #             if to_upload:
            #                 chunk_up_list = {}
            #                 for table, table_rows in to_upload.items():
            #                     chunk_up_list[table] = {0: []}
            #                     idx = 0
            #                     chunk_up_count = 0
            #
            #                     if table_rows:
            #                         for row in table_rows:
            #                             row_string = json.dumps(row).replace(" ", "__")
            #                             chunk_up_count += len(str(row_string))
            #
            #                             if chunk_up_count <= 2000:
            #                                 chunk_up_list[table][idx].append(row)
            #                             else:
            #                                 chunk_up_count = 0
            #                                 idx += 1
            #                                 chunk_up_list[table][idx] = [row]
            #             if chunk_up_list:
            #                 to_upload_chunk = {}
            #                 for table, rows in chunk_up_list.items():
            #                     if rows:
            #                         for row in rows:
            #                             to_upload_chunk[table] = chunk_up_list[table][row]
            #                             url = 'http://www.jayscleaners.com/admins/api/update/{cid}/{api}/{servat}/up={upload}/upd={update}'.format(
            #                                 cid=company.id,
            #                                 api=company.api_token,
            #                                 servat=company.server_at,
            #                                 upload=json.dumps(to_upload_chunk).replace(" ", "__"),
            #                                 update='{}'
            #                             )
            #                             run_page = Thread(target=partial(self.send_chunk, url))
            #                             run_page.start()
            #                             run_page.join()
            #                             print('sent update #{}'.format(row))
            #
            #             # Update chunk
            #             url = 'http://www.jayscleaners.com/admins/api/update/{cid}/{api}/{servat}/up={upload}/upd={update}'.format(
            #                 cid=company.id,
            #                 api=company.api_token,
            #                 servat=company.server_at,
            #                 upload='{}',
            #                 update=json.dumps(to_update).replace(" ", "__")
            #             )
            #             if len(update_string) <= 2000:
            #                 print('sending update chunk in whole')
            #                 run_page = Thread(target=partial(self.send_chunk, url))
            #                 run_page.start()
            #             else:
            #                 if to_update:
            #                     chunk_upd_list = {}
            #                     for table, table_rows in to_update.items():
            #                         chunk_upd_list[table] = {0: []}
            #                         idx = 0
            #                         chunk_upd_count = 0
            #
            #                         if table_rows:
            #                             for row in table_rows:
            #                                 row_string = json.dumps(row).replace(" ", "__")
            #                                 chunk_upd_count += len(str(row_string))
            #                                 print(chunk_upd_count)
            #
            #                                 if chunk_upd_count <= 2000:
            #                                     chunk_upd_list[table][idx].append(row)
            #                                 else:
            #                                     chunk_upd_count = 0
            #                                     idx += 1
            #                                     chunk_upd_list[table][idx] = [row]
            #                 if chunk_upd_list:
            #                     to_update_chunk = {}
            #                     for table, rows in chunk_upd_list.items():
            #
            #                         if rows:
            #                             for row in rows:
            #                                 to_update_chunk[table] = chunk_upd_list[table][row]
            #                                 url = 'http://www.jayscleaners.com/admins/api/update/{cid}/{api}/{servat}/up={upload}/upd={update}'.format(
            #                                     cid=company.id,
            #                                     api=company.api_token,
            #                                     servat=company.server_at,
            #                                     upload='{}',
            #                                     update=json.dumps(to_update_chunk).replace(" ", "__")
            #                                 )
            #                                 run_page = Thread(target=partial(self.send_chunk, url))
            #                                 run_page.start()
            #                                 run_page.join()
            #                                 print('sent update #{}'.format(row))
            #
            #     except urllib.error.URLError as e:
            #         print(e.reason)
            # if e.reason == 'Not Found':  # we found a / in the string replace it with a OR
            #     upload = json.dumps(to_upload).replace(" ", "__").replace("/", "OR")
            #     update = json.dumps(to_update).replace(" ", "__").replace("/", "OR")
            #     url = 'http://www.jayscleaners.com/admins/api/update/{cid}/{api}/{servat}/up={upload}/upd={update}'.format(
            #         cid=company.id,
            #         api=company.api_token,
            #         servat=company.server_at,
            #         upload=upload,
            #         update=update
            #     )
            #     run_page = Thread(target=partial(self.send_chunk, url))
            #     run_page.start()
            #     run_page.join()
            #     print('Improper url formed, found a / in the json. replacing with OR and resending')

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
                    Company().server_at_update(where, data)

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
        sync = Sync()
        # # addresses
        # table = 'addresses'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table,1))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #             # reset local db table
        #             addresses = Address()
        #             addresses.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #             else:
        #                 print('Obtaining rows {} through {}'.format(start, end))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)

        # cards
        # table = 'cards'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 2))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #             msg = 'Deleting current db table = {} on local db'.format(table)
        #             # reset local db table
        #             cards = Card()
        #             cards.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #             else:
        #                 print('Obtaining rows {} through {}'.format(start, end))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)
        #
        # # colors
        # table = 'colors'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 3))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #             # reset local db table
        #             colors = Colored()
        #             colors.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #             else:
        #                 print('Obtaining rows {} through {}'.format(start, end))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)
        #
        # # companies
        # table = 'companies'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 4))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #             # reset local db table
        #             companies = Company()
        #             companies.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(start, end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #             else:
        #                 print('Obtaining rows {} through {}'.format(start, end))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)
        #
        # # credits
        # table = 'credits'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 5))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #             # reset local db table
        #             credits = Credit()
        #             credits.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #             else:
        #                 print('Obtaining rows {} through {}'.format(start, end))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)
        #
        # # custids
        # table = 'custids'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 6))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #
        #             # reset local db table
        #             custids = Custid()
        #             custids.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #             else:
        #                 print('Obtaining rows {} through {}'.format(start, end))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)
        #
        # # deliveries
        # table = 'deliveries'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 7))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #
        #             # reset local db table
        #             deliveries= Delivery()
        #             deliveries.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #
        #
        #             else:
        #                 print('Obtaining rows {} through {}'.format(0, 5000))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)
        #
        #
        # # discounts
        # table = 'discounts'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 8))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #
        #             # reset local db table
        #             discounts= Discount()
        #             discounts.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #
        #
        #             else:
        #                 print('Obtaining rows {} through {}'.format(0, 5000))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)

        # # inventories
        # table = 'inventories'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 9))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #
        #             # reset local db table
        #             inventories = Inventory()
        #             inventories.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #
        #
        #             else:
        #                 print('Obtaining rows {} through {}'.format(0, 5000))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)
        #
        # # inventory Items
        # table = 'inventory_items'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 10))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #
        #             # reset local db table
        #             inventory_items = InventoryItem()
        #             inventory_items.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #
        #
        #             else:
        #                 print('Obtaining rows {} through {}'.format(0, 5000))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)
        #
        # # invoice
        table = 'invoices'
        url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        print('Syncing table - {} ({} / 21)'.format(table, 11))
        try:
            r = request.urlopen(url)
            count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if (count_data['status'] is 200):
                start = int(count_data['data']['first_row'])
                end = int(count_data['data']['last_row'])
                if int(end - start) > 0:  # reset table db and start pulling in new data from server

                    # reset local db table
                    invoices= Invoice()
                    invoices.truncate()
                    if end > 5000:
                        for num in range(start, end, 5000):
                            idx_start = num
                            idx_end = num + 5000
                            print('Obtaining rows {} through {}'.format(idx_start, idx_end))
                            t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
                            t1.start()
                            t1.join()


                    else:
                        print('Obtaining rows {} through {}'.format(0, 5000))
                        t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
                        t1.start()
                        t1.join()
        except urllib.error.URLError as e:
            print(e)
        #
        #
        # # Invoice Items
        # table = 'invoice_items'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 12))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #
        #             # reset local db table
        #             invoice_items= InvoiceItem()
        #             invoice_items.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #
        #
        #             else:
        #                 print('Obtaining rows {} through {}'.format(0, 5000))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)
        #
        #
        # # memos
        # table = 'memos'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 13))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #
        #             # reset local db table
        #             memos= Memo()
        #             memos.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #
        #
        #             else:
        #                 print('Obtaining rows {} through {}'.format(0, 5000))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)
        #
        #
        # # printers
        # table = 'printers'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 14))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #
        #             # reset local db table
        #             printers= Printer()
        #             printers.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #
        #
        #             else:
        #                 print('Obtaining rows {} through {}'.format(0, 5000))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)
        #
        # # profiles
        # table = 'profiles'
        # url = 'http://ja/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 15))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #
        #             # reset local db table
        #             profiles= Profile()
        #             profiles.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #
        #
        #             else:
        #                 print('Obtaining rows {} through {}'.format(0, 5000))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)
        #
        # # discounts
        # table = 'reward_transactions'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 16))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #
        #             # reset local db table
        #             rt= RewardTransaction()
        #             rt.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #
        #
        #             else:
        #                 print('Obtaining rows {} through {}'.format(0, 5000))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)
        #
        # # rewards
        # table = 'rewards'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 17))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #
        #             # reset local db table
        #             rewards= Reward()
        #             rewards.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #
        #
        #             else:
        #                 print('Obtaining rows {} through {}'.format(0, 5000))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)
        #
        # # schedules
        # table = 'schedules'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 18))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #
        #             # reset local db table
        #             schedules= Schedule()
        #             schedules.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #
        #
        #             else:
        #                 print('Obtaining rows {} through {}'.format(0, 5000))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)
        #
        # # transactions
        table = 'transactions'
        url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        print('Syncing table - {} ({} / 21)'.format(table, 19))
        try:
            r = request.urlopen(url)
            count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if (count_data['status'] is 200):
                start = int(count_data['data']['first_row'])
                end = int(count_data['data']['last_row'])

                if int(end - start) > 0:  # reset table db and start pulling in new data from server

                    # reset local db table
                    tr= Transaction()
                    tr.truncate()
                    if end > 5000:
                        for num in range(start, end, 5000):
                            idx_start = num
                            idx_end = num + 5000
                            print('Obtaining rows {} through {}'.format(idx_start, idx_end))
                            t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
                            t1.start()
                            t1.join()


                    else:
                        print('Obtaining rows {} through {}'.format(0, 5000))
                        t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
                        t1.start()
                        t1.join()
        except urllib.error.URLError as e:
            print(e)
        #
        # # users
        table = 'users'
        url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        print('Syncing table - {} ({} / 21)'.format(table, 20))
        try:
            r = request.urlopen(url)
            count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if (count_data['status'] is 200):
                start = int(count_data['data']['first_row'])
                end = int(count_data['data']['last_row'])

                if int(end - start) > 0:  # reset table db and start pulling in new data from server

                    # reset local db table
                    users= User()
                    users.truncate()
                    if end > 5000:
                        for num in range(start, end, 5000):
                            idx_start = num
                            idx_end = num + 5000
                            print('Obtaining rows {} through {}'.format(idx_start, idx_end))
                            t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
                            t1.start()
                            t1.join()


                    else:
                        print('Obtaining rows {} through {}'.format(0, 5000))
                        t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
                        t1.start()
                        t1.join()
        except urllib.error.URLError as e:
            print(e)
        #
        # # zipcodes
        # table = 'zipcodes'
        # url = 'http://www.jayscleaners.com/admins/api/auto/{}'.format(table)
        # print('Syncing table - {} ({} / 21)'.format(table, 21))
        # try:
        #     r = request.urlopen(url)
        #     count_data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        #     if (count_data['status'] is 200):
        #         start = int(count_data['data']['first_row'])
        #         end = int(count_data['data']['last_row'])
        #
        #         if int(end - start) > 0:  # reset table db and start pulling in new data from server
        #
        #             # reset local db table
        #             zipcodes= Zipcode()
        #             zipcodes.truncate()
        #             if end > 5000:
        #                 for num in range(start, end, 5000):
        #                     idx_start = num
        #                     idx_end = num + 5000
        #                     print('Obtaining rows {} through {}'.format(idx_start, idx_end))
        #                     t1 = Thread(target=sync.get_chunk(table=table, start=idx_start, end=idx_end))
        #                     t1.start()
        #                     t1.join()
        #
        #
        #             else:
        #                 print('Obtaining rows {} through {}'.format(0, 5000))
        #                 t1 = Thread(target=sync.get_chunk(table=table, start=0, end=5000))
        #                 t1.start()
        #                 t1.join()
        # except urllib.error.URLError as e:
        #     print(e)

        print('Process Complete. Local database has been completely synced.')
        Company().server_at_update()