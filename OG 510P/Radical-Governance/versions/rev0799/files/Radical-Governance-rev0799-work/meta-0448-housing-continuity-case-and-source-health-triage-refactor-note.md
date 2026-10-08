# meta-0448 — Housing continuity case and source-health triage refactor note

rev0747 shifts from maintenance-only repair into the riskier substantive gap: housing stability, eviction, rental assistance, tenant screening, right-to-counsel implementation, court-based assistance, and homelessness consequence surfaces.

The key design choice was to avoid a doctrine-only note. Notes 928 and 929 define a concrete joined docket and an applied case packet, while `metadata/housing_continuity_tests.json` makes the tests operational. The anti-theater rule is **no housing stability by portal status**.

The bounded refactor in this turn is source-health triage. `tools/build_source_health.py` now assigns source-health triage scores and reasons so unchecked sources with current-note, case-packet, claim, or high-volatility dependencies rise before low-risk catalog residue. This is deliberately a maintenance accelerant, not a new governance layer.

GAP-010 is now repaired for initial U.S. coverage. Future work should deepen local comparators and outcome studies only when a concrete case demands them.
