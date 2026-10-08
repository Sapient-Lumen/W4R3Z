## v900 (2026-06-18)

Release-gate runtime-risk sprint. Refactored the four newest executable evidence checks — primary CDF replay, independent CDF replay, ballot-accounting reconciliation, and election-event-log reconciliation — to run their positive path and negative controls in-process inside the already-isolated release-gate child rather than spawning nested Python interpreters. This keeps the same shipped reports and fail-closed vectors while reducing the CDF/accounting/event hot path from roughly 34 seconds to about 6 seconds in the cloudtainer.

Audit/refactor: added a current runtime-risk note and compacted superseded non-current source-byte, trust-policy, replay, and provenance history into `artifacts/history/rev0900-release-gate-hotpath-history.tar.gz`, with exact original bytes indexed by `artifacts/reports/rev0900-retrievable-history-compaction.json`. This is a release-completion, package-budget, and reproducibility improvement, not a new live-election authority claim.

Boundary: v900 remains synthetic/non-production only; the optimized checks are not live jurisdiction evidence, not full NIST EEL/CDF conformance, not the NIST CDF Test Method, not certification, not outcome proof, not current voter instruction, and not legal advice.

## v899 (2026-06-18)

- Add `tools/election_event_log_reconciler.py` and `scripts/check_election_event_log_reconciler.py`: a synthetic event-chain verifier that digest-binds the Example County BD/CVR/ERR/accounting inputs to the replay report, independent verifier report, CRO, mapping manifest, accounting reconciliation, and public boundary summaries.
- Add `artifacts/examples/example_county_2026_municipal_pilot/cdf/election-event-log-minimal.json`, public event-log boundary, reconciliation report, and negative controls for broken previous hashes, digest drift, timestamp regression, and missing required artifact roles.
- Wire the event-chain check into the release-gate inventory, offline drill, go/no-go decision, maintainer handoff, mission-kernel closeout, current-fixture sweep, and root navigation so chronological provenance cannot lag behind replay/reconciliation outputs.

Boundary: v899 remains synthetic/non-production only; the event-chain verifier is not live Election Event Log evidence, not full NIST EEL/CDF conformance, not the NIST CDF Test Method, not certification, not outcome proof, not current voter instruction, and not legal advice.

## v898 (2026-06-18)

- Move the synthetic CDF replay bridge from contest-only totals to reporting-unit-level reconciliation, so a precinct/unit misallocation cannot pass merely because countywide totals still match.
- Expand the Example County minimal CDF and ballot-accounting fixtures from one precinct/four CVRs to two precincts/six CVRs, preserving synthetic-only boundaries while exercising multi-unit replay.
- Add a total-preserving negative control, `artifacts/test-vectors/cdf-replay/election-results-unit-swap-total-preserving.json`, which fails only if the adapter and independent verifier compare by reporting unit.
- Refresh the primary CDF replay, independent verifier, ballot-accounting reconciliation, go/no-go, handoff, closeout, and fixture-sweep reports for v898.
- Audit/refactor the source-byte history pressure lane by compacting 84 superseded rev0895-rev0897 source-byte/cache reports and workpack files into `artifacts/history/rev0898-sourcebyte-fixture-history.tar.gz`, preserving exact prior bytes while recovering package budget for current executable evidence.
- Audit/refactor the release-risk seam around one-command gate completion: document the contest-only blind spot and the gate-runtime pressure, then keep the current fix executable rather than adding a new registry.

Boundary: v898 remains synthetic/non-production only; reporting-unit CDF replay and ballot-accounting reconciliation are not live custody evidence, not full NIST CDF conformance, not the NIST CDF Test Method, not certification, not outcome proof, not current voter instruction, and not legal advice.

## v897 (2026-06-18)

- Burn down the next riskiest K02/K03 seam by adding `tools/ballot_accounting_reconciler.py`: a synthetic ballot-accounting reconciliation that recomputes reporting-unit CVR counts, contest eligible-ballot counts, selection slots, CVR selection counts, undervote slots, and overvote-record counts from the BD/CVR fixture and compares them to a minimal accounting ledger.
- Add `scripts/check_ballot_accounting_reconciler.py`, `artifacts/examples/example_county_2026_municipal_pilot/cdf/ballot-accounting-minimal.json`, public summary, report, and negative controls for CVR-count drift, undervote drift, and unknown reporting-unit accounting rows.
- Wire the ballot-accounting reconciliation into the canonical release-gate inventory, mission-kernel closeout, release maintainer handoff, go/no-go decision, offline drill plan, current-fixture sweep, and operator navigation.
- Audit/refactor the stale-pack release seam: the uploaded v896 carrier had several non-rev-named no-go packs still carrying v895 archive_version values. Regenerate those packs and expand `scripts/check_current_revision_fixture_sweep.py` so local-pilot, redaction/publication, accessibility/language, custody/provenance, independent-review, adopter-capture, and release-decision packs cannot silently lag the root VERSION again.
- - Audit/refactor doctrine sprawl without losing history: compact eight oversized high-churn navigation/media/research docs into concise current control maps while preserving the original bytes in `artifacts/history/rev0897-doctrine-sprawl-preserved-docs.tar.gz` plus `artifacts/history/rev0897-media-authenticity-minimum-controls-preserved.tar.gz` plus `artifacts/history/rev0897-research-agenda-ledger-preserved.tar.gz` and indexing the recovery in `artifacts/reports/rev0897-doctrine-sprawl-compaction.json`.
Boundary: v897 remains synthetic/non-production only; the ballot-accounting reconciliation is not live custody evidence, not full NIST CDF conformance, not the NIST CDF Test Method, not certification, not outcome proof, not current voter instruction, and not legal advice.

