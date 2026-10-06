# ADR-0082: Attestation results evidence and admission-issue boundary

- Status: Accepted
- Date: 2026-03-07

## Context

DeriveBSD already had the main remote-attestation pieces:

- `boot.attestation`
- `attestation.reference`
- `attestation.requirement`
- `attestation.receipt`
- `attestation.admission.policy`
- action-specific authority objects such as `secret-receipt`, `breakglass-receipt`, and `workload-identity-issue-receipt`

The archive had also already decided that measured posture is profile-shaped and that attestation-gated actions should be reviewable.
What remained too soft was the **boundary between verifier output and the action that consumes it**.

The docs still risked implying that trust came from one of three accidental places:

- a passing `attestation.receipt` floating around without an explicit consuming decision,
- a subsystem pinning a raw receipt pointer but not the requirement/policy that made it acceptable,
- or product defaults making remote verification feel like ambient authority instead of an explicit gate.

That is too ambiguous for all four product shapes:

- **A / fleet host** and **D / appliance factory / regulatory** need attestation-gated actions to be replayable, freshness-bounded, and explicit.
- **B / workstation** needs sensitive gates to be explainable without making everyday local use depend on verifier folklore.
- **C / general-purpose OS** needs optional attestation lanes without letting a verifier receipt silently become the real policy engine.

Current remote-attestation practice points the same way:

- the Verifier appraises evidence and emits attestation results,
- the Relying Party applies its own policy to those results,
- measured-boot verification evaluates event logs against explicit measured-boot policy,
- and verifier outputs should stay reusable evidence rather than ambient authority.

## Decision

DeriveBSD will treat `attestation.receipt` as **attestation evidence only**, never as the final authority for issuing an attestation-gated action.

1. `attestation.receipt` becomes explicitly **evidence only** via `authority_semantics = attestation-evidence-only`.
   It records a verifier result, not an issued secret, not an identity credential, and not an operator-access authorization.

2. `attestation.admission.policy` remains the authoritative object that maps actions to `attestation.requirement` digests.
   It answers **which action is gated by which requirement**.

3. `attestation.requirement` remains the freshness/minimum-verdict policy object for accepting verifier results.
   Subsystems should point at a requirement digest rather than treat a raw receipt digest as general policy.

4. Action-specific authority receipts may carry one `attestation_verification` summary object recording:
   - the decision (`not-required`, `not-used`, `accepted`, `degraded`, `rejected`)
   - the `attestation_requirement_digest`
   - the `attestation_receipt_digest`
   - the optional `attestation_admission_policy_digest`
   - notes

5. In v0, the canonical action receipts for this summary are:
   - `secret-receipt`
   - `breakglass-receipt`
   - `workload-identity-issue-receipt`

6. Grants and policy objects may still say that attestation is required.
   But the authoritative answer to “did this secret / session / credential get issued under acceptable attestation posture?” must live in the action receipt, not in the verifier receipt alone.

## Consequences

### Positive

- The archive now has one compact answer to “who made the actual trust decision?”
- Sensitive actions can remain verifier-aware without letting verifier infrastructure become ambient authority.
- A/D can require fresh receipts and explicit policy joins while staying replayable and explainable.
- B/C can keep optional or narrow gates without making every verifier result look like a mandatory platform-wide verdict.

### Trade-offs

- Several action receipts gain one more optional summary section.
- Operators must look at both the verifier result and the consuming action receipt when debugging why something was allowed or denied.
- Older compatibility pointers such as raw `attestation_ref` fields stay secondary to the typed `attestation_verification` summary.

## Follow-up

This ADR does **not** settle:

- the final default sensitive-action set per profile,
- the exact attestation vendor / verifier topology,
- or whether more action receipts should adopt `attestation_verification` in v0.

Those remain implementation and posture questions.

## Why this is coherent with the rest of the archive

This follows the same boundary discipline now used elsewhere:

- publisher identity receipts are supplemental,
- workflow verification is supplemental,
- transparency evidence is supplemental,
- vulnerability verification is supplemental,
- and attestation results should likewise stay verifier evidence while action receipts remain authoritative.
