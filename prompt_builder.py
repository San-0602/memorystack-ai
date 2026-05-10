def build_prompt(user_message: str, memories: list) -> str:
    if not memories:
        return user_message

    # Group by memory type
    pinned = [m for m in memories if m.get("memory_type") == "pinned"]
    long_term = [m for m in memories if m.get("memory_type") == "long_term"]
    short_term = [m for m in memories if m.get("memory_type") == "short_term"]

    sections = []

    if pinned:
        block = "\n".join([f"- {m['content']}" for m in pinned])
        sections.append(f"Critical facts about this user:\n{block}")

    if long_term:
        block = "\n".join([f"- {m['content']}" for m in long_term])
        sections.append(f"Long-term preferences:\n{block}")

    if short_term:
        block = "\n".join([f"- {m['content']}" for m in short_term])
        sections.append(f"Recent context:\n{block}")

    memory_block = "\n\n".join(sections)

    return f"""You are a helpful AI assistant with memory about this user.

{memory_block}

Use this context naturally in your response when relevant. Don't mention that you're using memories explicitly.

User: {user_message}"""