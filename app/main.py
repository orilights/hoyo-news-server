from importlib import import_module
from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.utils import *

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
)

@app.on_event("startup")
def startup_event():
    print('SUPPORTED_PARAMS', config.SUPPORTED_PARAMS)
    for params in config.SUPPORTED_PARAMS:
        game, channal = params.split('.')
        cache = read_cache(params)
        if cache is None or is_expired(cache['update'],
                                       config.CACHE_INVALID_TIME):
            print(f'未检测到 {game}.{channal} 缓存或缓存已过期')


@app.get('/{game}/{channal}')
def get_game_news(game: str, channal: str, force_refresh: int = 0):
    index = f'{game}.{channal}'
    if index not in config.SUPPORTED_PARAMS:
        return {'code': 1, 'msg': '配置不存在'}

    channal_config = config.API_CONFIG[game][channal]

    cache = read_cache(index)
    if cache != None and force_refresh == 0:
        if not is_expired(cache['update'], config.CACHE_TIME):
            return {'code': 0, **cache}

    try:
        adapter = import_module(f'app.adapter.{channal_config["adapter"]}')
        data = adapter.get_news(channal_config, cache=cache)
        if data is None:
            if cache:
                return {'code': 1, 'msg': '刷新数据失败，请稍后再试，如有疑问请在 Github Issue 中提出', **cache}
            return {'code': 1, 'msg': '刷新数据失败，请稍后再试，如有疑问请在 Github Issue 中提出'}

        write_cache(index, data)
        return {'code': 0, **data}

    except Exception as e:
        print(e)
        if cache:
            return {'code': 1, 'msg': '服务器错误，请稍后再试，如有疑问请在 Github Issue 中提出', **cache}
        return {'code': 1, 'msg': '服务器错误，请稍后再试，如有疑问请在 Github Issue 中提出'}


@app.get('/refresh_all')
def refresh_all(token: Union[str, None] = None, full: int = 0):
    if token != config.ADMIN_TOKEN:
        return {'code': 1, 'msg': '无权限执行此操作'}
    statistics = {}
    for params in config.SUPPORTED_PARAMS:
        game, channal = params.split('.')
        channal_config = config.API_CONFIG[game][channal]
        try:
            adapter = import_module(f'app.adapter.{channal_config["adapter"]}')
            cache = None if full == 1 else read_cache(f'{game}.{channal}')
            data = adapter.get_news(channal_config, cache=cache)
            if data is None:
                print(f'{params} 获取数据失败')
                continue

            write_cache(f'{game}.{channal}', data)
            print(f'{game}.{channal} 刷新成功')
            statistics[f'{game}.{channal}'] = len(data['data'])
        except Exception as e:
            print(f'{game}.{channal} 刷新失败')
            print(e)
    return {'code': 0, 'msg': '刷新完成', 'data': statistics}
