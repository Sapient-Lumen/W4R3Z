# Release-hardening witnesses, receipt-delta coherence, path portability, and scored reentry canaries

This is the compact successor surface for `OQ-0218`.

`rev0324` resolves `OQ-0218` by treating transported closeout-history portability expiry as a release-hardening problem, not as an occasion to build a tombstone-history review layer.  Closeout history may expire by horizon, use exhaustion, successor supersession, source revocation, quarantine expiry, or release-evidence failure.  Its remaining role is warning, audit, or bounded successor context unless a public canary failure proves that a stronger surface is necessary.

## Governed exact-token family

Family: `release_hardening_state` / `WVF-0123`.

Allowed tokens:

- `receipt-delta-coherent` — the receipt, status, manifest, compact packets, and open-question tail name the same current revision, resolved question, successor question, and current method surface.
- `path-portable-bounded` — archive-relative paths and filename components stay below extraction-risk thresholds instead of encoding the whole genealogy in a path.
- `release-manifest-hashed` — a per-file manifest, checksum surface, provenance surface, deterministic packaging path, and sidecar bundle hash support release verification.
- `schema-backed` — public JSON surfaces have minimal external schemas so an importer can check shape before executing local Python.
- `assay-scored` — at least one reentry assay records packet inputs, expected answers, observed answers, and negative canaries.
- `metadata-exposed` — boring external metadata surfaces expose citation, rights posture, research-object metadata, CodeMeta, and SPDX-style package inventory.
- `mixed-release-hardening` — more than one of the above is load-bearing and none should be inflated into a review court.

Excluded synonyms:

- `tombstone-history-review-layer`
- `portable-closeout-history-expiry-court`
- `warning-renewal-by-closeout-history`
- `successor-review-senate`
- `redaction-vault-by-history-portability`
- `self-certifying-release-court`
- `checksum-tribunal`
- `canary-review-board`

## Expiry/currentness rule

The selected `mixed-release-hardening` token means the archive carries prior closeout-history portability only as bounded evidence.  Currentness comes from receipt-delta coherence, path-portability bounds, integrity manifests, public metadata, schemas, backlog triage, link-integrity policy, and a scored self-sufficiency canary.  None of those surfaces renews the closed history by itself.

## Guard set

The public guard set is deliberately procedural and non-juridical:

- `tools/check_receipt_delta_coherence.py` catches stale delta fields like a current receipt that still cites an older resolved question, older method, or older witness checker.
- `tools/check_path_portability_contract.py` enforces practical archive-relative path and filename-component limits.
- `tools/release_integrity_lib.py` provides sorted file hashing and provenance helpers.
- `tools/gen_release_integrity.py` emits `FILE-MANIFEST.json`, `CHECKSUMS.sha256`, and `RELEASE-PROVENANCE.json` from sorted release paths.
- `tools/check_release_integrity_contract.py` verifies the generated integrity surfaces against current files.
- `tools/check_external_metadata_contract.py` verifies `LICENSE`, `CITATION.cff`, `codemeta.json`, `ro-crate-metadata.json`, and `SBOM.spdx.json` are present and current.
- `tools/check_json_schema_surface_contract.py` verifies the public JSON schemas and their required keys.
- `tools/check_frontier_backlog_contract.py` keeps the next five frontier pressures visible without turning them into authority.
- `tools/check_link_integrity_policy_contract.py` records citation/link checking as policy, not a false live-check claim.
- `tools/check_self_sufficiency_assay_contract.py` requires the latest assay to be scored, canary-bearing, and bounded.
- `tools/check_llm_runbook_current_cue_alignment.py` keeps the practical LLM runbook cue aligned with the current receipt.
- `tools/check_release_hardening_witness_contract.py` ties this surface to the receipt, vocabulary, ledgers, and current witness slot.

## Scored reentry canary

`SELF-SUFFICIENCY-LEDGER.json#SA-0014` records the first scored assay.  Its role is to expose false green: a landing-only packet should identify the current head and live open question but should not overclaim derivative packets as canon; a compact packet should recover the current posture and boundaries; a full-archive packet should improve evidence depth without licensing tombstone-history review machinery.

Negative canaries are explicit: wrong head, wrong live open question, stale resolved question, treating derivative aids as canon, inventing a review court, losing quarantine boundaries, overclaiming causal mechanism, and claiming minimality has been proven.

## Fail-closed rule

When evidence is unclear, prefer ordinary release hardening, warning-only history, or quarantine.  Do not promote a new governance layer merely because an integrity surface, checksum, schema, backlog row, or assay row exists.

## Successor

`OQ-0219` asks when scored canaries should count as self-sufficiency evidence without becoming a continuation review court.
