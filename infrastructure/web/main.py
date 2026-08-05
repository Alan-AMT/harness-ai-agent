from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.web.routers import chat

app = FastAPI(
    title="FastAPI Hexagonal Architecture Blueprint",
    description=(
        "A premium boilerplate illustrating clean Hexagonal Architecture (Ports & Adapters) "
        "principles in Python. Easily swap databases, models, or UI presentation layers."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set up CORS middleware (standard for web apps)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

# Include Routers
app.include_router(chat.router)

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "healthy",
        "architecture": "Hexagonal Architecture (Ports and Adapters)",
        "docs": "/docs"
    }
