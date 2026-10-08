# Custody audit challenge proofs — rev0019

`custodyaudit.py` asks whether nodes that signed store contracts can still answer a fresh challenge for the exact digest. This is not proof of eternal storage; it is local evidence that catches cheap lies before a real network adds latency and churn.

The audit shape:

```text
fresh challenge = target + record digest + nonce + short live window
proof = contract hash + challenge hash + response digest + storage signature
```

The challenge is not bound to one contract, so several storage nodes can prove custody in the same audit round. The proof is bound to the challenge hash, so replaying an older proof becomes explicit replay pressure.

Risk tested here:

```text
wrong digest
wrong challenge / replay
proof for a contract outside the accepted set
one-family proof monoculture
useful refusal with backoff
expired challenge or proof
```
