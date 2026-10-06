# Archive economy audit witnesses

Rev0352 resolves `OQ-0244` by adding release-integrity mutation canaries and a helper-owned manifest/hash/provenance validator: `tools/check_release_integrity_negative_canaries.py` mutates FILE-MANIFEST, CHECKSUMS, and RELEASE-PROVENANCE fixtures while `tools/release_integrity_contract_lib.py` keeps the current release-integrity contract executable. `OQ-0245` remains live so these guards stay cheap and failure-local rather than becoming a bundle-notary or checksum-authority layer.


This witness keeps the current pass focused on concrete waste and release risk rather than adding another doctrinal layer. It now binds practical changes: release hygiene uses root-relative paths, `ARCHIVE-ECONOMY-AUDIT.json` measures file mass/checker sprawl/queue sediment, declarative checker wrappers have been batch-consolidated while preserving packet specs, shadow contract wrappers have been data-batched with named diagnostics, hot prose surfaces have been compacted with executable source-bundle restoration, stale ledger-debt transitions have a generated non-review gate, fifty-four GPU witness wrappers have moved into an exact-spec batch checker, forty standard GPustorming wrappers have moved into a no-exec declarative batch checker, oversized GPU and GPustorming spec tables are segmented into locality-sized parts, retired checker-path aliases now compact into verified batch alias groups, eighteen method-doc prompt/runbook ratchet wrappers now live in a two-part exact-spec batch with segment-local diagnostics and source-bound semantic guards, twenty simple core method/state wrappers now live in a two-part exact-spec batch with bounded source-document guards, and `tools/package_release.py` now regenerates archive-economy audit output after release-manifest rewrites and runs a lint preflight before zip emission so direct packaging cannot bypass admission.

## Witness family

- Family: `archive_economy_state`
- Handle: `WVF-0133`
- Selected token: `refactor-ready-archive-economy`
- Public witness surface: `docs/10-method/archive-economy-audit-witnesses.md`
- Contract surface: `tools/check_archive_economy_witness_contract.py`

## Allowed tokens

- `unchecked-archive-economy` — archive economy has not been measured for the current release.
- `inventory-only-archive-economy` — counts exist, but no threshold risk flag or refactor candidate is admitted.
- `risk-flagged-archive-economy` — generated counts identify concrete file, prose, checker, queue, or path pressure.
- `refactor-ready-archive-economy` — at least one measured pressure has a concrete low-risk consolidation path.
- `mixed-archive-economy` — multiple economy states apply and must stay token-explicit.

## Current evidence flags

`OQ-0244` is resolved by release-integrity helper refactoring and manifest/hash/provenance mutation canaries: the current release-integrity surfaces now fail on FILE-MANIFEST hash drift, malformed CHECKSUMS rows, manifest row omissions, path-count drift, and RELEASE-PROVENANCE command/policy drift. `OQ-0245` is the live successor for keeping these guards useful without turning manifest hashes or provenance rows into a bundle notary. Historical precursors: `OQ-0243` was resolved by release identity and verified sidecar guards, `OQ-0242` by deterministic writer canaries, `OQ-0241` by artifact-smoke mutation canaries, `OQ-0238` by a non-mutating generated-surface drift gate, `OQ-0237` by executable core-method mutation canaries, and `OQ-0236` by source-bound method-doc guards.


