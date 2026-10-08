# Protocol/measurement boundary event extinction refactor audit

Revision: `rev0350`  
Bundle: `Theory-of-Everything-rev0350-2026.06.10.02.50-protocol-measurement-boundary-event-extinction-refactor.zip`

## Purpose

This pass closes the riskiest unfinished residue from rev0346 through rev0349: small remaining `revXXXX_*note` fields whose content was not cosmetic. The notes encoded source-role exclusions, denominator custody, forecast-runway limits, or current-vs-conditional authority boundaries in high-salience control rows.

## Changes made

- Removed the remaining 79 ad hoc note keys from JSON sources.
- Added 74 typed `source_role_events` for source-bearing residue across acquisition/protocol, public-record carrier, measurement model, systematic uncertainty, calibration traceability, evidence severity, topology, entropy, QRF, causal-set, String/M, Family-B, Family-C, B-mode, cosmology, and GW-runway rows.
- Added 5 typed `authority_boundary_events` for claim-language and credit current-vs-conditional boundaries.
- Added global lint rejection for any future `revXXXX_*note` JSON key.
- Extended source-role validation so any ledger that carries `source_role_events` is dynamically discovered and checked.
- Added authority-boundary drift lint for the normalized claim-language and credit rows.
- Added compact negative replay tests to `make lint`.

## Substantive result

The archive no longer carries old per-revision note keys as machine-source fields. Former note semantics survive only as typed event provenance through `replaces_ad_hoc_keys` and `source_note` values. This preserves history without letting stale note fields become a shadow schema.

The key distinction is now executable:

- denominator and runway records remain denominator, forecast, or route-local handoff custody;
- current-vs-conditional language boundaries remain authority-boundary custody;
- decision nested outcome ceilings remain authority-ceiling custody;
- acquired-support rows, route scores, authority states, and promotion ceilings are unchanged.

## Audit counts

- Old note keys retired in this pass: 79.
- New `source_role_events`: 74.
- New `authority_boundary_events`: 5.
- Old note keys remaining after migration: 0.
- New negative replay cases: 5.

## No-promotion boundary

No route score, authority state, promotion ceiling, evidence-unit source credit, empirical-delta effect, forecast realization state, or decision-experiment outcome was promoted. The refactor changes custody representation and lint coverage only.

## Next risks

The next risky work is not another note migration. It is compression and replay quality:

1. compress generated audits whose pass rows are now too verbose;
2. factor repeated lint helpers without introducing a registry bureaucracy;
3. audit whether conservative `credit_cap` values on source-role events are consistent enough to prevent ambiguity;
4. extend freshness checks so expected source-role event dispositions are checked directly, not only row `source_refs` presence.
