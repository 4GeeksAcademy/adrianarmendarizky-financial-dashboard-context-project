# Rule: Business Logic Purity

**Scope:** Data transformation/calculation functions in
`frontend/src/lib/*.ts` and helper functions in `backend/app/routes.py`
(e.g. `summarize_movements`, `calculate_net_value`, `build_top_categories`).

**Rule:** Calculation and data-transformation logic must be written as
pure functions — no fetch calls, no DOM/React state, no I/O — kept
separate from components and route handlers, so they can be unit
tested without rendering anything or spinning up the API.

**Rationale:** `computeKPIs()` and `computeMonthlyData()` in
`financial-utils.ts` follow this pattern and are covered by
`financial-utils.test.ts`. The five dashboard components mix rendering
with no comparable logic, which is a real factor in why none of them
have tests. This rule preserves a pattern already working well.

**Compliant example:** A new "average transaction size" metric is
added as its own exported function in `financial-utils.ts`, taking a
movements array and returning a number, with a matching test.

**Non-compliant example:** The calculation is written inline inside a
component's render body or a `useEffect`, making it untestable without
rendering the whole component.