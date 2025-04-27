"""
API server for the GitHub Repo Analyzer using FastAPI.
"""
import os
import logging
import time
import json
import uvicorn
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from agent.handler import handle_user_input

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OSS BOSS API",
    description="API for analyzing GitHub repositories and NPM packages using AI agents",
    version="1.0.0",
)

# Define Pydantic models based on the agent_request.rs structure
class TaskVariable(BaseModel):
    """Model for task variables."""
    value: Union[str, Dict[str, Any], List[Dict[str, Any]]]
    mime_type: Optional[str] = None
    name: Optional[str] = None

class TaskInput(BaseModel):
    """Model for task inputs."""
    variables: Dict[str, TaskVariable] = Field(default_factory=dict)
    
class TaskOutput(BaseModel):
    """Model for task outputs."""
    variables: Dict[str, TaskVariable] = Field(default_factory=dict)
    error: Optional[str] = None

class RunTaskRequest(BaseModel):
    """Request model for run_task endpoint."""
    agent_id: str
    task_id: str
    inputs: TaskInput
    conversation_id: Optional[str] = None
    allow_trace: Optional[bool] = False
    allow_retry: Optional[bool] = False
    trace_id: Optional[str] = None
    task_retry_id: Optional[str] = None
    timeout_ms: Optional[int] = None
    response_format: Optional[str] = None
    max_scan_size: Optional[int] = None

class RunTaskResponse(BaseModel):
    """Response model for run_task endpoint."""
    agent_id: str
    task_id: str
    trace_id: Optional[str] = None
    state: str = "completed"  # Default state is completed
    outputs: TaskOutput
    error: Optional[str] = None
    
class HealthResponse(BaseModel):
    """Response model for health endpoint."""
    status: str
    version: str
    uptime: float

# Track start time for uptime calculation
start_time = time.time()

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        uptime=time.time() - start_time
    )

@app.post("/run-task", response_model=RunTaskResponse)
async def run_task(request: RunTaskRequest = Body(...)):
    """
    Execute a task with the OSS BOSS agent.
    
    This endpoint accepts a standardized task execution request and processes it
    using the appropriate agent.
    """
    try:
        logger.info(f"Received task request for agent: {request.agent_id}, task: {request.task_id}")
        
        # Extract the user query from the input variables
        # Assuming there's a "query" variable in the inputs
        query = None
        repository = None
        
        if "query" in request.inputs.variables:
            query = request.inputs.variables["query"].value
            
        if "repository" in request.inputs.variables:
            repository = request.inputs.variables["repository"].value
            
        if not query:
            raise HTTPException(status_code=400, detail="Missing 'query' variable in inputs")
            
        # Combine query and repository if provided
        full_query = query
        if repository:
            full_query = f"{repository}: {full_query}"
            
        # Process the query using the agent handler
        response = handle_user_input(full_query)
        
        # Convert response to string if it's not already
        if hasattr(response, 'get_content_as_string'):
            response_text = response.get_content_as_string()
        else:
            response_text = str(response)
            
        # Prepare the response
        task_output = TaskOutput(
            variables={
                "response": TaskVariable(
                    value=response_text,
                    mime_type="text/markdown"
                )
            }
        )
        
        return RunTaskResponse(
            agent_id=request.agent_id,
            task_id=request.task_id,
            trace_id=request.trace_id or f"trace_{time.time()}",
            outputs=task_output
        )
        
    except Exception as e:
        logger.error(f"Error processing task request: {e}")
        return RunTaskResponse(
            agent_id=request.agent_id,
            task_id=request.task_id,
            trace_id=request.trace_id,
            state="failed",
            outputs=TaskOutput(),
            error=str(e)
        )

# Keep the original analyze endpoint for backward compatibility
class QueryRequest(BaseModel):
    """Request model for repository analysis queries."""
    query: str
    repository: Optional[str] = None

class QueryResponse(BaseModel):
    """Response model for repository analysis results."""
    response: str

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

@app.post("/webhook")
async def receive_webhook(request: Request):
    """
    Endpoint to receive webhook events from external providers.
    Accepts any content type and logs the request for further processing.
    Security: Logs headers and payload, and provides a placeholder for signature validation.
    """
    try:
        # Log headers for debugging and traceability
        headers = dict(request.headers)
        logger.info(f"Received webhook with headers: {headers}")

        # Read raw body (can be JSON, form, or other)
        body = await request.body()
        logger.info(f"Received webhook payload: {body}")

        # TODO: Add signature validation here for supported providers
        # Example: Validate 'X-Hub-Signature' for GitHub, etc.

        # Respond with a generic 200 OK
        return JSONResponse(content={"status": "received"}, status_code=200)
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=400, detail=f"Webhook processing error: {str(e)}")

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