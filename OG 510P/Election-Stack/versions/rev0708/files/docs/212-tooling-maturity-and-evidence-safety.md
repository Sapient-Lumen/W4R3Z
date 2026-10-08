# 212 — Tooling maturity and evidence safety

**Track:** A (Deployable core)

This archive contains both **deployable operator helpers** and **research scaffolding**.
To prevent accidental misuse (especially under incident pressure), we maintain a small, auditable intent registry:

- **Canonical registry:** `artifacts/registries/tool-maturity.csv`

The registry is **non‑normative** (it does not define envelope semantics), but it is a **drift firewall**:
release checks ensure every `tools/*.py` file is classified and that the list stays sorted + complete.

## 212.1 Maturity classes

- **operator** — intended for drills/incidents; narrow inputs/outputs; keep smoke tests.
- **research** — exploratory analysis; outputs are not stable contracts.
- **skeleton** — explicitly incomplete placeholders; do not treat outputs as evidence.
- **library** — internal helper modules.

## 212.2 Evidence safety tags

The registry uses a tight tag set:

- **evidence_safe=yes** — output is bounded and primarily computed from local inputs (e.g., digest cards, registry pins).
- **evidence_safe=conditional** — output may be publishable but requires operator judgment (e.g., integrity checks that do not verify signatures).
- **evidence_safe=no** — do not publish outputs as evidence.

This is intentionally conservative: **a tool can be “operator” and still not be evidence‑safe**.

## 212.3 Maintenance rules

When adding or refactoring tools:

**Example packet expectation (tight):** for any `track=A` envelope kind marked `experimental`, ship at least one minimal example packet under `artifacts/examples/` so verifiers can regression-test parsers without rehosting large artifacts.


1. Add/adjust the row in `artifacts/registries/tool-maturity.csv` (keep sorted).
2. If the tool is operator‑facing, add a smoke test (release gate), set smoke_tested=yes in the registry, and ensure the harness invokes it; add a minimal example packet if needed.
3. If the tool output is intended for publication, add a proof obligation (docs/159–164) and a drift firewall.

Related:
- `tools/README.md` (human overview)
- `scripts/check_operator_tools_smoke.py` (operator regression vectors)
