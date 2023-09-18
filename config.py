import os
import hvac
import logging

# Authentication
client = hvac.Client(
    url='http://host.docker.internal:8200',
    token='myroot',
)

mount_point = 'nibas'
secret_path = 'kommuneinfo'

secret_version_response = client.secrets.kv.v2.read_secret_version(mount_point = mount_point, path=secret_path)

database = 'nibas'
user = 'nibas'
# database = 'administrative_enheter'
# user = 'dbles'
port = secret_version_response['data']['data']['db_port']
host = secret_version_response['data']['data']['db_host']
password = secret_version_response['data']['data']['db_password']


dbc = {'database': database, 'user': user,
              'port': port, 'host': host, 'password': password}

defSrid = 4258
set_json_as_ascii = False
locale_choice = 'nn_NO.utf8'

