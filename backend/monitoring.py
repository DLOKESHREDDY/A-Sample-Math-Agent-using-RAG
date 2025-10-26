from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from typing import Dict, Any
import time
import psutil
import os
from config import settings
from logging_config import get_logger

logger = get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
RAG_QUERY_COUNT = Counter('rag_queries_total', 'Total RAG queries', ['status'])
RAG_RESPONSE_TIME = Histogram('rag_response_time_seconds', 'RAG response time')
OPENAI_API_CALLS = Counter('openai_api_calls_total', 'Total OpenAI API calls', ['model', 'status'])
VECTOR_DB_QUERIES = Counter('vector_db_queries_total', 'Total vector DB queries', ['status'])
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active connections')
SYSTEM_MEMORY_USAGE = Gauge('system_memory_usage_percent', 'System memory usage percentage')
SYSTEM_CPU_USAGE = Gauge('system_cpu_usage_percent', 'System CPU usage percentage')

router = APIRouter()

class HealthChecker:
    """Health check service for monitoring application status."""
    
    def __init__(self):
        self.start_time = time.time()
        self.last_check = time.time()
    
    def check_openai_connection(self) -> Dict[str, Any]:
        """Check OpenAI API connectivity."""
        try:
            import openai
            # Simple API call to test connectivity
            response = openai.models.list()
            return {
                "status": "healthy",
                "response_time": 0.1,  # Placeholder
                "models_available": len(response.data) if response.data else 0
            }
        except Exception as e:
            logger.error("OpenAI health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def check_vector_db(self) -> Dict[str, Any]:
        """Check vector database connectivity."""
        try:
            import chromadb
            client = chromadb.PersistentClient(path=settings.chroma_db_path)
            collection = client.get_collection(name=settings.collection_name)
            
            # Test a simple query
            test_result = collection.query(
                query_embeddings=[[0.1] * 1536],  # Dummy embedding
                n_results=1
            )
            
            return {
                "status": "healthy",
                "collection_name": settings.collection_name,
                "test_query_successful": True
            }
        except Exception as e:
            logger.error("Vector DB health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            return {
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent_used": memory.percent
                },
                "cpu": {
                    "percent_used": cpu_percent
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "percent_used": (disk.used / disk.total) * 100
                }
            }
        except Exception as e:
            logger.error("System resource check failed", error=str(e))
            return {
                "error": str(e)
            }
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds."""
        return time.time() - self.start_time

health_checker = HealthChecker()

@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime_seconds": health_checker.get_uptime(),
        "version": "1.0.0",
        "environment": "production" if not settings.debug else "development"
    }
    
    # Check OpenAI
    openai_status = health_checker.check_openai_connection()
    health_status["openai"] = openai_status
    
    # Check Vector DB
    vector_db_status = health_checker.check_vector_db()
    health_status["vector_db"] = vector_db_status
    
    # Check system resources
    system_status = health_checker.check_system_resources()
    health_status["system"] = system_status
    
    # Determine overall health
    if (openai_status.get("status") != "healthy" or 
        vector_db_status.get("status") != "healthy"):
        health_status["status"] = "unhealthy"
        return JSONResponse(
            status_code=503,
            content=health_status
        )
    
    return health_status

@router.get("/health/live")
async def liveness_check():
    """Simple liveness check for Kubernetes."""
    return {"status": "alive", "timestamp": time.time()}

@router.get("/health/ready")
async def readiness_check():
    """Readiness check for Kubernetes."""
    # Check critical dependencies
    openai_status = health_checker.check_openai_connection()
    vector_db_status = health_checker.check_vector_db()
    
    if (openai_status.get("status") == "healthy" and 
        vector_db_status.get("status") == "healthy"):
        return {"status": "ready", "timestamp": time.time()}
    else:
        raise HTTPException(
            status_code=503,
            detail="Service not ready - dependencies unavailable"
        )

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    # Update system metrics
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent()
    
    SYSTEM_MEMORY_USAGE.set(memory.percent)
    SYSTEM_CPU_USAGE.set(cpu_percent)
    
    return Response(
        generate_latest(),
        media_type="text/plain"
    )

@router.get("/status")
async def status():
    """Detailed status information."""
    return {
        "application": {
            "name": settings.app_name,
            "version": "1.0.0",
            "uptime": health_checker.get_uptime(),
            "debug_mode": settings.debug
        },
        "configuration": {
            "openai_model": settings.openai_model,
            "embedding_model": settings.embedding_model,
            "max_context_chunks": settings.max_context_chunks,
            "similarity_threshold": settings.similarity_threshold
        },
        "dependencies": {
            "openai": health_checker.check_openai_connection(),
            "vector_db": health_checker.check_vector_db()
        },
        "system": health_checker.check_system_resources()
    }

# Middleware for updating metrics
async def update_metrics_middleware(request, call_next):
    """Middleware to update Prometheus metrics."""
    start_time = time.time()
    
    response = await call_next(request)
    
    # Update metrics
    duration = time.time() - start_time
    REQUEST_DURATION.observe(duration)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response
