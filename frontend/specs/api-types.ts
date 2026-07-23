/**
 * Shared API response and domain types for the frontend spec.
 * These interfaces mirror the exact shapes returned by the backend,
 * as defined in `backend/app/routes.py` and verified against `/docs`.
 */

/** The type of financial movement: money coming in or going out. */
export type OperationType = "income" | "outcome";

/** The spending/revenue category a movement is classified under. */
export type Category =
  | "suppliers"
  | "sales"
  | "operational"
  | "administrative"
  | "others";

/** Which business line a movement belongs to. */
export type BusinessType = "B2B" | "B2C";

/**
 * Response shape for `GET /api/metrics/facets`.
 * Reflects the complete dataset — this endpoint accepts no filter
 * parameters, so it always reports the full available range and
 * value sets regardless of any date range or other filter applied
 * elsewhere in the UI.
 */
export interface FacetsResponse {
  /** Distinct operation types present in the dataset. */
  operation_types: OperationType[];
  /** Distinct business types present in the dataset. */
  business_types: BusinessType[];
  /**
   * Distinct categories present in the dataset. Derived from actual
   * data, not a static list — in principle could omit a category if
   * it never appears in the generated data, though unlikely given
   * dataset size.
   */
  categories: Category[];
  /** Earliest movement date in the dataset. Format: YYYY-MM-DD. */
  min_date: string;
  /** Latest movement date in the dataset. Format: YYYY-MM-DD. */
  max_date: string;
}

/**
 * A single anomaly entry as returned by `GET /api/metrics/alerts`.
 * Represents one period whose outcome exceeded its historical
 * baseline by more than the requested threshold.
 */
export interface AlertEntry {
  /** The period this alert belongs to, e.g. "2025-12" (monthly grouping). */
  period: string;
  /** Total outcome (spending) recorded for this period. */
  outcome_total: number;
  /**
   * The cumulative average outcome across every period before this
   * one, starting from the beginning of the queried/filtered range —
   * NOT a fixed-length rolling window. The first period in any
   * queried range never appears in the alerts list, since no
   * baseline exists yet to compare it against.
   */
  baseline_average: number;
  /**
   * How far this period's outcome exceeded the baseline, as a ratio
   * (e.g. 0.6082 = a 60.82% increase over baseline). Only periods
   * exceeding the requested threshold are included in the response.
   */
  increase_ratio: number;
}

/** Response shape for `GET /api/metrics/alerts`: a list of anomalies. */
export type AlertsResponse = AlertEntry[];

/** A single category total as returned by `GET /api/metrics/categories/top`. */
export interface CategoryEntry {
  /** The category this total belongs to. */
  category: Category;
  /** The operation type this total was computed for (matches the request). */
  operation_type: OperationType;
  /**
   * Sum of all matching movement amounts for this category. Does NOT
   * include a percentage-of-total field — any percentage shown in
   * the UI must be computed client-side from the full response array.
   */
  total_amount: number;
}

/** Response shape for `GET /api/metrics/categories/top`: ranked category totals. */
export type TopCategoriesResponse = CategoryEntry[];