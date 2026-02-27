import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import async_get_db
from app.repositories.data_repository import DataRepository, MODEL_MAP

logger = logging.getLogger(__name__)
router = APIRouter()

REPORT_TOTALS = {"report_lottery", "report_funds", "report_provider"}


def _model_to_dict(obj) -> dict:
    """Convert SQLAlchemy model to dict, excluding internal fields."""
    exclude = {"id", "agent_id", "synced_at", "created_at", "updated_at"}
    result = {}
    for col in obj.__table__.columns:
        if col.name in exclude:
            continue
        val = getattr(obj, col.name)
        if val is not None:
            result[col.name] = val
        else:
            result[col.name] = None
    return result


@router.get(
    "/{endpoint_key}",
    status_code=status.HTTP_200_OK,
    summary="Get paginated data",
    description="Retrieve synced data for a specific endpoint. "
    "Returns paginated results with optional total aggregation for reports.",
)
async def get_data(
    endpoint_key: str,
    agent_id: int = Query(default=1, description="Agent ID"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=200, description="Records per page"),
    db: AsyncSession = Depends(async_get_db),
    _: dict = Depends(get_current_user),
) -> dict:
    if endpoint_key not in MODEL_MAP:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown endpoint: {endpoint_key}. "
            f"Available: {', '.join(MODEL_MAP.keys())}",
        )

    repo = DataRepository(db)
    rows, total = await repo.get_paginated(endpoint_key, agent_id, page, limit)

    data = [_model_to_dict(r) for r in rows]

    response: dict = {
        "data": data,
        "count": total,
        "page": page,
        "limit": limit,
        "code": 0,
    }

    # Add total_data for report endpoints
    if endpoint_key in REPORT_TOTALS:
        totals_map = {
            "report_lottery": repo.get_report_lottery_totals,
            "report_funds": repo.get_report_funds_totals,
            "report_provider": repo.get_report_provider_totals,
        }
        response["total_data"] = await totals_map[endpoint_key](agent_id)

    return response
