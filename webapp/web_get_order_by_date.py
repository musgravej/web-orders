import zeep
import datetime
import bs4
import mysql.connector as mariadb
import settings
import re
from flask import flash

"""
Error during get orders as: prepare_for_mysql result = self._cmysql.convert_to_mysql(*params)
    is probably from an order detail object not being formatted as a json object
    Look at error message: Python type ArrayOfOrderDetailType**FinishingOption** cannot be converted
    to show which object.
    Apply settings.clean_json() function to that object and update db field datatype to LONGTEXT
"""


class Supplier:
    def __init__(self):
        self.groups = []

    def append_to_group(self, od):
        self.groups.append({'id': od['Supplier']['ID']['_value_1'],
                            'name': od['Supplier']['Name']})


class OrderDetail:
    # create a order_detail list object for OrderDetail table
    def __init__(self):
        self.groups = []

    def append_to_group(self, od, rec):
        # Remove pesky non-ascii characters
        ascii_replace = re.compile(r'[^\x00-\x7F]+')

        self.groups.append({'order_id': rec,
                            'order_detail_id': od['ID']['_value_1'],
                            'order_type': od['OrderType'],
                            'user_id': od['User']['ID']['_value_1'],
                            'req_user': od['ReqUser'],
                            'product_id': od['ProductID']['_value_1'],
                            'product_name': od['ProductName'],
                            'product_description':
                                (bs4.BeautifulSoup(od['ProductDescription'], features="lxml").get_text()[:100] if
                                 od['ProductDescription'] is not None else None),
                            'sku_id': od['SKU']['ID']['_value_1'],
                            'sku_name': od['SKU']['Name'],
                            'sku_description': (bs4.BeautifulSoup(od['SKUDescription'], features="lxml").get_text()
                                                if od['SKUDescription'] is not None else None),

                            'template_fields': (settings.clean_json("".join(str(od['TemplateFields']['TemplateField'])))
                                                if od['TemplateFields'] is not None else None),

                            'quantity': od['Quantity'],
                            'quantity_shipped': od['QuantityShipped'],
                            'price_customer': od['Price']['Cost']['Customer']['_value_1'],
                            'price_seller': od['Price']['Cost']['Seller']['_value_1'],
                            'price_shipping': od['Price']['Cost']['Shipping']['_value_1'],
                            'price_unit': od['Price']['Cost']['Unit']['_value_1'],
                            'price_customer_discount': od['Price']['Cost']['CustomerDiscount']['_value_1'],
                            'price_seller_misc': od['Price']['Cost']['SellerMisc']['_value_1'],
                            'price_seller_store_discount': od['Price']['Cost']['SellerStoreDiscount']['_value_1'],
                            'price_seller_shipping': od['Price']['Cost']['SellerShipping']['_value_1'],
                            'price_customer_store_discount': od['Price']['Cost']['CustomerStoreDiscount']['_value_1'],
                            'price_postage': od['Price']['Cost']['Postage']['_value_1'],
                            'price_customer_misc': od['Price']['Cost']['CustomerMisc']['_value_1'],
                            'tax_customer_sales': od['Price']['Tax']['CustomerSales']['_value_1'],
                            'tax_direct_acct_sales': od['Price']['Tax']['DirectAcctSales']['_value_1'],
                            'tax_city': od['Price']['Tax']['City']['_value_1'],
                            'tax_county': od['Price']['Tax']['County']['_value_1'],
                            'tax_state': od['Price']['Tax']['State']['_value_1'],
                            'tax_district': od['Price']['Tax']['District']['_value_1'],
                            'tax_city_freight': od['Price']['Tax']['CityFreight']['_value_1'],
                            'tax_county_freight': od['Price']['Tax']['CountyFreight']['_value_1'],
                            'tax_state_freight': od['Price']['Tax']['StateFreight']['_value_1'],
                            'tax_district_freight': od['Price']['Tax']['DistrictFreight']['_value_1'],
                            'tax_total_freight': od['Price']['Tax']['TotalFreight']['_value_1'],
                            'tax_taxable_sales': od['Price']['Tax']['TaxableSalesAmount']['_value_1'],
                            'tax_exempt_sales': od['Price']['Tax']['ExemptSalesAmount']['_value_1'],
                            'tax_non_taxable': od['Price']['Tax']['NonTaxableSalesAmount']['_value_1'],
                            'tax_city_name': od['Price']['Tax']['CityName'],
                            'tax_county_name': od['Price']['Tax']['CountyName'],
                            'tax_state_name': od['Price']['Tax']['StateName'],
                            'tax_zip': od['Price']['Tax']['Zip'],
                            'department_id': od['Department']['ID']['_value_1'],
                            'department_name': od['Department']['Name'],
                            'department_number': od['Department']['Number'],
                            'supplier_work_order_id': (od['SupplierWorkOrder']['ID']['_value_1'] if
                                                       od['SupplierWorkOrder'] is not None else None),
                            'supplier_work_order_name': (od['SupplierWorkOrder']['Name'] if
                                                         od['SupplierWorkOrder'] is not None else None),
                            'supplier_id': od['Supplier']['ID']['_value_1'],
                            'shipping_date': od['Shipping']['Date'],
                            'shipping_date_shipped': od['Shipping']['DateShipped'],
                            'shipping_method': (ascii_replace.sub('', str(od['Shipping']['Method'])) if
                                                od['Shipping']['Method'] is not None else None),
                            'shipping_instructions': od['Shipping']['Instructions'],
                            'shipping_address_id': od['Shipping']['Address']['ID']['_value_1'],
                            'shipping_tracking': (od['Shipping']['TrackingNumber'][0:12] if
                                                  od['Shipping']['TrackingNumber'] is not None else None),
                            'shipping_tax': od['Shipping']['Tax'],
                            'postage_cost': (od['Postage']['Cost']['_value_1'] if
                                             od['Postage'] is not None else None),
                            'postage_method': (od['Postage']['Method'] if
                                               od['Postage'] is not None else None),
                            'client_status_value': od['ClientStatus']['Value'],
                            'client_status_date': od['ClientStatus']['Date'],
                            'seller_status_value': od['SellerStatus']['Value'],
                            'seller_status_date': od['SellerStatus']['Date'],
                            'supplier_status_value': od['SupplierStatus']['Value'],
                            'supplier_status_date': od['SupplierStatus']['Date'],
                            'credit_card_settlement': (settings.clean_json(od['CreditCardSettlement']) if
                                                       od['CreditCardSettlement'] is not None else None),

                            'kit': (settings.clean_json(od['Kit']['KitDetail']) if
                                    od['Kit'] is not None else None),

                            'order_order_id': od['OrderID']['_value_1'],
                            'order_order_number': od['OrderNumber'],
                            'client_po': od['ClientPONumber'],
                            'custom_work_order_fields': od['CustomOrderFields'],
                            'sales_work_order_id': od['SalesWorkOrderID']['_value_1'],
                            'product_type': od['ProductType'],
                            'list_vendor': od['ListVendor'],
                            'finishing_options': (settings.clean_json(od['FinishingOptions']) if
                                                  od['FinishingOptions'] is not None else None),
                            'coupons': od['Coupons'],
                            'attached_files': (settings.clean_json(od['AttachedFiles']) if
                                               od['AttachedFiles'] is not None else None),
                            'uploaded_files': (settings.clean_json(od['UploadedFiles']) if
                                               od['UploadedFiles'] is not None else None),
                            'sku_inventory_settings': od['SKUInventorySettings'],
                            'pagecount': od['PageCount'],
                            'catalog_tree_node_id': od['CatalogTreeNodeExternalId'],
                            'job_direct_options': od['JobDirectOptions'],
                            'impersonator_fields': (settings.clean_json(od['Impersonator']) if
                                                    od['Impersonator'] is not None else None),
                            'requisition_status': od['RequisitionStatus'],
                            'approver_user': od['ApproverUser'],
                            'explanation': od['Explanation'],
                            'job_direct_settings': od['JobDirectSettings']
                            })


