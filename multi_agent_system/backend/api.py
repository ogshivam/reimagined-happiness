"""
FastAPI Backend for Multi-Agent Conversational Database Assistant
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import logging

from agents.orchestrator import MultiAgentOrchestrator
from config.settings import settings
from database.models import DatabaseManager

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Database Assistant API",
    description="Conversational AI system for database querying with multiple specialized agents",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
orchestrator = MultiAgentOrchestrator()
db_manager = DatabaseManager()

# Pydantic models
class QuestionRequest(BaseModel):
    session_id: str
    question: str
    context: Optional[Dict[str, Any]] = None

class SessionRequest(BaseModel):
    user_id: Optional[str] = None

class ExportRequest(BaseModel):
    session_id: str
    format: str = "csv"
    include_charts: bool = True

# API Routes
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    try:
        # Database manager connects automatically when needed
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    try:
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Multi-Agent Conversational Database Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        tables = db_manager.get_tables()
        
        return {
            "status": "healthy",
            "database_connected": len(tables) > 0,
            "available_tables": len(tables)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.post("/sessions")
async def create_session(request: SessionRequest):
    """Create a new conversation session"""
    try:
        session_id = orchestrator.start_session(request.user_id)
        return {
            "success": True,
            "session_id": session_id,
            "message": "Session created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/stats")
async def get_session_stats(session_id: str):
    """Get session statistics"""
    try:
        stats = orchestrator.get_session_statistics(session_id)
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error getting session stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear session data"""
    try:
        orchestrator.clear_session(session_id)
        return {
            "success": True,
            "message": "Session cleared successfully"
        }
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def process_question(request: QuestionRequest):
    """Process a user question through the multi-agent system"""
    try:
        result = await orchestrator.process_question(
            session_id=request.session_id,
            question=request.question,
            context=request.context
        )
        
        # Convert pandas DataFrame to dict for JSON serialization
        if result.get("data") is not None:
            result["data"] = result["data"].to_dict(orient="records")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/database/schema")
async def get_database_schema():
    """Get database schema information"""
    try:
        schema = db_manager.get_database_summary()
        return {
            "success": True,
            "schema": schema
        }
    except Exception as e:
        logger.error(f"Error getting database schema: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/database/tables")
async def get_database_tables():
    """Get list of database tables"""
    try:
        tables = db_manager.get_tables()
        return {
            "success": True,
            "tables": tables,
            "count": len(tables)
        }
    except Exception as e:
        logger.error(f"Error getting database tables: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/database/tables/{table_name}/sample")
async def get_table_sample(table_name: str, limit: int = 5):
    """Get sample data from a table"""
    try:
        sample_data = db_manager.get_sample_data(table_name, limit)
        return {
            "success": True,
            "table_name": table_name,
            "sample_data": sample_data.to_dict(orient="records"),
            "columns": list(sample_data.columns),
            "row_count": len(sample_data)
        }
    except Exception as e:
        logger.error(f"Error getting table sample: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export/data")
async def export_data(request: ExportRequest):
    """Export conversation data"""
    try:
        # This would need to be implemented based on session history
        # For now, return a placeholder response
        return {
            "success": True,
            "message": "Export functionality will be implemented",
            "format": request.format
        }
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/stats")
async def get_memory_stats():
    """Get memory storage statistics"""
    try:
        stats = orchestrator.memory_agent.get_memory_statistics()
        return {
            "success": True,
            "memory_statistics": stats
        }
    except Exception as e:
        logger.error(f"Error getting memory stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    ) 