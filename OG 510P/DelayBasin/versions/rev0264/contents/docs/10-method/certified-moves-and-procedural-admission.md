# Certified moves and procedural admission

Status: `speculative but central`

## Core claim

DelayBasin should certify not only **terms** but also **move classes**.
A long-run archive can look coherent while still advancing by bad procedure: silent canon laundering, unsupported promotion, cosmetic summary churn, or untracked drift.
The live hypothesis is that archive continuity improves when some transition types are treated as explicitly **admissible moves** with minimal procedural integrity checks.

This is narrower than claiming formal proof.
It is a claim that “what changed” is not enough; the archive should also preserve **what kind of move this was** and **why it was allowed to count as progress**.

## Why this now belongs in canon

Several DelayBasin lines were already pushing here:

1. **Typed continuation protocol** separated workflow, state, and checks.
2. **Certified core vocabulary** separated trusted terms from provisional handles.
3. **Portable state interface** required bounded state plus deterministic checks.
4. Event-sourced agent architectures argue long-horizon consistency requires immutable, auditable state transitions rather than opaque in-memory drift.
5. Procedure-aware evaluation shows outcome success can conceal bad procedure; task completion alone is not a sufficient metric for trustworthy progress.
6. Verifier-bound and authenticated-workflow work both separate generation from admission and insist that boundary crossings require explicit acceptance semantics.

Taken together, this suggests a stronger archive rule:
**canon should preserve a small registry of certified move classes, and revisions should identify which move class they are instantiating when claiming advancement.**

## Minimal move classes

DelayBasin does not need a giant ontology.
A small starting registry is enough:

- **read / reopen** — re-enter current canon as source of truth;
- **research / cite** — import external pressure without hoarding artifacts;
- **refine / compress** — reduce entropy or clarify an existing surface;
- **quarantine** — keep a risky idea live without laundering it into canon;
- **promote** — move a previously risky or loose structure into canon with explicit wiring;
- **recertify** — confirm that a term, prompt, or surface still deserves trusted status;
- **package / handoff** — emit a compact release object for future continuation.

These are not the only possible moves.
They are the smallest current set that seems sufficient to describe most real DelayBasin progress honestly.

## Procedural admission

A move should not count as archive progress merely because it sounds good.
A certified move should carry at least the checks appropriate to its class.
Examples:

- **research / cite** should name the external pressure and preserve only compact load-bearing trace;
- **promote** should identify what changed status and where the new canonical wiring lives;
- **quarantine** should preserve consequences-if-true and what-would-count-against-it hooks;
- **recertify** should say what remained stable enough to keep trusting;
- **package / handoff** should pass lint and produce a compact bundle.

This is not a demand for bureaucratic ritual.
It is a way to prevent **corrupt success** at the archive level: revisions that look productive while violating the method's own continuation law.

## Archive-native consequences

- DelayBasin should maintain a **move registry**.
- `context-pack.json` should expose the current certified move classes.
- Revision summaries should identify the move classes actually performed.
- Prompt pairs should keep asking for at least one bold move and one hygiene move because those are distinct move classes, not interchangeable prose flourishes.

## What this does *not* claim

- not that every revision needs a formal proof object;
- not that archive work can be reduced to a tiny finite-state machine;
- not that the move registry is complete;
- not that procedural admission alone guarantees truth.

The claim is narrower:
**preserving trusted move classes may reduce archive-level corrupt success and improve faithful continuation.**

## What would count against this

- evidence that move classification adds ceremony without improving re-entry or honesty;
- evidence that revisions remain equally robust when move types are omitted entirely;
- evidence that the same archive quality can be maintained by vocabulary/state controls alone;
- evidence that the registry drifts into empty labeling with no practical discriminatory power.

## Relationship to stronger speculation

A stronger live speculation is that DelayBasin may be evolving toward a kind of **proof-carrying continuation**, where accepted archive moves increasingly need portable evidence objects or attestations.
That stronger ontology remains in quarantine.
