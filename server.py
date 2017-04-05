import datetime
import time

from addresses import Address
from cards import Card
from colors import Colored
from companies import Company
from credits import Credit
from custids import Custid
from deliveries import Delivery
from discounts import Discount
from inventories import Inventory
from inventory_items import InventoryItem
from invoices import Invoice
from invoice_items import InvoiceItem
from memos import Memo
from printers import Printer
from profiles import Profile
from reward_transactions import RewardTransaction
from rewards import Reward
from schedules import Schedule
from taxes import Tax
from transactions import Transaction
from users import User
from zipcodes import Zipcode

unix = time.time()
now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))


def sync_from_server(data):
    # print('sync from server')
    # start upload text
    # print(data)
    # print(data['rows_to_create'])
    if int(data['rows_to_create']) > 0:
        updates = data['updates']
        if 'addresses' in updates:
            for addresses in updates['addresses']:
                address = Address()
                address.address_id = addresses['id']
                address.user_id = addresses['user_id']
                address.name = addresses['name']
                address.street = addresses['street']
                address.suite = addresses['suite']
                address.city = addresses['city']
                address.state = addresses['state']
                address.zipcode = addresses['zipcode']
                address.primary_address = addresses['primary_address']
                address.concierge_name = addresses['concierge_name']
                address.concierge_number = addresses['concierge_number']
                address.status = addresses['status']
                address.deleted_at = addresses['deleted_at']
                address.created_at = addresses['created_at']
                address.updated_at = addresses['updated_at']
                # check to see if color_id already exists and update

                count_address = address.where({'address_id': address.address_id})
                if len(count_address) > 0 or address.deleted_at:
                    for data in count_address:
                        address.id = data['id']
                        if address.deleted_at:
                            address.delete()
                        else:
                            address.update()
                else:
                    address.add()
            address.close_connection()
 
        if 'cards' in updates:
            for cards in updates['cards']:
                card = Card()
                card.card_id = cards['id']
                card.company_id = cards['company_id']
                card.user_id = cards['user_id']
                card.profile_id = cards['profile_id']
                card.payment_id = cards['payment_id']
                card.root_payment_id = cards['root_payment_id']
                card.street = cards['street']
                card.suite = cards['suite']
                card.city = cards['city']
                card.state = cards['state']
                card.zipcode = cards['zipcode']
                card.exp_month = cards['exp_month']
                card.exp_year = cards['exp_year']
                card.status = cards['status']
                card.deleted_at = cards['deleted_at']
                card.created_at = cards['created_at']
                card.updated_at = cards['updated_at']
                # check to see if color_id already exists and update

                count_card = card.where({'card_id': card.card_id})
                if len(count_card) > 0 or card.deleted_at:
                    for data in count_card:
                        card.id = data['id']
                        if card.deleted_at:
                            card.delete()
                        else:
                            card.update()
                else:
                    card.add()
            card.close_connection()
        
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

                count_color = color.where({'color_id': color.color_id})
                if len(count_color) > 0 or color.deleted_at:
                    for data in count_color:
                        color.id = data['id']
                        if color.deleted_at:
                            color.delete()
                        else:
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
                company.zip = companies['zip']
                company.email = companies['email']
                company.phone = companies['phone']
                company.store_hours = companies['store_hours']
                company.turn_around = companies['turn_around']
                company.api_token = companies['api_token']
                company.payment_gateway_id = companies['payment_gateway_id']
                company.payment_api_login = companies['payment_api_login']
                company.deleted_at = companies['deleted_at']
                company.created_at = companies['created_at']
                company.updated_at = companies['updated_at']
                company.server_at = now
                count_company = company.where({'company_id': company.company_id})
                if len(count_company) > 0 or company.deleted_at:
                    for data in count_company:
                        company.id = data['id']
                        if company.deleted_at:
                            company.delete()
                        else:
                            company.update()
                else:
                    company.add()
            company.close_connection()
            
        if 'credits' in updates:
            for credits in updates['credits']:
                credit = Credit()
                credit.credit_id = credits['id']
                credit.employee_id = credits['employee_id']
                credit.customer_id = credits['customer_id']
                credit.amount = credits['amount']
                credit.reason = credits['reason']
                credit.status = credits['status']
                credit.deleted_at = credits['deleted_at']
                credit.created_at = credits['created_at']
                credit.updated_at = credits['updated_at']
                # check to see already exists and update

                count_credit = credit.where({'credit_id': credit.credit_id})
                if len(count_credit) > 0 or credit.deleted_at:
                    for data in count_credit:
                        credit.id = data['id']
                        if credit.deleted_at:
                            credit.delete()
                        else:
                            credit.update()
                else:
                    credit.add()
            credit.close_connection()
        if 'custids' in updates:
            for custids in updates['custids']:
                custid = Custid()
                custid.cust_id = custids['id']
                custid.customer_id = custids['customer_id']
                custid.company_id = custids['company_id']
                custid.mark = custids['mark']
                custid.status = custids['status']
                custid.deleted_at = custids['deleted_at']
                custid.created_at = custids['created_at']
                custid.updated_at = custids['updated_at']
                count_custid = custid.where({'cust_id': custids['id']})
                if len(count_custid) > 0 or custid.deleted_at:
                    for data in count_custid:
                        custid.id = data['id']
                        if custid.deleted_at:
                            custid.delete()
                        else:
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
                delivery.status = deliveries['status']
                delivery.deleted_at = deliveries['deleted_at']
                delivery.created_at = deliveries['created_at']
                delivery.updated_at = deliveries['updated_at']
                count_delivery = delivery.where({'delivery_id': delivery.delivery_id})
                if len(count_delivery) > 0 or delivery.deleted_at:
                    for data in count_delivery:
                        delivery.id = data['id']
                        if delivery.deleted_at:
                            delivery.delete()
                        else:
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
                count_discount = discount.where({'discount_id': discount.discount_id})
                if len(count_discount) > 0 or discount.deleted_at:
                    for data in count_discount:
                        discount.id = data['id']
                        if discount.deleted_at:
                            discount.delete()
                        else:
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
                inventory.laundry = inventories['laundry']
                inventory.status = inventories['status']
                inventory.deleted_at = inventories['deleted_at']
                inventory.create_at = inventories['created_at']
                inventory.updated_at = inventories['updated_at']
                count_inventory = inventory.where({'inventory_id': inventory.inventory_id})
                if len(count_inventory) > 0 or inventory.deleted_at:
                    for data in count_inventory:
                        inventory.id = data['id']
                        if inventory.deleted_at:
                            inventory.delete()
                        else:
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
                count_inventory_item = inventory_item.where({'item_id': inventory_item.item_id})
                if len(count_inventory_item) > 0 or inventory_item.deleted_at:
                    for data in count_inventory_item:
                        inventory_item.id = data['id']
                        if inventory_item.deleted_at:
                            inventory_item.delete()
                        else:
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
                invoice.transaction_id = invoices['transaction_id']
                invoice.schedule_id = invoices['schedule_id']
                invoice.status = invoices['status']
                invoice.deleted_at = invoices['deleted_at']
                invoice.created_at = invoices['created_at']
                invoice.updated_at = invoices['updated_at']
                count_invoice = invoice.where({'invoice_id': invoice.invoice_id})
                if len(count_invoice) > 0 or invoice.deleted_at:
                    for data in count_invoice:
                        invoice.id = data['id']
                        if invoice.deleted_at:
                            invoice.delete()
                        else:
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
                invoice_item.inventory_id = invoice_items['inventory_id']
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
                count_invoice_item = invoice_item.where({'invoice_items_id': invoice_item.invoice_items_id})
                if len(count_invoice_item) > 0 or invoice_item.deleted_at:
                    for data in count_invoice_item:
                        invoice_item.id = data['id']
                        if invoice_item.deleted_at:
                            invoice_item.delete()
                        else:
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
                count_memo = memo.where({'memo_id': memo.memo_id})
                if len(count_memo) > 0 or memo.deleted_at:
                    for data in count_memo:
                        memo.id = data['id']
                        if memo.deleted_at:
                            memo.delete()
                        else:
                            memo.update()
                else:
                    memo.add()
            memo.close_connection()

        # if 'printers' in updates:
        #     for printers in updates['printers']:
        #         printer = Printer()
        #         printer.printer_id = printers['id']
        #         printer.company_id = printers['company_id']
        #         printer.name = printers['name']
        #         printer.model = printers['model']
        #         printer.nick_name = printers['nick_name']
        #         printer.type = printers['type']
        #         printer.vendor_id = printers['vendor_id']
        #         printer.product_id = printers['product_id']
        #         printer.status = printers['status']
        #         printer.deleted_at = printers['deleted_at']
        #         printer.created_at = printers['created_at']
        #         printer.updated_at = printers['updated_at']
        #         count_printer = printer.where({'printer_id': printer.printer_id})
        #         if len(count_printer) > 0 or printer.deleted_at:
        #             for data in count_printer:
        #                 printer.id = data['id']
        #                 if printer.deleted_at:
        #                     printer.delete()
        #                 else:
        #                     printer.update()
        #         else:
        #             printer.add()
        #     printer.close_connection()

        if 'profiles' in updates:
            for profiles in updates['profiles']:
                profile = Profile()
                profile.p_id = profiles['id']
                profile.company_id = profiles['company_id']
                profile.user_id = profiles['user_id']
                profile.profile_id = profiles['profile_id']
                profile.status = profiles['status']
                profile.deleted_at = profiles['deleted_at']
                profile.created_at = profiles['created_at']
                profile.updated_at = profiles['updated_at']
                count_profile = profile.where({'p_id': profile.p_id})
                if len(count_profile) > 0 or profile.deleted_at:
                    for data in count_profile:
                        profile.id = data['id']
                        if profile.deleted_at:
                            profile.delete()
                        else:
                            profile.update()
                else:
                    profile.add()
            profile.close_connection()


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
                count_reward_transaction = reward_transaction.where({'reward_id': reward_transaction.reward_id})
                if len(count_reward_transaction) > 0 or reward_transaction.deleted_at:
                    for data in count_reward_transaction:
                        reward_transaction.id = data['id']
                        if reward_transaction.deleted_at:
                            reward_transaction.delete()
                        else:
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
                count_reward = reward.where({'reward_id': reward.reward_id})
                if len(count_reward) > 0 or reward.deleted_at:
                    for data in count_reward:
                        reward.id = data['id']
                        if reward.deleted_at:
                            reward.delete()
                        else:
                            reward.update()
                else:
                    reward.add()
            reward.close_connection()

        if 'schedules' in updates:
            for schedules in updates['schedules']:
                schedule = Schedule()
                schedule.schedule_id = schedules['id']
                schedule.company_id = schedules['company_id']
                schedule.customer_id = schedules['customer_id']
                schedule.card_id = schedules['card_id']
                schedule.pickup_delivery_id = schedules['pickup_delivery_id']
                schedule.pickup_address = schedules['pickup_address']
                schedule.pickup_date = schedules['pickup_date']
                schedule.dropoff_delivery_id = schedules['dropoff_delivery_id']
                schedule.dropoff_address = schedules['dropoff_address']
                schedule.dropoff_date = schedules['dropoff_date']
                schedule.special_instructions = schedules['special_instructions']
                schedule.type = schedules['type']
                schedule.token = schedules['token']
                schedule.status = schedules['status']
                schedule.deleted_at = schedules['deleted_at']
                schedule.created_at = schedules['created_at']
                schedule.updated_at = schedules['updated_at']
                count_schedule = schedule.where({'schedule_id': schedule.schedule_id})
                if len(count_schedule) > 0 or schedule.deleted_at:
                    for data in count_schedule:
                        schedule.id = data['id']
                        if schedule.deleted_at:
                            schedule.delete()
                        else:
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
                count_tax = tax.where({'tax_id': tax.tax_id})
                if len(count_tax) > 0 or tax.deleted_at:
                    for data in count_tax:
                        tax.id = data['id']
                        if tax.deleted_at:
                            tax.delete()
                        else:
                            tax.update()
                else:
                    tax.add()
            tax.close_connection()

        if 'transactions' in updates:
            for transactions in updates['transactions']:
                transaction = Transaction()
                transaction.trans_id = transactions['id']
                transaction.company_id = transactions['company_id']
                transaction.customer_id = transactions['customer_id']
                transaction.schedule_id = transactions['schedule_id']
                transaction.pretax = transactions['pretax']
                transaction.tax = transactions['tax']
                transaction.aftertax = transactions['aftertax']
                transaction.credit = transactions['credit']
                transaction.discount = transactions['discount']
                transaction.total = transactions['total']
                transaction.invoices = transactions['invoices'] if transactions['invoices'] else None
                transaction.account_paid = transactions['account_paid']
                transaction.account_paid_on = transactions['account_paid_on']
                transaction.type = transactions['type']
                transaction.last_four = transactions['last_four']
                transaction.tendered = transactions['tendered']
                transaction.transaction_id = transactions['transaction_id']
                transaction.status = transactions['status']
                transaction.deleted_at = transactions['deleted_at']
                transaction.created_at = transactions['created_at']
                transaction.updated_at = transactions['updated_at']
                count_transaction = transaction.where({'trans_id': transaction.trans_id})
                if len(count_transaction) > 0 or transaction.deleted_at:
                    for data in count_transaction:
                        transaction.id = data['id']
                        if transaction.deleted_at:
                            transaction.delete()
                        else:
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
                user.account_total = users['account_total']
                user.credits = users['credits']
                user.starch = users['starch']
                user.important_memo = users['important_memo']
                user.invoice_memo = users['invoice_memo']
                user.role_id = users['role_id']
                user.deleted_at = users['deleted_at']
                user.created_at = users['created_at']
                user.updated_at = users['updated_at']
                count_user = user.where({'user_id': user.user_id})
                if len(count_user) > 0 or user.deleted_at:
                    for data in count_user:
                        user.id = data['id']
                        if user.deleted_at:
                            user.delete()
                        else:
                            user.update()
                else:
                    user.add()
            user.close_connection()


        if 'zipcodes' in updates:
            for zipcodes in updates['zipcodes']:
                zipcode = Zipcode()
                zipcode.zipcode_id = zipcodes['id']
                zipcode.company_id = zipcodes['company_id']
                zipcode.delivery_id = zipcodes['delivery_id']
                zipcode.zipcode = zipcodes['zipcode']
                zipcode.status = zipcodes['status']
                zipcode.deleted_at = zipcodes['deleted_at']
                zipcode.created_at = zipcodes['created_at']
                zipcode.updated_at = zipcodes['updated_at']
                # check to see if color_id already exists and update
        
                count_zipcode = zipcode.where({'zipcode_id': zipcode.zipcode_id})
                if len(count_zipcode) > 0 or zipcode.deleted_at:
                    for data in count_zipcode:
                        zipcode.id = data['id']
                        if zipcode.deleted_at:
                            zipcode.delete()
                        else:
                            zipcode.update()
                else:
                    zipcode.add()
            zipcode.close_connection()

