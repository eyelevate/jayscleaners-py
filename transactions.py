from peewee import *

db = SqliteDatabase('db/transactions.db')

class Transaction(Model):

    id = PrimaryKeyField()
    transaction_id = IntegerField(null=True)
    company_id = IntegerField(null=True)
    customer_id = IntegerField(null=True)
    schedule_id = IntegerField(null=True)
    pretax = DecimalField(max_digits=11,decimal_places=2,null=True)
    tax = DecimalField(max_digits=11, decimal_places=2, null=True)
    aftertax = DecimalField(max_digits=11, decimal_places=2, null=True)
    discount = DecimalField(max_digits=11, decimal_places=2, null=True)
    total = DecimalField(max_digits=11, decimal_places=2, null=True)
    invoices = TextField(null=True)
    type = IntegerField(null=True)
    last_four = IntegerField(null=True)
    tendered = DecimalField(max_digits=11,decimal_places=2,null=True)
    transaction_id = IntegerField(null=True)
    status = IntegerField(null=True)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)


    class Meta:
        database = db

def initialize():
    """Create the database and the table if they do not exist"""
    db.connect()
    db.create_tables([Transaction],safe=True)