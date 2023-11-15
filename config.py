import os

db_user = os.environ.get('DB_USER', default='nibas')
db_password = os.environ.get('DB_PASSWORD', default="nibas")
db_uri = os.environ.get('DB_URI', default="postgresql://localhost:5432/nibas")

defSrid = 4258
set_json_as_ascii = False
locale_choice = 'no_NO.UTF-8'
