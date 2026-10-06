# Package identity audit

This generated surface exposes stale package-identity spillover that can hide outside the landing/currentness mesh.

- Revision: `rev0374`
- Bundle: `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`
- Resolved question: `OQ-0265`
- Live successor: `OQ-0266`
- Failures: `0`

## Non-claim
package-identity-court, metadata-sovereign, release-name-tribunal, license-revision-notary, current-key-senate, checksum-authority, manifest-court, and identity-spillover-board are forbidden; this surface detects stale package identity spillover but does not certify semantic truth, license interpretation, or continuation authority.

## Repaired findings
- `rev0328-license-stale-release-line` — LICENSE began with 'DelayBasin research archive release rev0327' inside the rev0328 package while the weaker external metadata check still passed because rev0328 appeared elsewhere. Repair: rev0329 requires external metadata to contain only the current revision token and requires the LICENSE first line to name the current package revision.
- `rev0328-path-alias-current-revision-stale` — PATH-ALIAS-LEDGER.json carried current_revision=rev0327 while revision=rev0328; the prior currentness audit did not scan this root metadata spillover surface. Repair: rev0329 sets PATH-ALIAS-LEDGER.current_revision to the current revision and adds package-identity auditing over root JSON current-key spillover.

## Counts
- `release_identity_rows`: `5`
- `json_revision_rows`: `16`
- `current_key_rows`: `48`
- `external_metadata_rows`: `22`
- `failures`: `0`

## Scan policy
- Scope: external metadata revision/bundle tokens, strict release bundle filename components, root JSON top-level revision fields, and current/head/latest revision keys outside ledger historical rows
- Historical exclusions: previous_revision, origin_revision, older ledger item revisions, historical_witness=true subtrees, anchor.expected_head, anchor.observed_head
- Repair: fail closed on package-identity spillover; repair metadata/current-key drift without treating identity freshness as semantic authority
