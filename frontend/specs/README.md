# Frontend Specs — Data Contracts

Endpoint shapes and parameter rules below were verified directly
against `backend/app/routes.py` and cross-checked in `/docs` against a
running instance of the backend. Types referenced here live in
`api-types.ts` and `param-types.ts` in this same folder.

---

## Feature 1 — Date Range Filter on the Home Dashboard

**Endpoints consumed:**
- `GET /api/metrics/facets` — no parameters. Returns the full dataset's
  available range; not affected by any filter applied elsewhere.
- `GET /api/metrics` — existing endpoint (already used by the current
  dashboard), extended with `start_date`/`end_date` query params.

**Types used:**
- Request: `DateRangeFilter` (`param-types.ts`)
- Response: `FacetsResponse` (`api-types.ts`) for the reference range
- Response: the existing `FinancialMovement[]` type already defined in
  `frontend/src/lib/financial-types.ts` — **not redefined here**, since
  `/api/metrics` isn't a new endpoint and its response shape hasn't
  changed, only its accepted query parameters have.

**Valid values / constraints:**
- `start_date`, `end_date` — optional, `YYYY-MM-DD`, inclusive bounds.
- Each bound is applied independently by the backend — there is no
  requirement that both be present together.

**Edge cases:**
1. **Only one date input is filled in.** Only that bound is sent to
   the API; the other is left unset (not defaulted to today or to the
   dataset's min/max). Example: only `start_date` set → all data from
   that date to the latest available is shown.
2. **`start_date` is after `end_date`.** The backend applies each
   bound as an independent filter, so an inverted range simply matches
   zero movements — not an error response. The UI must treat this the
   same as any other zero-result state (see Feature 2/3 empty-state
   patterns), not as a crash or a silently wrong chart.

---

## Feature 2 — Anomaly Alerts Table

**Endpoint consumed:**
- `GET /api/metrics/alerts` — `threshold`, `start_date`, `end_date`.
  (`group_by` and `business_type` also exist on this endpoint but are
  not used by this feature as specified — the table works at monthly
  granularity only, with no business-type split.)

**Types used:**
- Request: `AlertsParams` (`param-types.ts`)
- Response: `AlertsResponse` / `AlertEntry` (`api-types.ts`)

**Valid values / constraints:**
- `threshold` — the API itself only enforces `>= 0`, no upper bound.
  The product spec's `0.01`–`1.0` range is a **UI-level constraint**
  (enforced by `AnomalyThresholdInput`, see `components.md`), not
  something the API guarantees — this must not be assumed by anything
  reading the response.
- `baseline_average` is a **cumulative average of every prior period
  in the queried range**, not a fixed 3-period rolling window —
  verified by hand-calculating against real `/api/metrics/summary`
  data (Jul–Nov 2025 outcome values averaged to exactly match a real
  December alert's `baseline_average`). Any UI copy describing this
  column must not say "rolling 3-month average."

**Edge cases:**
1. **No anomalies at the current threshold.** The table must not
   disappear — render the header with an explicit empty-state message
   referencing the current threshold (and active date range, if set).
2. **Date range filtering changes what counts as "first period."**
   Because `/api/metrics/alerts` filters data *before* computing the
   baseline, whichever period is first *within the active date range*
   can never produce an alert — there's no prior data for it to be
   compared against, even if a broader baseline existed outside the
   filtered range. This is expected backend behavior, not something
   the UI should work around or flag as an error.

---

## Feature 3 — B2B vs B2C Comparison View

**Endpoints consumed:**
- `GET /api/metrics/categories/top?operation_type=income&business_type=...&limit=5`
  — called **twice**, once per business type, for each panel's table.
  The same response, summed, also produces the values behind the
  bottom comparison chart (there is no separate "total income by
  business type" endpoint).
- `GET /api/metrics/facets` — for the shared category reference.

**Types used:**
- Request: `TopCategoriesParams` (`param-types.ts`)
- Response: `TopCategoriesResponse` / `CategoryEntry` (`api-types.ts`)
- Response: `FacetsResponse` (`api-types.ts`), reused from Feature 1

**Valid values / constraints:**
- `operation_type` — fixed to `"income"` for this feature.
- `limit` — fixed to `5`. Because `Category` has exactly 5 possible
  values, this is guaranteed to return the *complete* category
  breakdown for that business type, not a truncated top slice — which
  is what makes summing `total_amount` across the response a valid way
  to derive each business type's true total income, not an
  approximation.
- `business_type` — required per call; `"B2B"` or `"B2C"`.
- **`total_amount` does not include a percentage.** "Percentage of
  group total" must be computed client-side per panel, as a pure
  function over that panel's own response array (see `components.md`).

**Edge cases:**
1. **One panel's top-5 list is empty while the other has data** (e.g.
   no B2C income in the selected range, but B2B has entries). Each
   `CategoryComparisonPanel` handles its own empty state independently
   — a business type with no data does not affect or hide the other
   panel, and does not empty the comparison chart if the other side
   has a nonzero total.
2. **`/api/metrics/facets` is not scoped by business type.** It has no
   `business_type` parameter, so both panels reference the *same*
   single, global category list from one shared facets call — not two
   separate B2B/B2C-filtered lists. This list is reference-only; it
   does not drive or filter the actual `categories/top` requests,
   which are scoped by `business_type` directly.

---

## Summary — Endpoint Reuse Across Features

| Endpoint | Used by |
|---|---|
| `GET /api/metrics/facets` | Feature 1 (date reference), Feature 3 (category reference) |
| `GET /api/metrics` | Feature 1 (existing, extended with date params) |
| `GET /api/metrics/alerts` | Feature 2 |
| `GET /api/metrics/categories/top` | Feature 3 (called per business type, and reused via summation for the comparison chart) |