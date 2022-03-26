from j2tools import YamlLoader
from jinja2 import Environment
from tools import to_t, to_k, dt_filter
from contextvars import ContextVar
from zoneinfo import ZoneInfo
import os

jinja = Environment(loader=YamlLoader('templates/ua.yml'))

admins = [788886288, 2519539]

api_server = None
api_server_host = 'localhost'
api_server_port = 8081
bot = None
bot_name = 'TG_BOT'

NATS_SERVER_URI = os.environ.get('NATS_SERVER_URI','127.0.0.1:4222')
NATS_TOKEN = os.environ.get('NATS_TOKEN','')

nc = None

current_T = ContextVar('current_T')
get_t = None

current_user = ContextVar('current_user')

validation_channel_id = -1001581247546
passes_channel_id = -1001601508518

secret_number = 9

tz = ZoneInfo('Europe/Kiev')

pass_active_hours = 12

ad_hash = '99a1f83b7f06bfbda437b74ab9381887'
api_url_available_campaigns = 'https://adbotapi.fastbots.net/available-campaigns'
api_url_get_advert = 'https://adbotapi.fastbots.net/get-advert'

