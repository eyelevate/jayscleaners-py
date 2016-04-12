
import datetime
from peewee import *
#!/usr/bin/env python3

db = SqliteDatabase('db/companies.db')


class Company(Model):
    id = PrimaryKeyField()
    company_id = IntegerField(null=True)
    name = CharField(max_length=50, null=True)
    street = CharField(max_length=200, null=True)
    suite = CharField(max_length=50, null=True)
    city = CharField(max_length=50, null=True)
    state = CharField(max_length=2, null=True)
    zipcode = CharField(max_length=10, null=True)
    email = CharField(max_length=255, null=True)
    phone = CharField(max_length=15, null=True)
    store_hours = TextField(null=True)
    turn_around = TextField(null=True)
    api_key = CharField(max_length=20, null=True)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    server_at = DateTimeField(null=True)

    class Meta:
        database = db


def initialize():
    """Create the database and the table if they do not exist"""
    db.connect()
    db.create_tables([Company], safe=True)


def add(data):
    """Add a user"""

    if data:
        initialize()
        Company.create(
            # username=data['username'] if data['username'] else None,
            company_id=data['company_id'] if data['company_id'] else None,
            name=data['name'] if data['name'] else None,
            street=data['street'] if data['street'] else None,
            suite=data['suite'] if data['suite'] else None,
            city=data['city'] if data['city'] else None,
            state=data['state'] if data['state'] else None,
            zipcode=data['zipcode'] if data['zipcode'] else None,
            email=data['email'] if data['email'] else None,
            phone=data['phone'] if data['phone'] else None,
            api_key=data['api_key'] if data['api_key'] else None
        )

        return True
    else:
        return False
