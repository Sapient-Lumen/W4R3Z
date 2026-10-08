# Verifier policy snapshots, deterministic appraisal, and trust-profile portability are world contracts, not just portable evidence

Portable receipts, bundles, checkpoints, and trust roots are not enough for any successor-facing archive or trust lane if future inheritors cannot also reconstruct the verifier's rulebook.

- `RS-GR-357` shows that appraisal is policy-driven twice over: a Verifier applies an Appraisal Policy for Evidence, and a Relying Party separately applies an Appraisal Policy for Attestation Results, so the same signed evidence can yield different outcomes under different rulebooks.
- `RS-GR-358` shows that SCITT registration policies and trust anchors must themselves be made transparent, that the policy committed at the time of registration is the one that must be applied, and that enough information must remain available to reproduce those historical checks, so policy snapshots are part of the evidence trail rather than background configuration.
- `RS-GR-359` shows that TUF clients ship with trusted root keys for configured repositories, evaluate thresholded roles and delegations, and revoke delegations through new metadata, so acceptance depends on an explicit trust profile rather than on raw signature validity alone.
- `RS-GR-360` shows that Sigstore keyless verification requires expected identity and issuer constraints and that disabling claim checks still verifies the signature while skipping payload semantics, so signature validity and policy acceptance are different layers.
- `RS-GR-361` shows that Sigstore policy-controller can validate signatures and attestations while also applying cue / rego policies and custom TrustRoots, so enforcement behavior is a configurable policy artifact rather than one universal verifier judgment.
- `RS-GR-362` shows that CoRIM-based appraisal is meant to be predictable and deterministic, that Verifiers reconcile multiple authorities into an appraisal claims set, and that any CoRIM profile must describe expected verifier behavior at the well-defined profile-dependent points, so profile identity and deterministic-processing rules belong in the retained contract.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **policy snapshots, accepted roots / identities, claim-check strictness, or deterministic appraisal profile semantics** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat a portable receipt or bundle as self-explanatory proof.

At minimum, it should distinguish between:

1. a world where evidence is retained but the historical verifier flags, identities, and trust roots are not;
2. a world where current policy is known but not versioned or linked to past decisions;
3. a world where policy is versioned but only as prose, with tool-specific behavior still implicit;
4. a world with profile-identified, machine-readable policy snapshots that let future verifiers replay historical decisions deterministically;
5. a world that preserves both the historical policy snapshot and the current policy, and explicitly records disagreement if the same evidence passes one and fails the other.

These are different worlds.
They change whether future inheritors can merely re-run today's favorite tool, reconstruct the historical decision rule that produced an old acceptance, or compare historical and current standards without confusing policy drift for moral change.

So verifier policy snapshots and deterministic appraisal belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, successor-safe authenticity, or replayable long-horizon verification should publish at least:

1. the exact verifier-policy artifacts retained locally: trust roots, delegation graph or role metadata, accepted signer identities / issuers, witness or freshness thresholds, claim predicates, and pass / warn / reject rules;
2. whether the policy snapshot used for each registration or verification decision is versioned, signed, and linked to the retained evidence packet;
3. whether the verifier profile is machine-readable and profile-identified or only embedded in tool flags, cluster config, or prose runbooks;
4. whether future inheritors are expected to replay the historical policy, the current policy, or both, and how disagreements between those verdicts should be reported;
5. which parts of appraisal are deterministic across implementations and which remain implementation-specific or advisory.

Without that compact contract, future inheritors can mistake rulebook drift for Golden-Rule progress.
