#!/usr/bin/env python3
"""rev0044 tiny trained-transformer attention trace probe.

The cube's next riskiest blocker after synthetic QK/softmax/V rows is absence
of model-generated attention traces. This script trains a small CPU PyTorch
transformer on a needle-token retrieval task, extracts real Q/K/V attention rows
from the trained model, and scores sparse compilers on dense-attention output
preservation.

It is not a public-model trace and not a kernel speed claim. It is E2.5 toy
model-trace evidence whose main purpose is to stop synthetic-only conclusions
from silently hardening into promotion claims.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import statistics
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0044"}
REV = META.get("revision", "rev0044")
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_TINY_TRANSFORMER_ATTENTION_TRACE_PROBE.json"

from experiments.attention_compiler_core.attention_core import (  # noqa: E402
    bytes_touched_est,
    compiler_points_for_row,
    output_metrics,
    stable_softmax,
    topk_indices,
    topp_indices_from_probs,
)

SEQ = 64
VALUE_COUNT = 40
VOCAB = 96
QUERY = 2
TARGET_BASE = 16
DISTRACTOR_BASE = 56
D_MODEL = 48
HEADS = 4
D_HEAD = D_MODEL // HEADS
LAYERS = 2
TRAIN_STEPS = 220
BATCH = 64
TRACE_BATCHES = 4
TRACE_BATCH = 32
K = 8
SEED = 4044


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class TraceAttentionLayer(nn.Module):
    def __init__(self, d_model: int, heads: int):
        super().__init__()
        self.heads = heads
        self.d_head = d_model // heads
        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.out = nn.Linear(d_model, d_model)
        self.ln1 = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(nn.Linear(d_model, 2 * d_model), nn.GELU(), nn.Linear(2 * d_model, d_model))
        self.ln2 = nn.LayerNorm(d_model)

    def forward(self, x: torch.Tensor, capture: bool = False):
        b, t, d = x.shape
        qkv = self.qkv(x).view(b, t, 3, self.heads, self.d_head)
        q = qkv[:, :, 0].transpose(1, 2)  # B,H,T,DH
        k = qkv[:, :, 1].transpose(1, 2)
        v = qkv[:, :, 2].transpose(1, 2)
        logits = torch.einsum("bhtd,bhsd->bhts", q, k) / math.sqrt(self.d_head)
        probs = torch.softmax(logits, dim=-1)
        y = torch.einsum("bhts,bhsd->bhtd", probs, v).transpose(1, 2).contiguous().view(b, t, d)
        x = self.ln1(x + self.out(y))
        x = self.ln2(x + self.ff(x))
        if capture:
            return x, {"logits": logits.detach().cpu(), "queries": q.detach().cpu(), "keys": k.detach().cpu(), "values": v.detach().cpu(), "probs": probs.detach().cpu()}
        return x, None


class TinyTraceTransformer(nn.Module):
    def __init__(self):
        super().__init__()
        self.tok = nn.Embedding(VOCAB, D_MODEL)
        self.pos = nn.Embedding(SEQ, D_MODEL)
        self.layers = nn.ModuleList([TraceAttentionLayer(D_MODEL, HEADS) for _ in range(LAYERS)])
        self.final_ln = nn.LayerNorm(D_MODEL)
        self.clf = nn.Linear(D_MODEL, VALUE_COUNT)

    def forward(self, x: torch.Tensor, capture: bool = False):
        pos = torch.arange(x.shape[1], device=x.device)[None, :]
        h = self.tok(x) + self.pos(pos)
        traces = []
        for layer in self.layers:
            h, tr = layer(h, capture=capture)
            if capture:
                traces.append(tr)
        h = self.final_ln(h)
        logits = self.clf(h[:, -1])
        return logits, traces


def make_batch(batch: int, rng: np.random.Generator) -> tuple[torch.Tensor, torch.Tensor, np.ndarray]:
    x = rng.integers(DISTRACTOR_BASE, VOCAB, size=(batch, SEQ), dtype=np.int64)
    x[:, -1] = QUERY
    y = rng.integers(0, VALUE_COUNT, size=(batch,), dtype=np.int64)
    target_pos = rng.integers(4, SEQ - 4, size=(batch,), dtype=np.int64)
    for i in range(batch):
        x[i, target_pos[i]] = TARGET_BASE + y[i]
    return torch.tensor(x, dtype=torch.long), torch.tensor(y, dtype=torch.long), target_pos


def train_model() -> tuple[TinyTraceTransformer, dict]:
    torch.manual_seed(SEED)
    np_rng = np.random.default_rng(SEED)
    model = TinyTraceTransformer()
    opt = torch.optim.AdamW(model.parameters(), lr=3.5e-3, weight_decay=0.01)
    losses: list[float] = []
    accs: list[float] = []
    model.train()
    for step in range(TRAIN_STEPS):
        x, y, _ = make_batch(BATCH, np_rng)
        logits, _ = model(x)
        loss = F.cross_entropy(logits, y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        losses.append(float(loss.detach()))
        if (step + 1) % 20 == 0:
            with torch.no_grad():
                pred = logits.argmax(dim=-1)
                accs.append(float((pred == y).float().mean()))
    model.eval()
    eval_accs = []
    with torch.no_grad():
        for j in range(10):
            x, y, _ = make_batch(BATCH, np.random.default_rng(SEED + 1000 + j))
            logits, _ = model(x)
            eval_accs.append(float((logits.argmax(dim=-1) == y).float().mean()))
    return model, {
        "train_steps": TRAIN_STEPS,
        "final_train_loss": losses[-1],
        "mean_last20_train_loss": statistics.fmean(losses[-20:]),
        "last_logged_train_accuracy": accs[-1] if accs else None,
        "eval_accuracy": statistics.fmean(eval_accs),
    }


def select(method: str, scores: np.ndarray) -> np.ndarray:
    probs = stable_softmax(scores)
    if method == "exact_topk_8":
        return topk_indices(scores, K)
    if method == "topk_16":
        return topk_indices(scores, 16)
    if method == "topk_32":
        return topk_indices(scores, 32)
    if method == "topp_0p90":
        return topp_indices_from_probs(scores, probs, 0.90)
    if method == "topp_0p95":
        return topp_indices_from_probs(scores, probs, 0.95)
    if method == "local_tail_16":
        return np.arange(max(0, SEQ - 16), SEQ, dtype=np.int64)
    if method == "full_dense":
        return np.arange(SEQ, dtype=np.int64)
    raise KeyError(method)


METHODS = ["full_dense", "exact_topk_8", "topk_16", "topk_32", "topp_0p90", "topp_0p95", "local_tail_16"]


def collect_trace_rows(model: TinyTraceTransformer, train_metrics: dict) -> list[dict]:
    rows: list[dict] = []
    with torch.no_grad():
        for tb in range(TRACE_BATCHES):
            x, y, target_pos = make_batch(TRACE_BATCH, np.random.default_rng(SEED + 2000 + tb))
            logits, traces = model(x, capture=True)
            pred = logits.argmax(dim=-1).cpu().numpy()
            batch_acc = float(np.mean(pred == y.numpy()))
            for layer_id, tr in enumerate(traces):
                layer_logits = tr["logits"].numpy()  # B,H,T,S
                layer_values = tr["values"].numpy()  # B,H,S,DH
                for b in range(TRACE_BATCH):
                    for h in range(HEADS):
                        scores = layer_logits[b, h, -1].astype(np.float64)
                        values = layer_values[b, h].astype(np.float64)
                        probs = stable_softmax(scores)
                        truth_topk = set(map(int, topk_indices(scores, K)))
                        for method in METHODS:
                            sel = select(method, scores)
                            m = output_metrics(scores, values, sel)
                            needle = int(target_pos[b])
                            m.update({
                                "row_kind": "model_trace_compiler_row",
                                "compiler": method,
                                "layer": int(layer_id),
                                "head": int(h),
                                "trace_batch": int(tb),
                                "example": int(b),
                                "N": SEQ,
                                "D": D_HEAD,
                                "DV": D_HEAD,
                                "K": K,
                                "value_reads": int(m["selected_count"]),
                                "qk_dot_products": SEQ,
                                "score_reads": SEQ,
                                "bytes_touched_est": bytes_touched_est(SEQ, SEQ, int(m["selected_count"]), D_HEAD, D_HEAD),
                                "topk_hit_rate": float(len(set(map(int, sel)) & truth_topk) / K),
                                "needle_position": needle,
                                "needle_selected": bool(needle in set(map(int, sel))),
                                "needle_probability": float(probs[needle]),
                                "max_probability": float(np.max(probs)),
                                "model_correct": bool(pred[b] == int(y[b])),
                                "model_accuracy_snapshot": batch_acc,
                                "passes_quality_bar": bool(m["output_cosine"] >= 0.995 and m["mass_retained"] >= 0.95 and m["attention_rel_l2_error"] <= 0.18),
                            })
                            rows.append(m)
    return rows


def fmean(xs: Iterable[float]) -> float | None:
    xs = list(xs)
    return statistics.fmean(xs) if xs else None


def summarize(rows: list[dict], train_metrics: dict) -> dict:
    methods = sorted({r["compiler"] for r in rows})
    method_summary = {}
    for method in methods:
        xs = [r for r in rows if r["compiler"] == method]
        method_summary[method] = {
            "mean_mass_retained": fmean(r["mass_retained"] for r in xs),
            "mean_attention_rel_l2_error": fmean(r["attention_rel_l2_error"] for r in xs),
            "mean_output_cosine": fmean(r["output_cosine"] for r in xs),
            "quality_bar_rate": fmean(float(r["passes_quality_bar"]) for r in xs),
            "mean_selected_count": fmean(r["selected_count"] for r in xs),
            "mean_bytes_touched_est": fmean(r["bytes_touched_est"] for r in xs),
            "needle_selected_rate": fmean(float(r["needle_selected"]) for r in xs),
            "mean_topk_hit_rate": fmean(r["topk_hit_rate"] for r in xs),
        }
    by_layer = {}
    for layer in range(LAYERS):
        xs = [r for r in rows if r["layer"] == layer and r["compiler"] == "exact_topk_8"]
        by_layer[str(layer)] = {
            "exact_topk_8_mean_mass_retained": fmean(r["mass_retained"] for r in xs),
            "exact_topk_8_quality_bar_rate": fmean(float(r["passes_quality_bar"]) for r in xs),
            "exact_topk_8_needle_selected_rate": fmean(float(r["needle_selected"]) for r in xs),
        }
    return {
        "train_metrics": train_metrics,
        "trace_rows": len(rows),
        "method_summary": method_summary,
        "by_layer_exact_topk8": by_layer,
        "interpretation": "The traces come from a trained tiny model, so they are stronger than synthetic rows but weaker than public-model traces. Compare exact_topk_8 against Top-p and dense to decide whether Top-K exactness translates to model attention-output preservation.",
    }


def run() -> dict:
    torch.set_num_threads(1)
    model, train_metrics = train_model()
    rows = collect_trace_rows(model, train_metrics)
    return {
        "project": "CloudtainerML",
        "revision": REV,
        "probe": "tiny_transformer_attention_trace_probe",
        "kind": "python_tiny_model_attention_trace_benchmark",
        "evidence_tier": "E2p5_tiny_trained_model_attention_traces",
        "run_provenance": {
            "script": str(Path(__file__).relative_to(ROOT)),
            "source_path": str(Path(__file__).relative_to(ROOT)),
            "source_sha256": sha256_file(Path(__file__)),
            "core_source_path": "experiments/attention_compiler_core/attention_core.py",
            "core_source_sha256": sha256_file(ROOT / "experiments/attention_compiler_core/attention_core.py"),
            "command": "python experiments/tiny_transformer_attention_traces/tiny_transformer_attention_trace_probe.py",
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "torch": torch.__version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "seed_policy": {"seed": SEED, "seq": SEQ, "value_count": VALUE_COUNT, "layers": LAYERS, "heads": HEADS, "d_model": D_MODEL, "train_steps": TRAIN_STEPS, "trace_batches": TRACE_BATCHES, "trace_batch": TRACE_BATCH},
        },
        "summary": {
            "primary_metric": {"name": "quality_bar_rate", "direction": "higher_is_better"},
            "score_source": "scores and values are extracted from an actual trained PyTorch transformer: per-layer/head QK logits at the final query position and that head's V vectors; outputs compare dense softmax(QK) @ V against sparse softmax(QK[selected]) @ V[selected]",
            "guard_fields": [
                "attention_rel_l2_error", "attention_l2_error", "output_cosine", "mass_retained",
                "dense_attention_output_norm", "topk_hit_rate", "selected_count", "value_reads",
                "qk_dot_products", "bytes_touched_est", "needle_selected", "needle_probability",
                "model_correct", "model_accuracy_snapshot", "passes_quality_bar",
            ],
            **summarize(rows, train_metrics),
        },
        "rows": rows,
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = run()
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "artifact": str(OUT.relative_to(ROOT)),
        "train_metrics": payload["summary"]["train_metrics"],
        "method_summary": payload["summary"]["method_summary"],
    }, indent=2))


if __name__ == "__main__":
    main()
