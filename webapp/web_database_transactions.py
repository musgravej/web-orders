# import mysql.connector as mariadb
# import re
# from flask import flash


def get_table_names(portal_cxn):
    # set the database for request
    database = portal_cxn['connection'].__dict__['_database']

    # Make a sql connection
    # conn = portal_cxn['connection'].cursor(buffered=True, dictionary=True)
    conn = portal_cxn['connection']
    cursor = conn.cursor(buffered=True, dictionary=True)

    sql = ("SELECT table_name FROM information_schema.tables "
           "WHERE table_schema = '{0}' AND table_type = 'BASE TABLE';".format(database))

    cursor.execute(sql)
    return cursor.fetchall()


if __name__ == '__main__':
    pass
