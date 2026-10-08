# 965 — Cloudtainer source-index compaction, priority source-health second tranche, and no completion by unresolved warning

## One-line thesis

Forward motion in this cloudtainer means closing the warning that is already visible, backfilling the sources that carry the most public-consequence dependency, and refusing to count another registry or docket as completion while generated surfaces and unchecked live sources still carry the risk.

## Why this matters

Rev0766 reduced several oversized generated routes, but `generated/SOURCES.json` still remained the largest generated file and the only file-level warning in the generated-surface audit. That is the archive doing exactly what it critiques: proving maintenance by a partial route while leaving the visible unresolved risk in place.

This revision treats that as the priority. The complete historical source map remains canonical in `sources/source_catalog.json`; the generated source index becomes a current-revision route plus a source-key registry snapshot, counts, and hashes. That keeps machine reproducibility without making every reader and every package carry a second full historical catalog.

## Pattern pack

1. **Finish visible warnings first.** If the audit points to a specific unresolved file, do not open a new policy frontier until the warning has either been closed or explicitly bounded.
2. **Canonical history stays editable; generated routes stay small.** A generated JSON route should not become a second archive when the source catalog is already the historical authority.
3. **Health-source rows beat source-key rows.** A source key says the archive can cite a surface; a source-health row says whether that surface is stable, volatile, supersession-prone, live, or only a historical anchor.
4. **Public-benefit clocks need direct currentness.** Medicaid renewal snapshots, ex parte guidance, Universal Credit migration notices, and appointee/payee guidance are not background doctrine; they affect whether people can keep money, coverage, or representation.
5. **AI transparency records are phase surfaces, not safety certificates.** GOV.UK Chat, DfE Correspondence Drafter, Redbox, ICO ICE360, and DWP Whitemail entries must be treated as live or change-prone records that need source-health cadence.
6. **Supplier-platform pages are implementation evidence only at the boundary.** NHS Federated Data Platform contract/privacy pages, ArriveCAN privacy summaries, and LA homelessness-transition pages show architecture and authority; they do not prove exit, handback, user remedy, or outcome repair.
7. **Redress and audit rows are repair clocks, not closure.** Robodebt, Horizon, ERC, and public audit records should trigger claimant-tail, evidence-tail, and recommendation-tail follow-up rather than ceremonial closure.
8. **Soft-law and cross-boundary waists must be checked for supersession.** FATF, Paris MoU, and IHR surfaces can govern behavior through inspection, evaluation, and alert waists even when their current text or implementation posture shifts.

## Corrections shipped

- Refactored `tools/build_sources_index.py` so `generated/SOURCES.json` no longer republishes the full historical note-to-source map. It now carries the current revision source route, full source-key registry snapshot, catalog hashes, and counts.
- Added a `SOURCES.json` generated-surface budget in `tools/lint_archive.py`, with lint checks that the generated route remains scoped to current revision notes and that historical rows remain canonical in `sources/source_catalog.json`.
- Backfilled source-health entries for the second high-priority tranche: Medicaid eligibility snapshot and ex parte renewal guidance; ArriveCAN platform PIA summary; Universal Credit migration notice guidance; GOV.UK Chat and four staff-facing AI transparency records; NHS FDP contract and privacy pages; benefit appointee and SSA payee surfaces; Mar Menor law/decree sources; Robodebt, ERC, and Horizon redress/audit anchors; LA homelessness authority sources; and FATF, Paris MoU, and IHR cross-boundary waist surfaces.
- Updated `GAP-027` as further partially repaired rather than closed, because remaining unchecked source keys and generated package-count pressure still exist.

## Failure modes

- **Completion theater:** closing the issue because the current lint is green while the generated-surface audit still has package-level warnings.
- **Registry displacement:** counting a source key as review when the row has no currentness, volatility, retrieval, and fallback statement.
- **Generated archive duplication:** letting generated JSON re-create the full historical archive and then treating package bloat as inevitable.
- **Live-surface drift:** trusting a live AI record, benefit guidance page, redress dashboard, or cross-boundary standard after its phase, text, or update cycle has changed.
- **Substance deferral:** adding a new domain packet while known currentness and package-risk warnings remain the easiest high-leverage work.

## Audit/refactor result

The targeted refactor removes the last file-level generated-surface warning by replacing historical duplication with a compact current-route index. The archive still keeps complete source history in `sources/source_catalog.json`, and lint now enforces the boundary so `generated/SOURCES.json` cannot silently become a second full catalog again.

The source-health tranche also moves a set of high-dependency live or case-carrying keys out of the unchecked queue. It does not claim the queue is done. It narrows the riskiest unfinished work from “large generated file plus high-priority unchecked rows” to “package-count budget and remaining staged source-health backfill.”

## Operational next move

The next pass should not add a policy docket unless a genuinely urgent missing domain appears. It should either reduce the generated file count/package-level warning or take another source-health tranche from the highest unchecked dependency scores, with priority for live dashboards, rights/benefit pages, volatile AI records, complaint/redress clocks, and sources that appear in current case packets.

## Rule of thumb

No completion by unresolved warning.
