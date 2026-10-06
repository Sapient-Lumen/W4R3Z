# ADR-0079: Supplychain verification evidence and publish-gate boundary

- Status: Accepted
- Date: 2026-03-07

## Context

DeriveBSD already had an optional workflow-verification lane built around:

- `supplychain-layout-policy` for workflow expectations,
- `supplychain-verify-receipt` for layout verification results,
- DSSE / in-toto statements for provenance and related attestations,
- and `release.authority.policy` / `release.publish.receipt` for the real publication authority path.

What remained unresolved was the authority boundary.

The archive still risked reading “the artifact has provenance / SBOM / test attestations and a passing workflow receipt” as if that were the same thing as “this artifact is authorized for release”.
That is dangerous because:

- **A / fleet host** and **D / appliance factory / regulatory** need strong workflow verification without turning CI or verifier outputs into silent publish authority.
- **B / workstation** needs explainable provenance and quality gates without backend folklore deciding what is trusted.
- **C / general-purpose OS** needs room for optional or adapter-shaped workflow verification without forcing every local build into a release-authority stack.

Current upstream practice points in the same direction:

- in-toto attestations are authenticated metadata consumed by policy engines,
- SLSA says provenance does nothing unless somebody inspects it,
- and SLSA’s Verification Summary Attestation is explicitly a verifier’s summary about evaluation against policy, not the artifact’s native release authority.

## Decision

DeriveBSD will treat supply-chain workflow verification as a **supplemental verification lane**, never as silent release authority.

1. `release.authority.policy` remains the authoritative publish/halt/resume surface.
   Threshold publication decisions still terminate in `release.publish.receipt`.

2. `supplychain-layout-policy` is a **workflow-constraint policy**.
   It says which layout / functionaries / predicate types / adjunct evidence must be satisfied for a subject to count as workflow-verified.
   It is not itself a publish-authorization object.

3. `supplychain-verify-receipt` is **workflow-verification evidence only**.
   It should carry `authority_semantics = workflow-verification-evidence-only`.
   A `pass` means the verifier concluded that a subject satisfied the named workflow policy.
   It does **not** mean the subject is automatically approved for publication.

4. `release.authority.policy` may optionally include `supplychain_verification` rules describing whether workflow verification is ignored / optional / required for publication review, which layout-policy digests are allowed, and freshness requirements for receipts.

5. `release.publish.receipt` may optionally include one `supplychain_verification` summary object.
   This summary is the only place where workflow-verification evidence becomes a publish-time gate result.

6. Attestations such as provenance, SBOM, VEX, test receipts, and in-toto links remain **input evidence** to workflow verification or other policy engines.
   They do not become publication authority merely by existing.

## Consequences

### Positive

- The archive now has one compact answer to “what approved publication?” versus “what evidence was evaluated before publication?”.
- CI / verifier stacks stay useful without becoming hidden release authorities.
- Offline or mirrored A/D workflows can carry workflow-verification receipts as portable evidence while keeping the final publication decision threshold-bound.
- B/C keep optional and adapter-shaped workflow verification without forcing every local build into a mandatory release lane.

### Trade-offs

- `release.authority.policy` and `release.publish.receipt` gain one more optional summary section.
- Operators who want “green CI means ship it” now have to encode that as explicit policy wiring instead of folklore.
- The older hyphenated supplychain artifact kinds remain in place for now to avoid widening the churn in this iteration.

## Follow-up

This ADR does **not** settle:

- whether the supplychain kinds should be renamed to dotted forms in a future cleanup,
- the exact freshness / expiry defaults for workflow verification by product shape,
- or how much of the verifier policy should be delegated to standardized VSA-like predicate exports.

Those remain implementation and interop questions.

## Why this is coherent with the rest of the archive

This follows the same boundary discipline now used elsewhere:

- identity evidence is supplemental,
- transparency is supplemental,
- runtime integrity evidence is distinct from policy intent,
- and workflow verification should likewise stay a reviewed gate input rather than ambient authority.
