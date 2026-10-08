#!/usr/bin/env python3
"""rev0053 learned-trace block-bound stress probe.

rev0052 showed that observable key-cache centroids/radii can make score-path
block pruning honest on synthetic caches.  The next risky gap is whether those
bounds stay tight on model-generated Q/K/V traces.  This script trains the same
kind of tiny retrieval transformer used in rev0044, captures final-token Q/K/V
rows, and applies block upper-bound pruning using only observable key-cache
metadata.

Selection is forbidden from inspecting V vectors or dense outputs.  Dense scores
and outputs are computed only for evaluation.  The probe is intentionally
non-promotional: it is tiny CPU model-trace evidence, not public/pretrained or
GPU/fused-kernel evidence.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0053"}
REV = META.get("revision", "rev0053")
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_LEARNED_TRACE_BLOCK_BOUNDS.json"
MANIFEST = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_LEARNED_TRACE_BLOCK_BOUNDS_RUN_MANIFEST.json"

from experiments.attention_compiler_core.attention_core import (  # noqa: E402
    effective_support,
    output_metrics,
    passes_attention_quality_bar,
    stable_softmax,
)

# Kept small enough for repeatable CPU execution while still producing real
# learned Q/K/V rows.
SEQ = 48
VALUE_COUNT = 24
VOCAB = 80
QUERY = 2
TARGET_BASE = 16
DISTRACTOR_BASE = 56
D_MODEL = 32
HEADS = 4
D_HEAD = D_MODEL // HEADS
LAYERS = 1
TRAIN_STEPS = 500
BATCH = 48
TRACE_BATCHES = 2
TRACE_BATCH = 12
BLOCK_SIZE = 6
TARGET_MASS = 0.95
QUALITY_COSINE = 0.995
QUALITY_REL_L2 = 0.18
SEED = 5053
SQRT_D = math.sqrt(D_HEAD)


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
            return x, {"q": q.detach().cpu(), "k": k.detach().cpu(), "v": v.detach().cpu(), "probs": probs.detach().cpu()}
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


def train_model() -> tuple[TinyTraceTransformer, dict[str, Any]]:
    torch.set_num_threads(1)
    torch.manual_seed(SEED)
    rng = np.random.default_rng(SEED)
    model = TinyTraceTransformer()
    opt = torch.optim.AdamW(model.parameters(), lr=3.5e-3, weight_decay=0.01)
    losses: list[float] = []
    accs: list[float] = []
    start = time.perf_counter()
    model.train()
    for step in range(TRAIN_STEPS):
        x, y, _ = make_batch(BATCH, rng)
        logits, _ = model(x)
        loss = F.cross_entropy(logits, y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        losses.append(float(loss.detach()))
        if (step + 1) % 20 == 0:
            with torch.no_grad():
                accs.append(float((logits.argmax(dim=-1) == y).float().mean()))
    model.eval()
    eval_accs = []
    with torch.no_grad():
        for j in range(8):
            x, y, _ = make_batch(BATCH, np.random.default_rng(SEED + 1000 + j))
            logits, _ = model(x)
            eval_accs.append(float((logits.argmax(dim=-1) == y).float().mean()))
    return model, {
        "train_steps": TRAIN_STEPS,
        "train_seconds": time.perf_counter() - start,
        "final_train_loss": losses[-1],
        "mean_last20_train_loss": statistics.fmean(losses[-20:]),
        "last_logged_train_accuracy": accs[-1] if accs else None,
        "eval_accuracy": statistics.fmean(eval_accs),
    }


@dataclass
class BlockIndex:
    name: str
    groups: list[np.ndarray]
    centroids: np.ndarray
    radii: np.ndarray
    observable_from_key_cache: bool = True
    uses_generator_oracle_bounds: bool = False
    unsafe_sampled_radius: bool = False
    build_score_free: bool = True
    build_ns: int = 0


@dataclass
class SelectionOut:
    selected: np.ndarray
    qk_dot_products: int
    exact_token_score_dots: int
    block_bound_dots: int
    opened_blocks: int
    asserted_lower_bound_mass_certificate: float
    bound_violation_rate: float
    exact_dense_scores_required: bool
    computes_all_qk_scores_before_selection: bool
    selection_uses_values: bool = False
    selection_uses_dense_output: bool = False
    block_upper_bound_pruning: bool = False
    observable_index_from_key_cache: bool = False
    uses_generator_oracle_bounds: bool = False
    unsafe_sampled_radius: bool = False
    bound_is_certified: bool = True


@dataclass
class Acc:
    rows: int = 0
    selected: float = 0.0
    mass: float = 0.0
    cert: float = 0.0
    rel_l2: float = 0.0
    cosine: float = 0.0
    support: float = 0.0
    max_prob: float = 0.0
    qk_dots: float = 0.0
    exact_token_dots: float = 0.0
    block_bound_dots: float = 0.0
    opened_blocks: float = 0.0
    violations: float = 0.0
    quality_pass: int = 0
    needle_selected: int = 0
    needle_prob: float = 0.0
    model_correct: int = 0
    index_build_ns: float = 0.0

    def add(self, row: dict[str, Any]) -> None:
        self.rows += 1
        self.selected += float(row["selected_count"])
        self.mass += float(row["mass_retained"])
        self.cert += float(row["asserted_lower_bound_mass_certificate"])
        self.rel_l2 += float(row["attention_rel_l2_error"])
        self.cosine += float(row["output_cosine"])
        self.support += float(row["effective_support"])
        self.max_prob += float(row["max_probability"])
        self.qk_dots += float(row["qk_dot_products"])
        self.exact_token_dots += float(row["exact_token_score_dots"])
        self.block_bound_dots += float(row["block_bound_dots"])
        self.opened_blocks += float(row["opened_blocks"])
        self.violations += float(row["bound_violation_rate"])
        self.quality_pass += int(bool(row["passes_quality_bar"]))
        self.needle_selected += int(bool(row["needle_selected"]))
        self.needle_prob += float(row["needle_probability"])
        self.model_correct += int(bool(row["model_correct"]))
        self.index_build_ns += float(row.get("index_build_ns", 0.0) or 0.0)

    def mean(self, attr: str) -> float:
        return float(getattr(self, attr)) / max(1, self.rows)


def dense_scores(q: np.ndarray, k: np.ndarray) -> np.ndarray:
    return (k @ q) / SQRT_D


def contiguous_blocks(n: int, block: int) -> list[np.ndarray]:
    return [np.arange(i, min(i + block, n), dtype=np.int64) for i in range(0, n, block)]


def pca_sorted_blocks(k: np.ndarray, block: int) -> list[np.ndarray]:
    centered = k - k.mean(axis=0, keepdims=True)
    try:
        _, _, vh = np.linalg.svd(centered, full_matrices=False)
        axis = vh[0]
    except np.linalg.LinAlgError:
        axis = np.zeros(k.shape[1], dtype=np.float64)
        axis[0] = 1.0
    order = np.argsort(centered @ axis).astype(np.int64)
    return [order[i : i + block].astype(np.int64) for i in range(0, len(order), block)]


def build_index(name: str, k: np.ndarray, groups: list[np.ndarray], unsafe_sampled_radius: bool = False) -> BlockIndex:
    start = time.perf_counter_ns()
    centroids = []
    radii = []
    for g in groups:
        pts = k[g]
        c = pts.mean(axis=0)
        if unsafe_sampled_radius:
            sample = pts[: max(1, min(2, len(pts)))]
            radius = 0.35 * float(np.max(np.linalg.norm(sample - c, axis=1))) + 1e-9
        else:
            radius = float(np.max(np.linalg.norm(pts - c, axis=1))) + 1e-9
        centroids.append(c)
        radii.append(radius)
    build_ns = time.perf_counter_ns() - start
    return BlockIndex(
        name=name,
        groups=groups,
        centroids=np.asarray(centroids, dtype=np.float64),
        radii=np.asarray(radii, dtype=np.float64),
        unsafe_sampled_radius=unsafe_sampled_radius,
        build_ns=build_ns,
    )


def block_bound_violation_rate(q: np.ndarray, k: np.ndarray, idx: BlockIndex) -> float:
    qnorm = float(np.linalg.norm(q))
    violations = 0
    for bi, g in enumerate(idx.groups):
        ub = float((idx.centroids[bi] @ q) / SQRT_D + qnorm * idx.radii[bi] / SQRT_D)
        actual = (k[g] @ q) / SQRT_D
        if bool(np.any(actual > ub + 1e-7)):
            violations += 1
    return float(violations) / max(1, len(idx.groups))


def block_pruned_selection(q: np.ndarray, k: np.ndarray, idx: BlockIndex, target_mass: float = TARGET_MASS) -> SelectionOut:
    qnorm = float(np.linalg.norm(q))
    ubs = (idx.centroids @ q) / SQRT_D + qnorm * idx.radii / SQRT_D
    order = np.argsort(-ubs)
    opened: list[int] = []
    opened_mask = np.zeros(len(idx.groups), dtype=bool)
    exact_scores: dict[int, float] = {}
    cert = 0.0
    opened_blocks = 0
    for bi in order:
        bi = int(bi)
        opened_mask[bi] = True
        opened_blocks += 1
        for t in idx.groups[bi]:
            t = int(t)
            opened.append(t)
            exact_scores[t] = float((k[t] @ q) / SQRT_D)
        opened_vals = np.fromiter(exact_scores.values(), dtype=np.float64)
        upper_unopened = ubs[~opened_mask]
        if len(opened_vals):
            m = float(np.max(opened_vals))
        else:
            m = -np.inf
        if len(upper_unopened):
            m = max(m, float(np.max(upper_unopened)))
        opened_w = float(np.sum(np.exp(np.clip(opened_vals - m, -80.0, 80.0)))) if len(opened_vals) else 0.0
        unopened_w = 0.0
        for j, ub in enumerate(ubs):
            if not opened_mask[j]:
                unopened_w += len(idx.groups[j]) * float(math.exp(max(-80.0, min(80.0, float(ub - m)))))
        cert = opened_w / max(1e-300, opened_w + unopened_w)
        if cert >= target_mass:
            break
    selected = np.unique(np.asarray(opened, dtype=np.int64))
    return SelectionOut(
        selected=selected,
        qk_dot_products=len(idx.groups) + len(selected),
        exact_token_score_dots=len(selected),
        block_bound_dots=len(idx.groups),
        opened_blocks=opened_blocks,
        asserted_lower_bound_mass_certificate=float(cert),
        bound_violation_rate=block_bound_violation_rate(q, k, idx),
        exact_dense_scores_required=False,
        computes_all_qk_scores_before_selection=False,
        block_upper_bound_pruning=True,
        observable_index_from_key_cache=True,
        unsafe_sampled_radius=idx.unsafe_sampled_radius,
        bound_is_certified=not idx.unsafe_sampled_radius,
    )


def dense_hist_selection(scores: np.ndarray) -> SelectionOut:
    probs = stable_softmax(scores)
    max_score = float(np.max(scores))
    # Reuse the score-only histogram policy from rev0045/52: no sort, coarse bins.
    bins = np.linspace(0.0, 16.0, 33)
    rel = np.maximum(0.0, max_score - scores)
    bid = np.searchsorted(bins, rel, side="right") - 1
    bid = np.clip(bid, 0, len(bins) - 1)
    mass_by = np.zeros(len(bins), dtype=np.float64)
    for b, p in zip(bid, probs):
        mass_by[int(b)] += float(p)
    cum = 0.0
    cutoff = len(bins) - 1
    for b, m in enumerate(mass_by):
        cum += float(m)
        if cum >= TARGET_MASS:
            cutoff = b
            break
    selected = np.flatnonzero(bid <= cutoff).astype(np.int64)
    return SelectionOut(
        selected=selected,
        qk_dot_products=len(scores),
        exact_token_score_dots=len(scores),
        block_bound_dots=0,
        opened_blocks=0,
        asserted_lower_bound_mass_certificate=float(np.sum(probs[selected])),
        bound_violation_rate=0.0,
        exact_dense_scores_required=True,
        computes_all_qk_scores_before_selection=True,
    )


def full_dense_selection(scores: np.ndarray) -> SelectionOut:
    n = len(scores)
    return SelectionOut(
        selected=np.arange(n, dtype=np.int64),
        qk_dot_products=n,
        exact_token_score_dots=n,
        block_bound_dots=0,
        opened_blocks=0,
        asserted_lower_bound_mass_certificate=1.0,
        bound_violation_rate=0.0,
        exact_dense_scores_required=True,
        computes_all_qk_scores_before_selection=True,
    )


def apply_selection(method: str, q: np.ndarray, k: np.ndarray, scores: np.ndarray, indexes: dict[str, BlockIndex]) -> SelectionOut:
    if method == "dense_full_attention":
        return full_dense_selection(scores)
    if method == "dense_score_mass_histogram_0p95_sparse":
        return dense_hist_selection(scores)
    if method == "position_mean_radius_block_pruned_0p95_sparse":
        return block_pruned_selection(q, k, indexes["position"])
    if method == "pca_sorted_mean_radius_block_pruned_0p95_sparse":
        return block_pruned_selection(q, k, indexes["pca"])
    if method == "unsafe_pca_sampled_radius2_block_pruned_0p95_sparse":
        return block_pruned_selection(q, k, indexes["unsafe_pca"])
    raise KeyError(method)


METHODS = [
    "dense_full_attention",
    "dense_score_mass_histogram_0p95_sparse",
    "position_mean_radius_block_pruned_0p95_sparse",
    "pca_sorted_mean_radius_block_pruned_0p95_sparse",
    "unsafe_pca_sampled_radius2_block_pruned_0p95_sparse",
]


def collect_trace_rows(model: TinyTraceTransformer) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    base_rows: list[dict[str, Any]] = []
    with torch.no_grad():
        for tb in range(TRACE_BATCHES):
            x, y, target_pos = make_batch(TRACE_BATCH, np.random.default_rng(SEED + 2000 + tb))
            logits, traces = model(x, capture=True)
            pred = logits.argmax(dim=-1).cpu().numpy()
            yy = y.cpu().numpy()
            for layer_id, tr in enumerate(traces):
                q_all = tr["q"].numpy().astype(np.float64)  # B,H,T,DH
                k_all = tr["k"].numpy().astype(np.float64)
                v_all = tr["v"].numpy().astype(np.float64)
                for b in range(TRACE_BATCH):
                    for h in range(HEADS):
                        q = q_all[b, h, -1]
                        k = k_all[b, h]
                        v = v_all[b, h]
                        scores = dense_scores(q, k)
                        probs = stable_softmax(scores)
                        base_rows.append({
                            "q": q,
                            "k": k,
                            "v": v,
                            "scores": scores,
                            "layer": int(layer_id),
                            "head": int(h),
                            "trace_batch": int(tb),
                            "example": int(b),
                            "needle_position": int(target_pos[b]),
                            "needle_probability": float(probs[int(target_pos[b])]),
                            "max_probability": float(np.max(probs)),
                            "effective_support": float(effective_support(probs)),
                            "model_correct": bool(pred[b] == int(yy[b])),
                        })
    supports = np.array([float(r["effective_support"]) for r in base_rows], dtype=np.float64)
    q25, q75 = np.quantile(supports, [0.25, 0.75]).tolist()
    buckets = {"low_support_le_q25": 0, "middle_support": 0, "high_support_ge_q75": 0}
    for r in base_rows:
        s = float(r["effective_support"])
        if s <= q25:
            r["support_bucket"] = "low_support_le_q25"
        elif s >= q75:
            r["support_bucket"] = "high_support_ge_q75"
        else:
            r["support_bucket"] = "middle_support"
        buckets[r["support_bucket"]] += 1
    meta = {
        "trace_rows": len(base_rows),
        "support_q25": float(q25),
        "support_q75": float(q75),
        "bucket_counts": buckets,
        "model_accuracy_on_trace_examples": float(np.mean([float(r["model_correct"]) for r in base_rows])),
    }
    return base_rows, meta


def evaluate(base_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw: list[dict[str, Any]] = []
    acc: dict[tuple[str, str], Acc] = {}
    for r in base_rows:
        q = r["q"]; k = r["k"]; v = r["v"]; scores = r["scores"]
        n = len(scores)
        groups_position = contiguous_blocks(n, BLOCK_SIZE)
        groups_pca = pca_sorted_blocks(k, BLOCK_SIZE)
        idxs = {
            "position": build_index("position_mean_radius_block_pruned_0p95_sparse", k, groups_position, False),
            "pca": build_index("pca_sorted_mean_radius_block_pruned_0p95_sparse", k, groups_pca, False),
            "unsafe_pca": build_index("unsafe_pca_sampled_radius2_block_pruned_0p95_sparse", k, groups_pca, True),
        }
        for method in METHODS:
            sel = apply_selection(method, q, k, scores, idxs)
            metrics = output_metrics(scores, v, sel.selected)
            pass_bar = passes_attention_quality_bar(metrics, TARGET_MASS)
            row = {
                "trace_source_type": "tiny_trained_transformer_qkv_trace",
                "trace_public_pretrained": False,
                "regime": "tiny_trained_retrieval_final_query",
                "support_bucket": r["support_bucket"],
                "method": method,
                "layer": r["layer"],
                "head": r["head"],
                "N": n,
                "D": D_HEAD,
                "DV": D_HEAD,
                "block_size": BLOCK_SIZE,
                "target_mass": TARGET_MASS,
                "selected_count": int(metrics["selected_count"]),
                "value_reads": int(metrics["selected_count"]),
                "mass_retained": float(metrics["mass_retained"]),
                "asserted_lower_bound_mass_certificate": float(sel.asserted_lower_bound_mass_certificate),
                "certificate_error_abs": float(abs(float(metrics["mass_retained"]) - float(sel.asserted_lower_bound_mass_certificate))),
                "attention_rel_l2_error": float(metrics["attention_rel_l2_error"]),
                "attention_l2_error": float(metrics["attention_l2_error"]),
                "output_cosine": float(metrics["output_cosine"]),
                "passes_quality_bar": bool(pass_bar),
                "effective_support": float(r["effective_support"]),
                "max_probability": float(r["max_probability"]),
                "needle_position": int(r["needle_position"]),
                "needle_probability": float(r["needle_probability"]),
                "needle_selected": bool(int(r["needle_position"]) in set(map(int, sel.selected))),
                "model_correct": bool(r["model_correct"]),
                "qk_dot_products": int(sel.qk_dot_products),
                "qk_dot_fraction_vs_dense": float(sel.qk_dot_products / n),
                "exact_token_score_dots": int(sel.exact_token_score_dots),
                "exact_token_score_fraction_vs_dense": float(sel.exact_token_score_dots / n),
                "block_bound_dots": int(sel.block_bound_dots),
                "opened_blocks": int(sel.opened_blocks),
                "opened_block_fraction": float(sel.opened_blocks / max(1, math.ceil(n / BLOCK_SIZE))),
                "bound_violation_rate": float(sel.bound_violation_rate),
                "exact_dense_scores_required": bool(sel.exact_dense_scores_required),
                "computes_all_qk_scores_before_selection": bool(sel.computes_all_qk_scores_before_selection),
                "block_upper_bound_pruning": bool(sel.block_upper_bound_pruning),
                "observable_index_from_key_cache": bool(sel.observable_index_from_key_cache),
                "uses_generator_oracle_bounds": bool(sel.uses_generator_oracle_bounds),
                "unsafe_sampled_radius": bool(sel.unsafe_sampled_radius),
                "bound_is_certified": bool(sel.bound_is_certified),
                "selection_uses_values": bool(sel.selection_uses_values),
                "selection_uses_dense_output": bool(sel.selection_uses_dense_output),
                "is_gpu_kernel_claim": False,
                "index_build_ns": int(idxs["position"].build_ns if "position" in method else idxs["pca"].build_ns if "pca" in method else 0),
            }
            raw.append(row)
            for bucket in ["all", str(r["support_bucket"]), f"layer{r['layer']}"]:
                key = (bucket, method)
                acc.setdefault(key, Acc()).add(row)
    rows: list[dict[str, Any]] = []
    for (bucket, method), a in sorted(acc.items()):
        rows.append({
            "support_bucket": bucket,
            "method": method,
            "rows": a.rows,
            "n_tokens": SEQ,
            "d_head": D_HEAD,
            "block_size": BLOCK_SIZE,
            "target_mass": TARGET_MASS,
            "mean_effective_support": a.mean("support"),
            "mean_max_probability": a.mean("max_prob"),
            "mean_selected_values": a.mean("selected"),
            "selected_value_fraction": a.mean("selected") / SEQ,
            "mean_true_mass_retained": a.mean("mass"),
            "mean_asserted_lower_bound_mass_certificate": a.mean("cert"),
            "mean_attention_rel_l2_error": a.mean("rel_l2"),
            "mean_output_cosine": a.mean("cosine"),
            "quality_bar_rate": a.quality_pass / max(1, a.rows),
            "needle_selected_rate": a.needle_selected / max(1, a.rows),
            "mean_needle_probability": a.mean("needle_prob"),
            "model_correct_rate": a.model_correct / max(1, a.rows),
            "mean_qk_dot_products": a.mean("qk_dots"),
            "qk_dot_fraction_vs_dense": a.mean("qk_dots") / SEQ,
            "mean_exact_token_score_dots": a.mean("exact_token_dots"),
            "exact_token_score_fraction_vs_dense": a.mean("exact_token_dots") / SEQ,
            "mean_block_bound_dots": a.mean("block_bound_dots"),
            "mean_opened_blocks": a.mean("opened_blocks"),
            "opened_block_fraction": a.mean("opened_blocks") / (SEQ / BLOCK_SIZE),
            "mean_bound_violation_rate": a.mean("violations"),
            "mean_index_build_ns_per_row": a.mean("index_build_ns"),
            "exact_dense_scores_required": method in {"dense_full_attention", "dense_score_mass_histogram_0p95_sparse"},
            "computes_all_qk_scores_before_selection": method in {"dense_full_attention", "dense_score_mass_histogram_0p95_sparse"},
            "block_upper_bound_pruning": "block_pruned" in method,
            "observable_index_from_key_cache": "block_pruned" in method,
            "uses_generator_oracle_bounds": False,
            "unsafe_sampled_radius": method.startswith("unsafe_"),
            "bound_is_certified": not method.startswith("unsafe_"),
            "selection_uses_values": False,
            "selection_uses_dense_output": False,
            "is_gpu_kernel_claim": False,
        })
    return rows, raw


def fmean(xs: Iterable[float]) -> float:
    return statistics.fmean(list(xs))


def make_artifact() -> dict[str, Any]:
    model, train_metrics = train_model()
    base_rows, trace_meta = collect_trace_rows(model)
    rows, raw_rows = evaluate(base_rows)
    all_rows = [r for r in rows if r["support_bucket"] == "all"]
    by_method = {r["method"]: r for r in all_rows}
    pca = by_method.get("pca_sorted_mean_radius_block_pruned_0p95_sparse", {})
    pos = by_method.get("position_mean_radius_block_pruned_0p95_sparse", {})
    unsafe = by_method.get("unsafe_pca_sampled_radius2_block_pruned_0p95_sparse", {})
    hist = by_method.get("dense_score_mass_histogram_0p95_sparse", {})
    low_pca = next((r for r in rows if r["support_bucket"] == "low_support_le_q25" and r["method"] == "pca_sorted_mean_radius_block_pruned_0p95_sparse"), {})
    high_pca = next((r for r in rows if r["support_bucket"] == "high_support_ge_q75" and r["method"] == "pca_sorted_mean_radius_block_pruned_0p95_sparse"), {})
    artifact = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": f"{REVUP}_LEARNED_TRACE_BLOCK_BOUNDS",
        "probe": "learned_trace_block_bounds",
        "kind": "tiny_trained_model_qkv_trace_block_bound_score_path_probe",
        "evidence_tier": "E2p5_tiny_trained_model_trace_score_path_bound_probe",
        "generated_at": "2026-06-18T03:59:00-04:00",
        "promotion_allowed": False,
        "gpu_kernel_claim": False,
        "public_pretrained_trace_loaded": False,
        "trace_source_type": "tiny_trained_transformer_qkv_trace",
        "selection_contract": "block selectors may use q, k, block centroids/radii built from k, and score-only mass certificates; they may not inspect V vectors or dense outputs before selection",
        "configuration": {
            "seq": SEQ,
            "d_model": D_MODEL,
            "heads": HEADS,
            "layers": LAYERS,
            "d_head": D_HEAD,
            "block_size": BLOCK_SIZE,
            "target_mass": TARGET_MASS,
            "quality_cosine_bar": QUALITY_COSINE,
            "quality_rel_l2_bar": QUALITY_REL_L2,
            "seed": SEED,
            "train_steps": TRAIN_STEPS,
            "trace_batches": TRACE_BATCHES,
            "trace_batch": TRACE_BATCH,
        },
        "train_metrics": train_metrics,
        "trace_meta": trace_meta,
        "summary": {
            "promotion_allowed": False,
            "primary_claim": "observable block bounds are tested on tiny learned Q/K/V traces; dense-score selectors still compute every QK score, while block-bound selectors can only claim score-path savings when qk_dot_fraction_vs_dense falls well below one",
            "mass_histogram_qk_fraction": hist.get("qk_dot_fraction_vs_dense"),
            "position_block_qk_fraction": pos.get("qk_dot_fraction_vs_dense"),
            "pca_block_qk_fraction": pca.get("qk_dot_fraction_vs_dense"),
            "pca_block_quality_bar_rate": pca.get("quality_bar_rate"),
            "low_support_pca_qk_fraction": low_pca.get("qk_dot_fraction_vs_dense"),
            "high_support_pca_qk_fraction": high_pca.get("qk_dot_fraction_vs_dense"),
            "unsafe_pca_bound_violation_rate": unsafe.get("mean_bound_violation_rate"),
            "remaining_blockers": [
                "actual_public_pretrained_trace_bundle_missing",
                "gpu_fused_attention_kernel_timing_missing",
                "learned_trace_block_bounds_not_public_pretrained",
                "kernel_implementation_of_block_bound_pruning_missing",
            ],
        },
        "rows": rows,
        "raw_row_count": len(raw_rows),
        "raw_rows_sample": raw_rows[:24],
        "run_provenance": {},
        "interpretation": "This rev0053 probe moves score-path pruning from hand-generated caches onto tiny learned Q/K/V traces. It does not close the public/pretrained or GPU blockers. Its purpose is to expose whether observable block metadata can skip exact QK scores on model-like rows without oracle geometry. Dense score-mass selectors are kept as a control because they can save value reads while still paying every QK dot product.",
    }
    return artifact


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    artifact = make_artifact()
    src_rel = "experiments/learned_trace_block_bounds/learned_trace_block_bounds.py"
    core_rel = "experiments/attention_compiler_core/attention_core.py"
    artifact["run_provenance"] = {
        "script": src_rel,
        "source_path": src_rel,
        "source_sha256": sha256_file(ROOT / src_rel),
        "core_source_path": core_rel,
        "core_source_sha256": sha256_file(ROOT / core_rel),
        "command": "python experiments/learned_trace_block_bounds/learned_trace_block_bounds.py",
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "torch": torch.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "seed_policy": artifact["configuration"],
    }
    OUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "artifact_sha256": sha256_file(OUT),
        "source": src_rel,
        "source_sha256": sha256_file(ROOT / src_rel),
        "core_source": core_rel,
        "core_source_sha256": sha256_file(ROOT / core_rel),
        "command": "python experiments/learned_trace_block_bounds/learned_trace_block_bounds.py",
        "public_pretrained_trace_loaded": False,
        "gpu_kernel_claim": False,
        "promotion_allowed": False,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "artifact": str(OUT.relative_to(ROOT)), "manifest": str(MANIFEST.relative_to(ROOT)), "rows": len(artifact["rows"]), "raw_rows": artifact["raw_row_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
