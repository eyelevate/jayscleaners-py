import datetime
import time
import sqlite3
from model import *


table = 'invoices'


class Invoice:
    id = None
    invoice_id = None
    company_id = None
    customer_id = None
    quantity = None
    pretax = None
    tax = None
    reward_id = None
    discount_id = None
    total = None
    rack = None
    rack_date = None
    due_date = None
    memo = None
    schedule_id = None
    transaction_id = None
    status = None
    deleted_at = None
    created_at = None
    updated_at = None

    def __init__(self):
        """Create the database and the table if they do not exist"""
        try:
            self.conn = sqlite3.connect('./db/jayscleaners.db')
        except sqlite3.OperationalError:
            self.conn = sqlite3.connect('jayscleaners.db')
        self.conn.row_factory = dict_factory
        self.c = self.conn.cursor()

    def create_table(self):

        table_schema = ', '.join([PrimaryKeyField(column='id').data_type(),
                                  IntegerField(column='invoice_id').data_type(),
                                  IntegerField(column='company_id').data_type(),
                                  IntegerField(column='customer_id').data_type(),
                                  IntegerField(column='quantity').data_type(),
                                  FloatField(column='pretax').data_type(),
                                  FloatField(column='tax').data_type(),
                                  IntegerField(column='reward_id').data_type(),
                                  IntegerField(column='discount_id').data_type(),
                                  FloatField(column='total').data_type(),
                                  CharField(column='rack', max_length=10).data_type(),
                                  TextField(column='rack_date').data_type(),
                                  TextField(column='due_date').data_type(),
                                  TextField(column='memo').data_type(),
                                  IntegerField(column='transaction_id').data_type(),
                                  IntegerField(column='schedule_id').data_type(),
                                  IntegerField(column='status').data_type(),
                                  TextField(column='deleted_at').data_type(),
                                  TextField(column='created_at').data_type(),
                                  TextField(column='updated_at').data_type(),
                                  ])

        self.c.execute('''CREATE TABLE IF NOT EXISTS {t} ({ts})'''.format(t=table, ts=table_schema))
        self.conn.commit()

    def add(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        self.created_at = now
        self.c.execute('''INSERT INTO {t}(invoice_id,company_id,customer_id,quantity,pretax,tax,reward_id,discount_id,
total,rack,rack_date,due_date,memo,transaction_id,schedule_id,status,created_at,updated_at)
VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.invoice_id,
                                                                 self.company_id,
                                                                 self.customer_id,
                                                                 self.quantity,
                                                                 self.pretax,
                                                                 self.tax,
                                                                 self.reward_id,
                                                                 self.discount_id,
                                                                 self.total,
                                                                 self.rack,
                                                                 self.rack_date,
                                                                 self.due_date,
                                                                 self.memo,
                                                                 self.transaction_id,
                                                                 self.schedule_id,
                                                                 self.status,
                                                                 self.created_at,
                                                                 self.updated_at)
                       )

        self.conn.commit()
        return True

    def put(self, where=False, data=False):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        sql = '''UPDATE {t} SET '''.format(t=table)
        if len(data) > 0:
            for key, value in data.items():
                if value is None:
                    sql += '''{k} = NULL, '''.format(k=key, v=value)
                else:
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

        return True

    def update(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))

        self.c.execute('''UPDATE {t} SET invoice_id = ?, company_id = ?, customer_id = ?, quantity = ?, pretax = ?,
tax = ?, reward_id = ?, discount_id = ?, total = ?, rack = ?, rack_date = ?, due_date = ?, memo = ?, transaction_id =?,
schedule_id = ?, status = ?, updated_at = ? WHERE id = ?'''.format(t=table), (self.invoice_id,
                                                                              self.company_id,
                                                                              self.customer_id,
                                                                              self.quantity,
                                                                              self.pretax,
                                                                              self.tax,
                                                                              self.reward_id,
                                                                              self.discount_id,
                                                                              self.total,
                                                                              self.rack,
                                                                              self.rack_date,
                                                                              self.due_date,
                                                                              self.memo,
                                                                              self.transaction_id,
                                                                              self.schedule_id,
                                                                              self.status,
                                                                              self.updated_at,
                                                                              self.id)
                       )

        self.conn.commit()
        return True

    def find(self):

        try:
            self.c.execute("""SELECT * FROM {t} WHERE deleted_at is null AND id = ?""".format(table), (str(self.id)))
            self.conn.commit()
        except ValueError:
            return "Could not find the company with that id"
        finally:
            return self.c.fetchone()

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
            return self.c.fetchone()
        else:
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

            return self.c.fetchall()
        else:
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
            return self.c.fetchall()
        else:
            return False

    def delete(self):
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

            return True
        else:
            return False

    def get_id(self, invoice_id):
        invoices = self.where({'invoice_id': invoice_id})
        if invoices:
            for invoice in invoices:
                id = invoice['id']
                return id
        else:
            return False
    def truncate(self):

        self.c.execute("""DELETE FROM {t}""".format(t=table))
        self.conn.commit()
        self.c.execute("""DELETE FROM SQLITE_SEQUENCE WHERE name='{t}'""".format(t=table))
        self.conn.commit()

    def get_last_insert_id(self):
        sql = '''SELECT last_insert_rowid();'''
        self.c.execute(sql)
        self.conn.commit()
        rows = self.c.fetchone()
        return rows['last_insert_rowid()']

    def close_connection(self):
        self.c.close()
        self.conn.close()
