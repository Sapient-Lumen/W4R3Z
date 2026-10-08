# Design: Repro Build lane map (source-package reproducibility, final-artifact compare, provenance and SBOM attestations, offline bundles, lifecycle)

## Goal
Sharpen **Repro Build Kit** so the archive stops treating “reproducible Rust releases” as one bucket.
The live ecosystem already spans materially different rebuild-adjacent lanes, and they differ in **what subject is being checked**, **what kind of equality is being claimed**, **whether a claim comes from comparison or attestation**, **whether verification can happen offline**, and **what lifecycle or revocation posture applies later**.

The archive should therefore keep rebuild review grounded in a lane map instead of one flattened “the release is reproducible” story.

## Signals from the current ecosystem
- Rust 1.91’s release notes say **building a crate with `cargo package` should now be independently reproducible**. That is a strong signal that source-package reproducibility has become an explicit upstream lane instead of folklore.
  https://doc.rust-lang.org/beta/releases.html
- `cargo package` still rewrites and normalizes `Cargo.toml`, removes `[patch]`, `[replace]`, and `[workspace]`, includes `Cargo.lock` by default, emits `.cargo_vcs_info.json`, flattens symlinks, and verifies the package by extracting the `.crate` and rebuilding it from a pristine state. That is a materially different subject from “compare a shipped binary later”.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- Cargo’s changelog says `trim-paths` now remaps all paths to `build.build-dir` and expands Windows/MSVC test coverage. That is direct evidence that final-artifact equivalence still depends on ongoing path-leakage work.
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo’s unstable docs say SBOM precursor files are generated for executable and linkable outputs uplifted into target or artifact directories. That makes artifact-linked inventory capture a real adjacent input lane for rebuild work rather than a separate compliance-only story.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- dist’s introduction says users should be able to rerun the same dist invocation locally and get the same results **“not to bit-level precision”** but to ordinary cargo-build expectations. That is excellent evidence that release tooling already distinguishes ordinary release repeatability from strict artifact equivalence.
  https://axodotdev.github.io/cargo-dist/book/
- dist’s supply-chain docs keep **signing**, **GitHub Attestation**, **CycloneDX SBOM output**, **cargo-auditable embedding**, and **OmniBOR IDs** as separate attachment surfaces. That means the release ecosystem itself is already plural here.
  https://axodotdev.github.io/cargo-dist/book/supplychain-security/index.html
- GitHub’s attestation docs say artifact attestations establish **where and how software was built**, can also attest SBOMs, can be verified offline, and are **not a guarantee that an artifact is secure**. That is direct evidence that attestation lanes and rebuild-comparison lanes must stay separate.
  https://docs.github.com/en/actions/concepts/security/artifact-attestations
  https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations
  https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations/verifying-attestations-offline
- GitHub’s lifecycle docs also say attestations are only meaningful while linked to artifacts people actually consume, recommend deleting stale or no-longer-trusted attestations, and note that deletion can prevent consumer verification. That makes lifecycle posture its own real lane.
  https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/manage-attestations

## The lanes

### 1) Source-package reproducibility lane (`cargo package` subject)
This is the lane where the reproducible subject is the produced `.crate` package rather than the later shipped binary or installer.

What defines it:
- normalized packaged manifest and curated file set
- packaged lockfile posture
- `.cargo_vcs_info.json` as a best-effort hint rather than verified provenance
- Cargo’s own extract-and-rebuild verification step
- independent reproducibility claim tied to the source package boundary

Why it deserves its own lane:
- Rust now explicitly says `cargo package` should be independently reproducible
- this lane is closer to source publication than to final release artifacts
- success here does not prove binary/installers are reproducible later

Design rule:
- keep package reproducibility distinct from final-artifact equivalence and distinct from provenance attestations

### 2) Final-artifact rebuild-compare lane (binaries, libraries, archives, installers)
This is the lane where a produced artifact is rebuilt and compared against a reference artifact.

What defines it:
- explicit artifact subject
- explicit compare mode (`bitwise`, `archive-member-digest`, `normalized-debug-insensitive`, etc.)
- diff reasons when artifacts diverge
- strong dependence on path, timestamp, archive-order, linker, SDK, compression, and post-processing behavior

Why it deserves its own lane:
- this is the core independent-verification claim people usually mean by “reproducible build”
- release tools like dist already say their local rerun target is not automatically bit-level precision
- installers, archives, and signed/postprocessed artifacts may need boundary-specific compare rules

Design rule:
- keep compare-mode truth explicit and refuse to let one artifact family silently define equivalence for all others

### 3) Provenance-attestation lane (where/how built)
This is the lane where the claim is about origin and workflow execution rather than equivalence.

