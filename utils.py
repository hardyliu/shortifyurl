import trafaret as t
import aioredis
import yaml
from aiohttp import web


CONFIG_TRAFARET = t.Dict(
    {
        t.Key('redis'): t.Dict({
            'port': t.Int(),
            'host': t.String(),
            'db': t.Int(),
            'minsize': t.Int(),
            'maxsize': t.Int(),

        }),
        'host': t.IP,
        'port': t.Int(),
    }
)


def load_config(fname):
    with open(fname,'rt') as f:
        data = yaml.load(f, Loader=yaml.CLoader)

    return CONFIG_TRAFARET.check(data)


async def init_redis(conf):
    pool = await aioredis.from_url('redis://'+conf['host'], port=conf['port'], db=conf['db'])
    return pool

CHARS = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'


def encode(num, alphabet = CHARS):
    if num == 0:
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        num, rem = divmod(num, base)
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


ShortifyRequest = t.Dict({
    t.Key('url'): t.URL
})


def fetch_url(data):
    try:
        data = ShortifyRequest(data)
    except t.DataError:
        raise web.HTTPBadRequest('Url is not valid')
    return data['url']



