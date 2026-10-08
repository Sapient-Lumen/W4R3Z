#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, math
from pathlib import Path
from dataclasses import dataclass, asdict
import numpy as np


def softmax(x: np.ndarray) -> np.ndarray:
    z = x - np.max(x)
    e = np.exp(z)
    return e / (np.sum(e) + 1e-12)


def normed_error(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a-b) / (np.linalg.norm(a) + 1e-9))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a,b) / ((np.linalg.norm(a)+1e-9)*(np.linalg.norm(b)+1e-9)))


def make_case(rng: np.random.Generator, n: int, d: int, gap_strength: float, evicted_frac: float):
    # Query points strongly at common direction e0. Kept-looking tokens cluster near e0.
    q = np.zeros(d); q[0] = 1.0; q += 0.05*rng.normal(size=d); q /= np.linalg.norm(q)
    n_hidden = max(4, int(n*evicted_frac))
    n_main = n - n_hidden
    K_main = rng.normal(scale=0.25, size=(n_main,d)); K_main[:,0] += 2.2
    V_main = rng.normal(scale=0.25, size=(n_main,d)); V_main[:,0] += 1.0
    # Hidden/directional-gap tokens have lower key score but values in a distinct direction e1.
    K_hidden = rng.normal(scale=0.25, size=(n_hidden,d)); K_hidden[:,0] += 1.0
    V_hidden = rng.normal(scale=0.25, size=(n_hidden,d)); V_hidden[:,1] += gap_strength
    K = np.vstack([K_main,K_hidden]); V = np.vstack([V_main,V_hidden])
    perm = rng.permutation(n)
    return q, K[perm], V[perm]


def full_output(q,K,V):
    logits = K @ q / math.sqrt(K.shape[1])
    a = softmax(logits)
    return a @ V, a, logits


def topk_indices(scores, budget):
    return np.argsort(scores)[-budget:]


def approx_kept_only(q,K,V,keep):
    Ko,Vo=K[keep],V[keep]
    return full_output(q,Ko,Vo)[0]


def approx_keep_plus_mean(q,K,V,keep):
    n=K.shape[0]; d=K.shape[1]
    out_full, a, logits = full_output(q,K,V)
    keep_mask=np.zeros(n,dtype=bool); keep_mask[keep]=True
    kept=keep_mask; ev=~keep_mask
    # compute kept exact numerator/denom, evicted as count * exp(q mean_k) * mean_v
    denom=0.0; numer=np.zeros(d)
    if kept.any():
        lk=logits[kept]; wk=np.exp(lk - np.max(logits))
        denom += np.sum(wk); numer += wk @ V[kept]
    if ev.any():
        mu_k=K[ev].mean(axis=0); mu_v=V[ev].mean(axis=0)
        w=np.exp((mu_k @ q / math.sqrt(d)) - np.max(logits)) * ev.sum()
        denom += w; numer += w * mu_v
    return numer/(denom+1e-12)


def approx_keep_plus_first_order(q,K,V,keep):
    n=K.shape[0]; d=K.shape[1]
    _, _, logits = full_output(q,K,V)
    keep_mask=np.zeros(n,dtype=bool); keep_mask[keep]=True
    kept=keep_mask; ev=~keep_mask
    denom=0.0; numer=np.zeros(d)
    shift=np.max(logits)
    if kept.any():
        wk=np.exp(logits[kept]-shift)
        denom += np.sum(wk); numer += wk @ V[kept]
    if ev.any():
        Ke=K[ev]; Ve=V[ev]
        mu_k=Ke.mean(axis=0); mu_v=Ve.mean(axis=0)
        centered_k=Ke-mu_k; centered_v=Ve-mu_v
        # Cov[v,k] @ q approximates how value direction changes with query-aligned key displacement.
        cov_vk = centered_v.T @ centered_k / max(1, ev.sum()-1)
        alpha = q / math.sqrt(d)
        corrected_v = mu_v + cov_vk @ alpha
        w=np.exp((mu_k @ alpha)-shift) * ev.sum()
        denom += w; numer += w * corrected_v
    return numer/(denom+1e-12)


def run(seed:int, n:int, d:int, budgets:list[int], trials:int, gap_strengths:list[float]):
    rng=np.random.default_rng(seed)
    rows=[]
    for gap in gap_strengths:
      for budget in budgets:
        for t in range(trials):
            q,K,V=make_case(rng,n,d,gap,evicted_frac=0.30)
            full,a,logits=full_output(q,K,V)
            policies={
                'top_attention_kept_only': topk_indices(a,budget),
                'top_attention_plus_mean_moment': topk_indices(a,budget),
                'top_attention_plus_first_order_moment': topk_indices(a,budget),
                'random_kept_only': rng.choice(n,size=budget,replace=False),
                'random_plus_first_order_moment': None,
                'value_norm_kept_only': topk_indices(np.linalg.norm(V,axis=1),budget),
            }
            policies['random_plus_first_order_moment']=policies['random_kept_only']
            for name,keep in policies.items():
                if name.endswith('plus_mean_moment'):
                    pred=approx_keep_plus_mean(q,K,V,keep)
                elif name.endswith('plus_first_order_moment'):
                    pred=approx_keep_plus_first_order(q,K,V,keep)
                else:
                    pred=approx_kept_only(q,K,V,keep)
                rows.append({
                    'seed':seed,'trial':t,'n':n,'d':d,'budget':budget,'gap_strength':gap,'policy':name,
                    'normed_error':normed_error(full,pred),'cosine':cosine(full,pred),
                    'retained_attention_mass':float(a[keep].sum()),
                    'retained_value_direction_e1':float(np.mean(V[keep,1] > 0.5*gap)) if gap>0 else 0.0,
                })
    return rows


def summarize(rows):
    groups={}
    for r in rows:
        k=(r['budget'],r['gap_strength'],r['policy'])
        groups.setdefault(k,[]).append(r)
    out=[]
    for (budget,gap,policy),rs in sorted(groups.items()):
        out.append({'budget':budget,'gap_strength':gap,'policy':policy,
                    'mean_normed_error':float(np.mean([r['normed_error'] for r in rs])),
                    'mean_cosine':float(np.mean([r['cosine'] for r in rs])),
                    'mean_retained_attention_mass':float(np.mean([r['retained_attention_mass'] for r in rs])),
                    'trials':len(rs)})
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--seed',type=int,default=11)
    ap.add_argument('--n',type=int,default=128)
    ap.add_argument('--d',type=int,default=32)
    ap.add_argument('--budgets',default='8,16,32,64')
    ap.add_argument('--trials',type=int,default=40)
    ap.add_argument('--gaps',default='0.5,1.5,3.0')
    ap.add_argument('--out',default='artifacts/probe-results/REV0005_MOMENT_DIRECTIONAL_SMOKE.json')
    args=ap.parse_args()
    budgets=[int(x) for x in args.budgets.split(',') if x]
    gaps=[float(x) for x in args.gaps.split(',') if x]
    rows=run(args.seed,args.n,args.d,budgets,args.trials,gaps)
    summary=summarize(rows)
    out=Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    payload={'probe':'moment_directional_gap','note':'Synthetic first-order approximation of evicted-token moment correction; not a faithful MomentKV implementation.','args':vars(args),'summary':summary,'rows':rows}
    out.write_text(json.dumps(payload,indent=2),encoding='utf-8')
    csv_path=out.with_suffix('.csv')
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(json.dumps({'summary':summary[:12], 'row_count':len(rows)}, indent=2))

if __name__=='__main__':
    main()
