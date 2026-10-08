# Start here — v900

**Track:** Shared

This archive remains **synthetic-release only**.

## Recent additions (v865–v900)

- v900 release-gate runtime refactor: `docs/937-release-gate-runtime-risk-and-inprocess-replay-refactor.md`, `scripts/check_cdf_export_replay.py`, `scripts/check_cdf_independent_replay_verifier.py`, `scripts/check_ballot_accounting_reconciler.py`, and `scripts/check_election_event_log_reconciler.py` remove redundant nested subprocess fan-out from the newest replay/accounting/event checks while preserving the same reports and negative controls. It remains synthetic only and is not live jurisdiction evidence, full NIST EEL/CDF conformance, the NIST CDF Test Method, certification, outcome proof, current voter instruction, or legal advice.

- v899 event-log provenance chain: `docs/936-event-log-provenance-chain-and-current-entrypoint-audit.md`, `tools/election_event_log_reconciler.py`, `scripts/check_election_event_log_reconciler.py`, `artifacts/examples/example_county_2026_municipal_pilot/cdf/election-event-log-minimal.json`, `artifacts/reports/election-event-log-reconciliation-rev0899.json`, and `artifacts/test-vectors/election-event-log/` add a digest-bound chronological witness over the synthetic replay/accounting artifacts and fail closed on broken previous-hash, digest, timestamp, and required-role controls. It remains synthetic only and is not live Election Event Log evidence, full NIST EEL/CDF conformance, the NIST CDF Test Method, certification, outcome proof, current voter instruction, or legal advice.

- v898 reporting-unit CDF replay: `docs/935-reporting-unit-cdf-replay-and-gate-runtime-risk-audit.md`, `tools/cdf_export_replay.py`, `tools/cdf_replay_independent_verifier.py`, `scripts/check_cdf_export_replay.py`, `scripts/check_cdf_independent_replay_verifier.py`, `artifacts/reports/cdf-export-replay-report-rev0898.json`, and `artifacts/test-vectors/cdf-replay/election-results-unit-swap-total-preserving.json` move the synthetic BD/CVR/ERR replay from aggregate contest totals to reporting-unit comparison rows. The same revision compacts superseded source-byte/cache history into `artifacts/history/rev0898-sourcebyte-fixture-history.tar.gz` while preserving exact bytes. It remains synthetic only and is not live export evidence, full NIST CDF conformance, certification, outcome proof, current voter instruction, or legal advice.

- v897 ballot-accounting reconciliation: `docs/934-ballot-accounting-reconciliation-and-stale-pack-audit.md`, `tools/ballot_accounting_reconciler.py`, `scripts/check_ballot_accounting_reconciler.py`, `artifacts/reports/ballot-accounting-reconciliation-rev0897.json`, and `artifacts/examples/example_county_2026_municipal_pilot/cdf/public-ballot-accounting-reconciliation.md` close the next K02/K03 risk: replayed CVR totals now reconcile against a synthetic ballot-accounting ledger for reporting-unit counts, contest eligible-ballot counts, selection slots, undervotes, and overvotes. The same revision also expands the current-fixture sweep to catch stale non-rev-named no-go packs. It remains synthetic only and is not live custody evidence, full NIST CDF conformance, certification, outcome proof, current voter instruction, or legal advice.

- v896 independent CDF replay verifier: `docs/933-cdf-independent-verifier-transcript-and-release-gate-risk-burndown.md`, `tools/cdf_replay_independent_verifier.py`, `scripts/check_cdf_independent_replay_verifier.py`, `artifacts/reports/cdf-independent-replay-verifier-rev0896.json`, and `artifacts/examples/example_county_2026_municipal_pilot/cdf/public-cdf-independent-verifier.md` add a separately implemented synthetic parser/tally path that replays the same BD/CVR/ERR fixture without importing the primary adapter, compares the shipped primary report and CRO, and fails on deliberate export/report/CRO drift. It remains synthetic only and is not full NIST CDF conformance, external independent review, live export evidence, certification, or outcome proof.

