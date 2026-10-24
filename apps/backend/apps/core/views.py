import logging

from django.db import DatabaseError, connection
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@require_GET
def health(request: HttpRequest) -> JsonResponse:
    """Liveness + database readiness probe for load balancers and the frontend."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        database = "ok"
    except DatabaseError:
        logger.exception("Health check: database unavailable")
        database = "unavailable"

    healthy = database == "ok"
    return JsonResponse(
        {"status": "ok" if healthy else "degraded", "database": database},
        status=200 if healthy else 503,
    )
