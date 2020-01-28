import datetime
import web_get_order_by_date as order_by_date
import web_get_job_ticket_by_date as ticket_by_date


def web_request_by_date(start, end, portal_cxn):
    date_start = datetime.datetime.strptime("{0} 00:00:00".format(start), "%Y-%m-%d %H:%M:%S")
    date_end = datetime.datetime.strptime("{0} 23:59:59".format(end), "%Y-%m-%d %H:%M:%S")

    # last variable is overwrite download, set for False to NOT update
    process_dates = order_by_date.order_request_by_date(date_start, date_end, portal_cxn, False)

    ticket_by_date.job_ticket_by_date(date_start, date_end, portal_cxn)

    # Loop through all the order dates to update the FedEx tables
    for date in process_dates:
        order_by_date.update_fedex_tables(date, portal_cxn)


if __name__ == '__main__':
    pass
