import re


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
