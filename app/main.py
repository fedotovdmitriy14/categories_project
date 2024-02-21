import aioredis
from fastapi import FastAPI, Request
from starlette.responses import FileResponse, HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app import redis
from app.api.v1 import categories
from app.constants import settings
from app.services.helpers import CustomException

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


app.mount("/app/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/tree")
async def get_index(request: Request):
    return FileResponse("app/static/tree.html")


@app.get("/single_category/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="single_category.html", context={"id": id}
    )


@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.code,
        content={"message": exc.message, "code": exc.code}
    )
