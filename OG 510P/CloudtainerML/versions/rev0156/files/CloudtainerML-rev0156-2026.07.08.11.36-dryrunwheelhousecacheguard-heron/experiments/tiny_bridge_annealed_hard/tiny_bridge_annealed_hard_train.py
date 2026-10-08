#!/usr/bin/env python3
"""Forward-path annealed hard sparse bridge probe.

rev0042 closes the rev0039/rev0041 labeling defect: temperature and
straight-through hardening now affect the actual attention forward pass instead
of only an auxiliary regularizer over edge logits. The probe still remains a tiny
synthetic falsifier; promotion depends on hard deployed accuracy, not soft loss.
"""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import platform
import random
import sys
from pathlib import Path

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
REV = json.loads((ROOT / "CUBE-META.json").read_text()).get("revision", "rev0042")
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "probe-results"
OUT.mkdir(parents=True, exist_ok=True)

# Reuse the compact boundary-copy world from the post-training sparse bridge probe.
BASE_PATH = ROOT / "experiments" / "tiny_bridge_posttrain_sparsify" / "tiny_bridge_posttrain_sparsify.py"
spec = importlib.util.spec_from_file_location("bridge_base", BASE_PATH)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)

torch.set_num_threads(1)
SEED = 3939
random.seed(SEED)
torch.manual_seed(SEED)
DEVICE = base.DEVICE
EPS_GATE = 1.0e-4


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class AnnealedForwardBoundaryReader(base.BoundaryReader):
    """BoundaryReader whose soft_gate path is genuinely temperature-controlled.

    The inherited forward() calls gate_probs() before adding log gate priors.
    rev0041 left that call at sigmoid(edge_logits), so annealing only shaped an
    auxiliary loss. This subclass makes the forward gate use sigmoid(logit / T)
    and can switch to a straight-through hard gate while keeping a small floor so
    log-priors and gradients remain finite.
    """

    def __init__(self, use_gate: bool = True, init_gate: float = -1.0):
        super().__init__(use_gate=use_gate, init_gate=init_gate)
        self.forward_temp = 1.0
        self.forward_st_hard = False
        self.forward_floor = EPS_GATE

    def configured_probs(self, temp: float | None = None, st_hard: bool | None = None, floor: bool = True):
        if self.edge_logits is None:
            return torch.ones(len(base.CANDIDATES), device=DEVICE)
        t = max(1.0e-3, float(self.forward_temp if temp is None else temp))
        hard = self.forward_st_hard if st_hard is None else bool(st_hard)
        soft = torch.sigmoid(self.edge_logits / t)
        if hard:
            discrete = (soft >= 0.5).to(soft.dtype)
            soft = (discrete - soft).detach() + soft
        if floor:
            soft = self.forward_floor + (1.0 - self.forward_floor) * soft
        return soft

    def gate_probs(self):
        return self.configured_probs()


def load_core_from_dense(dense, init_gate: float = -1.0):
    g = AnnealedForwardBoundaryReader(use_gate=True, init_gate=init_gate).to(DEVICE)
    sd = dense.state_dict()
    g.load_state_dict({k: v for k, v in sd.items() if k in g.state_dict() and g.state_dict()[k].shape == v.shape}, strict=False)
    return g


def edge_prf(edges):
    s = set(edges)
    true = base.TRUE_EDGES
    tp = len(s & true)
    fp = len(s - true)
    fn = len(true - s)
    prec = tp / max(1, tp + fp)
    rec = tp / max(1, tp + fn)
    f1 = 2 * prec * rec / max(1.0e-9, prec + rec)
    return prec, rec, f1


def topk_edges_from_probs(probs, k=None):
    if k is None:
        k = len(base.TRUE_EDGES)
    ranked = [e for _, e in sorted(zip([float(x) for x in probs], base.CANDIDATES), key=lambda pe: -pe[0])]
    return ranked[:k]


def eval_hard_edges(model, edges, label, soft_acc=None):
    acc, miss, reach, src = base.eval_model(model, "hard_edges", hard_edges=list(edges), batch=2048)
    p, r, f = edge_prf(edges)
    return {
        "method": label,
        "final_acc": acc,
        "target_miss": miss,
        "hard_topk_acc": acc,
        "hard_topk_target_miss": miss,
        "hard_topk_depth_reachable_fraction": reach,
        "active_edge_count": len(edges),
        "topk_edge_precision": p,
        "topk_edge_recall": r,
        "topk_edge_f1": f,
        "deployment_gap_soft_to_hard_topk": None if soft_acc is None else soft_acc - acc,
        "source_attention_mass_by_target_pos_last_layer": src,
    }


