"""
API server for the GitHub Repo Analyzer using FastAPI.
"""
import os
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Optional
from agent.handler import handle_user_input

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="GitHub Repo Analyzer API",
    description="API for analyzing GitHub repositories using AI agents",
    version="1.0.0",
)

class QueryRequest(BaseModel):
    """Request model for repository analysis queries."""
    query: str
    repository: Optional[str] = None

class QueryResponse(BaseModel):
    """Response model for repository analysis results."""
    response: str

@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "name": "GitHub Repo Analyzer API",
        "version": "1.0.0",
        "description": "API for analyzing GitHub repositories using AI agents",
    }

@app.post("/analyze", response_model=QueryResponse)
async def analyze_repo(request: QueryRequest = Body(...)):
    """
    Analyze a GitHub repository based on the provided query.
    
    If repository is specified, it will be incorporated into the query.
    """
    try:
        # Combine query and repository if provided
        full_query = request.query
        if request.repository:
            full_query = f"{request.repository}: {full_query}"
            
        # Process the query using the agent handler
        response = handle_user_input(full_query)
        
        # Convert response to string if it's not already
        if hasattr(response, 'get_content_as_string'):
            response_text = response.get_content_as_string()
        else:
            response_text = str(response)
            
        return QueryResponse(response=response_text)
        
    except Exception as e:
        logger.error(f"Error processing API request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

def start_api_server():
    """Start the FastAPI server."""
    # Get configuration from environment variables or use defaults
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info(f"Starting API server on {host}:{port}")
    try:
        uvicorn.run(app, host=host, port=port, log_level="info")
    except Exception as e:
        logger.error(f"Error starting API server: {e}", exc_info=True)
        raise