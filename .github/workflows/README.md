# GitHub Actions

CI workflows for the compliance RAG backend live in this directory.

The quality-gate workflow is intentionally lightweight and service-independent:
it validates code compilation and the repository's automated tests without
requiring OpenAI or Qdrant credentials.
