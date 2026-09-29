from typing import Optional

from qdrant_client.http import models

from app.retrieval.models import SearchFilters


def build_qdrant_filter(
    filters: Optional[SearchFilters],
) -> Optional[models.Filter]:
    if not filters:
        return None

    conditions = []

    for field_name in (
        "document_type",
        "status",
        "document_id",
        "version",
        "effective_date",
    ):
        value = getattr(filters, field_name)
        if value is None:
            continue

        conditions.append(
            models.FieldCondition(
                key=field_name,
                match=models.MatchValue(value=value),
            )
        )

    if not conditions:
        return None

    return models.Filter(must=conditions)
