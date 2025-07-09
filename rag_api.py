#!/usr/bin/env python3
"""
FastAPI endpoint for RAG Agent
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag_agent import RAGAgent
import uvicorn

app = FastAPI(title="RAG Agent API", description="RAG Agent with Llama 3 and ChromaDB")

# Initialize the RAG agent
rag_agent = RAGAgent()

class QueryRequest(BaseModel):
    query: str
    tenant_id: str = "tenant_ABC"
    top_k: int = 5

class QueryResponse(BaseModel):
    query: str
    context: str
    response: str
    status: str

@app.get("/")
def read_root():
    return {"message": "RAG Agent API is running"}

@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    """Query the RAG agent with a natural language question"""
    try:
        # Update tenant if different
        if request.tenant_id != rag_agent.tenant_id:
            rag_agent.tenant_id = request.tenant_id
        
        # Generate response
        result = rag_agent.generate_response(request.query)
        
        return QueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model": rag_agent.model_name}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 