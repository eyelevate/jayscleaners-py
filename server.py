import datetime
import time

from colors import Colored
from companies import Company
from custids import Custid
from deliveries import Delivery
from discounts import Discount
from inventories import Inventory
from inventory_items import InventoryItem
from invoices import Invoice
from invoice_items import InvoiceItem
from memos import Memo
from printers import Printer
from reward_transactions import RewardTransaction
from rewards import Reward
from schedules import Schedule
from taxes import Tax
from transactions import Transaction
from users import User

unix = time.time()
now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))

def sync_from_server(data):

    # start upload text
    if int(data['rows_to_create']) > 0:
        updates = data['updates']
        if 'colors' in updates:
            for colors in updates['colors']:
                color = Colored()
                color.color_id = colors['id']
                color.company_id = colors['company_id']
                color.color = colors['color']
                color.name = colors['name']
                color.ordered = colors['ordered']
                color.status = colors['status']
                color.deleted_at = colors['deleted_at']
                color.created_at = colors['created_at']
                color.updated_at = colors['updated_at']
                # check to see if color_id already exists and update

                count_color = color.where({'color_id':color.color_id})
                if len(count_color) > 0:
                    for data in count_color:
                        color.id = data['id']  
                        color.update()
                else:
                    color.add()
            color.close_connection()

        if 'companies' in updates:
            for companies in updates['companies']:
                company = Company()
                company.company_id = companies['id']
                company.name = companies['name']
                company.street = companies['street']
                company.city = companies['city']
                company.state = companies['state']
                company.zipcode = companies['zip']
                company.email = companies['email']
                company.phone = companies['phone']
                company.store_hours = companies['store_hours']
                company.turn_around = companies['turn_around']
                company.api_token = companies['api_token']
                company.deleted_at = companies['deleted_at']
                company.created_at = companies['created_at']
                company.updated_at = companies['updated_at']
                company.server_at = now
                count_company = company.where({'company_id':company.company_id})
                if len(count_company) > 0:
                    for data in count_company:
                        company.id = data['id']  
                        company.update()
                else:
                    company.add()
            company.close_connection()

        if 'custids' in updates:
            for custids in updates['custids']:
                custid = Custid()
                custid.cust_id = custids['id']
                custid.customer_id = custids['customer_id']
                custid.mark = custids['mark']
                custid.status = custids['status']
                custid.deleted_at = custids['deleted_at']
                custid.created_at = custids['created_at']
                custid.updated_at = custids['updated_at']
                count_custid = custid.where({'cust_id':custids['id']})
                if len(count_custid) > 0:
                    for data in count_custid:
                        custid.id = data['id']  
                        custid.update()
                else:
                    custid.add()
            custid.close_connection()

        if 'deliveries' in updates:
            for deliveries in updates['deliveries']:
                delivery = Delivery()
                delivery.delivery_id = deliveries['id']
                delivery.company_id = deliveries['company_id']
                delivery.route_name = deliveries['route_name']
                delivery.day = deliveries['day']
                delivery.delivery_limit = deliveries['limit']
                delivery.start_time = deliveries['start_time']
                delivery.end_time = deliveries['end_time']
                delivery.zipcode = deliveries['zipcode']
                delivery.blackout = deliveries['blackout']
                delivery.reward_points = deliveries['reward_points']
                delivery.deleted_at = deliveries['deleted_at']
                delivery.created_at = deliveries['created_at']
                delivery.updated_at = deliveries['updated_at']
                count_delivery = custid.where({'delivery_id':delivery.delivery_id})
                if len(count_delivery) > 0:
                    for data in count_delivery:
                        delivery.id = data['id']  
                        delivery.update()
                else:
                    delivery.add()
            delivery.close_connection()

        if 'discounts' in updates:
            for discounts in updates['discounts']:
                discount = Discount()
                discount.discount_id = discounts['id']
                discount.company_id = discounts['company_id']
                discount.inventory_id = discounts['inventory_id']
                discount.inventory_item_id = discounts['inventory_item_id']
                discount.name = discounts['name']
                discount.type = discounts['type']
                discount.discount = discounts['discount']
                discount.rate = discounts['rate']
                discount.end_time = discounts['end_time']
                discount.start_date = discounts['start_date']
                discount.end_date = discounts['end_date']
                discount.status = discounts['status']
                discount.deleted_at = discounts['deleted_at']
                discount.created_at = discounts['created_at']
                discount.updated_at = discounts['updated_at']
                count_discount = discount.where({'discount_id':discount.discount_id})
                if len(count_discount) > 0:
                    for data in count_discount:
                        discount.id = data['id']  
                        discount.update()
                else:
                    discount.add()
            discount.close_connection()

        if 'inventories' in updates:
            for inventories in updates['inventories']:
                inventory = Inventory()
                inventory.inventory_id = inventories['id']
                inventory.company_id = inventories['company_id']
                inventory.name = inventories['name']
                inventory.description = inventories['description']
                inventory.ordered = inventories['ordered']
                inventory.status = inventories['status']
                inventory.deleted_at = inventories['deleted_at']
                inventory.create_at = inventories['created_at']
                inventory.updated_at = inventories['updated_at']
                count_inventory = inventory.where({'inventory_id':inventory.inventory_id})
                if len(count_inventory) > 0:
                    for data in count_inventory:
                        inventory.id = data['id']  
                        inventory.update()
                else:
                    inventory.add()
            inventory.close_connection()

        if 'inventory_items' in updates:
            for inventory_items in updates['inventory_items']:
                inventory_item = InventoryItem()
                inventory_item.item_id = inventory_items['id']
                inventory_item.inventory_id = inventory_items['inventory_id']
                inventory_item.company_id = inventory_items['company_id']
                inventory_item.name = inventory_items['name']
                inventory_item.description = inventory_items['description']
                inventory_item.tags = inventory_items['tags']
                inventory_item.quantity = inventory_items['quantity']
                inventory_item.ordered = inventory_items['ordered']
                inventory_item.price = inventory_items['price']
                inventory_item.image = inventory_items['image']
                inventory_item.status = inventory_items['status']
                inventory_item.deleted_at = inventory_items['deleted_at']
                inventory_item.created_at = inventory_items['created_at']
                inventory_item.updated_at = inventory_items['updated_at']
                count_inventory_item = inventory_item.where({'item_id':inventory_item.item_id})
                if len(count_inventory_item) > 0:
                    for data in count_inventory_item:
                        inventory_item.id = data['id']  
                        inventory_item.update()
                else:
                    inventory_item.add()
            inventory_item.close_connection()

        if 'invoices' in updates:
            for invoices in updates['invoices']:
                invoice = Invoice()
                invoice.invoice_id = invoices['id']
                invoice.company_id = invoices['company_id']
                invoice.customer_id = invoices['customer_id']
                invoice.quantity = invoices['quantity']
                invoice.pretax = invoices['pretax']
                invoice.tax = invoices['tax']
                invoice.reward_id = invoices['reward_id']
                invoice.discount_id = invoices['discount_id']
                invoice.total = invoices['total']
                invoice.rack = invoices['rack']
                invoice.rack_date = invoices['rack_date']
                invoice.due_date = invoices['due_date']
                invoice.memo = invoices['memo']
                invoice.status = invoices['status']
                invoice.deleted_at = invoices['deleted_at']
                invoice.created_at = invoices['created_at']
                invoice.updated_at = invoices['updated_at']
                count_invoice = invoice.where({'invoice_id':invoice.invoice_id})
                if len(count_invoice) > 0:
                    for data in count_invoice:
                        invoice.id = data['id']
                        invoice.update()
                else:
                    invoice.add()
            invoice.close_connection()

        if 'invoice_items' in updates:
            for invoice_items in updates['invoice_items']:
                invoice_item = InvoiceItem()
                invoice_item.invoice_items_id = invoice_items['id']
                invoice_item.invoice_id = invoice_items['invoice_id']
                invoice_item.item_id = invoice_items['item_id']
                invoice_item.company_id = invoice_items['company_id']
                invoice_item.customer_id = invoice_items['customer_id']
                invoice_item.quantity = invoice_items['quantity']
                invoice_item.color = invoice_items['color']
                invoice_item.memo = invoice_items['memo']
                invoice_item.pretax = invoice_items['pretax']
                invoice_item.tax = invoice_items['tax']
                invoice_item.total = invoice_items['total']
                invoice_item.status = invoice_items['status']
                invoice_item.deleted_at = invoice_items['deleted_at']
                invoice_item.created_at = invoice_items['created_at']
                invoice_item.updated_at = invoice_items['updated_at']
                count_invoice_item = invoice_item.where({'invoice_items_id':invoice_item.invoice_items_id})
                if len(count_invoice_item) > 0:
                    for data in count_invoice_item:
                        invoice_item.id = data['id']  
                        invoice_item.update()
                else:
                    invoice_item.add()
            invoice_item.close_connection()

        if 'memos' in updates:
            for memos in updates['memos']:
                memo = Memo()
                memo.memo_id = memos['id']
                memo.company_id = memos['company_id']
                memo.memo = memos['memo']
                memo.ordered = memos['ordered']
                memo.status = memos['status']
                memo.deleted_at = memos['deleted_at']
                memo.created_at = memos['created_at']
                memo.updated_at = memos['updated_at']
                count_memo = memo.where({'memo_id':memo.memo_id})
                if len(count_memo) > 0:
                    for data in count_memo:
                        memo.id = data['id']  
                        memo.update()
                else:
                    memo.add()
            memo.close_connection()

        if 'printers' in updates:
            for printers in updates['printers']:
                printer = Printer()
                printer.printer_id = printers['id']
                printer.company_id = printers['company_id']
                printer.name = printers['name']
                printer.model = printers['model']
                printer.nick_name = printers['nick_name']
                printer.type = printers['type']
                printer.status = printers['status']
                printer.deleted_at = printers['deleted_at']
                printer.created_at = printers['created_at']
                printer.updated_at = printers['updated_at']
                count_printer = printer.where({'printer_id':printer.printer_id})
                if len(count_printer) > 0:
                    for data in count_printer:
                        printer.id = data['id']  
                        printer.update()
                else:
                    printer.add()
            printer.close_connection()

        if 'reward_transactions' in updates:
            for reward_transactions in updates['reward_transactions']:
                reward_transaction = RewardTransaction()
                reward_transaction.reward_id = reward_transactions['reward_id']
                reward_transaction.transaction_id = reward_transactions['transaction_id']
                reward_transaction.customer_id = reward_transactions['customer_id']
                reward_transaction.employee_id = reward_transactions['employee_id']
                reward_transaction.company_id = reward_transactions['company_id']
                reward_transaction.type = reward_transactions['type']
                reward_transaction.points = reward_transactions['points']
                reward_transaction.credited = reward_transactions['credited']
                reward_transaction.reduced = reward_transactions['reduced']
                reward_transaction.running_total = reward_transactions['running_total']
                reward_transaction.reason = reward_transactions['reason']
                reward_transaction.name = reward_transactions['name']
                reward_transaction.status = reward_transactions['status']
                reward_transaction.deleted_at = reward_transactions['deleted_at']
                reward_transaction.created_at = reward_transactions['created_at']
                reward_transaction.updated_at = reward_transactions['updated_at']
                count_reward_transaction = reward_transaction.where({'reward_id':reward_transaction.reward_id})
                if len(count_reward_transaction) > 0:
                    for data in count_reward_transaction:
                        reward_transaction.id = data['id']  
                        reward_transaction.update()
                else:
                    reward_transaction.add()
            reward_transaction.close_connection()

        if 'rewards' in updates:
            for rewards in updates['rewards']:
                reward = Reward()
                reward.reward_id = rewards['id']
                reward.company_id = rewards['company_id']
                reward.name = rewards['name']
                reward.points = rewards['points']
                reward.discount = rewards['discount']
                reward.status = rewards['status']
                reward.deleted_at = rewards['deleted_at']
                reward.created_at = rewards['created_at']
                reward.updated_at = rewards['updated_at']
                count_reward = reward.where({'reward_id':reward.reward_id})
                if len(count_reward) > 0:
                    for data in count_reward:
                        reward.id = data['id']  
                        reward.update()
                else:
                    reward.add()
            reward.close_connection()

        if 'schedules' in updates:
            for schedules in updates['schedules']:
                schedule = Schedule()
                schedule.schedule_id = schedules['id']
                schedule.company_id = schedules['company_id']
                schedule.pickup_delivery_id = schedules['pickup_delivery_id']
                schedule.pickup_date = schedules['pickup_date']
                schedule.dropoff_delivery_id = schedules['dropoff_delivery_id']
                schedule.dropoff_date = schedules['dropoff_date']
                schedule.special_instructions = schedules['special_instructions']
                schedule.type = schedules['type']
                schedule.token = schedules['token']
                schedule.status = schedules['status']
                schedule.deleted_at = schedules['deleted_at']
                schedule.created_at = schedules['created_at']
                schedule.updated_at = schedules['updated_at']
                count_schedule = schedule.where({'schedule_id':schedule.schedule_id})
                if len(count_schedule) > 0:
                    for data in count_schedule:
                        schedule.id = data['id']  
                        schedule.update()
                else:
                    schedule.add()
            schedule.close_connection()

        if 'taxes' in updates:
            for taxes in updates['taxes']:
                tax = Tax()
                tax.tax_id = taxes['id']
                tax.company_id = taxes['company_id']
                tax.rate = taxes['rate']
                tax.status = taxes['status']
                tax.deleted_at = taxes['deleted_at']
                tax.created_at = taxes['created_at']
                tax.updated_at = taxes['updated_at']
                count_tax = tax.where({'tax_id':tax.tax_id})
                if len(count_tax) > 0:
                    for data in count_tax:
                        tax.id = data['id']  
                        tax.update()
                else:
                    tax.add()
            tax.close_connection()

        if 'transactions' in updates:
            for transactions in updates['transactions']:
                transaction = Transaction()
                transaction.transaction_id = transactions['id']
                transaction.company_id = transactions['company_id']
                transaction.customer_id = transactions['customer_id']
                transaction.schedule_id = transactions['schedule_id']
                transaction.pretax = transactions['pretax']
                transaction.tax = transactions['tax']
                transaction.aftertax = transactions['aftertax']
                transaction.discount = transactions['discount']
                transaction.total = transactions['total']
                transaction.invoices = transactions['invoices']
                transaction.type = transactions['type']
                transaction.last_four = transactions['last_four']
                transaction.tendered = transactions['tendered']
                transaction.status = transactions['status']
                transaction.deleted_at = transactions['deleted_at']
                transaction.created_at = transactions['created_at']
                transaction.updated_at = transactions['updated_at']
                count_transaction = transaction.where({'transaction_id':transaction.transaction_id})
                if len(count_transaction) > 0:
                    for data in count_transaction:
                        transaction.id = data['id']  
                        transaction.update()
                else:
                    transaction.add()
            transaction.close_connection()

        if 'users' in updates:
            for users in updates['users']:
                user = User()
                user.user_id = users['id']
                user.company_id = users['company_id']
                user.username = users['username']
                user.first_name = users['first_name']
                user.last_name = users['last_name']
                user.street = users['street']
                user.suite = users['suite']
                user.city = users['city']
                user.state = users['state']
                user.zipcode = users['zipcode']
                user.email = users['email']
                user.phone = users['phone']
                user.intercom = users['intercom']
                user.concierge_name = users['concierge_name']
                user.concierge_number = users['concierge_number']
                user.special_instructions = users['special_instructions']
                user.shirt_old = users['shirt_old']
                user.shirt = users['shirt']
                user.delivery = users['delivery']
                user.profile_id = users['profile_id']
                user.payment_status = users['payment_status']
                user.payment_id = users['payment_id']
                user.token = users['token']
                user.api_token = users['api_token']
                user.reward_status = users['reward_status']
                user.reward_points = users['reward_points']
                user.account = users['account']
                user.starch = users['starch']
                user.important_memo = users['important_memo']
                user.invoice_memo = users['invoice_memo']
                user.role_id = users['role_id']
                user.deleted_at = users['deleted_at']
                user.created_at = users['created_at']
                user.updated_at = users['updated_at']
                count_user = user.where({'user_id':user.user_id})
                if len(count_user) > 0:
                    for data in count_user:
                        user.id = data['id']  
                        user.update()
                else:
                    user.add()
            user.close_connection()


