# Semantic Search Setup

This module provides utilities for chunking transcripts, generating OpenAI embeddings and indexing testimonies.

## Environment Variables

- `OPENAI_API_KEY` – your OpenAI API key.
- `SUPABASE_URL` – Supabase project URL.
- `SUPABASE_KEY` – Supabase service role or anon key.

Export these before running the indexer:

```bash
export OPENAI_API_KEY=sk-...
export SUPABASE_URL=https://xyz.supabase.co
export SUPABASE_KEY=eyJ...
```

## Indexing Existing Testimonies

Run the indexer to process testimonies missing from the `testimony_chunks` table:

```bash
python -m semantic.index_testimonies
```
