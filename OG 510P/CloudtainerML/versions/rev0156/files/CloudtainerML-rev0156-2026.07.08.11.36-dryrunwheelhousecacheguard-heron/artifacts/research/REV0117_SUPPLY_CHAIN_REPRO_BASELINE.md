# Supply-chain and reproducibility baseline — REV0117

Status: `research_context_not_promotion_evidence`  
Promotion allowed: `false`

This pass researched external standards that should shape the portable handoff and receipt layer without becoming another bureaucracy detour.

## Bottom line

The handoff archive should keep moving toward a minimal attestation/reproducibility shape: content-addressed subjects, explicit build/capture inputs, immutable model revisions, standard timestamp discipline, and runtime/resource metadata. The point is not to claim standards compliance. The point is to make the archive easy for a cold reviewer to verify and hard for future revisions to overclaim.

## Sources and pressure

### SLSA specification v1.2

- URL: https://slsa.dev/spec/v1.2/
- Pressure on cube: Provenance should describe the artifact, builder/process, and inputs. CloudtainerML already has subject digests; the next useful change is to keep receipts structured enough to map into SLSA/in-toto style statements later.

### SLSA levels / provenance framing

- URL: https://slsa.dev/spec/v1.1/levels
- Pressure on cube: A low-level provenance existence claim is not enough. The cube should avoid saying “trusted” when it only has local fixture receipts, and should keep promotion blocked until real trace and named-hardware evidence exist.

### in-toto and SLSA attestation primer

- URL: https://slsa.dev/blog/2023/05/in-toto-and-slsa
- Pressure on cube: The fixed statement/predicate pattern is a good model for CloudtainerML receipts: semantic subject names plus digest-bound predicates beat path-name trust.

### Reproducible Builds

- URL: https://reproducible-builds.org/
- Pressure on cube: Independent verification requires source-to-artifact correspondence. For this project that means capture code, model revision, prompt manifest, provenance JSON, and generated receipts must stay content-bound.

### SOURCE_DATE_EPOCH specification

- URL: https://reproducible-builds.org/docs/source-date-epoch/
- Pressure on cube: Future handoff archives should avoid timestamp entropy where possible and record intentional timestamps separately from reproducibility inputs.

### OpenTelemetry resource semantic conventions

- URL: https://opentelemetry.io/docs/specs/semconv/resource/
- Pressure on cube: Runtime/resource identity should use stable field names where possible. The current trace provenance already records device, dtype, CUDA, and timing; a future refactor can map those to standard resource attributes rather than inventing more local registry terms.

## Speculation

The claim-compiler product may be more durable than the sparse-attention claim. A lightweight, digest-bound handoff archive that borrows from SLSA/in-toto/reproducible-build conventions could become useful even if the original sparse selector loses against modern exact/KV baselines.
