"""One page of files for any list screen: parse the query, build the queryset, page it.

Paging is keyset: the page after a file starts right after it in the same
sort and order, using (sort field, id) so equal names don't skip or repeat.
"""

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from django.db.models import Q, QuerySet
from django.http import QueryDict

from apps.accounts.models import User
from apps.core.api import ApiError

from .models import File

Scope = Literal["mine", "shared_with_me", "shared_by_me", "search"]
Sort = Literal["name", "modified_at"]
Order = Literal["asc", "desc"]

DEFAULT_LIMIT = 50
MAX_LIMIT = 200


@dataclass(frozen=True)
class ListQuery:
    scope: Scope
    q: str
    sort: Sort
    order: Order
    limit: int
    after: UUID | None


def parse_query(params: QueryDict) -> ListQuery:
    problems: list[str] = []

    filters: list[Scope] = []
    for flag in ("shared_with_me", "shared_by_me"):
        value = params.get(flag)
        if value == "true":
            filters.append(flag)
        elif value is not None:
            problems.append(f"{flag} must be true.")
    q = params.get("q", "").strip()
    if "q" in params:
        filters.append("search")
        if len(q) < 2:
            problems.append("q must be at least 2 characters.")
    if len(filters) > 1:
        problems.append("Pass at most one of shared_with_me, shared_by_me, q.")
    scope: Scope = filters[0] if filters else "mine"

    sort = params.get("sort", "name")
    if sort not in ("name", "modified_at"):
        problems.append("sort must be name or modified_at.")
    order = params.get("order", "asc")
    if order not in ("asc", "desc"):
        problems.append("order must be asc or desc.")

    limit = DEFAULT_LIMIT
    raw_limit = params.get("limit")
    if raw_limit is not None:
        if raw_limit.isdecimal() and 1 <= int(raw_limit) <= MAX_LIMIT:
            limit = int(raw_limit)
        else:
            problems.append("limit must be between 1 and 200.")

    after: UUID | None = None
    raw_after = params.get("after")
    if raw_after is not None:
        try:
            after = UUID(raw_after)
        except ValueError:
            problems.append("after must be a file id.")

    if problems:
        raise ApiError(422, "validation_failed", messages=problems)
    return ListQuery(scope, q, sort, order, limit, after)  # type: ignore[arg-type]


def base_queryset(user: User, query: ListQuery) -> QuerySet[File]:
    files = File.objects.all()
    if query.scope == "mine":
        files = files.filter(owner=user)
    elif query.scope == "shared_with_me":
        files = files.filter(grants__user=user)
    elif query.scope == "shared_by_me":
        files = files.filter(owner=user, grants__isnull=False)
    else:
        files = files.filter(Q(owner=user) | Q(grants__user=user), name__icontains=query.q)
    return files.distinct()


def page(user: User, query: ListQuery) -> tuple[list[File], bool]:
    files = base_queryset(user, query)
    prefix = "" if query.order == "asc" else "-"
    files = files.order_by(f"{prefix}{query.sort}", f"{prefix}id")

    if query.after is not None:
        last = files.filter(id=query.after).first()
        if last is None:
            raise ApiError(
                422, "invalid_after", "after isn't a file in this list; reload from the start."
            )
        value = getattr(last, query.sort)
        beyond = "gt" if query.order == "asc" else "lt"
        files = files.filter(
            Q(**{f"{query.sort}__{beyond}": value})
            | Q(**{query.sort: value, f"id__{beyond}": last.id})
        )

    items = list(files[: query.limit + 1])
    return items[: query.limit], len(items) > query.limit
