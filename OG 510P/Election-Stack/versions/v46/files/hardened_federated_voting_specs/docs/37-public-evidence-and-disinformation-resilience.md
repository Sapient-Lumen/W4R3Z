# Public evidence and disinformation resilience

**Track:** A (Deployable core)


Elections fail politically when the public cannot distinguish:
- true errors vs. false claims,
- isolated incidents vs. outcome-altering failures.

End-to-end verification helps, but only if the evidence is:
- accessible,
- independently reproducible,
- communicated without overclaiming.

## Threats
- Fake screenshots / fake receipts circulated at scale.
- Claims that the log "forked" without evidence.
- Deliberate confusion about what is being verified (paper vs crypto vs vendor reports).

## Spec requirements

### Evidence package (MUST)
Publish a signed, content-addressed evidence package containing:
- election parameters (PK, contest definitions, hashes),
- witness checkpoints,
- ballot commitments/ciphertexts,
- proofs (shuffle/MPC/homomorphic),
- verifier outputs (multiple implementations),
- audit plan + final audit report.

### Reproducibility (MUST)
- At least two independent verifier implementations must reproduce the same results.
- Provide public test vectors and a "one-command" verification guide.

### Claim hygiene (MUST)
- Public communications must separate:
  - integrity evidence,
  - privacy assumptions,
  - coercion/malware residual risks.

## Operational practices
- Pre-election publish "what to check" guides for media/candidates.
- Run public tabletop exercises about likely misinformation scenarios.
- Publish a "known issues" registry and patch policy.