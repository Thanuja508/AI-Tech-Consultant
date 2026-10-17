import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = PROJECT_ROOT / "data" / "articles"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma_db"

COLLECTION_NAME = "product_knowledge"

# Initial relevance threshold; validate it against your dataset.
MIN_RELEVANCE_SCORE = 0.30

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


# --------------------------------------------------
# Build or update the knowledge base
# --------------------------------------------------

def build_knowledge_base():
    if not ARTICLES_DIR.exists():
        print(f"Articles directory not found: {ARTICLES_DIR}")
        return

    files = sorted(ARTICLES_DIR.glob("*.json"))

    if not files:
        print("No article JSON files found.")
        return

    documents = []
    metadatas = []
    ids = []

    for file in files:
        try:
            with file.open("r", encoding="utf-8") as f:
                article = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Skipping {file.name}: {exc}")
            continue

        if not isinstance(article, dict):
            continue

        content = str(article.get("content") or "").strip()

        if not content:
            continue

        documents.append(content)
        metadatas.append({
            "title": str(article.get("title") or file.stem),
            "url": str(article.get("url") or ""),
        })
        ids.append(file.stem)

    if not documents:
        print("No usable article content found.")
        return

    embeddings = model.encode(
        documents,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).tolist()

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(f"Knowledge base updated: {len(documents)} articles.")
    print(f"Total records: {collection.count()}")


# --------------------------------------------------
# Relevance score
# --------------------------------------------------

def _similarity_from_distance(distance):
    if distance is None:
        return 0.0

    distance = float(distance)
    metric = (collection.metadata or {}).get("hnsw:space", "l2")

    if metric == "cosine":
        return max(0.0, min(1.0, 1.0 - distance))

    if metric == "ip":
        return max(0.0, min(1.0, 1.0 - distance))

    # Normalized embeddings with ChromaDB's default squared L2 distance.
    return max(0.0, min(1.0, 1.0 - distance / 2.0))


# --------------------------------------------------
# Search with relevance filtering
# --------------------------------------------------

def search_knowledge_base(query: str, top_k: int = 5):
    query = str(query).strip()

    if not query or collection.count() == 0:
        return []

    top_k = max(1, min(int(top_k), 10))

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
    ).tolist()

    result_count = min(top_k * 3, collection.count(), 30)

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=result_count,
        include=["documents", "metadatas", "distances"],
    )

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    matches = []

    for i, article_id in enumerate(ids):
        content = documents[i] if i < len(documents) else None
        metadata = metadatas[i] if i < len(metadatas) else None
        distance = distances[i] if i < len(distances) else None

        if not content or not metadata:
            continue

        score = _similarity_from_distance(distance)

        # Reject weak semantic matches.
        if score < MIN_RELEVANCE_SCORE:
            continue

        matches.append({
            "id": article_id,
            "title": str(metadata.get("title") or "Untitled"),
            "url": str(metadata.get("url") or ""),
            "content": content,
            "relevance_score": round(score, 4),
        })

    return matches[:top_k]


# --------------------------------------------------
# Build index when run directly
# --------------------------------------------------

if __name__ == "__main__":
    build_knowledge_base()