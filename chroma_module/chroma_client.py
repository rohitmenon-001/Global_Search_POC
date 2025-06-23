from chromadb import PersistentClient
import chroma_module

# Connect to local ChromaDB instance on localhost
_client = PersistentClient(path="./chroma_storage")
_collection = _client.get_or_create_collection("global_search_poc")

def upsert_embedding(record_id, sentence, embedding):
    """Upsert a document into the ChromaDB collection."""
    _collection.upsert(ids=[str(record_id)], documents=[sentence], embeddings=[embedding])


if __name__ == "__main__":
    example_sentence = "Example document"
    example_embedding = [0.1, 0.2, 0.3]
    upsert_embedding("test1", example_sentence, example_embedding)
    print("Inserted test record")