def update_database(data):
    # start upload text
    if int(data['rows_saved']) > 0:
        if 'colors' in data['saved']:
            for colors in data['saved']['colors']:
                color = Colored()
                color.id = colors['id']
                color.color_id = colors['color_id']
                color.company_id = colors['company_id']
                color.color = colors['color']
                color.name = colors['name']
                color.ordered = colors['ordered']
                color.status = colors['status']
                color.updated_at = colors['updated_at']
                color.update()
            color.close_connection()

        if 'companies' in data['saved']:
            for companies in data['saved']['companies']:
                company = Company()
                company.id = companies['id']
                company.company_id = companies['company_id']
                company.name = companies['name']
                company.street = companies['street']
                company.city = companies['city']
                company.state = companies['state']
                company.zip = companies['zip']
                company.email = companies['email']
                company.phone = companies['phone']
                company.store_hours = companies['store_hours']
                company.turn_around = companies['turn_around']
                company.api_token = companies['api_token']
                company.updated_at = companies['updated_at']
                company.server_at = now
                company.update()
            company.close_connection()

        if 'custids' in data['saved']:
            for custids in data['saved']['custids']:
                custid = Custid()
                custid.id = custids['id']
                custid.cust_id = custids['cust_id']
                custid.customer_id = custids['customer_id']
                custid.mark = custids['mark']
                custid.status = custids['status']
                custid.deleted_at = custids['deleted_at']
                custid.created_at = custids['created_at']
                custid.updated_at = custids['updated_at']
                custid.update()
            custid.close_connection()

        if 'deliveries' in data['saved']:
            for deliveries in data['saved']['deliveries']:
                delivery = Delivery()
                delivery.id = deliveries['app_id']
                delivery.delivery_id = deliveries['id']
                delivery.company_id = deliveries['company_id']
                delivery.route_name = deliveries['route_name']
                delivery.day = deliveries['day']
                delivery.delivery_limit = deliveries['limit']
                delivery.start_time = deliveries['start_time']
                delivery.end_time = deliveries['end_time']
                delivery.zipcode = deliveries['zipcode']
                delivery.blackout = deliveries['blackout']
                delivery.reward_points = deliveries['reward_points']
                delivery.updated_at = deliveries['updated_at']
                delivery.update()
            delivery.close_connection()

        if 'discounts' in data['saved']:
            for discounts in data['saved']['discounts']:
                discount = Discount()
                discount.id = discounts['id']
                discount.discount_id = discounts['discount_id']
                discount.company_id = discounts['company_id']
                discount.inventory_id = discounts['inventory_id']
                discount.inventory_item_id = discounts['inventory_item_id']
                discount.name = discounts['name']
                discount.type = discounts['type']
                discount.discount = discounts['discount']
                discount.rate = discounts['rate']
                discount.end_time = discounts['end_time']
                discount.start_date = discounts['start_date']
                discount.end_date = discounts['end_date']
                discount.status = discounts['status']
                discount.updated_at = discounts['updated_at']
                discount.update()
            discount.close_connection()

        if 'inventories' in data['saved']:
            for inventories in data['saved']['inventories']:
                inventory = Inventory()
                inventory.id = inventories['id']
                inventory.inventory_id = inventories['inventory_id']
                inventory.company_id = inventories['company_id']
                inventory.name = inventories['name']
                inventory.description = inventories['description']
                inventory.ordered = inventories['ordered']
                inventory.status = inventories['status']
                inventory.deleted_at = inventories['deleted_at']
                inventory.create_at = inventories['created_at']
                inventory.updated_at = inventories['updated_at']
                inventory.update()
            inventory.close_connection()

        if 'inventory_items' in data['saved']:
            for inventory_items in data['saved']['inventory_items']:
                inventory_item = InventoryItem()
                inventory_item.id = inventory_items['id']
                inventory_item.item_id = inventory_items['item_id']
                inventory_item.inventory_id = inventory_items['inventory_id']
                inventory_item.company_id = inventory_items['company_id']
                inventory_item.name = inventory_items['name']
                inventory_item.description = inventory_items['description']
                inventory_item.tags = inventory_items['tags']
                inventory_item.quantity = inventory_items['quantity']
                inventory_item.ordered = inventory_items['ordered']
                inventory_item.price = inventory_items['price']
                inventory_item.image = inventory_items['image']
                inventory_item.status = inventory_items['status']
                inventory_item.updated_at = inventory_items['updated_at']
                inventory_item.update()
            inventory_item.close_connection()

        if 'invoices' in data['saved']:
            for invoices in data['saved']['invoices']:
                invoice = Invoice()
                invoice.id = invoices['id']
                invoice.invoice_id = invoices['invoice_id']
                invoice.company_id = invoices['company_id']
                invoice.customer_id = invoices['customer_id']
                invoice.quantity = invoices['quantity']
                invoice.pretax = invoices['pretax']
                invoice.tax = invoices['tax']
                invoice.reward_id = invoices['reward_id']
                invoice.discount_id = invoices['discount_id']
                invoice.total = invoices['total']
                invoice.rack = invoices['rack']
                invoice.rack_date = invoices['rack_date']
                invoice.due_date = invoices['due_date']
                invoice.memo = invoices['memo']
                invoice.status = invoices['status']
                invoice.updated_at = invoices['updated_at']
                invoice.update()
            invoice.close_connection()

        if 'invoice_items' in data['saved']:
            for invoice_items in data['saved']['invoice_items']:
                invoice_item = InvoiceItem()
                invoice_item.id = invoice_items['id']
                invoice_item.invoice_items_id = invoice_items['invoice_item_id']
                invoice_item.invoice_id = invoice_items['invoice_id']
                invoice_item.item_id = invoice_items['item_id']
                invoice_item.company_id = invoice_items['company_id']
                invoice_item.customer_id = invoice_items['customer_id']
                invoice_item.quantity = invoice_items['quantity']
                invoice_item.color = invoice_items['color']
                invoice_item.memo = invoice_items['memo']
                invoice_item.pretax = invoice_items['pretax']
                invoice_item.tax = invoice_items['tax']
                invoice_item.total = invoice_items['total']
                invoice_item.status = invoice_items['status']
                invoice_item.updated_at = invoice_items['updated_at']
                invoice_item.update()
            invoice_item.close_connection()

        if 'memos' in data['saved']:
            for memos in data['saved']['memos']:
                memo = Memo()
                memo.id = memos['id']
                memo.memo_id = memos['memo_id']
                memo.company_id = memos['company_id']
                memo.memo = memos['memo']
                memo.ordered = memos['ordered']
                memo.status = memos['status']
                memo.updated_at = memos['updated_at']
                memo.update()
            memo.close_connection()

        if 'printers' in data['saved']:
            for printers in data['saved']['printers']:
                printer = Printer()
                printer.id = printers['id']
                printer.printer_id = printers['printer_id']
                printer.company_id = printers['company_id']
                printer.name = printers['name']
                printer.model = printers['model']
                printer.nick_name = printers['nick_name']
                printer.type = printers['type']
                printer.status = printers['status']
                printer.updated_at = printers['updated_at']
                printer.update()
            printer.close_connection()

        if 'reward_transactions' in data['saved']:
            for reward_transactions in data['saved']['reward_transactions']:
                reward_transaction = RewardTransaction()
                reward_transaction.id = reward_transactions['id']
                reward_transaction.reward_id = reward_transactions['reward_id']
                reward_transaction.transaction_id = reward_transactions['transaction_id']
                reward_transaction.customer_id = reward_transactions['customer_id']
                reward_transaction.employee_id = reward_transactions['employee_id']
                reward_transaction.company_id = reward_transactions['company_id']
                reward_transaction.type = reward_transactions['type']
                reward_transaction.points = reward_transactions['points']
                reward_transaction.credited = reward_transactions['credited']
                reward_transaction.reduced = reward_transactions['reduced']
                reward_transaction.running_total = reward_transactions['running_total']
                reward_transaction.reason = reward_transactions['reason']
                reward_transaction.name = reward_transactions['name']
                reward_transaction.status = reward_transactions['status']
                reward_transaction.updated_at = reward_transactions['updated_at']
                reward_transaction.update()
            reward_transaction.close_connection()

        if 'rewards' in data['saved']:
            for rewards in data['saved']['rewards']:
                reward = Reward()
                reward.id = rewards['id']
                reward.reward_id = rewards['reward_id']
                reward.company_id = rewards['company_id']
                reward.name = rewards['name']
                reward.points = rewards['points']
                reward.discount = rewards['discount']
                reward.status = rewards['status']
                reward.updated_at = rewards['updated_at']
                reward.update()
            reward.close_connection()

        if 'schedules' in data['saved']:
            for schedules in data['saved']['schedules']:
                schedule = Schedule()
                schedule.id = schedules['id']
                schedule.schedule_id = schedules['schedule_id']
                schedule.company_id = schedules['company_id']
                schedule.pickup_delivery_id = schedules['pickup_delivery_id']
                schedule.pickup_date = schedules['pickup_date']
                schedule.dropoff_delivery_id = schedules['dropoff_delivery_id']
                schedule.dropoff_date = schedules['dropoff_date']
                schedule.special_instructions = schedules['special_instructions']
                schedule.type = schedules['type']
                schedule.token = schedules['token']
                schedule.status = schedules['status']
                schedule.updated_at = schedules['updated_at']
                schedule.update()
            schedule.close_connection()

        if 'taxes' in data['saved']:
            for taxes in data['saved']['taxes']:
                tax = Tax()
                tax.id = taxes['id']
                tax.tax_id = taxes['tax_id']
                tax.company_id = taxes['company_id']
                tax.rate = taxes['rate']
                tax.status = taxes['status']
                tax.updated_at = taxes['updated_at']
                tax.update()
            tax.close_connection()

        if 'transactions' in data['saved']:
            for transactions in data['saved']['transactions']:
                transaction = Transaction()
                transaction.id = transactions['id']
                transaction.transaction_id = transactions['transaction_id']
                transaction.company_id = transactions['company_id']
                transaction.customer_id = transactions['customer_id']
                transaction.schedule_id = transactions['schedule_id']
                transaction.pretax = transactions['pretax']
                transaction.tax = transactions['tax']
                transaction.aftertax = transactions['aftertax']
                transaction.discount = transactions['discount']
                transaction.total = transactions['total']
                transaction.invoices = transactions['invoices']
                transaction.type = transactions['type']
                transaction.last_four = transactions['last_four']
                transaction.tendered = transactions['tendered']
                transaction.status = transactions['status']
                transaction.updated_at = transactions['updated_at']
                transaction.update()
            transaction.close_connection()

        if 'users' in data['saved']:
            for users in data['saved']['users']:
                user = User()
                user.id = users['id']
                user.user_id = users['user_id']
                user.company_id = users['company_id']
                user.username = users['username']
                user.first_name = users['first_name']
                user.last_name = users['last_name']
                user.street = users['street']
                user.suite = users['suite']
                user.city = users['city']
                user.state = users['state']
                user.zipcode = users['zipcode']
                user.email = users['email']
                user.phone = users['phone']
                user.intercom = users['intercom']
                user.concierge_name = users['concierge_name']
                user.concierge_number = users['concierge_number']
                user.special_instructions = users['special_instructions']
                user.shirt_old = users['shirt_old']
                user.shirt = users['shirt']
                user.delivery = users['delivery']
                user.profile_id = users['profile_id']
                user.payment_status = users['payment_status']
                user.payment_id = users['payment_id']
                user.token = users['token']
                user.api_token = users['api_token']
                user.reward_status = users['reward_status']
                user.reward_points = users['reward_points']
                user.account = users['account']
                user.starch = users['starch']
                user.important_memo = users['important_memo']
                user.invoice_memo = users['invoice_memo']
                user.role_id = users['role_id']
                user.updated_at = users['updated_at']
                user.update()
            user.close_connection()