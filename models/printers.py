import datetime
import time
import sqlite3

import usb.core
import usb.util
import usb.backend.libusb1

from classes.popups import Popups
from models import sessions
from models.model import *
from os import path
from pathlib import Path

unix = time.time()
now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
table = 'printers'


class Printer:
    id = None
    printer_id = None
    company_id = None
    name = None
    model = None
    nick_name = None
    type = None
    vendor_id = None
    product_id = None
    status = None
    deleted_at = None
    created_at = now
    updated_at = now

    def __init__(self):
        self._setUp()

    def create_table(self):
        table_schema = ', '.join([PrimaryKeyField(column='id').data_type(),
                                  IntegerField(column='printer_id').data_type(),
                                  IntegerField(column='company_id').data_type(),
                                  CharField(column='name', max_length=100).data_type(),
                                  CharField(column='model', max_length=100).data_type(),
                                  CharField(column='nick_name', max_length=100).data_type(),
                                  CharField(column='vendor_id', max_length=100).data_type(),
                                  CharField(column='product_id', max_length=100).data_type(),
                                  IntegerField(column='type').data_type(),
                                  IntegerField(column='status').data_type(),
                                  TextField(column='deleted_at').data_type(),
                                  TextField(column='created_at').data_type(),
                                  TextField(column='updated_at').data_type(),
                                  ])

        self.c.execute('''CREATE TABLE IF NOT EXISTS {t} ({ts})'''.format(t=table, ts=table_schema))
        self.conn.commit()
        self._tearDown()

    def add(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        self.created_at = now
        self.c.execute('''INSERT INTO {t}(printer_id,company_id,name,model,nick_name,vendor_id,product_id,type,status,
created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.printer_id,
                                                                          self.company_id,
                                                                          self.name,
                                                                          self.model,
                                                                          self.nick_name,
                                                                          self.vendor_id,
                                                                          self.product_id,
                                                                          self.type,
                                                                          self.status,
                                                                          self.created_at,
                                                                          self.updated_at)
                       )

        self.conn.commit()
        self._tearDown()
        return True

    def add_special(self):
        self.c.execute('''INSERT INTO {t}(printer_id,company_id,name,model,nick_name,vendor_id,product_id,type,status,
created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.printer_id,
                                                                          self.company_id,
                                                                          self.name,
                                                                          self.model,
                                                                          self.nick_name,
                                                                          self.vendor_id,
                                                                          self.product_id,
                                                                          self.type,
                                                                          self.status,
                                                                          self.created_at,
                                                                          self.updated_at)
                       )

        self.conn.commit()
        self._tearDown()
        return True

    def put(self, where = False, data = False):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        sql = '''UPDATE {t} SET '''.format(t=table)
        if len(data) > 0:
            for key, value in data.items():
                if value is None:
                    sql += '''{k} = NULL, '''.format(k=key, v=value)
                else:
                    sql += '''{k} = "{v}", '''.format(k=key, v=value)
            sql += '''updated_at = "{v}" '''.format(v=self.updated_at)
        sql += '''WHERE '''
        idx = 0
        if len(where) > 0:
            for key, value in where.items():
                idx += 1
                if idx == len(where):
                    sql += '''{k} = {v}'''.format(k=key, v=value)
                else:
                    sql += '''{k} = {v} AND '''.format(k=key, v=value)

        self.c.execute(sql)
        self.conn.commit()
        self._tearDown()
        return True

    def update(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        self.c.execute('''UPDATE {t} SET printer_id = ?, company_id = ?, name = ?, model = ?, nick_name = ?,
vendor_id = ?,product_id = ?,type = ?, status = ?, updated_at = ? WHERE id = ?'''.format(t=table), (self.printer_id,
                                                                                                    self.company_id,
                                                                                                    self.name,
                                                                                                    self.model,
                                                                                                    self.nick_name,
                                                                                                    self.vendor_id,
                                                                                                    self.product_id,
                                                                                                    self.type,
                                                                                                    self.status,
                                                                                                    self.updated_at,
                                                                                                    self.id)
                       )

        self.conn.commit()
        self._tearDown()
        return True

    def update_special(self):
        self.c.execute('''UPDATE {t} SET printer_id = ?, company_id = ?, name = ?, model = ?, nick_name = ?,
vendor_id = ?,product_id = ?,type = ?, status = ?, updated_at = ? WHERE id = ?'''.format(t=table), (self.printer_id,
                                                                                                    self.company_id,
                                                                                                    self.name,
                                                                                                    self.model,
                                                                                                    self.nick_name,
                                                                                                    self.vendor_id,
                                                                                                    self.product_id,
                                                                                                    self.type,
                                                                                                    self.status,
                                                                                                    self.updated_at,
                                                                                                    self.id)
                       )

        self.conn.commit()
        self._tearDown()
        return True

    def find(self):
        try:
            self.c.execute("""SELECT * FROM {t} WHERE deleted_at is null AND id = ?""".format(table), (str(self.id)))
            self.conn.commit()
        except ValueError:
            self._tearDown()
            return "Could not find the company with that id"
        finally:
            fetch = self.c.fetchone()
            self._tearDown()
            return fetch

        return False

    def first(self, data=False):
        if data:
            sql = '''SELECT * FROM {t} WHERE deleted_at is null AND '''.format(t=table)
            idx = 0
            for key, value in data.items():
                idx += 1
                if idx == len(data):
                    sql += '''{k} = {v}'''.format(k=key, v=value)
                elif idx < len(data):
                    sql += '''{k} = {v} AND '''.format(k=key, v=value)

            self.c.execute(sql)
            self.conn.commit()
            fetch = self.c.fetchone()
            self._tearDown()
            return fetch
        else:
            self._tearDown()
            return False

    def where(self, data=False, deleted_at=True):
        if data:
            sql = '''SELECT * FROM {t} WHERE '''.format(t=table)
            idx = 0
            order_by = False
            limit = False
            if 'ORDER_BY' in data:
                order_by = data['ORDER_BY']
                del (data['ORDER_BY'])
            if 'LIMIT' in data:
                limit = data['LIMIT']
                del (data['LIMIT'])

            for key, value in data.items():
                idx += 1
                if isinstance(value, dict):
                    for oper, val in value.items():
                        if idx == len(data):
                            sql += '''{k} {o} {v}'''.format(k=key, o=oper, v=val)

                        elif idx < len(data):
                            sql += '''{k} {o} {v} AND '''.format(k=key, o=oper, v=val)

                else:
                    if idx == len(data):
                        if value is None:
                            sql += '''{k} is null'''.format(k=key)
                        else:
                            sql += '''{k} = {v}'''.format(k=key, v=value)
                    elif idx < len(data):
                        if value is None:
                            sql += '''{k} is null AND '''.format(k=key)
                        else:
                            sql += '''{k} = {v} AND '''.format(k=key, v=value)

            sql += ' AND deleted_at is null' if deleted_at else ''

            if order_by:
                sql += ''' ORDER BY {} '''.format(order_by)

            if limit:
                sql += '''LIMIT {}'''.format(limit)

            self.c.execute(sql)
            self.conn.commit()
            fetch = self.c.fetchall()
            self._tearDown()
            return fetch
        else:
            return False

    def like(self, data=False, deleted_at=True):
        if data:
            sql = '''SELECT * FROM {t} WHERE '''.format(t=table)
            idx = 0
            order_by = False
            limit = False
            if 'ORDER_BY' in data:
                order_by = data['ORDER_BY']
                del (data['ORDER_BY'])
            if 'LIMIT' in data:
                limit = data['LIMIT']
                del (data['LIMIT'])
            for key, value in data.items():
                idx += 1
                if idx == len(data):
                    if value is None:
                        sql += '''{k} is null'''.format(k=key)
                    else:
                        sql += '''{k} LIKE {v}'''.format(k=key, v=value)
                elif idx < len(data):
                    if value is None:
                        sql += '''{k} is null AND '''.format(k=key)
                    else:
                        sql += '''{k} LIKE {v} AND '''.format(k=key, v=value)

            sql += ' AND deleted_at is null ' if deleted_at else ''
            if order_by:
                sql += ''' ORDER BY {} '''.format(order_by)

            if limit:
                sql += '''LIMIT {}'''.format(limit)

            self.c.execute(sql)
            self.conn.commit()
            fetch = self.c.fetchall()
            self._tearDown()
            return fetch
        else:
            self._tearDown()
            return False

    def delete(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        if self.id:

            self.c.execute("""UPDATE {t} SET deleted_at = ?, updated_at = ? WHERE id = ?""".format(table),
                           (self.updated_at,
                            self.updated_at,
                            self.id)
                           )

            self.conn.commit()
            self._tearDown()
            return True
        else:
            self._tearDown()
            return False

    def truncate(self):

        self.c.execute("""DELETE FROM {t}""".format(t=table))
        self.conn.commit()
        self.c.execute("""DELETE FROM SQLITE_SEQUENCE WHERE name='{t}'""".format(t=table))
        self.conn.commit()
        self._tearDown()


    def find_printers(self):
        printers = []

        return printers

    staticmethod
    def backend_location(self, os):
        data_folder = Path("./lib/MS32/dll")

        known_backends = {
            'Linux': path.abspath(data_folder / "libusb-1.0.dll"),
            'Darwin': path.abspath(data_folder / "libusb-1.0.dll"),
            'Windows': "C:/windows/system32/libusb0.dll"
        }
        print('os and path {}'.format(known_backends[os]))
        if path.exists(known_backends[os]):
            print('exists')
            backend_location = usb.backend.libusb01.get_backend(find_library=lambda x: known_backends[os])
            print(backend_location)
            return backend_location
        else:
            print('does not exist')

        return False

    staticmethod
    def printer_list(self):
        known_printers = {
            'epson': {
                'vendorId': 1133,
                'productId': 5047,
                '_vendorId': hex(0x46d),
                '_productId': hex(0xc52b)
            },
            'bixolon': {
                'vendorId': 1133,
                'productId': 5047,
                '_vendorId': hex(0x46d),
                '_productId': hex(0xc52b)
            },
            'zebra': {
                'vendorId': 1133,
                'productId': 5047,
                '_vendorId': hex(0x46d),
                '_productId': hex(0xc52b)
            }
        }

        return known_printers

    def print_setup_tag(self, vendor_id, product_id):
        vendor_int = int(vendor_id, 16)
        product_int = int(product_id, 16)
        # find our device
        backend = usb.backend.libusb1.get_backend(find_library=lambda x: "./lib/libusb-1.0.so")
        dev = usb.core.find(idVendor=vendor_int, idProduct=product_int)

        # was it found?
        if dev is not None:
            print('device found')

            # set the active configuration. With no arguments, the first
            # configuration will be the active one
            dev.set_configuration()

            # get an endpoint instance
            cfg = dev.get_active_configuration()
            intf = cfg[(0, 0)]
            bixolon = usb.util.find_descriptor(
                intf,
                # match the first OUT endpoint
                custom_match= \
                    lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_OUT)

            sessions.put('_bixolon', value=bixolon)

        else:
            sessions.put('_bixolon', value=False)
            Popups.dialog_msg('Printer Error', 'Tag printer not found. Please check settings and try again')

    def print_setup(self, vendor_id, product_id):
        vendor_int = int(vendor_id, 16)
        product_int = int(product_id, 16)
        # find our device
        backend = usb.backend.libusb1.get_backend(find_library=lambda x: "../lib/libusb-1.0.so")
        dev = usb.core.find(idVendor=vendor_int, idProduct=product_int, backend=backend)

        # was it found?
        if dev is not None:
            print('Receipt Device Found')

            # set the active configuration. With no arguments, the first
            # configuration will be the active one
            dev.set_configuration()

            # get an endpoint instance
            cfg = dev.get_active_configuration()
            intf = cfg[(0, 0)]
            epson = usb.util.find_descriptor(
                intf,
                # match the first OUT endpoint
                custom_match= \
                    lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_OUT)
            sessions.put('_epson', value=epson)


        else:
            sessions.put('_epson', value=False)
            Popups.dialog_msg('Printer Error', 'Receipt printer not found. Please check settings and try again')

    def get_printer_ids(self, company_id, type):

        printers = self.where({'company_id': company_id,
                               'type': type})
        if printers:
            for printer in printers:
                vendor_id = printer['vendor_id']
                product_id = printer['product_id']
                ids = (vendor_id, product_id)
        else:
            ids = False

        return ids

    def pcmd(self, key):
        ESC = b'\x1b'
        GS = b'\x1d'
        BARCODE_HEIGHT = GS + b'h'  # Barcode Height [1-255]
        BARCODE_WIDTH = GS + b'w'  # Barcode Width  [2-6]
        # BARCODE HEIGHT 1 - 255
        _SET_BARCODE_TXT_POS = lambda n: GS + b'H' + n
        _SET_HRI_FONT = lambda n: GS + b'f' + n



        data = {
            'HT':b'\x09', # Horizontal Tab
            'LF':b'\n', # Print and Line Feed
            'CR': b'\r', # Print and Carriage Return
            'PFL': ESC + b'\x60\n', # print and feed line
            'INIT': ESC + b'\x40', # Initialize Printer
            'PARTIAL_CUT':b'\x1b\x6d', # Partial Cut
            'INCH1' : ESC + b'\x31', # 1/9 inch paper feed
            'INCH2': ESC +  b'\x32',  # 2/9 inch paper feed
            'TXTTALL':ESC + b'!\x10', # TALL text
            'TXTNORM':ESC + b'!\x00', # Normal text
            'ALGNLEFT': ESC + b'\x61\x00',  # Left justification
            'ALGNCENTER': ESC + b'\x61\x01',  # Centering
            'ALGNRIGHT':  ESC + b'\x61\x02',  # Right justification

            'TXT_NORMAL': ESC + b'!\x00',  # Normal text
            'TXT_2HEIGHT' : ESC + b'!\x10',  # Double height text
            'TXT_2WIDTH' : ESC + b'!\x20',  # Double width text
            'TXT_4SQUARE' : ESC + b'!\x30',  # Quad area text
            'TXT_UNDERL_OFF' : ESC + b'\x2d\x00',  # Underline font OFF
            'TXT_UNDERL_ON' : ESC + b'\x2d\x01',  # Underline font 1-dot ON
            'TXT_UNDERL2_ON' : ESC + b'\x2d\x02',  # Underline font 2-dot ON
            'TXT_BOLD_OFF' : ESC + b'\x45\x00',  # Bold font OFF
            'TXT_BOLD_ON' : ESC + b'\x45\x01',  # Bold font ON
            'TXT_FONT_A' : ESC + b'\x4d\x00',  # Font type A
            'TXT_FONT_B' : ESC + b'\x4d\x01',  # Font type B
            'TXT_ALIGN_LT' : ESC + b'\x61\x00',  # Left justification
            'TXT_ALIGN_CT' : ESC + b'\x61\x01',  # Centering
            'TXT_ALIGN_RT' : ESC + b'\x61\x02',  # Right justification
            'TXT_INVERT_ON' : GS + b'\x42\x01',  # Inverse Printing ON
            'TXT_INVERT_OFF' : GS + b'\x42\x00',  # Inverse Printing OFF
            'BARCODE_TXT_OFF' : _SET_BARCODE_TXT_POS(b'\x00'),  # HRI barcode chars OFF
            'BARCODE_TXT_ABV' : _SET_BARCODE_TXT_POS(b'\x01'),  # HRI barcode chars above
            'BARCODE_TXT_BLW' : _SET_BARCODE_TXT_POS(b'\x02'),  # HRI barcode chars below
            'BARCODE_TXT_BTH' : _SET_BARCODE_TXT_POS(b'\x03'),  # HRI both above and below
            'BARCODE_FONT_A' : _SET_HRI_FONT(b'\x00'),  # Font type A for HRI barcode chars
            'BARCODE_FONT_B' : _SET_HRI_FONT(b'\x01'),  # Font type B for HRI barcode chars'
            'TXT_FLIP_ON' : ESC + b'\x7b\x01',
            'TXT_FLIP_OFF' : ESC + b'\x7b\x00',
            'TXT_SMOOTH_ON' : GS + b'\x62\x01',
            'TXT_SMOOTH_OFF' : GS + b'\x62\x00',
            'TXT_SIZE' : GS + b'!',
            'TXT_WIDTH' : {1: 0x00,
                         2: 0x10,
                         3: 0x20,
                         4: 0x30,
                         5: 0x40,
                         6: 0x50,
                         7: 0x60,
                         8: 0x70},
            'TXT_HEIGHT' : {1: 0x00,
                          2: 0x01,
                          3: 0x02,
                          4: 0x03,
                          5: 0x04,
                          6: 0x05,
                          7: 0x06,
                          8: 0x07},
            'PD_N50' : GS + b'\x7c\x00',  # Printing Density -50%
            'PD_N37' : GS + b'\x7c\x01',  # Printing Density -37.5%
            'PD_N25' : GS + b'\x7c\x02',  # Printing Density -25%
            'PD_N12' : GS + b'\x7c\x03',  # Printing Density -12.5%
            'PD_0' : GS + b'\x7c\x04',  # Printing Density  0%
            'PD_P50' : GS + b'\x7c\x08',  # Printing Density +50%
            'PD_P37' : GS + b'\x7c\x07',  # Printing Density +37.5%
            'PD_P25' : GS + b'\x7c\x06',  # Printing Density +25%
            'PD_P12' : GS + b'\x7c\x05'  # Printing Density +12.5%

        }

        return data[key]

    def pcmd_set(self, align='left', font='a', text_type='normal', width=1, height=1, density=9, invert=False,
                 smooth=False, flip=False):
        cmd = ''
        
        # Width
        if height == 2 and width == 2:
            cmd += '{} {} '.format(self.pcmd('TXT_NORMAL').decode(),self.pcmd('TXT_4SQUARE').decode())
        elif height == 2 and width == 1:
            cmd += '{} {} '.format(self.pcmd('TXT_NORMAL').decode(), self.pcmd('TXT_2HEIGHT').decode())
        elif width == 2 and height == 1:
            cmd += '{} {} '.format(self.pcmd('TXT_NORMAL').decode(), self.pcmd('TXT_2WIDTH').decode())
        elif width == 1 and height == 1:
            cmd += '{} '.format(self.pcmd('TXT_NORMAL').decode())
        elif 1 <= width <= 8 and 1 <= height <= 8 and isinstance(width, int) and isinstance(height, int):
            size = self.pcmd('TXT_SIZE') + bytes([self.pcmd('TXT_WIDTH')[width] + self.pcmd('TXT_HEIGHT')[height]])
            cmd += '{}'.format(size.decode())

        # Upside down
        if flip:
            cmd += '{}'.format(self.pcmd('TXT_FLIP_ON').decode())
            
        else:
            cmd += '{}'.format(self.pcmd('TXT_FLIP_OFF').decode())
        # Smoothing
        if smooth:
            cmd += '{}'.format(self.pcmd('TXT_SMOOTH_ON').decode())
        else:
            cmd += '{}'.format(self.pcmd('TXT_SMOOTH_OFF').decode())
        # Type
        if text_type.upper() == "B":
            cmd += '{}'.format(self.pcmd('TXT_BOLD_ON').decode())
            cmd += '{}'.format(self.pcmd('TXT_UNDERL_OFF').decode())
            
        elif text_type.upper() == "U":
            cmd += '{}'.format(self.pcmd('TXT_BOLD_OFF').decode())
            cmd += '{}'.format(self.pcmd('TXT_UNDERL_ON').decode())

        elif text_type.upper() == "U2":
            cmd += '{}'.format(self.pcmd('TXT_BOLD_OFF').decode())
            cmd += '{}'.format(self.pcmd('TXT_UNDERL2_ON').decode())

        elif text_type.upper() == "BU":
            cmd += '{}'.format(self.pcmd('TXT_BOLD_ON').decode())
            cmd += '{}'.format(self.pcmd('TXT_UNDERL_ON').decode())

        elif text_type.upper() == "BU2":
            cmd += '{}'.format(self.pcmd('TXT_BOLD_ON').decode())
            cmd += '{}'.format(self.pcmd('TXT_UNDERL2_ON').decode())

        elif text_type.upper() == "NORMAL":
            cmd += '{}'.format(self.pcmd('TXT_BOLD_OFF').decode())
            cmd += '{}'.format(self.pcmd('TXT_UNDERL_OFF').decode())

        # Font
        if font.upper() == "B":
            cmd += '{}'.format(self.pcmd('TXT_FONT_B').decode())
        else:  # DEFAULT FONT: A
            cmd += '{}'.format(self.pcmd('TXT_FONT_A').decode())
        # Align
        if align.upper() == "CENTER":
            cmd += '{}'.format(self.pcmd('TXT_ALIGN_CT').decode())
            
        elif align.upper() == "RIGHT":
            cmd += '{}'.format(self.pcmd('TXT_ALIGN_RT').decode())
            
        elif align.upper() == "LEFT":
            cmd += '{}'.format(self.pcmd('TXT_ALIGN_LT').decode())
        # Density
        if density == 0:
            cmd += '{}'.format(self.pcmd('PD_N50').decode())

        elif density == 1:
            cmd += '{}'.format(self.pcmd('PD_N37').decode())

        elif density == 2:
            cmd += '{}'.format(self.pcmd('PD_N25').decode())

        elif density == 3:
            cmd += '{}'.format(self.pcmd('PD_N12').decode())

        elif density == 4:
            cmd += '{}'.format(self.pcmd('PD_0').decode())

        elif density == 5:
            cmd += '{}'.format(self.pcmd('PD_P12').decode())

        elif density == 6:
            cmd += '{}'.format(self.pcmd('PD_P25').decode())

        elif density == 7:
            cmd += '{}'.format(self.pcmd('PD_P37').decode())

        elif density == 8:
            cmd += '{}'.format(self.pcmd('PD_P50').decode())

        else:  # DEFAULT: DOES NOTHING
            pass
        # Invert Printing
        if invert:
            cmd += '{}'.format(self.pcmd('TXT_INVERT_ON').decode())

        else:
            cmd += '{}'.format(self.pcmd('TXT_INVERT_OFF').decode())

        return cmd
    
    def pcmd_barcode(self, text, type="CODE39", height = 64, width = 2, alignment = 'CENTER', font="B", pos="OFF"):
        _SET_HRI_FONT = lambda n: b'\x1d' + b'f' + n
        BARCODE_FONT_A = _SET_HRI_FONT(b'\x00')  # Font type A for HRI barcode chars
        BARCODE_FONT_B = _SET_HRI_FONT(b'\x01')  # Font type B for HRI barcode chars
        # Barcode format
        _SET_BARCODE_TXT_POS = lambda n: b'\x1d' + b'H' + n
        BARCODE_TXT_OFF = _SET_BARCODE_TXT_POS(b'\x00')  # HRI barcode chars OFF
        BARCODE_TXT_ABV = _SET_BARCODE_TXT_POS(b'\x01')  # HRI barcode chars above
        BARCODE_TXT_BLW = _SET_BARCODE_TXT_POS(b'\x02')  # HRI barcode chars below
        BARCODE_TXT_BTH = _SET_BARCODE_TXT_POS(b'\x03')  # HRI both above and below
        # barcode types
        _SET_BARCODE_TYPE = lambda m: b'\x1d' + b'k' + bytes([m])
        BARCODE_TYPE = {
            'UPC-A': _SET_BARCODE_TYPE(65),
            'UPC-E': _SET_BARCODE_TYPE(66),
            'EAN13': _SET_BARCODE_TYPE(67),
            'EAN8': _SET_BARCODE_TYPE(68),
            'CODE39': _SET_BARCODE_TYPE(69),
            'ITF': _SET_BARCODE_TYPE(70),
            'NW7': _SET_BARCODE_TYPE(71),
            'CODABAR': _SET_BARCODE_TYPE(71),  # Same as NW7
            'CODE93': _SET_BARCODE_TYPE(72),
            # These are all the same barcode, but using different charcter sets
            'CODE128A': _SET_BARCODE_TYPE(73) + b'{A',  # CODE128 character set A
            'CODE128B': _SET_BARCODE_TYPE(73) + b'{B',  # CODE128 character set B
            'CODE128C': _SET_BARCODE_TYPE(73) + b'{C',  # CODE128 character set C
            'GS1-128': _SET_BARCODE_TYPE(74),
            'GS1 DATABAR OMNIDIRECTIONAL': _SET_BARCODE_TYPE(75),
            'GS1 DATABAR TRUNCATED': _SET_BARCODE_TYPE(76),
            'GS1 DATABAR LIMITED': _SET_BARCODE_TYPE(77),
            'GS1 DATABAR EXPANDED': _SET_BARCODE_TYPE(78),
        }


        cmd = ''
        # Align Bar Code()
        if alignment is 'CENTER':
            cmd += '{}'.format(self.pcmd('TXT_ALIGN_CT').decode('utf-8'))

        # Height
        if 1 <= height <= 255:
            BARCODE_HEIGHT = b'\x1d' + b'h' + bytes([height])
            cmd += '{}'.format(BARCODE_HEIGHT.decode('utf-8'))

        # Width
        if 2 <= width <= 6:
            BARCODE_WIDTH = b'\x1d' + b'w' + bytes([width])
            cmd += '{}'.format(BARCODE_WIDTH.decode('utf-8'))

        # Font
        if font.upper() == "B":
            cmd += '{}'.format(BARCODE_FONT_B.decode('utf-8'))

        else:  # DEFAULT FONT: A
            cmd += '{}'.format(BARCODE_FONT_A.decode('utf-8'))

        # Position
        if pos.upper() == "OFF":
            cmd += '{}'.format(BARCODE_TXT_OFF.decode('utf-8'))

        elif pos.upper() == "BOTH":
            cmd += '{}'.format(BARCODE_TXT_BTH.decode('utf-8'))


        elif pos.upper() == "ABOVE":
            cmd += '{}'.format(BARCODE_TXT_ABV.decode('utf-8'))


        else:  # DEFAULT POSITION: BELOW
            cmd += '{}'.format(BARCODE_TXT_BLW.decode('utf-8'))


        # BARCODE TYPE SET
        bc_types = BARCODE_TYPE[type.upper()]
        cmd += '{}'.format(bc_types.decode('utf-8'))

        # print barcode B type
        cmd += '{}'.format(bytes([len(text)]).decode('utf-8'))

        # Print Code
        if text:
            cmd += '{}'.format(text)

        return cmd

    def _setUp(self):
        try:
            self.conn = sqlite3.connect('./db/jayscleaners.db')
        except sqlite3.OperationalError:
            self.conn = sqlite3.connect('jayscleaners.db')
        self.conn.row_factory = dict_factory
        self.c = self.conn.cursor()

    def _tearDown(self):
        self.c.close()
        self.conn.close()