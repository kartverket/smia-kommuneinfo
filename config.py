import os

db_user = os.environ.get('KOMMUNEINFO_DB_USER', default='nibas')
db_password = os.environ.get('KOMMUNEINFO_DB_PASSWORD', default="nibas")
db_uri = os.environ.get('KOMMUNEINFO_DB_URI', default="postgresql://localhost:5432/nibas")
app_ingress = os.environ.get("KOMMUNEINFO_INGRESS", default="localhost:5000")

defSrid = 4258
set_json_as_ascii = False
locale_choice = 'no_NO.UTF-8'
