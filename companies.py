import datetime
import time
import sqlite3


class Company:
    def __init__(self):
        """Create the database and the table if they do not exist"""
        self.unix = time.time()
        self.now = str(datetime.datetime.fromtimestamp(self.unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.conn = sqlite3.connect('./db/jayscleaners.db')
        self.c = self.conn.cursor()
        self.create_table()

    def create_table(self):
        table_columns = 'id INTEGER PRIMARY KEY, ' \
                        'company_id INTEGER NULL, ' \
                        'name CHAR(100) NULL, ' \
                        'street CHAR(200) NULL, ' \
                        'suite CHAR(20) NULL, ' \
                        'city CHAR(100) NULL, ' \
                        'state CHAR(25) NULL, ' \
                        'zipcode CHAR(20) NULL, ' \
                        'email CHAR(150) NULL, ' \
                        'phone CHAR(20) NULL, ' \
                        'store_hours TEXT NULL, ' \
                        'turn_around TEXT NULL, ' \
                        'api_key TEXT NULL, ' \
                        'deleted_at TEXT NULL, ' \
                        'created_at TEXT NULL, ' \
                        'updated_at TEXT NULL, ' \
                        'server_at TEXT NULL'

        self.c.execute('CREATE TABLE IF NOT EXISTS companies ({})'.format(table_columns))

    def add(self, data=False):
        print(data['company_id'])

        if data:

            company_id = data['company_id'] if data['company_id'] else None
            name = data['name'] if data['name'] else None
            street = data['street'] if data['street'] else None
            suite = data['suite'] if data['suite'] else None
            city = data['city'] if data['city'] else None
            state = data['state'] if data['state'] else None
            zipcode = data['zipcode'] if data['zipcode'] else None
            email = data['email'] if data['email'] else None
            phone = data['phone'] if data['phone'] else None
            api_key = data['api_key'] if data['api_key'] else None
            created_at = self.now
            updated_at = self.now

            self.c.execute('''INSERT INTO companies(company_id,name,street,suite,city,state,zipcode,email,phone,api_key,
created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',(company_id,
                                                           name,
                                                           street,
                                                           suite,
                                                           city,
                                                           state,
                                                           zipcode,
                                                           email,
                                                           phone,
                                                           api_key,
                                                           created_at,
                                                           updated_at)
                           )
            self.conn.commit()

            return True
        else:
            return False

        def edit(self, data=False):

            if data:
                updated_at = self.now

                self.c.execute('UPDATE companies SET'+
                               ' company_id = '+data['company_id'] if data['company_id'] else '' +
                               ' name = '+data['name'] if data['name'] else ''+
                               ' street = '+data['street'] if data['street'] else '' +
                               ' suite = '+data['suite'] if data['suite'] else '' +
                               ' city = '+data['city'] if data['city'] else '' +
                               ' state = '+data['state'] if data['state']  else '' +
                               ' zipcode = '+data['zipcode'] if data['zipcode'] else ''+
                               ' email = '+data['email'] if data['email'] else ''+
                               ' phone = '+data['phone'] if data['phone'] else ''+
                               ' api_key = '+data['api_key'] if data['api_key'] else ''+
                               ' updated_at = ? '+
                               ' WHERE company_id = ?', (updated_at, data['company_id']))

                self.conn.commit()

                return True
            else:
                return False

    def close_connection(self):
        self.c.close()
        self.conn.close()
