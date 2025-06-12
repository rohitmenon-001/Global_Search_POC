from sentence_transformers import SentenceTransformer

# Load model globally once
_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def generate_embedding(sentence: str) -> list[float]:
    """Return embedding vector for the given sentence."""
    embedding = _model.encode(sentence)
    # ensure plain list of floats
    if hasattr(embedding, "tolist"):
        return embedding.tolist()
    return list(embedding)


if __name__ == "__main__":
    example = "This is a test sentence."
    vector = generate_embedding(example)
    print(vector)