def eval_soft_forward(model: AnnealedForwardBoundaryReader, temp: float, st_hard: bool, label: str):
    model.forward_temp = temp
    model.forward_st_hard = st_hard
    acc, miss, reach, src = base.eval_model(model, "soft_gate", batch=2048)
    return {
        "method": label,
        "forward_temp": temp,
        "forward_st_hard": st_hard,
        "soft_forward_acc": acc,
        "soft_forward_target_miss": miss,
        "soft_forward_depth_reachable_fraction": reach,
        "source_attention_mass_by_target_pos_last_layer": src,
    }


def hard_finetune_from_sparse_core(sparse_model: AnnealedForwardBoundaryReader, hard_edges, label: str):
    """Fine-tune copied dense/core weights under a deployed hard edge set."""
    m = copy.deepcopy(sparse_model).to(DEVICE)
    # Make the hard-edge deployment independent of any learned gate parameters.
    m.forward_st_hard = False
    for p in m.parameters():
        p.requires_grad_(True)
    opt = torch.optim.AdamW(m.parameters(), lr=1.6e-3, weight_decay=1e-4)
    hist = []
    for step in range(1, base.HARD_FT_STEPS + 1):
        x, y = base.make_batch(base.BATCH)
        logits, _ = m(x, mode="hard_edges", hard_edges=hard_edges)
        loss = F.cross_entropy(logits.reshape(-1, base.VOCAB), y.reshape(-1))
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        if step in {1, 15, 30, 45}:
            acc, _, reach, _ = base.eval_model(m, "hard_edges", hard_edges=hard_edges, batch=512)
            hist.append({"step": step, "loss": float(loss.item()), "acc": acc, "depth_reachable_fraction": reach})
    acc, miss, reach, src = base.eval_model(m, "hard_edges", hard_edges=hard_edges, batch=2048)
    p, r, f = edge_prf(hard_edges)
    return {
        "method": label,
        "final_acc": acc,
        "target_miss": miss,
        "depth_reachable_fraction": reach,
        "active_edge_count": len(hard_edges),
        "topk_edge_precision": p,
        "topk_edge_recall": r,
        "topk_edge_f1": f,
        "history": hist,
        "source_attention_mass_by_target_pos_last_layer": src,
    }