class OrderDetailUsers:
    # create a order_detail_users list object for WebUser table from the order details
    def __init__(self):
        self.groups = []

    def append_to_group(self, od, elem):
        self.groups.append({'user_id': od['User']['ID']['_value_1'],
                            'fname': od['User']['FirstName'],
                            'lname': od['User']['LastName'],
                            'login_id': od['User']['LoginID'],
                            'email': od['User']['Email'],
                            'generic_user_fields': (settings.clean_json(od['User']['GenericUserFields']) if
                                                    od['User']['GenericUserFields'] is not None else None),
                            'update_date': datetime.datetime.strftime(elem['CreateDate'], "%Y-%m-%d %H:%M:%S"),
                            })


class SalesWork:
    # create a sales_work list object for SalesWorkOrder table
    def __init__(self):
        self.groups = []

    def append_to_group(self, order_id, swo):
        self.groups.append({'order_id': order_id,
                            'sales_work_order_id': swo['ID']['_value_1'],
                            'order_number': swo['OrderNumber'],
                            'supplier_name': swo['SupplierName'],
                            'credit_card': (settings.clean_json(swo['CreditCard']) if
                                            swo['CreditCard'] is not None else None),
                            'handling': swo['Handling']
                            })


class ShipAddr(dict):
    # create a ship_addr dictionary object for BillingAddress table
    def init_values(self, elem):
        self['id'] = elem['ShippingAddress']['ID']['_value_1']
        self['description'] = elem['ShippingAddress']['Description']
        self['address1'] = elem['ShippingAddress']['Address1']
        self['address2'] = elem['ShippingAddress']['Address2']
        self['address3'] = elem['ShippingAddress']['Address3']
        self['city'] = elem['ShippingAddress']['City']
        self['state'] = elem['ShippingAddress']['State']
        self['zip'] = elem['ShippingAddress']['Zip']
        self['country'] = elem['ShippingAddress']['Country']
        self['phone'] = elem['ShippingAddress']['PhoneNumber']
        self['fax'] = elem['ShippingAddress']['FaxNumber']
        self['company_name'] = elem['ShippingAddress']['CompanyName']
        self['attn'] = elem['ShippingAddress']['Attn']
        self['email'] = elem['ShippingAddress']['Email']
        self['type'] = elem['ShippingAddress']['Type']
        self['default_addr'] = (1 if (elem['ShippingAddress']['Default']) == 'True' else 0)


