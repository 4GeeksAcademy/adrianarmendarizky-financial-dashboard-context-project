from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Query

from app.models import (
    BusinessType,
    Category,
    FinancialMovement,
    GroupBy,
    MetricsAlert,
    MetricsComparison,
    MetricsFacets,
    MetricsSummaryItem,
    OperationType,
    TopCategoryItem,
)
from app.services import (
    build_metrics_facets,
    build_top_categories,
    calculate_net_value,
    detect_outcome_alerts,
    ensure_chronological_order,
    filter_movements,
    filter_movements_by_date,
    generate_mock_movements,
    summarize_movements,
)

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/metrics", response_model=list[FinancialMovement])
def get_metrics(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    category: Category | None = Query(default=None),
    operation_type: OperationType | None = Query(default=None),
) -> list[FinancialMovement]:
    movements = generate_mock_movements(seed=42)
    filtered = filter_movements(
        movements, start_date, end_date, category, operation_type
    )
    return ensure_chronological_order(filtered)


@router.get("/api/metrics/facets", response_model=MetricsFacets)
def get_metrics_facets() -> MetricsFacets:
    movements = generate_mock_movements(seed=42)
    return build_metrics_facets(movements)


@router.get("/api/metrics/summary", response_model=list[MetricsSummaryItem])
def get_metrics_summary(
    group_by: GroupBy = Query(default="month"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    category: Category | None = Query(default=None),
    operation_type: OperationType | None = Query(default=None),
    business_type: BusinessType | None = Query(default=None),
) -> list[MetricsSummaryItem]:
    movements = generate_mock_movements(seed=42)
    if business_type is not None:
        movements = [
            item for item in movements if item.business_type == business_type
        ]
    filtered = filter_movements(
        movements, start_date, end_date, category, operation_type
    )
    return summarize_movements(filtered, group_by)


@router.get("/api/metrics/categories/top", response_model=list[TopCategoryItem])
def get_top_categories(
    operation_type: OperationType = Query(default="outcome"),
    limit: int = Query(default=5, ge=1, le=20),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    business_type: BusinessType | None = Query(default=None),
) -> list[TopCategoryItem]:
    movements = generate_mock_movements(seed=42)
    if business_type is not None:
        movements = [
            item for item in movements if item.business_type == business_type
        ]
    filtered = filter_movements(
        movements, start_date, end_date, category=None, operation_type=operation_type
    )
    return build_top_categories(filtered, operation_type, limit)


@router.get("/api/metrics/comparison", response_model=MetricsComparison)
def get_metrics_comparison(
    start_date: date = Query(...),
    end_date: date = Query(...),
    business_type: BusinessType | None = Query(default=None),
) -> MetricsComparison:
    movements = generate_mock_movements(seed=42)
    if business_type is not None:
        movements = [
            item for item in movements if item.business_type == business_type
        ]

    current_movements = filter_movements(
        movements, start_date, end_date, category=None, operation_type=None
    )
    current_net = calculate_net_value(current_movements)

    duration = end_date - start_date
    previous_end = start_date - timedelta(days=1)
    previous_start = previous_end - duration
    previous_movements = filter_movements(
        movements, previous_start, previous_end, category=None, operation_type=None
    )
    previous_net = calculate_net_value(previous_movements)

    delta_abs = round(current_net - previous_net, 2)
    delta_pct = None
    if previous_net != 0:
        delta_pct = round((delta_abs / abs(previous_net)) * 100, 2)

    return MetricsComparison(
        current_period=current_net,
        previous_period=previous_net,
        delta_abs=delta_abs,
        delta_pct=delta_pct,
    )


@router.get("/api/metrics/alerts", response_model=list[MetricsAlert])
def get_metrics_alerts(
    threshold: float = Query(default=0.3, ge=0),
    group_by: GroupBy = Query(default="month"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    business_type: BusinessType | None = Query(default=None),
) -> list[MetricsAlert]:
    movements = generate_mock_movements(seed=42)
    if business_type is not None:
        movements = [
            item for item in movements if item.business_type == business_type
        ]

    filtered = filter_movements(
        movements, start_date, end_date, category=None, operation_type=None
    )
    summary = summarize_movements(filtered, group_by)
    return detect_outcome_alerts(summary, threshold)


@router.get("/api/metrics/b2b", response_model=list[FinancialMovement])
def get_b2b_metrics(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    category: Category | None = Query(default=None),
    operation_type: OperationType | None = Query(default=None),
) -> list[FinancialMovement]:
    movements = [
        movement
        for movement in generate_mock_movements(seed=42)
        if movement.business_type == "B2B"
    ]
    filtered = filter_movements(
        movements, start_date, end_date, category, operation_type
    )
    return ensure_chronological_order(filtered)


@router.get("/api/metrics/b2c", response_model=list[FinancialMovement])
def get_b2c_metrics(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    category: Category | None = Query(default=None),
    operation_type: OperationType | None = Query(default=None),
) -> list[FinancialMovement]:
    movements = [
        movement
        for movement in generate_mock_movements(seed=42)
        if movement.business_type == "B2C"
    ]
    filtered = filter_movements(
        movements, start_date, end_date, category, operation_type
    )
    return ensure_chronological_order(filtered)


@router.get(
    "/api/metrics/b2c/categories/top-spenders",
    response_model=list[TopCategoryItem],
)
def get_b2c_top_spenders(
    limit: int = Query(default=5, ge=1, le=20),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
) -> list[TopCategoryItem]:
    movements = [
        movement
        for movement in generate_mock_movements(seed=42)
        if movement.business_type == "B2C"
    ]
    filtered = filter_movements(
        movements,
        start_date,
        end_date,
        category=None,
        operation_type="outcome",
    )
    return build_top_categories(filtered, "outcome", limit)
