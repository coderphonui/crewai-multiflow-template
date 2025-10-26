"""
Main FastAPI application setup.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .poem_flow import router as poem_flow_router


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="CrewAI Multi-Flow API",
        description="REST API for executing and monitoring CrewAI flows",
        version="0.1.0",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register flow routers
    app.include_router(poem_flow_router, prefix="/api/v1/poem-flow", tags=["poem-flow"])
    
    @app.get("/")
    def root():
        """Root endpoint with API information."""
        return {
            "message": "CrewAI Multi-Flow API",
            "version": "0.1.0",
            "endpoints": {
                "poem_flow": "/api/v1/poem-flow"
            }
        }
    
    @app.get("/health")
    def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    return app


# Create the FastAPI app instance
app = create_app()
