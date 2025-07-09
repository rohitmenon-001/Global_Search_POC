#!/usr/bin/env python3
"""
Hybrid RAG Agent POC - Supports both local Ollama and cloud LLMs
"""

import ollama
import chromadb
from chroma_module.multitenant_chroma import get_tenant_collection
from utils.embedding_generator import generate_embedding
import json
import numpy as np
import os

class HybridRAGAgent:
    def __init__(self, tenant_id="tenant_ABC", use_cloud_fallback=True):
        self.tenant_id = tenant_id
        self.use_cloud_fallback = use_cloud_fallback
        
        # Try different models in order of preference
        self.model_options = [
            "llama3:8b",      # Quantized Llama 3
            "llama2:7b",      # Smaller Llama 2
            "llama3",         # Full Llama 3 (if enough memory)
        ]
        
        self.current_model = None
        self.setup_model()
        
    def setup_model(self):
        """Try to find a working model"""
        for model in self.model_options:
            try:
                print(f"🔄 Trying model: {model}")
                # Test the model with a simple query
                test_response = ollama.chat(
                    model=model,
                    messages=[{'role': 'user', 'content': 'Hello'}],
                    options={'num_ctx': 512}  # Very small context for testing
                )
                self.current_model = model
                print(f"✅ Successfully loaded model: {model}")
                return
            except Exception as e:
                print(f"❌ Failed to load {model}: {e}")
                continue
        
        if not self.current_model:
            print("⚠️ No local models available. Consider using cloud fallback.")
            self.current_model = "none"
        
    def retrieve_context(self, query, top_k=5):
        """Retrieve relevant context from ChromaDB using semantic search"""
        try:
            # Generate embedding for the query
            query_embedding = generate_embedding(query)
            
            # Convert to list if it's a numpy array
            if isinstance(query_embedding, np.ndarray):
                query_embedding = query_embedding.tolist()
            
            # Get tenant collection
            collection = get_tenant_collection(self.tenant_id)
            
            # Search for similar documents
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Extract documents and metadata
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            # Format context
            context = []
            for i, doc in enumerate(documents):
                metadata = metadatas[i] if i < len(metadatas) else {}
                context.append(f"Document {i+1}: {doc}")
                if metadata:
                    context.append(f"Metadata: {metadata}")
            
            return "\n\n".join(context) if context else "No relevant context found."
            
        except Exception as e:
            print(f"Error in retrieval: {e}")
            return "Error retrieving context."
    
    def generate_response_local(self, prompt):
        """Generate response using local Ollama model"""
        try:
            response = ollama.chat(
                model=self.current_model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a helpful assistant that answers questions using the provided context from a database of order information. Always base your answers on the context provided and be specific about order details, customer information, and business insights.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'num_ctx': 2048,  # Reduce context window
                    'num_thread': 4,  # Limit threads
                    'temperature': 0.7
                }
            )
            return response['message']['content']
        except Exception as e:
            raise e
    
    def generate_response_cloud(self, prompt):
        """Generate response using cloud LLM (placeholder for OpenAI, etc.)"""
        # This is a placeholder - you would implement OpenAI, Azure, etc. here
        return f"[CLOUD LLM] Based on the context provided, here's what I found: {prompt[:100]}... (Cloud LLM integration not implemented yet)"
    
    def generate_response(self, user_query):
        """Generate a response using RAG approach"""
        try:
            # Step 1: Retrieve relevant context
            print(f"🔍 Retrieving context for query: {user_query}")
            context = self.retrieve_context(user_query)
            print(f"📄 Retrieved context: {context[:200]}...")
            
            # Step 2: Construct prompt with context
            prompt = f"""User Query: {user_query}

Context from database:
{context}

Please answer the user's question based on the context provided above. Be specific and provide relevant details from the order data. If the context doesn't contain enough information to answer the question, please say so.

Answer:"""
            
            # Step 3: Generate response
            print(f"🤖 Generating response with {self.current_model}...")
            
            if self.current_model != "none":
                try:
                    response_text = self.generate_response_local(prompt)
                except Exception as e:
                    print(f"Local model failed: {e}")
                    if self.use_cloud_fallback:
                        print("🔄 Falling back to cloud LLM...")
                        response_text = self.generate_response_cloud(prompt)
                    else:
                        raise e
            else:
                if self.use_cloud_fallback:
                    response_text = self.generate_response_cloud(prompt)
                else:
                    raise Exception("No local model available and cloud fallback disabled")
            
            return {
                "query": user_query,
                "context": context,
                "response": response_text,
                "status": "success",
                "model_used": self.current_model
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                "query": user_query,
                "context": "",
                "response": f"Error: {str(e)}",
                "status": "error",
                "model_used": self.current_model
            }

def main():
    """Test the hybrid RAG agent with sample queries"""
    print("🚀 Initializing Hybrid RAG Agent...")
    
    # Initialize the agent
    agent = HybridRAGAgent(use_cloud_fallback=True)
    
    # Test queries
    test_queries = [
        "Show me all orders for customer 12345",
        "What are the highest value orders?",
        "Find orders with delivery issues",
        "Show me recent orders from last month"
    ]
    
    print("\n" + "="*50)
    print("🧪 Testing Hybrid RAG Agent")
    print("="*50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 30)
        
        result = agent.generate_response(query)
        
        print(f"✅ Response: {result['response']}")
        print(f"📊 Status: {result['status']}")
        print(f"🤖 Model: {result['model_used']}")
        
        if i < len(test_queries):
            print("\n" + "="*50)

if __name__ == "__main__":
    main() 