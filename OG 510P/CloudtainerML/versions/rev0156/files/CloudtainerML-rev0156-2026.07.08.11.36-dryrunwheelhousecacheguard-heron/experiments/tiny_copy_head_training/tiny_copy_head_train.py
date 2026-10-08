#!/usr/bin/env python3
"""
REV0032 Tiny Copy-Head Training Probe.

A deliberately tiny trained experiment inspired by recent copy-head phase-transition work.
It is NOT a reproduction. It asks whether a one-query pointer-copy model gives different
emergence shapes for softmax, sparsemax, and relu-normalized attention under the same task.

Task:
  context tokens x[0:L], pointer token p_j at final position -> predict x[j].

Outputs JSON/CSV with per-step accuracy, target attention mass, and crude abruptness metrics.
"""
from __future__ import annotations
import argparse, csv, json, math, random, time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import torch
torch.set_num_threads(2)
import torch.nn as nn
import torch.nn.functional as F


def sparsemax(logits: torch.Tensor, dim: int = -1) -> torch.Tensor:
    z = logits - logits.max(dim=dim, keepdim=True).values
    z_sorted, _ = torch.sort(z, descending=True, dim=dim)
    z_cumsum = z_sorted.cumsum(dim) - 1
    ks = torch.arange(1, z.size(dim) + 1, device=z.device, dtype=z.dtype)
    view = [1] * z.dim(); view[dim] = -1
    ks = ks.view(*view)
    support = z_sorted - z_cumsum / ks > 0
    k = support.sum(dim=dim, keepdim=True).clamp_min(1)
    tau = z_cumsum.gather(dim, k - 1) / k.to(z.dtype)
    return torch.clamp(z - tau, min=0.0)


def make_batch(batch: int, L: int, V: int, device: torch.device, generator: torch.Generator):
    tokens = torch.randint(0, V, (batch, L), device=device, generator=generator)
    ptr = torch.randint(0, L, (batch,), device=device, generator=generator)
    target = tokens.gather(1, ptr[:, None]).squeeze(1)
    return tokens, ptr, target


class CopyPointerModel(nn.Module):
    def __init__(self, L: int, V: int, d: int, attn: str):
        super().__init__()
        self.L=L; self.V=V; self.d=d; self.attn=attn
        self.token_value = nn.Embedding(V, d)
        self.pos_key = nn.Embedding(L, d)
        self.pointer_query = nn.Embedding(L, d)
        self.out = nn.Linear(d, V, bias=False)
        nn.init.normal_(self.token_value.weight, std=0.2)
        nn.init.normal_(self.pos_key.weight, std=0.2)
        nn.init.normal_(self.pointer_query.weight, std=0.2)
    def forward(self, tokens: torch.Tensor, ptr: torch.Tensor):
        B,L = tokens.shape
        pos = torch.arange(L, device=tokens.device)
        K = self.pos_key(pos).unsqueeze(0).expand(B, L, self.d)
        Vv = self.token_value(tokens)
        q = self.pointer_query(ptr).unsqueeze(1)
        scores = (q * K).sum(-1) / math.sqrt(self.d)
        if self.attn == 'softmax':
            w = torch.softmax(scores, dim=-1)
        elif self.attn == 'relu_norm':
            w = F.relu(scores) + 1e-6
            w = w / w.sum(dim=-1, keepdim=True)
        elif self.attn == 'sparsemax':
            w = sparsemax(scores, dim=-1)
            w = w / w.sum(dim=-1, keepdim=True).clamp_min(1e-6)
        elif self.attn == 'cosine_relu':
            # non-exponential cosine-ish readout; a cheap software proxy inspired by oscillator/cosine attention.
            qn = F.normalize(q, dim=-1)
            kn = F.normalize(K, dim=-1)
            cs = (qn * kn).sum(-1)
            w = F.relu(cs) + 1e-6
            w = w / w.sum(dim=-1, keepdim=True)
        else:
            raise ValueError(self.attn)
        ctx = torch.bmm(w.unsqueeze(1), Vv).squeeze(1)
        logits = self.out(ctx)
        return logits, w


