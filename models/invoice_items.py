import datetime
import time
import sqlite3
from models.model import *
from models.inventory_items import InventoryItem
import json
import urllib
from urllib import error, request, parse

unix = time.time()
now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
table = 'invoice_items'


class InvoiceItem:
    id = None
    invoice_items_id = None
    invoice_id = None
    item_id = None
    inventory_id = None
    company_id = None
    customer_id = None
    quantity = None
    color = None
    memo = None
    pretax = None
    tax = None
    total = None
    status = None
    deleted_at = None
    created_at = now
    updated_at = now

    def __init__(self):
        self._setUp()

    def create_table(self):

        table_schema = ', '.join([PrimaryKeyField(column='id').data_type(),
                                  IntegerField(column='invoice_items_id').data_type(),
                                  IntegerField(column='invoice_id').data_type(),
                                  IntegerField(column='item_id').data_type(),
                                  IntegerField(column='inventory_id').data_type(),
                                  IntegerField(column='company_id').data_type(),
                                  IntegerField(column='customer_id').data_type(),
                                  IntegerField(column='quantity').data_type(),
                                  TextField(column='color').data_type(),
                                  TextField(column='memo').data_type(),
                                  FloatField(column='pretax').data_type(),
                                  FloatField(column='tax').data_type(),
                                  FloatField(column='total').data_type(),
                                  IntegerField(column='status').data_type(),
                                  TextField(column='deleted_at').data_type(),
                                  TextField(column='created_at').data_type(),
                                  TextField(column='updated_at').data_type()
                                  ])

        self.c.execute('''CREATE TABLE IF NOT EXISTS {t} ({ts})'''.format(t=table, ts=table_schema))
        self.conn.commit()
        self._tearDown()

    def add(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        self.created_at = now
        self.c.execute('''INSERT INTO {t}(invoice_items_id,invoice_id,item_id,inventory_id,company_id,customer_id,
quantity,color,memo, pretax,tax,total,status,created_at,updated_at)
VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.invoice_items_id,
                                                           self.invoice_id,
                                                           self.item_id,
                                                           self.inventory_id,
                                                           self.company_id,
                                                           self.customer_id,
                                                           self.quantity,
                                                           self.color,
                                                           self.memo,
                                                           self.pretax,
                                                           self.tax,
                                                           self.total,
                                                           self.status,
                                                           self.created_at,
                                                           self.updated_at)
                       )

        self.conn.commit()
        self._tearDown()
        return True

    def add_special(self):

        self.c.execute('''INSERT INTO {t}(invoice_items_id,invoice_id,item_id,inventory_id,company_id,customer_id,
quantity,color,memo, pretax,tax,total,status,created_at,updated_at)
VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.invoice_items_id,
                                                           self.invoice_id,
                                                           self.item_id,
                                                           self.inventory_id,
                                                           self.company_id,
                                                           self.customer_id,
                                                           self.quantity,
                                                           self.color,
                                                           self.memo,
                                                           self.pretax,
                                                           self.tax,
                                                           self.total,
                                                           self.status,
                                                           self.created_at,
                                                           self.updated_at)
                       )

        self.conn.commit()
        self._tearDown()
        return True

    def put(self, where=False, data=False):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        sql = """UPDATE {t} SET """.format(t=table)
        if len(data) > 0:
            for key, value in data.items():
                if value is None:
                    sql += """{k} = NULL, """.format(k=key, v=value)
                else:
                    sql += """{k} = '{v}', """.format(k=key, v=value)
            sql += """updated_at = '{v}' """.format(v=self.updated_at)
        sql += """WHERE """
        idx = 0
        if len(where) > 0:
            for key, value in where.items():
                idx += 1
                if idx == len(where):
                    sql += """{k} = {v}""".format(k=key, v=value)
                else:
                    sql += """{k} = {v} AND """.format(k=key, v=value)

        self.c.execute(sql)
        self.conn.commit()
        self._tearDown()

        return True

    def update(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        self.c.execute('''UPDATE {t} SET invoice_items_id = ?, invoice_id = ?, item_id = ?, inventory_id = ?,
company_id = ?, customer_id = ?, quantity = ?, color = ?, memo = ?, pretax = ?, tax = ?, total = ?, status = ?,
updated_at = ? WHERE id = ?'''.format(t=table), (self.invoice_items_id,
                                                 self.invoice_id,
                                                 self.item_id,
                                                 self.inventory_id,
                                                 self.company_id,
                                                 self.customer_id,
                                                 self.quantity,
                                                 self.color,
                                                 self.memo,
                                                 self.pretax,
                                                 self.tax,
                                                 self.total,
                                                 self.status,
                                                 self.updated_at,
                                                 self.id)
                       )

        self.conn.commit()
        self._tearDown()
        return True

    def update_special(self):

        self.c.execute('''UPDATE {t} SET invoice_items_id = ?, invoice_id = ?, item_id = ?, inventory_id = ?,
company_id = ?, customer_id = ?, quantity = ?, color = ?, memo = ?, pretax = ?, tax = ?, total = ?, status = ?,
updated_at = ? WHERE id = ?'''.format(t=table), (self.invoice_items_id,
                                                 self.invoice_id,
                                                 self.item_id,
                                                 self.inventory_id,
                                                 self.company_id,
                                                 self.customer_id,
                                                 self.quantity,
                                                 self.color,
                                                 self.memo,
                                                 self.pretax,
                                                 self.tax,
                                                 self.total,
                                                 self.status,
                                                 self.updated_at,
                                                 self.id)
                       )

        self.conn.commit()
        self._tearDown()
        return True

    def find(self):

        try:
            self.c.execute("""SELECT * FROM {t} WHERE deleted_at is null AND id = ?""".format(table), (str(self.id)))
            self.conn.commit()
        except ValueError:
            self._tearDown()
            return "Could not find the company with that id"
        finally:
            fetch = self.c.fetchone()
            self._tearDown()
            return fetch

        return False

    def first(self, data=False):

        if data:
            sql = '''SELECT * FROM {t} WHERE deleted_at is null AND '''.format(t=table)
            idx = 0
            for key, value in data.items():
                idx += 1
                if idx == len(data):
                    sql += '''{k} = {v}'''.format(k=key, v=value)
                elif idx < len(data):
                    sql += '''{k} = {v} AND '''.format(k=key, v=value)

            self.c.execute(sql)
            self.conn.commit()
            fetch = self.c.fetchone()
            self._tearDown()
            return fetch
        else:
            self._tearDown()
            return False

    def where(self, data=False, deleted_at=True):

        if data:
            sql = '''SELECT * FROM {t} WHERE '''.format(t=table)
            idx = 0
            order_by = False
            limit = False
            if 'ORDER_BY' in data:
                order_by = data['ORDER_BY']
                del (data['ORDER_BY'])
            if 'LIMIT' in data:
                limit = data['LIMIT']
                del (data['LIMIT'])

            for key, value in data.items():
                idx += 1
                if isinstance(value, dict):
                    for oper, val in value.items():
                        if idx == len(data):
                            sql += '''{k} {o} {v}'''.format(k=key, o=oper, v=val)

                        elif idx < len(data):
                            sql += '''{k} {o} {v} AND '''.format(k=key, o=oper, v=val)

                else:
                    if idx == len(data):
                        if value is None:
                            sql += '''{k} is null'''.format(k=key)
                        elif value is 'not None':
                            sql += '''{k} is not null'''.format(k=key)
                        else:
                            sql += '''{k} = {v}'''.format(k=key, v=value)
                    elif idx < len(data):
                        if value is None:
                            sql += '''{k} is null AND '''.format(k=key)
                        else:
                            sql += '''{k} = {v} AND '''.format(k=key, v=value)

            sql += ' AND deleted_at is null' if deleted_at else ''

            if order_by:
                sql += ''' ORDER BY {} '''.format(order_by)

            if limit:
                sql += '''LIMIT {}'''.format(limit)

            self.c.execute(sql)
            self.conn.commit()
            fetch = self.c.fetchall()
            self._tearDown()
            return fetch
        else:
            self._tearDown()
            return False

    def like(self, data=False, deleted_at=True):
        if data:
            sql = '''SELECT * FROM {t} WHERE '''.format(t=table)
            idx = 0
            order_by = False
            limit = False
            if 'ORDER_BY' in data:
                order_by = data['ORDER_BY']
                del (data['ORDER_BY'])
            if 'LIMIT' in data:
                limit = data['LIMIT']
                del (data['LIMIT'])
            for key, value in data.items():
                idx += 1
                if idx == len(data):
                    if value is None:
                        sql += '''{k} is null'''.format(k=key)
                    else:
                        sql += '''{k} LIKE {v}'''.format(k=key, v=value)
                elif idx < len(data):
                    if value is None:
                        sql += '''{k} is null AND '''.format(k=key)
                    else:
                        sql += '''{k} LIKE {v} AND '''.format(k=key, v=value)

            sql += ' AND deleted_at is null ' if deleted_at else ''
            if order_by:
                sql += ''' ORDER BY {} '''.format(order_by)

            if limit:
                sql += '''LIMIT {}'''.format(limit)

            self.c.execute(sql)
            self.conn.commit()
            fetch = self.c.fetchall()
            self._tearDown()
            return fetch
        else:
            self._tearDown()
            return False

    def sum(self, column, where, deleted_at=False):
        sql = '''SELECT SUM({}) FROM {} WHERE '''.format(column, table)
        if where:
            for key, value in where.items():
                sql += '{} = {}'.format(key, value)
        sql += ' AND deleted_at is null' if deleted_at else ''

        self.c.execute(sql)
        self.conn.commit()

        totals = self.c.fetchall()
        self._tearDown()
        if totals:
            for total in totals:
                return total['SUM(pretax)']
        else:
            return False

    def delete(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now

        if self.id:

            self.c.execute("""UPDATE {table} SET deleted_at = ?, updated_at = ? WHERE id = ?""".format(table=table),
                           (self.updated_at,
                            self.updated_at,
                            self.id)
                           )

            self.conn.commit()
            self._tearDown()
            return True
        else:
            self._tearDown()
            return False

    def delete_item(self,invoice_items_id):
        deleted_item = self.where({'invoice_items_id': invoice_items_id})
        if deleted_item:
            for inv_item in deleted_item:
                self.id = inv_item['id']
                if self.delete():
                    print('deleted row {}'.format(inv_item['id']))
                    return True
                else:
                    print('could not find item to delete')
                    return False
            return True
        else:
            print('could not delete')
            return False

    def truncate(self):

        self.c.execute("""DELETE FROM {t}""".format(t=table))
        self.conn.commit()
        self.c.execute("""DELETE FROM SQLITE_SEQUENCE WHERE name='{t}'""".format(t=table))
        self.conn.commit()
        self._tearDown()

    def total_tags(self, invoice_id):
        total = 0
        invoice_items = self.where({'invoice_id': invoice_id})
        if invoice_items:
            for invoice_item in invoice_items:
                item_id = invoice_item['item_id']
                inventory_items = InventoryItem().where({'item_id': item_id})
                if inventory_items:
                    for inventory_item in inventory_items:
                        tags = int(inventory_item['tags']) if inventory_item['tags'] else 1
                        total += tags
        return total

    def get_id(self, invoice_items_id):
        invoice_items = self.where({'invoice_items_id': invoice_items_id})
        if invoice_items:
            for invoice_item in invoice_items:
                id = invoice_item['id']
                return id
        else:
            return False

    def prepareLocationList(self):
        list = [
            'Accepted',
            'In Dry Clean',
            'In Wash',
            'In Press - Shirts',
            'In Press - Pants',
            'In Press - Blouse',
            'In Press - Touch Up',
            'In Spotting',
            'In Assembly',
            'In Bagging',
            'Racked',
            'In Delivery',
            'Complete'
        ]
        return list

    def prepareLocationStatus(self, location):
        list = {
            'Accepted': 1,
            'In Dry Clean': 2,
            'In Wash': 3,
            'In Press - Shirts': 4,
            'In Press - Pants': 5,
            'In Press - Blouse': 6,
            'In Press - Touch Up': 7,
            'In Spotting': 8,
            'In Assembly': 9,
            'In Bagging': 10,
            'Racked': 11,
            'In Delivery': 12,
            'Complete': 13
        }
        return list[location]

    def get_tags(self, invoice_id):
        # attempt to connect to server
        url = 'http://www.jayscleaners.com/admins/api/invoice-items-data'
        data = parse.urlencode({'id': invoice_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))

            return data_1

        except urllib.error.URLError as e:
            return False

        return False

    def set_barcodes(self, invoice_id, company_id, data):
        encoded_data = json.dumps(data)
        if data:
            # attempt to connect to server
            url = 'http://www.jayscleaners.com/admins/api/set-barcode'
            data = parse.urlencode({'invoice_id': invoice_id,
                                    'company_id': company_id,
                                    'data': encoded_data}).encode('utf-8')
            req = request.Request(url=url, data=data)  # this will make the method "POS
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is not 400:
                return True

        except urllib.error.URLError as e:
            return False

        return False

    def _setUp(self):
        try:
            self.conn = sqlite3.connect('./db/jayscleaners.db')
        except sqlite3.OperationalError:
            self.conn = sqlite3.connect('jayscleaners.db')
        self.conn.row_factory = dict_factory
        self.c = self.conn.cursor()

    def _tearDown(self):
        self.c.close()
        self.conn.close()