What defines it:
- signed statement about repository / workflow / build environment / invocation
- online or offline verification of the attestation itself
- policy around signer repository, signer workflow, and issuer identity
- no intrinsic claim that an independent rebuild matched the artifact

Why it deserves its own lane:
- GitHub explicitly frames artifact attestations as provenance for where/how software was built
- provenance is useful and important, but it answers a different question from rebuild comparison
- provenance can coexist with mismatch, inconclusive rebuilds, or absent rebuild checks

Design rule:
- keep provenance success distinct from equivalence success

### 4) SBOM-attestation / inventory-attachment lane
This is the lane where attached inventory documents or SBOM attestations travel with artifacts.

What defines it:
- inventory document or attested predicate attached to a build artifact or release artifact
- predicate-type or format differences such as SPDX versus CycloneDX
- linkage to the artifact under discussion rather than direct equivalence evidence
- import relationship to SBOM Evidence / Inventory Evidence rather than ownership replacement

Why it deserves its own lane:
- GitHub explicitly supports SBOM attestations as distinct from default build-provenance attestations
- Cargo-native SBOM precursor work and release-attached inventory files are adjacent evidence, not rebuild verdicts
- release reviews often need inventory context, but that must not replace compare results

Design rule:
- keep inventory attachment truth separate from both provenance-attestation truth and final-artifact compare truth

### 5) Offline verification bundle lane
This is the lane where a consumer verifies claims without live network lookups.

What defines it:
- imported artifact copy
- imported attestation bundle and trusted root material when relevant
- local compare inputs and explicit trust assumptions
- limited freshness that depends on what was imported and when

Why it deserves its own lane:
- GitHub documents offline attestation verification as a distinct workflow with imported bundle and trusted-root files
- air-gapped or incident-response users care about this mode specifically
- online “can fetch and check” behavior should not be narrated as equivalent to offline evidence portability

Design rule:
- keep offline-bundle completeness and freshness explicit instead of pretending that offline verification is simply online verification with the internet unplugged

### 6) Lifecycle / revocation lane
This is the lane where attestations or rebuild evidence stop being appropriate to rely on.

What defines it:
- artifact still exists or no longer exists
- attestation or evidence intentionally retained, superseded, or deleted
- consumer policy about stale, revoked, or no-longer-trusted evidence
- explicit transition from active verification aid to historical record or dead reference

Why it deserves its own lane:
- GitHub says attestations are only meaningful while linked to consumed artifacts and may need deletion when artifacts are removed or untrusted
- release ecosystems often accumulate evidence that silently drifts away from current artifacts
- lifecycle posture matters especially for downstream mirrors, policy, and incident work

Design rule:
- keep lifecycle status explicit; deletion or supersession is not the same thing as cryptographic failure, and historical retention is not the same thing as active consumer validity

## Lane transitions the archive must keep explicit
1. **source-package reproducibility ↔ final-artifact equivalence**
   - a reproducible `.crate` package is not automatically a reproducible signed binary or installer.
2. **final-artifact equivalence ↔ provenance attestation**
   - “built by this workflow” is not the same statement as “independently rebuilt to the same result”.
3. **provenance attestation ↔ SBOM attestation**
   - build-origin claims and inventory-document claims are different predicates with different review uses.
4. **online verification ↔ offline verification**
   - importing bundles and trusted roots changes freshness and lifecycle assumptions.
5. **active evidence ↔ historical evidence**
   - retained references, deleted attestations, and superseded artifacts must not silently keep the same trust meaning.
6. **rebuild evidence ↔ release/distribution/install conclusions**
   - producer-side rebuild evidence remains distinct from what a mirror served or what a consumer actually installed.

## What should change elsewhere in the archive
- **Repro Build Kit** should remain the base rebuild-verification kit, but it should now cite this lane map as the rule for what must stay separate.
- **Release Truth Stack** should attach rebuild, provenance, and inventory lanes without flattening them into one producer-side badge.
- **SBOM Evidence / Inventory Evidence** should keep inventory predicates and precursor/recovery evidence distinct from rebuild verdicts.
- **Distribution Contract**, **Policy**, **Trust Signals**, and **Incident** layers should import bounded rebuild summaries rather than quietly redefining rebuild truth.
- **Airgap Kit** should stay the place that owns restricted-network topology and import posture; Repro Build should only own the offline-verification evidence once the inputs are in hand.

## Worthy contribution, sharpened
The worthy contribution here is **not** another provenance badge, another CI wrapper, or a generic Nix/dev-container recipe.
It is a thin `cargo repro` / `repro-pack/v0` layer whose lane profiles, compare-mode reports, attestation references, offline bundles, and lifecycle notes make Rust rebuild claims reviewable across package, artifact, provenance, inventory, and offline-consumer workflows without semantic collapse.
