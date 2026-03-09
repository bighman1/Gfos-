from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

import routers.rails      as rails_router
import routers.corridors  as corridors_router
import routers.heatmap    as heatmap_router
import routers.fx         as fx_router
import routers.analysis   as analysis_router

from collectors.scheduler import start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_scheduler()
    yield
    await stop_scheduler()

app = FastAPI(title="GFOS Intelligence API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rails_router.router,      prefix="/v1/rails",        tags=["Rails"])
app.include_router(corridors_router.router,  prefix="/v1/corridors",    tags=["Corridors"])
app.include_router(heatmap_router.router,    prefix="/v1/heatmap",      tags=["Heatmap"])
app.include_router(fx_router.router,         prefix="/v1/fx",           tags=["FX"])
app.include_router(analysis_router.router,   prefix="/v1/intelligence", tags=["Intelligence"])

@app.get("/")
async def root():
    return {"name": "GFOS Intelligence API", "version": "0.1.0", "status": "live"}

@app.get("/health")
async def health():
    return {"status": "ok"}
