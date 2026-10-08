# Risk register — rev0009

## Highest-risk guesses now under test

| Risk | Current test surface | Why it matters |
|---|---|---|
| Valid old heads | `LocalHeadMemory` rollback verdicts | Attackers can replay signed stale values. |
| Same-sequence equivocation | fork verdicts + witness receipts | A compromised signer can split clients without invalid signatures. |
| Pointer without history | `require_prev=True` | Pure latest pointers fail when clients need continuity. |
| Delegation sprawl | capability chain validation | Garden helpers must not become root authority. |
| Revocation staleness | revocation set + mutable head | Revocation only helps once known; tests should expose that. |
| Captured lookups | fake chaos transcript | Fast answers can be stale or forked. |

## Next risks to implement

- Seed/policy portfolio capture under multi-authority heads.
- Garden witness receipt poisoning.
- Revocation-head rollback.
- Key rotation with succession proofs.
- Mutable manifest chains with skipped sequence checkpoints.
- Region-sweep pressure under thousands of heads.
