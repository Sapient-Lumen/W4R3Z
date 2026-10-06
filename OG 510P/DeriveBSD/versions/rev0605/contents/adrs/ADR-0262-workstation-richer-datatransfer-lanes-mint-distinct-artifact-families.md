# ADR-0262: Workstation richer data-transfer lanes mint distinct artifact families

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0261` froze the ordinary workstation `ui.datatransfer.grant` lane as the portable baseline, complete enough to implement, and made richer replay/batching, widened/substituting, collection-like, or otherwise broader transfer lanes RFC-first.

That stop-point still leaves one practical archive-management risk:
**a future richer lane could try to sneak back in by reusing the same `ui.datatransfer.grant` / `ui.datatransfer.receipt` family with one more enum, one more flag, one more top-level field, or one more “special-case” interpretation.**

If that happens, the archive loses the main benefit of freezing the ordinary lane:
portable support/export can no longer tell whether a given `ui.datatransfer.*` artifact is the boring ordinary reviewed transfer floor or a richer authority family wearing the same clothes.

## Decision

For workstation cross-domain transfer:

1. the ordinary `ui.datatransfer.grant` / `ui.datatransfer.receipt` family remains reserved for the frozen ordinary reviewed-transfer baseline.
2. any future richer transfer lane must mint a **distinct artifact family** rather than widening or variant-switching the ordinary one.
3. therefore a richer lane must not be introduced by adding a new transfer-class enum, hidden mode bit, profile-local interpretation, or successor-path special case to the ordinary `ui.datatransfer.*` family.
4. a richer lane must arrive RFC-first with its own schemas, examples, and discovery wiring.
5. joins between the ordinary lane and any future richer lane must be explicit and digest-bound rather than implicit reuse of ordinary grant lineage fields.

## Consequences

- The ordinary workstation transfer artifacts stay boring to decode, support, and export.
- Future richer lanes can still exist, but they must look obviously different at the artifact boundary.
- A/B/C/D can share one small ordinary transfer family without product-local variants quietly changing its meaning.

## Alternatives considered

- **Reuse `ui.datatransfer.grant` with a new mode or class field:** rejected because it reopens quiet baseline growth under a different name.
- **Allow profile-local richer interpretations of the same artifacts:** rejected because profile forks would make detached evidence and support/export ambiguous.
- **Leave the split implicit:** rejected because future archive drift would eventually blur the ordinary and richer lanes back together.

## Related

- `adrs/ADR-0261-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md`
- `docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md`
- `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`
