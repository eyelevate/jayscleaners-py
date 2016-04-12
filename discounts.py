from peewee import *

db = SqliteDatabase('db/discounts.db')

class Discount(Model):

    id = PrimaryKeyField()
    discount_id = IntegerField(null=True)
    company_id = IntegerField(null=True)
    inventory_id = IntegerField(null=True)
    inventory_item_id = IntegerField(null=True)
    name = CharField(max_length=50, null=True)
    type = IntegerField(null=True)
    discount = DecimalField(max_digits=11, decimal_places=2)
    rate = DecimalField(max_digits=6, decimal_places=4)
    end_time = CharField(max_length=25, null=True)
    start_date = DateTimeField(null=True)
    end_date = DateTimeField(null=True)
    status = IntegerField(null=True)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)


    class Meta:
        database = db