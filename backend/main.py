"""GeneReg Explorer - Educational Genomic Variant Sandbox

A web application for exploring AlphaGenome predictions in an educational context.
This tool is for educational and research purposes only - not for medical diagnosis.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from routers import variants, examples, regions


# API metadata
API_TITLE = "GeneReg Explorer API"
API_DESCRIPTION = """
**Educational Genomic Variant Analysis Tool**

GeneReg Explorer provides an interactive sandbox for learning about how DNA 
variants affect gene regulation. Using Google DeepMind's AlphaGenome model, 
users can explore predicted effects of mutations on:

- Gene expression (RNA-seq)
- Chromatin accessibility (ATAC-seq)
- Splicing patterns
- Transcription factor binding

**Important Disclaimers:**
- This tool is for educational and research purposes only
- Not intended for medical diagnosis or treatment decisions
- AlphaGenome API is used under non-commercial terms
- Results should not be used for clinical interpretation

**Citation:**
If you use this tool or AlphaGenome in your research, please cite:
Avsec et al. (2026) Advancing regulatory variant effect prediction with AlphaGenome. Nature.
"""

API_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("Starting GeneReg Explorer...")

    api_key = os.getenv("ALPHAGENOME_API_KEY")
    if not api_key:
        print("Warning: ALPHAGENOME_API_KEY not set. API calls will fail.")
        print("Get your key at: https://deepmind.google.com/science/alphagenome")
    else:
        print("AlphaGenome API key detected")

    yield

    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=API_TITLE, description=API_DESCRIPTION, version=API_VERSION, lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],  # Vite and common React ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(variants.router)
app.include_router(examples.router)
app.include_router(regions.router)


@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "name": "GeneReg Explorer API",
        "version": API_VERSION,
        "description": "Educational tool for exploring AlphaGenome predictions",
        "disclaimer": "For educational use only - not for medical diagnosis",
        "endpoints": {
            "docs": "/docs",
            "examples": "/examples",
            "tissues": "/regions/tissues",
            "genes": "/regions/genes",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "genereg-explorer-api"}


@app.get("/stats")
async def get_stats():
    """Get API usage statistics."""
    try:
        from utils.alphagenome_client import get_client

        client = get_client()
        cache_stats = client.get_cache_stats()

        return {
            "cache": cache_stats,
            "service": "genereg-explorer-api",
            "api_type": "AlphaGenome (non-commercial use)",
        }
    except Exception as e:
        return {
            "cache": {"error": str(e)},
            "service": "genereg-explorer-api",
            "api_type": "AlphaGenome (non-commercial use)",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
