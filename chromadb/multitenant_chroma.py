import chromadb

# Client connection to ChromaDB
_client = chromadb.HttpClient()

# In-memory cache of collections by tenant
_tenant_collections = {}


def get_collection_for_tenant(tenant_id: str):
    """Return the ChromaDB collection for the given tenant, creating it if needed."""
    if tenant_id in _tenant_collections:
        return _tenant_collections[tenant_id]
    collection_name = f"tenant_{tenant_id}_collection"
    collection = _client.get_or_create_collection(collection_name)
    _tenant_collections[tenant_id] = collection
    return collection


def upsert_tenant_embedding(tenant_id: str, record_id: str, sentence: str, embedding):
    """Upsert record for the tenant-specific collection."""
    collection = get_collection_for_tenant(tenant_id)
    collection.upsert(
        ids=[str(record_id)],
        documents=[sentence],
        embeddings=[embedding],
    )


if __name__ == "__main__":
    example_embedding = [0.1, 0.2, 0.3]

    upsert_tenant_embedding("tenant_ABC", "1", "Tenant ABC doc", example_embedding)
    upsert_tenant_embedding("tenant_XYZ", "1", "Tenant XYZ doc", example_embedding)
    print("Inserted example records into tenant collections")
