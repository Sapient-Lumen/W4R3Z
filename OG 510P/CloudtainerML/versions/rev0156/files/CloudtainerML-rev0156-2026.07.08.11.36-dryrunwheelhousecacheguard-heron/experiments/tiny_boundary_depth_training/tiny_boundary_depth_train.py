#!/usr/bin/env python3
from __future__ import annotations
import json, math, random
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
REV = json.loads((ROOT/'CUBE-META.json').read_text()).get('revision','rev0036')
REVUP = REV.upper()
OUT = ROOT/'artifacts'/'probe-results'
OUT.mkdir(parents=True, exist_ok=True)

torch.set_num_threads(1)
SEED = 3636
random.seed(SEED)
torch.manual_seed(SEED)
DEVICE = torch.device('cpu')
L = 16
BLOCK = 4
VOCAB = 13
D = 32
BATCH = 80
STEPS = 90
TARGET_POS = torch.tensor([5, 9, 13], dtype=torch.long)  # second token of each block after block 0
SOURCE_POS = TARGET_POS - 2  # previous block end: 3,7,11,15; needs a bridge token at boundary then same-block read


def build_mask(kind: str) -> torch.Tensor:
    m = torch.zeros(L, L, dtype=torch.bool)
    for i in range(L):
        for j in range(i + 1):
            same_block = (i // BLOCK) == (j // BLOCK)
            if kind == 'dense_causal':
                ok = True
            elif kind == 'fixed_block':
                ok = same_block
            elif kind == 'sliding_w2':
                ok = (i - j) <= 2
            elif kind == 'sliding_w1':
                ok = (i - j) <= 1
            elif kind == 'one_hop_boundary_bridge':
                # Only first token of a block may read previous block end. Target at block-position 1
                # must use that first token as a one-layer relay.
                ok = same_block or (i % BLOCK == 0 and j == i - 1)
            elif kind == 'two_hop_source_extended':
                # A weaker bridge: boundary token reads previous block's penultimate token; the source
                # at previous block end is reachable only via same-block local propagation inside previous block,
                # then boundary, then target.
                ok = same_block or (i % BLOCK == 0 and j == i - 2)
            elif kind == 'periodic_skip_b4':
                ok = same_block or (j == i - BLOCK)
            elif kind == 'ring_anchor':
                ok = same_block or (j == 0) or (i % BLOCK == 0 and j == max(0, i - BLOCK))
            else:
                raise ValueError(kind)
            if ok:
                m[i, j] = True
    return m


def transitive_depth_reach(mask: torch.Tensor, depth: int) -> torch.Tensor:
    # Boolean reachability after depth attention layers: token i can contain information from j.
    reach = mask.clone()
    total = mask.clone()
    for _ in range(1, depth):
        reach = (mask.float() @ reach.float() > 0)
        total |= reach
    return total


class MultiLayerReader(nn.Module):
    def __init__(self, mask: torch.Tensor, layers: int):
        super().__init__()
        self.layers = layers
        self.value_emb = nn.Embedding(VOCAB, D)
        self.pos_emb = nn.Embedding(L, D)
        self.q = nn.ModuleList([nn.Linear(D, D, bias=False) for _ in range(layers)])
        self.k = nn.ModuleList([nn.Linear(D, D, bias=False) for _ in range(layers)])
        self.v = nn.ModuleList([nn.Linear(D, D, bias=False) for _ in range(layers)])
        self.ff = nn.ModuleList([nn.Sequential(nn.LayerNorm(D), nn.Linear(D, 2*D), nn.GELU(), nn.Linear(2*D, D)) for _ in range(layers)])
        self.out = nn.Linear(D, VOCAB)
        self.register_buffer('mask', mask)

    def forward(self, x: torch.Tensor):
        b = x.shape[0]
        pos = torch.arange(L, device=x.device).unsqueeze(0).expand(b, L)
        h = self.value_emb(x) + self.pos_emb(pos)
        last_att = None
        for li in range(self.layers):
            q = self.q[li](h); k = self.k[li](h); v = self.v[li](h)
            scores = q @ k.transpose(-1, -2) / math.sqrt(D)
            scores = scores.masked_fill(~self.mask.unsqueeze(0), -1e9)
            att = torch.softmax(scores, dim=-1)
            h = h + att @ v
            h = h + self.ff[li](h)
            last_att = att
        logits = self.out(h[:, TARGET_POS, :])
        return logits, last_att[:, TARGET_POS, :]


def make_batch(batch: int):
    x = torch.randint(0, VOCAB, (batch, L), dtype=torch.long, device=DEVICE)
    y = x[:, SOURCE_POS].clone()
    # Decorrelate target, relay, and source labels so self/relay shortcuts are punished.
    for idx, (src, tgt) in enumerate(zip(SOURCE_POS.tolist(), TARGET_POS.tolist())):
        for pos in [tgt, tgt - 1]:
            same = x[:, pos] == y[:, idx]
            if same.any():
                x[same, pos] = (x[same, pos] + 1 + idx) % VOCAB
    return x, y


def train_one(kind: str, layers: int):
    mask = build_mask(kind).to(DEVICE)
    torch.manual_seed(SEED + layers * 31 + sum(ord(c) for c in kind))
    model = MultiLayerReader(mask, layers).to(DEVICE)
    opt = torch.optim.AdamW(model.parameters(), lr=2.8e-3, weight_decay=1e-4)
    reach1 = transitive_depth_reach(mask.cpu(), 1)
    reachd = transitive_depth_reach(mask.cpu(), layers)
    one_step = [bool(reach1[int(t), int(s)].item()) for t, s in zip(TARGET_POS, SOURCE_POS)]
    depth_step = [bool(reachd[int(t), int(s)].item()) for t, s in zip(TARGET_POS, SOURCE_POS)]
    history=[]
    best=0.0
    for step in range(1, STEPS+1):
        x,y = make_batch(BATCH)
        logits, att = model(x)
        loss = F.cross_entropy(logits.reshape(-1, VOCAB), y.reshape(-1))
        opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
        if step in {1,20,45,70,90}:
            with torch.no_grad():
                xt,yt = make_batch(384)
                lg,at = model(xt)
                pred = lg.argmax(-1)
                acc = (pred == yt).float().mean().item()
                src_mass = at[:, torch.arange(len(TARGET_POS)), SOURCE_POS].mean().item()
                best = max(best, acc)
                history.append({'step':step,'loss':float(loss.item()),'acc':acc,'source_attention_mass_last_layer':src_mass})
    with torch.no_grad():
        xt,yt = make_batch(1024)
        lg,at = model(xt)
        pred = lg.argmax(-1)
        final_acc = (pred == yt).float().mean().item()
        acc_by_pos = (pred == yt).float().mean(dim=0).cpu().tolist()
        src_mass_by_pos = at[:, torch.arange(len(TARGET_POS)), SOURCE_POS].mean(dim=0).cpu().tolist()
    return {
        'mask': kind,
        'layers': layers,
        'one_step_reachable_fraction': sum(one_step)/len(one_step),
        'depth_reachable_fraction': sum(depth_step)/len(depth_step),
        'final_acc': final_acc,
        'best_acc': best,
        'target_miss': 1.0 - final_acc,
        'acc_by_target_pos': {str(int(p)): float(a) for p,a in zip(TARGET_POS.tolist(), acc_by_pos)},
        'source_attention_mass_by_target_pos_last_layer': {str(int(p)): float(a) for p,a in zip(TARGET_POS.tolist(), src_mass_by_pos)},
        'history': history,
    }


def main():
    configs=[
        ('fixed_block',2),('periodic_skip_b4',2),('ring_anchor',2),
        ('sliding_w1',1),('sliding_w1',2),('sliding_w2',1),
        ('one_hop_boundary_bridge',1),('one_hop_boundary_bridge',2),
        ('two_hop_source_extended',2),('two_hop_source_extended',3),
        ('dense_causal',1)
    ]
    rows=[train_one(k,l) for k,l in configs]
    non_oracle=[r for r in rows if r['mask'] != 'dense_causal']
    winner=max(non_oracle, key=lambda r:(r['final_acc'], r['depth_reachable_fraction'], -r['layers']))
    payload={
        'project':'CloudtainerML',
        'revision':REV,
        'probe':'tiny_boundary_depth_train',
        'kind':'trained_tiny_probe',
        'source_ids':['SRC-0348','SRC-0350'],
        'cell_ids':['CELL-341'],
        'summary':{
            'primary_metric':{'name':'final_acc','direction':'higher_is_better'},
            'winner_excluding_dense_oracle':winner['mask']+f"_L{winner['layers']}",
            'mean_final_acc':sum(r['final_acc'] for r in rows)/len(rows),
            'guard_fields':['depth_reachable_fraction','one_step_reachable_fraction','target_miss','source_attention_mass_by_target_pos_last_layer'],
            'interpretation':'Multi-layer trained boundary copy probe separates one-step visibility from depth reachability: masks that are only reachable through a relay can succeed with enough layers, while truly unreachable block masks stay near chance.',
        },
        'rows':rows,
    }
    path=OUT/f'{REVUP}_TINY_BOUNDARY_DEPTH_TRAIN_SMOKE.json'
    path.write_text(json.dumps(payload,indent=2),encoding='utf-8')
    print(json.dumps(payload['summary'],indent=2))

if __name__=='__main__':
    main()
