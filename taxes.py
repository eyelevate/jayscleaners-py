from peewee import *

db = SqliteDatabase('db/taxes.db')

class Tax(Model):

    id = PrimaryKeyField()
    tax_id = IntegerField(null=True)
    company_id = IntegerField(null=True)
    rate = DecimalField(max_digits=6,decimal_places=4,null=True)
    status = IntegerField(null=True)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)


    class Meta:
        database = db

def initialize():
    """Create the database and thew table if they do not exist"""
    db.connect()
    db.create_tables([Tax],safe=True)