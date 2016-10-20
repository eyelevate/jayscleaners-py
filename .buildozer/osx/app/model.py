

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class PrimaryKeyField:
    def __init__(self, column=None):
        self.column = column
        super(PrimaryKeyField, self).__init__()

    def data_type(self):
        return '{c} INTEGER PRIMARY KEY'.format(c=self.column)


class IntegerField:
    def __init__(self, column=None):
        self.column = column
        super(IntegerField, self).__init__()

    def data_type(self):
        return '{c} INTEGER NULL'.format(c=self.column)


class CharField:
    def __init__(self, column=None, max_length=255):
        self.column = column
        self.max_length = max_length
        super(CharField, self).__init__()

    def data_type(self):
        return '{c} CHAR({ml}) NULL'.format(c=self.column, ml=self.max_length)


class TextField:
    def __init__(self, column=None):
        self.column = column
        super(TextField, self).__init__()

    def data_type(self):
        return '{c} TEXT NULL'.format(c=self.column)


class FloatField:
    def __init__(self, column=None):
        self.column = column
        super(FloatField, self).__init__()

    def data_type(self):
        return '{c} REAL NULL'.format(c=self.column)


