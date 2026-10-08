# Meta: Consumer routing protocol (rev0429)

Use this protocol when a revision introduces or changes a **consumer-facing slice, brief, hint, gate payload, or assistant-facing rendering** of a canonical artifact.

The point is not to standardize one payload for all consumers.
The point is to force each routed view to admit:
- who it is for;
- what decisions it may support;
- what it omitted;
- and when the consumer must escalate.

## Minimum routing card
Every serious routed view should be able to answer:

### 1) Identity
- seam name;
- canonical artifact family;
- routed view name;
- revision / date.

### 2) Consumer class
Choose one primary class:
- reviewer / maintainer;
- CI / automation;
- release / publish;
- security / policy;
- editor / IDE / docs indexer;
- assistant / agent;
- specialist orchestrator;
- or explicitly name another bounded class.

### 3) Allowed decisions
State what this routed view may support:
- explain;
- annotate / warn;
- diff / compare;
- verify / gate;
- package / publish;
- allow / deny / quarantine;
- suggest / escalate;
- or another bounded action family.

### 4) Authority floor
The routed view must preserve at least:
- exact subject identity;
- source lineage or pointer to it;
- freshness anchor;
- explicit partiality / unsupported states;
- and a reference back to the canonical pack.

### 5) Lossiness budget
State what may be omitted and why.
Examples:
- large attachments omitted;
- raw imports hidden but linked;
- only summary deltas shown;
- canonical payload not embedded.

Do **not** omit:
- uncertainty;
- unsupported / fallback states;
- changed authority basis;
- or the path back to stronger evidence.

### 6) Escalation rule
State when the consumer must stop using the routed view and open:
- the canonical pack;
- a verify receipt;
- an attachment;
- a freshness / import record;
- or a human review lane.

### 7) Prohibited conclusions
State what this routed view must **not** be used to conclude.
Examples:
- no publish decision from an editor hint;
- no quarantine decision from a recommendation brief;
- no assistant-only summary treated as canonical diagnosis.

## Default fail-closed rules
Reject a routed view if any of these are true:
- the primary consumer class is not named;
- the decisions supported are broader than the evidence preserved;
- freshness / partiality / unsupported states are omitted;
- escalation is missing;
- or the routed view can be mistaken for the canonical artifact.

## Archive-level default
When in doubt:
- prefer a smaller honest brief over a larger ambiguous one;
- prefer explicit escalation over overclaiming;
- and prefer separate routed views for CI, reviewers, editors, and assistants over one “universal summary”.