## v896 (2026-06-18)

- Burn down the next riskiest K03/MKB-003 seam after the primary replay bridge by adding `tools/cdf_replay_independent_verifier.py`: a separate stdlib parser/tally path that replays the synthetic BD/CVR/ERR fixture without importing or executing `tools/cdf_export_replay.py`.
- Add `scripts/check_cdf_independent_replay_verifier.py` and require both positive agreement and negative controls: mismatched ERR totals, unknown CVR option identifiers, selection-limit/overvote violations, altered primary comparison rows, and altered CRO vote rows all fail closed.
- Wire the independent verifier transcript into the canonical release-gate inventory, go/no-go decision, offline drill plan, pilot data ledger, current fixture sweep, `docs/START_HERE.md`, and the K03 risk-burndown note.
- Audit/refactor the CDF lane so the minimal-projection mapping manifest and public navigation no longer drift on stale embedded revision text; current v896 artifacts point at rev0896 reports while preserving v895 as historical context.
- Correct current-entrypoint drift in the cloudtainer: `README.md`, `ARCHIVE_INDEX.md`, and `docs/13-artifact-index.md` now identify v896 as the head instead of carrying v895 navigation above v896 evidence.
- Boundary: v896 remains synthetic/non-production only; the independent verifier is not full NIST CDF conformance, not the NIST CDF Test Method, not live jurisdiction export evidence, not external reviewer execution, not certification, not outcome proof, not current voter instruction, and not legal advice.

## v895 (2026-06-18)

- Burn down the riskiest unfinished mission-kernel seam, MKB-003, by adding `tools/cdf_export_replay.py`: a concrete replay bridge that ingests the synthetic Ballot Definition, Cast Vote Records, and Election Results minimal projection fixtures and recomputes published option totals into a schema-clean `CanonicalResultsObject`.
- Add synthetic CDF projection fixtures under `artifacts/examples/example_county_2026_municipal_pilot/cdf/` plus negative controls for mismatched totals, unknown option identifiers, and selection-limit violations under `artifacts/test-vectors/cdf-replay/`.
- Add `scripts/check_cdf_export_replay.py` and wire it into the canonical release-gate inventory, release-gate documentation, go/no-go offline drill, and current go/no-go signal set.
- Refactor the mission-kernel K03 standardized-results-export closeout row from a prose-only CDF promise into executable evidence references: the replay report, canonical results object, mapping manifest, and public CDF replay summary.
- Audit/refactor the retrievable-history lane so compaction is multi-revision instead of v894-bound; compact 112 superseded pre-v895 generated reports, source-byte handoffs, and v894 trust-policy fixtures into an in-carrier deterministic history bundle while leaving current v895 artifacts complete.
- Boundary: v895 remains synthetic/non-production only; the CDF bridge is not full NIST CDF conformance, not the NIST CDF Test Method, not live jurisdiction export evidence, not certification, not outcome proof, not current voter instruction, and not legal advice.

## v894 (2026-06-18)

- Deep-read the full v893 carrier and restate the mission as a portable evidence-and-recovery sidecar: bind, preserve, replay, and recover the seven mission-kernel evidence lanes.
- Correct a critical trust-boundary flaw: a bare SHA-256 digest plus a free-text approving role is now an unauthenticated live candidate, never authenticated live evidence; live promotion requires a signed canonical `EvidenceEnvelope` verified against an external trust profile.
- Harden mission-kernel intake and submission with duplicate-key rejection, source-mode binding, opaque external locators, redaction/boundary consistency, retention and explicit UTC capture requirements, and stable descriptor-based file fingerprinting.
- Add ADR 0005, claim `CLM-040`, strict mission-kernel schemas, negative controls, `docs/932-mission-heart-authentication-boundary-and-cloudtainer-correction-plan.md`, and `artifacts/reports/mission-heart-trust-boundary-audit-rev0894.json`.
- Record and repair the uploaded v893 carrier's stale canonical go/no-go dependency hashes; regenerate current packs in dependency order and seal v894 only through the full gate, manifest write, deterministic ZIP build, and independent ZIP verifier.
- Replace 73 superseded v892-v893 report, policy, and source-byte workpack snapshots with retrievable stubs backed by one deterministic in-carrier history bundle; add a safe single-member recovery tool and retain original bytes rather than another unrecoverable hash-only layer.
- Boundary: v894 remains synthetic/non-production only; it is not live election evidence, certification, outcome proof, current voter instruction, public-release authorization, production signer authority, approval to test live election systems, or legal advice.

## v893 (2026-06-18)

