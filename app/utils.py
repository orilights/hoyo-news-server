from datetime import datetime
import os, json

from app import config

def get_ts():
    return int(datetime.now().timestamp())

def is_expired(timestamp, duration):
    if timestamp is None:
        return True
    return timestamp + duration < get_ts()

def read_cache(cache_name):
    filename = os.path.join(config.CACHE_PATH, f'cache.{cache_name}.json')
    if os.path.exists(filename):
        return json.load(open(filename, mode='r', encoding='utf-8'))
    else:
        return None

def write_cache(cache_name, data):
    if not os.path.exists(config.CACHE_PATH):
        os.makedirs(config.CACHE_PATH)
    filename = os.path.join(config.CACHE_PATH,  f'cache.{cache_name}.json')
    json.dump(data, open(filename, 'w', encoding='utf-8'), ensure_ascii=False)
