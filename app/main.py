import aioredis
from fastapi import FastAPI, Request
from starlette.responses import FileResponse, HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

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


app.mount("/app/static", StaticFiles(directory="app/static"), name="static")


@app.get("/front")
async def get_index(request: Request):
    return FileResponse("app/static/front.html")


@app.get("/tree")
async def get_index(request: Request):
    return FileResponse("app/static/tree.html")


# @app.get("/single_category/{id}")
# async def get_single_category(id: int, request: Request):
#     return FileResponse("app/static/single_category.html")

templates = Jinja2Templates(directory="app/templates")


@app.get("/single_category/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="single_category.html", context={"id": id}
    )

# @app.get("/single_category/{id}")
# async def get_single_category(request: Request, id: int):
#     return templates.TemplateResponse("single_category.html", {"request": request, "category_id": id})


# @app.get("/single_category/{category_id}")
# async def get_single_category(category_id: int, request: Request):
#     # Logic to fetch data for the single category with category_id
#     # This can include fetching data from your database or other sources
#
#     # Once you have the data, you can pass it to your HTML template
#     # and render the template with the data
#
#     # Example: You can render a Jinja2 template passing the category data
#     return templates.TemplateResponse("tree.html", {"category_id": category_id})