class BillAddr(dict):
    # create a ship_addr dictionary object for BillingAddress table
    def init_values(self, elem):
        self['id'] = elem['BillingAddress']['ID']['_value_1']
        self['description'] = elem['BillingAddress']['Description']
        self['address1'] = elem['BillingAddress']['Address1']
        self['address2'] = elem['BillingAddress']['Address2']
        self['address3'] = elem['BillingAddress']['Address3']
        self['city'] = elem['BillingAddress']['City']
        self['state'] = elem['BillingAddress']['State']
        self['zip'] = elem['BillingAddress']['Zip']
        self['country'] = elem['BillingAddress']['Country']
        self['phone'] = elem['BillingAddress']['PhoneNumber']
        self['fax'] = elem['BillingAddress']['FaxNumber']
        self['company_name'] = elem['BillingAddress']['CompanyName']
        self['attn'] = elem['BillingAddress']['Attn']
        self['email'] = elem['BillingAddress']['Email']
        self['type'] = elem['BillingAddress']['Type']
        self['default_addr'] = (1 if (elem['BillingAddress']['Default']) == 'True' else 0)


class Company(dict):
    # create a company dictionary object for Company table
    def init_values(self, elem):
        self['company_id'] = elem['Company']['ID']['_value_1']
        self['company_name'] = elem['Seller']['Name']


