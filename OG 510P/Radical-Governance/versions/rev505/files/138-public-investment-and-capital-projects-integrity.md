# 138 — Public Investment & Capital Projects Integrity

**Stack relation:** use `304-public-capital-assets-and-infrastructure-resilience-routing-guide.md` for the canonical route across the public-capital / assets / infrastructure-resilience family. This memo is the large-project integrity / change-order / benefits-realization specialization; `97` is the broad capital-allocation / stage-gate front door; `225` handles maintenance and lifecycle-planning discipline; `48` is the asset-register substrate; and `154` / `59` remain the resilience and cyber-continuity neighbors. `302` remains the fiscal-state neighbor when the real question is broader budget architecture.

**Purpose:** prevent large projects (infrastructure, IT, procurement-heavy programs) from becoming a *capture + waste machine* by making commitments, changes, and outcomes **legible, gated, and contestable**.

This memo treats “big projects” as a recurring governance failure mode: optimism bias, strategic misrepresentation, procurement gaming, change-order capture, and benefit drift. See: [BIB-WB-PIM], [BIB-OECD-INFRA-GOV], [BIB-FLYVBJERG-MEGA], [BIB-UK-IPA-GBP].

## Core primitives (joinable receipts)

### 1) Project Card (PC-*)
A public, versioned card for every material project/program:

- **PC-ID** stable identifier; **PC-VER** version; **PC-OWNER** accountable “one face” (see `132`).
- **Scope:** what is in/out; interfaces and dependencies (`128`).
- **Budget envelope:** cap + contingency rules; funding source link (`110`, `135`).
- **Delivery milestones:** dates + acceptance criteria.
- **Benefit claims:** measurable outcomes + who is served (person-facing).
- **Risks:** top risks + mitigations; *kill criteria* (what would make us stop).
- **Equity/displacement impacts:** if applicable (`136`).
- **Complexity budget:** steps/time/docs for affected people (`134`).

### 2) Stage-Gate Receipts (SGR-*)
Each gate MUST publish a **Stage-Gate Receipt** with:

- decision (advance/pause/stop), reasons, evidence pack pointer,
- updated PC-* diffs (what changed and why),
- assurance status (open findings + who owns closure) (`73`, `130`).

**Default:** no gate receipt → **no spend increase** beyond a small “keep-safe” amount.

### 3) Change Control Receipts (CCR-PI-*)
For scope/budget/schedule changes above thresholds:

- the delta, the initiating cause (unknowns vs. design choice vs. supplier failure),
- who requested/benefits, alternatives considered,
- downstream effects on service standards/time budgets (`108`), and
- whether the change triggers *re-bid / re-competition* safeguards (`110`).

**Anti-capture rule:** repeated change orders to the same vendor over thresholds MUST trigger an independent review + competition analysis.

### 4) Procurement-to-Delivery Link (PDL-*)
Contracts are not just legal artifacts; they are the project’s execution interface.

- Every major contract gets a pointer from PC-* to its contracting record (`110` / OCDS),
- plus performance commitments that map to milestones and acceptance criteria.

### 5) Benefits Realization Receipts (BRR-*)
At defined post-implementation windows (e.g., 3/12/24 months), publish:

- measured outcomes vs. benefit claims,
- user harm signals (complaints, outages, adverse decisions) joined to `107` tests,
- what will be changed as a result (or why not) (`133`).

**Default:** if BRR-* is missing, the project’s *next funding tranche* is blocked (or automatically escalated) unless a continuity exception is logged (`112`).

## Contestability & remedies

- **Standing:** any materially affected person/group has standing to request the evidence pack pointer and to trigger an oversight review where gate/change thresholds are crossed (`106`, `08`).
- **Interim protection:** if a project causes harm (service cutoff, unsafe condition), continuity and time-budget triggers apply (`108`, `109`, `137`).

## Minimal metrics (publishable)

- % of projects with current PC-* and last SGR-* within required window.
- Forecast error: (baseline vs. current) for cost and schedule; by tier.
- Change-order concentration: spend in change orders / total; by vendor.
- Benefit drift: fraction of claimed benefits unmeasured or unmet at BRR-*.
- Audit follow-through: open findings aged > X days (`130`).

## Implementation notes (tight)

- Start with **PC-*** + **SGR-*** for the top 20 spend items; then expand.
- Keep receipts short: one page + pointers; no PDF dumps.
- Treat “unknown unknowns” as a governance signal; update risk and kill criteria, not just budget.

