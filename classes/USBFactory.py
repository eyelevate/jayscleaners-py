import threading
import usb
import usb.core
import usb.util
import usb.backend.libusb1

class USBFactory():
    ''' Monitor udev for detection of usb '''
    thread = threading
    epson = None
    epson_ids = (None, None)
    bixolon = None
    bixolon_ids = (None, None)
    zebra = None
    zebra_ids = (None, None)

    def __init__(self):
        ''' Initiate the object '''
        print('started usb detection')

    def work(self):
        # self.thread = threading.Timer(60*5, self.work)
        # self.thread.start()
        # # fallback if we cannot find any known devices try seeing if other devices work as printers
        # dev = usb.core.find(find_all=True)
        # # loop through devices, printing vendor and product ids in decimal and hex
        # devices = {}
        # for cfg in dev:
        #     id_vendor = cfg.idVendor
        #     id_vendor_hex = hex(cfg.idVendor)
        #     id_product = cfg.idProduct
        #     id_product_hex = hex(cfg.idProduct)
        #     devices[(id_vendor, id_product)] = {
        #         'idVendor': id_vendor,
        #         'idVendorHex': id_vendor_hex,
        #         'idProduct': id_product,
        #         'idProductHex': id_product_hex
        #     }
        #
        # # finish checking
        # print(devices)
        pass

    def stop_work(self, *args, **kwargs):
        # try:
        #     self.thread.cancel()
        #     print('event canceled')
        # except (AttributeError, TypeError) as e:
        #     print(e)
        pass
