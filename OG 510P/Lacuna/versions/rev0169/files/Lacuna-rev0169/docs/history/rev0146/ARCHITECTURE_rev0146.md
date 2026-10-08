# Architecture — rev0146

## System boundary

Lacuna is an event-sourced epistemic custody kernel with thin entrances for humans and models.

```text
human                           language model / external director
  |                                           |
campaign library                           turn packet
  |                               audience view + optional planner view
selected campaign                              |
  |                                         proposal
  +-------------------+-----------------------+
                      v
            adapter normalization
      aliases + disclosure preflight + source digest
                      |
                JSON change-set
                      v
             validation + refusal
                      |
           immutable event ledger
                      |
          deterministic projections
                      v
 claims | assertions | worlds | evidence | questions
                      |
       context | canon | perspective | unknowns
```

Generation, model hosting, plot scoring, and dramatic policy remain outside the kernel. The turn adapter does not call a model. It provides a contract by which a model or human can propose one mutation.

## Storage layers

### Cube

A cube remains:

```text
cube.json
lacuna.sqlite3
```

`lacuna.sqlite3` owns the immutable event chain, atomic change receipts, and rebuildable projections.

### Campaign

A campaign directory is also a cube and adds:

```text
campaign.json
cube.json
lacuna.sqlite3
```

`campaign.json` names the campaign and records default owner, player, and narrator IDs. It is mutable application metadata, not event-sourced story state.

### Library

A library contains:

```text
lacuna-library.json
campaigns/
  campaign-slug/
    campaign.json
    cube.json
    lacuna.sqlite3
```

The library’s selected campaign is a user-interface preference. Every normal cube-opening CLI command accepts either a cube path or a library path with an active selected campaign.

## Context projection

Rev0146 introduces one authoritative structured context builder. Markdown is now only a renderer over that structure.

Two access modes exist:

- **perspective** — visible assertions, visible questions, visible anchors, and visible tensions for one agent;
- **planner** — privileged assertions, candidate worlds, world-scoped evidence, consensus, and unresolved state.

A perspective context and a named candidate world are mutually exclusive. A director that needs both receives two separately labelled projections in a turn packet. This prevents the renderer from accidentally smuggling hidden-world state into a player packet.

## Turn boundary

A turn packet is bound to the current ledger head. A proposal contains:

- IDs copied from the packet;
- human-facing narration;
- a narration source ID;
- ordered adapter operations;
- assertion IDs declared as revealed;
- an optional message.

Adapter operations may bind an ID with `as` and use sequential `@alias` references. The adapter expands these into strict kernel operations. Built-ins are `@narration`, `@audience`, and `@actor`.

At commit, Lacuna:

1. checks the expected head before mutation;
2. expands aliases and generates explicit IDs;
3. verifies disclosure/source/visibility relationships;
4. prepends an utterance source containing the narration SHA-256 and provenance metadata;
5. applies the complete change-set atomically through the ordinary kernel;
6. returns the narration, receipt, new head, bindings, and latest audience context.

The narration body is not stored in rev0146. The source digest proves which bytes the caller received only if the caller retains those bytes. Lacuna does not prove that the prose semantically entails exactly the declared assertions.

## Invariants added in rev0146

- A perspective packet may not name or expose a candidate world.
- A hidden anchor or privileged consensus may not settle a perspective-visible claim by omission.
- Privileged and audience contexts are separately labelled objects.
- A stale turn cannot add even its narration source.
- Every new audience-visible assertion sourced from narration must be declared as revealed.
- Every newly revealed assertion must cite the narration source and be visible to the named audience.
- Turn-local aliases are sequential; forward or unknown aliases are refused.
- Campaign creation is no-clobber and path-safe.
- Campaign manifests and library configs refuse unknown fields.

## Invariants deliberately not claimed

- Natural-language narration is not semantically verified against the ledger.
- Campaign metadata is not protected by the cube’s hash chain.
- The runtime does not choose candidate worlds, assign posterior weights, or score story quality.
- A narration digest is not a transcript archive.
- A selected campaign or selected world is not canon.
