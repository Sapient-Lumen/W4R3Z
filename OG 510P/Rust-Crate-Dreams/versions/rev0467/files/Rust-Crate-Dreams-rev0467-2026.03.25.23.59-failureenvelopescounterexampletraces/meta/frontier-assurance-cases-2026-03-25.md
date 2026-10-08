# Frontier assurance cases — 2026-03-25

This note keeps the frontier broadly stable **while making traceable justification first-class**.

The archive no longer needs more sector inflation.
It needs sharper answers to:
- what exactly is being claimed,
- which witnesses support that claim,
- what warrant turns those witnesses into the claim,
- which challenges remain open,
- and how a new case inherits or supersedes an old one.

## Main judgment

The strongest missing Rust contributions are still mostly **receiver-facing control-plane kits**.
But many of the leading lanes should now be planned as shipping **assurance cases / claim catalogs / witness bundles** rather than only renewal loops, review packets, or delta summaries.

## Assurance-leverage board

### 1. P-0509 + P-0536 + minimal P-0535
**Role:** decision / knowledge / recommendation assurance front door

Why first under this lens:
- it is where another team most directly consumes a claim such as “prefer crate X for this profile” or “this support posture is adequate for review”;
- it already imports evidence, conformance, policy, review, renewal, and delta layers;
- and it is the natural place to expose decisive witnesses, warrants, exceptions, and non-claims in one bounded packet.

What the crate should provide:
- `claim-catalog.json`,
- `assurance-case.json`,
- `witness-bundle.json`,
- `challenge-register.json`,
- `assurance-summary.md`,
- and `non-claims.md`.

### 2. P-0472 + P-0484
**Role:** witness and basis-supplier ring

Why second:
- docs.rs metadata, build metadata, rustdoc JSON, and downloadable docs archives make witness-grade support facts increasingly importable;
- target support and hosted docs behavior give clear witness material for bounded claims;
- but shared warrant and challenge semantics should stay above the raw import layer.

What the crate should provide:
- witness receipts,
- basis-to-claim trace links,
- scope and freshness annotations,
- and explicit “witness present but insufficient for claim” outcomes.

### 3. P-0431 + P-0496 + P-0125
**Role:** inheritance / supersession / route-continuity ring

Why third:
- inherited claims are most fragile where registries, mirrors, advisories, public boundaries, or inventory routes change;
- this ring is the natural place to record whether an assurance case still inherits prior trust, partially inherits it, or must reset;
- and it is the right place to make supersession visible instead of rhetorical.

What the crate should provide:
- inheritance bridges,
- supersession links,
- route-parity challenge notes,
- and explicit “prior case no longer carries” outcomes.

### 4. P-0486
**Role:** debugger-matrix assurance borrower

Why fourth:
- debugging support is highly salient and highly matrix-heavy;
- an assurance case is valuable here because teams need to know exactly which tuple and async scenarios support the claim;
- but the shared witness/warrant vocabulary should be proven in simpler lanes first.

What the crate should provide:
- tuple-scoped claims,
- witness-to-cell trace links,
- async-debug challenge notes,
- and sharply bounded non-claims.

### 5. P-0537
**Role:** iteration and rebuild-cause assurance later

Why fifth:
- build-analysis and relink-don't-rebuild work make build-cause explanation more plausible;
- but the substrate is still moving enough that this lane should borrow the shared case vocabulary rather than define it first.

What the crate should provide:
- causal claims,
- build-cause witnesses,
- and explicit uncertainty when substrate movement weakens the case.

### 6. P-0538
**Role:** scenario-heavy assurance later

Why sixth:
- highly important,
- but scenario maintenance is expensive and should inherit a proven claim/witness/challenge discipline rather than invent one first.

## Why the broad frontier still stays stable

This assurance lens still does **not** justify resetting the archive toward giant umbrella frameworks for web, GUI, game, ML, or local-first work.
Those sectors may still have unmet needs, but the sharper cross-domain missing value is usually:
- explicit claims,
- named witnesses,
- reviewable warrants,
- visible open challenges,
- and clean supersession / inheritance.

That is why the archive still prefers control-plane kits above broad sector reinventions.

## Guardrail

Do not strengthen a lane under the assurance lens unless the pass can name:
1. the **claim**,
2. the **decisive witnesses**,
3. the **warrant**,
4. the **open challenges / non-claims**,
5. and the **inheritance or supersession rule**.
