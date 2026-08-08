from fastapi import FastAPI

from app.api.feed_route import router as feed_router
from app.api.init_route import router as init_router

app = FastAPI()

app.include_router(init_router)
app.include_router(feed_router)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
