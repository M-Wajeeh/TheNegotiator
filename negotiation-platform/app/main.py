from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.negotiations import router as negotiations_router
from app.api.routes.voice import router as voice_router
from app.api.routes.documents import router as documents_router
from app.api.routes.calls import router as calls_router
from app.api.routes.quotes import router as quotes_router
from app.api.routes.reports import router as reports_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.files import router as files_router

app = FastAPI(title="Negotiation Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(negotiations_router, prefix="/negotiations", tags=["negotiations"])
app.include_router(voice_router, prefix="/voice", tags=["voice"])
app.include_router(documents_router, prefix="/documents", tags=["documents"])
app.include_router(calls_router, prefix="/calls", tags=["calls"])
app.include_router(quotes_router, prefix="/quotes", tags=["quotes"])
app.include_router(reports_router, prefix="/reports", tags=["reports"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(files_router, prefix="/api/files", tags=["files"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