- v895 CDF replay risk bridge: `tools/cdf_export_replay.py`, `scripts/check_cdf_export_replay.py`, `artifacts/reports/cdf-export-replay-report-rev0895.json`, `artifacts/examples/example_county_2026_municipal_pilot/cdf/canonical-results-object-from-cdf.json`, and `artifacts/examples/example_county_2026_municipal_pilot/cdf/cdf-mapping-manifest.json` turn K03/MKB-003 from a prose CDF promise into an executable synthetic BD/CVR/ERR total-replay seam with negative controls. It remains synthetic only and is not full NIST CDF conformance, live export evidence, certification, or outcome proof.

- v894 mission-heart/authentication correction: `docs/932-mission-heart-authentication-boundary-and-cloudtainer-correction-plan.md`, `adr/0005-mission-kernel-live-evidence-requires-authenticated-envelope.md`, `artifacts/reports/mission-heart-trust-boundary-audit-rev0894.json`, and the hardened submitter/intake path make bare digests unauthenticated candidates, preserve zero authenticated live objects, record the stale v893 go/no-go defect, and define the A0 evidence-sidecar adoption path.
- v893 full mission-kernel drill replay: `docs/931-full-mission-kernel-drill-replay-and-intake-boundary-audit.md`, `tools/mission_kernel_full_drill_replay.py`, `scripts/check_mission_kernel_full_drill_replay.py`, `artifacts/reports/mission-kernel-full-drill-replay-audit-rev0893.json`, and `artifacts/examples/example_county_2026_municipal_pilot/public-full-closeout-drill-replay.md` exercise all seven workqueue rows and twenty-eight evidence classes through the submitter/intake path while proving zero live objects, zero local-path leaks, and zero live-readiness overclaims.

- v892 operator evidence submitter: `docs/930-operator-evidence-submitter-and-nonproduction-drill.md`, `tools/mission_kernel_evidence_submitter.py`, `scripts/check_mission_kernel_evidence_submitter.py`, and `schemas/MissionKernelEvidenceSubmission.json` add the external-record hashing seam and non-production drill path while proving governed synthetic-tree paths fail closed and live evidence remains zero.
- v891 live-evidence intake validator: `docs/929-live-evidence-intake-validator-and-mission-kernel-common-refactor.md`, `tools/mission_kernel_live_evidence_intake.py`, `scripts/check_mission_kernel_live_evidence_intake.py`, `tools/mission_kernel_common.py`, and `artifacts/examples/example_county_2026_municipal_pilot/live-closeout-evidence-intake-status.json` add the fail-closed bridge from empty workqueue slots to future digest-bound jurisdictional evidence while proving the shipped archive has zero live evidence objects.

- v890 live-closeout workqueue: `docs/928-live-closeout-workqueue-and-intake-refactor.md`, `tools/mission_kernel_live_workqueue.py`, `scripts/check_mission_kernel_live_workqueue.py`, `artifacts/examples/example_county_2026_municipal_pilot/live-closeout-workqueue.json`, and `artifacts/examples/example_county_2026_municipal_pilot/live-closeout-intake-template.json` convert the seven mission blockers into concrete evidence-intake rows while keeping live closeout no-go.

- v889 mission-kernel closeout: `docs/927-mission-kernel-closeout-gaps-and-example-county-refactor.md`, `tools/mission_kernel_closeout.py`, `scripts/check_mission_kernel_closeout_pack.py`, and `artifacts/examples/example_county_2026_municipal_pilot/mission-kernel-closeout-index.json` make the seven-element mission gap executable while preserving live no-go boundaries.


- `docs/926-mission-kernel-release-gate-closure-and-sprawl-reset.md` and `artifacts/reports/mission-kernel-deep-audit-rev0888.json` recenter the archive on the seven-part evidence/recovery mission kernel and document the v887 release-control failure and sprawl reset.

For rev0888, start with the mission-kernel audit and canonical release path:

- `docs/926-mission-kernel-release-gate-closure-and-sprawl-reset.md`
- `artifacts/reports/mission-kernel-deep-audit-rev0888.json`
- `scripts/release_gate.py`
- `scripts/check_release_gate_step_inventory.py`
- `docs/162-release-and-ci-evidence-pipeline.md`

This revision repairs the uploaded v887 carrier, binds semantic checks through verified packaging, and preserves the synthetic-only no-go. It does not turn the archive into current voter instruction or live deployment evidence.

- `docs/925-source-byte-operator-workplan-and-workpack-parser-refactor.md`, `scripts/build_source_byte_operator_workplan.py`, and `tools/source_byte_workpack_common.py` convert the DNS-blocked source-byte lane into a current outside-cloudtainer operator plan and centralize strict `.sha256` workpack parsing.

