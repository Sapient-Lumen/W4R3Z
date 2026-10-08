# Component license ledger — rev0866 representation clarification

The aggregate component counts below are inherited canonical-ledger counts; they do not mean the partial overlay physically carries those payloads. See `AUDIT/PATCH_CORPUS_EXACT_RECOVERY_REV0866.json` for exact/mismatched/missing materialization.

One narrow file-level conclusion is now recorded: exact upstream `sources/pact/PACT_workdir/eval_real_registry_scan/servers_README.md` is `CC-BY-4.0`, with evidence and attribution in `RIGHTS/MCP_SERVERS_README_RECOVERY_REV0865.json`. PACT and the archive remain `NOASSERTION`.

---

# Component license ledger and rights-readiness blocker

This is a release-readiness surface, not a license grant.

- Status: `publication_blocked_pending_rights_decision`
- Decision required before publication: `true`
- Root LICENSE/COPYING/NOTICE present: `false`
- RO-Crate root license value: `NOASSERTION`
- License-reference integrity status: `license_references_locally_resolved`
- Missing/outside local license references: **0**
- Observed files under component paths: **4046**
- Observed bytes under component paths: **97360690**

## Remaining blocking finding

### `missing_root_license_or_notice` — `blocker`

No root `LICENSE`, `COPYING`, or `NOTICE` is present. Archive-wide redistribution rights are therefore not granted. The owner must choose an archive-level policy and component decisions before publication metadata can be promoted.

## Component table

| Component | Files | Bytes | License concluded | Status |
| --- | ---: | ---: | --- | --- |
| `core_governance` | 4 | 33474 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |
| `papers` | 16 | 1967154 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |
| `ctg` | 92 | 3140421 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |
| `docf` | 694 | 13953016 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |
| `pact` | 648 | 26747613 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |
| `ocf_llm` | 2222 | 28862450 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |
| `streamfold` | 83 | 2778263 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |
| `zkrtp` | 193 | 18902244 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |
| `validators_and_scripts` | 94 | 976055 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |

The PACT count increases by one exact upstream `LICENSE` file. That repairs reference integrity only; PACT remains `NOASSERTION` because the transition file is contribution/category-specific and the broader component provenance is unresolved.
