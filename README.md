# Pearson Math Tutor - Production-Ready RAG-Powered AI Assistant

A production-grade web application that uses Retrieval-Augmented Generation (RAG) with OpenAI's API to answer math questions based on a collection of math textbook PDFs for grades 1-12. The application features a robust FastAPI backend with comprehensive monitoring, error handling, and security features, plus a modern chat frontend.

## 🚀 Production Features

- **100% Accuracy Focus**: Enhanced RAG pipeline with query optimization and similarity filtering
- **Production-Grade Security**: Rate limiting, input validation, and comprehensive error handling
- **Comprehensive Monitoring**: Health checks, metrics, logging, and performance monitoring
- **Scalable Architecture**: Docker containerization with production-ready configuration
- **Robust Error Handling**: Graceful degradation and detailed error reporting
- **Testing Suite**: Comprehensive unit and integration tests
- **Easy Deployment**: One-command deployment with Docker

## 📁 Project Structure

```
Pearson/
├── backend/
│   ├── main.py                 # Enhanced FastAPI application
│   ├── config.py               # Production configuration
│   ├── rag_service.py          # Enhanced RAG service
│   ├── error_handling.py       # Comprehensive error handling
│   ├── logging_config.py       # Structured logging setup
│   ├── rate_limiting.py        # Advanced rate limiting
│   ├── monitoring.py            # Health checks and metrics
│   ├── data_processing.py      # PDF processing and vector DB setup
│   ├── test_main.py            # Comprehensive test suite
│   ├── requirements.txt        # Production dependencies
│   ├── .env                    # Environment variables
│   └── math_books/             # Directory for PDF files
├── frontend/
│   └── index.html              # Enhanced chat interface
├── Dockerfile                  # Production Docker configuration
├── docker-compose.yml          # Multi-service deployment
├── deploy.sh                   # Automated deployment script
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Features

- **RAG-Powered Responses**: Uses OpenAI embeddings and GPT-4 to provide contextual answers
- **PDF Processing**: Automatically extracts and chunks text from math textbook PDFs
- **Vector Database**: Uses ChromaDB for efficient similarity search
- **Modern UI**: Clean, responsive chat interface with Tailwind CSS
- **Real-time Chat**: Interactive chat experience with loading indicators

## 🚀 Quick Start (Production Deployment)

### Prerequisites

1. **Docker & Docker Compose** installed
2. **OpenAI API Key** - Get one from [OpenAI Platform](https://platform.openai.com/api-keys)

### One-Command Deployment

```bash
# Make deployment script executable
chmod +x deploy.sh

# Run complete deployment
./deploy.sh
```

This will:
- ✅ Check all requirements
- ✅ Build production Docker image
- ✅ Run comprehensive tests
- ✅ Process PDF data (if available)
- ✅ Deploy with health monitoring
- ✅ Show deployment status

### Manual Setup (Development)

If you prefer to run locally for development:

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Add PDFs to backend/math_books/

# 3. Process data
python data_processing.py

# 4. Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 5. Open frontend/index.html in browser
```

## 📊 Production Monitoring

### Health Endpoints

- **Liveness**: `GET /health/live` - Simple alive check
- **Readiness**: `GET /health/ready` - Dependency check
- **Comprehensive**: `GET /health` - Full system status
- **Metrics**: `GET /metrics` - Prometheus metrics
- **Status**: `GET /status` - Detailed system information

### Monitoring Features

- **Real-time Metrics**: Request counts, response times, error rates
- **System Monitoring**: CPU, memory, disk usage
- **Dependency Health**: OpenAI API, Vector DB status
- **Structured Logging**: JSON logs with correlation IDs
- **Performance Tracking**: Response time monitoring

## Testing the Application

### 1. Basic Functionality Test

1. Open the frontend in your browser
2. Type a math question like "What is 2 + 2?" or "Explain fractions"
3. Press Send or Enter
4. You should see a response from the AI tutor

