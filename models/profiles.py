import datetime
import time
import sqlite3
from models.model import *

unix = time.time()
now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
table = 'profiles'


class Profile:
    id = None
    p_id = None
    user_id = None
    company_id = None
    profile_id = None
    status = None
    deleted_at = None
    created_at = now
    updated_at = now

    def __init__(self):
        self._setUp()

    def create_table(self):
        table_schema = ', '.join([PrimaryKeyField(column='id').data_type(),
                                  IntegerField(column='p_id').data_type(),
                                  IntegerField(column='user_id').data_type(),
                                  IntegerField(column='company_id').data_type(),
                                  IntegerField(column='profile_id').data_type(),
                                  IntegerField(column='status').data_type(),
                                  TextField(column='deleted_at').data_type(),
                                  TextField(column='created_at').data_type(),
                                  TextField(column='updated_at').data_type(),
                                  ])

        self.c.execute('''CREATE TABLE IF NOT EXISTS {t} ({ts})'''.format(t=table, ts=table_schema))
        self.conn.commit()
        self._tearDown()

    def add(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        self.created_at = now
        self.c.execute('''INSERT INTO {t}(p_id,user_id,company_id,profile_id,status,created_at,updated_at)
VALUES(?,?,?,?,?,?,?)'''.format(t=table), (self.p_id,
                                           self.user_id,
                                           self.company_id,
                                           self.profile_id,
                                           self.status,
                                           self.created_at,
                                           self.updated_at)
                       )

        self.conn.commit()
        self._tearDown()
        return True

    def add_special(self):
        self.c.execute('''INSERT INTO {t}(p_id,user_id,company_id,profile_id,status,created_at,updated_at)
VALUES(?,?,?,?,?,?,?)'''.format(t=table), (self.p_id,
                                           self.user_id,
                                           self.company_id,
                                           self.profile_id,
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
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        self.c.execute('''UPDATE {t} SET p_id= ?, profile_id = ?, user_id = ?, company_id = ?, status = ?,
updated_at = ? WHERE id = ?'''.format(t=table), (self.p_id,
                                                 self.profile_id,
                                                 self.user_id,
                                                 self.company_id,
                                                 self.status,
                                                 self.updated_at,
                                                 self.id)
                       )

        self.conn.commit()
        self._tearDown()
        return True

    def update_special(self):
        self.c.execute('''UPDATE {t} SET p_id= ?, profile_id = ?, user_id = ?, company_id = ?, status = ?,
updated_at = ? WHERE id = ?'''.format(t=table), (self.p_id,
                                                 self.profile_id,
                                                 self.user_id,
                                                 self.company_id,
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
            self._tearDown()
            return True
        else:
            self._tearDown()
            return False

    def truncate(self):

        self.c.execute("""DELETE FROM {t}""".format(t=table))
        self.conn.commit()
        self.c.execute("""DELETE FROM SQLITE_SEQUENCE WHERE name='{t}'""".format(t=table))
        self.conn.commit()
        self._tearDown()

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