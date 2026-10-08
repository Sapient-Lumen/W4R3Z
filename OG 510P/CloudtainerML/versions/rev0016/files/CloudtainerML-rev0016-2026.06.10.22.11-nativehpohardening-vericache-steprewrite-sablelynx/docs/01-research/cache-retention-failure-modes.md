# Cache retention failure modes worth tiny-scale testing

This note groups the current cache-memory hunt into testable failure modes.

## 1. Error accumulation

Quantized K/V can look acceptable on static reconstruction metrics while decode-time hidden states drift. This is the KVarN/TurboQuant/KV-geometry lane.

## 2. Region wipe-out

Token-level top-k can retain high total attention mass while eliminating entire reasoning regions. The relevant unit may be a segment/episode/proof chunk, not an individual token.

## 3. Dormant tokens

Some tokens are near-zero attention until an unpredictable future query asks for them. Anchors can semantically sponsor adjacent values.

## 4. Value outliers

Some value vectors may carry disproportionate state-update force. Evicting them may be worse than evicting high-attention low-value tokens.

## 5. Irreversible eviction

If evicted tokens are gone forever, a policy error is fatal. L2 tensor memories, latent summaries, or reversible/retrievable evictions can turn deletion into compression.

## 6. Support recovery

For sparse attention, exact zeros make retention a support-recovery problem. This may be easier to certify than softmax tail truncation.

## 7. Adaptive budget mismatch

A fixed K is wrong for mixed workloads. The problem is partly selecting a budget and policy per request, not only choosing the best universal policy.
