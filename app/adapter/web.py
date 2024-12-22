import re, math

import requests
from requests.adapters import HTTPAdapter

from app import config
from app.utils import *

PAGE_SIZE = 100


def transform_news(news_raw):
    result = {
        'id': news_raw['iInfoId'],
        'title': news_raw['sTitle'],
        'startTime': news_raw['dtStartTime'],
        'createTime': news_raw['dtCreateTime'],
        'cover': None,
        'video': None,
    }
    ext_data = json.loads(news_raw['sExt'])
    for ext in ext_data:
        datalist = ext_data[ext]
        if not isinstance(datalist, list):
            continue
        for data in datalist:
            if data.get('url'):
                if data['url'].startswith('http'):
                    result['cover'] = data['url']
                    break
        if result['cover']:
            break
    if video := re.search(config.VIDEO_PATTERN, news_raw['sContent']):
        result['video'] = video.group(0)
    return result


def get_count(api_url):
    res = requests.get(api_url.format(page=1, page_size=5))
    if not res.ok:
        return None

    ret_data = res.json()
    if ret_data['retcode'] != 0:
        return None

    return ret_data['data']['iTotal']


def patch_news(news: list, patch: list, total: int):
    if total <= len(patch):
        return patch
    return patch + news[-(total - len(patch)):]


def get_page(session,api_url, page_size, page):
    res = session.get(api_url.format(page_size=page_size, page=page))
    if not res.ok:
        return None

    ret_data = res.json()
    if ret_data['retcode'] != 0:
        return None

    return ret_data['data']['list']


def get_news(config, cache=None):
    api_url = config['url']

    news_list = []
    news_count = get_count(api_url)
    cache_data = cache['data'] if cache else []
    print(f"count: {news_count}")
    current_page = 1
    max_page = math.ceil((news_count - len(cache_data)) / PAGE_SIZE)
    if max_page == 0:
        max_page = 1
    print(f'max_page: {max_page}')

    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=3))
    while current_page <= max_page:
        print(f'get page: {current_page}')
        news_list.extend(get_page(session,api_url, PAGE_SIZE, current_page))
        current_page += 1
    session.close()

    patch = [transform_news(news) for news in news_list]
    news_list = patch_news(cache_data, patch, news_count)

    return {'update': get_ts(), 'data': news_list}
