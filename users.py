import datetime
from peewee import *

db = SqliteDatabase('db/users.db')


class User(Model):
    id = PrimaryKeyField()
    user_id = IntegerField(null=True)
    company_id = IntegerField(null=True)
    username = CharField(max_length=50, null=True)
    first_name = CharField(max_length=50, null=True)
    last_name = CharField(max_length=50, null=True)
    street = CharField(max_length=200, null=True)
    suite = CharField(max_length=50, null=True)
    city = CharField(max_length=50, null=True)
    state = CharField(max_length=2, null=True)
    zipcode = CharField(max_length=10, null=True)
    email = CharField(max_length=255, null=True)
    phone = CharField(max_length=15, null=True)
    intercom = CharField(max_length=20, null=True)
    concierge_name = CharField(max_length=50, null=True)
    concierge_number = CharField(max_length=20, null=True)
    special_instructions = TextField(null=True)
    shirt_old = CharField(max_length=10, null=True)
    shirt = IntegerField(null=True)
    delivery = IntegerField(null=True)
    profile_id = CharField(null=True)
    payment_status = IntegerField(null=True)
    payment_id = CharField(max_length=11, null=True)
    token = CharField(max_length=8, null=True)
    api_token = CharField(max_length=20, null=True)
    reward_status = IntegerField(null=True)
    reward_points = IntegerField(null=True)
    account = BooleanField(default=False)
    starch = IntegerField(null=True)
    important_memo = TextField(null=True)
    invoice_memo = TextField(null=True)
    password = CharField(max_length=60, null=True)
    role_id = IntegerField(null=True)
    deleted_at = DateTimeField(null=True)
    remember_token = CharField(max_length=100, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


def initialize():
    """Connects to database and/or Create the database and the table if they do not exist"""
    db.connect()
    db.create_tables([User], safe=True)


def add(data):
    """Add a user"""

    if data:
        initialize()
        User.create(
            # username=data['username'] if data['username'] else None,
            company_id = data['company_id'] if data['company_id'] else None,
            first_name=data['first_name'] if data['first_name'] else None,
            last_name=data['last_name'] if data['last_name'] else None,
            # street=data['street'] if data['street'] else None,
            # suite=data['suite'] if data['suite'] else None,
            # city=data['city'] if data['city'] else None,
            # state=data['state'] if data['state'] else None,
            # zipcode=data['zipcode'] if data['zipcode'] else None,
            email=data['email'] if data['email'] else None,
            phone=data['phone'] if data['phone'] else None,
            # intercom=data['intercom'] if data['intercom'] else None,
            # concierge_name=data['concierge_name'] if data['concierge_name'] else None,
            # concierge_number=data['concierge_number'] if data['concierge_number'] else None,
            # special_instructions=data['special_instructions'] if data['special_instructions'] else None,
            # shirt_old=data['shirt_old'] if data['shirt_old'] else None,
            # shirt=data['shirt'] if data['shirt'] else None,
            # delivery=data['delivery'] if data['delivery'] else None,
            # profile_id=data['profile_id'] if data['profile_id'] else None,
            # payment_status=data['payment_status'] if data['payment_status'] else None,
            # payment_id=data['payment_id'] if data['payment_id'] else None,
            # token=data['token'] if data['token'] else None,
            # api_token=data['api_token'] if data['api_token'] else None,
            # reward_status=data['reward_status'] if data['reward_status'] else None,
            # reward_points=data['reward_points'] if data['reward_points'] else None,
            # account=data['delivery'] if data['delivery'] else None,
            # starch=data['delivery'] if data['delivery'] else None,
            # important_memo=data['delivery'] if data['delivery'] else None,
            # invoice_memo=data['delivery'] if data['delivery'] else None,
            # password=data['delivery'] if data['delivery'] else None,
            # role_id=data['delivery'] if data['delivery'] else None,
            # deleted_at=data['delivery'] if data['delivery'] else None,
            # remember_token=data['delivery'] if data['delivery'] else None,
            # created_at=created_at,
            # updated_at=updated_at
        )

        return True
    else:
        return False



def edit(data):
    """Edit a user"""

    if data:
        initialize()
        User.update(content=data)


def delete(data):
    """Deletes an instance of a user"""
    if data:
        initialize()
        User.delete_instance(data)
    else:
        return False


def retrieve(self, search_query=None):
    """View all users or by query"""
    self.initialize()
    users = User.select().order_by(User.id.desc())

    if search_query:
        users = users.where(User.content.contains(search_query))

    return users
