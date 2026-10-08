# Rev0811 lineage

## Exact parent archive

`AnonSync-rev0810-2026.07.17.12.30-stickyowner-resetfence-privatepermit-transactionaudit.zip`

SHA-256:

`99da2dc69724cd085b5739f6913509b151f57383b464264871267a82e500c0ba`

Rev0811 was developed from the exact extracted file bytes of that archive. No
compiled object, generated build product, or reconstructed source was used as
the parent.

## Parent release-state defect

The parent archive is a real byte parent but is not verifier-clean as rev0810:

- the ZIP root is
  `AnonSync-rev0810-2026.07.17.12.30-stickyowner-resetfence-privatepermit-transactionaudit/`
  rather than `AnonSync/`;
- `RELEASE_GATE.json` and README declare rev0809;
- `MANIFEST.sha256` omits `MANIFEST.rev0810.sha256`, `REVISION-0810.md`, and the
  two `rev0810_sticky_owner_reference/` files;
- the sticky-owner reference is outside the production build and test graph.

Verifier results retained in this evidence directory:

| Parent view | Result |
|---|---:|
| ZIP, no expected revision | 7/17 |
| ZIP, expected rev0810 | 7/18 |
| Extracted directory, no expected revision | 19/20 |
| Extracted directory, expected rev0810 | 19/21 |

The extracted source remains suitable as an exact parent. Rev0811 repairs the
release state rather than claiming that the parent passed a gate it did not.

## Source descent

The exact active source delta is stored at:

`REVISION_EVIDENCE/rev0811/SOURCE_DIFF_rev0810_to_rev0811.patch`

Twelve active implementation files changed. No CMake file and no third-party
source changed. New revision metadata and evidence are additive and are not
represented as parent source changes in the source-only patch.

## Revision identity

- conversation predecessor: rev0810;
- exact byte parent: uploaded rev0810 archive above;
- parent embedded release identity: rev0809;
- new canonical release identity: rev0811;
- build products used as source: no;
- third-party source changed: no;
- lineage proof: parent archive SHA-256, exact extraction, per-file source hashes,
  unified source patch, active implementation projection, exact final manifest,
  and final package verification.
