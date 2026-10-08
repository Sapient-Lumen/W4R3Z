#!/usr/bin/env python3
from __future__ import annotations
import json, math, random
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
REV = json.loads((ROOT/'CUBE-META.json').read_text()).get('revision','rev0035')
REVUP = REV.upper()
OUT = ROOT/'artifacts'/'probe-results'
OUT.mkdir(parents=True, exist_ok=True)

# Tiny trained guard for the boundary-reachability hypothesis:
# A one-head attention reader must copy the value immediately before a block boundary.
# Fixed block-causal attention cannot see that source at the first token of a block;
# bridge/sliding/full variants can. The task is deliberately minimal so reachability,
# not model capacity, is the bottleneck.

torch.set_num_threads(1)
SEED = 3535
random.seed(SEED)
torch.manual_seed(SEED)
DEVICE = torch.device('cpu')
L = 16
B = 4
VOCAB = 16
D = 48
TARGET_POS = torch.tensor([4, 8, 12], dtype=torch.long)
STEPS = 220
BATCH = 192


def build_mask(kind: str) -> torch.Tensor:
    m = torch.zeros(L, L, dtype=torch.bool)
    for i in range(L):
        for j in range(i + 1):
            same_block = (i // B) == (j // B)
            if kind == 'full_causal':
                ok = True
            elif kind == 'fixed_block':
                ok = same_block
            elif kind == 'sliding_w2':
                ok = (i - j) <= 2
            elif kind == 'source_extended_bridge':
                ok = same_block or (i % B == 0 and j == i - 1)
            elif kind == 'post_boundary_bridge':
                ok = same_block or (i % B in (0, 1) and i - j <= 2 and (j // B) == (i // B) - 1)
            elif kind == 'periodic_skip_b4':
                ok = same_block or j == i - B
            else:
                raise ValueError(kind)
            if ok:
                m[i, j] = True
    return m


class OneHeadReader(nn.Module):
    def __init__(self, mask: torch.Tensor):
        super().__init__()
        self.value_emb = nn.Embedding(VOCAB, D)
        self.pos_emb = nn.Embedding(L, D)
        self.q = nn.Linear(D, D, bias=False)
        self.k = nn.Linear(D, D, bias=False)
        self.v = nn.Linear(D, D, bias=False)
        self.o = nn.Linear(D, VOCAB)
        self.register_buffer('mask', mask)

    def forward(self, x: torch.Tensor):
        # x: batch x L integer values. All target tokens carry unrelated random values;
        # the only way to get the label is to read the reachable previous-boundary source.
        b = x.shape[0]
        pos = torch.arange(L, device=x.device).unsqueeze(0).expand(b, L)
        h = self.value_emb(x) + self.pos_emb(pos)
        q = self.q(h)
        k = self.k(h)
        v = self.v(h)
        scores = q @ k.transpose(-1, -2) / math.sqrt(D)
        scores = scores.masked_fill(~self.mask.unsqueeze(0), -1e9)
        att = torch.softmax(scores, dim=-1)
        y = att @ v
        logits = self.o(y[:, TARGET_POS, :])
        return logits, att[:, TARGET_POS, :]


def make_batch(batch: int):
    x = torch.randint(0, VOCAB, (batch, L), dtype=torch.long, device=DEVICE)
    y = x[:, TARGET_POS - 1].clone()
    # Make sure target's own token is decorrelated from the source to prevent self-copy cheating.
    for idx, pos in enumerate(TARGET_POS.tolist()):
        same = x[:, pos] == y[:, idx]
        if same.any():
            x[same, pos] = (x[same, pos] + 1) % VOCAB
    return x, y


def train_one(kind: str):
    mask = build_mask(kind).to(DEVICE)
    torch.manual_seed(SEED + sum(ord(c) for c in kind))
    model = OneHeadReader(mask).to(DEVICE)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-3, weight_decay=1e-4)
    reach_flags = [bool(mask[int(t), int(t)-1].item()) for t in TARGET_POS]
    history=[]
    best=0.0
    for step in range(1, STEPS + 1):
        x,y = make_batch(BATCH)
        logits, att = model(x)
        loss = F.cross_entropy(logits.reshape(-1, VOCAB), y.reshape(-1))
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        if step % 20 == 0 or step == 1:
            with torch.no_grad():
                xt, yt = make_batch(1024)
                lg, at = model(xt)
                pred = lg.argmax(-1)
                acc = (pred == yt).float().mean().item()
                src_mass = at[:, torch.arange(len(TARGET_POS)), TARGET_POS-1].mean().item()
                best = max(best, acc)
                history.append({'step':step,'loss':float(loss.item()),'acc':acc,'source_attention_mass':src_mass})
    with torch.no_grad():
        xt, yt = make_batch(4096)
        lg, at = model(xt)
        pred = lg.argmax(-1)
        acc_by_pos = (pred == yt).float().mean(dim=0).cpu().tolist()
        final_acc = (pred == yt).float().mean().item()
        src_mass_by_pos = at[:, torch.arange(len(TARGET_POS)), TARGET_POS-1].mean(dim=0).cpu().tolist()
    return {
        'mask': kind,
        'reachable_sources': reach_flags,
        'reachable_fraction': sum(reach_flags)/len(reach_flags),
        'final_acc': final_acc,
        'best_acc': best,
        'acc_by_target_pos': {str(int(p)): float(a) for p,a in zip(TARGET_POS.tolist(), acc_by_pos)},
        'source_attention_mass_by_target_pos': {str(int(p)): float(a) for p,a in zip(TARGET_POS.tolist(), src_mass_by_pos)},
        'history': history,
    }


def main():
    kinds = ['fixed_block','periodic_skip_b4','sliding_w2','source_extended_bridge','post_boundary_bridge','full_causal']
    rows = [train_one(k) for k in kinds]
    non_oracle = [r for r in rows if r['mask'] != 'full_causal']
    winner = max(non_oracle, key=lambda r: (r['final_acc'], -abs(r['reachable_fraction']-1.0)))['mask']
    payload = {
        'project':'CloudtainerML',
        'revision':REV,
        'probe':'tiny_boundary_reach_train',
        'kind':'trained_tiny_probe',
        'source_ids':['SRC-0348'],
        'cell_ids':['CELL-336'],
        'summary':{
            'primary_metric':{'name':'final_acc','direction':'higher_is_better'},
            'winner_excluding_full_oracle':winner,
            'mean_final_acc':sum(r['final_acc'] for r in rows)/len(rows),
            'guard_fields':['reachable_sources','reachable_fraction','source_attention_mass_by_target_pos','acc_by_target_pos','target_miss'],
            'interpretation':'Tiny trained copy probe converts the boundary-reachability symbolic result into a learned one-head task: inaccessible boundary sources remain hard even when capacity is sufficient.',
        },
        'rows':rows,
    }
    path = OUT/f'{REVUP}_TINY_BOUNDARY_REACH_TRAIN_SMOKE.json'
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(json.dumps(payload['summary'], indent=2))

if __name__ == '__main__':
    main()
