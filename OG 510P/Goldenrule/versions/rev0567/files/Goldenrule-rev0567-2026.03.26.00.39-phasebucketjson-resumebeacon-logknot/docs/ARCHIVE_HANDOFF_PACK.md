# Archive Handoff Pack

Compact hash-bearing manifest for the blocked-session archive control plane: one primary reentry target plus the exact doc/report pairs and verify/refresh commands that future inheritors should trust first.

## Headline findings

- The compact archive handoff pack spans 22 retained files and 147928 raw bytes (0.141 MiB), so the exact blocked-session control stack can be verified without reopening the wider tree.
- The primary open target stays `docs/ARCHIVE_REENTRY_CARD.md` with verify `make test-archive-reentry-card` and refresh `make update-archive-reentry-card`; doc_sha256=`27e8056ff5189e492cf954b6f624e27d2bd6e969ccb8db1e09ccbc0971c51583`.
- The blocked local move remains `make cloudtainer-shadow-pass-medium`, and the first Rust foothold remains `git apply artifacts/patches/rust_external_test_shards/01_fsm_grim_trigger_probe.patch` then `cargo test -p gr_engine --test probe_run lift_fsm_strategy_family_lift_first_seed -- --exact`.
- The package steward still settles through `make settle-archive-truth` and cuts through `python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"`, while the exact external reopen winner remains `Goldenrule-rev0565-2026.03.25.23.58-offlineproofladder-cachetruth-nightsignal.zip`.
- The pack itself is now executable: `python3 scripts/tools/verify_archive_handoff_pack.py` verifies every retained doc/report hash in the compact control stack from one command.
- The authoritative external winner now has a one-command verifier too: `python3 scripts/tools/verify_authoritative_archive_zip.py` proves the winning zip path, authority rule, and live bytes together.
- The cap-first markdown diet pack would still recover 1398919 bytes, which is 9.457x this whole hash-bearing handoff pack.
- The sibling-lane hazards that justify revision-first authority remain explicit in-pack: duplicate_revision_count=1 and chronology_inversion_count=0.

## Primary entry target

- primary_open_path: `docs/ARCHIVE_REENTRY_CARD.md`
- primary_verify_command: `make test-archive-reentry-card`
- primary_refresh_command: `make update-archive-reentry-card`
- manifest_sha256: `d27731b6e27a09b13d7d2528a43663b9a5dfb5baaf87368549328556097e56d5`
- pack_file_count: `22`
- pack_raw_bytes: `147928` (0.141 MiB)

## Ordered group manifest

### archive_head_reentry

- role: `current_head_entry`
- doc_path: `docs/ARCHIVE_REENTRY_CARD.md`
- doc_bytes: `6333`
- doc_sha256: `27e8056ff5189e492cf954b6f624e27d2bd6e969ccb8db1e09ccbc0971c51583`
- report_path: `artifacts/reports/archive_reentry_card.json`
- report_bytes: `12839`
- report_sha256: `59eb1da9b6b079e68ae4d4da9d78c5fd7263c43e0171159a32bef728617ffee8`
- verify_command: `make test-archive-reentry-card`
- refresh_command: `make update-archive-reentry-card`
- intent_summary: open the current head card first and recover the exact blocked-cloudtainer, first-machine, and package-steward branches without rescanning neighboring docs
- outcome_summary: current head, blocked-cloudtainer first move, first Rust foothold, and package closeout route remain path-addressable from one compact entry surface

### blocked_cloudtainer

- role: `blocked_cloudtainer_operator`
- doc_path: `docs/CLOUDTAINER_RUST_RECOVERY_CARD.md`
- doc_bytes: `5891`
- doc_sha256: `132a97db5aafd9b7b9f4e6cacf14887515c0d8346e1002c9272fb6aee40d3fc4`
- report_path: `artifacts/reports/cloudtainer_rust_recovery_card.json`
- report_bytes: `6851`
- report_sha256: `2d08661c64e200dc9c9901da39342905b3637f77038e6d3bf56fd219d1c3b2d5`
- verify_command: `make test-cloudtainer-rust-recovery-card`
- refresh_command: `make update-cloudtainer-rust-recovery-card`
- intent_summary: decide whether in-place Rust recovery is even possible here or whether to stay on the static lanes
- outcome_summary: the current cloudtainer stays on the static lane and the local first move remains the shadow-pass medium profile

### first_rust_machine

