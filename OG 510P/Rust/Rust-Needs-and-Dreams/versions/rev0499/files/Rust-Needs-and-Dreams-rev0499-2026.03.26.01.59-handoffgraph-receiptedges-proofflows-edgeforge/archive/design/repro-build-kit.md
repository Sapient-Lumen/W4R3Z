# Design: Repro Build Kit (`cargo repro`, `repro-pack/v0`)

## Goal
Make “can this Rust artifact be independently rebuilt from declared inputs?” into a reviewable, attachable truth instead of an assumption inferred from provenance, signatures, or CI success.

This kit is the rebuild-verification attachment layer inside the archive’s **Release Truth Stack**.
Read it together with:
- [`design/repro-build-lane-map.md`](./repro-build-lane-map.md)
- [`design/repro-build-pilot-program.md`](./repro-build-pilot-program.md)

## References (signals)
- Rust 1.91 release notes say **building a crate with `cargo package` should now be independently reproducible**.
  https://doc.rust-lang.org/beta/releases.html
- `cargo package` still defines a curated source-package boundary: it rewrites and normalizes `Cargo.toml`, removes `[patch]`, `[replace]`, and `[workspace]`, includes `Cargo.lock` by default, emits `.cargo_vcs_info.json`, and verifies by extracting the `.crate` and rebuilding from a pristine state.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- Cargo’s changelog shows `trim-paths` is still active work, including remapping all paths to `build.build-dir` and widening Windows/MSVC coverage.
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo’s unstable `sbom` support emits precursor JSON files for executable and linkable outputs uplifted into target or artifact directories, giving rebuild tooling better artifact-linked inputs.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- dist explicitly says users should be able to rerun the same dist invocation locally and get the same ordinary results, **not necessarily bit-level precision**.
  https://axodotdev.github.io/cargo-dist/book/
- dist’s supply-chain docs keep signing, GitHub Attestation, standalone CycloneDX output, embedded `cargo-auditable` data, and OmniBOR IDs as distinct release attachments.
  https://axodotdev.github.io/cargo-dist/book/supplychain-security/index.html
- GitHub’s docs say artifact attestations establish **where and how software was built**, can also attest SBOMs, can be verified offline, and are **not a guarantee that an artifact is secure**.
  https://docs.github.com/en/actions/concepts/security/artifact-attestations
  https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations
  https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations/verifying-attestations-offline
  https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/manage-attestations

## Core UX
### Producer / verifier
- `cargo repro capture`
  - collect subject identity, declared inputs, artifact pointers, environment summary, and lane profile
- `cargo repro run`
  - execute a rebuild in one declared compare mode
- `cargo repro compare`
  - compare rebuilt outputs against reference outputs and emit reason-coded results
- `cargo repro attach`
  - link provenance or SBOM attestation references without collapsing them into compare verdicts
- `cargo repro pack`
  - bundle everything as `repro-pack/v0`

## Lane posture (v0)
Repro Build must keep these lanes distinct even when one pack carries several of them:
1. **source-package reproducibility** (`cargo package` subject)
2. **final-artifact rebuild compare** (binary/archive/installer subject with explicit compare mode)
3. **provenance attestation** (where/how built)
4. **SBOM-attestation / inventory attachment**
5. **offline verification bundle**
6. **lifecycle / supersession posture**

## Core artifacts
### `repro-subject/v0`
- subject kind (`.crate`, binary, archive, installer, release asset)
- release subject / package selection / target triple / profile
- compare-mode class (`bitwise`, `normalized`, `attachment-only`, etc.)
- source snapshot / tag / commit
- reference artifact pointers and checksums

### `repro-run-report/v0`
- toolchain / environment summary
- inputs discovered / missing / substituted
- native tooling / SDK notes
- execution outcome and incompleteness markers
- offline-versus-online verification posture when relevant

### `repro-compare-report/v0`
- verdict: `MATCH` / `MISMATCH` / `INCONCLUSIVE` / `UNSUPPORTED`
- strength class for the claim
- diff reasons:
  - path leakage
  - timestamp / archive-order drift
  - debug-info differences
  - build-script / generated-code drift
  - native-tool / linker / SDK differences
  - post-processing differences
  - unknown

### `repro-attestation-link/v0`
- attached provenance-attestation references
- attached SBOM-attestation or inventory references
- signer / predicate / issuer notes
- explicit `attachment-only` posture when no compare result is present

### `repro-pack/v0`
- subject
- run report(s)
- compare report(s)
- optional attestation links
- optional offline bundles / trusted-root notes
- optional raw attachments and diff summaries
- lifecycle notes when evidence is superseded, deleted, or retained only historically

## Design rules
- **Do not equate provenance with equivalence.** Attestations and signatures may be attached, but the rebuild verdict remains distinct.
- **Do not equate SBOM attachment with rebuild evidence.** Inventory travels with release truth but does not replace compare results.
- **Keep compare mode explicit.** A bitwise binary compare is not the same claim as a normalized archive compare or a package-only reproducibility check.
- **Keep build strength explicit.** A local replay is not the same as a constrained or independent rebuild.
- **Report native involvement honestly.** Build scripts, SDKs, system libraries, and linkers are first-class participants in divergence.
- **Offline bundles are inputs, not magic.** Imported bundle and trusted-root posture must stay explicit.
- **Lifecycle status matters.** Historical, superseded, or deleted attestations/evidence must not silently retain the same consumer meaning.
- **Prefer diff reasons over badge theater.** The point is to explain mismatch, not merely color a box green.

## Integration points
- **Release Pipeline Kit:** attach `repro-pack/v0` into `release-pack/v0` when available.
- **Signed Binaries Kit:** complementary but distinct; signatures prove issuer integrity, not reproducibility.
- **SBOM Evidence / Inventory Evidence:** attach precursor/export/recovery facts without collapsing them into rebuild truth.
- **Policy Kit / Trust Signals Kit:** can require rebuild evidence or attestation posture for selected release classes.
- **Incident Kit:** post-incident rebuild checks become attachable evidence instead of shell transcripts.
- **Airgap Kit:** owns restricted-network import posture; Repro Build owns the bounded verification evidence once the inputs are present.

## Hard problems (explicitly scoped)
1. **Native dependencies are real**
   - v0 must report native-tool / SDK involvement honestly.
2. **Not every artifact should be compared bitwise**
   - signing, notarization, packaging, and installer wrapping may require boundary-specific compare rules.
3. **One build is not evidence**
   - provenance can describe one workflow run; reproducibility requires comparison.
4. **Do not overclaim hermeticity**
   - report strong and weak modes separately.
5. **Offline trust is bounded**
   - imported roots and bundles have freshness and lifecycle limits.

## Evaluation plan
Follow [`design/repro-build-pilot-program.md`](./repro-build-pilot-program.md):
1. source-package lane,
2. pure-Rust final-binary lane,
3. native / `build.rs` lane,
4. dist-managed release-asset lane,
5. provenance + SBOM attestation lane,
6. offline verification + lifecycle lane.

Success bar:
- maintainers can tell **which reproducibility claim** is being made,
- consumers can tell whether a result came from comparison or only from attached attestations,
- offline verification is practical but bounded,
- and release tooling can attach the result without inventing another one-off format.
