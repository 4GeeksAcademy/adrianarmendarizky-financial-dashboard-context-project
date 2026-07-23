from __future__ import annotations

import random
from collections import defaultdict
from datetime import date

from app.models import (
    BusinessType,
    Category,
    FinancialMovement,
    GroupBy,
    MetricsAlert,
    MetricsFacets,
    MetricsSummaryItem,
    OperationType,
    OUTCOME_CATEGORIES,
    TopCategoryItem,
)


def _year_for_month(month: int, today: date) -> int:
    if month < today.month:
        return today.year
    return today.year - 1


def _build_movement(month: int, income_probability: float, today: date) -> FinancialMovement:
    operation_type: OperationType = "income" if random.random() < income_probability else "outcome"
    movement_day = random.randint(1, 28)
    movement_date = date(_year_for_month(month, today), month, movement_day)
    business_type: BusinessType = "B2B" if random.random() < 0.55 else "B2C"

    if operation_type == "income":
        category: Category = "sales" if random.random() < 0.9 else "others"
        amount = round(random.uniform(800, 12000), 2)
    else:
        category = random.choice(OUTCOME_CATEGORIES)
        amount = round(random.uniform(500, 9000), 2)

    return FinancialMovement(
        create_date=movement_date,
        amount=amount,
        operation_type=operation_type,
        category=category,
        business_type=business_type,
    )


def generate_mock_movements(seed: int | None = None) -> list[FinancialMovement]:
    if seed is not None:
        random.seed(seed)
    today = date.today()
    movements: list[FinancialMovement] = []
    for month in range(1, 13):
        income_probability = random.uniform(0.45, 0.7)
        for _ in range(30):
            movements.append(_build_movement(month, income_probability, today))
    movements.sort(key=lambda item: item.create_date)
    return movements


def filter_movements_by_date(
    movements: list[FinancialMovement],
    start_date: date | None,
    end_date: date | None,
) -> list[FinancialMovement]:
    if start_date is None and end_date is None:
        return movements

    filtered = movements
    if start_date is not None:
        filtered = [movement for movement in filtered if movement.create_date >= start_date]
    if end_date is not None:
        filtered = [movement for movement in filtered if movement.create_date <= end_date]
    return filtered


def filter_movements(
    movements: list[FinancialMovement],
    start_date: date | None,
    end_date: date | None,
    category: Category | None,
    operation_type: OperationType | None,
) -> list[FinancialMovement]:
    filtered = filter_movements_by_date(movements, start_date, end_date)
    if category is not None:
        filtered = [movement for movement in filtered if movement.category == category]
    if operation_type is not None:
        filtered = [movement for movement in filtered if movement.operation_type == operation_type]
    return filtered


def ensure_chronological_order(movements: list[FinancialMovement]) -> list[FinancialMovement]:
    return sorted(movements, key=lambda item: item.create_date)


def build_metrics_facets(movements: list[FinancialMovement]) -> MetricsFacets:
    ordered = ensure_chronological_order(movements)
    return MetricsFacets(
        operation_types=sorted({item.operation_type for item in ordered}),
        business_types=sorted({item.business_type for item in ordered}),
        categories=sorted({item.category for item in ordered}),
        min_date=ordered[0].create_date,
        max_date=ordered[-1].create_date,
    )


def summarize_movements(
    movements: list[FinancialMovement],
    group_by: GroupBy,
) -> list[MetricsSummaryItem]:
    summary_map: dict[str, dict[str, float]] = defaultdict(lambda: {"income": 0.0, "outcome": 0.0})
    for movement in movements:
        if group_by == "day":
            key = movement.create_date.isoformat()
        elif group_by == "week":
            iso_year, iso_week, _ = movement.create_date.isocalendar()
            key = f"{iso_year}-W{iso_week:02d}"
        else:
            key = movement.create_date.strftime("%Y-%m")

        summary_map[key][movement.operation_type] += movement.amount

    return [
        MetricsSummaryItem(
            period=period,
            income=round(values["income"], 2),
            outcome=round(values["outcome"], 2),
            net=round(values["income"] - values["outcome"], 2),
        )
        for period, values in sorted(summary_map.items(), key=lambda item: item[0])
    ]


def build_top_categories(
    movements: list[FinancialMovement],
    operation_type: OperationType,
    limit: int,
) -> list[TopCategoryItem]:
    totals: dict[Category, float] = defaultdict(float)
    for movement in movements:
        if movement.operation_type == operation_type:
            totals[movement.category] += movement.amount

    ordered = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    return [
        TopCategoryItem(
            category=category,
            operation_type=operation_type,
            total_amount=round(total_amount, 2),
        )
        for category, total_amount in ordered[:limit]
    ]


def calculate_net_value(movements: list[FinancialMovement]) -> float:
    income = sum(item.amount for item in movements if item.operation_type == "income")
    outcome = sum(item.amount for item in movements if item.operation_type == "outcome")
    return round(income - outcome, 2)


def detect_outcome_alerts(
    summary: list[MetricsSummaryItem],
    threshold: float,
) -> list[MetricsAlert]:
    alerts: list[MetricsAlert] = []
    historical_outcomes: list[float] = []
    for item in summary:
        if historical_outcomes:
            baseline = sum(historical_outcomes) / len(historical_outcomes)
            if baseline > 0:
                increase_ratio = (item.outcome - baseline) / baseline
                if increase_ratio > threshold:
                    alerts.append(
                        MetricsAlert(
                            period=item.period,
                            outcome_total=round(item.outcome, 2),
                            baseline_average=round(baseline, 2),
                            increase_ratio=round(increase_ratio, 4),
                        )
                    )
        historical_outcomes.append(item.outcome)
    return alerts