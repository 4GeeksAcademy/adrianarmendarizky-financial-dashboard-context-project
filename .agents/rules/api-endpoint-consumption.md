# Rule: API Endpoint Consumption

**Scope:** Any backend route added to `backend/app/routes.py`.

**Rule:** A backend endpoint must either (a) be called by the frontend,
or (b) have an explicit comment or memory-bank entry stating why it
exists without a consumer (e.g. "reserved for a future filters panel").
No endpoint should exist silently unconsumed with no explanation.

**Rationale:** In Phase 2 we found 8 of 9 routes, plus all filter/sort
query params, were built but never called from `App.tsx` (verified via
`grep -rn "fetch(" .`). That's not inherently wrong — but with no
documentation of intent, there's no way to tell "planned, not yet
wired up" apart from "abandoned, safe to delete."

**Compliant example:** A new `/api/metrics/export` route ships with
either a frontend call to it, or a one-line comment: `# Reserved for
CSV export feature — not yet wired to frontend, see memory-bank/status.md`.

**Non-compliant example:** A new route is added with no frontend call
and no note — exactly the current state of `/api/metrics/summary`,
`/comparison`, `/alerts`, etc.