#!/usr/bin/env python3
from __future__ import annotations

import argparse, csv, json, math, random, time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class RunResult:
    variant: str
    seed: int
    steps: int
    params: int
    cache_components_per_token: int
    cache_scalar_ratio_vs_qkv: float
    final_train_loss: float
    eval_loss: float
    eval_accuracy: float
    seconds: float


class ProjectionSharedAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int, variant: str):
        super().__init__()
        assert d_model % n_heads == 0
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        self.variant = variant
        if variant == 'qkv':
            self.q = nn.Linear(d_model, d_model, bias=False)
            self.k = nn.Linear(d_model, d_model, bias=False)
            self.v = nn.Linear(d_model, d_model, bias=False)
        elif variant == 'k_equals_v':
            self.q = nn.Linear(d_model, d_model, bias=False)
            self.kv = nn.Linear(d_model, d_model, bias=False)
        elif variant == 'q_equals_k':
            self.qk = nn.Linear(d_model, d_model, bias=False)
            self.v = nn.Linear(d_model, d_model, bias=False)
        elif variant == 'q_equals_k_equals_v':
            self.qkv_shared = nn.Linear(d_model, d_model, bias=False)
        else:
            raise ValueError(f'unknown variant {variant}')
        self.out = nn.Linear(d_model, d_model, bias=False)

    def project(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        if self.variant == 'qkv':
            q,k,v = self.q(x), self.k(x), self.v(x)
        elif self.variant == 'k_equals_v':
            q = self.q(x); k = v = self.kv(x)
        elif self.variant == 'q_equals_k':
            q = k = self.qk(x); v = self.v(x)
        else:
            q = k = v = self.qkv_shared(x)
        return q,k,v

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B,T,D = x.shape
        q,k,v = self.project(x)
        def split(t):
            return t.view(B,T,self.n_heads,self.d_head).transpose(1,2)
        q,k,v = split(q), split(k), split(v)
        logits = (q @ k.transpose(-2,-1)) / math.sqrt(self.d_head)
        # Final query should not attend to itself in the lookup task; earlier tokens are visible.
        mask = torch.triu(torch.ones(T,T,device=x.device,dtype=torch.bool), diagonal=1)
        logits = logits.masked_fill(mask, -1e9)
        weights = torch.softmax(logits, dim=-1)
        y = weights @ v
        y = y.transpose(1,2).contiguous().view(B,T,D)
        return self.out(y)


class TinyLookupModel(nn.Module):
    def __init__(self, vocab: int, max_len: int, d_model: int, n_heads: int, variant: str):
        super().__init__()
        self.tok = nn.Embedding(vocab, d_model)
        self.pos = nn.Embedding(max_len, d_model)
        self.attn = ProjectionSharedAttention(d_model, n_heads, variant)
        self.norm = nn.LayerNorm(d_model)
        self.mlp = nn.Sequential(nn.Linear(d_model, 2*d_model), nn.GELU(), nn.Linear(2*d_model, d_model))
        self.head = nn.Linear(d_model, vocab)

    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        B,T = tokens.shape
        pos = torch.arange(T, device=tokens.device).unsqueeze(0)
        x = self.tok(tokens) + self.pos(pos)
        x = x + self.attn(self.norm(x))
        x = x + self.mlp(self.norm(x))
        return self.head(x[:, -1, :])


def make_batch(batch: int, pairs: int, vocab_keys: int, vocab_values: int, device: str) -> Tuple[torch.Tensor, torch.Tensor]:
    # Token ranges are disjoint so the model must learn pair structure, not just copy surface frequency.
    # Sequence: K1 V1 K2 V2 ... Kn Vn QUERY_KEY. Label is matching value.
    seq_len = pairs*2 + 1
    x = torch.zeros(batch, seq_len, dtype=torch.long, device=device)
    y = torch.zeros(batch, dtype=torch.long, device=device)
    for b in range(batch):
        keys = torch.randperm(vocab_keys, device=device)[:pairs] + 1
        values = torch.randint(0, vocab_values, (pairs,), device=device) + 1 + vocab_keys
        query_idx = torch.randint(0, pairs, (1,), device=device).item()
        seq = torch.empty(seq_len, dtype=torch.long, device=device)
        seq[0:2*pairs:2] = keys
        seq[1:2*pairs:2] = values
        seq[-1] = keys[query_idx]
        x[b] = seq
        y[b] = values[query_idx]
    return x,y


def evaluate(model, batches: int, batch: int, pairs: int, vocab_keys: int, vocab_values: int, device: str):
    model.eval()
    losses=[]; correct=0; total=0
    with torch.no_grad():
        for _ in range(batches):
            x,y = make_batch(batch,pairs,vocab_keys,vocab_values,device)
            logits = model(x)
            losses.append(F.cross_entropy(logits,y).item())
            correct += (logits.argmax(dim=-1)==y).sum().item()
            total += y.numel()
    return sum(losses)/len(losses), correct/total


def cache_components(variant: str) -> int:
    # Components that must be cached per generated token: standard/Q=K need K+V; K=V/Q=K=V cache one tensor.
    return 1 if variant in {'k_equals_v','q_equals_k_equals_v'} else 2


def run_variant(variant: str, seed: int, steps: int, batch: int, pairs: int, d_model: int, n_heads: int, lr: float, device: str) -> RunResult:
    random.seed(seed); torch.manual_seed(seed)
    vocab_keys = 32; vocab_values = 32; vocab = 1 + vocab_keys + vocab_values
    model = TinyLookupModel(vocab, pairs*2+1, d_model, n_heads, variant).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-3)
    t0 = time.time(); last_loss = None
    for step in range(steps):
        model.train()
        x,y = make_batch(batch,pairs,vocab_keys,vocab_values,device)
        logits = model(x)
        loss = F.cross_entropy(logits,y)
        opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
        last_loss = float(loss.item())
    ev_loss, ev_acc = evaluate(model, batches=10, batch=batch, pairs=pairs, vocab_keys=vocab_keys, vocab_values=vocab_values, device=device)
    comps = cache_components(variant)
    return RunResult(variant=variant, seed=seed, steps=steps, params=sum(p.numel() for p in model.parameters()), cache_components_per_token=comps, cache_scalar_ratio_vs_qkv=comps/2.0, final_train_loss=last_loss, eval_loss=ev_loss, eval_accuracy=ev_acc, seconds=time.time()-t0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--steps', type=int, default=120)
    ap.add_argument('--batch', type=int, default=64)
    ap.add_argument('--pairs', type=int, default=6)
    ap.add_argument('--d-model', type=int, default=48)
    ap.add_argument('--n-heads', type=int, default=3)
    ap.add_argument('--lr', type=float, default=3e-3)
    ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--device', default='cpu')
    ap.add_argument('--out', default='artifacts/probe-results/REV0005_QKV_PROJECTION_SMOKE.json')
    args = ap.parse_args()
    variants=['qkv','k_equals_v','q_equals_k','q_equals_k_equals_v']
    results=[]
    for i,v in enumerate(variants):
        results.append(run_variant(v, args.seed+i, args.steps, args.batch, args.pairs, args.d_model, args.n_heads, args.lr, args.device))
    out=Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    payload={'probe':'qkv_projection_sharing','note':'Tiny synthetic smoke only; not a reproduction of large language-model results.','args':vars(args),'results':[asdict(r) for r in results]}
    out.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    csv_path=out.with_suffix('.csv')
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=list(asdict(results[0]).keys()))
        w.writeheader(); [w.writerow(asdict(r)) for r in results]
    print(json.dumps(payload, indent=2))

if __name__ == '__main__':
    main()