def update_database(data):
    print('updating db')
    # start upload text
    if int(data['rows_saved']) > 0:
        if 'saved' in data:
            saved = data['saved']
            if 'addresses' in saved:
                for addresses in saved['addresses']:
                    address = Address()
                    where = {'id': addresses['id']}
                    data = {'address_id': addresses['address_id']}
                    address.put(where=where, data=data)

            if 'colors' in saved:
                for colors in saved['colors']:
                    color = Colored()
                    where = {'id': colors['id']}
                    data = {'color_id': colors['color_id']}
                    color.put(where=where, data=data)
                    
            if 'cards' in saved:
                for cards in saved['cards']:
                    card = Card()
                    where = {'id': cards['id']}
                    data = {'card_id': cards['card_id']}
                    card.put(where=where, data=data)
            if 'credits' in saved:
                for credit in saved['credits']:
                    credits = Credit()
                    where = {'id': credit['id']}
                    data = {'credit_id': credit['credit_id']}
                    credits.put(where=where, data=data)
            if 'companies' in saved:
                for companies in saved['companies']:
                    company = Company()
                    where = {'id': companies['id']}
                    data = {'company_id': companies['company_id']}
                    company.put(where=where, data=data)

            if 'custids' in saved:
                for custids in saved['custids']:
                    custid = Custid()
                    where = {'id': custids['id']}
                    data = {'cust_id': custids['cust_id']}
                    custid.put(where=where, data=data)

            if 'deliveries' in saved:
                for deliveries in saved['deliveries']:
                    delivery = Delivery()
                    where = {'id': deliveries['id']}
                    data = {'delivery_id': deliveries['delivery_id']}
                    delivery.put(where=where, data=data)

            if 'discounts' in saved:
                for discounts in saved['discounts']:
                    discount = Discount()
                    where = {'id': discounts['id']}
                    data = {'discount_id': discounts['discount_id']}
                    discount.put(where=where, data=data)

            if 'inventories' in saved:
                for inventories in saved['inventories']:
                    inventory = Inventory()
                    where = {'id': inventories['id']}
                    data = {'inventory_id': inventories['inventory_id']}
                    inventory.put(where=where, data=data)

            if 'inventory_items' in saved:
                for inventory_items in saved['inventory_items']:
                    inventory_item = InventoryItem()
                    where = {'id': inventory_items['id']}
                    data = {'item_id': inventory_items['item_id']}
                    inventory_item.put(where=where, data=data)

            if 'invoices' in saved:
                for invoices in saved['invoices']:

                    invoice = Invoice()
                    where = {'id': invoices['id']}
                    data = {'invoice_id': invoices['invoice_id']}
                    invoice.put(where=where, data=data)

            if 'invoice_items' in saved:
                for invoice_items in saved['invoice_items']:

                    invoice_item = InvoiceItem()
                    where = {'id': invoice_items['id']}
                    data = {'invoice_items_id': invoice_items['invoice_items_id']}
                    invoice_item.put(where=where, data=data)

            if 'memos' in saved:
                for memos in saved['memos']:
                    memo = Memo()
                    where = {'id': memos['id']}
                    data = {'memo_id': memos['memo_id']}
                    memo.put(where=where, data=data)
            if 'printers' in saved:
                for printers in saved['printers']:
                    printer = Printer()
                    where = {'id': printers['id']}
                    data = {'printer_id': printers['printer_id']}
                    printer.put(where=where, data=data)
                    
            if 'profiles' in saved:
                for profiles in saved['profiles']:
                    profile = Profile()
                    where = {'id': profiles['id']}
                    data = {'p_id': profiles['p_id']}
                    profile.put(where=where, data=data)
                    
            if 'reward_transactions' in saved:
                for reward_transactions in saved['reward_transactions']:
                    reward_transaction = RewardTransaction()
                    where = {'id': reward_transactions['id']}
                    data = {'reward_id': reward_transactions['reward_id']}
                    reward_transaction.put(where=where, data=data)

            if 'rewards' in saved:
                for rewards in saved['rewards']:
                    reward = Reward()
                    where = {'id': rewards['id']}
                    data = {'reward_id': rewards['reward_id']}
                    reward.put(where=where, data=data)

            if 'schedules' in saved:
                for schedules in saved['schedules']:
                    schedule = Schedule()
                    where = {'id': schedules['id']}
                    data = {'schedule_id': schedules['schedule_id']}
                    schedule.put(where=where, data=data)

            if 'taxes' in saved:
                for taxes in saved['taxes']:
                    tax = Tax()
                    where = {'id': taxes['id']}
                    data = {'tax_id': taxes['tax_id']}
                    tax.put(where=where, data=data)

            if 'transactions' in saved:
                for transactions in saved['transactions']:
                    transaction = Transaction()
                    where = {'id': transactions['id']}
                    data = {'trans_id': transactions['trans_id']}
                    transaction.put(where=where, data=data)

            if 'users' in saved:
                for users in saved['users']:
                    user = User()
                    where = {'id': users['id']}
                    data = {'user_id': users['user_id']}
                    user.put(where=where, data=data)

            if 'zipcodes' in saved:
                for zipcodes in saved['zipcodes']:
                    zipcode = Zipcode()
                    where = {'id': zipcodes['id']}
                    data = {'zipcode_id': zipcodes['zipcode_id']}
                    zipcode.put(where=where, data=data)