- `release-hygiene-root-relative` — release exclusions operate on archive-relative parts so an absolute workdir named like `DelayBasin-rev####-*` cannot suppress every packaged file.
- `economy-audit-generated` — `ARCHIVE-ECONOMY-AUDIT.json` is built from release-hygiene paths, not hand-counted prose.
- `checker-sprawl-measured` — validation/checker counts and short contract-checker candidates are listed for future consolidation.
- `queue-sediment-measured` — followthrough, assumption, obligation, retrospective, and related ledger states are counted.
- `checker-batch-consolidated` — `tools/check_declarative_witness_contract_batch.py` replaces the smallest one-file declarative witness wrappers while retaining the exact `tools/packet_contract_common.py` specs.
- `queue-sediment-reduced` — stale early followthrough rows are expired in-place instead of being allowed to remain live by inertia.
- `stale-ledger-debt-reduced` — oldest non-current active assumptions, open obligations, and cooling retrospectives are retired or expired in place before the current continuity rows are added.
- `shadow-batch-consolidated` — `tools/check_shadow_batch_contract.py` replaces one-file shadow wrappers with explicit specs in `tools/shadow_contract_common.py` while preserving per-kind diagnostics.
- `gpustorming-late-search-batched` — `tools/check_gpustorming_late_search_family_batch_contract.py` replaces thirteen late-search GPustorming wrapper files while keeping per-family contract diagnostics in `tools/gpustorming_contract_lib.py`.
- `hot-surface-compacted` — `HOT-SURFACE-COMPACTION.json` records compaction of quarantine, prompt-pair, bibliography, and runbook hot markdown surfaces with `HOT-SURFACE-COMPACTION-ORIGINALS.json` retaining the full pre-compaction text.
- `source-roundtrip-verified` — `tools/check_hot_surface_source_roundtrip_contract.py` restores each original hot surface from `HOT-SURFACE-COMPACTION-ORIGINALS.json` into a temporary tree and re-verifies hashes, byte counts, and word counts.
- `markdown-risk-reduced` — generated economy counts now fall below the previous `markdown_words_gt_500k` risk threshold without pretending compact markdown is a semantic substitute for the retained source.
- `self-reference-excluded` — audit and release-integrity self-reference surfaces are excluded from economy totals to avoid unstable generator loops.
- `gpu-witness-batch-consolidated` — `tools/check_gpu_witness_batch_contract.py` replaces fifty-four GPU witness wrapper files while preserving exact source checker names and per-kind arguments in `tools/gpu_witness_contract_specs.py`.
- `ledger-debt-nonreview-gate` — `LEDGER-AUDIT.json` now includes debt-pressure rows and bulk state-transition groups; `tools/check_ledger_audit_contract.py` verifies transition groups exclude latest rows, retain reasons, and remain sediment triage rather than semantic waivers.
- `path-alias-batch-resolved` — `PATH-ALIAS-LEDGER.json` maps retired checker aliases to batch checkers through compact `batch_alias_groups` while preserving source checker names and keeping aliases audit-only.
- `gpustorming-standard-batched` — `tools/check_gpustorming_standard_family_batch_contract.py` replaces forty non-late GPustorming wrapper files while preserving exact source checker names and per-family arguments in `tools/gpustorming_standard_contract_specs.py`.
- `gpustorming-standard-no-exec` — standard GPustorming specs are declarative `needle_map`, `standard_family`, or `phrase_family` rows; the batch checker no longer stores or executes source strings.
- `batch-specs-segmented` — GPU witness specs and GPustorming standard specs are split into four locality-sized part modules each, with small aggregators retaining the public import path.
- `batch-spec-locality-checked` — `tools/check_batch_spec_locality_contract.py` enforces segment existence, row counts, source-checker uniqueness, byte budgets, no stored source payloads, and former wrapper absence.
- `batch-alias-groups-verified` — `PATH-ALIAS-LEDGER.json#batch_alias_groups` verifies four compact groups covering one hundred thirty-two retired checker paths without wrapper-regrowth-by-alias.
- `batch-spec-reviewability-guard` — `OQ-0235` is resolved by deriving public aggregate spec lists and part-path indexes from segment rows rather than maintaining a separate segment-index authority.
- `method-doc-ratchet-batched` — `tools/check_method_doc_ratchet_batch_contract.py` replaces eighteen homogeneous method-doc prompt/runbook ratchet wrappers while still checking each source document, prompt-pair needle, and runbook needle.
- `segment-index-derived-from-parts` — GPU, GPustorming standard, and method-doc ratchet batch aggregators expose iterators and part lists derived from segment rows, and `tools/check_batch_spec_locality_contract.py` rejects drift from those rows.
- `batch-diagnostics-segment-local` — GPU and GPustorming standard batch failures now include the former source checker and segment path so repairs stay local without wrapper regrowth.
- `package-release-audit-order-repaired` — `tools/package_release.py` regenerates `ARCHIVE-ECONOMY-AUDIT.json` after `RELEASE-MANIFEST.json` is rewritten, then refreshes release integrity before zipping.
- `method-doc-semantic-boundary-guard` — `tools/check_method_doc_ratchet_batch_contract.py` now rejects unsupported row keys, excessive needle counts, undersized source documents, and doc-needle sets large enough to become substitute summaries.
- `core-method-batched` — `tools/check_core_method_batch_contract.py` replaces twenty simple method/state wrappers while still checking each source document and auxiliary prompt/registry/runbook surface.
- `core-method-source-bound` — `tools/core_method_contract_specs.py` and its two part modules are bounded validator input; source docs remain semantic surfaces and `OQ-0237` stays live for cross-surface semantic-substitution risk.
- `core-method-negative-canaries` — `tools/check_core_method_batch_negative_canaries.py` injects source-doc, auxiliary-surface, duplicate-source, and wrapper-regrowth mutations so the batch checker must fail locally rather than merely carry bounded prose.
- `external-metadata-date-guard` — `tools/external_metadata_contract_lib.py` generates and checks `CITATION.cff`, `codemeta.json`, `ro-crate-metadata.json`, and `SBOM.spdx.json` date fields from the release receipt/manifest instead of hand-maintained stale dates.
- `executable-canary-runs` — `CANARY-RUNS.json` records generated positive checks and negative mutation observations so canary evidence is scored from current surfaces rather than asserted as protocol doctrine.
- `risk-burn-bureaucracy-boundary` — `OQ-0238` is closed only because the remaining false-green risk moved from canary prose into non-mutating generated-surface admission; it remains reopenable through `OQ-0239` if ceremony replaces failure-local checks.
- `generated-surface-drift-gated` — `tools/check_generated_surface_drift.py` compares generated outputs against a temporary regenerated tree before validation so stale derivative packets fail before any generator can repair them.
- `lint-generator-mutation-removed` — `tools/validation_toolchain_lib.py` keeps generator scripts out of `make lint`, and `VALIDATION-TOOLCHAIN-MANIFEST.json`/`CANARY-RUNS.json` record the zero-generator lint posture.
- `package-release-refreshes-all-generated-surfaces` — `tools/package_release.py` calls `tools/generated_surface_lib.py` before deterministic zipping, while `tools/gen_all_generated_surfaces.py` is the single explicit refresh entrypoint for `make context-pack`.
- `package-release-lint-preflight` — `tools/package_release.py` calls `tools/package_preflight_lib.py` after generated-surface refresh and before `write_deterministic_zip`, so direct package-release calls must pass `tools/run_lint_suite.py`; `tools/check_package_release_preflight_contract.py` keeps the order executable.
- `package-release-artifact-smoke` — `tools/package_release.py` calls `run_artifact_smoke` after deterministic zip creation and before sidecar hashing.
- `package-artifact-negative-canaries` — `tools/check_package_artifact_smoke_negative_canaries.py` runs cheap synthetic zip mutations for missing members, extra members, unsafe paths, duplicate members, member order drift, and direct unsafe extraction.
- `safe-extract-independent` — `tools/package_preflight_lib.py` rejects unsafe member targets even when extraction is called outside the full release smoke path.
- `zip-member-set-checked` — `tools/package_preflight_lib.py` compares the zip member list against `iter_release_paths` for the same bundle name.
- `clean-extraction-lint-gated` — the emitted zip is safely extracted to a temporary tree and checked with `tools/run_lint_suite.py` before sidecar trust is emitted.
- `package-sidecar-after-smoke` — the SHA256 sidecar is written only after artifact smoke passes.
- `release-identity-validated` — `tools/release_hygiene_lib.py#validate_release_identity` rejects malformed revision, impossible timestamp, uppercase/empty/path-like/dot-dot slug components before a bundle path is built.
- `release-identity-canaries` — `tools/check_release_identity_canaries.py` runs cheap negative cases for canonical release-name drift without invoking a full package release.
- `package-sidecar-verified` — `tools/package_preflight_lib.py#write_verified_sha256_sidecar` writes the sidecar after artifact smoke and immediately verifies filename, exact digest, and exact sha256sum-compatible line.
- `package-sidecar-canaries` — `tools/check_package_sidecar_canaries.py` rejects stale digest, spacing drift, bundle-name mismatch, and sidecar filename mismatch.
- `sidecar-format-digest-checked` — sidecar evidence is helper-local package-boundary hygiene, not checksum authority.
- `release-integrity-helper-refactored` — `tools/release_integrity_contract_lib.py` owns FILE-MANIFEST, CHECKSUMS, and RELEASE-PROVENANCE validation while `tools/check_release_integrity_contract.py` remains a thin wrapper.
- `release-integrity-negative-canaries` — `tools/check_release_integrity_negative_canaries.py` runs cheap synthetic release-integrity mutations inside lint rather than invoking full package release.
- `manifest-hash-drift-checked` — FILE-MANIFEST content-hash and row-omission mutations fail against current release file records.
- `checksum-format-checked` — CHECKSUMS header, lowercase digest rows, duplicate paths, and manifest path order are checked by the helper.
- `provenance-command-checked` — RELEASE-PROVENANCE command and self-reference policy drift fail locally without making provenance rows authoritative.