### 2. API Testing

You can test the API directly using curl:

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is the Pythagorean theorem?"}'
```

### 3. Troubleshooting

**Common Issues:**

- **CORS Errors**: If you see CORS errors, make sure you're accessing the frontend from one of the allowed origins in `main.py`
- **API Key Issues**: Ensure the `.env` file exists in the `backend/` directory with your `OPENAI_API_KEY`
- **Vector DB Not Found**: Run `data_processing.py` first to create the vector database
- **No PDFs Found**: Make sure PDF files are in the `backend/math_books/` directory
- **Module Not Found**: Make sure you've installed all dependencies with `pip install -r requirements.txt`

## Deployment Guide

### Frontend Deployment

**Option 1: Vercel (Recommended)**
1. Push your code to GitHub
2. Connect your repository to Vercel
3. Update `API_URL` in `index.html` to point to your deployed backend
4. Deploy

**Option 2: Netlify**
1. Drag and drop the `frontend` folder to Netlify
2. Update `API_URL` in `index.html`
3. Deploy

**Option 3: GitHub Pages**
1. Push to GitHub repository
2. Enable GitHub Pages in repository settings
3. Update `API_URL` in `index.html`

### Backend Deployment

**Option 1: Render (Recommended)**
1. Connect your GitHub repository to Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variable: `OPENAI_API_KEY`
5. Deploy

**Option 2: Heroku**
1. Install Heroku CLI
2. Create `Procfile`: `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Deploy: `git push heroku main`

**Option 3: AWS/GCP/Azure**
- Use container services (ECS, Cloud Run, Container Instances)
- Create Dockerfile for containerization
- Set up environment variables

### Vector Database for Production

**Important**: The local ChromaDB (`./chroma_db` folder) won't work in production. Consider these alternatives:

**Option 1: Host ChromaDB Separately**
- Deploy ChromaDB on a separate server
- Update connection settings in `main.py`

**Option 2: Cloud Vector Databases**
- **Pinecone**: Managed vector database service
- **Weaviate**: Open-source vector database
- **Qdrant**: High-performance vector database

**Option 3: Database Migration**
Update `data_processing.py` and `main.py` to use cloud vector databases:

```python
# Example for Pinecone
import pinecone

pinecone.init(api_key="your-pinecone-key")
index = pinecone.Index("math-textbooks")
```

### Environment Variables for Production

Ensure these are set in your deployment environment:
- `OPENAI_API_KEY`: Your OpenAI API key
- `CHROMA_DB_PATH`: Path to vector database (if using local ChromaDB)
- `COLLECTION_NAME`: Name of the vector collection

### Security Considerations

1. **API Keys**: Never hardcode API keys in your code
2. **CORS**: Update allowed origins for production domains
3. **Rate Limiting**: Consider implementing rate limiting for production
4. **Input Validation**: The current implementation has basic validation, consider adding more robust validation for production

## API Endpoints

### GET /
Returns API status
```json
{"message": "Pearson Math Tutor API is running"}
```

### POST /chat
Accepts chat messages and returns AI responses

**Request:**
```json
{
  "message": "What is 2 + 2?"
}
```

**Response:**
```json
{
  "answer": "2 + 2 equals 4. This is a basic addition problem..."
}
```

## Customization

### Modifying the AI Tutor Personality

Edit the `system_prompt` in `main.py` to change how the AI responds:

```python
system_prompt = """You are a friendly math tutor who specializes in..."""
```

### Adjusting Chunk Size

Modify chunk parameters in `data_processing.py`:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,  # Increase for longer context
    chunk_overlap=200,  # Increase for better continuity
)
```

### Changing the UI

The frontend uses Tailwind CSS. Modify `index.html` to customize:
- Colors and styling
- Layout and components
- Additional features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is created for Pearson's math tutoring application.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the logs in the terminal
3. Ensure all dependencies are installed correctly
4. Verify API keys and environment variables
