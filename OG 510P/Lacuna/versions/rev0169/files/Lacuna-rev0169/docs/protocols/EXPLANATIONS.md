# Custody explanations

## Question answered

`explain` answers:

> What record is this, where did it enter custody, where did it end, what does it directly reference, what directly references it, and which of those links may this caller see?

It does **not** answer whether a proposition is true, a decision is fair, a clue is sufficient, or a dependency is physically causal.

## CLI

Privileged planner trace:

```bash
./lacuna explain ./stories ast_observed_cup
```

Perspective-safe trace:

```bash
./lacuna explain ./stories ast_observed_cup --agent-id player
```

The target may be an agent, source, claim, relation, cardinality constraint, assertion, world, world assignment, commitment transition, evidence link, consequence link, consequence repair, particle update, particle reconciliation, question, event, or change receipt. IDs must be globally unambiguous; accidental cross-namespace collisions are refused.

## Response shape

```json
{
  "schema": "lacuna.explanation.v1",
  "access": {"mode": "planner", "privileged": true},
  "link_scope": "planner-full",
  "target": {"id": "ast_...", "kind": "assertion", "record": {}},
  "custody": {
    "created_by_event": {},
    "ended_by_event": null,
    "active": true
  },
  "dependencies": [
    {"kind": "claim", "id": "clm_...", "role": "asserts"},
    {"kind": "source", "id": "src_...", "role": "sourced_from"}
  ],
  "dependents": [],
  "nonclaim": "..."
}
```

Links are direct structural custody, capped to a bounded result. They are not recursively expanded and do not constitute a proof.

## Planner access

With no `--agent-id`, the result may include full records, privileged IDs, revision ancestry, raw event payloads, and change custody.

Examples of dependency roles include:

- assertion → claim, assertor, perspective holder, source, superseded assertion;
- relation/cardinality → endpoint or member claims and source;
- world assignment → world, claim, source assertion, commitment source, inherited assignment, revised predecessor;
- commitment transition → assignment and source;
- consequence link → premise assignment, typed dependent, and source;
- evidence link → evidence assertion, target claim, and optional world;
- particle update → evidence factor, complete member update custody, and origin event;
- particle reconciliation → baseline update, included/excluded factors, complete member replay custody, and origin event;
- question → target claim, opener, resolution assertion;
- event → change receipt and actor.

Reverse links include `asserted_as`, `assigned_in`, `constrained_by`, `commitment_history`, `explicit_consequence`, `revised_by`, `used_as_evidence`, and `superseded_by`.

## Perspective access and noninterference

Perspective access is a separate projection, not a planner object with cosmetic redaction.

Allowed targets:

- assertions visible under ordinary assertion visibility;
- questions visible under ordinary question visibility;
- claims visible through any historically visible assertion or question;
- sources visible through any historically visible assertion;
- agents, with metadata removed.

Planner-only targets:

- claim relations and cardinality constraints;
- candidate worlds and assignments;
- commitment transitions;
- evidence links, consequence links, consequence repairs, particle updates, and particle reconciliations;
- events and changes.

Every dependency and dependent is independently checked before inclusion. A visible assertion therefore cannot disclose a hidden world, consequence, constraint, or private assertion merely by returning its ID.

Perspective sanitation also:

- emits safe event envelopes without payload or change ID;
- removes source locator and metadata;
- removes agent metadata;
- nulls an invisible `supersedes_id`;
- nulls an invisible question resolution ID;
- marks `link_scope` as `visible-only`.

A guessed hidden ID is refused rather than confirmed.

## Historical visibility

Ending or superseding a record does not erase that a perspective once saw it. Claims and sources remain explainable through historically visible assertions/questions, while hidden records remain hidden.

## Why this belongs in the kernel

Revision, commitment, clue review, and confidentiality all need trustworthy lineage. Reconstructing it from prose or model memory would recreate the canon-paragraph problem. The kernel exposes recorded custody while naming exactly what it does not prove.


## Consequence repair lineage

Planner explanations treat a repair as its own custody record. The repair depends on its predecessor and successor consequences; the predecessor reports the repair as `replaced_by`, and the successor reports it as `created_by_repair`.

These edges explain why records exist and how they were replaced. They do not assert that the successor is causally or semantically equivalent to the predecessor.

Perspective explanations refuse repair targets and omit repair-linked consequence IDs entirely.


## Particle reconciliation custody

Planner explanations expose a reconciliation as a distinct repair record. Its dependencies identify the baseline update and every included or excluded historical factor; member arithmetic remains available through the planner-only reconciliation query. Reverse links allow an update to show that a later reconciliation included or excluded it.

These edges explain factor disposition and derived-weight custody. They do not certify the likelihoods, factor independence, world adequacy, or posterior truth. Perspective explanations refuse reconciliation and particle-update targets, preventing factor IDs, hidden-world membership, and distribution arithmetic from crossing the context firewall.
