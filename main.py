from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from api.auth.routes import router as auth_router
from api.ingest.routes import router as ingest_router
from api.memory.routes import router as memory_router
from api.memory.conversation_routes import router as conversation_router
from api.persona.routes import router as persona_router
from api.export.routes import router as export_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TESTIGO API",
    description="Memoria longitudinal personal con IA",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
async def root():
    return {"message": "TESTIGO API v1.0.0 - Memoria que dura"}

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(ingest_router, prefix="/api/events", tags=["events"])
app.include_router(memory_router, prefix="/api/memory", tags=["memory"])
app.include_router(conversation_router, prefix="/api/conversation", tags=["conversation"])
app.include_router(persona_router, prefix="/api/persona", tags=["persona"])
app.include_router(export_router, prefix="/api/export", tags=["export"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
