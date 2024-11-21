from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import benchmark

app = FastAPI(
    title="SWE-bench API",
    description="API for serving and evaluating SWE-bench tasks",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(benchmark.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to SWE-bench API"} 