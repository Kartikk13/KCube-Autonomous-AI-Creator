from fastapi import FastAPI

from app.api.init_route import router as init_router

app = FastAPI()

app.include_router(init_router)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
