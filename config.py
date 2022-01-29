import datetime
# DB_NAME = "farmerapp-stage"
# DB_USER = "postgres"
# DB_PASSWORD = "pass_stag_farmapp@2021"
# DB_HOST = "localhost"
# DB_PORT = 5433

# ssh -i C:\Users\sarbj\.ssh\id_rsa  -L 5433:localhost:5432 ubuntu@65.2.107.176 -N -f
# DB_NAME = 'farmerapp-live'
# DB_USER = 'postgres'
# DB_PASSWORD = 'pass_live_farmapp@2021'
# DB_HOST = 'localhost'
# DB_PORT = 5434

DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = 5432

REFRESH_TOKEN_EXP = datetime.timedelta(seconds=500)
ACCESS_TOKEN_EXP = datetime.timedelta(seconds=2592000)
SECRET_KEY = 'Artisthenotahealthy'
REGION_NAME = 'ap-south-1'
AWS_ACCESS_KEY = 'AKIASQEXC2RL3KWI5RJY'
AWS_SECRET_ACCESS_KEY = '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'
BUCKET = 'subudh-farmer-app'
FIREBASE_API_KEY = 'AAAA61ETuPo:APA91bFUjYBhRXoc7' \
                   '-FysNFj1SEs9YRdBjoCjg11myO5jr' \
                   'CXZMDg2xAW3JgB7xRei5PmHcHGAdz' \
                   'c9etlKOsskC6Qwdw0SXhs0C0AAIQG' \
                   'UbDzwSEFkX_W3-kuxCQefKCK_W5ZIDuuQxRi '

# CELERY_BROKER_URL = 'redis://ubuntu:admin@65.2.107.176:6379/0'
CELERY_BROKER_URL = 'redis://localhost:6379/0'

THINGSPEAK_KEY = 'E4PV4FJNDPRRB6BS'
GET_CHANNELS = 'https://api.thingspeak.com/channels.json?api_key={}'.format(THINGSPEAK_KEY)
GET_CHANNEL_FEED = 'https://api.thingspeak.com/channels/{}/feeds.json?api_key={}&results='

TEMP_PATH = '/home/karanjot/Projects/farmers-backend/temp/'
NODE_ODM = 'localhost'
# NODE_ODM = '172.31.35.68'