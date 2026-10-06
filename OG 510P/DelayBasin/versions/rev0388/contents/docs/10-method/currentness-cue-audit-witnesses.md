# Currentness-cue audit witnesses

This is the compact successor surface for `OQ-0222`.

`rev0328` resolves `OQ-0222` by treating validation-toolchain manifests as bounded admission evidence while adding a generated currentness-cue audit for the false-green seam found in `rev0327`: `SURFACE-STATUS.json` carried a stale terse `current_revision` value even though higher-level bundle and latest-head cues were green. The repair is intentionally narrow. Validation manifests, release hashes, and currentness audits may expose stale admission cues, but none of them certify semantic truth, continuation authority, or archive minimality.

## Governed exact-token family

Family: `currentness_cue_state` / `WVF-0127`.

Allowed tokens:

- `stale-current-key-detected` — a terse current/head/latest key drifted while broader lint still passed.
- `status-field-synchronized` — high-risk `SURFACE-STATUS.json` revision and bundle fields agree with the receipt and manifest.
- `landing-cue-synchronized` — landing surfaces agree on current revision, bundle, resolved question, successor question, and canon additions.
- `generated-audit-backed` — `CURRENTNESS-CUE-AUDIT.json` and `docs/00-meta/currentness-cue-audit.md` are generated from current underliers and fail closed on stale cues.
- `compact-surface-resynced` — compact derivative surfaces project the current revision and successor question after the audit refactor.
- `currentness-non-authoritative` — currentness evidence can block a release or trigger repair, but it cannot certify semantic correctness or continuation authority.
- `mixed-currentness-cue` — stale-key detection, status-field synchronization, landing-cue synchronization, generated audit evidence, compact resync, and non-authority boundaries are all load-bearing.

Excluded synonyms:

- `currentness-cue-court`
- `latest-head-tribunal`
- `status-sovereign`
- `bundle-revision-notary`
- `recency-court`
- `landing-cue-authority`
- `green-lint-currentness-waiver`
- `current-key-senate`

## Admission-evidence rule

Validation-toolchain manifests count as admission evidence when they expose exact tool order, script hashes, support-module hashes, and entrypoint fingerprints for the current release. They do not certify that the methods are true. Currentness-cue auditing adds one more admission-evidence boundary: terse current/head/latest keys must agree with the receipt and release manifest before a package can claim ordinary currentness.

The repaired `SURFACE-STATUS.current_revision` field is the canary. `rev0327` had enough high-level current cues to pass, but this field was stale. `rev0328` records the finding and makes the stale key visible through `CURRENTNESS-CUE-AUDIT.json`, `tools/check_currentness_cue_audit_contract.py`, and the strengthened `tools/check_surface_status_current_key_coherence.py`.

## Currentness-cue audit

`CURRENTNESS-CUE-AUDIT.json` is generated evidence. It records:

- expected revision, bundle, stamp, slug, resolved question, successor question, and resolution id;
- selected `SURFACE-STATUS.json` current/head/latest revision and bundle fields;
- landing-surface latest-revision cues;
- compact/root JSON revision cues;
- a high-risk current-key scan;
- the known repaired `rev0327` stale-current-key finding.

The audit has no authority over canon. Canon remains in the receipt, status surface, open-question registry, ledgers, and method surfaces.

## Guard set

- `tools/gen_currentness_cue_audit.py` generates `CURRENTNESS-CUE-AUDIT.json` and `docs/00-meta/currentness-cue-audit.md` from the current receipt, manifest, status, and landing cues.
- `tools/check_currentness_cue_audit_contract.py` recomputes the audit and fails if any currentness cue is stale.
- `tools/check_currentness_witness_contract.py` ties this method, vocabulary family, receipt slot, self-sufficiency assay, currentness audit, and successor question together.
- `tools/check_surface_status_current_key_coherence.py` now directly checks `SURFACE-STATUS.current_revision`, the field missed by `rev0327`.
- `tools/check_current_witness_receipt_slot.py` keeps the current witness family explicit in the receipt.

## Successor

`OQ-0223` asks when currentness-cue audits should block or repair a release without becoming a currentness court, recency tribunal, or status sovereign.
