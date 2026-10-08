# Surprise ledger — rev0009

These are not claims of paper correctness. They are places where the research hunt or tiny probes changed the working intuition.

## SURPRISE-001: Window order signal without explicit position

Degree: **medium**

A finite sliding window update can leak order through what changed, so absolute/relative positional encoding is not the only way order enters tiny autoregressive systems.

Next question: Can we make an adversarial stream where histogram-delta order vanishes, and does a tiny model still infer order?

## SURPRISE-002: Context-free value vectors may be useful deep in the stack

Degree: **medium-high**

Attention value vectors are usually treated as context-dependent residual-stream products; Bank-of-Values reframes late-layer values as partly token-identity memory.

Next question: When do values need context: entity identity, relation binding, or state updates?

## SURPRISE-003: K=V can be sane while Q=K=V collapses

Degree: **medium**

The QKV sharing lane suggests the model may tolerate key/value sharing far better than complete projection collapse; directionality of queries is the fragile part.

Next question: Can a tiny trained attention model learn to compensate for K=V sharing on algorithmic recall but not on routing-heavy tasks?

## SURPRISE-004: Heuristic cache routing loses to simpler anchors more often than expected

Degree: **medium**

Several smoke probes showed oracle/top-anchor methods winning cleanly and hand-designed routing heuristics failing, which is useful negative evidence against prematurely complex policies.

Next question: Which heuristic features are redundant, and where is training actually needed?

## SURPRISE-005: Encoder-decoder context compression is back on the table

Degree: **medium-high**

I expected KV compression/eviction to dominate this cube, but LCLM-style context compression suggests a separate latent-skim-and-expand axis is worth testing even at toy scale.

Next question: Is compressed context best viewed as answer substrate, router, or memory index?
