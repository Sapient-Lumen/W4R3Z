#!/usr/bin/env python3
from __future__ import annotations
import json, math, random
from pathlib import Path
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
REV = json.loads((ROOT/'CUBE-META.json').read_text()).get('revision','rev0037')
REVUP = REV.upper()
OUT = ROOT/'artifacts'/'probe-results'
OUT.mkdir(parents=True, exist_ok=True)

torch.set_num_threads(1)
SEED = 3738
random.seed(SEED)
torch.manual_seed(SEED)
DEVICE = torch.device('cpu')
L = 8
VOCAB = 11
BATCH = 256
STEPS = 140

@dataclass
class Regime:
    name: str
    source_route: float
    distractor_route: float
    source_amp: float
    distractor_amp: float
    source_importance: float
    distractor_importance: float
    noise_tokens: int = 5

REGIMES = [
    Regime('route_easy_gain_irrelevant', 1.25, 0.20, 1.00, 0.70, 1.0, 0.2),
    Regime('weak_source_value', 0.85, 0.55, 0.22, 0.90, 1.0, 0.3),
    Regime('high_gain_distractor', 0.95, 0.80, 0.55, 1.45, 1.0, 0.2),
    Regime('ambiguous_route_importance_clear', 0.72, 0.70, 0.35, 1.10, 1.0, 0.0),
    Regime('importance_misleading', 0.95, 0.80, 0.42, 1.20, 0.75, 0.65),
]

class RouteGainReadout(nn.Module):
    def __init__(self, method: str):
        super().__init__()
        self.method = method
        # route features: route_marker, normalized_position, bias
        route_in = 3 if method != 'importance_in_route' else 4
        self.route = nn.Linear(route_in, 1, bias=False)
        if method in {'gain_decoupled','route_gain_hybrid'}:
            self.gain = nn.Linear(3, 1, bias=True)  # importance, raw_amp, bias-like feature
        else:
            self.gain = None
        # Initialize route so route_marker matters at first but can be learned.
        with torch.no_grad():
            self.route.weight.zero_()
            self.route.weight[0,0] = 1.0
            if self.gain is not None:
                self.gain.weight.zero_(); self.gain.bias.fill_(0.0)
                self.gain.weight[0,0] = 0.8

    def forward(self, route_marker, pos, importance, amp, value_onehot, source_mask=None):
        bias = torch.ones_like(route_marker)
        if self.method == 'importance_in_route':
            rf = torch.stack([route_marker, pos, bias, importance], dim=-1)
        else:
            rf = torch.stack([route_marker, pos, bias], dim=-1)
        score = self.route(rf).squeeze(-1)
        att = torch.softmax(score, dim=-1)
        if self.method == 'oracle_gain':
            gain = torch.where(source_mask, torch.full_like(amp, 3.0), torch.ones_like(amp))
        elif self.gain is not None:
            gf = torch.stack([importance, amp, bias], dim=-1)
            gain = 0.15 + F.softplus(self.gain(gf).squeeze(-1))
            if self.method == 'route_gain_hybrid':
                # mild cap prevents the gain head from blindly amplifying all high-amplitude tokens
                gain = 0.15 + 2.5 * torch.sigmoid(gain)
        else:
            gain = torch.ones_like(amp)
        # Logits live in label space. Raw value amplitude is not learned away, by design.
        logits = torch.einsum('bl,bl,bl,blv->bv', att, gain, amp, value_onehot)
        return logits, att, gain


def make_batch(reg: Regime, batch: int):
    source = torch.randint(0, L-2, (batch,), device=DEVICE)
    distractor = (source + torch.randint(1, L-1, (batch,), device=DEVICE)) % (L-1)
    same = distractor == source
    if same.any(): distractor[same] = (distractor[same] + 1) % (L-1)
    y = torch.randint(0, VOCAB, (batch,), device=DEVICE)
    wrong = (y + torch.randint(1, VOCAB, (batch,), device=DEVICE)) % VOCAB
    labels = torch.randint(0, VOCAB, (batch, L), device=DEVICE)
    labels[torch.arange(batch), source] = y
    labels[torch.arange(batch), distractor] = wrong
    value_onehot = F.one_hot(labels, num_classes=VOCAB).float()
    route_marker = 0.10 * torch.randn(batch, L, device=DEVICE)
    amp = torch.full((batch, L), 0.12, device=DEVICE) + 0.04*torch.rand(batch, L, device=DEVICE)
    importance = 0.05 * torch.rand(batch, L, device=DEVICE)
    route_marker[torch.arange(batch), source] += reg.source_route
    route_marker[torch.arange(batch), distractor] += reg.distractor_route
    amp[torch.arange(batch), source] = reg.source_amp
    amp[torch.arange(batch), distractor] = reg.distractor_amp
    importance[torch.arange(batch), source] = reg.source_importance
    importance[torch.arange(batch), distractor] = reg.distractor_importance
    pos = torch.arange(L, device=DEVICE).float().unsqueeze(0).expand(batch, L) / (L-1)
    source_mask = torch.zeros(batch, L, dtype=torch.bool, device=DEVICE)
    source_mask[torch.arange(batch), source] = True
    distractor_mask = torch.zeros(batch, L, dtype=torch.bool, device=DEVICE)
    distractor_mask[torch.arange(batch), distractor] = True
    return route_marker, pos, importance, amp, value_onehot, y, source_mask, distractor_mask


