# Gap: provenance and release attachments are improving faster than lane-aware rebuild verification

## Summary
Rust now has better **source-package reproducibility**, **artifact provenance**, **SBOM capture/attestation**, **artifact collection**, and **release-manifest** pieces than it had a year ago. What it still lacks is a shared, Cargo-native way to answer the harder questions without flattening them together:

- **Did the packaged source boundary reproduce?**
- **Did the shipped binary or installer independently rebuild to the same result, under what compare mode, and if not, why not?**
- **Which claims come from comparison, which come from provenance attestation, which come from SBOM attestation, and which can still be verified offline later?**

Today, teams can often:
- package crates reproducibly with `cargo package`,
- generate GitHub artifact attestations,
- attach or attest SBOMs,
- collect final artifacts into predictable release layouts,
- and ship machine-readable release manifests with dist.

But those pieces do **not** by themselves provide an independent, reviewable **rebuild verdict** or a shared map of the different lanes involved.

## Why now
- Rust 1.91 release notes say **building a crate with `cargo package` should now be independently reproducible**. That means source-package reproducibility is now a first-class upstream lane.
  https://doc.rust-lang.org/beta/releases.html
- `cargo package` still rewrites and normalizes manifests, includes `Cargo.lock` by default, emits `.cargo_vcs_info.json`, and verifies by extracting the `.crate` and rebuilding it. That is a concrete source-package subject, not just a tarball hash.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- Cargo’s `trim-paths` work is still moving, including remapping all paths to `build.build-dir` and expanding Windows/MSVC coverage. That is a reminder that final-artifact equivalence remains an active engineering seam rather than a solved fact.
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo’s unstable `sbom` support now emits precursor JSON files for executable and linkable outputs uplifted into target or artifact directories. That gives rebuild tooling stronger artifact-linked inputs than “scrape the build log”.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- dist’s introduction says the same dist invocation should be runnable locally with the same ordinary results, **not to bit-level precision**. That is a strong signal that release automation already knows “repeatable release build” and “strict equivalence” are different lanes.
  https://axodotdev.github.io/cargo-dist/book/
- dist’s supply-chain docs keep signing, GitHub Attestation, CycloneDX SBOM output, `cargo-auditable`, and OmniBOR as distinct release-side surfaces. That is exactly the environment in which a portable `repro-pack/v0` needs sharper lane discipline.
  https://axodotdev.github.io/cargo-dist/book/supplychain-security/index.html
- GitHub’s attestation docs say artifact attestations establish **where and how software was built**, can also attest SBOMs, can be verified offline, and are **not a guarantee that an artifact is secure**. That means provenance and SBOM attestations are important attachments, but not replacements for independent compare results.
  https://docs.github.com/en/actions/concepts/security/artifact-attestations
  https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations
  https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations/verifying-attestations-offline
- GitHub’s lifecycle docs say attestations should be deleted when the associated artifact no longer exists or should no longer be trusted. That makes lifecycle posture part of the real contract.
  https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/manage-attestations

## Concrete missing pieces
1. **Explicit lane identity**
   - source-package reproducibility
   - final-artifact rebuild compare
   - provenance attestation
   - SBOM-attestation / inventory attachment
   - offline verification bundle
   - lifecycle / supersession posture

2. **Declared equivalence mode**
   - bit-for-bit
   - archive-member digests
   - normalized/debug-insensitive
   - attachment-only / no-compare

3. **An honest build-input summary**
   - toolchain versions
   - target triple and profile
   - lockfile digest
   - enabled features
   - relevant build-script / proc-macro / native-tool inputs
   - whether path sanitization and SBOM precursor generation were enabled

4. **A second-build verdict with diff reasons**
   - `MATCH`
   - `MISMATCH`
   - `INCONCLUSIVE`
   - `UNSUPPORTED`
   - reason codes for path leakage, timestamps, native drift, generated-code drift, linker/debug-info variance, or post-processing differences

5. **Bounded attestation attachment**
   - provenance references that do not replace compare results
   - SBOM-attestation references that do not replace inventory truth
   - signer/predicate/issuer notes that remain explicit imports

6. **Portable offline verification bundles**
   - imported artifact copy
   - imported attestation bundle
   - imported trusted-root material
   - explicit freshness and lifecycle notes

7. **Lifecycle / revocation handling**
   - retained versus superseded evidence
   - deleted or no-longer-trusted attestation posture
   - historical record versus active consumer validity

## Desired properties
- Independent verification, not just “trust the CI run.”
- Small, attachable artifacts rather than giant log archives.
- Honest capability reporting when native dependencies or non-hermetic build steps prevent strong verdicts.
- Offline / air-gapped verification that stays explicit about imported trust material.
- Clear separation between compare results, provenance claims, SBOM claims, and later policy decisions.
- Composability with release tooling rather than replacing it.

## Distinction from nearby archive entries
- **Release Pipeline Kit** defines the portable shipping boundary. Repro Build asks whether the shipped artifact can be independently recreated from declared inputs, and under which lane / compare mode.
- **Signed Binaries Kit** verifies signatures and issuer metadata. Repro Build verifies source→artifact equivalence claims.
- **SBOM Evidence / Inventory Evidence** own precursor/export/recovery and inventory attachment truth. Repro Build may attach or import those results but must not replace them.
- **Airgap Kit** governs restricted-network inputs and mirror configuration. Repro Build governs the bounded verification evidence once those inputs are present.
- **Cargo Report Kit** standardizes build reports. Repro Build standardizes rebuild verdicts and diff reasons over release/package/artifact subjects.