For rev0887, start with the source-byte operator workplan. This revision does not add fake receipts and does not change the live no-go posture, but it gives a network-capable operator the current batch, host-slice, classified-workpack, and exact-cache return commands in one gate-checked surface:

- `docs/925-source-byte-operator-workplan-and-workpack-parser-refactor.md`
- `artifacts/reports/risk-priority-forward-motion-rev0887.json`
- `artifacts/reports/source-byte-operator-workplan-rev0887.json`
- `artifacts/reports/source-byte-batch-host-slices-rev0887.json`
- `artifacts/reports/source-byte-batch-attempt-workpacks-rev0887.json`
- `tools/source_byte_workpack_common.py`
- `scripts/build_source_byte_operator_workplan.py`
- `scripts/check_source_byte_operator_workplan.py`
- `scripts/check_source_byte_workpack_common.py`

- `docs/924-source-byte-dns-preflight-and-attempt-workpack-refactor.md`, `tools/source_byte_dns_preflight.py`, and `scripts/build_source_byte_batch_attempt_workpacks.py` turn a DNS-blocked batch01 fetch attempt into classified retry workpacks instead of hiding it inside an undifferentiated missing-receipts queue.

For rev0886, start with the DNS preflight and attempt-workpack reports. This revision attempted source-byte acquisition, but the cloudtainer resolver failed for all first-batch hosts, so it adds no receipts and does not change the live no-go posture:

- `docs/924-source-byte-dns-preflight-and-attempt-workpack-refactor.md`
- `artifacts/reports/risk-priority-forward-motion-rev0886.json`
- `artifacts/reports/source-byte-dns-preflight-rev0886.json`
- `artifacts/reports/source-byte-batch-attempt-workpacks-rev0886.json`
- `artifacts/source_byte_cache_intake/attempt_workpacks/`
- `tools/source_byte_dns_preflight.py`
- `scripts/build_source_byte_batch_attempt_workpacks.py`
- `scripts/check_source_byte_dns_preflight.py`
- `scripts/check_source_byte_batch_attempt_workpacks.py`

- `docs/923-source-byte-host-slices-and-priority-policy-refactor.md`, `scripts/build_source_byte_batch_host_slices.py`, and `scripts/check_source_byte_batch_host_slices.py` split the first unresolved source-byte batch into same-host `.sha256` workpacks, and `tools/source_byte_priority.py` removes duplicated priority logic from the queue/intake/cache-scan path.

For rev0885, start with the host-slice source-byte workpack report. This revision does not add fake source receipts and does not change the live no-go posture:

- `docs/923-source-byte-host-slices-and-priority-policy-refactor.md`
- `artifacts/reports/risk-priority-forward-motion-rev0885.json`
- `artifacts/reports/source-byte-batch-host-slices-rev0885.json`
- `artifacts/source_byte_cache_intake/host_slices/`
- `tools/source_byte_priority.py`
- `scripts/build_source_byte_batch_host_slices.py`
- `scripts/check_source_byte_batch_host_slices.py`

- `docs/922-source-byte-resumable-batch-followup-and-fetch-filter-refactor.md`, `scripts/build_source_byte_batch_followup.py`, and `scripts/check_source_byte_batch_followup.py` turn the first source-byte batch into a resumable operator workflow: exact-hash fetch attempts can now be filtered by source ID, converted into unresolved follow-up handoffs, and checked without converting plan-only or failed attempts into receipts.

For rev0884, start with the resumable source-byte batch follow-up note and the current follow-up handoff. This revision does not add fake source receipts and does not change the live no-go posture:

- `docs/922-source-byte-resumable-batch-followup-and-fetch-filter-refactor.md`
- `artifacts/reports/risk-priority-forward-motion-rev0884.json`
- `artifacts/reports/source-byte-batch-fetch-plan-rev0884.json`
- `artifacts/reports/source-byte-batch-followup-rev0884.json`
- `artifacts/reports/source-byte-cache-batch-status-rev0884.json`
- `artifacts/source_byte_cache_intake/followups/source-byte-cache-followup-rev0884-batch01-unresolved.sha256`
- `scripts/fetch_source_byte_batch.py`
- `scripts/build_source_byte_batch_followup.py`
- `scripts/check_source_byte_batch_followup.py`

