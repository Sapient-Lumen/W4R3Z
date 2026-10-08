# Queues & Prioritization Integrity

**Problem:** In real systems, *waiting is power.* When demand exceeds supply, queue design (and priority overrides) becomes a covert discretionary regime.

**Design target:** make scarcity-handling **legible, receipted, contestable, and seam-safe** without forcing every case into litigation.

This memo defines a portable interface: **Queue & Prioritization Integrity (QPI)**.

Joins: service clocks (`108`), continuity (`109/114`), rule change control (`118`), coercion/exception controls (`112/116`), conflicts/influence (`120`), audit (`130`), sanctions (`131`), complexity budgets (`134`).

---

## Non‑negotiables (minimum viable QPI)

1. **Queue is a governed artifact, not a secret.** Every queue has a public-facing description of *what it is*, *who is eligible*, *what priority rules apply*, and *how decisions can be challenged*.
2. **Position & priority are receipted.** People can prove *what the system believed*, *when*, and *why*.
3. **Priority overrides are bounded.** Overrides must be reasoned, logged, reviewable, and statistically audited.
4. **Seams don’t reset people.** Transfers across agencies/jurisdictions must preserve standing, evidence, and (when applicable) time already waited.
5. **Complexity is budgeted.** Scarcity cannot be used to add hidden steps, unclear requirements, or impossible-proof loops.

---

## Artifacts

### 1) Queue Card (QC-*)
A compact public description of a queue.

**QC fields (minimum):**
- `QC.id`, `QC.scope`, `QC.owner`, `QC.service`
- `QC.eligibility` (who can enter; exclusions)
- `QC.priority_schema_ref` (links to criteria registry)
- `QC.entry_points` (how to enter; evidence ladder)
- `QC.position_semantics` (what “position” means; batch vs continuous)
- `QC.clocks` (service promise/time budgets; joins `108`)
- `QC.contest_lane` (how to challenge; joins `106`)
- `QC.transfer_rules` (non-reset; joins `109/114`)
- `QC.public_metrics` (see below)

### 2) Priority Criteria Registry (PCR-*)
A versioned registry of criteria and weights.

- Criteria must be **versioned** (rule replay: see `118`).
- Each criterion includes: purpose, evidence allowed, bias risk note, and the **appeal standard**.

### 3) Queue Position Receipt (QPR-*)
Issued whenever a person enters a queue or their status changes.

**QPR fields (minimum):**
- `QPR.subject`, `QPR.queue_id`, `QPR.timestamp`
- `QPR.position` (and semantics reference)
- `QPR.priority_class` (and criteria version)
- `QPR.inputs` (what evidence was used; hashes/pointers)
- `QPR.next_review_at` (if applicable)
- `QPR.contest_window` (how long; where)

### 4) Priority Decision Receipt (PDR-*)
Issued when priority classification changes or an override is applied.

**PDR fields (minimum):**
- `PDR.type` = `class_change | override | suspension | deferral`
- `PDR.reason_receipt_ref` (joins decision receipts `106`)
- `PDR.criteria_version`
- `PDR.authorizer` (role/authority) and conflict check (`120`)
- `PDR.review_trigger` (automatic sampling / threshold triggers)

### 5) Transfer Receipt (XFR-*)
When a case moves between queues or institutions.

- must include: carried-over waited time, evidence pointers, and *which ruleset* now governs.
- must enforce the **non-reset rule** unless explicitly justified (with contest lane).

---

## Controls & circuit breakers

### Override limits
- **Hard caps** on override rate per period (per queue and per decision-maker role).
- **Audit sampling**: every override is eligible for review; a minimum sample is automatic.
- **Outlier triggers**: if override rates diverge materially by subgroup, geography, or decision-maker, auto-escalate (joins `105/130`).

### Deadline-miss behavior (anti-limbo)
If service clocks are missed (see `108`), the queue must define one of:
- **auto-approve** (safe cases), or
- **interim protection** (benefit/service continues pending decision), or
- **mandatory escalation** to a higher-capacity lane.

### Impossible-proof breaker
If requirements exceed an evidence ladder (or create loops), trigger **Complexity Incident** (`134`) and provide a temporary alternative proof path.

---

## Minimal publishable metrics (do not overfit)

Per queue, publish at least:
- median and 90th percentile wait time (by priority class)
- breach rate of service promises/time budgets (`108`)
- override rate, plus override audit findings
- transfer counts and transfer-breach rate (non-reset violations)
- contestation volume and reversal rate (signal, not shame)

---

## Scope notes

- **Micro-local (clubs/co-ops):** use QPI to prevent informal favoritism; publish QC + lightweight QPR.
- **Municipal/regional:** QPI is critical for housing allocation, permits, schooling, healthcare access.
- **National:** treat backlog and scarcity as accountable policy outcomes (joins budget/project memos).
- **Global / federated systems:** QPI ensures portability across borders and institutions (joins `109/114/125/127/128`).

---

## Tests (links)

- `107` should include: **T1.25 Queue integrity** (replayable position, bounded overrides, seam continuity, clocked remedies).

