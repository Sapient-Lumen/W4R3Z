# Rights decision packet — rev0863

This is a decision packet, not a license grant and not legal advice. It converts the existing mechanical rights evidence into the smallest set of human decisions needed before publication.

## Current block

- Status: `publication_blocked_pending_rights_decision`
- Root LICENSE/COPYING/NOTICE present: `False`
- RO-Crate root license value: `NOASSERTION`
- Missing/outside local license reference count: `1`
- Components: `9`

## Blocking findings

- `missing_root_license_or_notice` (blocker): No root LICENSE/COPYING/NOTICE file is present; archive-wide redistribution rights are not granted. Repair: Add root LICENSE and NOTICE, then update RO-Crate and component ledger license conclusions.
- `missing_local_license_reference_targets` (blocker): 1 shipped local LICENSE/COPYING/NOTICE reference target(s) are missing or outside the archive. Repair: Add the pinned upstream license/notice file(s), or remove/annotate the unresolved local reference after human rights review.

## Component decision table

| Component | Files | Bytes | License concluded | Review status |
| --- | ---: | ---: | --- | --- |
| `core_governance` | 4 | 33474 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |
| `papers` | 16 | 1967154 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |
| `ctg` | 92 | 3140421 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |
| `docf` | 694 | 13953016 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |
| `pact` | 647 | 26735386 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |
| `ocf_llm` | 2222 | 28862450 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |
| `streamfold` | 83 | 2778263 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |
| `zkrtp` | 193 | 18902244 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |
| `validators_and_scripts` | 94 | 976055 | `NOASSERTION` | `blocked_pending_owner_or_upstream_license_decision` |

## Owner/upstream questions

1. What archive-level license, if any, applies to owner-authored EvidenceVault governance, scripts, papers, and generated evidence?
2. Which components are owned by the archive owner versus copied from upstream projects?
3. For each upstream-derived component, which upstream license file and copyright notice should be shipped?
4. How should the missing PACT LICENSE reference at sources/pact/PACT_workdir/eval_real_registry_scan/LICENSE be resolved?
5. Which files/components must be excluded rather than licensed?
6. Who are the citable authors/contributors, and what release/DOI identity should be used after rights closure?

## Minimum repair after decisions

Do not add a root `LICENSE`, `NOTICE`, SPDX conclusion, or RO-Crate license assertion until the owner/upstream decision is explicit. After the decision, regenerate the rights ledger, SPDX, RO-Crate, and citation/authorship bridge from the same source table.

## Non-claims

This packet does not grant redistribution rights, does not conclude component licenses, does not replace human review, and does not make the datacube publication-ready.