def train_one(method: str, reg: Regime):
    torch.manual_seed(SEED + sum(ord(c) for c in method + reg.name))
    model = RouteGainReadout(method).to(DEVICE)
    if method == 'oracle_gain':
        params = [p for p in model.parameters() if p.requires_grad]
        opt = torch.optim.AdamW(params, lr=0.0)
    else:
        opt = torch.optim.AdamW(model.parameters(), lr=2.5e-2, weight_decay=1e-4)
    hist=[]
    for step in range(1, STEPS+1):
        batch = make_batch(reg, BATCH)
        logits, att, gain = model(*batch[:5], source_mask=batch[6])
        loss = F.cross_entropy(logits, batch[5])
        if method != 'oracle_gain':
            opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
        if step in {1, 20, 60, 100, 140}:
            with torch.no_grad():
                tb = make_batch(reg, 1024)
                lg, at, gn = model(*tb[:5], source_mask=tb[6])
                pred = lg.argmax(-1)
                acc = (pred == tb[5]).float().mean().item()
                src_mass = at[tb[6]].mean().item()
                dis_mass = at[tb[7]].mean().item()
                src_gain = gn[tb[6]].mean().item()
                dis_gain = gn[tb[7]].mean().item()
                hist.append({'step':step,'loss':float(loss.item()),'acc':acc,'source_attention_mass':src_mass,'distractor_attention_mass':dis_mass,'source_gain':src_gain,'distractor_gain':dis_gain})
    with torch.no_grad():
        tb = make_batch(reg, 4096)
        lg, at, gn = model(*tb[:5], source_mask=tb[6])
        pred = lg.argmax(-1)
        acc = (pred == tb[5]).float().mean().item()
        src_mass = at[tb[6]].mean().item(); dis_mass = at[tb[7]].mean().item()
        src_gain = gn[tb[6]].mean().item(); dis_gain = gn[tb[7]].mean().item()
        route_error = max(0.0, dis_mass - src_mass)
        gain_error = max(0.0, dis_gain - src_gain)
    return {
        'regime': reg.name,
        'method': method,
        'final_acc': acc,
        'target_miss': 1.0-acc,
        'source_attention_mass': src_mass,
        'distractor_attention_mass': dis_mass,
        'route_error': route_error,
        'source_gain': src_gain,
        'distractor_gain': dis_gain,
        'gain_error': gain_error,
        'history': hist,
    }


def main():
    methods = ['route_only','importance_in_route','gain_decoupled','route_gain_hybrid','oracle_gain']
    rows=[]
    wins={}
    for reg in REGIMES:
        rr=[train_one(m, reg) for m in methods]
        for r in rr:
            # A promotion score that punishes winning by route-only attention when gain errors remain high.
            r['promotion_score'] = r['final_acc'] - 0.10*r['route_error'] - 0.06*r['gain_error']
        non_oracle=[r for r in rr if r['method']!='oracle_gain']
        w=max(non_oracle, key=lambda r:r['promotion_score'])
        wins[w['method']]=wins.get(w['method'],0)+1
        for r in rr: r['winner_excluding_oracle']=w['method']
        rows.extend(rr)
    top=max(wins.items(), key=lambda kv: kv[1])[0]
    payload={
        'project':'CloudtainerML',
        'revision':REV,
        'probe':'tiny_route_gain_train',
        'kind':'trained_tiny_probe',
        'source_ids':['SRC-0353'],
        'cell_ids':['CELL-347'],
        'summary':{
            'primary_metric':{'name':'promotion_score','direction':'higher_is_better'},
            'top_non_oracle_winner':top,
            'winner_counts_excluding_oracle':wins,
            'guard_fields':['route_error','gain_error','source_attention_mass','distractor_attention_mass','source_gain','distractor_gain','target_miss'],
            'interpretation':'Tiny trained route/gain readout separates selection from value transmission: route features can identify evidence while a gain channel is needed in weak-source/high-distractor regimes. It is a constrained proxy, not a full Transformer layer.',
        },
        'rows':rows,
    }
    path=OUT/f'{REVUP}_TINY_ROUTE_GAIN_TRAIN_SMOKE.json'
    path.write_text(json.dumps(payload,indent=2),encoding='utf-8')
    print(json.dumps(payload['summary'],indent=2))

if __name__=='__main__':
    main()
