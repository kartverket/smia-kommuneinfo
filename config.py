import os

db_user = os.environ.get('KOMMUNEINFO_DB_USER', default='kominfo')
db_password = os.environ.get('KOMMUNEINFO_DB_PASSWORD', default="kominfo")
db_uri = os.environ.get('KOMMUNEINFO_DB_URI',
                        default="postgresql://localhost:5430/kominfo")
app_ingress = os.environ.get("KOMMUNEINFO_INGRESS", default="localhost:5000")

is_dev = True if app_ingress == "localhost:5000" else False
defSrid = 4258
set_json_as_ascii = False
locale_choice = 'no_NO.UTF-8'
