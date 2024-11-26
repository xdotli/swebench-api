from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
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

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint for container orchestration"""
    try:
        # Add any critical service checks here
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "healthy"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        ) 