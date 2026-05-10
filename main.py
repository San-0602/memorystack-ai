from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cohere
import os
from dotenv import load_dotenv
from memory_store import save_memory, get_relevant_memories
from prompt_builder import build_prompt
from summarizer import summarize_memories

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = cohere.Client(os.getenv("COHERE_API_KEY"))

class ChatRequest(BaseModel):
    message: str
    tags: list = []

class MemoryRequest(BaseModel):
    content: str
    tags: list = []
    importance: float = 0.5
    memory_type: str = "short_term"

@app.post("/chat")
def chat(req: ChatRequest):
    memories = get_relevant_memories(req.message)
    filtered = [m for m in memories if m["similarity"] >= 0.35]

    if len(filtered) > 1:
        summary = summarize_memories(filtered)
        summary_memory = [{
            "content": summary,
            "memory_type": "long_term",
            "tags": ["summary"],
            "score": 1.0,
            "similarity": 1.0
        }]
        prompt = build_prompt(req.message, summary_memory)
    else:
        prompt = build_prompt(req.message, filtered)

    response = client.chat(
        model="command-a-03-2025",
        message=prompt
    )
    reply = response.text

    save_memory(req.message, tags=req.tags, memory_type="short_term")

    return {
        "reply": reply,
        "memories_used": filtered,
        "injected_context": prompt
    }

@app.post("/memory")
def add_memory(req: MemoryRequest):
    save_memory(
        req.content,
        tags=req.tags,
        importance=req.importance,
        memory_type=req.memory_type
    )
    return {"status": "saved", "type": req.memory_type}