from chroma_module.multitenant_chroma import get_tenant_collection

def cleanup_chroma():
    """Clean up all records in ChromaDB for testing"""
    try:
        collection = get_tenant_collection("tenant_ABC")
        count_before = collection.count()
        print(f"📊 Records before cleanup: {count_before}")
        
        if count_before > 0:
            # Delete all records by id
            ids = collection.get()["ids"]
            if ids:
                collection.delete(ids=ids)
            count_after = collection.count()
            print(f"✅ Cleanup complete. Records after cleanup: {count_after}")
        else:
            print("ℹ️ No records to clean up")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    cleanup_chroma() 