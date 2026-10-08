# Frontier salience scan — 2026-03-16 (publish-surface truth)

This pass again avoided adding another top-level proposal.
The stronger move was to sharpen two existing crates whose value became much more concrete after recent crates.io changes:

- **P-0175 Trusted Publishing Tooling Kit**
- **P-0477 Cargo Publish Receipt Join Kit**

## Main judgment

The repo’s next strong move was not “another supply-chain dashboard”.
It was to sharpen the **publish-surface truth** stack.

Four current signals matter most:

1. crates.io trusted publishing now supports **GitHub Actions and GitLab CI/CD**,
2. crates can now enable **trusted-publishing-only mode**,
3. crates.io explicitly blocks some risky GitHub workflow triggers from trusted publishing,
4. and crates.io now has both **publish notifications** and a clearer **malicious-crate notification policy**, which makes it easier to distinguish routine release receipts from public incident communication.

Together, those make the missing value much more concrete:

- a **rehearsal / trigger-policy artifact** before release,
- and a **joined release receipt** after release.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0489 Cargo Build-Dir Consumer Transition Kit**
3. **P-0244 SemVer API Diff Evidence Kit**
4. **P-0431 Public Dependency Boundary Kit**
5. **P-0477 Cargo Publish Receipt Join Kit**
6. **P-0175 Trusted Publishing Tooling Kit**
7. **P-0492 Cargo Registry Auth Doctor Kit**
8. **P-0496 Cargo Vendor & Source Parity Kit**
9. **P-0435 Cargo Script Workbench Kit**
10. **P-0484 Toolchain & Target Support Contract Kit**
11. **P-0472 Docs.rs Build Parity & Evidence Kit**
12. **P-0434 Sanitizer Profile & Evidence Kit**

## Why P-0175 rose now

The earlier version of this proposal was too easy to read as “one command that does trusted publishing”.
That is not sharp enough.

The more interesting missing value is a **provider-aware release rehearsal artifact** that can survive:

- GitHub versus GitLab differences,
- blocked-trigger rules,
- trusted-publishing-only mode,
- repository / workflow / environment identity expectations,
- and mixed workspaces that have not migrated fully off tokens.

That is now timely because crates.io itself has crossed from “initial support” into “provider matrix + policy mode + trigger restrictions”.

## Why P-0477 rose now

The earlier version of this proposal already had the right instincts.
But it is now sharper to describe it as a **post-publish release-history receipt**, not a generic package audit bundle.

The important missing value is a compact artifact that joins:

- local `.crate` facts,
- registry checksum and `pubtime`,
- publish-mode labeling,
- and release-history diffs.

That became more concrete because crates.io now has richer trusted-publishing posture and routine publish notifications, while its malware-notification policy also clarifies that public incident communication is a separate lane.

## Why this pass did not widen P-0015 instead

The archive already has a good attestation/provenance lane in **P-0015 Cargo Attest**.
But broadening it further before the publish-surface lanes are sharper would make the repo more hand-wavy, not less.

The better move was to strengthen:

- trusted-publishing rehearsal,
- post-publish release receipts,
- and the lane note that keeps those distinct from provenance and registry-auth diagnosis.

## Working rule for the next few passes

Prefer upgrades that add:

- provider capability matrices,
- trigger-policy fixtures,
- joined release-history schemas,
- and sharper boundary notes for publish-surface crates.

The repo is large enough now that **release-lane honesty beats proposal count** surprisingly often.

## Sources

- crates.io development update (2026-01-21): https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io development update (2025-02-05): https://blog.rust-lang.org/2025/02/05/crates-io-development-update/
- crates.io malicious crate notification policy update: https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- RFC 3691 trusted publishing: https://rust-lang.github.io/rfcs/3691-trusted-publishing-cratesio.html
