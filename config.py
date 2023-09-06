import os

database = 'nibas'
user = 'nibas'
# database = 'administrative_enheter'
# user = 'dbles'
port = '5432'
host = os.environ.get('DBCLUSTER_2')
password = os.environ.get('PG_PASS_ADM_ENH')

dbc = {'database': database, 'user': user,
              'port': port, 'host': host, 'password': password}

defSrid = 4258
set_json_as_ascii = False
locale_choice = 'nn_NO.utf8'

