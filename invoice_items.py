from peewee import *

db = SqliteDatabase('db/invoice_items.db')

class InvoiceItem(Model):

    id = PrimaryKeyField()
    invoice_items_id = IntegerField(null=True)
    invoice_id = IntegerField(null=True)
    item_id = IntegerField(null=True)
    company_id = IntegerField(null=True)
    customer_id = IntegerField(null=True)
    quantity = IntegerField(null=True)
    color = IntegerField(null=True)
    memo = TextField(null=True)
    pretax = DecimalField(max_digits=11,decimal_places=2,null=True)
    tax = DecimalField(max_digits=11, decimal_places=2, null=True)
    total = DecimalField(max_digits=11, decimal_places=2, null=True)
    status = IntegerField(null=True)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)


    class Meta:
        database = db