## Non-authority boundary

This is not a deletion court, archive-quality score, semantic completeness proof, release legitimacy board, segment-index authority, semantic-ratchet-substitution board, or permission to delete governing surfaces without ordinary review. The witness only makes the next refactor/deletion decision cheaper and harder to dodge.

## Refactor rule admitted here

Archive-economy metrics may drive concrete refactor work only when the target is mechanically low-risk, the source semantics remain in stronger governing surfaces, the validation suite still names the failing contract kind, and the resulting audit shows an actual reduction in checker, queue, file-count, or hot-prose pressure. Hot-surface compaction also requires lossless retained originals, a checker that verifies the round trip, and exact restoration evidence before compacted hot-path prose can count as operationally usable. Large batch-spec modules must preserve exact source-checker provenance, named diagnostics, no-exec declarative rows, locality-sized spec parts, and indexes derived from segment rows; method-doc ratchet rows and core-method rows must remain bounded validator inputs; if they become semantic substitutes for source documents, prompt pairs, runbook cues, or registry wiring, they must route through `OQ-0240` rather than restoring wrapper sprawl, generator-side lint mutation, release ceremony, or package-admission theater. This is still not a deletion court, ledger review court, path-alias authority, wrapper-regrowth-by-alias board, segment-index-authority court, semantic-ratchet-substitution board, or spec-data-dump court, canary-run-court, metadata-authority, registry-bureaucracy-ratchet, generator-authority-court, or release-ceremony-ratchet, package-release-court, release-legitimacy-board, lint-waiver-sovereign, clean-extraction-notary, artifact-smoke-sovereign, or zip-certification-board.

