import datetime
import time
import sqlite3
import authorize
from model import *
from companies import Company

unix = time.time()
now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
table = 'cards'


class Card:
    id = None
    card_id = None
    company_id = None
    user_id = None
    profile_id = None
    payment_id = None
    root_payment_id = None
    street = None
    suite = None
    city = None
    state = None
    zipcode = None
    exp_month = None
    exp_year = None
    status = None
    deleted_at = None
    created_at = now
    updated_at = now
    last_four = None
    card_type = None

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
                                  IntegerField(column='card_id').data_type(),
                                  IntegerField(column='company_id').data_type(),
                                  IntegerField(column='user_id').data_type(),
                                  IntegerField(column='profile_id').data_type(),
                                  IntegerField(column='payment_id').data_type(),
                                  IntegerField(column='root_payment_id').data_type(),
                                  TextField(column='street').data_type(),
                                  TextField(column='suite').data_type(),
                                  TextField(column='city').data_type(),
                                  TextField(column='state').data_type(),
                                  TextField(column='zipcode').data_type(),
                                  TextField(column='exp_month').data_type(),
                                  TextField(column='exp_year').data_type(),
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
        self.c.execute('''INSERT INTO {t}(card_id,company_id,user_id,profile_id,payment_id,root_payment_id,street,suite,
city,state,zipcode,exp_month, exp_year,status,created_at,updated_at)
VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.card_id,
                                                             self.company_id,
                                                             self.user_id,
                                                             self.profile_id,
                                                             self.payment_id,
                                                             self.root_payment_id,
                                                             self.street,
                                                             self.suite,
                                                             self.city,
                                                             self.state,
                                                             self.zipcode,
                                                             self.exp_month,
                                                             self.exp_year,
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
        self.updated_at = now
        self.c.execute('''UPDATE {t} SET card_id = ?, company_id = ?, user_id = ?, profile_id = ?, payment_id = ?,
root_payment_id = ?, street = ?, suite = ?, city = ?, state = ?, zipcode = ?, exp_month = ?, exp_year = ?, status = ?,
updated_at = ? WHERE id = ?'''.format(t=table), (self.card_id,
                                                 self.company_id,
                                                 self.user_id,
                                                 self.profile_id,
                                                 self.payment_id,
                                                 self.root_payment_id,
                                                 self.street,
                                                 self.suite,
                                                 self.city,
                                                 self.state,
                                                 self.zipcode,
                                                 self.exp_month,
                                                 self.exp_year,
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

    def close_connection(self):
        self.c.close()
        self.conn.close()

    def connectAuthNet(self, company_id):
        payment_api_login = False
        payment_gateway_id = False
        comps = Company()
        companies = comps.where({'id': company_id})
        if companies:
            for company in companies:
                payment_api_login = str(company['payment_api_login'])
                payment_gateway_id = str(company['payment_gateway_id'])
        if payment_api_login and payment_gateway_id:
            authorize.Configuration.configure(
                authorize.Environment.TEST,
                payment_api_login,
                payment_gateway_id,
            )
            # authorize.Configuration.configure(
            #     authorize.Environment.PRODUCTION,
            #     'api_login_id',
            #     'api_transaction_key',
            # )

            return True
        else:
            return False

    def collect(self, company_id, profile_id):
        profile_id = str(profile_id)
        auth_connect = self.connectAuthNet(company_id)
        if profile_id and profile_id is not None :

            if auth_connect:

                cards = self.where({'company_id': company_id, 'profile_id': profile_id})
                cards_update = []
                if cards:
                    for card in cards:
                        payment_id = str(card['payment_id'])
                        result = authorize.CreditCard.details(profile_id, payment_id)
                        last_four = result.payment_profile.payment.credit_card.card_number
                        card_type = result.payment_profile.payment.credit_card.card_type
                        card['last_four'] = last_four
                        card['card_type'] = card_type
                        card['first_name'] = result.payment_profile.bill_to.first_name
                        card['last_name'] = result.payment_profile.bill_to.last_name
                        cards_update.append(card)

                return cards_update
            else:
                return False
        else:
            return False

    def create_profile(self, company_id, data):

        if self.connectAuthNet(company_id):
            try:
                result = authorize.Customer.create(data)
                print(result)
                if result.messages:
                    for response in result.messages:
                        if response['result_code'] == 'Ok':

                            return {'status': True,
                                    'profile_id': result.customer_id,
                                    'payment_id': result.payment_ids[0]}
                        else:
                            return {
                                'status': False,
                                'message': result.messages.text
                            }
                else:
                    return {
                        'status':False,
                        'message': 'Could not connect to server. Please try again'
                    }
            except authorize.exceptions.AuthorizeResponseError:
                return {'status':False,
                        'message': authorize.exceptions.AuthorizeResponseError}
            except authorize.exceptions.AuthorizeInvalidError:
                error_message = 'There were problems validating your card. Please try again.'


                return {'status':False,
                        'message': error_message}

        else:
            return {'status':False,
                    'message': 'Could not authenticate with authorize.net'}
        pass

    def create_card(self,company_id, profile_id, data):
        if self.connectAuthNet(company_id):
            try:
                result = authorize.CreditCard.create(str(profile_id), data)
                print(result)
                if result.messages:
                    for response in result.messages:
                        if response['result_code'] == 'Ok':

                            return {'status': True,
                                    'profile_id': result.customer_id,
                                    'payment_id': result.payment_id}
                        else:
                            return {
                                'status': False,
                                'message': response['messages']
                            }
                else:
                    return {
                        'status':False,
                        'message': 'Could not connect to server. Please try again'
                    }

            except authorize.exceptions.AuthorizeResponseError:
                return {'status':False,
                        'message':authorize.exceptions.AuthorizeResponseError}
            except authorize.exceptions.AuthorizeInvalidError:
                error_message = ''
                for key, value in authorize.exceptions.AuthorizeInvalidError:
                    error_message = 'Error: {} field has an error of "{}"'.format(key, value)
                return {'status':False,
                        'message':error_message}
        else:
            return {'status': False,
                    'message': 'Could not authenticate with server'}

    def card_update(self,company_id, profile_id, payment_id, data):

        if self.connectAuthNet(company_id):

            try:
                result = authorize.CreditCard.update(str(profile_id), str(payment_id),data)
                return {'status':True,
                        'message':'Successfully updated credit cards with all companies'}
            except authorize.exceptions.AuthorizeResponseError:
                return {'status':False,
                        'message':authorize.exceptions.AuthorizeResponseError}
        else:
            return {'status': False,
                    'message': 'Could not authenticate with server'}

    def validate_card(self, company_id, profile_id, payment_id):
        if self.connectAuthNet(company_id):
            try:
                result = authorize.CreditCard.validate(str(profile_id), str(payment_id), {
                    'validationMode': 'liveMode'
                })
                print(result)
                if result.messages:
                    for response in result.messages:
                        if response['result_code'] == 'Ok':

                            return {'status': True,
                                    'message': 'Card has been validated, and can can be used for this transaction.'}
                        else:
                            return {
                                'status': False,
                                'message': response['message']['text ']
                            }
                else:
                    return {
                        'status': False,
                        'message': 'Could not connect to server. Please try again'
                    }

            except authorize.exceptions.AuthorizeResponseError:
                return {'status': False,
                        'message': authorize.exceptions.AuthorizeResponseError}
            except authorize.exceptions.AuthorizeInvalidError:
                error_message = 'Error: there were problems with your validation. please use another card'

                return {'status': False,
                        'message': error_message}
        else:
            return {'status': False,
                    'message': 'Could not authenticate with server'}