- `docs/921-priority-risk-source-byte-batch-fetch-and-measurement-refactor.md`, `scripts/fetch_source_byte_batch.py`, and `scripts/check_measurement_tool_boundaries.py` move from diagnosis to executable risk reduction: the first incomplete source-byte batch now has a network-capable exact-hash fetch/receipt path, and two measurement helpers now fail closed instead of emitting evidence-shaped emptiness.

For rev0883, start with the priority-risk note and the current batch-fetch plan. This revision does not add fake source receipts and does not change the live no-go posture:

- `docs/921-priority-risk-source-byte-batch-fetch-and-measurement-refactor.md`
- `artifacts/reports/risk-priority-forward-motion-rev0883.json`
- `artifacts/reports/source-byte-batch-fetch-plan-rev0883.json`
- `artifacts/reports/source-byte-cache-batch-status-rev0883.json`
- `scripts/fetch_source_byte_batch.py`
- `scripts/check_source_byte_batch_fetcher.py`
- `scripts/check_measurement_tool_boundaries.py`

- `docs/920-deep-read-gap-map-cloudtainer-waste-and-correction-plan.md` and `artifacts/reports/deep-review-gap-map-rev0882.json` record the session deep read: missing evidence lanes, source-byte cache blockers, ZIP/storage tradeoffs, doc-range gaps, and correction order.

For rev0882, start with the deep-read gap map and refreshed source-byte dashboard. This revision does not add fake source-byte receipts and does not change the live no-go posture:

- `docs/920-deep-read-gap-map-cloudtainer-waste-and-correction-plan.md`
- `artifacts/reports/deep-review-gap-map-rev0882.json`
- `artifacts/reports/rev0882-deep-read-history-compaction.json`
- `artifacts/reports/source-byte-cache-batch-status-rev0882.json`
- `artifacts/reports/current-revision-fixture-sweep-rev0882.json`

- `docs/919-source-byte-batch-status-and-stale-batch-firewall.md` and `scripts/check_source_byte_cache_batch_status.py` join source-byte receipts, the acquisition queue, and batch sha256sum handoffs so stale receipt-missing batch files fail closed.

For rev0881, start with source-byte batch status. This revision does not add fake source receipts; it records the first incomplete batch and makes the gate fail if completed receipt-present rows remain in receipt-missing batch handoffs:

- `docs/919-source-byte-batch-status-and-stale-batch-firewall.md`
- `scripts/build_source_byte_cache_batch_status.py`
- `scripts/check_source_byte_cache_batch_status.py`
- `artifacts/reports/source-byte-cache-batch-status-rev0881.json`
- `artifacts/reports/source-byte-cache-batch-resume-rev0881.json`
- `artifacts/reports/source-byte-cache-batch-manifests-rev0881.json`
- `artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev0881-batch01.sha256`

- `docs/918-source-byte-batch-resume-and-selected-cache-ingest-firewall.md` and `scripts/check_source_byte_cache_batch_resume.py` make source-byte receipt generation resumable by selected batch file rather than scanning the whole receipt-missing queue.

For rev0880, start with selected-batch source-byte resume. This revision does not add fake source receipts; it lets an operator run one `.sha256` batch against an external cache and write only that batch's exact-match receipts while rejecting wrong/unsafe batch entries and ignoring valid cache bytes outside the selected batch:

- `docs/918-source-byte-batch-resume-and-selected-cache-ingest-firewall.md`
- `scripts/source_byte_receipts_from_cache_batch.py`
- `scripts/check_source_byte_cache_batch_resume.py`
- `artifacts/reports/source-byte-cache-batch-resume-rev0880.json`
- `artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev0880-batch01.sha256`
- `artifacts/reports/source-byte-cache-batch-manifests-rev0880.json`
- `artifacts/reports/rev0880-prepilot-ledger-history-compaction.json`

- `docs/917-source-byte-cache-batch-manifests-and-incremental-intake.md` and `scripts/check_source_byte_cache_batch_manifests.py` split the current source-byte cache intake handoff into deterministic sha256sum batch files for incremental external-cache execution.

For rev0879, start with the source-byte cache batch manifests. This revision does not add fake source receipts; it makes the existing 105-entry external-cache handoff easier to execute in six operator-sized batches and checks that the batch files reconstruct the master `.sha256` intake exactly:

