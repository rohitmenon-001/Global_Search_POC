# 🤖 RAG Agent Integration Guide

This guide explains how the RAG (Retrieval-Augmented Generation) agent has been integrated with your Global Search POC, providing AI-powered natural language query capabilities alongside the existing semantic search functionality.

## 🎯 Overview

The integration adds an AI Assistant that can:
- Understand natural language queries about your order data
- Retrieve relevant context from your ChromaDB embeddings
- Generate intelligent responses using LLMs (Llama 3 or cloud alternatives)
- Provide insights and analysis of your data

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   Flask API     │    │   RAG Agent     │
│                 │    │                 │    │                 │
│ 🔍 Semantic     │◄──►│ /api/search     │    │ 🤖 AI Assistant │
│ 🤖 AI Assistant │    │ /api/ai/query   │◄──►│ 📚 Context      │
│                 │    │                 │    │ 🧠 LLM          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Oracle DB     │    │   ChromaDB      │
                       │   (Raw Data)    │    │   (Embeddings)  │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Start the Flask API Server
```bash
cd api
python app.py
```

### 2. Start the Streamlit Frontend
```bash
streamlit run streamlit_app.py
```

### 3. Access the Application
- **Semantic Search**: http://localhost:8501 (Tab 1)
- **AI Assistant**: http://localhost:8501 (Tab 2)

## 🔧 Features

### 🔍 Semantic Search Tab
- Original semantic search functionality
- Visual analytics and insights
- Order details and metrics
- Score distribution charts

### 🤖 AI Assistant Tab
- Natural language query interface
- AI-powered responses with context
- Chat history
- Example queries for quick testing
- Model information display

## 📡 API Endpoints

### AI Query Endpoint
```http
POST /api/tenant/{tenant_id}/ai/query
Content-Type: application/json
X-Tenant-ID: {tenant_id}

{
  "query": "What are the highest value orders?"
}
```

**Response:**
```json
{
  "status": "success",
  "response": "Based on the retrieved data, the highest value orders are...",
  "context": "Retrieved context from ChromaDB...",
  "model_used": "llama3:8b"
}
```

### AI Status Endpoint
```http
GET /api/tenant/{tenant_id}/ai/status
X-Tenant-ID: {tenant_id}
```

**Response:**
```json
{
  "rag_available": true,
  "tenant_id": "tenant_ABC",
  "status": "ready"
}
```

## 🧪 Testing

### Test RAG Integration
```bash
python test_rag_integration.py
```

### Test API Integration
```bash
python test_api_integration.py
```

## 💡 Example Queries

Try these natural language questions in the AI Assistant:

1. **"What are the highest value orders in the system?"**
2. **"Show me all orders for customer 26"**
3. **"Find orders with delivery issues"**
4. **"Which orders are currently active?"**
5. **"What's the average order value?"**
6. **"Find orders from June 2021"**

## 🔧 Configuration

### LLM Models
The system supports multiple LLM options:

1. **Local Llama 3** (requires Ollama)
   - `llama3:8b` (default)
   - `llama2:7b` (fallback)
   - Requires 2.5-3GB RAM

2. **Cloud LLM** (fallback)
   - Used when local models are unavailable
   - Placeholder responses for demo purposes

### Memory Optimization
If you encounter memory issues:

1. **Use smaller models:**
   ```python
   # In rag_agent_simple.py
   models_to_try = ["llama2:7b", "llama3:8b"]
   ```

2. **Increase system memory** (recommended: 4GB+)

3. **Use cloud-based LLMs** for production

## 🛠️ Troubleshooting

### Common Issues

1. **"RAG Agent not available"**
   ```bash
   pip install pyautogen chromadb sentence-transformers ollama fix-busted-json
   ```

2. **"Model not found"**
   ```bash
   # Install Ollama and pull models
   ollama pull llama3:8b
   ollama pull llama2:7b
   ```

3. **Memory errors**
   - Use smaller models
   - Increase system RAM
   - Use cloud LLMs

4. **API connection errors**
   - Ensure Flask API is running: `python api/app.py`
   - Check port 5000 is available

### Debug Mode
Enable debug logging in `rag_agent_simple.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Performance

### Response Times
- **Context Retrieval**: ~100-500ms
- **LLM Generation**: ~2-10 seconds (local) / ~1-3 seconds (cloud)
- **Total Response**: ~3-15 seconds

### Accuracy
- **Semantic Retrieval**: High accuracy with embeddings
- **LLM Responses**: Depends on model quality and context
- **Fallback Handling**: Graceful degradation to cloud LLM

## 🔒 Security

- **Tenant Isolation**: Each tenant has separate ChromaDB collections
- **Authentication**: Tenant ID validation via middleware
- **Input Validation**: Query sanitization and validation
- **Error Handling**: Secure error messages without data leakage

## 🚀 Production Deployment

### Recommended Setup
1. **Cloud LLM Integration**: Replace placeholder with OpenAI/Anthropic
2. **Load Balancing**: Multiple API instances
3. **Caching**: Redis for frequent queries
4. **Monitoring**: Logging and metrics
5. **Security**: API keys and rate limiting

### Environment Variables
```bash
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export REDIS_URL="redis://localhost:6379"
```

## 📈 Future Enhancements

1. **Multi-modal Support**: Image and document analysis
2. **Conversation Memory**: Persistent chat history
3. **Custom Training**: Fine-tuned models for your domain
4. **Analytics Dashboard**: Query analytics and insights
5. **Batch Processing**: Bulk query processing
6. **Real-time Updates**: Live data synchronization

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the test scripts
3. Check system requirements
4. Verify all dependencies are installed

---

**🎉 Congratulations!** Your Global Search POC now has AI-powered natural language query capabilities alongside semantic search. Users can ask questions in plain English and get intelligent, contextual responses about their order data. 