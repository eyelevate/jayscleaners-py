import re
import time
import datetime
import phonenumbers
from decimal import Decimal, ROUND_05UP, ROUND_HALF_UP, DecimalException


class Job:

    def is_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def make_numeric(self,data, *args, **kwargs):
        regex = re.compile(r'[^\d.]+')
        return regex.sub('', data)

    def make_no_whitespace(self, data, *args, **kwargs):
        return data.rstrip()

    def make_alpha_numeric(self, data, *args, **kwargs):
        regex = re.compile(r'[\W_]+')
        return regex.sub('',data)

    def check_valid_email(self,email, *args, **kwargs):
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
            return False
        else:
            return True

    def check_valid_phone(self, phone, *args, **kwargs):
        if len(self.make_numeric(phone)) == 10:
            return True
        else:
            return False

    def date_leading_zeroes(self, num):
        return "%02d" % (num,)

    def make_us_phone(self, num):
        country_code = '+1'
        x_phone = phonenumbers.parse('{}{}'.format(country_code,str(num)),None)
        return phonenumbers.format_number(x_phone, phonenumbers.PhoneNumberFormat.NATIONAL)

    def round_up(self, amount):
        cents = Decimal('0.01')
        try:
            currency = Decimal(amount).quantize(cents, ROUND_HALF_UP)
        except (ValueError, DecimalException):
            currency = Decimal(amount)

        return currency


