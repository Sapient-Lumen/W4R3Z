# Cargo Future-Incompat Triage Kit fixtures

These fixtures are for **P-0478 Cargo Future-Incompat Triage Kit**.

The point of this fixture pack is to freeze the support layer **above** Cargo's built-in future-incompat reporting:

- one capture lock,
- one finding snapshot vocabulary,
- one owner / waiver / release ledger family,
- one evidence-source receipt,
- and scenario packs where the hard part is ownership, expiry, release timing, or toolchain-era reclassification.

These fixtures should stay distinct from:

- Cargo's own report display and storage,
- broad build-analysis history warehousing,
- lint-edit / fix orchestration,
- resolver explanation,
- and semver / upgrade-proof crates.

Scenario families in this pass:
- `transitive_new_warning_unknown_owner/`
- `waiver_expires_on_release_branch/`
- `toolchain_bump_const_eval_reclassification/`


Additional scenario families in this pass:
- `allow_suppressed_future_incompat_still_counts_as_latent_debt/`
- `package_filtered_recall_hides_workspace_blocker_without_visibility_receipt/`

New schema pair in this pass:
- `finding-visibility.report.schema.json`
- `suppression-basis.receipt.schema.json`
