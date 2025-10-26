from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
import time
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import our production modules
from config import settings
from logging_config import setup_logging, get_logger, RequestLogger
from error_handling import (
    global_exception_handler, create_error_response,
    ValidationError, RAGError, OpenAIError, VectorDBError
)
from rate_limiting import check_rate_limit, get_rate_limit_info
from rag_service_gemini import rag_service
from monitoring import router as monitoring_router, update_metrics_middleware

# Setup logging
setup_logging(settings.log_level)
logger = get_logger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered math tutoring system using RAG",
    version="1.0.0",
    debug=settings.debug
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add monitoring middleware
app.middleware("http")(update_metrics_middleware)

# Add exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include monitoring routes
app.include_router(monitoring_router)

# Pydantic models with validation
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="Math question or query")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI tutor response")
    success: bool = Field(default=True, description="Request success status")
    processing_time: float = Field(..., description="Response processing time in seconds")
    rate_limit_info: dict = Field(default=None, description="Rate limit information")

class ErrorResponse(BaseModel):
    error: dict = Field(..., description="Error details")
    success: bool = Field(default=False, description="Request success status")

# Root endpoint
@app.get("/")
async def root():
    """API status endpoint."""
    return {
        "message": f"{settings.app_name} API is running",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": time.time()
    }

# Chat endpoint with enhanced production features
@app.post("/chat", response_model=ChatResponse)
@limiter.limit(f"{settings.max_requests_per_minute}/minute")
async def chat(request: Request, chat_request: ChatRequest):
    """Enhanced chat endpoint with production-grade features."""
    start_time = time.time()
    
    try:
        # Check rate limiting
        if not check_rate_limit(request, settings.max_requests_per_minute):
            rate_limit_info = get_rate_limit_info(request)
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "type": "RateLimitExceeded",
                        "message": "Too many requests. Please slow down.",
                        "retry_after": rate_limit_info["reset_time"] - time.time()
                    },
                    "success": False
                }
            )
        
        # Log request
        logger.info(
            "Chat request received",
            message=chat_request.message[:100],
            client_ip=get_remote_address(request),
            user_agent=request.headers.get("user-agent")
        )
        
        # Generate RAG response
        answer = rag_service.generate_response(chat_request.message)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Get rate limit info
        rate_limit_info = get_rate_limit_info(request)
        
        # Log successful response
        logger.info(
            "Chat response generated",
            processing_time=processing_time,
            response_length=len(answer)
        )
        
        return ChatResponse(
            answer=answer,
            success=True,
            processing_time=processing_time,
            rate_limit_info=rate_limit_info
        )
        
    except ValidationError as e:
        logger.warning("Validation error", error=str(e), message=chat_request.message)
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "type": "ValidationError",
                    "message": str(e)
                },
                "success": False
            }
        )
        
    except (OpenAIError, VectorDBError) as e:
        logger.error("Service error", error=str(e), message=chat_request.message)
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "type": type(e).__name__,
                    "message": "Service temporarily unavailable. Please try again later."
                },
                "success": False
            }
        )
        
    except RAGError as e:
        logger.error("RAG error", error=str(e), message=chat_request.message)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "RAGError",
                    "message": "Unable to process your request. Please try again."
                },
                "success": False
            }
        )
        
    except Exception as e:
        logger.error("Unexpected error", error=str(e), message=chat_request.message)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "InternalServerError",
                    "message": "An unexpected error occurred. Please try again later."
                },
                "success": False
            }
        )

# API documentation endpoint
@app.get("/docs")
async def api_docs():
    """API documentation."""
    return {
        "title": settings.app_name,
        "version": "1.0.0",
        "description": "AI-powered math tutoring system using RAG",
        "endpoints": {
            "POST /chat": "Send a math question and get AI tutor response",
            "GET /health": "Comprehensive health check",
            "GET /metrics": "Prometheus metrics",
            "GET /status": "Detailed system status"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
