# Wake from amnesia — rev0013

You are inside a Python-first DHT design cube for a future DHT over I2P. Future applications are distant consumers.

The current revision is `rev0013 proofhandshake-headwitness-latencyforge`.

## What matters most

1. **Provider records are claims.** rev0013 adds challenge-bound provider proof transcripts and useful refusal handling.
2. **Mutable heads are observations.** rev0013 adds path-family and witness-aware lookup pressure for stale/forked/broken-prev heads.
3. **Latency is policy.** rev0013 adds fake SAM-like latency/churn/retry tests so transport does not accidentally decide trust semantics.
4. **The cube audits itself.** rev0013 prunes transient cache files and records duplicate historical surfaces as visible warnings.

## The strongest sentence

```text
The DHT should prove its hardest local judgments before it talks to a real network.
```

## Next likely move

rev0014 should connect proof handshakes to private provider probe planning, feed head-witness receipts into garden sentinel scoring, and start larger randomized-but-reproducible adversarial sweeps.