- `docs/917-source-byte-cache-batch-manifests-and-incremental-intake.md`
- `scripts/build_source_byte_cache_batch_manifests.py`
- `scripts/check_source_byte_cache_batch_manifests.py`
- `artifacts/reports/source-byte-cache-batch-manifests-rev0879.json`
- `artifacts/source_byte_cache_intake/batches/`
- `artifacts/reports/source-byte-cache-intake-manifest-rev0879.json`
- `artifacts/source_byte_cache_intake/source-byte-cache-missing-receipts-rev0879.sha256`

- `docs/916-source-byte-cache-intake-manifest-and-sha256sum-firewall.md` and `scripts/check_source_byte_cache_intake_manifest.py` add a sha256sum-ready external-cache intake manifest for every receipt-missing pinned source.

For rev0878, start with the source-byte cache intake manifest. This revision does not add fake source receipts; it creates a current `.sha256` expectation file that a network-capable/offline-cache operator can run with `sha256sum -c`, and the gate proves empty or wrong bytes do not become receipts:

- `docs/916-source-byte-cache-intake-manifest-and-sha256sum-firewall.md`
- `scripts/build_source_byte_cache_intake_manifest.py`
- `scripts/check_source_byte_cache_intake_manifest.py`
- `artifacts/reports/source-byte-cache-intake-manifest-rev0878.json`
- `artifacts/source_byte_cache_intake/source-byte-cache-missing-receipts-rev0878.sha256`
- `artifacts/reports/source-byte-cache-batch-ingest-rev0878.json`

- `docs/915-current-revision-fixture-sweep-and-source-byte-ratchet.md` and `scripts/check_current_revision_fixture_sweep.py` add a current-revision drift gate for trust-policy fixtures, source-byte batch reports, PacketVerificationReport examples, and Example County synthetic outputs.

For rev0877, start with the current-fixture sweep and source-byte ratchet. This revision does not add fake source receipts; it prevents current synthetic evidence from lagging behind `VERSION`, raises the receipt floor to the actual current count, and proves batch cache runs skip existing receipts without `--force`:

- `docs/915-current-revision-fixture-sweep-and-source-byte-ratchet.md`
- `scripts/check_current_revision_fixture_sweep.py`
- `artifacts/reports/current-revision-fixture-sweep-rev0877.json`
- `artifacts/reports/source-byte-cache-batch-ingest-rev0877.json`
- `scripts/check_source_byte_cache_batch_ingest.py`

- `docs/914-source-byte-cache-batch-ingest-and-mismatch-firewall.md` and `scripts/source_byte_receipts_from_cache_batch.py` add a batch external-cache ingest path for receipt-missing pinned sources, with a gate that blocks mismatched bytes from becoming receipts.


For rev0876, start with the batch external-cache ingest path. It does not add fake source-byte receipts; it makes the remaining receipt queue executable in one scan, reports missing/mismatched cache files, and writes receipts only for exact SHA-256 matches:

- `docs/914-source-byte-cache-batch-ingest-and-mismatch-firewall.md`
- `scripts/source_byte_receipts_from_cache_batch.py`
- `scripts/check_source_byte_cache_batch_ingest.py`
- `artifacts/reports/source-byte-cache-batch-ingest-rev0876.json`

For rev0875, start with the offline cache-receipt path and root-entrypoint drift fix. The revision does not add fake source-byte receipts; it records the cloudtainer DNS blocker and adds a no-network helper that can turn already-populated external cache files into validated receipts after sha256 match:

- `docs/913-offline-cache-receipts-dns-preflight-and-root-entrypoint-drift.md`
- `scripts/source_byte_receipt_from_cache.py`
- `tools/source_byte_receipt_pack.py`
- `scripts/check_source_byte_acquisition_queue.py`
- `artifacts/reports/source-byte-dns-preflight-rev0875.json`
- `scripts/check_version_consistency.py`
- `README.md`
- `ARCHIVE_INDEX.md`

For rev0874, start with the source-byte acquisition queue and cache-basename firewall. It makes every pinned lockfile row fetch-addressable by stable local filename, queues the `105` pinned rows that still lack source-byte receipts, and refactors the fetch helper so maintainers can fetch by source ID instead of hand-copying URLs:

