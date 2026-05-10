from db import get_connection
from embeddings import embed
from datetime import datetime

def save_memory(content: str, tags: list = [], importance: float = 0.5, memory_type: str = 'short_term'):
    vector = embed(content)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO memories (content, embedding, tags, importance, memory_type) VALUES (%s, %s, %s, %s, %s)",
        (content, vector, tags, importance, memory_type)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_relevant_memories(query: str, top_k: int = 5) -> list:
    query_vector = embed(query)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT content, tags, importance, created_at, memory_type,
               1 - (embedding <=> %s::vector) AS similarity
        FROM memories
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (query_vector, query_vector, top_k * 3))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    results = []
    now = datetime.now()
    for content, tags, importance, created_at, memory_type, similarity in rows:
        age_days = (now - created_at).days
        recency = max(0, 1 - age_days / 30)

        # Pinned memories get a boost
        importance_score = 1.0 if memory_type == 'pinned' else importance

        final_score = (similarity * 0.7) + (recency * 0.2) + (importance_score * 0.1)

        results.append({
            "content": content,
            "tags": tags,
            "score": round(final_score, 4),
            "similarity": round(similarity, 4),
            "memory_type": memory_type
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    # Deduplication — remove near-identical memories
    deduplicated = []
    seen_contents = []
    for r in results:
        is_duplicate = False
        for seen in seen_contents:
            # Simple word overlap check
            words_r = set(r["content"].lower().split())
            words_seen = set(seen.lower().split())
            overlap = len(words_r & words_seen) / max(len(words_r), len(words_seen))
            if overlap > 0.7:
                is_duplicate = True
                break
        if not is_duplicate:
            deduplicated.append(r)
            seen_contents.append(r["content"])

    return deduplicated[:top_k]