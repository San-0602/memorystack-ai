import cohere
import os
from dotenv import load_dotenv

load_dotenv()

client = cohere.Client(os.getenv("COHERE_API_KEY"))

def summarize_memories(memories: list) -> str:
    if not memories:
        return ""

    memory_text = "\n".join([f"- {m['content']}" for m in memories])

    response = client.chat(
        model="command-a-03-2025",
        message=f"""Summarize these user memories into one concise paragraph that captures who this user is, what they care about, and what they are working on. Be specific. Do not use bullet points.

Memories:
{memory_text}

Summary:"""
    )

    return response.text.strip()