- Add a full mission-kernel non-production drill replay that exercises all seven live-closeout workqueue rows and all 28 required evidence classes through the same operator submitter and intake validator used by the future evidence path.
- Add `tools/mission_kernel_full_drill_replay.py`, `scripts/check_mission_kernel_full_drill_replay.py`, `docs/931-full-mission-kernel-drill-replay-and-intake-boundary-audit.md`, and `artifacts/reports/mission-kernel-full-drill-replay-audit-rev0893.json`.
- Gate the drill on zero local path leaks, zero governed synthetic source locators, zero live evidence objects, zero live-readiness overclaims, and a decision of `DRILL_COMPLETE_NOT_LIVE_READY`.
- Refactor the full replay so it imports `mission_kernel_evidence_submitter.build_submission()` and `mission_kernel_live_evidence_intake.evaluate_submission()` instead of carrying a parallel intake implementation.
- Boundary: v893 remains synthetic/non-production only; full-drill success is not live jurisdiction evidence, live-pilot authorization, certification, outcome proof, current voter instruction, source-byte completeness, public-release approval, or legal advice.

## v892 (2026-06-18)

- Add an operator-side mission-kernel evidence submitter that hashes external records into a submission JSON while refusing governed synthetic-tree paths.
- Add a non-production drill source mode and release check proving a narrow external digest-bound drill can validate without creating live-election evidence or live-pilot readiness.
- Extend the live-evidence intake status with drill counts/statuses while keeping the shipped archive empty, zero-live, and no-go.
- Add a shared MissionKernelEvidenceSubmission schema and register the submitter/check in the release gate, maturity registry, handoff, and go/no-go controls.
- Boundary: v892 remains synthetic-only; drill success is not live election evidence, jurisdiction authorization, certification, outcome proof, current voter instruction, source-byte completeness, or legal advice.

## v891 (2026-06-18)

- Add the mission-kernel live-evidence intake validator and status pack so future jurisdictional closeout submissions must provide digest-bound local records rather than prose assertions or generated synthetic artifacts.
- Add `tools/mission_kernel_live_evidence_intake.py`, `scripts/check_mission_kernel_live_evidence_intake.py`, and `schemas/MissionKernelLiveEvidenceIntake.json`, with the new gate wired into the release inventory, release-maintainer handoff, and go/no-go decision pack.
- Add the deliberately empty Example County intake submission and public intake status: zero live evidence objects, seven missing work items, and decision `NO_GO_NO_LIVE_EVIDENCE_SUBMITTED`.
- Refactor mission-kernel evidence-class, source-mode, boundary, and synthetic-path guard constants into `tools/mission_kernel_common.py` so the live workqueue and intake validator cannot drift.
- Compact superseded v890 generated reports into digest-preserving historical stubs while leaving current v891 reports complete.
- Boundary: v891 remains synthetic-only and does not establish live jurisdiction evidence, current voter instruction, legal reliance, source-byte completeness, public-release authorization, production signer authority, independent validation, certification, or live-pilot readiness.

## v890 (2026-06-18)

- Add the mission-kernel live-closeout workqueue and intake template so the seven v889 blockers become concrete owner-assigned evidence-collection rows instead of a passive gap list.
- Add `tools/mission_kernel_live_workqueue.py`, `scripts/check_mission_kernel_live_workqueue.py`, and `schemas/MissionKernelLiveWorkqueue.json`, with the new gate wired into the release inventory and human gate doc.
- Refactor the live-closeout queue to generate from `tools/mission_kernel_closeout.py` rather than duplicating blocker data, and remove a duplicated `shared_helper` key from the closeout refactor audit.
- Extend the release-maintainer handoff to surface the live-closeout workqueue decision, critical blocker count, intake template, and no-go boundary alongside existing local-pilot, custody, accessibility, and independent-review gates.
- Boundary: v890 remains synthetic-only and does not establish live jurisdiction evidence, current voter instruction, legal reliance, source-byte completeness, public-release authorization, production signer authority, independent validation, certification, or live-pilot readiness.

## v889 (2026-06-18)

- Added an executable mission-kernel closeout pack for Example County that maps the seven mission elements to concrete packet evidence, owner roles, closure tests, and live blockers while keeping the verdict `SYNTHETIC_REPLAY_PASS_LIVE_NO_GO`.
- Refactored Example County packet iteration and verification into `tools/example_county_common.py` so the smoke path, output pack, and mission-kernel closeout share one verifier route.
- Replaced `TBD` owners in the claim and hazard registers with concrete operational owner roles to make the risk surface assignable without asserting live authority or certification.

## v888 (2026-06-18)

- Repair seven independent v887 release-evidence defects discovered by running the archive's own gates rather than trusting the shipped carrier status.
- Bind the full semantic gate, final manifest write, deterministic ZIP build, and independent ZIP verification under one single-instance lock through `scripts/release_gate.py --write-manifest --build-zip ABSOLUTE_PATH`.
- Add `docs/926-mission-kernel-release-gate-closure-and-sprawl-reset.md` and `artifacts/reports/mission-kernel-deep-audit-rev0888.json`, defining the seven-part mission kernel and a concrete sprawl/adoption reset.
- Recenter root navigation on election definition, ballot accounting/custody, standardized results, audit/recount, authenticated notice, independent verification, and dispute closeout rather than the latest source-byte maintenance lane.
- Record the v887 carrier failure in the known-issues registry without making any outcome-effect or malicious-cause claim.
- Compact 25 superseded v886-v887 generated reports into digest-preserving in-place summaries, recovering 324,640 gross bytes while leaving current v888 reports full and gate-readable.
- Boundary: v888 remains synthetic-only and does not establish current voter instruction, legal reliance, source-byte completeness, public-release authorization, current state/local authority, production signer authority, independent validation, certification, or live-pilot readiness.

