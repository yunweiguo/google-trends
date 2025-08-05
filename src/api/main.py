    """
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import config


def create_api_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="Google Trends Website Builder API",
        description="API for Google Trends data analysis and website generation",
        version="0.1.0",
        debug=config.api.debug
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {"message": "Google Trends Website Builder API", "version": "0.1.0"}
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "trends-api"}
    
    return app


app = create_api_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.api.debug
    )