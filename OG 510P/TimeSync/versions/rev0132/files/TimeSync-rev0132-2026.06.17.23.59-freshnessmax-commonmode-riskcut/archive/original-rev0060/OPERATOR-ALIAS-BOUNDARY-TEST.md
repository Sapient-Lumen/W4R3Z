# OPERATOR-ALIAS-BOUNDARY-TEST

This note tests whether operator-facing request aliases need their own boundary.

rev0052 rejected native request bundles.
It still allowed local presets that lower to explicit item requests.

The remaining question is whether those presets should be left entirely implicit,
or documented as a separate non-protocol boundary so they do not leak into the shared machine-facing surface.

## Question

Do operator-facing aliases deserve a boundary?

Examples of local aliases might be:
- show timing evidence
- show boundary explanation
- show measurement timing context

These are useful phrases for humans.
They are dangerous if they become hidden request semantics.

## Source pattern

The source pattern supports separation, not promotion.

- NTPv5 is explicit that the current specification defines the on-wire protocol and leaves client-side algorithms out of scope; optional behavior is expressed through concrete extension fields, and unsupported or unknown fields are handled at that item level.
- Roughtime keeps requests and responses tag-typed; mandatory tags and registries carry item identity, while unknown tags are ignored rather than interpreted as higher-level operator intentions.
- The PTP Enterprise Profile is profile/configuration-heavy, but it still makes specific choices: default rates, allowed message modes, forbidden options, and a separate management/security discussion. It does not turn operator convenience names into exchange subjects.
- The NTPv5 requirements draft keeps remote monitoring out of the core protocol, even while allowing that separate extension specifications may exist.

The recurring pattern is:
operational and management convenience can exist,
but it should not silently become exchange grammar.

## Smallest answer that survives the pressure

Yes to a thin documentation boundary.
No to a shared alias surface.

The boundary is not a new protocol object.
It is a quarantine rule for human-facing convenience.

Current best rule:

> an operator alias may be documented locally, but the only shared machine-facing request remains the expanded explicit item list.

## What the boundary may contain

A local alias sheet may say:
- alias name
- scope
- explicit expansion
- intended operator use
- non-meaning / limits

Example shape:

```text
alias: show-boundary-explanation
scope: P4 local operations console
expands_to:
  - boundary_context
limits:
  - not a protocol request name
  - not a profile-default requirement
  - no stronger meaning than the expanded item result
```

This is documentation, not a packet grammar.

## Hard rules

### 1. Expansion happens before the shared surface

The shared request surface never receives the alias name.
It receives only explicit item names.

### 2. Item status remains visible

If an alias expands to multiple items, each item still reports its own exposure or response result.
A local UI may summarize after the fact, but it must not hide mixed outcomes.

### 3. Alias names are not interoperable

Two profiles may use the same friendly phrase differently.
That is acceptable only because the phrase is not shared machine syntax.

### 4. Audit may retain aliases only as annotations

Logs may retain the operator-facing name if useful,
but the expanded item list is the accountable representation.

### 5. Aliases cannot upgrade semantics

An alias cannot turn `requestable` into `required`,
`unknown` into present,
or a partial result into a complete result.

### 6. A profile default is not an alias

A profile can require an item by default.
That is a profile rule, not shorthand.

An alias only helps a human ask for or view a set of already named items.

## Why the boundary earns itself

Leaving aliases completely undocumented would not keep the archive smaller in practice.
Operators and tools will still invent names.
Without a boundary, those names are more likely to become informal protocol commitments.

A thin boundary prevents that leakage:
- it acknowledges the human layer
- it refuses a global alias registry
- it keeps the machine surface item-level
- it forces expansion and item-level accountability

This is a reduction move, not an expansion move.

## Non-goals

This boundary does not add:
- native bundle requests
- a shared alias registry
- cross-profile preset names
- alias negotiation
- alias exposure classes
- alias-level response status

It also does not require every profile to publish aliases.
A profile may have none.

## Promotion / retirement discipline

If a local alias starts to recur across profiles,
it does not automatically become a shared alias.

It must first pass the rev0052 native-bundle promotion test:
- exact item set recurrence
- repeated item-level operational error
- all-or-nothing consequence not reducible to members
- stable name across tracks
- no hidden mixed item result

Until then, the alias remains local documentation.

Aliases should also be retired when their expansion becomes misleading.
A stale alias is worse than no alias because it gives operators an easy false confidence path.

## Current archive judgment

Operator-facing aliases do deserve a boundary,
but only a **local documentation boundary**.

The archive now keeps three layers distinct:

1. **profile defaults** — what a profile requires or exposes by default;
2. **operator aliases** — local human-facing conveniences that expand before exchange;
3. **shared requests** — explicit item-level machine-facing request names.

Only the third layer is shared request syntax.

## What this still does **not** settle

This note does not decide:
- whether expanded item lists must always be logged
- whether profile documents should include a standard alias-sheet heading
- whether profile satisfaction needs a compact local marker

## rev0054 follow-on

rev0054 resolves this note's request-lifetime frontier.

Operator aliases may repeat local expansions for a user or tool,
but the ordinary shared request list remains exchange-scoped.
An alias cannot create sticky remote state.
A persistent delivery arrangement would require an explicit lease/subscription surface with item-level results.

## rev0055 follow-on

rev0055 resolves this note's response-result frontier.

Alias expansion remains accountable because negative results are item-level:
- a returned item satisfies only that item
- `unavailable`, `unknown`, and `omitted` attach to explicit item names
- an alias summary may not hide mixed outcomes

## rev0056 follow-on

rev0056 resolves this note's required/default absence frontier.

Alias names still cannot change profile satisfaction:
- a profile-required item omitted after alias expansion remains missing
- a local alias summary may not display full satisfaction when an item-level requirement failed
- fallback must be profile-defined and weaker than full satisfaction

## Next useful move

Test the profile-conformance marker rather than alias-level status.