## v887 (2026-06-13)

- Add `scripts/build_source_byte_operator_workplan.py`, `scripts/check_source_byte_operator_workplan.py`, and `artifacts/reports/source-byte-operator-workplan-rev0887.json` so the DNS-blocked source-byte lane now has a current, finite outside-cloudtainer execution plan and cache-return receipt path.
- Add `tools/source_byte_workpack_common.py` plus `scripts/check_source_byte_workpack_common.py`, then refactor the host-slice and attempt-workpack builders onto shared strict `.sha256` parsing so unsafe names, duplicate lines, duplicate local filenames, empty workpacks, and unpinned entries cannot diverge across handoff surfaces.
- Refresh current source-byte queue, intake, batch, host-slice, DNS, attempt-workpack, follow-up, operator-workplan, current-fixture, no-go, handoff, and Example County outputs for `v887` while preserving the honest count: 118 pinned source-byte rows, 13 valid receipts, and 105 receipt-missing rows.
- Add `docs/925-source-byte-operator-workplan-and-workpack-parser-refactor.md` and `artifacts/reports/risk-priority-forward-motion-rev0887.json` to record the v887 risk burn-down, concrete next commands, and remaining no-go posture.
- Boundary: v887 remains synthetic-only and does not establish current voter instruction, legal reliance, source-byte cache completeness, public-release authorization, current state/local authority, production signer authority, independent validation, certification, or live-pilot readiness.

## v886 (2026-06-13)

- Begin source-byte acquisition completion work by attempting exact-SHA-256 batch01 host-slice fetches against an external cache, writing only receipt/report metadata into the release archive and never bundling third-party bytes.
- Add retry classification and host-slice attempt summarization so unresolved source-byte work can be divided into matched, mismatch, transient, not-found, and operator-review buckets instead of one undifferentiated missing-receipts queue.
- Add a current risk-forward report and documentation capturing the v886 source-byte completion delta, remaining no-go posture, and next executable handoffs.
- Boundary: v886 remains synthetic-only and does not establish current voter instruction, legal reliance, source-byte cache completeness, public-release authorization, current state/local authority, production signer authority, independent validation, certification, or live-pilot readiness.

## v885 (2026-06-13)

- Add `scripts/build_source_byte_batch_host_slices.py`, `scripts/check_source_byte_batch_host_slices.py`, `artifacts/reports/source-byte-batch-host-slices-rev0885.json`, and host-scoped batch01 `.sha256` slices so the first unresolved source-byte batch can be run by same-host workpacks instead of a single mixed-host command.
- Refactor duplicated source-byte priority ordering into `tools/source_byte_priority.py` and route the acquisition queue, intake manifest, and external-cache receipt scanner through the shared policy.
- Refresh current source-byte batch/intake/status/follow-up surfaces for `v885` while preserving the honest counts: 118 pinned source-byte rows, 13 valid receipts, and 105 receipt-missing rows.
- Boundary: v885 remains synthetic-only and does not establish current voter instruction, legal reliance, source-byte cache completeness, public-release authorization, current state/local authority, production signer authority, independent validation, certification, or live-pilot readiness.

## v884 (2026-06-13)

- Add resumable source-byte batch follow-up tooling so partial fetch/cache attempts can be converted into a strict next `.sha256` handoff for only unresolved rows, without network I/O or bundled third-party bytes.
- Extend the network-capable batch fetcher with source-id include/skip filters so operators can route around one bad host or large file without hand-editing governed batch files.
- Add current `v884` source-byte batch/follow-up reports and gate coverage so batch01 remains executable, resumable, and current with `VERSION` rather than only documented.
- Refactor the source-byte operator surface around finite next actions: acquisition queue now exposes the current batch fetch template and the follow-up template, reducing one-off operator spelunking.
- Add `docs/922-source-byte-resumable-batch-followup-and-fetch-filter-refactor.md` and `artifacts/reports/risk-priority-forward-motion-rev0884.json` to record the substance-first risk work and remaining no-go boundary.
- Boundary: v884 remains synthetic-only and does not establish current voter instruction, legal reliance, source-byte cache completeness, public-release authorization, current state/local authority, production signer authority, independent validation, certification, or live-pilot readiness.

## v883 (2026-06-13)

- Add `scripts/fetch_source_byte_batch.py` and `scripts/check_source_byte_batch_fetcher.py`, giving the first incomplete source-byte batch a network-capable, exact-SHA-256 receipt path while preserving the no-bundled-third-party-bytes release boundary.
- Refactor `tools/atlas_urp_generator.py` from an empty-payload prototype into a fail-closed RIPE Atlas request-draft generator: dry-run emits a non-empty payload, and active measurement creation requires explicit operator review.
- Refactor `tools/ooni_corroborator.py` so the default path is no-network, schema-shaped, supplementary-only output that records pointers and bounded summaries rather than embedding raw measurement bodies.
- Add `scripts/check_measurement_tool_boundaries.py` and wire both new checks into the release-gate step inventory and pipeline documentation, so the source-byte batch fetch path and measurement-helper safety boundaries cannot silently regress.
- Add `docs/921-priority-risk-source-byte-batch-fetch-and-measurement-refactor.md` and `artifacts/reports/risk-priority-forward-motion-rev0883.json` to record the substance-first risk reduction, remaining at-risk work, and next executable source-byte move.
- Compact stale non-current generated report row bodies into `artifacts/reports/rev0883-stale-generated-report-compaction.json`, preserving original SHA-256 digests and summary counts while keeping current `v883` reports full and gate-readable.
- Boundary: v883 remains synthetic-only and does not establish current voter instruction, legal reliance, source-byte cache completeness, public-release authorization, current state/local authority, production signer authority, independent validation, certification, or live-pilot readiness.

