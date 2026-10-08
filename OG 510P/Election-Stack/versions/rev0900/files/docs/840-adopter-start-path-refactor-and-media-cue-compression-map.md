# 840. Adopter start-path refactor and media-cue compression map

**Track:** Shared / adoption safety / documentation refactor  
**Status:** Current navigation rule as of v839

## Why this exists

The cube has grown enough that the reading path itself can create risk. A careful but overloaded adopter can mistake a long family of highly specific media/authenticity-cue firewall docs for the project’s core readiness story. That is backwards.

As of v839, `docs/START_HERE.md` is deliberately shortened. It points readers to the few live-risk gates first, and routes deep media/authenticity-cue edge cases through this map instead of listing dozens of near-neighbor documents at the top of the archive.

Measured families in this refactor pass are recorded in `artifacts/reports/start-path-refactor-family-counts-rev0839.csv`:

| Family | Count | Default treatment |
|---|---:|---|
| official voter information docs | 286 | Use only after a voter-facing surface is in scope. |
| platform-media docs | 129 | Use only when the evidence object is an official media route or derivative. |
| authenticity-cue docs | 69 | Use as a specialist packet-capture firewall, not as general authenticity proof. |
| authenticity-cue packet-wrapper docs | 52 | Use only when a later packet/slide/PDF/wrapper adds labels, highlights, order, styling, or playback state. |
| release-firewall docs | 36 | Maintainer route only. |
| source-lock/source-review docs | 24 | Maintainer/current-source route only. |
| verifier/verification docs | 28 | Verifier route only; start with `188`, `193`, and `839`. |

## New start-path rule

A first reader should not be sent into the `585–651` authenticity-cue tail unless all three conditions are true:

1. the local question is actually about an official media object or a derivative of one;
2. a captured cue might be overread as source identity, provenance, authority, or absence; and
3. the concise family router (`523`, `524`, `583`, `600`, `652`) did not already answer the question.

## Compression router for media/authenticity-cue work

Use this order:

1. `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md` — decide whether the object is in the platform-media family at all.
2. `docs/524-official-voter-information-platform-media-route-state-lexicon-badge-normalization-and-capture-order-discipline.md` — normalize the route/state/capture vocabulary.
3. `docs/583-official-voter-information-platform-media-stacked-authenticity-cues-identity-context-provenance-ordering-and-non-collapse-firewall.md` — handle stacked cue meanings without collapse.
4. `docs/600-official-voter-information-platform-media-authenticity-cue-detached-derivative-family-quickmap-mixed-packets-and-anti-fragmentation-firewall.md` — handle detached derivatives and mixed packets.
5. `docs/652-authenticity-cue-family-compression-and-promotion-budget.md` — decide whether a new cue doc is justified or whether an existing family router should absorb it.

Only after those should a reviewer use a narrow doc from `585–651`.

## What changed in v839

- `START_HERE.md` no longer lists the authenticity-cue tail inline.
- The top-level path now starts with current source status, live-pilot no-go status, verifier authentication status, and external-review/custody/publication gates.
- The media/authenticity-cue family is treated as a specialist router, not as the archive’s main adoption path.

## What not to delete yet

Do not delete the narrow `585–651` docs in this revision. Some are useful as regression fixtures for capture/derivative ambiguity. The next substantive reduction should demote or merge them through `652` after comparing actual examples against the routers above.

## Go/no-go effect

- Adopter orientation: **GO** through the shortened `START_HERE.md` path.
- Treating a cue, badge, platform label, or wrapper artifact as signer authentication: **NO-GO**; use `docs/839-verifier-authentication-status-boundary-and-hash-only-no-go.md` for the signer-authentication boundary.
- Adding another near-neighbor authenticity-cue doc without a concrete captured example and a failed-router reason: **NO-GO** under the v839 compression rule.