class Seller(dict):
    # create a seller dictionary object for Seller table
    def init_values(self, elem):
        self['seller_id'] = elem['Seller']['ID']['_value_1']
        self['seller_name'] = elem['Seller']['Name']


class User(dict):
    # create a user dictionary object for WebUser table
    def init_values(self, elem):
        self['user_id'] = elem['User']['ID']['_value_1']
        self['fname'] = elem['User']['FirstName']
        self['lname'] = elem['User']['LastName']
        self['login_id'] = elem['User']['LoginID']
        self['generic_user_fields'] = ""
        self['email'] = elem['User']['Email']
        self['update_date'] = datetime.datetime.strftime(elem['CreateDate'], "%Y-%m-%d %H:%M:%S")
        self['user_group'] = (settings.clean_json(elem['UserGroups']['UserGroup']) if
                              elem['UserGroups']['UserGroup'] is not None else None)


class Record(dict):
    # create a rec dictionary object for OrderByRequest table
    def init_values(self, elem, token, fetch_date):
        self['order_id'] = elem['ID']['_value_1']
        self['order_number'] = elem['OrderNumber']
        self['order_description'] = elem['Description']
        self['create_date'] = elem['CreateDate']
        self['status'] = elem['Status']
        self['user_id'] = elem['User']['ID']['_value_1']
        self['user_group_syncmode'] = elem['UserGroups']['SyncMode']
        self['user_group_all_or_none'] = elem['UserGroups']['AllOrNone']
        self['seller_id'] = elem['Seller']['ID']['_value_1']
        self['company_id'] = elem['Company']['ID']['_value_1']
        self['supplier'] = elem['Supplier']
        self['billing_address_id'] = elem['BillingAddress']['ID']['_value_1']
        self['shipping_address_id'] = elem['ShippingAddress']['ID']['_value_1']
        self['payment_method'] = elem['PaymentMethod']
        self['payment_method_detail'] = elem['PaymentMethodDetail']
        self['credit_card'] = (settings.clean_json(elem['CreditCard']) if
                               elem['CreditCard'] is not None else None)
        self['attached_files'] = elem['AttachedFiles']
        self['token'] = token
        self['fetch_date'] = fetch_date