## rev0350 deterministic writer canary

`package-deterministic-writer-canaries` narrows the artifact-smoke burden boundary: `tools/package_preflight_lib.py#write_deterministic_zip` owns the release writer, and `tools/check_package_deterministic_zip_canaries.py` runs cheap synthetic writer probes instead of a full double package-release ceremony. The canary rows include `deterministic-writer-identical-bytes`, `deterministic-writer-member-order`, `deterministic-writer-fixed-metadata`, `deterministic-writer-hygiene-exclusions`, and `deterministic-writer-smoke-compatible`; together they check `zip-fixed-metadata-checked`, byte-stable rewrite behavior, release-hygiene exclusions, and compatibility with artifact smoke without claiming reproducibility authority.

`zip-rebuild-byte-canary` is the named archive-economy flag for the `deterministic-writer-identical-bytes` row; it is a local writer guard, not reproducibility authority.

## rev0351 release identity and verified sidecar guard

`release-identity-validated` and `release-identity-canaries` bind the required `Project-rev####-YYYY.MM.DD.HH.MM-slug.zip` structure to executable validation: invalid revision tokens, impossible dates, uppercase slugs, slash/path-like slugs, dot-dot slug fragments, and empty slugs fail locally before package paths are constructed.

`package-sidecar-verified`, `package-sidecar-canaries`, and `sidecar-format-digest-checked` move SHA256 sidecar creation into `tools/package_preflight_lib.py`, where the exact sidecar filename and `sha256sum`-compatible line are verified against the emitted zip after artifact smoke. This is package-boundary hygiene, not filename-canonization, checksum authority, or release legitimacy.

