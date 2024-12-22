import yaml, os

API_CONFIG = yaml.load(open('./app/api_config.yml', encoding='utf-8'),
                       Loader=yaml.FullLoader)
if os.environ.get('SUPPORTED_PARAMS'):
    SUPPORTED_PARAMS = os.environ.get('SUPPORTED_PARAMS').split(',')
else:
    SUPPORTED_PARAMS = [f'{game}.{channal}' for game in API_CONFIG for channal in API_CONFIG[game] ]
CACHE_TIME = 3600
CACHE_INVALID_TIME = 2 * 24 * 3600
CACHE_PATH = './data'
VIDEO_PATTERN = r'https?://[^ ]+\.(mp4|mov)'

ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'token')