def order_request_by_date(date_start, date_end, portal_cxn,  overwrite_download=True):
    request_datetime = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")

    # set the database for request
    database = portal_cxn['connection'].__dict__['_database']

    # Make a sql connection
    # conn = portal_cxn['connection'].cursor(buffered=True, dictionary=True)
    conn = portal_cxn['connection']
    cursor = conn.cursor()

    # get a set of all the order_id's we run before, so we can skip if already done
    history = get_request_history(database, cursor)

    client = zeep.Client(portal_cxn['order_wsdl'])
    # print(client.namespaces)

    elem = client.get_element('ns1:OrderRequestByDate')
    arg = elem(PartnerCredentials=portal_cxn['token'],
               DateRange={'Start': date_start, 'End': date_end})

    flash("Initializing OrderRequestByDate API connection")

    # creates python dict
    response = (client.service.GetOrdersByDate(arg))
    flash("Returning API response")

    # Initialize a commit counter
    commit_cnt = 0
    # Initialize processing date
    process_date = ''
    # Let's keep track of all the processing dates, we'll use this later to
    # update all the FedEx tables in web_api_transactions.web_request_by_date()
    process_date_set = set()

    # Loop through all the first level elements in each response record
    try:
        for n, elem in enumerate(response.GetOrdersResponse.Orders.Order):
            rec = Record()
            rec.init_values(elem, portal_cxn['token_name'], request_datetime)

            user = User()
            user.init_values(elem)

            seller = Seller()
            seller.init_values(elem)

            company = Company()
            company.init_values(elem)

            bill_addr = BillAddr()
            bill_addr.init_values(elem)

            ship_addr = ShipAddr()
            ship_addr.init_values(elem)

            sales_work = SalesWork()
            order_detail_users = OrderDetailUsers()
            order_detail = OrderDetail()
            supplier = Supplier()

            for swo in elem['SalesWorkOrders']['SalesWorkOrder']:
                sales_work.append_to_group(rec['order_id'], swo)

            # the WebUser table is populated from two sources:
            # OrderRequestByDate.OrderDetails.OrderDetail and the OrderRequestByDate objects
            for od in elem['OrderDetails']['OrderDetail']:
                order_detail_users.append_to_group(od, elem)
                order_detail.append_to_group(od, rec['order_id'])
                supplier.append_to_group(od)

            # print the process date
            if datetime.datetime.strftime(rec['create_date'], '%Y-%m-%d') != process_date:
                process_date = datetime.datetime.strftime(rec['create_date'], '%Y-%m-%d')
                process_date_set.add(process_date)
                flash('Processing Orders for: {0}'.format(process_date))

            # """Insert MySQL update functions here"""
            if rec['order_id'] not in history or overwrite_download:
                flash("Updating {0} order id: {1}".format(portal_cxn['token_name'], rec['order_id']))

                replace_into_table(rec, 'OrderRequestByDate', cursor, database)
                replace_into_table(company, 'Company', cursor, database)
                replace_into_table(order_detail.groups, 'OrderDetail', cursor, database)
                replace_into_table(sales_work.groups, 'SalesWorkOrder', cursor, database)
                replace_into_table(supplier.groups, 'Supplier', cursor, database)
                replace_into_table(bill_addr, 'BillingAddress', cursor, database)
                replace_into_table(ship_addr, 'ShippingAddress', cursor, database)

                replace_into_webuser(user, cursor, database)
                update_webuser(order_detail_users.groups, cursor, database)

                replace_into_table(seller, 'Seller', cursor, database)
                replace_into_table({'order_id': rec['order_id'],
                                    'request_date': request_datetime}, 'RequestHistory', cursor, database)

                # commit every 10th record
                if commit_cnt == 9:
                    conn.commit()
                    commit_cnt = 0
                else:
                    commit_cnt += 1

            else:
                flash("Skipping order id: {}".format(rec['order_id']))

        conn.commit()
        return process_date_set

    except AttributeError:
        flash("No API response for chosen data range")


def print_dict(d):
    """
    Sends a readable key --> value to the console
    :param d: dictionary or list of dictionaries
    """
    if isinstance(d, (list,)):
        for entry in d:
            for key, value in entry.items():
                print("{0} --> {1}".format(key, value))

    if isinstance(d, (dict,)):
        for key, value in d.items():
            print("{0} --> {1}".format(key, value))


def update_fedex_tables(create_date, portal_cxn):
    # set the database for request
    database = portal_cxn['connection'].__dict__['_database']

    # Make a sql connection
    conn = portal_cxn['connection']
    cursor = conn.cursor()

    try:
        sql = ("CALL {database}.add_to_fedex_shipping('{create_date}');".format(database=database,
                                                                                create_date=create_date))
        cursor.execute(sql)
        conn.commit()

    except mariadb.Error as err:
        flash("Error: {}".format(err))
        print("Error: {}".format(err))


def replace_into_webuser(record_obj, cursor, database):
    """
    Inserts into WebUser table.  For use with User class object only.
    This function does not include the generic_user_fields.  Those fields
    are updated with the update_webuser function, using the OrderDetailUsers class object.
    """
    try:
        placeholders = (', '.join(['%s'] * len(record_obj)))
        fields = ', '.join(record_obj.keys())
        sql = "REPLACE INTO {database}.WebUser ({fields}) VALUES ({placeholders});".format(fields=fields,
                                                                                           placeholders=placeholders,
                                                                                           database=database)
        cursor.execute(sql, list(record_obj.values()))

    except mariadb.Error as err:
        flash("Error: {}".format(err))
        print("Error: {}".format(err))


