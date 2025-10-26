from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Union
import traceback
from logging_config import get_logger

logger = get_logger(__name__)

class RAGError(Exception):
    """Base exception for RAG-related errors."""
    pass

class VectorDBError(RAGError):
    """Exception for vector database errors."""
    pass

class OpenAIError(RAGError):
    """Exception for OpenAI API errors."""
    pass

class ValidationError(RAGError):
    """Exception for input validation errors."""
    pass

class RateLimitError(RAGError):
    """Exception for rate limiting errors."""
    pass

def create_error_response(
    error_type: str,
    message: str,
    details: dict = None,
    status_code: int = 500
) -> JSONResponse:
    """Create a standardized error response."""
    
    error_response = {
        "error": {
            "type": error_type,
            "message": message,
            "details": details or {}
        },
        "success": False
    }
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled exceptions."""
    
    logger.error(
        "Unhandled exception",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        url=str(request.url),
        method=request.method,
        traceback=traceback.format_exc()
    )
    
    return create_error_response(
        error_type="InternalServerError",
        message="An unexpected error occurred. Please try again later.",
        status_code=500
    )

def handle_openai_error(exc: Exception) -> JSONResponse:
    """Handle OpenAI API specific errors."""
    
    error_message = str(exc)
    
    if "rate_limit" in error_message.lower():
        return create_error_response(
            error_type="RateLimitError",
            message="API rate limit exceeded. Please try again in a moment.",
            status_code=429
        )
    elif "invalid_api_key" in error_message.lower():
        return create_error_response(
            error_type="AuthenticationError",
            message="Invalid API key. Please check your configuration.",
            status_code=401
        )
    elif "insufficient_quota" in error_message.lower():
        return create_error_response(
            error_type="QuotaExceededError",
            message="API quota exceeded. Please check your OpenAI account.",
            status_code=402
        )
    else:
        return create_error_response(
            error_type="OpenAIError",
            message="OpenAI API error occurred. Please try again.",
            status_code=502
        )

def handle_vector_db_error(exc: Exception) -> JSONResponse:
    """Handle vector database specific errors."""
    
    return create_error_response(
        error_type="VectorDBError",
        message="Vector database error. Please ensure the database is properly initialized.",
        status_code=503
    )

def validate_input(message: str) -> None:
    """Validate user input for security and quality."""
    
    if not message or not message.strip():
        raise ValidationError("Message cannot be empty")
    
    if len(message) > 2000:
        raise ValidationError("Message is too long. Please keep it under 2000 characters.")
    
    # Check for potentially harmful content
    dangerous_patterns = [
        "<script", "javascript:", "data:", "vbscript:",
        "onload=", "onerror=", "onclick="
    ]
    
    message_lower = message.lower()
    for pattern in dangerous_patterns:
        if pattern in message_lower:
            raise ValidationError("Message contains potentially harmful content")
    
    # Check for excessive repetition (potential spam)
    words = message.split()
    if len(words) > 10:
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        max_repetition = max(word_counts.values())
        if max_repetition > len(words) * 0.5:
            raise ValidationError("Message appears to contain excessive repetition")

def sanitize_response(response: str) -> str:
    """Sanitize AI response for security."""
    
    # Remove potential HTML/JavaScript
    import re
    
    # Remove script tags
    response = re.sub(r'<script.*?</script>', '', response, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove javascript: URLs
    response = re.sub(r'javascript:', '', response, flags=re.IGNORECASE)
    
    # Remove data: URLs
    response = re.sub(r'data:', '', response, flags=re.IGNORECASE)
    
    # Limit response length
    if len(response) > 5000:
        response = response[:5000] + "..."
    
    return response.strip()