- role: `first_rust_capable_implementor`
- doc_path: `docs/RUST_COMEBACK_EXECUTION_CARD.md`
- doc_bytes: `15239`
- doc_sha256: `672fe554a02f2cce0982503d3c33f922c812adf92e056b4b7969c0fe0082666f`
- report_path: `artifacts/reports/rust_comeback_execution_card.json`
- report_bytes: `19225`
- report_sha256: `6d5aa8e4d0ea5ccad991f2046b81f09bc0db0010971512d22991ecedbfacd0ef`
- verify_command: `make test-rust-comeback-execution-card`
- refresh_command: `make update-rust-comeback-execution-card`
- intent_summary: land the first patch shard and run the exact first witness on the first machine that can execute cargo tests
- outcome_summary: the quick foothold stays one apply plus one exact witness and the full closure still ends at the final dual-lane shard

### package_cut

- role: `package_cut_steward`
- doc_path: `docs/ARCHIVE_PACKAGE_CUT_CARD.md`
- doc_bytes: `10787`
- doc_sha256: `fdd161db8fe9e75a6ffae48ee6a2f16e7d9a15e1b7c8f58ff681ab23e17bfccd`
- report_path: `artifacts/reports/archive_package_cut_card.json`
- report_bytes: `12448`
- report_sha256: `d0990e0defe3441bd788265a41b63591c3225c5c0f0ca715b632bc63494d090d`
- verify_command: `make test-archive-package-cut-card`
- refresh_command: `make update-archive-package-cut-card`
- intent_summary: settle the archive truth surfaces in the right order before cutting the next revision zip
- outcome_summary: the package steward retains the expected-gate settle wrapper, fixed-point size and triage pair, and canonical cut command

### external_zip_lineage

- role: `external_package_lane_audit`
- doc_path: `docs/ARCHIVE_ZIP_LINEAGE_CARD.md`
- doc_bytes: `2775`
- doc_sha256: `a7b562571e17d6f75595bf8805b254d86819f494d24886d7d804a59db646c660`
- report_path: `artifacts/reports/archive_zip_lineage_card.json`
- report_bytes: `4148`
- report_sha256: `87101d910f9448153697fad8a47b5f700b47c24a1c4d41a139eaa874d54d9ba3`
- verify_command: `make test-archive-zip-lineage-card`
- refresh_command: `make update-archive-zip-lineage-card`
- intent_summary: show the visible sibling zip chain and detect duplicate revision labels or missing current-root zips
- outcome_summary: the sibling zip lane stays aligned to the live root and keeps duplicate revision hazards explicit instead of implicit

### external_zip_chronology

- role: `external_package_lane_ordering`
- doc_path: `docs/ARCHIVE_ZIP_CHRONOLOGY_CARD.md`
- doc_bytes: `3483`
- doc_sha256: `09ea5a550f70b1f6295f9759de29d210ec9ec2e75fbdc77ea2b73a9ddee4c49a`
- report_path: `artifacts/reports/archive_zip_chronology_card.json`
- report_bytes: `5451`
- report_sha256: `8ac9c46e8346cd313d97cf0d75b62ac3e21fbc9eb5179150fa0fc39810e92ac7`
- verify_command: `make test-archive-zip-chronology-card`
- refresh_command: `make update-archive-zip-chronology-card`
- intent_summary: keep timestamp inversions across revision order explicit so head authority stays revision-first
- outcome_summary: the sibling lane still records timestamp regressions that would mislead anyone choosing “latest timestamp” instead of “highest revision”

### external_zip_authority

- role: `authoritative_reopen_target`
- doc_path: `docs/ARCHIVE_ZIP_AUTHORITY_CARD.md`
- doc_bytes: `2797`
- doc_sha256: `4ba8be18109ac0f8fc8fc820bbf5bc80f570a67c15ebb6550a86372fc6e3a63d`
- report_path: `artifacts/reports/archive_zip_authority_card.json`
- report_bytes: `5167`
- report_sha256: `3aedc74adcd6078cb4d4217aca2feedff1d99a07ec46b33384906fb473288511`
- verify_command: `make test-archive-zip-authority-card`
- refresh_command: `make update-archive-zip-authority-card`
- intent_summary: emit the exact sibling zip path to reopen after duplicate revisions and chronology inversions are taken into account
- outcome_summary: the exact external zip winner remains machine-emittable instead of guessed from filenames by hand

### external_zip_digest

- role: `authoritative_zip_bytes`
- doc_path: `docs/ARCHIVE_ZIP_DIGEST_CARD.md`
- doc_bytes: `3105`
- doc_sha256: `9be0b4bc4778fd9bc63699a8cdcb2d816130a368740e38a031f8b5d11a7a255c`
- report_path: `artifacts/reports/archive_zip_digest_card.json`
- report_bytes: `3595`
- report_sha256: `316a0d6225714b54a6bf43b8c1a907991a5a97dca065af15a21cac0891edf1e5`
- verify_command: `make test-archive-zip-digest-card`
- refresh_command: `make update-archive-zip-digest-card`
- intent_summary: publish the authoritative sibling zip size and sha256 so the winning external package bytes can be verified directly
- outcome_summary: the exact external zip winner is not only locatable but also hash-verifiable from one compact control-plane surface