- `docs/912-source-byte-acquisition-queue-and-cache-basename-firewall.md`
- `tools/source_byte_acquisition_queue.py`
- `scripts/check_source_byte_acquisition_queue.py`
- `artifacts/reports/source-byte-acquisition-queue.json`
- `scripts/fetch_source_sha256.py`
- `evidence/lock/external-sources.toml`


For rev0873, start with the source-byte receipt lane and adopter-capture hardening. It records selected byte observations for pinned EAC/VVSG, NIST, RFC, and NASEM rows without bundling third-party bytes, adds a release-gate validator for those receipts, and prevents synthetic capture fixtures from being shape-valid while requesting promotion:

- `docs/911-source-byte-receipts-adopter-shaped-capture-and-size-audit.md`
- `tools/source_byte_receipt_pack.py`
- `scripts/check_source_byte_receipt_pack.py`
- `artifacts/source_byte_receipts/`
- `artifacts/reports/source-byte-receipt-validation-report.json`
- `artifacts/examples/adopter_authority_capture_records/valid-example-county-in-custody-route-no-promotion.synthetic.json`
- `artifacts/reports/rev0873-historical-report-size-compaction.json`

For rev0872, start with the release-gate/date-context audit. It fixes the immediate `check_tracks.py` blocker in docs `904` through `909`, centralizes stale source-review defaults through shared release context, and records the remaining source-byte cache/adopter-capture/platform-sprawl debt:

- `docs/910-session-audit-release-gate-date-context-and-source-cache-debt.md`
- `artifacts/reports/session-audit-release-gate-date-context-rev0872.json`
- `tools/release_maintainer_handoff_pack.py`
- `scripts/check_current_authority_review_cliff.py`
- `scripts/report_source_review_pressure.py`

For rev0871, start with the quarantined-source public-surface wording firewall. It proves the 70 quarantined state/local routes are still example official routes only and that affected voter-facing surface docs do not reintroduce authoritative/current source-section wording without the non-instruction boundary:

- `docs/909-quarantined-source-public-surface-firewall-and-state-local-example-boundaries.md`
- `scripts/check_quarantined_source_public_surface_firewall.py`
- `artifacts/reports/quarantined-source-public-surface-firewall-report.json`

For rev0870, start with the capture-record promotion firewall that makes the adopter source-authority path executable instead of only documented:

1. `docs/908-adopter-capture-record-validator-and-promotion-negative-controls.md` — validator behavior, negative fixtures, and go/no-go integration.
2. `artifacts/reports/adopter-capture-record-validation-report.json` — six-fixture validation report with five expected failures and zero shape-valid promotions.
3. `tools/adopter_capture_record_validator.py` — executable shape/negative-control validator for adopter capture records.
4. `scripts/check_adopter_capture_record_validator.py` — release-gate promotion firewall for capture-record fixtures.
5. `artifacts/examples/adopter_authority_capture_records/` — one shape-valid non-promoting fixture plus expected-failure fixtures.

For rev0869, start with the adopter-authority capture surfaces that convert the state/local quarantine into a concrete missing-capture queue and fix release-date drift in generated no-go packs:

1. `docs/907-adopter-authority-capture-pack-and-release-date-refactor.md` — adopter capture queue, required promotion evidence, and no-go pack release-date refactor.
2. `artifacts/reports/adopter-authority-capture-matrix.json` — 70-row missing-capture matrix for quarantined state/local xrefs.
3. `artifacts/reports/adopter-authority-capture-summary.json` — compact priority-lane summary, including 8 pin-first candidates.
4. `tools/adopter_authority_capture_pack.py` — deterministic report builder for the adopter capture matrix.
5. `scripts/check_adopter_authority_capture_pack.py` — release-gate drift firewall for the capture reports and non-instruction boundary.

For rev0868, start with the source-safety surfaces that quarantine mutable state/local examples and prevent them from being mistaken for live voter instruction:

1. `docs/906-state-local-source-quarantine-and-current-wording-firewall.md` — state/local quarantine, wording refactor, and new release-gate boundary.
2. `artifacts/reports/state-local-jurisdiction-quarantine-rev0868.json` — 70-row watchlist of quarantined state/local jurisdiction xrefs.
3. `artifacts/reports/current-authority-source-queue-45day-rev0868.json` — 45-day current-authority queue now zero after quarantine.
4. `scripts/check_state_local_xref_quarantine.py` — drift firewall for non-instruction notes and ambiguous current wording around unpinned jurisdiction xrefs.

