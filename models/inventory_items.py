import datetime
import time
import sqlite3
from models.model import *
from models.inventories import Inventory

unix = time.time()
now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
table = 'inventory_items'


class InventoryItem:
    id = None
    item_id = None
    inventory_id = None
    company_id = None
    name = None
    description = None
    tags = None
    quantity = None
    ordered = None
    price = None
    image = None
    status = None
    deleted_at = None
    created_at = None
    updated_at = None

    def __init__(self):
        self._setUp()

    def create_table(self):
        self._setUp()
        table_schema = ', '.join([PrimaryKeyField(column='id').data_type(),
                                  IntegerField(column='item_id').data_type(),
                                  IntegerField(column='inventory_id').data_type(),
                                  IntegerField(column='company_id').data_type(),
                                  CharField(column='name', max_length=100).data_type(),
                                  TextField(column='description').data_type(),
                                  IntegerField(column='tags').data_type(),
                                  IntegerField(column='quantity').data_type(),
                                  IntegerField(column='ordered').data_type(),
                                  FloatField(column="price").data_type(),
                                  CharField(column='image', max_length=150).data_type(),
                                  IntegerField(column='status').data_type(),
                                  TextField(column='deleted_at').data_type(),
                                  TextField(column='created_at').data_type(),
                                  TextField(column='updated_at').data_type(),
                                  ])

        self.c.execute('''CREATE TABLE IF NOT EXISTS {t} ({ts})'''.format(t=table, ts=table_schema))
        self.conn.commit()
        self._tearDown()

    def add(self):
        self._setUp()
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        self.created_at = now
        self.c.execute('''INSERT INTO {t}(item_id,inventory_id,company_id,name,description,tags,quantity,ordered,
price,image,status,created_at,updated_at)VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.item_id,
                                                                                                self.inventory_id,
                                                                                                self.company_id,
                                                                                                self.name,
                                                                                                self.description,
                                                                                                self.tags,
                                                                                                self.quantity,
                                                                                                self.ordered,
                                                                                                self.price,
                                                                                                self.image,
                                                                                                self.status,
                                                                                                self.created_at,
                                                                                                self.updated_at)
                       )

        self.conn.commit()
        self._tearDown()
        return True

    def add_special(self):
        self._setUp()
        self.c.execute('''INSERT INTO {t}(item_id,inventory_id,company_id,name,description,tags,quantity,ordered,
price,image,status,created_at,updated_at)VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.item_id,
                                                                                                self.inventory_id,
                                                                                                self.company_id,
                                                                                                self.name,
                                                                                                self.description,
                                                                                                self.tags,
                                                                                                self.quantity,
                                                                                                self.ordered,
                                                                                                self.price,
                                                                                                self.image,
                                                                                                self.status,
                                                                                                self.created_at,
                                                                                                self.updated_at)
                       )

        self.conn.commit()
        self._tearDown()
        return True

    def put(self, where=False, data=False):
        self._setUp()
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        sql = '''UPDATE {t} SET '''.format(t=table)
        if len(data) > 0:
            for key, value in data.items():
                sql += '''{k} = "{v}", '''.format(k=key, v=value)
            sql += '''updated_at = "{v}" '''.format(v=self.updated_at)
        sql += '''WHERE '''
        idx = 0
        if len(where) > 0:
            for key, value in where.items():
                idx += 1
                if idx == len(where):
                    sql += '''{k} = {v}'''.format(k=key, v=value)
                else:
                    sql += '''{k} = {v} AND '''.format(k=key, v=value)

        self.c.execute(sql)
        self.conn.commit()
        self._tearDown()
        return True

    def update(self):
        self._setUp()
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        self.c.execute('''UPDATE {t} SET item_id = ?, inventory_id = ?, company_id = ?, name = ?, description = ?,
tags = ?, quantity = ?, ordered = ?, price = ?, image = ?, status = ?, updated_at = ?
WHERE id = ?'''.format(t=table), (self.item_id,
                                  self.inventory_id,
                                  self.company_id,
                                  self.name,
                                  self.description,
                                  self.tags,
                                  self.quantity,
                                  self.ordered,
                                  self.price,
                                  self.image,
                                  self.status,
                                  self.updated_at,
                                  self.id)
                       )

        self.conn.commit()
        self._tearDown()
        return True

    def update_special(self):
        self._setUp()
        self.c.execute('''UPDATE {t} SET item_id = ?, inventory_id = ?, company_id = ?, name = ?, description = ?,
tags = ?, quantity = ?, ordered = ?, price = ?, image = ?, status = ?, updated_at = ?
WHERE id = ?'''.format(t=table), (self.item_id,
                                  self.inventory_id,
                                  self.company_id,
                                  self.name,
                                  self.description,
                                  self.tags,
                                  self.quantity,
                                  self.ordered,
                                  self.price,
                                  self.image,
                                  self.status,
                                  self.updated_at,
                                  self.id)
                       )

        self.conn.commit()
        self._tearDown()
        return True

    def find(self):
        self._setUp()
        try:
            self.c.execute("""SELECT * FROM {t} WHERE deleted_at is null AND id = ?""".format(table), (str(self.id)))
            self.conn.commit()
        except ValueError:
            self._tearDown()
            return "Could not find the company with that id"
        finally:
            if self.c.fetchone():
                for single in self.c.fetchone():
                    self.item_id = single['item_id']
                    self.inventory_id = single['inventory_id']
                    self.company_id = single['company_id']
                    self.name = single['name']
                    self.description = single['description']
                    self.tags = single['tags']
                    self.quantity = single['quantity']
                    self.ordered = single['ordered']
                    self.price = single['price']
                    self.image = single['image']
                    self.status = single['status']
                    self.deleted_at = single['deleted_at']
                    self.created_at = single['created_at']
            fetch = self.c.fetchone()
            self._tearDown()
            return fetch

        return False

    def first(self, data=False):
        self._setUp()
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
        self._setUp()
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
        self._setUp()
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

    def delete(self):
        self._setUp()
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        if self.id:

            self.c.execute("""UPDATE {t} SET deleted_at = ?, updated_at = ? WHERE id = ?""".format(t=table),
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

    def truncate(self):
        self._setUp()
        self.c.execute("""DELETE FROM {t}""".format(t=table))
        self.conn.commit()
        self.c.execute("""DELETE FROM SQLITE_SEQUENCE WHERE name='{t}'""".format(t=table))
        self.conn.commit()
        self._tearDown()

    def get_image_src(self, item_id, *args, **kwargs):
        src = 'src'
        inventory_items = self.where({'item_id': item_id})
        if inventory_items:
            for inventory_item in inventory_items:
                img_src = '{}/{}'.format(src, inventory_item['image'])
        else:
            img_src = '{}/{}'.format(src, 'img/inventory/question.png')

        return img_src

    def tagsToPrint(self, item_id):
        iitems = self.where({'item_id': item_id})
        tags = 1
        if iitems:
            for item in iitems:
                tags = item['tags']

        return int(tags)

    def getInventoryId(self, item_id):
        iitems = self.where({'item_id': item_id})
        inventory_id = ''
        if iitems:
            for item in iitems:
                inventory_id = item['inventory_id']

        return inventory_id

    def getItemName(self, item_id):
        iitems = self.where({'item_id': item_id})
        item_name = ''
        if iitems:
            for item in iitems:
                item_name = item['name']

        return item_name

    def getLaundry(self, item_id):
        iitems = self.where({'item_id': item_id})
        inventory_id = False
        if iitems:
            for item in iitems:
                inventory_id = item['inventory_id']

        if inventory_id:
            inventories = Inventory().where({'inventory_id': inventory_id})
            if inventories:
                for inventory in inventories:
                    return inventory['laundry']
        else:
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