def train_one(attn: str, seed: int, steps: int, batch: int, L: int, V: int, d: int, lr: float, device: torch.device):
    torch.manual_seed(seed); random.seed(seed)
    gen = torch.Generator(device=device).manual_seed(seed + 991)
    model = CopyPointerModel(L,V,d,attn).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    rows=[]
    reached90=None; reached95=None
    last_loss=None
    for step in range(steps+1):
        if step > 0:
            model.train()
            tokens, ptr, target = make_batch(batch, L, V, device, gen)
            logits, w = model(tokens, ptr)
            loss = F.cross_entropy(logits, target)
            opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
            last_loss = float(loss.detach().cpu())
        if step % max(1, steps//40) == 0 or step == steps:
            model.eval()
            with torch.no_grad():
                vt, vp, vy = make_batch(512, L, V, device, gen)
                vlogits, vw = model(vt, vp)
                pred = vlogits.argmax(-1)
                acc = float((pred == vy).float().mean().cpu())
                target_mass = float(vw.gather(1, vp[:,None]).mean().cpu())
                entropy = float((-(vw.clamp_min(1e-9) * vw.clamp_min(1e-9).log()).sum(-1)).mean().cpu())
                max_mass = float(vw.max(dim=-1).values.mean().cpu())
                if reached90 is None and acc >= 0.90: reached90 = step
                if reached95 is None and acc >= 0.95: reached95 = step
                rows.append({
                    'step': step, 'attn': attn, 'seed': seed, 'loss': last_loss if last_loss is not None else None,
                    'acc': acc, 'target_mass': target_mass, 'entropy': entropy, 'max_mass': max_mass,
                })
    # Crude abruptness: biggest finite difference in target mass and accuracy between checkpoints.
    max_dacc=0.0; max_dmass=0.0; transition_width=None
    for a,b in zip(rows, rows[1:]):
        dt=max(1,b['step']-a['step'])
        max_dacc=max(max_dacc, (b['acc']-a['acc'])/dt)
        max_dmass=max(max_dmass, (b['target_mass']-a['target_mass'])/dt)
    above20=[r['step'] for r in rows if r['target_mass']>=0.20]
    above80=[r['step'] for r in rows if r['target_mass']>=0.80]
    if above20 and above80: transition_width=max(0, min(above80)-min(above20))
    summary={
        'attn': attn, 'seed': seed, 'final_acc': rows[-1]['acc'], 'final_target_mass': rows[-1]['target_mass'],
        'final_entropy': rows[-1]['entropy'], 'reached90_step': reached90, 'reached95_step': reached95,
        'max_dacc_per_step': max_dacc, 'max_dmass_per_step': max_dmass,
        'transition_width_steps': transition_width,
    }
    return rows, summary


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out-dir', default='artifacts/probe-results')
    ap.add_argument('--revision', default='REV0032')
    ap.add_argument('--steps', type=int, default=180)
    ap.add_argument('--batch', type=int, default=64)
    ap.add_argument('--L', type=int, default=8)
    ap.add_argument('--V', type=int, default=16)
    ap.add_argument('--d', type=int, default=24)
    ap.add_argument('--lr', type=float, default=2e-2)
    ap.add_argument('--seeds', type=int, default=1)
    ap.add_argument('--attn', nargs='+', default=['softmax','sparsemax','relu_norm','cosine_relu'])
    args=ap.parse_args()
    root=Path(__file__).resolve().parents[2]
    out_dir=(root/args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    device=torch.device('cpu')
    all_rows=[]; summaries=[]
    t0=time.time()
    for attn in args.attn:
        for seed in range(args.seeds):
            rows, summary=train_one(attn, seed, args.steps, args.batch, args.L, args.V, args.d, args.lr, device)
            all_rows.extend(rows); summaries.append(summary)
    # aggregate
    agg=[]
    for attn in args.attn:
        ss=[s for s in summaries if s['attn']==attn]
        def mean(key):
            vals=[s[key] for s in ss if s[key] is not None]
            return sum(vals)/len(vals) if vals else None
        agg.append({
            'attn': attn,
            'mean_final_acc': mean('final_acc'),
            'mean_final_target_mass': mean('final_target_mass'),
            'mean_reached90_step': mean('reached90_step'),
            'mean_reached95_step': mean('reached95_step'),
            'mean_max_dacc_per_step': mean('max_dacc_per_step'),
            'mean_transition_width_steps': mean('transition_width_steps'),
            'seeds': len(ss),
        })
    winner=sorted(agg, key=lambda x: (-(x['mean_final_acc'] or 0), x['mean_reached95_step'] if x['mean_reached95_step'] is not None else 1e9))[0]
    obj={
        'revision': args.revision.lower(),
        'probe_id': 'tiny_copy_head_training',
        'kind': 'trained_tiny_probe',
        'note': 'Tiny pointer-copy model; synthetic trained escalation, not paper reproduction.',
        'config': vars(args),
        'summary': {
            'primary_metric': {'name': 'mean_final_acc', 'direction': 'higher_is_better', 'winner_field': 'attn'},
            'winner_by_final_acc_then_speed': winner['attn'],
            'elapsed_seconds': time.time()-t0,
            'aggregate': agg,
            'guard_fields': ['final_acc','reached95_step','max_dacc_per_step','transition_width_steps','target_mass'],
        },
        'seed_summaries': summaries,
        'rows': all_rows,
    }
    json_path=out_dir/f'{args.revision}_TINY_COPY_HEAD_TRAINING_SMOKE.json'
    csv_path=out_dir/f'{args.revision}_TINY_COPY_HEAD_TRAINING_SMOKE.csv'
    json_path.write_text(json.dumps(obj, indent=2), encoding='utf-8')
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        writer=csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader(); writer.writerows(all_rows)
    print(json.dumps(obj['summary'], indent=2))
if __name__=='__main__':
    main()
