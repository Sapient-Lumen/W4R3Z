# Audit — rev0162

## Scope

This audit examined whether rev0161's single comparative scenario could be replicated without allowing block selection, late assignment, outcome-informed later execution, context reuse, or ambiguous recovery. It also reviewed the experimental code surface for duplicated implementations, child-path substitution, report-export hazards, and model-facing legibility.

## Findings and dispositions

### A-162-01 — no parent custody for a replicated study

**Severity:** high research-validity gap  
**Disposition:** fixed

Rev0161 could run one four-cell block but left block roster, order, repeated invocation, inclusion, and aggregate reporting to manual glue. Rev0162 adds a strict two-to-128-block plan, private schedule, parent state machine, and deterministic rater-level report.

### A-162-02 — lazy replicate creation would permit result-conditioned selection

**Severity:** high selective-reporting risk  
**Disposition:** fixed within the same-filesystem publication boundary

Every child run, private assignment, and exact clone tree is now staged before the parent path becomes visible. Failure in any child leaves no final bundle.

Residual: a same-host owner can discard the entire unwitnessed bundle before sharing its commitment.

### A-162-03 — hidden assignments could otherwise be generated immediately before use

**Severity:** high treatment-integrity risk  
**Disposition:** fixed

The private schedule fixes one child run ID and assignment seed for every block. Child assignments are materialized and digest-bound during parent publication, not when a block becomes active.

### A-162-04 — sequential per-block unblinding leaks outcomes into later operation

**Severity:** high experiment-contamination risk  
**Disposition:** fixed

Each fully rated child is sealed but remains `ready-to-unblind`. No child report may be produced until every scheduled block is sealed and the parent durably enters `unblinding`.

### A-162-05 — direct child unblind produced a generic topology error

**Severity:** medium diagnosis and recovery risk  
**Disposition:** fixed and refactored

The parent now shares one sealed-child-still-blind predicate across completed-prefix and all-sealed checks. Direct early unblinding emits `scenario-bundle-premature-unblinding` and is not adopted as recoverable cache drift.

### A-162-06 — same-host discarded-run bias had no executable witness gate

**Severity:** high claim-validity risk  
**Disposition:** partially mitigated

A preregistered threshold can block execution until unique operator-supplied external receipt records bind the public commitment. Direct child advancement before the threshold is detected even when it bypasses the parent CLI.

Residual: Lacuna does not validate signatures, timestamps, service identity, locator availability, or the nonexistence of earlier unwitnessed bundles.

### A-162-07 — cross-block context and invocation reuse

**Severity:** high treatment-contamination risk  
**Disposition:** fixed at declaration level

Candidate returns are checked against every retained prior block before child mutation. Full audit rejects repeated declared context IDs or non-null provider invocation IDs anywhere in the bundle.

Residual: a dishonest host can relabel one real context with fresh strings.

### A-162-08 — future-child direct mutation

**Severity:** high order-integrity risk  
**Disposition:** fixed by detection

Pending children must remain pristine until their private ordinal becomes active. Direct dispatch or mutation of a future child makes the parent audit refuse.

### A-162-09 — active-child direct transition can leave parent cache stale

**Severity:** medium crash/adapter interoperability risk  
**Disposition:** narrowly recoverable

`recover` may adopt only a valid transition in the sole active child and regenerate parent status/pointer. It does not manufacture content or adopt future-child contamination.

### A-162-10 — partial all-child unblinding after process interruption

**Severity:** high duplicate/re-randomization risk  
**Disposition:** fixed

The parent records an `unblinding` phase and fixed timestamp before child report construction. Completed child reports are adopted idempotently; retries continue from retained state and publish the same aggregate.

### A-162-11 — child directory substitution through symlink

**Severity:** high path-authority risk  
**Disposition:** fixed

Every child directory is resolved as a contained, non-symlink sidecar member. Replacing a future child with a link to another run is refused before interpretation.

### A-162-12 — incomparable ratings could be aggregated

**Severity:** high inference risk  
**Disposition:** fixed

Plan validation requires exact equality of rating scale, prompts, dimensions, and required rater count across blocks.

### A-162-13 — failed and refused cells were not both represented in aggregate counts

**Severity:** medium reporting-validity risk  
**Disposition:** fixed

Condition summaries now retain separate `completed`, `refused`, and `failed` counts. No terminal status is silently merged or dropped.

### A-162-14 — report references trusted manifest digests rather than reconstructed objects

**Severity:** medium custody risk  
**Disposition:** fixed

The aggregate report derives commitment and witness artifact digests from the fully validated retained objects, not merely from cached manifest references.

### A-162-15 — CSV formula interpretation

**Severity:** medium operator-surface risk  
**Disposition:** fixed for the convenience export

Rater comments and stratum labels can be adversarial text. CSV export now prefixes formula-leading values before spreadsheet import. Canonical JSON remains unchanged.

### A-162-16 — duplicated half-built experiment modules

**Severity:** medium maintenance and model-legibility risk  
**Disposition:** fixed

Two competing draft implementations were removed. Shared clone, sidecar, and staged-child primitives are retained under the single scenario/bundle architecture.

### A-162-17 — witness overflow was detected only after publication

**Severity:** medium fail-before-mutation violation  
**Disposition:** fixed and refactored

The full audit already rejected more than 64 witness references, but the append path could write a 65th file and manifest before that late refusal. One shared `MAX_BUNDLE_WITNESSES` constant now governs plan validation, append preflight, audit, and public schemas. The 65th receipt refuses before any sidecar member or manifest byte changes.

## Refactor review

The audit retained one child scenario engine and one parent bundle engine. Clone construction, private directory creation, sidecar member containment, immutable artifact publication, and child staging are shared rather than copied. The parent topology check now centralizes the seal-before-unblind predicate. Public schema names, CLI verbs, operator vocabulary, and `NEXT.md` use one term: **scenario bundle**.

## Negative and recovery tests

Rev0162 adds coverage for:

- atomic precreation of every child and hidden assignment;
- public commitment omission of condition mappings;
- schema validation of all emitted bundle artifacts;
- witness threshold refusal and direct-child witness bypass detection;
- complete seal-all-before-unblind lifecycle;
- direct premature child unblind detection;
- cross-block context reuse refusal before child mutation;
- future-child direct advance detection;
- permitted active-child cache recovery;
- interrupted multi-child unblinding and exact resume;
- failed staging with no visible parent;
- child-directory symlink substitution;
- incomparable rating contract refusal;
- witness-threshold boundary and fail-before-mutation overflow refusal; and
- spreadsheet-formula neutralization in CSV.

## Residual risks

- Parent and child operations are cooperative filesystem protocols, not hostile-user confinement.
- A direct child mutation can be detected after the fact but not undone.
- Witness and provider metadata remain declarations unless independently verified.
- Semantic method leakage, rater collusion, and model memory sharing are outside byte-level custody.
- No statistical analysis, power calculation, rater reliability model, or multiplicity policy is implemented.
- A registered block can be badly designed; preregistration preserves the design rather than certifying it.

## Acceptance judgment

The implementation is suitable for preregistering and operating a small replicated comparative study without manually joining children or exposing earlier condition outcomes to later execution. It materially strengthens the proposed gift to Gwern because it can retain a null or negative result and makes several experiment-level retcons detectable. It remains an instrument, not a completed study or proof that Lacuna improves fiction or science.