## v882 (2026-06-13)

- Add `docs/920-deep-read-gap-map-cloudtainer-waste-and-correction-plan.md` and `artifacts/reports/deep-review-gap-map-rev0882.json` to record the session deep read, missing evidence lanes, cloudtainer DNS/source-byte constraints, numbered-doc range gap, and waste-reduction plan.
- Keep the canonical release ZIP policy explicit: stored entries are intentional for deterministic verification; compression belongs in a future governed sidecar, not a silent canonical artifact change.
- Fix the generated artifact-index revision matcher so `v882` resolves to `rev0882` current reports instead of silently omitting zero-padded current artifacts.
- Refresh current source-byte batch/intake/status reports and current-revision fixtures for `v882` without fabricating source-byte receipts or bundling third-party bytes.
- Compact stale non-current source-byte and trust-policy history into `artifacts/reports/rev0882-deep-read-history-compaction.json`, preserving original digests while keeping current `v882` gates full.
- Boundary: v882 remains synthetic-only and does not establish current voter instruction, legal reliance, source-byte cache completeness, public-release authorization, current state/local authority, production signer authority, independent validation, certification, or live-pilot readiness.

## v881 (2026-06-13)

- Add `scripts/build_source_byte_cache_batch_status.py`, `scripts/check_source_byte_cache_batch_status.py`, and `artifacts/reports/source-byte-cache-batch-status-rev0881.json` so source-byte receipts, the acquisition queue, and per-batch sha256sum handoffs have a current joined progress report.
- Extend the release-gate source-byte lane so receipt-present sources cannot remain in receipt-missing batch files, receipt-missing sources cannot fall out of the batch handoff, and the first incomplete batch is explicit.
- Extend the current-revision fixture sweep to include the batch-status report, reducing the risk that source-byte operator handoffs lag behind `VERSION`.
- Compact historical row-heavy source-byte cache reports into digest-preserving summaries so current source-byte completion evidence stays within the tracked-byte budget.
- Refresh current source-byte reports, strict verification-policy fixtures, PacketVerificationReport examples, Example County outputs, no-go packs, handoff packs, and firewall reports for `v881`.
- Boundary: v881 remains synthetic-only and does not establish current voter instruction, legal reliance, source-byte cache completeness, public-release authorization, current state/local authority, production signer authority, independent validation, certification, or live-pilot readiness.

## v880 (2026-06-13)

- Add selected-batch resume mode to `scripts/source_byte_receipts_from_cache_batch.py` via `--batch-file`, so receipt writing can be limited to one strict sha256sum batch instead of scanning the whole receipt-missing queue.
- Add `scripts/check_source_byte_cache_batch_resume.py` and `artifacts/reports/source-byte-cache-batch-resume-rev0880.json`; the gate proves batch01 readiness without inspecting release-local cache bytes, then smoke-tests that exact-match bytes outside the selected batch do not become receipts.
- Extend the current-revision fixture sweep to include the selected-batch resume report, reducing the recurring stale-fixture problem around rev-specific source-byte artifacts.
- Refresh current source-byte intake, batch manifests, batch-ingest readiness, strict verification-policy fixtures, PacketVerificationReport examples, Example County outputs, handoff packs, no-go packs, and firewall reports for `v880`.
- Compact historical pre-pilot ledger rows into `artifacts/reports/rev0880-prepilot-ledger-history-compaction.json`, preserving original CSV digests and removed-row canonical digests while keeping current `v880` no-go evidence rows in the registries.
- Boundary: v880 remains synthetic-only and does not establish current voter instruction, legal reliance, source-byte cache completeness, public-release authorization, current state/local authority, production signer authority, independent validation, certification, or live-pilot readiness.

## v879 (2026-06-13)

- Add `scripts/build_source_byte_cache_batch_manifests.py`, `scripts/check_source_byte_cache_batch_manifests.py`, `artifacts/reports/source-byte-cache-batch-manifests-rev0879.json`, and six current-revision batch `.sha256` files so the receipt-missing pinned-source queue can be processed incrementally instead of as one 105-file handoff.
- Extend the release-gate source-byte lane so batch files must reconstruct the master intake manifest exactly, cover each missing receipt once, stay current with `VERSION`, and retain the no-network/no-bundled-bytes/no-public-guidance boundary.
- Extend the current-revision fixture sweep to include the new batch-manifest report and batch-file set, further reducing the repeated stale-fixture drift seen across recent revisions.
- Compact historical current-authority source-queue JSON row bodies into digest-preserving summaries to preserve byte budget for source-cache completion mechanics rather than old generated row dumps.
- Boundary: v879 remains synthetic-only and does not establish current voter instruction, legal reliance, source-byte cache completeness, public-release authorization, current state/local authority, production signer authority, independent validation, certification, or live-pilot readiness.

