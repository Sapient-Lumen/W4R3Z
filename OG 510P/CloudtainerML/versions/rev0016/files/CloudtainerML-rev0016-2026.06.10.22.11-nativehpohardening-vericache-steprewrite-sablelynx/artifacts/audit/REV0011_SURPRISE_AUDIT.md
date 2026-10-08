# Surprise ledger — rev0011

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

## SURPRISE-006: Retrieval as query-side supervision, not just pruning

Degree: **medium-high**

EASE-TTT makes retrieval look like a source of temporary attention targets; the model can still answer from full context after query-side adaptation.

Next question: How noisy can the evidence target be before adaptation hurts more than base full-context inference?

## SURPRISE-007: Parametric memory becomes interesting exactly when cache memory disappears

Degree: **medium**

The LoRA/KV framing suggests adapter memory is not a general replacement for context, but a complementary channel whose value appears under aggressive compression.

Next question: Can stale parametric memory be gated safely when fresh context disagrees?

## SURPRISE-008: Supervised memory labels are a clean bridge away from BPTT

Degree: **medium-high**

SMT reframes long-memory training as learning one-step transitions from teacher predictive states; in the toy, this creates a cheap bridge from tensor probes to tiny trainable memory.

Next question: Can we add noisy/imperfect teacher labels so the SMT toy is not an exact update table?

## SURPRISE-009: Agentic DFS is a sharper tiny-training lane than expected

Degree: **medium**

Most of the hunt has been cache/memory systems, but the agentic transformer search lane gives a tiny environment with a plausible mechanistic success criterion: action-trace and failure-trace specialization.

Next question: Can a tiny policy-gradient transformer actually rediscover the two-trace DFS mechanism, or does symbolic DFS make the task too easy?

## SURPRISE-010: Entropy alone may not be the decisive signal

Degree: **medium**

The entropy probe makes decode-conditioned information look much stronger than entropy-only allocation, suggesting online/generated-token feedback may matter more than static head entropy classification.

Next question: Split the budget arena into strict prefill-only, decode-token-only, and mixed policies to see whether entropy survives without future-support leakage.
