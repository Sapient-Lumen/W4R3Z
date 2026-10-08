# 910 — Session audit: release-gate failure, date-context drift, and source-cache debt

**Track:** Shared / Session audit / Release governance

rev0872 is a corrective audit revision. It does not attempt to make the archive a current voter guide, a legal authority package, a certified election system artifact, a public-release authorization, or live-pilot evidence.

## What was missing or wrong

1. **The release gate failed at the track-header check.** The newest six numbered docs, `904` through `909`, used either no track line or an unbolded `Track:` line. `scripts/check_tracks.py` requires an exact `**Track:**` header and requires the label to include `A`, `B`, `C`, or `Shared`. This meant the shipped v871 carrier had a valid manifest but could not pass its own full release gate after extraction.
2. **Several source-review tools still carried stale default dates.** The release context refactor did not reach `tools/release_maintainer_handoff_pack.py` or the source-pressure/current-authority report helpers. Some defaults still evaluated source windows at `2026-06-05` or `2026-06-10` instead of the current archive release date. That can hide near-cliff rows as the session date moves forward.
3. **The release-maintainer handoff had a hidden expired-row double-count bug.** If expired unpinned rows returned, `build_source_triage()` would append the same expired row twice. The current queue is zero, so the bug was latent, but it would make future handoff triage noisy at exactly the wrong time.
4. **Two newer gates were internally out of alignment.** The quarantined-source firewall correctly required state/local source sections to say `official route examples; not current voter instruction`, while the older voter-surface structure checker still required a `Sources (authoritative public examples)` heading. That stale requirement would have pushed docs back toward the risky wording the firewall was designed to prevent.
5. **A verifier-report example and strict-policy fixture were stale for the current revision.** The minimal `PacketVerificationReport` example still carried `tool.version=v869`, and the current-revision strict verification-policy lockfile/receipt pair was missing for `rev0872`.
6. **The archive still lacks a local source-byte cache.** The lockfile has many source commitments and review windows, but this carrier still cannot independently verify third-party bytes unless a separate cache or fetch policy is supplied.
7. **Adopter authority capture is still intentionally missing.** The 70 quarantined state/local rows remain example official routes only. No row has the jurisdiction-specific capture, hash/text digest, responsible office, help route, conflict review, and human approval needed for public-answer promotion.

## What changed in rev0872

- Added exact `**Track:** Shared / ...` headers to docs `904` through `909`.
- Moved stale source-review defaults in the source-pressure/current-authority scripts to `tools/release_context.py`, while preserving `ELECTION_STACK_SOURCE_REVIEW_DATE` as an explicit override for current-date operator checks.
- Updated `tools/release_maintainer_handoff_pack.py` to use the shared release date instead of hard-coding `2026-06-05`.
- Removed the duplicate expired-row append in the handoff source triage builder.
- Added this audit note and a compact machine-readable report at `artifacts/reports/session-audit-release-gate-date-context-rev0872.json`.
- Aligned `scripts/check_voter_facing_surface_structure_minimums.py` with the quarantined-source firewall so safe non-instruction source headings are accepted instead of forcing risky authoritative wording.
- Regenerated the minimal verifier-report packet at `v872` and added the current-revision strict verification-policy lockfile/receipt pair.
- Restored voter-facing family-tail entrypoint coverage in `README.md` and `ARCHIVE_INDEX.md`.
- Minified selected generated JSON reports after semantic checks to keep the 16 MiB size-budget tripwire useful without deleting current no-go evidence.
- Regenerated the current source-pressure, current-authority, adopter-capture, no-go, handoff, and pre-pilot reports at `v872`.

## Current audit posture at this revision

At the `2026-06-12` release-review date, the source-pressure report still shows zero expired rows and zero rows due within 30 days. That is useful, but it is not source correctness. The deeper posture remains:

| Item | Current posture |
|---|---:|
| External-source rows | `1216` |
| Byte-pinned rows | `118` |
| Unpinned rows | `1098` |
| Quarantined state/local rows | `70` |
| Affected public-surface docs with quarantined xrefs | `21` |
| Quarantined xref occurrences in the firewall report | `139` |
| Public-guidance promotions allowed from shipped capture records | `0` |
| Release-gate child steps checked in this session | `146 / 146` |

## What should change next

1. **Source-byte acquisition should become a real lane.** Pick a small number of high-leverage official PDFs/specs and add local byte evidence or recorded fetch transcripts. Do not spend the next turn extending review windows for mutable pages unless an active public surface depends on them.
2. **Select one adopter-shaped jurisdiction scenario.** The archive now has quarantine, capture-matrix, capture-record validation, and wording-firewall pieces. The next useful proof is one complete non-promoting adopter capture fixture with realistic conflict review and human approval fields, still marked synthetic and not public guidance.
3. **Consolidate platform/media/UI doctrine.** The platform media and public fingerprint families are now large enough that new single-surface docs are mostly waste. Future work should merge repeated rules into a smaller normative map plus generated coverage tables.
4. **Keep release-date context centralized.** Any future report or gate that depends on a review date should use `tools/release_context.py` or an explicit operator override. Stale defaults are dangerous because they fail quietly.
5. **Add a verifier lane for report freshness across release dates.** Several checks compare generated outputs to checked-in outputs, but date-aware reports should also assert the top changelog date unless they are historical revision artifacts.

## Speculation from online context

The conservative source-use posture still looks right. Official EAC/EAC-CISA materials emphasize decentralized administration and state/local officials as the primary practical source for voters, so this cube should not transform example jurisdiction routes into national guidance. Recent public reporting also suggests federal election-security support arrangements can change, which makes offline verification, local official routing, and independent source capture more important than broad assumptions about centralized coordination.

Boundary: this audit is maintainer triage. It is not current voter instruction, legal advice, a source-byte cache, source-currentness proof, independent validation, certification evidence, public-release authorization, or live-pilot authorization.
