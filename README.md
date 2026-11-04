# AI Research Agent

Custom agent loop built from scratch. No LangChain — I wanted to understand how tool calling actually works.

It decides by itself whether to check my docs (ChromaDB), search the web, or do both. Streams everything live so you can see what it's thinking.

Hardest part was stopping it from calling the wrong tool. Still tweaking that.

## how to run
```
pip install -r requirements.txt
cp .env.example .env  # add your GROQ_API_KEY
python main.py
```

Upload a couple PDFs to `data/` first, otherwise it just uses web search.

## stack
Python, ChromaDB, sentence-transformers, Groq Llama 3, FastAPI SSE

TODO: it's slow on big PDFs, need to fix chunking later.