def train_annealed(
    dense,
    label: str,
    lam: float,
    entropy_lam: float,
    temp0: float,
    temp1: float,
    hard_mix_step: int | None,
    margin_lam: float,
    steps: int = 135,
):
    torch.manual_seed(SEED + int(lam * 10000) + int(entropy_lam * 1000) + int(temp1 * 100) + (hard_mix_step or 0))
    g = load_core_from_dense(dense, init_gate=-1.2)
    # Keep core mostly stable; sparse program should emerge from edge priors, not weight relearning.
    g.set_core_requires_grad(False)
    opt = torch.optim.AdamW([g.edge_logits], lr=0.16, weight_decay=0.0)
    history = []
    for step in range(1, steps + 1):
        frac = (step - 1) / max(1, steps - 1)
        temp = temp0 * (temp1 / temp0) ** frac
        g.forward_temp = temp
        g.forward_st_hard = hard_mix_step is not None and step >= hard_mix_step
        x, y = base.make_batch(base.BATCH)
        # This now uses AnnealedForwardBoundaryReader.gate_probs() inside the actual attention logits.
        logits, _ = g(x, mode="soft_gate")
        ce = F.cross_entropy(logits.reshape(-1, base.VOCAB), y.reshape(-1))
        soft_probs = torch.sigmoid(g.edge_logits / temp)
        l0_proxy = soft_probs.mean()
        entropy_proxy = (soft_probs * (1 - soft_probs)).mean()
        topk_vals = torch.topk(soft_probs, k=len(base.TRUE_EDGES) + 1).values
        topk_margin = topk_vals[len(base.TRUE_EDGES) - 1] - topk_vals[len(base.TRUE_EDGES)]
        hard_count_proxy = g.configured_probs(temp=temp, st_hard=True, floor=False).sum()
        count_penalty = torch.relu(hard_count_proxy - len(base.TRUE_EDGES)) / len(base.CANDIDATES)
        loss = ce + lam * l0_proxy + entropy_lam * entropy_proxy + 0.04 * count_penalty - margin_lam * topk_margin
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        if step in {1, 25, 60, 95, 120, 135}:
            acc, _, _, _ = base.eval_model(g, "soft_gate", batch=512)
            history.append({
                "step": step,
                "ce": float(ce.item()),
                "acc": acc,
                "forward_temp": float(temp),
                "forward_st_hard": bool(g.forward_st_hard),
                "mean_gate_temp": float(soft_probs.mean().item()),
                "entropy_proxy": float(entropy_proxy.item()),
                "topk_margin": float(topk_margin.item()),
                "hard_count_proxy": float(hard_count_proxy.item()),
            })

    soft_temp = eval_soft_forward(g, temp1, False, label + "_soft_temp_forward")
    st_forward = eval_soft_forward(g, temp1, True, label + "_st_hard_forward")
    raw_forward = eval_soft_forward(g, 1.0, False, label + "_raw_sigmoid_forward")

    raw_probs = torch.sigmoid(g.edge_logits).detach().cpu().tolist()
    temp_probs = torch.sigmoid(g.edge_logits / temp1).detach().cpu().tolist()
    hard_forward_probs = g.configured_probs(temp=temp1, st_hard=True, floor=False).detach().cpu().tolist()
    topk_raw = topk_edges_from_probs(raw_probs)
    topk_temp = topk_edges_from_probs(temp_probs)
    th05 = [e for p, e in zip(temp_probs, base.CANDIDATES) if p >= 0.5]
    th02 = [e for p, e in zip(temp_probs, base.CANDIDATES) if p >= 0.2]
    raw_metrics = base.edge_metrics_from_probs(raw_probs)
    temp_metrics = base.edge_metrics_from_probs(temp_probs)
    hard_raw = eval_hard_edges(g, topk_raw, label + "_hard_topk_raw", soft_temp["soft_forward_acc"])
    hard_temp = eval_hard_edges(g, topk_temp, label + "_hard_topk_temp", soft_temp["soft_forward_acc"])
    th05_acc, th05_miss, th05_reach, _ = base.eval_model(g, "hard_edges", hard_edges=th05, batch=2048) if th05 else (0.0, 1.0, 0.0, {})
    th02_acc, th02_miss, th02_reach, _ = base.eval_model(g, "hard_edges", hard_edges=th02, batch=2048) if th02 else (0.0, 1.0, 0.0, {})
    row = {
        "method": label,
        "lambda": lam,
        "entropy_lambda": entropy_lam,
        "margin_lambda": margin_lam,
        "temp0": temp0,
        "temp1": temp1,
        "hard_mix_step": hard_mix_step,
        "annealing_in_forward_path": True,
        "forward_gate_class": "AnnealedForwardBoundaryReader",
        "soft_temp_forward_acc": soft_temp["soft_forward_acc"],
        "st_hard_forward_acc": st_forward["soft_forward_acc"],
        "raw_sigmoid_forward_acc": raw_forward["soft_forward_acc"],
        "soft_target_miss": soft_temp["soft_forward_target_miss"],
        "soft_depth_reachable_fraction": soft_temp["soft_forward_depth_reachable_fraction"],
        "hard_topk_acc": hard_temp["hard_topk_acc"],
        "hard_topk_target_miss": hard_temp["hard_topk_target_miss"],
        "hard_topk_depth_reachable_fraction": hard_temp["hard_topk_depth_reachable_fraction"],
        "hard_raw_topk_acc": hard_raw["hard_topk_acc"],
        "hard_threshold_0p5_acc": th05_acc,
        "hard_threshold_0p5_target_miss": th05_miss,
        "hard_threshold_0p5_depth_reachable_fraction": th05_reach,
        "hard_threshold_0p2_acc": th02_acc,
        "hard_threshold_0p2_target_miss": th02_miss,
        "hard_threshold_0p2_depth_reachable_fraction": th02_reach,
        "deployment_gap_soft_to_hard_topk": soft_temp["soft_forward_acc"] - hard_temp["hard_topk_acc"],
        "deployment_gap_st_forward_to_hard_topk": st_forward["soft_forward_acc"] - hard_temp["hard_topk_acc"],
        "deployment_gap_topk_to_threshold_0p5": hard_temp["hard_topk_acc"] - th05_acc,
        "active_edge_count_threshold_0p5": len(th05),
        "active_edge_count_threshold_0p2": len(th02),
        "hard_forward_active_edge_count": int(sum(1 for p in hard_forward_probs if p >= 0.5)),
        "topk_edges_temp": [f"{i}->{j}" for i, j in topk_temp],
        "topk_edges_raw": [f"{i}->{j}" for i, j in topk_raw],
        "topk_edge_f1": hard_temp["topk_edge_f1"],
        "topk_edge_precision": hard_temp["topk_edge_precision"],
        "topk_edge_recall": hard_temp["topk_edge_recall"],
        "edge_f1_threshold_0p5": edge_prf(th05)[2] if th05 else 0.0,
        "edge_f1_threshold_0p2": edge_prf(th02)[2] if th02 else 0.0,
        "true_false_prob_gap_raw": raw_metrics["true_false_prob_gap"],
        "true_false_prob_gap_temp": temp_metrics["true_false_prob_gap"],
        "gate_entropy_proxy_raw": raw_metrics["gate_entropy_proxy"],
        "history": history,
    }
    deployed_modes = {
        "hard_topk": row["hard_topk_acc"],
        "threshold_0p5": row["hard_threshold_0p5_acc"],
        "threshold_0p2": row["hard_threshold_0p2_acc"],
    }
    row["best_deployed_hard_mode"] = max(deployed_modes, key=deployed_modes.get)
    row["best_deployed_hard_acc"] = deployed_modes[row["best_deployed_hard_mode"]]
    row["deployment_gap_soft_to_best_hard"] = soft_temp["soft_forward_acc"] - row["best_deployed_hard_acc"]
    row["promotion_score"] = (
        row["best_deployed_hard_acc"]
        + 0.12 * row["topk_edge_f1"]
        - 0.06 * max(0.0, row["deployment_gap_soft_to_best_hard"])
        - 0.012 * max(0, row["active_edge_count_threshold_0p2"] - len(base.TRUE_EDGES))
    )
    return g, row, hard_temp, [soft_temp, st_forward, raw_forward]