## rev0352 release integrity mutation canary

`release-integrity-negative-canaries` narrows the package-boundary guard stack to internal manifest/checksum/provenance drift: `tools/release_integrity_contract_lib.py#validate_release_integrity` owns the current-state validator, and `tools/check_release_integrity_negative_canaries.py` runs cheap synthetic mutations rather than a full package release. The canary rows include `release-integrity-content-hash-mutation`, `release-integrity-checksum-drift`, `release-integrity-manifest-row-omission`, `release-integrity-path-count-drift`, `release-integrity-provenance-command-drift`, and `release-integrity-provenance-policy-drift`.

`manifest-hash-drift-checked`, `checksum-format-checked`, and `provenance-command-checked` are local release-integrity flags only; they are not a bundle-notary, checksum-authority, or release-legitimacy layer.


## rev0354 currentness and metadata risk burn

`currentness-residue-guarded`, `external-metadata-schema-hardened`, and `generator-tool-count-repaired` are bounded archive-economy evidence for this turn. They point to `tools/check_currentness_residue_guard.py`, `tools/external_metadata_contract_lib.py`, and `tools/archive_economy_audit_lib.py`. This is not a currentness-cue-court, metadata-authority, or schema-bureaucracy-ratchet; it is a narrow repair for stale live-state fields and shallow external descriptors discovered by the rev0353 audit.

### rev0355 debt guard and cold-source retention

`rev0355` closes `OQ-0246` by treating the riskiest archive-economy debt as executable maintenance: `tools/check_ledger_debt_guard.py` enforces live-count budgets and revision-local transition reasons, while `tools/hot_surface_compaction_lib.py` restores deterministic gzip+base64 retained originals before checking text hashes and byte/word counts. This is explicitly not a deletion authority; `OQ-0247` remains open to test whether the mechanism stays lean.

## rev0356 ledger coldstore note

`rev0356` extends the archive-economy witness with `LEDGER-COLDSTORE.json` and `tools/check_ledger_coldstore_roundtrip_contract.py`. The move is a hot-path trim only: exact row restoration, cold payload hashes, byte counts, hot-tail exclusion, and net-savings arithmetic are the evidence; cold payloads are not deletion authority, historical truth authority, or a ledger court.


## rev0358 receipt coldstore trim

`receipt-coldstore-roundtrip` means historical receipt witness/meta fields may move to `RECEIPT-COLDSTORE.json` only when `tools/check_receipt_coldstore_roundtrip_contract.py` can restore the exact receipt and `tools/check_receipt_coldstore_mutation_canaries.py` proves representative payload, key, hot-overlap, current-key, and savings mutations fail. This is not a deletion court, receipt replacement, witness court, or cold-payload authority.
