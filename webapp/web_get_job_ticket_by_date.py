import zeep
import re
from flask import flash
import mysql.connector as mariadb


def get_order_detail_by_order(database, db_param, order_id):
    results = []
    try:
        conn = mariadb.connector.connect(database=database, **db_param)
        cursor = conn.cursor()

        sql = ("SELECT `order_detail_id`, `quantity` FROM OrderDetail "
               "WHERE `order_order_number` = %s "
               "AND `supplier_id` IN ('3331','3536');")

        cursor.execute(sql, (order_id,))
        for result in cursor:
            results.append({'item_ID': result[0], 'item_qty': result[1]})

        conn.close()
        return results

    except mariadb.connector.Error as err:
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


def replace_into_job_ticket_instructions(record_obj, cursor, database):
    """
    Inserts into JobTicketInstructions table.
    """
    try:
        placeholders = (', '.join(['%s'] * len(record_obj)))
        fields = ', '.join(record_obj.keys())
        sql = ("REPLACE INTO {database}.JobTicketInstructions ({fields}) "
               "VALUES ({placeholders});".format(fields=fields,
                                                 placeholders=placeholders,
                                                 database=database))

        cursor.execute(sql, list(record_obj.values()))

    except mariadb.Error as err:
        print("Error: {}".format(err))


def job_ticket_by_date(date_start, date_end, portal_cxn):
    # set the database for request
    database = portal_cxn['connection'].__dict__['_database']

    # Make a sql connection
    # conn = portal_cxn['connection'].cursor(buffered=True, dictionary=True)
    conn = portal_cxn['connection']
    cursor = conn.cursor()

    # history = get_request_history(database, cursor)

    client = zeep.Client(portal_cxn['jobticket_wsdl'])
    elem = client.get_element('ns1:JobTicketRequestByDate')

    arg = elem(PartnerCredentials=portal_cxn['token'],
               DateRange={'Start': date_start, 'End': date_end})

    flash("Initializing JobTicketRequestByDate API connection", 'message')
    print("Initializing JobTicketRequestByDate API connection")

    # # creates python dict
    response = (client.service.GetJobTicketsByDate(arg))
    if isinstance(response, type(None)):
        flash("No API response for chosen data range", 'message')
        return

    flash("Returning API response", 'message')
    print("Returning API response")

    # Initialize a commit counter
    commit_cnt = 0
    # Remove pesky non-ascii characters
    replace = re.compile(r'[^\x00-\x7F]+')

    try:
        for n, elem in enumerate(response):
            values = dict()
            values['order_job_ticket_number'] = (elem['JobTicketNumber'])

            values['shipping_instructions'] = (elem['JobTicketInstructions']['ShippingInstructions']
                                               if elem['JobTicketInstructions']['ShippingInstructions']
                                               is not None else None)

            values['general_description'] = (elem['JobTicketInstructions']['GeneralDescription']
                                             if elem['JobTicketInstructions']['GeneralDescription']
                                             is not None else None)

            values['paper_description'] = (elem['JobTicketInstructions']['PaperDescription'])
            values['film_description'] = (elem['JobTicketInstructions']['FilmDescription'])
            values['press_instructions'] = (elem['JobTicketInstructions']['PressInstructions'])
            values['bindery_instructions'] = (elem['JobTicketInstructions']['BinderyInstructions'])

            for d in elem['OrderDetails']['OrderDetail']:
                values['order_order_number'] = (d['OrderNumber'])
                values['order_detail_id'] = (d['ID']['_value_1'])
                values['order_id'] = (d['OrderID']['_value_1'])
                values['shipping'] = (d['Shipping']['Method'] if d['Shipping']['Method'] is not None else None)

                flash("Updating {0} job ticket, order id: {1}".format(portal_cxn['token_name'], values['order_id']))
                print("Updating {0} job ticket, order id: {1}".format(portal_cxn['token_name'], values['order_id']))
                replace_into_job_ticket_instructions(values, cursor, database)

            # commit every 10th record
            if commit_cnt == 9:
                conn.commit()
                commit_cnt = 0
            else:
                commit_cnt += 1

        conn.commit()

    except AttributeError:
        flash("No API response for chosen data range", 'message')
        print("No API response for chosen data range")


if __name__ == '__main__':
    pass