## v878 (2026-06-13)

- Add `scripts/build_source_byte_cache_intake_manifest.py`, `scripts/check_source_byte_cache_intake_manifest.py`, `artifacts/reports/source-byte-cache-intake-manifest-rev0878.json`, and `artifacts/source_byte_cache_intake/source-byte-cache-missing-receipts-rev0878.sha256` so the remaining receipt-missing pinned sources have a sha256sum-ready external-cache intake manifest instead of only a JSON queue.
- Extend the release-gate source-byte lane so the intake manifest must match the acquisition queue, receipt report, and current batch-ingest candidate count; the checker also proves an empty cache fails as missing bytes and wrong bytes for a real intake filename cannot become a receipt.
- Extend the current-revision fixture sweep to include the intake manifest and sha256sum expectation file, reducing the recurring risk that `VERSION` advances while rev-specific source-byte artifacts lag behind.
- Refresh current synthetic fixtures and reports for `v878`, including the strict verification-policy lockfile/receipt, PacketVerificationReport template/packet, Example County outputs, release no-go packs, and source-byte batch/intake reports.
- Boundary: v878 remains synthetic-only and does not establish current voter instruction, legal reliance, source-byte cache completeness, public-release authorization, current state/local authority, production signer authority, independent validation, certification, or live-pilot readiness.

## v877 (2026-06-13)

- Refactor batch source-byte cache ingest to derive the current report path and release date from shared release context, removing another hard-coded rev-specific drift seam.
- Add a current-revision fixture sweep gate so strict verification-policy fixtures, source-byte batch reports, PacketVerificationReport examples, and Example County synthetic outputs cannot lag behind `VERSION` silently.
- Tighten the source-byte receipt ratchet to the actual current floor: 13 valid receipts and 10,421,893 observed bytes, while still refusing to invent receipts in this DNS-blocked cloudtainer.
- Extend the batch-cache smoke test to prove existing receipts are skipped without `--force`, so repeated operator runs do not overwrite evidence by accident.
- Boundary: v877 remains synthetic-only and does not establish current voter instruction, legal reliance, source-byte cache completeness, public-release authorization, current state/local authority, production signer authority, independent validation, certification, or live-pilot readiness.

## v876 (2026-06-13)

- Add `scripts/source_byte_receipts_from_cache_batch.py` so a network-capable operator can drop externally fetched source bytes into one cache directory and generate every matching `operator_cache_file` receipt in one pass, with mismatches and missing files reported rather than hidden.
- Add `scripts/check_source_byte_cache_batch_ingest.py` and `artifacts/reports/source-byte-cache-batch-ingest-rev0876.json`; the gate proves clean-release readiness without bundling third-party bytes, then smoke-tests a temp lockfile/cache where one file matches and one mismatches.
- Extend the release-gate inventory and `docs/162-release-and-ci-evidence-pipeline.md` so the batch-ingest path is a checked operator lane, not an undocumented helper.
- Refresh current generated reports and fixtures for `v876` while preserving the synthetic-only/no-current-authority boundary.

## v875 (2026-06-13)

- Add `scripts/source_byte_receipt_from_cache.py` so operators can convert an already-populated external source cache into validated source-byte receipts without network I/O or bundled third-party bytes.
- Harden `tools/source_byte_receipt_pack.py` with explicit `observation_type` semantics: legacy/current network receipts are `network_fetch`, while future offline cache observations must be `operator_cache_file` with a verified cache hash-match flag.
- Record `artifacts/reports/source-byte-dns-preflight-rev0875.json`, showing that the next 20 high-impact receipt-missing rows were blocked in this cloudtainer by DNS resolution failure across 8 unique hosts rather than by completed byte acquisition.
- Refactor `scripts/check_version_consistency.py` so root entrypoints cannot lag behind `VERSION` again; v874 had `README.md` and `ARCHIVE_INDEX.md` still advertising v873 despite a current VERSION/CHANGELOG.
- Add `docs/913-offline-cache-receipts-dns-preflight-and-root-entrypoint-drift.md` and refresh README/START_HERE/ARCHIVE_INDEX around the source-byte workflow.
- Refactor release-generated JSON packs to emit compact deterministic JSON where gate checks compare generated bytes, preserving semantic objects while reducing size-budget pressure without post-gate drift.
- Boundary: v875 remains synthetic-only and does not establish current voter instruction, legal reliance, source-byte cache completeness, public-release authorization, current state/local authority, production signer authority, independent validation, certification, or live-pilot readiness.

## v874 (2026-06-13)

- Add `tools/source_byte_acquisition_queue.py`, `scripts/check_source_byte_acquisition_queue.py`, and `artifacts/reports/source-byte-acquisition-queue.json` so the remaining pinned source-byte work is a finite operator queue rather than ad hoc lockfile browsing.
- Require every pinned `evidence/lock/external-sources.toml` row to carry a stable `local_filename`, adding deterministic cache basenames for the remaining 101 pinned rows that lacked one.
- Refactor `scripts/fetch_source_sha256.py` so maintainers can fetch by `--source-id`, optionally populate an external source cache, and emit source-byte receipts without copying third-party bytes into release ZIPs.
- Add `docs/912-source-byte-acquisition-queue-and-cache-basename-firewall.md` to record the cache-basename firewall, current queue counts, and no-promotion boundary.
- Boundary: v874 remains synthetic-only and does not establish current voter instruction, legal reliance, source-byte cache completeness, public-release authorization, current state/local authority, production signer authority, independent validation, certification, or live-pilot readiness.

