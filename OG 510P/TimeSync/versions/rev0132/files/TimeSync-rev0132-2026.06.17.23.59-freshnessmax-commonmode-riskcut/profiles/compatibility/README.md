# Profile compatibility statements

This directory contains detached compatibility statement examples for independently operated profile catalogs.

A compatibility statement says how one profile reference relates to another profile reference. It does not distribute profile rules, update the local catalog, bind a transport adapter, negotiate a profile, or authorize disclosure.

Positive examples:

```text
p3-exact-equivalent-self.json
p3-challenge-portability-workflow.json
p3-replay-transparency-policy-equivalence.json
p3-replay-transparency-authority-rotation-equivalence.json
```

`p3-exact-equivalent-self.json` demonstrates the deterministic case: `exact_equivalent` with identical normative profile-rule digest values.

`p3-challenge-portability-workflow.json` demonstrates a rev0071 workflow caveat: the statement names `authorized_verifier_challenge_result_portability` while keeping evidence policy `identical`.

`p3-replay-transparency-authority-rotation-equivalence.json` demonstrates rev0079 replay-visibility-only authority rotation/delegation/compromise-response equivalence. It does not equate key material, authority rosters, delegation chains, incident forensics, trust anchors, policy language, profile evidence, or provenance.

rev0079 recovery-attestation portability is expressed by digest-bound references; compatibility statements may be cited by digest but do not export incident forensics, authority rosters, or key material.
