#!/usr/bin/env python3
"""Branch cache sharing toy probe.

Inspired by RKSC-style cache sharing for multi-branch reasoning, this is a
synthetic falsifier rather than a reproduction. It asks when hidden-state cosine
similarity is enough to decide that two reasoning branches can safely reuse the
same prefix KV cache.

The probe creates groups of branches. Each branch has:
  * an observable hidden summary used for sharing decisions,
  * a true prefix KV cache used by attention,
  * a latent cache_family that says which branches are actually safe to share.
Some scenarios create semantic masquerades: hidden summaries look similar, but
value vectors have branch-specific payloads that make sharing unsafe.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np


@dataclass
class Row:
    seed: int
    scenario: str
    policy: str
    branches: int
    groups: int
    prefix_len: int
    dim: int
    computed_caches: int
    cache_compute_fraction: float
    implied_speedup: float
    shared_fraction: float
    false_share_rate: float
    mean_output_rel_error: float
    p95_output_rel_error: float
    unacceptable_error_rate: float
    mean_output_cosine: float


def l2norm(x: np.ndarray, axis: int = -1, eps: float = 1e-8) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=axis, keepdims=True) + eps)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / ((np.linalg.norm(a) * np.linalg.norm(b)) + 1e-8))


def softmax(x: np.ndarray) -> np.ndarray:
    y = x - np.max(x)
    e = np.exp(y)
    return e / (np.sum(e) + 1e-12)


def attention_output(q: np.ndarray, k: np.ndarray, v: np.ndarray, temp: float) -> np.ndarray:
    w = softmax((k @ q) / max(temp, 1e-6))
    return w @ v


def make_cache(rng: np.random.Generator, prefix_len: int, dim: int) -> Tuple[np.ndarray, np.ndarray]:
    k = l2norm(rng.normal(size=(prefix_len, dim)))
    v = l2norm(0.65 * k + 0.35 * rng.normal(size=(prefix_len, dim)))
    return k, v


def generate_world(seed: int, scenario: str, groups: int, branches_per_group: int, prefix_len: int, dim: int) -> List[dict]:
    rng = np.random.default_rng(seed)
    group_h = l2norm(rng.normal(size=(groups, dim)))
    branches: List[dict] = []
    params = {
        'clean_semantic': dict(hidden_noise=0.05, kv_noise=0.04, masquerade_frac=0.0, decoy_frac=0.0),
        'mild_drift': dict(hidden_noise=0.10, kv_noise=0.10, masquerade_frac=0.08, decoy_frac=0.0),
        'semantic_masquerade': dict(hidden_noise=0.05, kv_noise=0.06, masquerade_frac=0.35, decoy_frac=0.0),
        'hidden_collision': dict(hidden_noise=0.08, kv_noise=0.08, masquerade_frac=0.10, decoy_frac=0.22),
    }[scenario]
    base_caches = [make_cache(rng, prefix_len, dim) for _ in range(groups)]

    for g in range(groups):
        base_k, base_v = base_caches[g]
        for b in range(branches_per_group):
            masquerade = rng.random() < params['masquerade_frac']
            decoy = rng.random() < params['decoy_frac']
            hidden_group = int(rng.integers(0, groups)) if decoy else g
            hidden = l2norm(group_h[hidden_group] + params['hidden_noise'] * rng.normal(size=dim))

            # Most branches are small perturbations of the group cache. Masquerades
            # look semantically similar but carry a rotated value payload.
            k = l2norm(base_k + params['kv_noise'] * rng.normal(size=(prefix_len, dim)))
            v = l2norm(base_v + params['kv_noise'] * rng.normal(size=(prefix_len, dim)))
            family = f'g{g}'
            if masquerade:
                rot = l2norm(rng.normal(size=(dim, dim)), axis=0)
                # Keep keys close so hidden/query similarity can be high; change values.
                v = l2norm(0.25 * v + 0.75 * (v @ rot))
                family = f'g{g}:mask{b}'

            target = int(rng.integers(0, prefix_len))
            q = l2norm(k[target] + 0.05 * rng.normal(size=dim))
            branches.append(dict(group=g, family=family, hidden=hidden, k=k, v=v, q=q))
    rng.shuffle(branches)
    return branches


def pick_rep(policy: str, branch: dict, reps: List[dict], threshold: float) -> Tuple[int | None, bool]:
    if policy == 'no_sharing':
        return None, False
    if not reps:
        return None, False
    if policy == 'oracle_family':
        for i, rep in enumerate(reps):
            if rep['family'] == branch['family']:
                return i, True
        return None, False
    sims = np.array([cosine(branch['hidden'], r['hidden']) for r in reps])
    best = int(np.argmax(sims))
    if policy == 'aggressive_nearest':
        return best, True
    if policy.startswith('cosine_'):
        return (best, True) if sims[best] >= threshold else (None, False)
    if policy == 'token_exact_prefix':
        # Deliberately strict: only exact family and exact group match. In this
        # synthetic setup it acts as a conservative lower-sharing baseline.
        for i, rep in enumerate(reps):
            if rep['family'] == branch['family'] and rep['group'] == branch['group']:
                return i, True
        return None, False
    raise ValueError(f'unknown policy {policy}')


def eval_policy(seed: int, scenario: str, policy: str, branches: List[dict], groups: int, prefix_len: int, dim: int) -> Row:
    threshold = 0.0
    if policy.startswith('cosine_'):
        threshold = float(policy.split('_', 1)[1])
    reps: List[dict] = []
    errors: List[float] = []
    cosines: List[float] = []
    shared = 0
    false_shared = 0
    temp = 0.11
    for branch in branches:
        true_out = attention_output(branch['q'], branch['k'], branch['v'], temp)
        rep_i, did_share = pick_rep(policy, branch, reps, threshold)
        if did_share and rep_i is not None:
            rep = reps[rep_i]
            approx_out = attention_output(branch['q'], rep['k'], rep['v'], temp)
            shared += 1
            if rep['family'] != branch['family']:
                false_shared += 1
        else:
            reps.append(branch)
            approx_out = true_out
        rel_err = float(np.linalg.norm(approx_out - true_out) / (np.linalg.norm(true_out) + 1e-8))
        errors.append(rel_err)
        cosines.append(cosine(approx_out, true_out))
    n = len(branches)
    computed = len(reps)
    return Row(
        seed=seed,
        scenario=scenario,
        policy=policy,
        branches=n,
        groups=groups,
        prefix_len=prefix_len,
        dim=dim,
        computed_caches=computed,
        cache_compute_fraction=float(computed / n),
        implied_speedup=float(n / max(computed, 1)),
        shared_fraction=float(shared / n),
        false_share_rate=float(false_shared / max(shared, 1)),
        mean_output_rel_error=float(np.mean(errors)),
        p95_output_rel_error=float(np.percentile(errors, 95)),
        unacceptable_error_rate=float(np.mean(np.array(errors) > 0.25)),
        mean_output_cosine=float(np.mean(cosines)),
    )


def summarize(rows: List[Row]) -> dict:
    summary: Dict[str, dict] = {}
    for scenario in sorted(set(r.scenario for r in rows)):
        for policy in sorted(set(r.policy for r in rows)):
            sub = [r for r in rows if r.scenario == scenario and r.policy == policy]
            if not sub:
                continue
            key = f'{scenario}/{policy}'
            summary[key] = {
                'mean_cache_compute_fraction': float(np.mean([r.cache_compute_fraction for r in sub])),
                'mean_implied_speedup': float(np.mean([r.implied_speedup for r in sub])),
                'mean_false_share_rate': float(np.mean([r.false_share_rate for r in sub])),
                'mean_output_rel_error': float(np.mean([r.mean_output_rel_error for r in sub])),
                'mean_p95_output_rel_error': float(np.mean([r.p95_output_rel_error for r in sub])),
                'mean_unacceptable_error_rate': float(np.mean([r.unacceptable_error_rate for r in sub])),
                'mean_output_cosine': float(np.mean([r.mean_output_cosine for r in sub])),
            }
    return {'row_count': len(rows), 'by_scenario_policy': summary}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=Path('artifacts/probe-results/REV0006_BRANCH_CACHE_SHARING_SMOKE'))
    ap.add_argument('--seeds', type=int, default=12)
    ap.add_argument('--groups', type=int, default=8)
    ap.add_argument('--branches-per-group', type=int, default=6)
    ap.add_argument('--prefix-len', type=int, default=64)
    ap.add_argument('--dim', type=int, default=32)
    args = ap.parse_args()

    scenarios = ['clean_semantic', 'mild_drift', 'semantic_masquerade', 'hidden_collision']
    policies = ['no_sharing', 'token_exact_prefix', 'oracle_family', 'cosine_0.95', 'cosine_0.90', 'cosine_0.85', 'aggressive_nearest']
    rows: List[Row] = []
    for seed in range(args.seeds):
        for scenario in scenarios:
            world = generate_world(seed, scenario, args.groups, args.branches_per_group, args.prefix_len, args.dim)
            for policy in policies:
                rows.append(eval_policy(seed, scenario, policy, world, args.groups, args.prefix_len, args.dim))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    csv_path = args.out.with_suffix('.csv')
    json_path = args.out.with_suffix('.json')
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for r in rows:
            writer.writerow(asdict(r))
    payload = {
        'probe': 'branch_cache_sharing',
        'purpose': 'Synthetic ASKS/RKSC-style cache sharing tradeoff probe: speedup vs semantic false sharing.',
        'csv': str(csv_path),
        'config': {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()} | {'scenarios': scenarios, 'policies': policies},
        'summary': summarize(rows),
        'interpretation': 'Cache sharing is attractive only if hidden-summary similarity tracks value-cache equivalence; masquerades expose false-sharing risk.',
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(json.dumps(payload['summary'], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
