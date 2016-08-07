
class Static:
    CUSTOMER_ID = None
    INVOICE_ID = None
    INVOICE_ITEMS_ID = None
    ITEM_ID = None
    SEARCH_NEW = False
    LAST10 = []
    SEARCH_RESULTS = []
    SEARCH_RESULTS_STATUS = False
    SEARCH_TEXT = None
    ROW_SEARCH = 0,9
    ROW_CAP = 0
    TAX_RATE = 1
    #sync.py used for mutlithreading
    WORKLIST = []
    EXITFLAG = False
    THREADID = 1
    THREADS = []

    def update_last_10(self):
        if self.CUSTOMER_ID in self.LAST10:
            self.LAST10.remove(self.CUSTOMER_ID)

        self.LAST10.insert(0, self.CUSTOMER_ID)
        if len(self.LAST10) > 10:
            del self.LAST10[10]

    def dow_schedule(self, day):
        if day == 0:
            return 'Sunday'
        elif day == 1:
            return 'Monday'
        elif day == 2:
            return 'Tuesday'
        elif day == 3:
            return 'Wednesday'
        elif day == 4:
            return 'Thursday'
        elif day == 5:
            return 'Friday'
        else:
            return 'Saturday'

    def dow(self, day):
        if day == 0:
            return 'Mon'
        elif day == 1:
            return 'Tue'
        elif day == 2:
            return 'Wed'
        elif day == 3:
            return 'Thu'
        elif day == 4:
            return 'Fri'
        elif day == 5:
            return 'Sat'
        else:
            return 'Sun'

    def us_dollar(self, amount):
        try:
            dollar = '${:,.2f}'.format(amount)
        except TypeError:
            return amount
        except ValueError:
            return amount
        finally:
            return dollar

    def color_rgba(self,href):
        if href == '#000000' or href == 'black': # black
            return (0,0,0,1)
        elif href == '#ffffff' or href == 'white': # white
            return (1,1,1,1)
        elif href == '#0433ff' or href == 'blue': # blue
            return (0.01568627,0.2,1,1)
        elif href == '#aa7942' or href == 'brown': # brown
            return (0.667,0.47450980,0.25882353,1)
        elif href == '#00f900' or href == 'green': # green
            return (0,0.97647059,0,1)
        elif href == '#ff40ff' or href == 'pink':
            return (1,0.25098039,1,1)
        elif href == '#ff9300' or href == 'orange':
            return (1,0.57647059,0,1)
        elif href == '#942192' or href == 'purple': # purple
            return (0.58039216,0.12941176,0.57254902,1)
        elif href == '#ff2600' or href == 'ff0000' or href == 'red':
            return (1,0,0,1)
        elif href == '#fffb00' or href == 'yellow':
            return (1,0.98431373,0,1)

    def month_by_number(self, num):
        if num == 1:
            return 'January'
        elif num == 2:
            return 'February'
        elif num == 3:
            return 'March'
        elif num == 4:
            return 'April'
        elif num == 5:
            return 'May'
        elif num == 6:
            return 'June'
        elif num == 7:
            return 'July'
        elif num == 8:
            return 'August'
        elif num == 9:
            return 'September'
        elif num == 10:
            return 'October'
        elif num == 11:
            return 'November'
        else:
            return 'December'

    def get_starch_by_code(self, code):
        if code == 4:
            starch = 'Heavy'
        elif code == 2:
            starch = 'Light'
        elif code == 3:
            starch = 'Medium'
        else:
            starch = 'None'

        return starch

    def esc(self, command):
        if 'initiate':
            return b'\x1b'+ b'@'





