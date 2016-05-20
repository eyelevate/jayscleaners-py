import datetime
import time
import sqlite3
from model import *

unix = time.time()
now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
table = 'transactions'


class Transaction:
    id = None
    transaction_id = None
    company_id = None
    customer_id = None
    schedule_id = None
    pretax = None
    tax = None
    aftertax = None
    discount = None
    total = None
    invoices = None
    type = None
    last_four = None
    tendered = None
    status = None
    deleted_at = None
    created_at = None
    updated_at = None

    def __init__(self):
        """Create the database and the table if they do not exist"""
        self.conn = sqlite3.connect('./db/jayscleaners.db')
        self.conn.row_factory = dict_factory
        self.c = self.conn.cursor()

    def create_table(self):
        table_schema = ', '.join([PrimaryKeyField(column='id').data_type(),
                                  IntegerField(column='transaction_id').data_type(),
                                  IntegerField(column='company_id').data_type(),
                                  IntegerField(column='customer_id').data_type(),
                                  IntegerField(column='schedule_id').data_type(),
                                  FloatField(column='pretax').data_type(),
                                  FloatField(column='tax').data_type(),
                                  FloatField(column='aftertax').data_type(),
                                  FloatField(column='discount').data_type(),
                                  FloatField(column='total').data_type(),
                                  TextField(column='invoices').data_type(),
                                  IntegerField(column='type').data_type(),
                                  IntegerField(column='last_four').data_type(),
                                  FloatField(column='tendered').data_type(),
                                  IntegerField(column='status').data_type(),
                                  TextField(column='deleted_at').data_type(),
                                  TextField(column='created_at').data_type(),
                                  TextField(column='updated_at').data_type(),
                                  ])

        self.c.execute('''CREATE TABLE IF NOT EXISTS {t} ({ts})'''.format(t=table, ts=table_schema))
        self.conn.commit()

    def add(self):

        self.c.execute('''INSERT INTO {t}(transaction_id,company_id,customer_id,schedule_id,pretax,tax,aftertax,
discount,total,invoices,type,last_four,tendered,status,deleted_at,created_at,updated_at
VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.transaction_id,
                                                               self.company_id,
                                                               self.customer_id,
                                                               self.schedule_id,
                                                               self.pretax,
                                                               self.tax,
                                                               self.aftertax,
                                                               self.discount,
                                                               self.total,
                                                               self.invoices,
                                                               self.type,
                                                               self.last_four,
                                                               self.tendered,
                                                               self.status,
                                                               self.deleted_at,
                                                               self.created_at,
                                                               self.updated_at)
                       )

        self.conn.commit()
        return True

    def update(self):

        self.c.execute('''UPDATE {t} SET transaction_id = ?, company_id = ?, customer_id = ?, schedule_id = ?,
pretax = ?, tax = ?, aftertax = ?, discount = ?, total = ?, invoices = ?, type = ?, last_four = ?, tendered = ?,
status = ?, updated_at = ? WHERE id = ?'''.format(t=table), (self.transaction_id,
                                                             self.company_id,
                                                             self.customer_id,
                                                             self.schedule_id,
                                                             self.pretax,
                                                             self.tax,
                                                             self.aftertax,
                                                             self.discount,
                                                             self.total,
                                                             self.invoices,
                                                             self.type,
                                                             self.last_four,
                                                             self.tendered,
                                                             self.status,
                                                             self.updated_at,
                                                             self.id)
                       )

        self.conn.commit()
        return True

    def find(self):
        try:
            self.c.execute("""SELECT * FROM {t} WHERE id = ?""".format(table), (str(self.id)))
            self.conn.commit()
        except ValueError:
            return "Could not find the company with that id"
        finally:
            return self.c.fetchone()

        return False

    def first(self, data=False):
        if data:
            sql = '''SELECT * FROM {t} WHERE '''.format(t=table)
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

    def where(self, data=False):
        if data:
            sql = '''SELECT * FROM {t} WHERE '''.format(t=table)
            idx = 0
            order_by = False
            limit = False
            if 'ORDER_BY' in data:
                order_by = data['ORDER_BY']
                del (data['ORDER_BY'])
                print('removed order_by {}'.format(order_by))
            if 'LIMIT' in data:
                limit = data['LIMIT']
                del (data['LIMIT'])
                print('removed limit {}'.format(limit))

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

        if self.id:

            self.c.execute("""UPDATE {t} SET deleted_at = ?, updated_at = ? WHERE id = ?""".format(table),
                           (self.updated_at,
                            self.updated_at,
                            self.id)
                           )

            self.conn.commit()

            return True
        else:
            return False

    def close_connection(self):
        self.c.close()
        self.conn.close()
