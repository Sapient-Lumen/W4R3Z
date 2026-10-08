# Design: Repro Build pilot program (`cargo repro pilot`, `repro-lane-report/v0`, `repro-pilot-pack/v0`)

## Goal
Give **Repro Build Kit** its own ranked pilot program so the archive proves lane-aware rebuild truth before widening back out into the full **Release Truth Stack**.

The missing contribution is not another release wrapper, badge, or attestation-only integration.
It is a disciplined rollout that proves Rust projects can publish enough rebuild-lane evidence that humans and tools can distinguish:
- source-package reproducibility,
- final-artifact compare truth,
- provenance-attestation truth,
- SBOM-attestation / inventory-attachment truth,
- offline verification bundles,
- and lifecycle / supersession posture.

## References (signals)
- Rust 1.91 release notes say building a crate with `cargo package` should now be independently reproducible.
  https://doc.rust-lang.org/beta/releases.html
- `cargo package` still verifies by extracting the `.crate` and building it from a pristine state.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- Cargo’s changelog shows `trim-paths` is still moving, including remapping paths to `build.build-dir` and widening Windows/MSVC coverage.
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo’s unstable docs expose SBOM precursor files for uplifted outputs, which gives rebuild tooling a stronger artifact-linked input lane.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- dist’s introduction says the same dist invocation should be runnable locally with the same ordinary results, but not necessarily bit-level precision.
  https://axodotdev.github.io/cargo-dist/book/
- GitHub’s attestation docs distinguish build provenance, SBOM attestations, offline verification, and lifecycle management.
  https://docs.github.com/en/actions/concepts/security/artifact-attestations
  https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations
  https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations/verifying-attestations-offline
  https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/manage-attestations

## Why this needs its own design layer
Without a rebuild-specific pilot program, the archive is vulnerable to three bad outcomes:
1. **package theater** — a reproducible `.crate` gets narrated as a reproducible release artifact;
2. **attestation theater** — provenance or SBOM attestations get narrated as independent equivalence evidence;
3. **offline theater** — copied bundles and imported roots get narrated as timeless, self-explanatory truth.

A worthy contribution here should prove a smaller and stronger claim:
> Rust projects can attach enough lane-aware rebuild evidence that reviewers can tell which reproducibility claim actually holds, under which compare mode, with which imported attachments and lifecycle assumptions.

## Shared artifact posture
### 1. `repro-lane-profile/v0`
Declares the lane under test.

Should record:
- lane identity (`package`, `artifact-compare`, `provenance-attestation`, `sbom-attestation`, `offline-bundle`, `lifecycle`)
- subject kind (`.crate`, binary, archive, installer, release asset)
- compare mode if relevant
- required imports and optional imports
- whether the lane is authoritative, attached, or imported

### 2. `repro-collection-profile/v0`
Declares what evidence was collected.

Should record:
- package/build/release inputs used
- compare inputs used
- attestation references or bundles used
- inventory attachments used
- required versus optional evidence
- missing-data render (`unknown`, `partial`, `inconclusive`, `import-only`)

### 3. `repro-lane-report/v0`
Asks whether the lane stayed honest.

Should record:
- verdict (`MATCH`, `MISMATCH`, `ATTESTED`, `MISSING`, `INCONCLUSIVE`, `SUPERSEDED`)
- strength class
- diff or reason codes
- imported-attachment notes
- lifecycle and freshness notes when relevant

### 4. `repro-pilot-pack/v0`
Bundle for review and reuse:
- lane profile
- collection profile
- lane report(s)
- linked `repro-pack/v0`
- optional raw diffs, attestation bundles, trusted roots, or release-manifest attachments

## Ranked first pilots

### 1) Source-package lane (`cargo package` subject)
**Why first**
- This is now directly blessed by Rust 1.91 release notes.
- It proves the archive can talk about reproducibility at the source-package boundary before artifact distribution widens the story.

**Must prove**
- packaged subject is explicit;
- packaged manifest rewrites and lockfile posture stay visible;
- pristine extract-and-build verification is preserved;
- success is not narrated as final binary equivalence.

### 2) Pure-Rust final-binary compare lane
**Why second**
- This is the simplest artifact-equivalence lane that most users actually mean by reproducible build.
- It exercises compare-mode truth without pulling native SDK drift in too early.

**Must prove**
- artifact subject and compare mode are explicit;
- path/timestamp/archive-order/debug-info drift gets reason codes;
- provenance attachments do not replace compare results;
- `INCONCLUSIVE` remains first-class when inputs are insufficient.

### 3) Native / `build.rs` / toolchain-sensitive lane
**Why third**
- This is where real divergence pressure becomes visible.
- It proves the archive can stay honest when Cargo-native comparison meets SDKs, linkers, generated code, and native libraries.

**Must prove**
- native inputs stay explicit;
- compare reasons can blame toolchain / linker / SDK drift honestly;
- strong/weak equivalence classes remain separate;
- the lane can fail honestly without collapsing back into provenance theater.

### 4) dist-managed release-asset lane
**Why fourth**
- dist is a real release substrate and explicitly says its repeatability target is not automatically bit-level precision.
- This lane proves the archive can distinguish ordinary repeatability from stricter artifact equivalence across archives/installers.

**Must prove**
- release asset families stay explicit;
- archive/installer compare modes are explicit and not silently inherited from raw binaries;
- dist manifest or release-pack attachments remain attachments, not verdicts;
- post-processing steps stay visible.

### 5) Provenance + SBOM attestation attachment lane
**Why fifth**
- These are already live consumer-facing security signals.
- The archive needs to prove they compose with rebuild evidence without replacing it.

**Must prove**
- build provenance and SBOM predicates stay separate;
- signer/issuer/workflow identity remains explicit;
- attached inventory docs do not become rebuild verdicts;
- attestation success can coexist with compare mismatch or compare absence.

### 6) Offline verification + lifecycle lane
**Why sixth**
- This is where real long-term use happens for cautious consumers, mirrors, and incident responders.
- It should come after the online lanes are already legible.

**Must prove**
- imported bundle and trusted-root posture stay explicit;
- freshness is bounded rather than implied;
- superseded/deleted/no-longer-trusted evidence is rendered honestly;
- historical retention and active consumer validity stay distinct.

## Immediate archive consequences
Read this file together with:
- `design/repro-build-lane-map.md`
- `design/repro-build-kit.md`
- `proposals/epic-repro-build-kit.md`
- `design/release-truth-stack.md`
- `design/release-truth-pilot-program.md`

## Archive decision
Future rebuild-verification revisions should prefer:
- lane profiles over one universal “reproducible release” score,
- compare-mode and reason-code honesty over provenance theater,
- bounded offline bundles over timeless-trust claims,
- and explicit lifecycle posture over forgotten stale evidence.
