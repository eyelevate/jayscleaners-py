
class Static:
    CUSTOMER_ID = None
    INVOICE_ID = None
    SEARCH_NEW = False
    LAST10 = []
    SEARCH_RESULTS = []
    SEARCH_RESULTS_STATUS = False
    SEARCH_TEXT = None
    ROW_SEARCH = 0,9
    ROW_CAP = 0

    def update_last_10(self):
        if self.CUSTOMER_ID in self.LAST10:
            self.LAST10.remove(self.CUSTOMER_ID)

        self.LAST10.insert(0, self.CUSTOMER_ID)
        if len(self.LAST10) > 10:
            del self.LAST10[10]