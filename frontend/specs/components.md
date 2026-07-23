# Component Specifications

Scope note: this document specifies component boundaries, props, and
conditional rendering only. No implementation, no API calls — those
belong to whoever builds against this spec.

---

## Feature 1 — Date Range Filter on the Home Dashboard

### `DateRangeFilterBar`
New component. Renders the two date inputs and the available-range
reference text. **Shared** between Feature 1 and Feature 2 on the home
dashboard (one instance, not one per feature) — Feature 2's table must
respect the same filter, per the challenge spec. Feature 3 uses a
**separate instance** on its own page, with independent state.

**Props:**
| Prop | Type | Notes |
|---|---|---|
| `value` | `{ start_date?: string; end_date?: string }` | Current selection, `param-types.ts`'s `DateRangeFilter` shape. |
| `onChange` | `(range: { start_date?: string; end_date?: string }) => void` | Fired when either input changes. |
| `availableRange` | `Pick<FacetsResponse, "min_date" \| "max_date"> \| null` | From `/api/metrics/facets`. `null` while loading. |
| `isLoadingRange` | `boolean` | True while the facets request is in flight. |

**Conditional rendering:**
- Both inputs empty → no filter is applied anywhere consuming this
  component; all available data is shown (no `start_date`/`end_date`
  sent to the API).
- **Only one input filled** (explicitly specified, per evaluation
  requirement): only that bound is sent to the API — the other stays
  unset, not defaulted to today's date or the dataset boundary. This
  matches the backend's own filtering logic (`filter_movements_by_date`
  applies each bound independently, only if present). Example: only
  `start_date` set → shows everything from that date to the most
  recent available data.
- `availableRange === null` (facets still loading): the two date
  inputs still render and remain interactive; the reference text
  (e.g. "Data available: ...") shows a loading placeholder instead of
  a date range.
- Once `availableRange` resolves: reference text shows
  `availableRange.min_date` – `availableRange.max_date`, formatted for
  display (raw values are `YYYY-MM-DD` strings).

### Existing dashboard components (KPI cards, charts)
No new components required. They continue to receive computed
KPI/chart data as before — the only change is that the underlying
`/api/metrics` call now includes whatever `start_date`/`end_date` the
`DateRangeFilterBar` currently holds.

---

## Feature 2 — Anomaly Alerts Table

### `AnomalyThresholdInput`
New component. Numeric input controlling spike sensitivity.

**Props:**
| Prop | Type | Notes |
|---|---|---|
| `value` | `number` | Current threshold. Defaults to `0.3`. |
| `onChange` | `(value: number) => void` | Fired on change. |
| `min` | `number` | `0.01` — UI-level bound; the API itself only enforces `>= 0`. |
| `max` | `number` | `1.0` — UI-level bound; not enforced by the API. |

**Conditional rendering:**
- Values outside `0.01`–`1.0` are rejected/clamped at this component's
  level before a request is ever made — the API would otherwise
  silently accept them and likely just return an empty or unexpected
  alert list rather than an error.

### `AnomalyAlertsTable`
New component. Renders below the existing charts.

**Props:**
| Prop | Type | Notes |
|---|---|---|
| `alerts` | `AlertsResponse` (`AlertEntry[]`) | Result of `GET /api/metrics/alerts`. |
| `isLoading` | `boolean` | True while the request is in flight. |
| `threshold` | `number` | The threshold value the current `alerts` reflect — needed for the empty-state message. |
| `dateRange` | `{ start_date?: string; end_date?: string }` | The active range from the shared `DateRangeFilterBar`, for the empty-state message. |

**Conditional rendering:**
- `isLoading === true` → show a loading indicator in place of the table body.
- **`alerts.length === 0`** (explicitly specified, per evaluation
  requirement): the table does **not** disappear. Render the table
  header (Period / Recorded Outcome / Rolling Baseline / Spike
  Increase) with an explicit empty-state row/message beneath it, e.g.
  *"No anomalies detected at the current threshold ({threshold})"* —
  appended with *"within the selected date range"* if `dateRange` has
  either bound set.
- `alerts.length > 0` → render one row per `AlertEntry`: `period`,
  `outcome_total` (currency-formatted), `baseline_average`
  (currency-formatted, labeled as a running average, not "last 3
  periods"), `increase_ratio` (formatted as a percentage, e.g. `0.6082`
  → `"60.82%"`).
- Edge case: if the active date range's first period has no prior
  data to compare against, it will never appear as a row — this is
  expected backend behavior (see `README.md`), not a bug to design
  around.

---

## Feature 3 — B2B vs B2C Comparison View

### `ComparisonPage`
New page/route. Hosts its own `DateRangeFilterBar` instance (state
independent from the home dashboard's), and arranges the two
`CategoryComparisonPanel`s side by side with `IncomeComparisonChart`
below.

**Props:** none (top-level page; manages its own date range state
internally, passed down to its children).

### `CategoryComparisonPanel`
New component. Rendered **twice** — once per business type.

**Props:**
| Prop | Type | Notes |
|---|---|---|
| `businessType` | `BusinessType` | `"B2B"` or `"B2C"` — which panel this is. |
| `categories` | `TopCategoriesResponse` (`CategoryEntry[]`) | Result of `GET /api/metrics/categories/top?operation_type=income&business_type=...&limit=5`. |
| `isLoading` | `boolean` | True while the request is in flight. |

**Conditional rendering:**
- `isLoading === true` → loading indicator in place of the table.
- **`categories.length === 0`** (explicitly specified, per evaluation
  requirement, independently for each panel): render an explicit
  empty-state message scoped to that business type, e.g. *"No income
  recorded for B2C in the selected date range."* — not a blank table,
  and not the other panel's data.
- `categories.length > 0` → render one row per `CategoryEntry`:
  `category`, `total_amount` (currency-formatted), and a **percentage
  of group total** column. That percentage is not part of the API
  response — it must be computed client-side as
  `entry.total_amount / sum(all entries in this panel's total_amount)`.
  This computation should be written as a pure function (no side
  effects), consistent with the existing `financial-utils.ts` pattern
  and the `business-logic-purity` rule from Phase 3 — so it can be
  unit tested the same way `computeKPIs` is.

### `IncomeComparisonChart`
New component. Renders below both panels.

**Props:**
| Prop | Type | Notes |
|---|---|---|
| `b2bTotal` | `number` | Sum of `total_amount` across the B2B panel's `CategoryEntry[]`. |
| `b2cTotal` | `number` | Sum of `total_amount` across the B2C panel's `CategoryEntry[]`. |
| `isLoading` | `boolean` | True while either underlying request is in flight. |

**Conditional rendering:**
- `isLoading === true` → loading indicator.
- `b2bTotal === 0 && b2cTotal === 0` → explicit empty-state message
  instead of rendering an empty/misleading chart, e.g. *"No income
  data available for the selected date range."*
- Otherwise → render the two-value visual comparison. A single group
  having `0` while the other doesn't is a valid, renderable state (not
  an empty state) — the chart should show that contrast, not hide it.