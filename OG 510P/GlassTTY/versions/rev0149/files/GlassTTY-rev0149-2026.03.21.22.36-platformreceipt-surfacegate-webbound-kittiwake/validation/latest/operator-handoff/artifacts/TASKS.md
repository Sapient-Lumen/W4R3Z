# Tasks

This task list is organized around the larger product direction and the concrete artifacts a future implementer will need.

## A. Canon and doctrine

### A1. Adopt the rev0123 canon
- Replace the repo’s top-level strategic framing with the current multi-surface canon.
- Make `README.md`, `STATUS.md`, `ROADMAP.md`, `TASKS.md`, `TASK_QUEUE.md`, `PROJECT_MAP.md`, `AGENTS.md`, and `DECISIONS.md` the first source of truth.
- Acceptance idea: a new implementer can explain the product and the next work from top-level docs alone.

### A2. Lock design principles
- Use `docs/design-principles.md` as the check against accidental drift in project shape.
- Acceptance idea: new features can be defended against explicit principles instead of vibes.

### A3. Separate canon from history
- Preserve historical handoff docs, but stop forcing future implementers to derive strategy from them.
- Acceptance idea: no new strategic idea should live only in a handoff file.

## B. Shared vocabulary and traceability

### B1. Lock canonical keys
- Keep a stable vocabulary for surface keys, workflow keys, browser lanes, support tiers, drift severities, artifact kinds, and agent modes.
- Record additions in `docs/canon-keys.md` before using them casually elsewhere.
- Acceptance idea: docs stop inventing synonyms for the same system noun.

### B2. Publish the feature traceability map
- Every major feature/theme should tie back to workflows, state families, evidence, release claims, and support records.
- Acceptance idea: future implementers can trace why a feature exists and what it must emit.

## C. Support records and support truth

### C1. Keep one canonical support record per official surface
Required surfaces:
- Claude
- ChatGPT
- Google AI Studio
- Grok
- Kimi
- Z.ai

Each record should include:
- metadata and lane scope
- workflow rows against the shared vocabulary
- evidence posture
- known caveats and blockers
- promotion requirements
- next high-value capture or implementation step

Acceptance idea:
- every official surface has one current support record in-tree under `docs/support-records/`.

### C2. Backfill the first formal Claude support record
- Use current artifacts to convert Claude from “reference adapter in spirit” to “reference adapter with one dated support record.”
- Acceptance idea: at least one Claude browser lane has workflow rows with named evidence refs.

### C3. Start support-record lifecycle discipline
- Record when support records are seeded, backfilled, updated, promoted, demoted, or made stale.
- Acceptance idea: support records are living operational docs instead of static placeholders.

### C4. Choose the second adapter implementation target
- Use `docs/second-adapter-decision-frame.md` instead of informal defaulting.
- Acceptance idea: `DECISIONS.md` records the choice, scoring logic, and intended first workflow proof.

## D. Shared workflow contract

### D1. Lock the minimum shared workflow set
The first support baseline across official surfaces should be:
- surface-detect
- receiver-resolve
- composer-read
- composer-write
- turn-submit
- generation-read
- latest-turn-read
- support-capture

Acceptance idea:
- every support record explicitly reports status for those workflows.

### D2. Define workflow success and failure language
- For every workflow, document inputs, preconditions, success signals, degradation cases, evidence outputs, and common failure classes.
- Acceptance idea: future implementers can test workflows without inventing their own criteria.

### D3. Use workflow proof templates
- Every serious workflow proof run should leave a concise structured record.
- Acceptance idea: later support promotions can cite named proofs instead of memory.

## E. Structured state API

### E1. Define state families and field levels
Write stable docs for:
- session
- surface
- receiver
- composer
- generation
- conversation
- turn
- selection
- diagnostics
- support
- evidence
- action outcome

Acceptance idea:
- the docs distinguish required fields, optional fields, nullability, and invariants.

### E2. Map current outputs into the state model
- Identify which existing bridge/probe/doctor/readiness outputs correspond to state families and which are still one-off diagnostics.
- Acceptance idea: future implementation can evolve the current system rather than restart blindly.

### E3. Define action→outcome semantics
- Every meaningful write/submit/control action should have a structured outcome object with target, attempt, result, reason, and artifact pointers.
- Acceptance idea: future agent work has a stable execution report contract.

## F. Drift and evidence

### F1. Reframe fixture-lab as part of the drift program
- Fixtures are not only for debugging selectors; they are baselines for support truth and adapter maintenance.
- Acceptance idea: the docs explain how fixture-lab, probe captures, support bundles, comparison bundles, and ledgers fit together.

### F2. Lock drift severity language
Suggested severities:
- informational
- low-risk
- degraded
- blocking
- unknown

Acceptance idea:
- support reports can classify drift without collapsing immediately to “broken” or “fine”.

### F3. Define evidence families and naming rules
- state snapshot
- probe capture
- fixture capture
- smoke run
- support bundle
- workflow proof
- operator handoff
- operator attempt
- comparison bundle
- release-gate artifact
- drift report
- support update

Acceptance idea:
- every support claim points to at least one named evidence family with stable naming conventions.

### F4. Use the drift triage playbook
- Treat drift detection as an operating loop: detect → classify → compare → choose next action → update support truth.
- Acceptance idea: a broken run yields a clearer next action than “inspect manually.”

## G. Release gates and rollout

### G1. Define promotion and demotion gates
- Clarify what moves a workflow from investigated → experimental → provisional → supported and what forces a tier downward.
- Acceptance idea: “supported” means something operational and inspectable.

### G2. Build the first per-surface baseline plan
- Record the first capture plan and next support-capture action for every official surface.
- Acceptance idea: rollout is based on repeatable evidence collection instead of memory.

### G3. Add release-claim traceability
- Every support claim should point to gate artifacts, workflow proofs, and record updates.
- Acceptance idea: release truth is auditable from docs alone.

## H. Agent mode

### H1. Define operating modes
- human-piloted
- assisted
- approval-required agent
- bounded autonomous agent

Acceptance idea:
- future work can add agent behavior without weakening visible operator control.

### H2. Define the autonomy ladder
- spell out which actions, loops, approvals, evidence outputs, and stop conditions belong to each level.
- Acceptance idea: local/private LLM use expands by level, not by unbounded enthusiasm.

### H3. Require execution reporting
- every agent-capable action or loop should leave an action plan or execution report.
- Acceptance idea: autonomous behavior is inspectable after the fact.

## I. Immediate implementation-facing tasks

1. adopt the rev0123 doctrine docs and templates
2. backfill one formal Claude support record from existing artifacts
3. lock the second concrete adapter target with the decision frame
4. publish the shared workflow catalog, acceptance checklists, and state contract as stable canon
5. map current evidence lanes into the support-truth model and ledger schema
6. seed baseline capture plans for all official surfaces
7. publish promotion/demotion guidance and support-record lifecycle discipline
8. create one first cross-doc vocabulary audit to remove drift
9. create one first workflow proof and one first support-record update from real artifacts
