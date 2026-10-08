#!/usr/bin/env python3
"""Emit a small surprise ledger/report for CloudtainerML.

The user asked whether anything has actually been surprising. This tool records
surprise claims as first-class cube objects instead of burying them in prose.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "artifacts" / "audit"

SURPRISES = [
    {
        "id": "SURPRISE-001",
        "name": "Window order signal without explicit position",
        "degree": "medium",
        "why_it_surprised": "A finite sliding window update can leak order through what changed, so absolute/relative positional encoding is not the only way order enters tiny autoregressive systems.",
        "evidence_inside_cube": ["experiments/hist_window_order/hist_window_probe.py", "artifacts/probe-results/REV0008_HIST_WINDOW_ORDER_SMOKE.json"],
        "next_question": "Can we make an adversarial stream where histogram-delta order vanishes, and does a tiny model still infer order?",
    },
    {
        "id": "SURPRISE-002",
        "name": "Context-free value vectors may be useful deep in the stack",
        "degree": "medium-high",
        "why_it_surprised": "Attention value vectors are usually treated as context-dependent residual-stream products; Bank-of-Values reframes late-layer values as partly token-identity memory.",
        "evidence_inside_cube": ["experiments/bank_of_values/bov_probe.py", "artifacts/probe-results/REV0006_BANK_OF_VALUES_SMOKE.json"],
        "next_question": "When do values need context: entity identity, relation binding, or state updates?",
    },
    {
        "id": "SURPRISE-003",
        "name": "K=V can be sane while Q=K=V collapses",
        "degree": "medium",
        "why_it_surprised": "The QKV sharing lane suggests the model may tolerate key/value sharing far better than complete projection collapse; directionality of queries is the fragile part.",
        "evidence_inside_cube": ["experiments/qkv_projection_sharing/qkv_projection_sharing_probe.py", "artifacts/probe-results/REV0005_QKV_PROJECTION_SHARING_SMOKE.json"],
        "next_question": "Can a tiny trained attention model learn to compensate for K=V sharing on algorithmic recall but not on routing-heavy tasks?",
    },
    {
        "id": "SURPRISE-004",
        "name": "Heuristic cache routing loses to simpler anchors more often than expected",
        "degree": "medium",
        "why_it_surprised": "Several smoke probes showed oracle/top-anchor methods winning cleanly and hand-designed routing heuristics failing, which is useful negative evidence against prematurely complex policies.",
        "evidence_inside_cube": ["artifacts/probe-results/REV0008_PCAF_SPARSE_MEMORY_SMOKE.json", "artifacts/probe-results/REV0008_INTENT_KV_PRUNING_SMOKE.json", "artifacts/probe-results/REV0007_REASONING_WAVE_BUDGET_SMOKE.json"],
        "next_question": "Which heuristic features are redundant, and where is training actually needed?",
    },
    {
        "id": "SURPRISE-005",
        "name": "Encoder-decoder context compression is back on the table",
        "degree": "medium-high",
        "why_it_surprised": "I expected KV compression/eviction to dominate this cube, but LCLM-style context compression suggests a separate latent-skim-and-expand axis is worth testing even at toy scale.",
        "evidence_inside_cube": ["experiments/latent_context_compression/lclm_probe.py", "artifacts/probe-results/REV0009_LATENT_CONTEXT_COMPRESSION_SMOKE.json"],
        "next_question": "Is compressed context best viewed as answer substrate, router, or memory index?",
    },
    {
        "id": "SURPRISE-006",
        "name": "Retrieval as query-side supervision, not just pruning",
        "degree": "medium-high",
        "why_it_surprised": "EASE-TTT makes retrieval look like a source of temporary attention targets; the model can still answer from full context after query-side adaptation.",
        "evidence_inside_cube": ["experiments/evidence_aligned_ttt/ease_ttt_probe.py", "artifacts/probe-results/REV0010_EVIDENCE_ALIGNED_TTT_SMOKE.json"],
        "next_question": "How noisy can the evidence target be before adaptation hurts more than base full-context inference?",
    },
    {
        "id": "SURPRISE-007",
        "name": "Parametric memory becomes interesting exactly when cache memory disappears",
        "degree": "medium",
        "why_it_surprised": "The LoRA/KV framing suggests adapter memory is not a general replacement for context, but a complementary channel whose value appears under aggressive compression.",
        "evidence_inside_cube": ["experiments/parametric_kv_memory/parametric_kv_probe.py", "artifacts/probe-results/REV0010_PARAMETRIC_KV_MEMORY_SMOKE.json"],
        "next_question": "Can stale parametric memory be gated safely when fresh context disagrees?",
    },
    {
        "id": "SURPRISE-008",
        "name": "Supervised memory labels are a clean bridge away from BPTT",
        "degree": "medium-high",
        "why_it_surprised": "SMT reframes long-memory training as learning one-step transitions from teacher predictive states; in the toy, this creates a cheap bridge from tensor probes to tiny trainable memory.",
        "evidence_inside_cube": ["experiments/smt_transition_training/smt_transition_probe.py", "artifacts/probe-results/REV0010_SMT_TRANSITION_SMOKE.json"],
        "next_question": "Can we add noisy/imperfect teacher labels so the SMT toy is not an exact update table?",
    },
    {
        "id": "SURPRISE-009",
        "name": "Agentic DFS is a sharper tiny-training lane than expected",
        "degree": "medium",
        "why_it_surprised": "Most of the hunt has been cache/memory systems, but the agentic transformer search lane gives a tiny environment with a plausible mechanistic success criterion: action-trace and failure-trace specialization.",
        "evidence_inside_cube": ["experiments/agentic_dfs_search/dfs_search_probe.py", "artifacts/probe-results/REV0011_AGENTIC_DFS_SEARCH_SMOKE.json"],
        "next_question": "Can a tiny policy-gradient transformer actually rediscover the two-trace DFS mechanism, or does symbolic DFS make the task too easy?",
    },
    {
        "id": "SURPRISE-010",
        "name": "Entropy alone may not be the decisive signal",
        "degree": "medium",
        "why_it_surprised": "The entropy probe makes decode-conditioned information look much stronger than entropy-only allocation, suggesting online/generated-token feedback may matter more than static head entropy classification.",
        "evidence_inside_cube": ["experiments/entropy_guided_budget/entropy_head_probe.py", "artifacts/probe-results/REV0011_ENTROPY_GUIDED_BUDGET_SMOKE.json"],
        "next_question": "Split the budget arena into strict prefill-only, decode-token-only, and mixed policies to see whether entropy survives without future-support leakage.",
    },
    {
        "id": "SURPRISE-011",
        "name": "C++ changes the feasible probe frontier",
        "degree": "medium-high",
        "why_it_surprised": "The environment has gcc/g++, so high-volume cache/rollout/coreset simulations can move out of slow Python loops while staying dependency-free.",
        "evidence_inside_cube": ["tools/native_probe_audit.py", "experiments/express_streaming_coreset/express_coreset.cpp"],
        "next_question": "Which existing Python probe should be promoted to C++ only after the metric/falsifier stabilizes?",
    },
    {
        "id": "SURPRISE-012",
        "name": "Streaming coreset toy does not solve early needles",
        "degree": "medium",
        "why_it_surprised": "The C++ Express-style surrogate helps broad/drifting regimes but remains bad on isolated early-needle retention, showing coreset quality must be judged by adversarial evidence retention, not only average attention error.",
        "evidence_inside_cube": ["artifacts/probe-results/REV0013_EXPRESS_STREAMING_CORESET_SMOKE.json"],
        "next_question": "Can a query-independent cache preserve rare early evidence without degenerating into salience oracle or storing too much?",
    },
    {
        "id": "SURPRISE-013",
        "name": "Autoresearch belongs as a meta-optimizer lane",
        "degree": "medium",
        "why_it_surprised": "The linked HPO paper is not a cache/memory paper, but it directly informs how CloudtainerML should allocate experimental trials: LLM/domain priors should complement classical state, not replace it.",
        "evidence_inside_cube": ["experiments/centaur_hpo_state/centaur_hpo_probe.py", "artifacts/probe-results/REV0013_CENTAUR_HPO_STATE_SMOKE.json"],
        "next_question": "Can a Centaur-style optimizer choose probe configs better than hand sweeps on our synthetic cells?",
    },
    {
        "id": "SURPRISE-014",
        "name": "Cache object choice may dominate cache policy",
        "degree": "high",
        "why_it_surprised": "Residual-checkpoint/KV-Direct framing makes full KV, residual states, hidden states, adapters, and token streams competing cache objects rather than variants of one cache.",
        "evidence_inside_cube": ["experiments/residual_stream_kv/residual_stream_kv.cpp", "artifacts/probe-results/REV0013_RESIDUAL_STREAM_KV_SMOKE.json"],
        "next_question": "Can residual checkpointing and KV quantization coexist in a tiered object system?",
    },
    {
        "id": "SURPRISE-015",
        "name": "Move-query systems papers are toy-testable",
        "degree": "medium-high",
        "why_it_surprised": "A cross-instance GPU-fabric paper still yields a useful tiny phase-boundary probe because the core arithmetic is payload size, latency, and selected-block count.",
        "evidence_inside_cube": ["experiments/query_move_cache/query_move_probe.cpp", "artifacts/probe-results/REV0013_QUERY_MOVE_CACHE_SMOKE.json"],
        "next_question": "Should systems-cost cells stay P0 even when they do not train a model?",
    },
    {
        "id": "SURPRISE-016",
        "name": "Naive decoupled erase/write gates lost",
        "degree": "medium",
        "why_it_surprised": "The first hand-built decoupled fast-weight memory probe did not validate the intuitive architecture claim; tied scalar delta won all smoke regimes, suggesting decoupling needs learned/calibrated gates.",
        "evidence_inside_cube": ["experiments/gated_delta_memory/gated_delta_memory_probe.cpp", "artifacts/probe-results/REV0013_GATED_DELTA_MEMORY_SMOKE.json"],
        "next_question": "Can trained decoupled gates beat tied scalar gates on the same generated regimes?",
    },
    {
        "id": "SURPRISE-017",
        "name": "Persistent memory can lose to no memory",
        "degree": "high",
        "why_it_surprised": "The new memory-sycophancy trap makes memory an accuracy risk, not just a recall booster; skeptical/provenance policies matter because belief-only snippets can preserve misconceptions while losing correction context.",
        "evidence_inside_cube": ["experiments/memory_sycophancy_trap/memory_sycophancy_probe.cpp", "artifacts/probe-results/REV0015_MEMORY_SYCOPHANCY_TRAP_SMOKE.json"],
        "next_question": "Can a provenance/correction coupling rule keep useful preferences while refusing factual misconceptions?",
    },
    {
        "id": "SURPRISE-018",
        "name": "Structure-aware memory did not automatically beat flat retrieval",
        "degree": "medium",
        "why_it_surprised": "The first hypergraph working-memory toy was dominated by oracle evidence and only weakly won by hierarchy/hypergraph policies in non-oracle slices, so graph structure alone is not a free win.",
        "evidence_inside_cube": ["experiments/hypergraph_memory_trace/hypergraph_trace_probe.cpp", "artifacts/probe-results/REV0015_HYPERGRAPH_MEMORY_TRACE_SMOKE.json"],
        "next_question": "Can we design regimes where hypergraph structure adds value without leaking oracle evidence or overfitting section priors?",
    },
    {
        "id": "SURPRISE-019",
        "name": "The crude DF-SSM scaffold toy favored int8 over binary-plus-low-rank",
        "degree": "medium",
        "why_it_surprised": "The first 1-bit scaffold plus low-rank correction toy did not yet produce a clean win; fp32 is the sanity winner and int8 wins some regularized practical slices, suggesting our low-rank correction or regimes are too crude.",
        "evidence_inside_cube": ["experiments/dfssm_quant_scaffold/dfssm_quant_probe.cpp", "artifacts/probe-results/REV0015_DFSSM_QUANT_SCAFFOLD_SMOKE.json"],
        "next_question": "Should the next DF-SSM probe use learned/distilled correction vectors or a fairer byte-normalized practical leaderboard?",
    },
]


def revision() -> str:
    try:
        return json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")).get("revision", "rev0009")
    except Exception:
        return "rev0009"


def merged_surprises():
    merged = {s["id"]: dict(s) for s in SURPRISES}
    existing_path = ROOT / "SURPRISE-LEDGER.json"
    if existing_path.exists():
        try:
            existing = json.loads(existing_path.read_text(encoding="utf-8"))
            for item in existing.get("surprises", []):
                if isinstance(item, dict) and item.get("id"):
                    merged[item["id"]] = item
        except Exception:
            pass
    def key(item):
        try: return int(str(item.get("id", "0")).split("-")[-1])
        except Exception: return 0
    return [merged[k] for k in sorted(merged, key=lambda x: key(merged[x]))]

def main() -> int:
    AUDIT.mkdir(parents=True, exist_ok=True)
    surprises = merged_surprises()
    payload = {"project": "CloudtainerML", "revision": revision(), "count": len(surprises), "surprises": surprises}
    (ROOT / "SURPRISE-LEDGER.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md = [f"# Surprise ledger — {revision()}", "", "These are not claims of paper correctness. They are places where the research hunt or tiny probes changed the working intuition.", ""]
    for s in surprises:
        md.extend([f"## {s['id']}: {s['name']}", "", f"Degree: **{s['degree']}**", "", s["why_it_surprised"], "", f"Next question: {s['next_question']}", ""])
    (ROOT / "SURPRISE-LEDGER.md").write_text("\n".join(md), encoding="utf-8")
    (AUDIT / f"{revision().upper()}_SURPRISE_AUDIT.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    (AUDIT / f"{revision().upper()}_SURPRISE_AUDIT.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps({"surprise_count": len(surprises), "revision": revision()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
