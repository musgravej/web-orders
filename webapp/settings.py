import configparser
import re
import json

"""
Home to the GlobalVar class, and other classes and functions that 
need to be accessible through the whole application 
"""


class GlobalVar:
    def __init__(self, config_file_path):
        config = configparser.ConfigParser()
        config.read(config_file_path)

        # VERY IMPORTANT
        self.environment = 'DEV'
        # self.environment = 'PRODUCTION'

        self.wellmark_token = config['token']['wellmark_token']
        self.fb_token = config['token']['fb_token']
        self.medica_token = config['token']['medica_token']
        self.go_token = config['token']['go_token']
        self.waukee_token = config['token']['waukee_token']
        self.capital_token = config['token']['capital_token']
        self.hyvee_token = config['token']['hyvee_token']
        self.polkco_token = config['token']['polkco_token']

        self.closeout_token = config['token']['closeout_token']
        self.db_user = config['db_credentials']['user']
        self.db_password = config['db_credentials']['password']
        self.db_host = config['db_credentials']['host']

        # Push XML to MarcomCentral
        self.closeout_url = config['closeout']['production']
        self.closeout_url_wsdl = config['closeout']['production_wsdl']

        # Pull XML order information from MarcomCentral platform – each portal will have a different Token
        self.order_url = config['order']['production']
        self.order_url_wsdl = config['order']['production_wsdl']

        self.jobticket_url = config['jobticket']['production']
        self.jobticket_url_wsdl = config['jobticket']['production_wsdl']

        self.token_names = {self.wellmark_token: 'Wellmark',
                            self.fb_token: 'Farm Bureau',
                            self.medica_token: 'Medica',
                            self.go_token: 'Guide One',
                            self.waukee_token: 'Waukee',
                            self.capital_token: 'Capitol Orthopaedics',
                            self.hyvee_token: 'HyVee',
                            self.polkco_token: 'Polk County',
                            }

        self.db_name = {self.wellmark_token: 'Wellmark',
                        self.fb_token: 'FarmBureau',
                        self.medica_token: 'Medica',
                        self.go_token: 'GuideOne',
                        self.waukee_token: 'Waukee',
                        self.capital_token: 'Capitol',
                        self.hyvee_token: 'HyVee',
                        self.polkco_token: 'PolkCo',
                        }

        self.dev_db_name = {self.wellmark_token: 'WellmarkDev',
                            self.fb_token: 'FarmBureauDev',
                            self.medica_token: 'MedicaDev',
                            self.go_token: 'GuideOneDev',
                            self.waukee_token: 'WaukeeDev',
                            self.capital_token: 'CapitolDev',
                            self.hyvee_token: 'HyVeeDev',
                            self.polkco_token: 'PolkCoDev',
                            }


def clean_json(json_string):
    """
    This is a stupid way to deal with a problem it was taking me all f-ing day
    to figure out.  You're welcome.

    :param json_string as string to clean up json formatting
    """
    json_string = "".join(str(json_string))

    rpl_1 = re.compile("': '")
    rpl_2 = re.compile("\s{4}'")
    rpl_3 = re.compile("':")
    rpl_4 = re.compile("',\n")
    rpl_5 = re.compile("'\n")
    rpl_6 = re.compile('=""')
    rpl_7 = re.compile("\\'")
    rpl_8 = re.compile('[\d]""')

    cleaned_json = re.sub(rpl_1, '": "', json_string)
    cleaned_json = re.sub(rpl_2, '    "', cleaned_json)
    cleaned_json = re.sub(rpl_3, '":', cleaned_json)
    cleaned_json = re.sub(rpl_4, '",\n', cleaned_json)
    cleaned_json = re.sub(rpl_5, '"\n', cleaned_json)
    cleaned_json = re.sub(rpl_6, '=\"\"', cleaned_json)

    cleaned_json = str.replace(cleaned_json, "\\'", "'")

    for r in rpl_8.findall(cleaned_json):
        cleaned_json = re.sub(r, '{}\\""'.format(r[:-2]), cleaned_json)

    return cleaned_json


def search_json_list(cursor, search_key, search_value, result_key, contains_keys=False):
    """
    Returns a list of matching values in a json array
    Takes connection cursor and key result returns dictionary (key, result)
    If contains_keys is True, looks to first field in cursor results for key
    If contains_keys is False, assigns dictionary key as position in cursor result

    :parameter cursor: object after cursor.execute()
    :parameter search_value: value to match in key search
    :parameter search_key: object key to search
    :parameter result_key: key to look in for value

    Example:
        {
        search_key : search_value,
        result_key : [FUNCTION RETURNS THIS VALUE]
        }
    """
    cursor_results = cursor.fetchall()
    key_list = []

    if contains_keys:
        key_list = [r[0] for r in cursor_results]
        cursor_results = ([r[1] for r in cursor_results])

    if not key_list:
        key_list = range(1, len(cursor_results) + 1)

    return_result = dict()

    if not contains_keys:
        for key, fetch in zip(key_list, cursor_results):
            for rec in fetch:
                template = json.loads(rec)
                result = ([field[result_key] for field in template
                           if field[search_key] == search_value])
                if result:
                    return_result[key] = result[0]
    else:
        for key, fetch in zip(key_list, cursor_results):
            print(key, fetch)
            template = json.loads(fetch)
            result = ([field[result_key] for field in template
                       if field[search_key] == search_value])
            if result:
                return_result[key] = result[0]

    return return_result


def main():
    pass


if __name__ == '__main__':
    main()
