#!/usr/bin/env python3
from __future__ import annotations
import json, math, random
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
REV = json.loads((ROOT/'CUBE-META.json').read_text()).get('revision','rev0037')
REVUP = REV.upper()
OUT = ROOT/'artifacts'/'probe-results'
OUT.mkdir(parents=True, exist_ok=True)

torch.set_num_threads(1)
SEED = 3737
random.seed(SEED)
torch.manual_seed(SEED)
DEVICE = torch.device('cpu')

L = 16
BLOCK = 4
VOCAB = 17
D = 40
BATCH = 128
STEPS = 160
TARGET_POS = torch.tensor([5, 9, 13], dtype=torch.long, device=DEVICE)
SOURCE_POS = TARGET_POS - 2  # 3,7,11. Requires boundary token 4/8/12 to bridge to previous block end.
BOUNDARY_POS = TARGET_POS - 1


def fixed_block_mask() -> torch.Tensor:
    m = torch.zeros(L, L, dtype=torch.bool)
    for i in range(L):
        for j in range(i + 1):
            if i // BLOCK == j // BLOCK:
                m[i, j] = True
    return m


def candidate_edges():
    # Candidate repair edges are deliberately too broad: every block-boundary token may read any token
    # from the previous block. Only one edge per boundary token is actually needed for this task.
    edges = []
    true_edges = set()
    for b in range(1, L // BLOCK):
        i = b * BLOCK
        for j in range((b - 1) * BLOCK, b * BLOCK):
            edges.append((i, j))
        true_edges.add((i, i - 1))
    return edges, true_edges


CANDIDATES, TRUE_EDGES = candidate_edges()
CANDIDATE_INDEX = {e: idx for idx, e in enumerate(CANDIDATES)}
BASE_MASK = fixed_block_mask().to(DEVICE)


def transitive_reach_from_mask(mask: torch.Tensor, depth: int = 2) -> torch.Tensor:
    reach = mask.clone().cpu().float()
    total = reach.clone()
    for _ in range(1, depth):
        reach = (reach @ mask.clone().cpu().float() > 0).float()
        total = ((total + reach) > 0).float()
    return total.bool()


def make_batch(batch: int):
    x = torch.randint(0, VOCAB, (batch, L), dtype=torch.long, device=DEVICE)
    y = x[:, SOURCE_POS].clone()
    # Destroy target/relay shortcuts.
    for idx, (src, relay, tgt) in enumerate(zip(SOURCE_POS.tolist(), BOUNDARY_POS.tolist(), TARGET_POS.tolist())):
        for pos in [relay, tgt]:
            same = x[:, pos] == y[:, idx]
            if same.any():
                x[same, pos] = (x[same, pos] + 1 + idx) % VOCAB
    return x, y


class TwoLayerReader(nn.Module):
    def __init__(self, mode: str, sparsity_lambda: float = 0.0, init_bias: float = -2.0):
        super().__init__()
        self.mode = mode
        self.sparsity_lambda = sparsity_lambda
        self.value_emb = nn.Embedding(VOCAB, D)
        self.pos_emb = nn.Embedding(L, D)
        self.q = nn.ModuleList([nn.Linear(D, D, bias=False) for _ in range(2)])
        self.k = nn.ModuleList([nn.Linear(D, D, bias=False) for _ in range(2)])
        self.v = nn.ModuleList([nn.Linear(D, D, bias=False) for _ in range(2)])
        self.ff = nn.ModuleList([nn.Sequential(nn.LayerNorm(D), nn.Linear(D, D), nn.GELU(), nn.Linear(D, D)) for _ in range(2)])
        self.out = nn.Linear(D, VOCAB)
        if mode == 'learned_candidate_gate':
            self.edge_logits = nn.Parameter(torch.full((len(CANDIDATES),), init_bias))
        else:
            self.register_parameter('edge_logits', None)
        self.register_buffer('base_mask', BASE_MASK)
        cand_mask = torch.zeros(L, L, dtype=torch.bool)
        for i, j in CANDIDATES:
            cand_mask[i, j] = True
        self.register_buffer('candidate_mask', cand_mask.to(DEVICE))
        edge_id = torch.full((L, L), -1, dtype=torch.long)
        for idx, (i, j) in enumerate(CANDIDATES):
            edge_id[i, j] = idx
        self.register_buffer('edge_id', edge_id.to(DEVICE))

    def effective_gate_probs(self):
        if self.mode == 'fixed_block':
            return torch.zeros(len(CANDIDATES), device=DEVICE)
        if self.mode == 'all_candidate_edges':
            return torch.ones(len(CANDIDATES), device=DEVICE)
        return torch.sigmoid(self.edge_logits)

    def current_bool_mask(self, threshold: float = 0.5):
        m = self.base_mask.detach().clone().cpu()
        probs = self.effective_gate_probs().detach().cpu()
        for p, (i, j) in zip(probs, CANDIDATES):
            if float(p) >= threshold:
                m[i, j] = True
        return m

    def layer_attention(self, h, li: int):
        q = self.q[li](h); k = self.k[li](h); v = self.v[li](h)
        scores = q @ k.transpose(-1, -2) / math.sqrt(D)
        if self.mode == 'fixed_block':
            scores = scores.masked_fill(~self.base_mask.unsqueeze(0), -1e9)
        elif self.mode == 'all_candidate_edges':
            mask = self.base_mask | self.candidate_mask
            scores = scores.masked_fill(~mask.unsqueeze(0), -1e9)
        elif self.mode == 'learned_candidate_gate':
            mask = self.base_mask | self.candidate_mask
            scores = scores.masked_fill(~mask.unsqueeze(0), -1e9)
            # Candidate gates act as log-priors on reachability. Base edges are unpenalized.
            gate = torch.sigmoid(self.edge_logits).clamp(1e-4, 1.0)
            log_prior = torch.zeros(L, L, device=h.device)
            ids = self.edge_id
            cand_locs = ids >= 0
            log_prior[cand_locs] = torch.log(gate[ids[cand_locs]])
            scores = scores + log_prior.unsqueeze(0)
        else:
            raise ValueError(self.mode)
        att = torch.softmax(scores, dim=-1)
        return att @ v, att

    def forward(self, x: torch.Tensor):
        b = x.shape[0]
        pos = torch.arange(L, device=x.device).unsqueeze(0).expand(b, L)
        h = self.value_emb(x) + self.pos_emb(pos)
        last_att = None
        for li in range(2):
            y, att = self.layer_attention(h, li)
            h = h + y
            h = h + self.ff[li](h)
            last_att = att
        logits = self.out(h[:, TARGET_POS, :])
        penalty = torch.tensor(0.0, device=x.device)
        if self.mode == 'learned_candidate_gate':
            penalty = self.sparsity_lambda * torch.sigmoid(self.edge_logits).mean()
        return logits, last_att[:, TARGET_POS, :], penalty


def edge_metrics(model: TwoLayerReader, threshold: float = 0.5):
    probs = model.effective_gate_probs().detach().cpu().tolist()
    active = [edge for p, edge in zip(probs, CANDIDATES) if p >= threshold]
    active_set = set(active)
    tp = len(active_set & TRUE_EDGES)
    fp = len(active_set - TRUE_EDGES)
    fn = len(TRUE_EDGES - active_set)
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 2 * precision * recall / max(1e-9, precision + recall)

    ranked = [edge for _, edge in sorted(zip(probs, CANDIDATES), key=lambda pe: -pe[0])]
    topk = ranked[:len(TRUE_EDGES)]
    topk_set = set(topk)
    ktp = len(topk_set & TRUE_EDGES)
    kfp = len(topk_set - TRUE_EDGES)
    kfn = len(TRUE_EDGES - topk_set)
    topk_precision = ktp / max(1, ktp + kfp)
    topk_recall = ktp / max(1, ktp + kfn)
    topk_f1 = 2 * topk_precision * topk_recall / max(1e-9, topk_precision + topk_recall)

    m = model.current_bool_mask(threshold=threshold)
    reach = transitive_reach_from_mask(m, 2)
    reachable_flags = [bool(reach[int(t), int(s)].item()) for t, s in zip(TARGET_POS.cpu(), SOURCE_POS.cpu())]
    topk_m = BASE_MASK.detach().clone().cpu()
    for i, j in topk:
        topk_m[i, j] = True
    topk_reach = transitive_reach_from_mask(topk_m, 2)
    topk_reachable_flags = [bool(topk_reach[int(t), int(s)].item()) for t, s in zip(TARGET_POS.cpu(), SOURCE_POS.cpu())]
    true_probs = [probs[CANDIDATE_INDEX[e]] for e in sorted(TRUE_EDGES)]
    false_probs = [p for p, e in zip(probs, CANDIDATES) if e not in TRUE_EDGES]
    true_mean = sum(true_probs)/max(1,len(true_probs))
    false_mean = sum(false_probs)/max(1,len(false_probs))
    return {
        'active_edge_count': len(active),
        'true_edge_count': len(TRUE_EDGES),
        'edge_precision': precision,
        'edge_recall': recall,
        'edge_f1_threshold_0p5': f1,
        'topk_edge_precision': topk_precision,
        'topk_edge_recall': topk_recall,
        'topk_edge_f1': topk_f1,
        'true_edge_mean_prob': true_mean,
        'false_edge_mean_prob': false_mean,
        'true_false_prob_gap': true_mean - false_mean,
        'depth_reachable_fraction': sum(reachable_flags)/len(reachable_flags),
        'topk_depth_reachable_fraction': sum(topk_reachable_flags)/len(topk_reachable_flags),
        'candidate_gate_probs': {f'{i}->{j}': float(p) for p, (i,j) in zip(probs, CANDIDATES)},
        'active_edges': [f'{i}->{j}' for i,j in active],
        'topk_edges': [f'{i}->{j}' for i,j in topk],
        'true_edges': [f'{i}->{j}' for i,j in sorted(TRUE_EDGES)],
    }


def train_one(mode: str, sparsity_lambda: float = 0.0):
    torch.manual_seed(SEED + int(10000*sparsity_lambda) + sum(ord(c) for c in mode))
    model = TwoLayerReader(mode, sparsity_lambda=sparsity_lambda).to(DEVICE)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-3, weight_decay=1e-4)
    history=[]
    for step in range(1, STEPS+1):
        x, y = make_batch(BATCH)
        logits, att, penalty = model(x)
        ce = F.cross_entropy(logits.reshape(-1, VOCAB), y.reshape(-1))
        loss = ce + penalty
        opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
        if step in {1, 20, 60, 100, 160}:
            with torch.no_grad():
                xt, yt = make_batch(768)
                lg, at, _ = model(xt)
                pred = lg.argmax(-1)
                acc = (pred == yt).float().mean().item()
                src_mass = at[:, torch.arange(len(TARGET_POS), device=DEVICE), SOURCE_POS].mean().item()
                em = edge_metrics(model)
                history.append({'step': step, 'ce_loss': float(ce.item()), 'acc': acc, 'source_attention_mass_last_layer': src_mass, 'active_edge_count': em['active_edge_count'], 'topk_edge_f1': em['topk_edge_f1']})
    with torch.no_grad():
        xt, yt = make_batch(2048)
        lg, at, _ = model(xt)
        pred = lg.argmax(-1)
        final_acc = (pred == yt).float().mean().item()
        src_mass_by_pos = at[:, torch.arange(len(TARGET_POS), device=DEVICE), SOURCE_POS].mean(dim=0).cpu().tolist()
    em = edge_metrics(model)
    return {
        'method': mode if mode != 'learned_candidate_gate' else f'learned_gate_lam{str(sparsity_lambda).replace(".","p")}',
        'mode': mode,
        'sparsity_lambda': sparsity_lambda,
        'final_acc': final_acc,
        'target_miss': 1.0 - final_acc,
        'source_attention_mass_by_target_pos_last_layer': {str(int(p)): float(v) for p,v in zip(TARGET_POS.cpu().tolist(), src_mass_by_pos)},
        'history': history,
        **em,
    }


