from peewee import *

db = SqliteDatabase('db/reward_transactions.db')

class RewardTransaction(Model):

    id = PrimaryKeyField()
    reward_id = IntegerField(null=True)
    transaction_id = IntegerField(null=True)
    customer_id = IntegerField(null=True)
    employee_id = IntegerField(null=True)
    company_id = IntegerField(null=True)
    type = IntegerField(null=True)
    points = IntegerField(null=True)
    credited = IntegerField(null=True)
    reduced = IntegerField(null=True)
    running_total = IntegerField(null=True)
    reason = IntegerField(null=True)
    name = CharField(max_length=100,null=True)
    status = IntegerField(null=True)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)


    class Meta:
        database = db

def initialize():
    """Create the database and the table if they do not exist"""
    db.connect()
    db.create_tables([RewardTransaction],safe=True)