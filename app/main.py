import aioredis
from fastapi import FastAPI

from app import redis
from app.api.v1 import categories
from app.constants import settings

app = FastAPI(
    title='Categories API',
    version='1.0.0',
)
app.include_router(categories.router, prefix='/api/v1/categories', tags=['categories'])


@app.get('/')
async def status():
    return {'status': 'OK'}


@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.create_redis_pool((settings.redis_host, settings.redis_port), minsize=10, maxsize=20)


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await redis.redis.wait_closed()