### external_zip_size_truth

- role: `authoritative_zip_size_truth`
- doc_path: `docs/ARCHIVE_ZIP_SIZE_TRUTH_CARD.md`
- doc_bytes: `2554`
- doc_sha256: `dd54b21371493984e03147be49c2196808a240eba4f73b0a5dc0ed3aa4001fc4`
- report_path: `artifacts/reports/archive_zip_size_truth_card.json`
- report_bytes: `3987`
- report_sha256: `145bb4bb0484154d3a7774b93ac98a8623cd415c3e28404df99376adbaaffa36`
- verify_command: `make test-archive-zip-size-truth-card`
- refresh_command: `make update-archive-zip-size-truth-card`
- intent_summary: keep the internal packaged-size proxy distinct from the exact sibling zip bytes and calibrate the gap from the immutable predecessor zip
- outcome_summary: the current head is no longer allowed to pretend its internal proxy is the same as the final external zip bytes

### revision_cut

- role: `next_revision_naming`
- doc_path: `docs/ARCHIVE_REVISION_CUT_CARD.md`
- doc_bytes: `3446`
- doc_sha256: `cf17e99164a8a5d98052421c61cbe78891b6cb96d01c3fb3a4910e5e25185b1f`
- report_path: `artifacts/reports/archive_revision_cut_card.json`
- report_bytes: `4205`
- report_sha256: `26113bc8ee57062928810d444d947b37a847455c94d48a1e004ab3e3e0545876`
- verify_command: `make test-archive-revision-cut-card`
- refresh_command: `make update-archive-revision-cut-card`
- intent_summary: derive the next safe revision label and normalized root and zip stem before the cut
- outcome_summary: the next safe revision label remains explicit and the canonical cutter need not improvise root or zip stems by hand

### byte_diet

- role: `archive_byte_diet`
- doc_path: `docs/ARCHIVE_BYTE_TRIAGE_CARD.md`
- doc_bytes: `5543`
- doc_sha256: `d34aa26b800feb5fdc7ed432d5fc21db2bc02d01888380c71194af3fe7f711d6`
- report_path: `artifacts/reports/archive_byte_triage_card.json`
- report_bytes: `8059`
- report_sha256: `ad0bd2725f877f4f2864e3d5d75d9a7738d232de6b5285bc8d0474a5740d3e51`
- verify_command: `make test-archive-byte-triage-card`
- refresh_command: `make update-archive-byte-triage-card`
- intent_summary: recover bytes from the smallest safe markdown compaction pack instead of shaving the compact blocked-session handoff surfaces
- outcome_summary: the first safe diet pack still outweighs the protected blocked-session control plane and remains the correct place to save bytes first

## Direct witnesses

- blocked_cloudtainer_primary_command: `make cloudtainer-shadow-pass-medium`
- first_rust_apply_hint: `git apply artifacts/patches/rust_external_test_shards/01_fsm_grim_trigger_probe.patch`
- first_rust_exact_witness_command: `cargo test -p gr_engine --test probe_run lift_fsm_strategy_family_lift_first_seed -- --exact`
- package_settle_command: `make settle-archive-truth`
- canonical_cut_command: `python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"`
- handoff_pack_verify_command: `python3 scripts/tools/verify_archive_handoff_pack.py`
- authoritative_zip_resolver_command: `python3 scripts/tools/resolve_authoritative_archive_zip.py --emit zip-path`
- authoritative_zip_verify_command: `python3 scripts/tools/verify_authoritative_archive_zip.py`
- authoritative_zip_basename: `Goldenrule-rev0565-2026.03.25.23.58-offlineproofladder-cachetruth-nightsignal.zip`
- next_revision_label: `rev0566`
- cap_first_markdown_recoverable_bytes: `1398919`
- duplicate_revision_count: `1`
- chronology_inversion_count: `0`

## Source reports

- `artifacts/reports/archive_reentry_card.json`
- `artifacts/reports/cloudtainer_rust_recovery_card.json`
- `artifacts/reports/rust_comeback_execution_card.json`
- `artifacts/reports/archive_package_cut_card.json`
- `artifacts/reports/archive_zip_lineage_card.json`
- `artifacts/reports/archive_zip_chronology_card.json`
- `artifacts/reports/archive_zip_authority_card.json`
- `artifacts/reports/archive_zip_digest_card.json`
- `artifacts/reports/archive_zip_size_truth_card.json`
- `artifacts/reports/archive_revision_cut_card.json`
- `artifacts/reports/archive_byte_triage_card.json`
