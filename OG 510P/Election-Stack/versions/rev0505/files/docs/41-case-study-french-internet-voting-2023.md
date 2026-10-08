# 41 — Case study: breaking an internet voting system (France legislative elections)

**Track:** B (Remote return / hard-mode research)



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

This case study summarizes lessons from a peer-reviewed analysis of a deployed internet voting system used in the context of French legislative elections (USENIX Security 2023).

## Why this matters

Real systems fail via:
- implementation flaws
- operational shortcuts
- hidden complexity
- update and deployment mistakes

Independent review has repeatedly found serious weaknesses in internet voting deployments.

## Lessons (generalized, non-exploitative)

1. **Assume the client is hostile.** Browser environments and remote devices are hard to secure.
2. **Assume updates are the main compromise route.** Secure update frameworks and reproducible builds are mandatory.
3. **Make verification usable.** “In theory verifiable” is not enough if observers cannot independently verify.
4. **Minimize TCB.** Reduce the amount of code that can affect correctness or privacy.
5. **Publish evidence early and continuously.** Delayed transparency is ineffective when trust collapses.

## What to steal for our design

- Use a public, append-only evidence pipeline (PBB + witnesses) so failures are detectable.
- Tighten “no remote return at scale” posture unless you accept the residual risk.

## References

See `references.md` entries for the USENIX Security 2023 paper.