def update_webuser(record_obj, cursor, database):
    """
    Updates WebUser table with an OrderDetailUsers class object.  OrderDetailUsers objects
    are defined at the ORDER DETAIL level.  This will update the fields: 'fname', 'lname',
    'login_id', 'email', 'generic_user_fields' to the fields at the ORDER DETAIL level.
    """
    try:
        for entry in record_obj:
            for key in ['fname', 'lname', 'login_id', 'email', 'generic_user_fields', 'update_date']:
                sql = "UPDATE {database}.WebUser SET {key} = %s WHERE user_id = %s;".format(key=key,
                                                                                            database=database)
                cursor.execute(sql, (entry[key], entry['user_id']))

    except mariadb.Error as err:
        flash("Error: {}".format(err))
        print("Error: {}".format(err))


def insert_into_table(record_obj, table, conn):
    """
    This should be used for inserting with no replacement.
    Possible PRIMARY KEY conflicts!
    :param record_obj: object to be used to fill table 'table'
    :param table: table to insert records into
    :param conn: current MariaDB connection
    """
    try:
        cursor = conn.cursor()

        if isinstance(record_obj, (dict,)):
            placeholders = (', '.join(['%s'] * len(record_obj)))
            fields = ', '.join(record_obj.keys())
            sql = ("INSERT INTO {table} ({fields}) VALUES ({placeholders});".format(fields=fields,
                                                                                    placeholders=placeholders,
                                                                                    table=table))
            cursor.execute(sql, list(record_obj.values()))

        if isinstance(record_obj, (list,)):
            for entry in record_obj:
                placeholders = (', '.join(['%s'] * len(entry)))
                fields = ', '.join(entry.keys())
                sql = ("INSERT INTO {table} ({fields}) VALUES ({placeholders});".format(fields=fields,
                                                                                        placeholders=placeholders,
                                                                                        table=table))
                cursor.execute(sql, list(entry.values()))

    except mariadb.Error as err:
        flash("Error: {}".format(err))
        print("Error: {}".format(err))


def replace_into_table(record_obj, table, cursor, db):
    """
    This should be used for inserting WITH replacement
    If a record already exists with the same primary index,
    the old record will be deleted and the new record will be added

    :param record_obj: object to be used to fill table 'table'
    :param db: database to insert records into
    :param table: table to insert records into
    :param cursor: current MariaDB cursor connection
    """
    try:
        if isinstance(record_obj, (dict,)):
            placeholders = (', '.join(['%s'] * len(record_obj)))
            fields = ', '.join(record_obj.keys())
            sql = ("REPLACE INTO {db}.{table} ({fields}) VALUES ({placeholders});".format(fields=fields,
                                                                                          placeholders=placeholders,
                                                                                          table=table,
                                                                                          db=db))
            cursor.execute(sql, list(record_obj.values()))

        if isinstance(record_obj, (list,)):
            for entry in record_obj:
                placeholders = (', '.join(['%s'] * len(entry)))
                fields = ', '.join(entry.keys())
                sql = ("REPLACE INTO {table} ({fields}) VALUES ({placeholders});".format(fields=fields,
                                                                                         placeholders=placeholders,
                                                                                         table=table))
                cursor.execute(sql, list(entry.values()))

    except mariadb.Error as err:
        flash("Error: {}".format(err))
        print("Error: {}".format(err))


def get_request_history(database, cursor):
    """
    :param database: database the table, RequestHistory is in
    :param cursor: db connection cursor
    :return: historical list of api request order_id
    """
    results = set()
    try:
        sql = "SELECT order_id FROM {database}.RequestHistory;".format(database=database)
        cursor.execute(sql)
        for result in cursor:
            results.add(str(result[0]))

        return results

    except mariadb.Error as err:
        flash("Error: {}".format(err))
        print("Error: {}".format(err))


if __name__ == '__main__':
    pass
