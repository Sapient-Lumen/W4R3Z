# Authority scope, namespace custody, and designated speaker rules are world contracts, not just verified issuers

Verified bytes, preserved semantics, and stable subject identifiers are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **why this issuer, functionary, or workload was allowed to make this kind of statement about this subject, namespace, step, or audience at the time the claim was accepted**.

- `RS-GR-387` shows that X.509 separates identity from authority scope: basic constraints determine whether a key may certify, extended key usage constrains acceptable purposes, and name constraints restrict the namespace for subsequent certificates, so a valid chain does not imply universal speaking rights.
- `RS-GR-388` shows that TUF delegations trust specific delegated roles for specific target paths, require a target to stay within the trusted paths of every role in the delegation chain, and let terminating delegations ignore later conflicting statements outside that chain, so admissibility depends on retained delegation scope rather than on a bare signature alone.
- `RS-GR-389` shows that in-toto layouts explicitly say which keys are authorized for each supply-chain step and clients verify that each step was performed by the authorized functionary, so provenance depends on preserved role-to-step authorization and not just on knowing the signer identity.
- `RS-GR-390` shows that SCITT leaves registration policies implementation-specific but requires them and their trust anchors to be made transparent, requires enough information to reproduce the registration checks in force at registration time, and allows multiple issuers to make conflicting statements about the same artifact, so successor replay needs the standing policy that admitted one issuer's claim rather than just the retained receipt.
- `RS-GR-391` shows that a SPIFFE trust domain is an identity namespace backed by an issuing authority and validators must choose the bundle corresponding to the trust domain of the identity being checked, so namespace custody is part of the authority contract and not just cosmetic naming.
- `RS-GR-392` shows that SPIRE issues a workload identity only when workload selectors and parent-SPIFFE relationships match an authorized registration entry, so non-human issuer standing can depend on retained attestation / selector state and not just on possession of a workload key.
- `RS-GR-393` shows that audience can also be part of authority scope: the JWT `aud` claim identifies intended recipients and a principal that does not identify itself in the audience claim must reject the token, so some apparently valid claims are only admissible for declared relying parties.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **issuer standing, delegated role scope, namespace custody, workload-registration semantics, or audience restrictions** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat “the signature verifies and we know who issued it” as the end of the story.

At minimum, it should distinguish between:

1. a world where any recognized signer may speak about any subject or artifact under a trust root;
2. a world where issuer identity survives, but purpose, namespace, path, or step restrictions do not;
3. a world where delegation scope exists, but the delegation chain / registration entry / selector evidence that granted authority is not retained beside the proof;
4. a world where subject namespace or step scope survives, but audience or relying-party admissibility is still implicit and replay depends on unstated local policy;
5. a world where future inheritors can replay the full standing snapshot — issuer identity, delegated role or registration entry, namespace / path scope, purpose / predicate / step scope, audience, and any workload / parent constraints — and see why one issuer's claim was admissible while another equally well-signed claim was not.

These are different worlds.
They change whether future inheritors can merely verify that some recognized principal signed a statement, reconstruct why that principal had authority over the relevant namespace or step, or detect that a later policy replay silently broadened or narrowed who counts as a designated speaker.

So authority scope, namespace custody, and designated speaker rules belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, successor-safe authenticity, or replayable long-horizon verification should publish at least:

1. the exact issuer / functionary / workload identity bound to the statement and the trust domain or root under which that identity is meaningful;
2. the specific standing artifact that granted authority at decision time: certificate constraints, delegated role, layout step authorization, registration policy, or workload registration entry;
3. the subject / namespace / path / step / predicate scope over which that authority applies;
4. whether admissibility is universal or restricted by audience, tenant, relying-party class, or local policy profile;
5. which local state must survive for future replay — trust-domain bundle, delegation chain, selector evidence, parent identity, registration policy snapshot, or equivalent;
6. how authority ends or changes: expiry, revocation, bundle rotation, delegation replacement, selector drift, or policy supersession.

Without that compact contract, future inheritors can mistake a recognized signer, a still-valid receipt, or a stable subject ID for proof that the signer was actually entitled to speak for that subject in the relevant context.