def main():
    dense, dense_hist = base.train_dense()
    dense_acc, dense_miss, dense_reach, _ = base.eval_model(dense, "dense_candidate", batch=2048)
    fixed_acc, fixed_miss, fixed_reach, _ = base.eval_model(dense, "fixed_block", batch=2048)
    rows = [
        {
            "method": "dense_candidate_trained",
            "final_acc": dense_acc,
            "target_miss": dense_miss,
            "depth_reachable_fraction": dense_reach,
            "active_edge_count": len(base.CANDIDATES),
            "topk_edge_f1": 0.0,
            "promotion_score": dense_acc - 0.04 * len(base.CANDIDATES),
            "history": dense_hist,
        },
        {
            "method": "fixed_block_same_weights",
            "final_acc": fixed_acc,
            "target_miss": fixed_miss,
            "depth_reachable_fraction": fixed_reach,
            "active_edge_count": 0,
            "topk_edge_f1": 0.0,
            "promotion_score": fixed_acc,
        },
    ]
    anneal_specs = [
        ("forward_anneal_soft_temp0p35", 0.004, 0.010, 1.8, 0.35, None, 0.020),
        ("forward_anneal_stlate_temp0p25", 0.010, 0.018, 1.8, 0.25, 96, 0.026),
        ("forward_anneal_stmid_temp0p18", 0.018, 0.030, 2.0, 0.18, 72, 0.034),
        ("forward_anneal_rank_temp0p20", 0.007, 0.075, 2.0, 0.20, 104, 0.045),
    ]
    hard_rows = []
    soft_forward_rows = []
    best = None
    best_score = -1.0e9
    for label, lam, ent, t0, t1, hard_mix_step, margin_lam in anneal_specs:
        g, row, hard, soft_rows = train_annealed(dense, label, lam, ent, t0, t1, hard_mix_step, margin_lam)
        rows.append(row)
        hard_rows.append(hard)
        soft_forward_rows.extend(soft_rows)
        if row["promotion_score"] > best_score:
            best_score = row["promotion_score"]
            best = (g, row)
    rows += soft_forward_rows
    rows += hard_rows
    if best:
        topk = [tuple(map(int, e.split("->"))) for e in best[1]["topk_edges_temp"]]
        rows.append(hard_finetune_from_sparse_core(best[0], topk, "hard_finetune_from_best_forward_annealed_topk"))
        rows[-1]["promotion_score"] = rows[-1]["final_acc"] + 0.10 * rows[-1]["topk_edge_f1"] - 0.003 * rows[-1]["active_edge_count"]
        rows.append(base.hard_finetune_from(dense, sorted(base.TRUE_EDGES), "oracle_true_bridge_finetune"))
        rows[-1]["promotion_score"] = rows[-1]["final_acc"] + 0.10 * rows[-1]["topk_edge_f1"] - 0.003 * rows[-1]["active_edge_count"]
    non_oracle = [r for r in rows if "oracle" not in r["method"] and r["method"] != "dense_candidate_trained"]
    deployment_candidates = [r for r in non_oracle if "promotion_score" in r]
    winner = max(deployment_candidates, key=lambda r: r["promotion_score"])
    payload = {
        "project": "CloudtainerML",
        "revision": REV,
        "probe": "tiny_bridge_annealed_hard_train",
        "kind": "trained_tiny_probe",
        "source_ids": ["SRC-0348", "SRC-0356", "SRC-0357", "SRC-0359"],
        "cell_ids": ["CELL-352"],
        "repair_of": "rev0039_rev0041_auxiliary_only_annealing_label_defect",
        "run_provenance": {
            "script": str(Path(__file__).relative_to(ROOT)),
            "source_sha256": sha256_file(Path(__file__)),
            "base_script": str(BASE_PATH.relative_to(ROOT)),
            "base_source_sha256": sha256_file(BASE_PATH),
            "command": "python experiments/tiny_bridge_annealed_hard/tiny_bridge_annealed_hard_train.py",
            "python": sys.version.split()[0],
            "torch": torch.__version__,
            "platform": platform.platform(),
            "seed": SEED,
            "forward_path_repair": "soft_gate attention logits now call AnnealedForwardBoundaryReader.gate_probs(), which uses sigmoid(edge_logits / temperature) and optional straight-through hard gates.",
        },
        "summary": {
            "primary_metric": {"name": "promotion_score", "direction": "higher_is_better"},
            "winner_excluding_dense_and_oracle": winner["method"],
            "annealing_in_forward_path": True,
            "forward_path_repair_status": "implemented_and_executed",
            "best_hard_topk_acc": max(r.get("hard_topk_acc", r.get("final_acc", 0.0)) for r in non_oracle),
            "best_deployed_hard_acc": max(r.get("best_deployed_hard_acc", r.get("final_acc", 0.0)) for r in deployment_candidates),
            "best_deployed_hard_mode": max(deployment_candidates, key=lambda r: r.get("best_deployed_hard_acc", r.get("final_acc", 0.0))).get("best_deployed_hard_mode", "hard_finetune"),
            "best_st_hard_forward_acc": max(r.get("st_hard_forward_acc", 0.0) for r in rows),
            "best_topk_edge_f1": max(r.get("topk_edge_f1", 0.0) for r in rows),
            "best_threshold_0p5_acc": max(r.get("hard_threshold_0p5_acc", 0.0) for r in rows),
            "dense_candidate_acc": dense_acc,
            "fixed_block_acc_same_weights": fixed_acc,
            "guard_fields": [
                "annealing_in_forward_path",
                "soft_temp_forward_acc",
                "st_hard_forward_acc",
                "hard_topk_acc",
                "hard_threshold_0p5_acc",
                "hard_threshold_0p2_acc",
                "deployment_gap_soft_to_hard_topk",
                "deployment_gap_soft_to_best_hard",
                "deployment_gap_st_forward_to_hard_topk",
                "best_deployed_hard_mode",
                "best_deployed_hard_acc",
                "topk_edge_f1",
                "edge_f1_threshold_0p5",
                "edge_f1_threshold_0p2",
                "hard_topk_target_miss",
                "hard_threshold_0p5_target_miss",
                "hard_topk_depth_reachable_fraction",
                "hard_forward_active_edge_count",
                "true_false_prob_gap_temp",
                "gate_entropy_proxy_raw",
            ],
            "interpretation": "rev0042 fixes the mislabeled annealing defect: temperature and optional straight-through hard gates are now in the actual attention forward path. The result is still judged by deployed hard edges and deployment gap, not by soft forward accuracy.",
        },
        "rows": rows,
    }
    path = OUT / f"{REVUP}_TINY_BRIDGE_ANNEALED_HARD_TRAIN_SMOKE.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))


if __name__ == "__main__":
    main()
