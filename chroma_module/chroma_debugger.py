import chromadb
from chromadb import PersistentClient

def list_all_collections():
    client = PersistentClient(path="./chroma_storage")
    collections = client.list_collections()
    print("\n📦 Available Collections:")
    if not collections:
        print("  (None found)")
    for col in collections:
        print(f"  - {col.name}")

def print_collection_contents(collection_name):
    client = PersistentClient(path="./chroma_storage")

    try:
        collection = client.get_collection(collection_name)
        data = collection.get(include=["documents", "embeddings"])
    except chromadb.errors.NotFoundError:
        print(f"\n❌ Collection '{collection_name}' not found.")
        return

    print(f"\n🔍 Inspecting Collection: {collection_name}")
    print(f"📄 Total records: {len(data['ids'])}")

    for i in range(len(data['ids'])):
        print(f"\n🧾 Record {i+1}:")
        print(f"🆔 ID: {data['ids'][i]}")
        print(f"📄 Document: {data['documents'][i]}")
        embedding_preview = data['embeddings'][i][:5] if 'embeddings' in data else "N/A"
        print(f"🔢 Embedding (first 5 dims): {embedding_preview}")

if __name__ == "__main__":
    list_all_collections()

    # 🔧 Specify the collection to inspect
    collection_to_debug = "tenant_tenant_XYZ_collection"
    print_collection_contents(collection_to_debug)
