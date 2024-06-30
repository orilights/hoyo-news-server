from datetime import datetime
import json, os, re

from flask import Flask, request
from flask_cors import CORS
from flask_compress import Compress
import requests

GAME_API = {
    'genshin':
    'https://api-takumi-static.mihoyo.com/content_v2_user/app/16471662a82d418a/getContentList?iAppId=43&iChanId=719&iPageSize={pageSize}&iPage={pageNum}&sLangKey=zh-cn',
    'starrail':
    'https://api-takumi-static.mihoyo.com/content_v2_user/app/1963de8dc19e461c/getContentList?iPage={pageNum}&iPageSize={pageSize}&sLangKey=zh-cn&isPreview=0&iChanId=255',
    'honkai3':
    'https://api-takumi-static.mihoyo.com/content_v2_user/app/b9d5f96cd69047eb/getContentList?iPageSize={pageSize}&iPage={pageNum}&sLangKey=zh-cn&iChanId=693&isPreview=0',
    'zzz':
    "https://api-takumi-static.mihoyo.com/content_v2_user/app/706fd13a87294881/getContentList?iPageSize={pageSize}&iPage={pageNum}&sLangKey=zh-cn&iChanId=273",
    'mihoyo':
    "https://api-takumi-static.mihoyo.com/content_v2_user/app/537c17c553834ed6/getContentList?iPageSize={pageSize}&iPage={pageNum}&sLangKey=zh-cn&iChanId=107",
    'genshin_os':
    "https://sg-public-api-static.hoyoverse.com/content_v2_user/app/a1b1f9d3315447cc/getContentList?iAppId=32&iChanId=395&iPageSize={pageSize}&iPage={pageNum}&sLangKey=zh-tw",
    'starrail_os':
    "https://sg-public-api-static.hoyoverse.com/content_v2_user/app/113fe6d3b4514cdd/getContentList?iPage={pageNum}&iPageSize={pageSize}&sLangKey=zh-cn&isPreview=0&iChanId=248",
    'honkai3_os':
    "https://sg-public-api-static.hoyoverse.com/content_v2_user/app/5fcd2aa439ca4aea/getContentList?iPageSize={pageSize}&iPage={pageNum}&sLangKey=zh-cn&iChanId=514&isPreview=0",
    'zzz_os':
    "https://sg-public-api-static.hoyoverse.com/content_v2_user/app/3e9196a4b9274bd7/getContentList?iPageSize={pageSize}&iPage={pageNum}&iChanId=288&sLangKey=zh-cn",
    'hoyoverse':
    "https://sg-public-api-static.hoyoverse.com/content_v2_user/app/ea15ca8a7a654b5e/getContentList?isPreview=0&iPage={pageNum}&iPageSize={pageSize}&iChanId=206&sLangKey=zh-cn",
}

PAGE_SIZE = 100
CACHE_TIME = 3600
CACHE_PATH = './data'
VIDEO_PATTERN = r'https?://[^ ]+\.(mp4|mov)'

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
compress = Compress(app)


def get_news(api_url, pageSize, pageNum=1):
    res = requests.get(api_url.format(pageSize=pageSize, pageNum=pageNum))
    if not res.ok:
        return None

    ret_data = res.json()
    if ret_data['retcode'] != 0:
        return None

    return [transform_news(news) for news in ret_data['data']['list']]


def get_total(api_url):
    res = requests.get(api_url.format(pageSize=5, pageNum=1))
    if not res.ok:
        return None

    ret_data = res.json()
    if ret_data['retcode'] != 0:
        return None

    return ret_data['data']['iTotal']


def transform_news(news_raw):
    ret = {
        'id': news_raw['iInfoId'],
        'title': news_raw['sTitle'],
        'startTime': news_raw['dtStartTime'],
        'createTime': news_raw['dtCreateTime'],
        'banner': None,
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
                    ret['banner'] = data['url']
                    break
        if ret['banner']:
            break
    if video := re.search(VIDEO_PATTERN, news_raw['sContent']):
        ret['video'] = video.group(0)
    return ret


def read_cache(cache_name):
    filename = os.path.join(CACHE_PATH, cache_name + '_cache.json')
    if os.path.exists(filename):
        return json.load(open(filename, mode='r', encoding='utf-8'))
    else:
        return None


def write_cache(cache_name, data):
    if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH)
    filename = os.path.join(CACHE_PATH, cache_name + '_cache.json')
    json.dump(data, open(filename, 'w', encoding='utf-8'), ensure_ascii=False)


def get_ts():
    return int(datetime.now().timestamp())


def get_news_data(game: str):
    api_url = GAME_API[game]

    news_total = get_total(api_url)
    print(f"game: {game}")
    print(f"news: {news_total}")

    news_list = []

    current_page = 1

    while (current_page - 1) * PAGE_SIZE < news_total:
        print(f'page: {current_page}')
        news_list.extend(get_news(api_url, PAGE_SIZE, current_page))
        current_page += 1

    return {
        'updateTime': get_ts(),
        'newsCount': news_total,
        'newsData': news_list
    }


def patch_news_list(news_list: list, patch: list, total: int):
    return patch + news_list[-(total - len(patch)):]


with app.app_context():
    for game in GAME_API:
        if cache := read_cache(game):
            total = get_total(GAME_API[game])
            if total - len(cache['newsData']) < PAGE_SIZE:
                continue
        write_cache(game, get_news_data(game))


@app.route('/<game>/news', methods=['GET'])
def get_game_news(game: str):
    if game not in GAME_API:
        return {'code': 1, 'msg': '配置不存在'}
    query = request.args
    force_refresh = query.get('force_refresh', '0') == '1'
    data = read_cache(game)

    try:
        if data is None:
            data = get_news_data(game)
            if data:
                write_cache(game, data)
        if data is None:
            return {'code': 1, 'msg': '获取数据失败'}

        cache_expired = data['updateTime'] + CACHE_TIME < get_ts()
        if force_refresh or cache_expired:
            total = get_total(GAME_API[game])
            data['updateTime'] = get_ts()
            if total != data['newsCount']:
                data['newsCount'] = total
                data['newsData'] = patch_news_list(
                    data['newsData'], get_news(GAME_API[game], PAGE_SIZE, 1),
                    total)
            write_cache(game, data)
        return {'code': 0, **data}
    except Exception as e:
        print(e)
        return {'code': 1, 'msg': '服务器错误，请稍后再试'}


if __name__ == '__main__':
    app.run('0.0.0.0', port=3000, debug=True)
