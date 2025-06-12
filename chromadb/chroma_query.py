import chromadb
from utils.embedding_generator import generate_embedding

# Connect to local ChromaDB collection
_client = chromadb.HttpClient()
_collection = _client.get_or_create_collection("global_search_poc")


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
    example_query = "test order query"
    results = semantic_search(example_query, top_k=3)
    for res in results:
        print(res)
