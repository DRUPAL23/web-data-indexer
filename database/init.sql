CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS documents (
  id BIGSERIAL PRIMARY KEY,
  url TEXT NOT NULL UNIQUE,
  title TEXT,
  content TEXT,
  content_hash TEXT,
  embedding vector(1536),
  search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(title,'') || ' ' || coalesce(content,''))) STORED,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at TIMESTAMPTZ,
  status TEXT NOT NULL DEFAULT 'indexed'
);
CREATE INDEX IF NOT EXISTS documents_search_idx ON documents USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS documents_embedding_idx ON documents USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS entities (
  id BIGSERIAL PRIMARY KEY,
  canonical_name TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  description TEXT,
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(canonical_name, entity_type)
);

CREATE TABLE IF NOT EXISTS relationships (
  id BIGSERIAL PRIMARY KEY,
  source_entity_id BIGINT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
  target_entity_id BIGINT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
  relation_type TEXT NOT NULL,
  weight DOUBLE PRECISION NOT NULL DEFAULT 1,
  document_id BIGINT REFERENCES documents(id) ON DELETE SET NULL,
  metadata JSONB NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS relationships_source_idx ON relationships(source_entity_id);
CREATE INDEX IF NOT EXISTS relationships_target_idx ON relationships(target_entity_id);

CREATE TABLE IF NOT EXISTS provenance (
  id BIGSERIAL PRIMARY KEY,
  document_id BIGINT REFERENCES documents(id) ON DELETE CASCADE,
  source_url TEXT NOT NULL,
  retrieved_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  extractor TEXT,
  checksum TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'
);
