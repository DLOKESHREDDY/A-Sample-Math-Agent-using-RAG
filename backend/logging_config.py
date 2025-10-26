import structlog
import logging
import sys
from typing import Any, Dict
import time

def setup_logging(log_level: str = "INFO") -> None:
    """Setup structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)

class RequestLogger:
    """Middleware for logging HTTP requests."""
    
    def __init__(self, logger: structlog.BoundLogger):
        self.logger = logger
    
    async def __call__(self, request, call_next):
        start_time = time.time()
        
        # Log request
        self.logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        self.logger.info(
            "Request completed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=round(process_time, 4),
        )
        
        return response

class RAGLogger:
    """Logger for RAG operations."""
    
    def __init__(self, logger: structlog.BoundLogger):
        self.logger = logger
    
    def log_query(self, query: str, user_id: str = None) -> None:
        """Log incoming query."""
        self.logger.info(
            "RAG query received",
            query=query[:100] + "..." if len(query) > 100 else query,
            user_id=user_id,
        )
    
    def log_embedding_creation(self, query_length: int) -> None:
        """Log embedding creation."""
        self.logger.info(
            "Creating query embedding",
            query_length=query_length,
        )
    
    def log_vector_search(self, results_count: int, similarity_scores: list) -> None:
        """Log vector search results."""
        self.logger.info(
            "Vector search completed",
            results_count=results_count,
            avg_similarity=sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0,
            max_similarity=max(similarity_scores) if similarity_scores else 0,
        )
    
    def log_llm_call(self, model: str, tokens_used: int = None) -> None:
        """Log LLM API call."""
        self.logger.info(
            "LLM API call",
            model=model,
            tokens_used=tokens_used,
        )
    
    def log_response(self, response_length: int, processing_time: float) -> None:
        """Log final response."""
        self.logger.info(
            "RAG response generated",
            response_length=response_length,
            processing_time=round(processing_time, 4),
        )
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """Log RAG errors."""
        self.logger.error(
            "RAG error occurred",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context or {},
            exc_info=True,
        )

