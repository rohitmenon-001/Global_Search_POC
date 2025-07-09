#!/usr/bin/env python3
"""
Simple RAG Agent POC using Llama 3 + Ollama + ChromaDB
"""

import ollama
import chromadb
from chroma_module.multitenant_chroma import get_tenant_collection
from utils.embedding_generator import generate_embedding
import json
import numpy as np

class SimpleRAGAgent:
    def __init__(self, tenant_id="tenant_ABC"):
        self.tenant_id = tenant_id
        self.model_name = "llama3:8b"  # Try quantized version
        
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
    
    def generate_response(self, user_query, history=None, history_turns=3):
        """Generate a response using RAG approach, with optional conversational history"""
        try:
            # Step 1: Retrieve relevant context
            print(f"🔍 Retrieving context for query: {user_query}")
            context = self.retrieve_context(user_query)
            print(f"📄 Retrieved context: {context[:200]}...")

            # Step 2: Build conversational history prompt
            history_prompt = ""
            if history:
                # Only use the last N turns
                for turn in history[-history_turns:]:
                    history_prompt += f"User: {turn['query']}\nAI: {turn['response']}\n"

            # Step 3: Construct prompt with context and history
            prompt = f"""
{history_prompt}User: {user_query}

Context from database:
{context}

You are a helpful assistant. Always answer in a conversational, friendly, and natural way, as if you are chatting with the user. Be clear and concise, and use plain English sentences and paragraphs. Do not use tables, code, or lists unless the user explicitly asks for them. If the context doesn't contain enough information to answer the question, just say so.

Answer:"""

            # Step 4: Generate response using Llama 3 via Ollama
            print("🤖 Generating response with Llama 3...")
            response = ollama.chat(
                model=self.model_name,
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

            response_text = response['message']['content']

            return {
                "query": user_query,
                "context": context,
                "response": response_text,
                "status": "success"
            }

        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                "query": user_query,
                "context": "",
                "response": f"Error: {str(e)}",
                "status": "error"
            }

def main():
    """Test the simple RAG agent with sample queries"""
    print("🚀 Initializing Simple RAG Agent with Llama 3...")
    
    # Initialize the agent
    agent = SimpleRAGAgent()
    
    # Test queries
    test_queries = [
        "Show me all orders for customer 12345",
        "What are the highest value orders?",
        "Find orders with delivery issues",
        "Show me recent orders from last month"
    ]
    
    print("\n" + "="*50)
    print("🧪 Testing Simple RAG Agent")
    print("="*50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 30)
        
        result = agent.generate_response(query)
        
        print(f"✅ Response: {result['response']}")
        print(f"📊 Status: {result['status']}")
        
        if i < len(test_queries):
            print("\n" + "="*50)

    # Example history
    history = [
        {"query": "Show me all orders for customer 12345", "response": "Order 12345: ..."},
        {"query": "What is the status of those orders?", "response": "Order 12345 is ACTIVE."}
    ]
    result = agent.generate_response("What about their delivery dates?", history=history)
    print(f"\nConversational Response: {result['response']}")

if __name__ == "__main__":
    main() 