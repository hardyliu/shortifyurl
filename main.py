import asyncio
import logging
import pathlib
from utils import init_redis, load_config
import aiohttp_jinja2
import jinja2
from aiohttp import web
from routes import setup_routes
from views import SiteHandler

PROJ_ROOT = pathlib.Path(__file__).parent
TEMPLATES_ROOT = pathlib.Path(__file__).parent / 'templates'


async def setup_redis(app, conf):
    """
    建立redis连接池
    :param app:
    :param conf: 配置redis相关信息
    :return:
    """
    pool = await init_redis(conf['redis'])

    async def close_redis(app):
        pool.close()
        await pool.wait_closed()

    app.on_cleanup.append(close_redis)
    app['redis_pool'] = pool
    return pool


def setup_jinja(app):
    loader = jinja2.FileSystemLoader(str(TEMPLATES_ROOT))
    jinja_env = aiohttp_jinja2.setup(app, loader=loader)
    return jinja_env


async def init():
    """
    初始化web应用：1、获取配置
    2、初始化application
    3、初始化redis
    4、初始化模板
    5、建立页面和处理函数的路由关系
    :return:
    """
    conf = load_config(PROJ_ROOT/'config'/'config.yml')
    logging.info(conf)
    app = web.Application()
    redis_pool = await setup_redis(app, conf)
    setup_jinja(app)

    handler = SiteHandler(redis_pool, conf)
    setup_routes(app, handler, PROJ_ROOT)
    host, port = conf['host'],conf['port']
    return app, host, port

def main():
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    app, host, port = loop.run_until_complete(init())
    web.run_app(app, host=host, port=port)


if __name__ == '__main__':
    main()