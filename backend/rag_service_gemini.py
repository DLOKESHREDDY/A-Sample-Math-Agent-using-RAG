import os
import time
import re
import hashlib
from typing import List, Dict, Tuple, Optional
from config import settings
from logging_config import RAGLogger, get_logger
from error_handling import (
    RAGError, VectorDBError, OpenAIError, ValidationError,
    validate_input, sanitize_response
)
import pinecone
from pinecone import Pinecone
import google.generativeai as genai

class GeminiRAGService:
    """RAG service using Google Gemini API with Pinecone."""
    
    def __init__(self):
        self.logger = RAGLogger(get_logger(__name__))
        self.index = None
        self.model = None
        self._initialize_pinecone()
        self._initialize_gemini()
    
    def _initialize_pinecone(self) -> None:
        """Initialize connection to Pinecone vector database."""
        try:
            # Initialize Pinecone v3 client
            pc = Pinecone(api_key=settings.pinecone_api_key)
            
            # Connect to index
            self.index = pc.Index(settings.pinecone_index_name)
            
            # Test connection
            stats = self.index.describe_index_stats()
            self.logger.logger.info(
                "Pinecone initialized successfully",
                index_name=settings.pinecone_index_name,
                total_vectors=stats.total_vector_count,
                dimension=stats.dimension
            )
        except Exception as e:
            self.logger.log_error(e, {"operation": "pinecone_init"})
            raise VectorDBError(f"Failed to initialize Pinecone: {str(e)}")
    
    def _initialize_gemini(self) -> None:
        """Initialize Google Gemini API."""
        try:
            # Configure Gemini API
            genai.configure(api_key=settings.gemini_api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel(settings.gemini_model)
            
            self.logger.logger.info("Gemini API initialized successfully")
        except Exception as e:
            self.logger.log_error(e, {"operation": "gemini_init"})
            raise RAGError(f"Failed to initialize Gemini API: {str(e)}")
    
    def _get_free_embedding(self, text: str) -> list:
        """Get embedding using hash-based approach."""
        try:
            # Create a simple embedding based on text hash
            text_hash = hashlib.md5(text.encode()).hexdigest()
            
            # Convert hash to 384-dimensional vector
            embedding = []
            for i in range(0, len(text_hash), 2):
                val = int(text_hash[i:i+2], 16) / 255.0  # Normalize to 0-1
                embedding.append(val)
            
            # Pad or truncate to 384 dimensions
            while len(embedding) < 384:
                embedding.append(0.0)
            embedding = embedding[:384]
            
            return embedding
            
        except Exception as e:
            print(f"Error creating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 384
    
    def _enhance_query(self, query: str) -> str:
        """Enhance the user query for better retrieval."""
        # Add context keywords for math problems
        math_keywords = {
            "solve": "solution steps method",
            "calculate": "calculation formula",
            "explain": "explanation concept definition",
            "what is": "definition meaning concept",
            "how to": "steps method procedure",
            "find": "solution answer result"
        }
        
        query_lower = query.lower()
        enhanced_query = query
        
        for keyword, additions in math_keywords.items():
            if keyword in query_lower:
                enhanced_query += f" {additions}"
                break
        
        return enhanced_query
    
    def _get_relevant_context(self, query: str, n_results: int = None) -> Tuple[List[str], List[float]]:
        """Get relevant context chunks with similarity scores from Pinecone."""
        if not self.index:
            raise VectorDBError("Pinecone index not initialized")
        
        n_results = n_results or settings.max_context_chunks
        
        try:
            # Enhance query for better retrieval
            enhanced_query = self._enhance_query(query)
            
            # Create embedding using free method
            self.logger.log_embedding_creation(len(enhanced_query))
            query_vector = self._get_free_embedding(enhanced_query)
            
            # Search Pinecone index
            search_results = self.index.query(
                vector=query_vector,
                top_k=n_results,
                include_metadata=True
            )
            
            # Extract results (client v3 API format)
            documents = []
            similarity_scores = []
            
            if search_results and 'matches' in search_results:
                for match in search_results['matches']:
                    if 'metadata' in match and match['metadata'] and 'text' in match['metadata']:
                        documents.append(match['metadata']['text'])
                        similarity_scores.append(match.get('score', 0.0))
            elif hasattr(search_results, 'matches'):
                # Handle object-based results
                for match in search_results.matches:
                    if hasattr(match, 'metadata') and match.metadata and 'text' in match.metadata:
                        documents.append(match.metadata['text'])
                        similarity_scores.append(getattr(match, 'score', 0.0))
            
            # Filter by similarity threshold
            filtered_docs = []
            filtered_scores = []
            
            for doc, score in zip(documents, similarity_scores):
                if score >= settings.similarity_threshold:
                    filtered_docs.append(doc)
                    filtered_scores.append(score)
            
            self.logger.log_vector_search(len(filtered_docs), filtered_scores)
            
            return filtered_docs, filtered_scores
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "vector_search"})
            raise VectorDBError(f"Pinecone search failed: {str(e)}")
    
    def _construct_enhanced_prompt(self, query: str, context_chunks: List[str]) -> str:
        """Construct enhanced prompt for Gemini."""
        
        # Combine context with deduplication
        unique_context = []
        seen_content = set()
        
        for chunk in context_chunks:
            # Simple deduplication based on first 50 characters
            chunk_key = chunk[:50]
            if chunk_key not in seen_content:
                unique_context.append(chunk)
                seen_content.add(chunk_key)
        
        context = "\n\n".join(unique_context)
        
        # Enhanced prompt for Gemini - CLEAN FORMATTING
        prompt = f"""You are a math tutor. Answer clearly and concisely with clean formatting.

TEXTBOOK CONTENT (from Mathematics.pdf):
{context}

STUDENT QUESTION: {query}

IMPORTANT FORMATTING RULES:
- DO NOT use markdown syntax like ** or * for bold/italic
- ABSOLUTELY NO numbered lists like "1. 2. 3." or "Step 1, Step 2"
- ABSOLUTELY NO bullet points with "-" or "•"
- Write in natural, flowing conversation style with full sentences
- Connect thoughts with phrases like "Let me explain", "Here's how it works", "Now"
- Use plain text with clear spacing
- Create clean ASCII diagrams for formulas and geometry
- Use clear mathematical notation
- Be encouraging and friendly

FORMAT FOR MATH CONCEPTS:

For formulas, show them simply like:

The formula is: a² + b² = c²

For triangles or geometry, use clean ASCII art:

     /\
    /  \
   /    \   c
  /______\ 
    a      b

RESPONSE STRUCTURE (NATURAL CONVERSATION):
Start with a brief, direct answer. Then explain the concept naturally using textbook content when available. Include visual representation using ASCII art for geometric concepts. Provide a simple step-by-step example. End with brief encouragement.

Write as if you're talking to a student face-to-face. Use full sentences in natural paragraphs. Absolutely no numbered lists, no bullets, no markdown formatting."""

        return prompt
    
    def _call_gemini_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Call Gemini API with retry logic for reliability."""
        
        for attempt in range(max_retries):
            try:
                self.logger.log_llm_call(settings.gemini_model)
                
                # Generate content using Gemini - CONCISE MODE WITH DIAGRAMS
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=settings.gemini_temperature,
                        max_output_tokens=settings.gemini_max_tokens,
                        top_p=0.9,
                    )
                )
                
                return response.text
                
            except Exception as e:
                self.logger.log_error(e, {"attempt": attempt + 1, "max_retries": max_retries})
                
                if attempt == max_retries - 1:
                    raise RAGError(f"Gemini API call failed after {max_retries} attempts: {str(e)}")
                
                # Exponential backoff
                time.sleep(2 ** attempt)
    
    def generate_response(self, query: str) -> str:
        """Generate RAG response using Gemini API and Pinecone."""
        start_time = time.time()
        
        try:
            # Validate input
            validate_input(query)
            
            # Log query
            self.logger.log_query(query)
            
            # Get relevant context from Pinecone
            context_chunks, similarity_scores = self._get_relevant_context(query)
            
            if not context_chunks:
                return "I couldn't find relevant information in the Mathematics textbook to answer your question accurately. Please try rephrasing your question or ask about a different math topic."
            
            # Construct enhanced prompt
            prompt = self._construct_enhanced_prompt(query, context_chunks)
            
            # Call Gemini API with retry logic
            response = self._call_gemini_with_retry(prompt)
            
            # Sanitize response
            sanitized_response = sanitize_response(response)
            
            # Log successful response
            processing_time = time.time() - start_time
            self.logger.log_response(len(sanitized_response), processing_time)
            
            return sanitized_response
            
        except Exception as e:
            self.logger.log_error(e, {"query": query[:100]})
            
            if isinstance(e, (ValidationError, VectorDBError, RAGError)):
                raise
            else:
                raise RAGError(f"Unexpected error in RAG pipeline: {str(e)}")

# Global RAG service instance
rag_service = GeminiRAGService()