## v873 (2026-06-13)

- Add `tools/source_byte_receipt_pack.py`, `scripts/check_source_byte_receipt_pack.py`, `artifacts/source_byte_receipts/`, and `artifacts/reports/source-byte-receipt-validation-report.json` to create a concrete source-byte receipt lane without bundling third-party bytes.
- Record 13 valid source-byte receipts across EAC/VVSG, NIST, RFC, and NASEM pinned rows; add `local_filename` hints to those lockfile rows for future external-cache verification.
- Tighten `tools/adopter_capture_record_validator.py` so synthetic records cannot be shape-valid while requesting public-answer promotion, and add an adopter-shaped in-custody route fixture that remains non-promoting.
- Add `docs/911-source-byte-receipts-adopter-shaped-capture-and-size-audit.md` to explain the receipt lane, capture fixture, and remaining no-go boundaries.
- Compact obsolete historical generated CSV row bodies and retain original digests in `artifacts/reports/rev0873-historical-report-size-compaction.json`, saving 161144 tracked bytes for substantive evidence work.
- Boundary: v873 remains synthetic-only and does not establish current voter instruction, legal reliance, source-byte cache completeness, certification, public-release authorization, production signer authority, independent validation, or live-pilot readiness.

## v872 (2026-06-12)

- Fix a real release-gate blocker: docs `904` through `909` now carry exact `**Track:** Shared / ...` headers so `scripts/check_tracks.py` can pass instead of failing immediately after extraction.
- Remove stale release-date defaults from source-pressure/current-authority report helpers and quarantine checks by routing them through `tools/release_context.py`, while preserving explicit `ELECTION_STACK_SOURCE_REVIEW_DATE` operator overrides.
- Refactor `tools/release_maintainer_handoff_pack.py` to use shared release context instead of hard-coding `2026-06-05`, and remove a latent duplicate expired-row append in source triage.
- Add `docs/910-session-audit-release-gate-date-context-and-source-cache-debt.md` and `artifacts/reports/session-audit-release-gate-date-context-rev0872.json` to record the audit, missing source-byte cache, adopter-capture gap, and platform-sprawl waste.
- Align the voter-facing structure checker with the quarantined-source public-surface firewall; safe `official route examples; not current voter instruction` headings now satisfy structure checks.
- Refresh the minimal packet-verification report example to `v872`, add the current strict verification-policy lockfile/receipt fixture, and restore family-tail entrypoint coverage in root indexes.
- Compact selected generated JSON reports to preserve the 16 MiB size-budget gate without deleting current no-go evidence.
- Regenerate current source-pressure, current-authority, adopter-capture, release go/no-go, release-maintainer, local-pilot, redaction, accessibility/language, custody/provenance, independent-review, Example County, human-review, and trust-recovery reports at `v872`.
- Boundary: v872 remains synthetic-only and does not establish current voter instruction, legal reliance, source-byte cache completeness, public-release authorization, production signer authority, independent validation, certification, or live-pilot readiness.

## v871 (2026-06-10)

- Add a quarantined-source public-surface firewall so state/local example xrefs cannot be gathered under authoritative/current source headings or active-claim prose without an explicit non-instruction boundary.
- Rewrite high-risk source sections across 21 voter-facing surface docs as official route examples, not current voter instructions, and add a shared state/local quarantine boundary marker.
- Add `scripts/check_quarantined_source_public_surface_firewall.py` and `artifacts/reports/quarantined-source-public-surface-firewall-report.json` to make the wording firewall release-gate enforceable.
- Regenerate adopter capture, capture-record validation, release go/no-go, local-pilot, redaction, accessibility/language, custody/provenance, independent-review, Example County, human-review, trust-recovery, source-pressure, current-authority, and release-maintainer reports at v871.
- Boundary: v871 remains synthetic-only and does not establish current voter instruction, legal reliance, certification, source-byte cache completeness, production signer authority, independent validation, publication governance, or live-pilot readiness.

## v870 (2026-06-10)

- Add `tools/adopter_capture_record_validator.py` and `scripts/check_adopter_capture_record_validator.py` so adopter source-authority capture records have executable promotion-shape checks instead of only a worksheet/matrix.
- Add six synthetic capture-record fixtures, including five expected-failure negative controls for missing hash, global jurisdiction scope, missing human approval, non-quarantined source use, and synthetic `promotion_allowed=true`.
- Generate `artifacts/reports/adopter-capture-record-validation-report.json` and wire the validator into the release-gate inventory, docs/162, release go/no-go offline drill, and current-signal summary.
- Update release go/no-go criterion RGN-003 so current-authority no-go is not falsely tied only to due-within-30-days source rows; adopter capture records and human approval are now explicit prerequisites for quarantined state/local xref promotion.
- Regenerate adopter capture, capture-record validation, release go/no-go, local-pilot, redaction, accessibility/language, custody/provenance, independent-review, Example County, human-review, trust-recovery, source-pressure, current-authority, and release-maintainer reports at v870.
- Compact four historical platform-source sampling CSV row bodies, saving 116400 bytes while preserving JSON/doc audit anchors in `artifacts/reports/rev0870-size-compaction.json`.
- Boundary: v870 remains synthetic-only and does not establish current voter instruction, legal reliance, certification, source-byte cache completeness, production signer authority, independent validation, publication governance, or live-pilot readiness.

