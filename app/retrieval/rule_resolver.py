from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, List, Optional, Tuple

from app.retrieval.models import SearchResult


class RuleResolutionError(ValueError):
    """Raised when compliance rule resolution cannot be completed."""


@dataclass(frozen=True)
class ResolutionGroup:
    document_id: str
    version: Optional[str]
    effective_date: Optional[date]
    status: Optional[str]
    results: List[SearchResult]

    @property
    def best_score(self) -> float:
        return max((result.score for result in self.results), default=0.0)


@dataclass(frozen=True)
class RuleResolution:
    selected: List[SearchResult]
    excluded: List[SearchResult]
    as_of_date: date

    @property
    def has_current_rule(self) -> bool:
        return bool(self.selected)


def _parse_date(value: object) -> Optional[date]:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _version_key(version: Optional[str]) -> Tuple[int, str]:
    if not version:
        return (0, "")
    parts = str(version).split(".")
    numeric = []
    for part in parts:
        if part.isdigit():
            numeric.append(part.zfill(12))
        else:
            return (1, str(version))
    return (2, ".".join(numeric))


class CurrentRuleResolver:
    """Deterministically resolves retrieved evidence to applicable active versions."""

    ACTIVE_STATUS = "active"

    def resolve(self, results: Iterable[SearchResult], *, as_of_date: Optional[date] = None) -> RuleResolution:
        evidence = list(results)
        reference_date = as_of_date or date.today()
        if not evidence:
            return RuleResolution([], [], reference_date)

        groups = self._group_versions(evidence)
        eligible_groups = [
            group for group in groups
            if group.status == self.ACTIVE_STATUS
            and group.effective_date is not None
            and group.effective_date <= reference_date
        ]

        winners = {}
        for group in eligible_groups:
            family = group.document_id
            current = winners.get(family)
            if current is None or self._group_sort_key(group) > self._group_sort_key(current):
                winners[family] = group

        selected_groups = sorted(
            winners.values(),
            key=lambda group: (
                group.effective_date or date.min,
                group.best_score,
                _version_key(group.version),
                group.document_id,
            ),
            reverse=True,
        )

        selected=[]
        selected_group_keys={(group.document_id, group.version) for group in selected_groups}
        for group in selected_groups:
            selected.extend(sorted(group.results, key=lambda result: (-result.score, result.chunk_id)))

        excluded=[
            result
            for group in groups
            if (group.document_id, group.version) not in selected_group_keys
            for result in group.results
        ]
        return RuleResolution(selected=selected, excluded=excluded, as_of_date=reference_date)

    @staticmethod
    def _group_sort_key(group: ResolutionGroup):
        return (group.effective_date or date.min, _version_key(group.version), group.best_score)

    @staticmethod
    def _group_versions(results: List[SearchResult]) -> List[ResolutionGroup]:
        buckets={}
        for result in results:
            key=(result.document_id, result.version)
            buckets.setdefault(key, []).append(result)

        groups=[]
        for (document_id, version), group_results in buckets.items():
            effective_dates=[_parse_date(result.effective_date) for result in group_results]
            effective_dates=[item for item in effective_dates if item is not None]
            statuses=[(result.status or "").strip().lower() for result in group_results]
            unique_statuses={status for status in statuses if status}
            status=next(iter(unique_statuses)) if len(unique_statuses)==1 else None
            groups.append(ResolutionGroup(
                document_id=document_id,
                version=version,
                effective_date=min(effective_dates) if effective_dates else None,
                status=status,
                results=group_results,
            ))
        return groups
