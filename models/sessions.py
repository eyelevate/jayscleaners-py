from kivy.storage.dictstore import DictStore

sessions = DictStore('sessions')
if not sessions.exists('_rememberMe'):
    sessions.put('_rememberMe', value=False)
if not sessions.exists('_rememberMeTimestamp'):
    sessions.put('_rememberMeTimestamp', value=False)
if not sessions.exists('_customerId'):
    sessions.put('_customerId', value=None)
if not sessions.exists('_username'):
    sessions.put('_username', value=None)
if not sessions.exists('_userId'):
    sessions.put('_userId', value=None)
if not sessions.exists('_companyId'):
    sessions.put('_companyId', value=None)
if not sessions.exists('_invoiceId'):
    sessions.put('_invoiceId', value=False)
if not sessions.exists('_invoiceItemsId'):
    sessions.put('_invoiceItemsId', value=None)
if not sessions.exists('_itemId'):
    sessions.put('_itemId', value=None)
if not sessions.exists('_inventories'):
    sessions.put('_inventories', value=None)
if not sessions.exists('_inventoryTimestamp'):
    sessions.put('_inventoryTimestamp', value=None)
if not sessions.exists('_searchNew'):
    sessions.put('_searchNew', value=False)
if not sessions.exists('_last10'):
    sessions.put('_last10', value=[])
if not sessions.exists('_searchResults'):
    sessions.put('_searchResults', value=[])
if not sessions.exists('_searchResultsStatus'):
    sessions.put('_searchResultsStatus', value=False)
if not sessions.exists('_searchText'):
    sessions.put('_searchText', value=False)
if not sessions.exists('_rowGroup'):
    sessions.put('_rowGroup', value=0)
if not sessions.exists('_rowSearch'):
    sessions.put('_rowSearch', value=(0,9))
if not sessions.exists('_rowCap'):
    sessions.put('_rowCap', value=0)
if not sessions.exists('_taxRate'):
    sessions.put('_taxRate', value=1)
if not sessions.exists('_paymentId'):
    sessions.put('_paymentId', value=None)
if not sessions.exists('_profileId'):
    sessions.put('_profileId', value=None)
if not sessions.exists('_workList'):
    sessions.put('_workList', value=[])
if not sessions.exists('_exitFlag'):
    sessions.put('_exitFlag', value=False)
if not sessions.exists('_threadId'):
    sessions.put('_threadId', value=1)
if not sessions.exists('_threads'):
    sessions.put('_threads', value=[])
if not sessions.exists('_epson'):
    sessions.put('_epson', value=None)
if not sessions.exists('_bixolon'):
    sessions.put('_bixolon', value=None)
if not sessions.exists('_usDollar'):
    sessions.put('_usDollar', value=0)
if not sessions.exists('_zebra'):
    sessions.put('_zebra', value=None)
