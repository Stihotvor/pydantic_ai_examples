import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

_collection = chromadb.Client().get_or_create_collection(
    name="documents",
    embedding_function=ONNXMiniLM_L6_V2()
)


def add_text(text: str, doc_id: str) -> None:
    _collection.add(
        documents=[text],
        ids=[doc_id]
    )


def search(query: str, top_k: int = 3) -> list[str]:
    results = _collection.query(
        query_texts=[query],
        n_results=top_k
    )
    return results['documents'][0]
