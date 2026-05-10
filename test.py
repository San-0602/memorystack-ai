from memory_store import save_memory, get_relevant_memories

save_memory('I want to become an AI engineer', tags=['career', 'ai'])
save_memory('I prefer Python over JavaScript', tags=['coding'])
save_memory('I ate pizza for lunch', tags=['personal'])

results = get_relevant_memories('What are my career goals?')
for r in results:
    print(r['content'], '→ score:', r['score'])