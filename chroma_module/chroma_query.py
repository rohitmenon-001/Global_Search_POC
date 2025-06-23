import chromadb
from utils.embedding_generator import generate_embedding
from chromadb import PersistentClient

# Connect to local ChromaDB collection
_client = PersistentClient(path="./chroma_storage")
_collection = _client.get_or_create_collection("tenant_tenant_ABC_collection")


def semantic_search(query: str, top_k: int = 5):
    """Return top_k semantic search results for the given query."""
    embedding = generate_embedding(query)
    results = _collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        include=["documents", "distances"],
    )
    matches = []
    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    dists = results.get("distances", [[]])[0]
    for i in range(len(ids)):
        match = {
            "record_id": ids[i],
            "sentence": docs[i] if i < len(docs) else None,
            "score": dists[i] if i < len(dists) else None,
        }
        matches.append(match)
    return matches


if __name__ == "__main__":
    example_query = "Order O2020 for customer C200 on 2024-06-24 amount 9999.0 status PAID"

    print(f"\nPerforming semantic search for query: '{example_query}'")
    results = semantic_search(example_query, top_k=3)
    print("\nSearch Results:")
    print("-" * 50)
    for i, res in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Record ID: {res['record_id']}")
        print(f"Sentence: {res['sentence']}")
        print(f"Score: {res['score']}")
        print("-" * 50)
