from chroma_module.multitenant_chroma import get_tenant_collection

def check_chroma_records():
    """Check how many records are currently in ChromaDB"""
    try:
        collection = get_tenant_collection("tenant_ABC")
        count = collection.count()
        print(f"📊 Current records in ChromaDB for tenant 'tenant_ABC': {count}")
        
        if count > 0:
            print("\n🔍 Sample records:")
            results = collection.peek(limit=5)
            for i, (id, metadata, embedding) in enumerate(zip(results['ids'], results['metadatas'], results['embeddings']), 1):
                print(f"  {i}. ID: {id}")
                if metadata:
                    print(f"     Metadata: {metadata}")
                print(f"     Embedding dims: {len(embedding) if embedding is not None else 0}")
                print()
        
        return count
    except Exception as e:
        print(f"❌ Error checking ChromaDB: {e}")
        return 0

if __name__ == "__main__":
    check_chroma_records() 