from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.query_router import router

app = FastAPI(
    title="RAG Query API",
    description="Offline RAG system for document query and retrieval"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
