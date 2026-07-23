import type { BusinessType, OperationType } from "./api-types";

/**
 * Optional date range shared across all three features. Both fields
 * are optional — when omitted, the corresponding feature falls back
 * to its own "no filter" behavior (e.g. showing all available data).
 * Field names match the API's query parameter names exactly
 * (snake_case) to avoid a translation step when building requests.
 */
export interface DateRangeFilter {
  /** Inclusive start date. Format: YYYY-MM-DD. Omit for no lower bound. */
  start_date?: string;
  /** Inclusive end date. Format: YYYY-MM-DD. Omit for no upper bound. */
  end_date?: string;
}

/**
 * Query parameters sent to `GET /api/metrics/alerts` by the anomaly
 * alerts table (Feature 2).
 */
export interface AlertsParams extends DateRangeFilter {
  /**
   * Spike sensitivity as a ratio. The API itself only enforces >= 0
   * (no upper bound) — the 0.01–1.0 range shown on the UI's numeric
   * input is a product-level constraint, not an API-level one.
   * Defaults to 0.3 if omitted.
   */
  threshold?: number;
}

/**
 * Query parameters sent to `GET /api/metrics/categories/top` by the
 * B2B vs B2C comparison view (Feature 3). Called once per business
 * line (business_type: "B2B", then again with "B2C").
 */
export interface TopCategoriesParams extends DateRangeFilter {
  /** Always "income" for this feature — comparing revenue categories. */
  operation_type: OperationType;
  /**
   * Max categories to return. Fixed at 5 for this feature. Since
   * Category has exactly 5 possible values, a limit of 5 always
   * returns the complete category breakdown rather than a truncated
   * "top slice" — which is what makes summing total_amount across
   * the response a valid way to derive a true group total.
   */
  limit: number;
  /** Which business line this request is scoped to. */
  business_type: BusinessType;
}