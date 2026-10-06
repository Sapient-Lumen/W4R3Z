# Package identity spillover witnesses

`rev0329` resolves `OQ-0223` by narrowing currentness block/repair into a package-identity spillover audit. The concrete audit finding is deliberately small and mechanical: `rev0328` had a green lint suite while `LICENSE` still opened with `rev0327` and `PATH-ALIAS-LEDGER.json#current_revision` still carried `rev0327`. `PACKAGE-IDENTITY-AUDIT.json` makes that class of stale identity spillover visible without turning package names, license headers, manifests, hashes, or current-key freshness into semantic authority.

## Controlled family

- Handle: `WVF-0128`
- Family: `package_identity_state`
- Selected token: `mixed-package-identity`

Allowed tokens:

- `external-metadata-synchronized`
- `root-json-revision-synchronized`
- `current-key-spillover-detected`
- `license-revision-repaired`
- `path-alias-current-repaired`
- `package-identity-non-authoritative`
- `mixed-package-identity`

Excluded machinery: `package-identity-court`, `metadata-sovereign`, `release-name-tribunal`, `license-revision-notary`, `current-key-senate`, `checksum-authority`, `manifest-court`, and `identity-spillover-board`.

## Audit/refactor

The refactor adds `PACKAGE-IDENTITY-AUDIT.json` and `docs/00-meta/package-identity-audit.md` as generated visibility surfaces. They scan external metadata revision/bundle tokens, root JSON top-level `revision` fields, and high-risk `current_revision` / `latest_revision` / `current_head` / `head_revision` keys across root machine surfaces. The scan intentionally excludes historical ledger row revisions, `previous_revision`, `origin_revision`, anchor-underlier fields, and `historical_witness=true` subtrees.

The repair is not a new authority layer. A package-identity failure may block packaging or require metadata/current-key repair; it may not prove semantic correctness, license interpretation, archive minimality, or continuation authority.

## Required validation surfaces

- `tools/check_package_identity_witness_contract.py`
- `tools/check_package_identity_audit_contract.py`
- `tools/gen_package_identity_audit.py`
- `tools/check_external_metadata_contract.py`
- `tools/check_json_schema_surface_contract.py`
- `tools/check_current_witness_receipt_slot.py`

## Repaired false-green seams

- `rev0328-license-stale-release-line` — `LICENSE` named `rev0327` on line 1 inside the `rev0328` package.
- `rev0328-path-alias-current-revision-stale` — `PATH-ALIAS-LEDGER.json#current_revision` named `rev0327` while the same surface's `revision` field named `rev0328`.

## Successor pressure

`OQ-0224` inherits only the narrow question of when package-identity audits can compact, retire, or hand off their repaired findings without becoming an identity court.
