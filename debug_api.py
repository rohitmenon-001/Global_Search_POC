#!/usr/bin/env python3
"""
Debug script to test API search functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.embedding_generator import generate_embedding
from chroma_module.multitenant_chroma import get_tenant_collection

def test_search():
    print("🔍 Testing search functionality...")
    
    # Test 1: Check collection
    print("\n1. Checking collection...")
    collection = get_tenant_collection('tenant_ABC')
    print(f"   Collection count: {collection.count()}")
    
    # Test 2: Generate embedding
    print("\n2. Generating embedding...")
    query = "orders"
    embedding = generate_embedding(query)
    print(f"   Query: '{query}'")
    print(f"   Embedding length: {len(embedding)}")
    print(f"   Embedding sample: {embedding[:5]}...")
    
    # Test 3: Direct ChromaDB query
    print("\n3. Direct ChromaDB query...")
    results = collection.query(
        query_embeddings=[embedding],
        n_results=3,
        include=["documents", "distances"]
    )
    print(f"   Results keys: {list(results.keys())}")
    print(f"   IDs: {results['ids']}")
    print(f"   Documents count: {len(results['documents'][0]) if results['documents'] else 0}")
    print(f"   Distances: {results['distances']}")
    
    # Test 4: Simulate API response
    print("\n4. Simulating API response...")
    response = []
    if results["ids"] and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            response.append({
                "record_id": results["ids"][0][i],
                "sentence": results["documents"][0][i],
                "score": results["distances"][0][i]
            })
    
    print(f"   Response length: {len(response)}")
    if response:
        print(f"   First result: {response[0]}")
    else:
        print("   No results found!")

if __name__ == "__main__":
    test_search() 