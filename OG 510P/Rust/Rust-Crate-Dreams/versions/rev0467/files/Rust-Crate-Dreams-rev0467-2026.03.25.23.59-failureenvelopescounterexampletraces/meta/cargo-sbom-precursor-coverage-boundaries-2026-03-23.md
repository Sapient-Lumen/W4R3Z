# Cargo SBOM precursor coverage boundaries — 2026-03-23

This note keeps **P-0125 Cargo SBOM Precursor Workbench Kit** from collapsing several support questions into one fake “SBOM captured” claim.

## Main judgment

When future passes touch **P-0125**, keep these layers distinct:

1. **capture route** — where precursor evidence came from,
2. **artifact coverage** — which outputs were actually eligible under Cargo’s documented surface,
3. **transform exactness** — what later normalization/emission preserved or lost,
4. **claim ceilings** — where imported state, copied outputs, or fresh-cache reuse stop stronger claims.

## What belongs in this lane

### Capture route
Questions like:
- was this a direct build invocation,
- did we observe `CARGO_SBOM_PATH`,
- did we correlate with `compiler-artifact` messages,
- or did we merely scan a target/artifact directory later?

### Artifact coverage
Questions like:
- which reported outputs were executable or linkable,
- which outputs were non-linkable and therefore not expected to get precursors,
- whether a missing precursor is a defect, an import omission, or simply out of scope.

### Claim ceilings
Questions like:
- does imported filesystem state prove same-invocation capture,
- does `fresh = true` weaken “generated now” claims,
- does an artifact-dir copy prove target-tree completeness,
- and which gaps still force manual review.

## What it is not

### 1. Not general sidecar shipping policy
That belongs more cleanly to **P-0479 Cargo Artifact Sidecar Contract Kit**.
P-0125 can import sidecar facts, but it should not become the generic ship/local/manual-review policy crate.

### 2. Not publish identity or registry protection
That belongs to publish-receipt / registry-capability lanes such as **P-0477**.
A perfect precursor capture story does not prove who published the crate or what registry protections were active.

### 3. Not higher-level provenance attestation
Attestations, signatures, and broader provenance systems sit above precursor capture.
P-0125 should provide honest inputs for them, not absorb them.

### 4. Not format emission exactness by itself
CycloneDX/SPDX/VEX transforms are adjacent and still belong in the workbench, but a transform receipt is not the same question as whether precursor coverage was complete or directly captured.

## Working rule for future passes

Do not let the archive silently flatten any of the following into one fake “Cargo emitted an SBOM” story:

- `CARGO_SBOM_PATH` existed,
- a `compiler-artifact` message existed,
- a sidecar file was found next to an artifact,
- an artifact was copied with `--artifact-dir`,
- a precursor file existed in an imported directory,
- or a later CycloneDX/SPDX file was produced.

A workflow can have all of those truths and still leave capture route, artifact coverage, or claim ceilings unresolved.

## Sources

- https://doc.rust-lang.org/cargo/reference/unstable.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
