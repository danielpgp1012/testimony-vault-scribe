CREATE EXTENSION IF NOT EXISTS vector;

-- New table for semantic chunks
CREATE TABLE IF NOT EXISTS testimony_chunks (
    id            BIGSERIAL PRIMARY KEY,
    testimony_id  BIGINT NOT NULL
                  REFERENCES testimonies(id) ON DELETE CASCADE,
    chunk_index   INT NOT NULL,
    text          TEXT NOT NULL,
    tokens        SMALLINT NOT NULL,
    embedding     VECTOR(768) NOT NULL,
    model_version TEXT NOT NULL DEFAULT 'openai-t3-small-768'
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_chunks_testimony_id
    ON testimony_chunks (testimony_id);

CREATE INDEX IF NOT EXISTS idx_chunks_embedding
    ON testimony_chunks
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