## v869 (2026-06-10)

- Add an adopter authority-capture no-go pack that converts the 70 quarantined mutable state/local source rows into a concrete missing-capture queue before any public guidance promotion.
- Add `tools/adopter_authority_capture_pack.py`, `scripts/check_adopter_authority_capture_pack.py`, and `artifacts/templates/adopter-source-authority-capture-worksheet.md`; wire the check into the release-gate inventory and docs/162.
- Refactor no-go pack tools to use a shared `tools/release_context.py` helper so regenerated local-pilot, redaction, accessibility/language, custody/provenance, independent-review, and release-go/no-go reports carry the current archive release date instead of the old v862 baseline date.
- Update local-pilot source-freshness requirement LPI-003 to require adopter capture, responsible-office routing, conflict review, and human approval before quarantined state/local xrefs can be promoted.
- Regenerate adopter capture, local-pilot, redaction, accessibility/language, custody/provenance, independent-review, release go/no-go, source-pressure, and current-authority reports for v869.
- Boundary: v869 remains synthetic-only and does not establish current voter instruction, legal reliance, certification, source-byte cache completeness, production signer authority, independent validation, publication governance, or live-pilot readiness.

## v868 (2026-06-10)

- Quarantine the remaining 70 mutable state/local jurisdiction source rows as example/routing `xref` context with `review_by=2026-07-25`; no byte pins are added and no state/local source is promoted as current voter instruction.
- Rewrite 26 high-risk special-case surface lines that previously described unpinned state/local xrefs as “current” pages; those lines now identify the rows as example official routes only and say they are not current voter instruction.
- Add `scripts/check_state_local_xref_quarantine.py` and wire it into the release gate so quarantined state/local rows must keep a non-instruction boundary and markdown cannot reintroduce ambiguous “current” wording around unpinned jurisdiction xrefs.
- Refactor the shared current-authority classifier so rows tagged `jurisdiction_quarantine` + `not_current_voter_instruction` are excluded from current-authority queues until adopter-specific promotion.
- Compact bulky generated JSON reports after digest-bearing handoff regeneration to keep the carrier under the release size budget without deleting the row-level state/local watchlist.
- Regenerate current-date source pressure and 45-day current-authority queue reports; the 45-day current-authority queue is now zero while the state/local quarantine report preserves the 70-row watchlist.
- Add `docs/906-state-local-source-quarantine-and-current-wording-firewall.md` and `artifacts/reports/state-local-jurisdiction-quarantine-rev0868.*`.
- Boundary: v868 remains synthetic-only and does not establish current state/local law, current voter instruction, legal reliance, source-byte cache completeness, production signer authority, independent validation, publication governance, certification, or live-pilot readiness.

## v867 (2026-06-10)

- Centralize current-authority source classification in `scripts/_shared/current_authority.py` after finding that current-authority queue and burndown-batch reports disagreed on state/host/tag coverage.
- Add `scripts/check_current_authority_report_consistency.py` so the source queue and burndown batch reports cannot drift silently again.
- Re-review 75 non-state current-authority routes in the 45-day queue as bounded official/federal/current-routing `xref` context with `review_by=2026-08-09`; no byte pins are added and no guidance authority is promoted.
- Leave 70 state/local jurisdiction rows visible in the 45-day queue because they are the highest-risk rows for misuse as current voter instructions.
- Add `docs/905-federal-official-source-sweep-and-authority-classifier-refactor.md` and `artifacts/reports/federal-official-route-sweep-rev0867.*`.
- Regenerate current-date source pressure, 45-day current-authority queue, current-authority burndown batches, release go/no-go, release-maintainer handoff, Example County output/evaluator/negative-control packs, and pre-pilot ledgers for v867.
- Boundary: v867 remains synthetic-only and does not establish current voter instruction, legal reliance, certification, source-byte cache completeness, production signer authority, independent validation, publication governance, or live-pilot readiness.

## v866 (2026-06-10)

- Clear the seven-row near-term source-review queue without inventing source-byte pins.
- Split NCSL/BPC/Brennan/Elections Group/IML/Science context rows into explicit `xref` decisions rather than treating them as current authority.
- Add `docs/903-seven-source-burndown-and-xref-authority-split.md` plus `artifacts/reports/source-seven-row-decision-burndown-rev0866.*` to record the row-level decisions and boundaries.
- Regenerate current-date source pressure and current-authority queue reports for v866; the `2026-06-10` pressure report now shows zero expired rows and zero due-within-30-days rows.
- Audit and recheck three EAC current-authority pages into a short next-review window and document them in `docs/904-next-authority-eac-page-audit.md`.
- Boundary: v866 remains synthetic-only and does not establish current voter instruction, legal reliance, certification, source-byte cache completeness, production signer authority, independent validation, publication governance, or live-pilot readiness.
