from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.health import router as health_router
from api.routers.metrics import router as metrics_router
from api.routers.graphs import router as graphs_router
from api.routers.deputies import router as deputies_router
from api.routers.rankings import router as rankings_router

app = FastAPI(
    title="Termômetro da Polarização API",
    description="API para métricas e grafos de polarização da Câmara dos Deputados",
    version="1.0.0",
)

# TODO: Allow only frontend here
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(graphs_router)
app.include_router(deputies_router)
app.include_router(rankings_router)
