import re
import time
import datetime
import phonenumbers
from decimal import Decimal, ROUND_05UP, ROUND_HALF_UP, DecimalException
from operator import itemgetter as i
from functools import cmp_to_key

class Job:
    @staticmethod
    def is_int(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def make_numeric(data, *args, **kwargs):
        regex = re.compile(r'[^\d.]+')
        return regex.sub('', data)

    @staticmethod
    def make_no_whitespace(data, *args, **kwargs):
        return data.rstrip()

    @staticmethod
    def make_alpha_numeric(data, *args, **kwargs):
        regex = re.compile(r'[\W_]+')
        return regex.sub('',data)

    @staticmethod
    def check_valid_email(email, *args, **kwargs):
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
            return False
        else:
            return True

    def check_valid_phone(self, phone, *args, **kwargs):
        if len(self.make_numeric(phone)) == 10:
            return True
        else:
            return False

    @staticmethod
    def date_leading_zeroes(num):
        return "%02d" % (num,)

    @staticmethod
    def make_us_phone(num):
        country_code = '+1'
        x_phone = phonenumbers.parse('{}{}'.format(country_code,str(num)),None)
        return phonenumbers.format_number(x_phone, phonenumbers.PhoneNumberFormat.NATIONAL)

    @staticmethod
    def round_up(amount):
        cents = Decimal('0.01')
        try:
            currency = Decimal(amount).quantize(cents, ROUND_HALF_UP)
        except (ValueError, DecimalException):
            currency = Decimal(amount)

        return currency


