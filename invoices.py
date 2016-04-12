from peewee import *

db = SqliteDatabase('db/invoices.db')

class Invoice(Model):

    id = PrimaryKeyField()
    invoice_id = IntegerField(null=True)
    company_id = IntegerField(null=True)
    customer_id = IntegerField(null=True)
    quantity = IntegerField(null=True)
    pretax = DecimalField(max_digits=11,decimal_places=2,null=True)
    tax = DecimalField(max_digits=11, decimal_places=2, null=True)
    reward_id = IntegerField(null=True)
    discount_id = IntegerField(null=True)
    total = DecimalField(max_digits=11, decimal_places=2, null=True)
    rack = CharField(max_length=10, null=True)
    rack_date = DateTimeField(null=True)
    due_date = DateTimeField(null=True)
    memo = TextField(null=True)
    status = IntegerField(null=True)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)


    class Meta:
        database = db