def main():
    rows = []
    rows.append(train_one('fixed_block'))
    rows.append(train_one('all_candidate_edges'))
    for lam in [0.000, 0.010, 0.030, 0.060, 0.120]:
        rows.append(train_one('learned_candidate_gate', sparsity_lambda=lam))
    # Score favors exactness first, then sparse correct edge recovery.
    for r in rows:
        r['promotion_score'] = r['final_acc'] + 0.08 * r['topk_edge_f1'] + 0.02 * r['topk_depth_reachable_fraction'] - 0.015 * max(0, r['active_edge_count'] - r['true_edge_count'])
    non_oracle = [r for r in rows if r['method'] != 'all_candidate_edges']
    winner = max(non_oracle, key=lambda r: r['promotion_score'])
    payload = {
        'project':'CloudtainerML',
        'revision':REV,
        'probe':'tiny_learned_boundary_mask',
        'kind':'trained_tiny_probe',
        'source_ids':['SRC-0348','SRC-0350'],
        'cell_ids':['CELL-346'],
        'summary':{
            'primary_metric':{'name':'promotion_score','direction':'higher_is_better'},
            'winner_excluding_all_candidate_oracle':winner['method'],
            'best_final_acc_excluding_oracle':max(r['final_acc'] for r in non_oracle),
            'best_topk_edge_f1_excluding_oracle':max(r['topk_edge_f1'] for r in non_oracle),
            'guard_fields':['edge_precision','edge_recall','edge_f1_threshold_0p5','topk_edge_f1','topk_depth_reachable_fraction','true_false_prob_gap','active_edge_count','depth_reachable_fraction','target_miss','source_attention_mass_by_target_pos_last_layer'],
            'interpretation':'Tiny trained repair-mask probe asks whether boundary bridges can be discovered from an overcomplete candidate set under sparsity pressure. Success requires both exact copy accuracy and recovery of the minimal relay edges, not merely dense candidate access.',
        },
        'rows': rows,
    }
    path = OUT/f'{REVUP}_TINY_LEARNED_BOUNDARY_MASK_SMOKE.json'
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(json.dumps(payload['summary'], indent=2))

if __name__ == '__main__':
    main()
