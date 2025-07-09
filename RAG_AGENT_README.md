# RAG Agent POC - Llama 3 + AutoGen + ChromaDB

This is a Proof-of-Concept (POC) for a Retrieval-Augmented Generation (RAG) agent that combines:
- **Llama 3** (via Ollama) for language generation
- **ChromaDB** for semantic retrieval
- **Oracle DB** as the knowledge source
- **AutoGen** (optional) for agent orchestration

## 🏗️ Architecture

```
[User Query] → [RAG Agent] → [Semantic Retrieval (ChromaDB)] → [Oracle DB]
                                    ↓
                              [Llama 3 (Ollama)] → [Generated Response]
```

## 🚀 Features

- **Semantic Search**: Uses sentence-transformers to find relevant order data
- **Multi-tenant Support**: Separate ChromaDB collections per tenant
- **Natural Language Queries**: Ask questions in plain English
- **Context-Aware Responses**: LLM generates answers based on retrieved data
- **API Endpoint**: RESTful API for integration

## 📋 Prerequisites

1. **Python 3.8+**
2. **Ollama** installed and running
3. **Oracle DB** with order data
4. **ChromaDB** for vector storage

## 🛠️ Installation

### 1. Install Dependencies
```bash
pip install pyautogen chromadb sentence-transformers ollama fix-busted-json fastapi uvicorn
```

### 2. Set up Ollama
```bash
# Install Ollama (if not already installed)
# Download from: https://ollama.com/download

# Pull Llama 3 model
ollama pull llama3

# For lower memory usage, use a smaller model
ollama pull llama2:7b
```

### 3. Prepare Data
```bash
# Run the backfill script to populate ChromaDB
python backfill_orders.py
```

## 🎯 Usage

### Simple RAG Agent
```python
from rag_agent_simple import SimpleRAGAgent

# Initialize agent
agent = SimpleRAGAgent(tenant_id="tenant_ABC")

# Query the agent
result = agent.generate_response("Show me all orders for customer 12345")
print(result['response'])
```

### API Endpoint
```bash
# Start the API server
python rag_api.py

# Query via API
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Show me high-value orders", "tenant_id": "tenant_ABC"}'
```

### Test Scripts
```bash
# Test the simple RAG agent
python rag_agent_simple.py

# Test the AutoGen version (if you have enough memory)
python rag_agent.py
```

## 📁 File Structure

```
├── rag_agent_simple.py      # Simple RAG agent using Ollama directly
├── rag_agent.py            # RAG agent using AutoGen (experimental)
├── rag_api.py              # FastAPI endpoint
├── backfill_orders.py      # Script to populate ChromaDB
├── RAG_AGENT_README.md     # This file
└── requirements.txt        # Python dependencies
```

## 🔧 Configuration

### Model Selection
Edit `rag_agent_simple.py` to change the model:
```python
self.model_name = "llama2:7b"  # Smaller model for less memory
# or
self.model_name = "llama3"     # Larger model for better quality
```

### ChromaDB Settings
The agent uses the existing ChromaDB setup from your project:
- Multi-tenant collections
- Sentence-transformers embeddings
- Oracle DB integration

## 🧪 Testing

### Sample Queries
1. "Show me all orders for customer 12345"
2. "What are the highest value orders?"
3. "Find orders with delivery issues"
4. "Show me recent orders from last month"

### Expected Output
```
🔍 Retrieving context for query: Show me all orders for customer 12345
📄 Retrieved context: Document 1: Order TestErrorADGIT-14236 (ID: 4694521)...
🤖 Generating response with Llama 3...
✅ Response: Based on the context, I found the following order...
```

## 🚨 Troubleshooting

### Memory Issues
If you get memory errors:
1. Use a smaller model: `llama2:7b` instead of `llama3`
2. Increase system memory or use cloud deployment
3. Reduce `top_k` parameter in retrieval

### Ollama Connection Issues
1. Ensure Ollama is running: `ollama serve`
2. Check model availability: `ollama list`
3. Verify API endpoint: `http://localhost:11434`

### ChromaDB Issues
1. Ensure data is populated: `python backfill_orders.py`
2. Check tenant collection exists
3. Verify embedding generation works

## 🔄 Next Steps

1. **Production Deployment**:
   - Use cloud-based LLM (OpenAI, Azure, etc.)
   - Implement proper error handling
   - Add authentication and rate limiting

2. **Enhanced Features**:
   - Multi-turn conversations
   - Structured output (JSON, tables)
   - Integration with existing Streamlit UI

3. **Performance Optimization**:
   - Caching for frequent queries
   - Batch processing for large datasets
   - Async processing for better throughput

## 📊 Performance Notes

- **Retrieval**: Fast semantic search via ChromaDB
- **Generation**: Depends on LLM model and hardware
- **Memory**: Llama 3 requires ~2.6GB, Llama2:7b requires ~1.5GB
- **Response Time**: 2-10 seconds depending on query complexity

## 🤝 Integration

The RAG agent can be integrated into your existing Streamlit app:

```python
# In your Streamlit app
from rag_agent_simple import SimpleRAGAgent

agent = SimpleRAGAgent()
user_query = st.text_input("Ask about your orders...")
if user_query:
    result = agent.generate_response(user_query)
    st.write(result['response'])
```

## 📝 License

This POC is part of the Global Search project and follows the same licensing terms. 