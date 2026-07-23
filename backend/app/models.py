from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel

OperationType = Literal["income", "outcome"]
Category = Literal["suppliers", "sales", "operational", "administrative", "others"]
BusinessType = Literal["B2B", "B2C"]
GroupBy = Literal["day", "week", "month"]

OUTCOME_CATEGORIES = ["suppliers", "operational", "administrative", "others"]


class FinancialMovement(BaseModel):
    create_date: date
    amount: float
    operation_type: OperationType
    category: Category
    business_type: BusinessType


class MetricsFacets(BaseModel):
    operation_types: list[OperationType]
    business_types: list[BusinessType]
    categories: list[Category]
    min_date: date
    max_date: date


class MetricsSummaryItem(BaseModel):
    period: str
    income: float
    outcome: float
    net: float


class TopCategoryItem(BaseModel):
    category: Category
    operation_type: OperationType
    total_amount: float


class MetricsComparison(BaseModel):
    current_period: float
    previous_period: float
    delta_abs: float
    delta_pct: float | None


class MetricsAlert(BaseModel):
    period: str
    outcome_total: float
    baseline_average: float
    increase_ratio: float