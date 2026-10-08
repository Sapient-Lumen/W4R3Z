# Frontier salience snapshot — 2026-03-21-151

This pass did **not** add another domain-specific evidence kit.
It deepened **P-0256 Evidence Bundle Core Kit**.

## Why this frontier moved up

The current substrate now makes the missing layer much sharper:

- in-toto now keeps **predicate**, **statement**, **envelope**, and **bundle** explicitly distinct;
- Sigstore bundles are now a concrete “everything required to verify” lane rather than just a vague signing story;
- OCI 1.1 / ORAS referrers make attachment/publication routes concrete enough that local bundle validity and publication route should no longer be conflated;
- SCITT is clarifying the external transparency/publication side rather than replacing local portable evidence packs;
- the archive itself now has enough bundle-first proposals that private grammar drift is a bigger risk than lack of ideas.

That combination means “supports signed evidence bundles” is now too vague as a crate claim.
A worthy crate in this frontier should publish at least:

1. **container basis** truth,
2. **entry lineage** truth,
3. **attestation lane** truth,
4. **publication route** truth,
5. **share-safety posture** truth.

## Main conclusion

Promote **P-0256** again, but keep it narrow.
The sharper next move is not another attestation format and not another publication service.
It is a boring contract that keeps **packing**, **lineage**, **attestation**, **publication**, and **shareability** separately reviewable.

## Ranked near-term frontier from this pass

1. **P-0256 Evidence Bundle Core Kit** — strengthened because more of the archive now depends on it as shared substrate.
2. **P-0503 Assurance Case Workbench Kit** — still strong because higher-layer argument/review imports remain fragmented.
3. **P-0264 Rust Conformance Harness Toolkit** — still strong because suite/case/result contracts remain fragmented.
4. **P-0073 Async Replay Debugger Kit** — still strong because replay evidence wants bundle substrate without a private grammar.
5. **P-0485 Verification Campaign Workbench Kit** — still strong because campaign truth still rides above reusable bundle semantics.

## Keep these boundaries sharp

- **P-0256** is container basis + entry lineage + attestation lane + publication route + share-safety posture.
- domain bundle profiles are separate.
- attestation standards are separate.
- publication infrastructure is separate.
- assurance/review consumers are separate.

Do not let “evidence bundle” flatten those into one fake crate.
