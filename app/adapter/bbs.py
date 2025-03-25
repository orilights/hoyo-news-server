import time

import requests

from app.utils import *

PAGE_SIZE = 50


def transform_news(news_raw):
    cover = news_raw['post']['cover']
    if (not cover or cover == '') and news_raw['cover']:
        cover = news_raw['cover']['url']

    if not cover and len(news_raw['post']['images']) > 0:
        cover = news_raw['post']['images'][0]

    if not cover:
        print(f'no cover: {news_raw["post"]["post_id"]}')

    return ({
        'id': int(news_raw['post']['post_id']),
        'title': news_raw['post']['subject'],
        'startTime': news_raw['post']['created_at'],
        'createTime': news_raw['post']['created_at'],
        'cover': cover,
        'video': None,
    })


def get_page(session, api_url, page_size, last_id):
    res = session.get(api_url.format(page_size=page_size, last_id=last_id))
    if not res.ok:
        return None

    ret_data = res.json()
    if ret_data['retcode'] != 0:
        return None
    print(f'last_id: {last_id} , count: {len(ret_data["data"]["list"])}')
    is_last_page = len(ret_data['data']['list']) == 0

    return ret_data['data']['list'], is_last_page


def get_news(config, cache=None):
    api_url = config['url']

    news_list = []
    cache_data = cache['data'] if cache else []
    cache_index = [news['id'] for news in cache_data]
    current_page = 1
    session = requests.Session()
    while True:
        print(f'get page: {current_page}')
        response, is_last_page = get_page(session, api_url, PAGE_SIZE,
                                          (current_page - 1) * PAGE_SIZE)

        news_list.extend([transform_news(news) for news in response])
        current_page += 1
        if is_last_page:
            break

        if news_list and news_list[-1]['id'] in cache_index:
            match_position = cache_index.index(news_list[-1]['id'])
            remaining_cache_data = cache_data[match_position + 1:]
            news_list.extend(remaining_cache_data)
            break
        time.sleep(0.3)

    session.close()

    return {'update': get_ts(), 'data': news_list}
