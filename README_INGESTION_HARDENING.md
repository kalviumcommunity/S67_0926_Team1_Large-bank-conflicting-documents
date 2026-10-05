# PR: Harden Production Document Ingestion

## Summary

This PR is a production-hardening follow-up to Kushal's document ingestion PR.

The previous implementation introduced the real upload → ingestion → embedding → Qdrant flow, but several failure and concurrency cases needed to be closed before treating the ingestion path as production-ready.

This PR fixes those gaps without changing the external purpose of the ingestion workflow.

## Problems Fixed

### 1. Concurrent upload collision

The previous implementation created temporary files using:

```text
.uploading-<original filename>
```

Two simultaneous uploads with the same filename could overwrite or delete each other's temporary file.

This PR uses OS-generated unique temporary files.

### 2. Race-prone JSON manifest

The previous manifest used a JSON read/modify/write cycle.

Two workers could simultaneously:

```text
read
  ↓
modify
  ↓
write
```

and lose each other's state.

The manifest is now backed by SQLite with:

- transactional claims;
- WAL mode;
- busy timeout;
- unique document/content keys;
- durable processing state;
- indexed/failed state.

### 3. Stuck processing jobs

A process could crash after claiming a document but before finalizing the manifest.

The manifest now records:

```text
processing
indexed
failed
```

and supports reclamation of stale `processing` entries after a configurable TTL.

### 4. Missing compliance metadata

The previous pipeline could allow missing `document_type` and `build_chunk_records()` could then fall back to:

```text
pdf
docx
```

Those are file formats, not compliance document categories.

This PR requires a valid compliance `document_type` at the production ingestion boundary and removes the physical file-type fallback.

### 5. False readiness

The previous `/api/ready` endpoint only constructed a Qdrant client.

Client construction does not prove that Qdrant is reachable.

Readiness now actively checks Qdrant connectivity.

### 6. Failure observability

Failed ingestion jobs are retained in the manifest with:

```text
status
error_code
error_message
updated_at
```

The public API does not expose raw infrastructure details.

## Ingestion Flow

```text
Upload
  ↓
Extension validation
  ↓
Metadata validation
  ↓
Unique temporary file
  ↓
SHA-256 content hash
  ↓
Atomic manifest claim
  ↓
Extraction / cleaning / chunking
  ↓
Production quality gate
  ↓
Embeddings
  ↓
Qdrant upsert
  ↓
Manifest → indexed
```

Failure path:

```text
Any failure
    ↓
Manifest → failed
    ↓
Safe API error
```

## Document Status

Adds:

```http
GET /api/documents/{document_id}/status
```

Only operational fields are exposed:

```text
document_id
filename
status
chunk_count
indexed_count
version
updated_at
```

Internal paths and raw error messages are not returned.

## Durable Manifest Migration

If the previous JSON manifest exists:

```text
data/ingestion_manifest.json
```

the new SQLite manifest attempts a one-time migration into:

```text
data/ingestion_manifest.db
```

The SQLite database becomes the authoritative store.

## Configuration

The ingestion hardening layer supports:

```text
MAX_UPLOAD_BYTES=26214400
INGESTION_MANIFEST_DB=data/ingestion_manifest.db
INGESTION_PROCESSING_TTL_SECONDS=1800
```

The defaults are suitable for the initial deployment but can be overridden per environment.

## Tests

Added:

```text
tests/test_manifest_service.py
tests/test_ingestion_service.py
tests/test_metadata.py
tests/test_qdrant_readiness.py
```

Coverage includes:

- atomic duplicate claims;
- failed-job recovery;
- indexed-job protection;
- stale processing detection;
- successful ingestion;
- duplicate-content rejection;
- missing compliance metadata rejection;
- unsupported file rejection;
- failed ingestion persistence;
- physical-format metadata regression;
- Qdrant readiness checks.

No OpenAI or Qdrant credentials are required for the unit tests.

## Validation

```bash
python -m compileall -q app tests
python -m pytest -q
```

## Dependency

This PR is intended to land after Kushal's production ingestion PR.

It fixes and hardens that implementation rather than introducing a separate ingestion architecture.

## Acceptance Criteria

- [ ] Concurrent uploads cannot collide on temporary filenames.
- [ ] Manifest updates are transactional.
- [ ] Duplicate content cannot be concurrently indexed twice.
- [ ] Stale processing claims can be recovered.
- [ ] Failed ingestion attempts are recorded.
- [ ] Compliance `document_type` is required at the production boundary.
- [ ] PDF/DOCX physical formats are not used as compliance document types.
- [ ] Qdrant readiness performs an actual connectivity check.
- [ ] Document status can be queried safely.
- [ ] Internal file paths and infrastructure errors are not exposed through public API responses.
- [ ] Unit tests cover the new production failure modes.
- [ ] Existing ingestion functionality remains compatible.

## Out of Scope

- RAG query generation;
- rule/version resolution;
- citation validation;
- frontend UI;
- authentication/authorization;
- deployment-provider-specific manifests.

## Suggested Commit

```text
fix: harden production document ingestion state and readiness
```
