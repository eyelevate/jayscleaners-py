import sys
import platform
import time
import os
from os import path
from pathlib import Path
# !/usr/local/bin/python3
# !/usr/bin/env python3
from kivy.clock import Clock

os.environ['TZ'] = 'US/Pacific'
if platform.system() == 'Darwin':  # Mac
    sys.path.append('~/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages')
    time.tzset()
    time.tzset()
elif platform.system() == 'Linux':  # Linux
    sys.path.append('/')  # TODO
    time.tzset()
elif platform.system() == 'Windows':  # Windows
    sys.path.append('/')  # TODO

# Models
from models.sync import Sync
from models.users import User

# Helpers
from decimal import *

getcontext().prec = 3

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager


# SCREEN CLASSES
from models.listeners import *
from classes.mainScreen import MainScreen
from classes.colorsScreen import ColorsScreen
from classes.company import CompanyScreen
from classes.delivery import DeliveryScreen
from classes.dropoff import DropoffScreen
from classes.editCustomers import EditCustomerScreen
from classes.editInvoices import EditInvoiceScreen
from classes.employees import EmployeesScreen
from classes.history import HistoryScreen
from classes.inventories import InventoriesScreen
from classes.inventoryItems import InventoryItemsScreen
from classes.invoiceDetails import InvoiceDetailsScreen
from classes.itemDetails import ItemDetailsScreen
from classes.last10 import Last10Screen
from classes.login import LoginScreen
from classes.memos import MemosScreen
from classes.newCustomer import NewCustomerScreen
from classes.pickup import PickupScreen
from classes.printer import PrinterScreen
from classes.rack import RackScreen
from classes.reports import ReportsScreen
from classes.search import SearchScreen
from classes.searchResults import SearchResultsScreen
from classes.settings import SettingsScreen
from classes.taxes import TaxesScreen
from classes.update import UpdateScreen


class ScreenManagement(ScreenManager):

    pass

data_folder = Path("./kv")
main_path_relative = data_folder / "main.kv"
KV_PATH = path.abspath(main_path_relative)
presentation = Builder.load_file(KV_PATH)

class MainApp(App):

    def build(self):
        self.title = 'Jays POS'
        return presentation


if __name__ == "__main__":
    MainApp().run()
    pub.sendMessage("checkLoggedIn")