For rev0867, start with the source-maintenance surfaces that cut the 45-day current-authority queue down to state/local rows and fixed duplicated classifier drift:

1. `docs/905-federal-official-source-sweep-and-authority-classifier-refactor.md` — federal/official source sweep plus shared current-authority classifier refactor.
2. `artifacts/reports/federal-official-route-sweep-rev0867.json` — row-level record for the 75 non-state current-authority routes re-reviewed as bounded `xref` context.
3. `artifacts/reports/current-authority-source-queue-45day-rev0867.json` — 45-day queue now reduced to state/local jurisdiction rows only.
4. `scripts/check_current_authority_report_consistency.py` — drift firewall ensuring the source queue and burndown-batch reports agree.

For rev0866, start with the source-maintenance surfaces that finished the visible near-term burn-down without adding another doctrine layer:

1. `docs/903-seven-source-burndown-and-xref-authority-split.md` — seven remaining source rows resolved into replacement, mutable-context, blocked, or implementation-context decisions.
2. `artifacts/reports/source-seven-row-decision-burndown-rev0866.json` — compact machine-readable summary of the seven row-level decisions and boundaries.
3. `artifacts/reports/source-review-pressure-current-rev0866.json` — current-date pressure report for `2026-06-10`, now showing zero expired and zero due-within-30-days rows.
4. `artifacts/reports/current-authority-source-queue-current-rev0866.json` — current-authority queue report showing zero expired or due-soon current-authority rows on `2026-06-10`.
5. `docs/902-source-cliff-demotion-lockfile-truth-and-currentness-budget.md` — prior rev0865 source-cliff demotion, lockfile note-truth cleanup, C2PA 2.4 pointer update, and side-effect-free verifier refactor.
6. `artifacts/checklists/automated-voter-information-assistant-surface-checklist.md` — no-rights-affecting-automated-determination and source-hierarchy controls.
7. `docs/901-current-date-source-cliff-burndown-and-ai-assistant-risk-cut.md` — prior rev0864 current-date source cliff burn-down and automated assistant risk cut.

Do not treat this archive as current voter instruction, legal advice, certification evidence, production signer authority, filesystem sandbox certification, source-byte verification, or live-pilot authorization.

## Required voter-facing family-tail entrypoints

These remain linked here so promoted high-risk voter-facing surfaces stay visible from core entrypoints without making them the first reading path:

- `docs/335-guardianship-conservatorship-and-court-determined-voting-capacity-as-evidence-surfaces.md`
- `docs/336-tribal-community-voting-tribal-ids-reservation-addresses-and-tribal-government-ballot-access-paths-as-evidence-surfaces.md`
- `docs/337-disaster-displacement-evacuation-and-temporary-relocation-voting-paths-as-evidence-surfaces.md`
- `docs/338-new-citizen-and-newly-naturalized-voter-registration-timing-proof-and-post-ceremony-fallback-paths-as-evidence-surfaces.md`
- `docs/339-signature-alternatives-mark-witness-stamp-and-accessible-signature-cure-paths-as-evidence-surfaces.md`
- `docs/340-youth-voter-preregistration-activation-timing-and-primary-before-general-eligibility-as-evidence-surfaces.md`
- `docs/341-voter-assistance-person-of-choice-interpreter-rules-and-restricted-helper-boundaries-as-evidence-surfaces.md`
- `docs/342-ballot-return-by-another-person-designated-agent-or-bearer-rules-and-ballot-handoff-boundaries-as-evidence-surfaces.md`
- `docs/343-challenged-voter-oaths-affidavits-witnesses-and-fail-safe-ballot-rights-as-evidence-surfaces.md`

- `docs/904-next-authority-eac-page-audit.md` — next 45-day current-authority queue audit for high-reference EAC pages.
- `docs/905-federal-official-source-sweep-and-authority-classifier-refactor.md` — federal official-source sweep and current-authority classifier refactor.
- `docs/906-state-local-source-quarantine-and-current-wording-firewall.md` — state/local source quarantine and current-wording firewall.
- `docs/907-adopter-authority-capture-pack-and-release-date-refactor.md` — adopter authority-capture queue and no-go pack release-date refactor.
