# Deep-read router debt / source-gap audit (rev0356)

## Scope

This audit records a cloudtainer deep read of rev0355 plus targeted external source checks. It is intentionally a control and followthrough revision: it does not add new source rows, route evidence, public-record credit, route scores, or promotion ceilings.

## Mechanical health checked

- `make lint` passed on the incoming rev0355 tree before edits.
- The incoming package had a deterministic, lint-clean release spine, schema validation, negative source-role replay, and package tooling.
- The working tree remains organized around manifest/receipt/status/context surfaces plus executable ledgers and generated mirrors.

## Corrected now

The stable current-head/navigation surfaces retained a historical section titled `Current release identity (rev0330)`. That wording was misleading because the manifest, receipt, status, and top update sections already identify rev0355/rev0356 as the live bundle head. rev0356 retires that heading into historical release-navigation wording in:

- `docs/40-model/current-head-control-router.md`
- `docs/00-meta/trajectory-map.md`
- `ARCHIVE_INDEX.md`

rev0356 also adds lint so fixed-revision `Current release identity (rev####)` headings and stale `Current linked release:` lines cannot reappear in the stable current-head surfaces.

## Severe or wasteful debt found

### Durable-ledger revision churn

`AGENTS.md` says durable ledgers should not be stamped with head revision metadata unless the metadata is operationally meaningful. The executable tooling currently enforces manifest-aligned top-level `revision` fields across registered ledgers. That means a navigation/control revision can force widespread JSON churn in ledgers whose scientific rows did not change. This is useful for the current generated audit, but wasteful for long sessions and noisy for review. The queued fix is not deletion; it is a split between manifest-owned bundle identity and row-local provenance/change revision.

### Source snapshot custody gap

The archive has strong bibliography/source-role discipline, but it still lacks a compact source-snapshot manifest that records public data-product URL/DOI, retrieval date, checksum/hash where available, license/custody role, row placement, and maximum route-credit cap. This matters most for public data products and likelihood chains, where freshness and replay should not depend on prose memory.

### Frontier-source intake gaps

The deep read found public-frontier pressure lanes that are not yet represented as archive source-pressure rows: ACT DR6 CMB likelihood/power-spectrum products and PTA/nanohertz stochastic-background public results. These should enter only as S0 denominator/watchlist or route-local burden pressure until the relevant route caps, source roles, and snapshot custody are explicit.

### Cloudtainer replay cost

The lint/replay path is healthy but heavy enough to matter during iterative sessions. The incoming lint path spent most time and memory in monolithic archive lint, negative replay, and schema validation. The next performance fix should factor repeated JSON loads/evaluators and add targeted lint subsets, while keeping `make lint` as the release gate.

### Schema permissiveness

Many schemas still allow extra properties or omit `additionalProperties`. This is tolerable for active growth but leaves drift paths open. The safe path is family-by-family tightening after row migration, not a blanket lock that blocks active ledgers.

## Missing next artifacts

1. A source-snapshot/hash manifest for high-value public data products.
2. A revision-stamp decoupling design for durable ledgers.
3. ACT DR6 and PTA/nanohertz-GWB intake rows capped as denominator/watchlist pressure only.
4. A targeted lint mode or cached load layer for cloudtainer iteration.
5. Regression fixtures for stale-currentness wording, not only current linked revision lines.

## Non-promotion boundary

No route score, authority state, promotion ceiling, empirical-delta authority, forecast realization, decision outcome, evidence-unit score, public-record credit, or observed-sector recovery state is promoted by rev0356; this revision only repairs stale currentness wording, adds lint, and records deep-read followthrough.
