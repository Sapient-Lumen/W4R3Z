#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from dataclasses import asdict, dataclass
from pathlib import Path
import numpy as np

@dataclass
class Row:
    seed:int; n_tokens:int; dim:int; block_size:int; scenario:str; eps:float; method:str
    blocks_read:int; read_fraction:float; cosine_to_full:float; mse_to_full:float; stopped:int

def norm(x, eps=1e-8): return x/(np.linalg.norm(x)+eps)
def softmax(x):
    y=x-np.max(x); e=np.exp(y); return e/np.sum(e)

def make_case(rng,n,d,scenario):
    q=norm(rng.normal(size=d)); k=rng.normal(size=(n,d)); v=rng.normal(size=(n,d))*0.4
    if scenario=='front_loaded':
        hot=rng.choice(np.arange(0,n//4),size=12,replace=False); k[hot]+=5*q; v[hot]+=rng.normal(size=d)
    elif scenario=='tail_surprise':
        hot=rng.choice(np.arange(3*n//4,n),size=12,replace=False); k[hot]+=5*q; v[hot]+=2*norm(rng.normal(size=d))
    elif scenario=='diffuse':
        k+=0.8*q; v+=0.1*rng.normal(size=(n,d))
    elif scenario=='late_direction_flip':
        early=rng.choice(np.arange(0,n//3),size=10,replace=False); late=rng.choice(np.arange(2*n//3,n),size=10,replace=False)
        dir1=norm(rng.normal(size=d)); k[early]+=4*q; v[early]+=2*dir1; k[late]+=3.7*q; v[late]+=-2*dir1
    else: raise ValueError(scenario)
    return q,k,v

def full_attention(q,k,v):
    w=softmax(k@q); return w@v,w

def order_blocks(w,block,method):
    blocks=[np.arange(i,min(i+block,len(w))) for i in range(0,len(w),block)]
    if method=='sequential': return blocks
    if method=='recency_first': return list(reversed(blocks))
    if method=='attention_mass_desc': return sorted(blocks,key=lambda b:float(np.sum(w[b])),reverse=True)
    raise ValueError(method)

def art_run(q,k,v,full,w,block,eps,method):
    logits=k@q; shift=np.max(logits); denom=0.0; s=np.zeros(v.shape[1]); prev=None; read=0; stopped=0; out=np.zeros(v.shape[1])
    for b in order_blocks(w,block,method):
        e=np.exp(logits[b]-shift); denom+=float(np.sum(e)); s+=e@v[b]; out=s/max(denom,1e-12); read+=1
        if prev is not None:
            dmag=np.linalg.norm(out-prev)/(np.linalg.norm(prev)+1e-8); ddir=1-float(np.dot(norm(out),norm(prev)))
            if dmag<eps and ddir<eps: stopped=1; break
        prev=out.copy()
    return float(np.dot(norm(out),norm(full))), float(np.mean((out-full)**2)), read, stopped

def run(seed,n,d,block,scenario,eps,method):
    rng=np.random.default_rng(seed); q,k,v=make_case(rng,n,d,scenario); full,w=full_attention(q,k,v); cos,mse,read,stopped=art_run(q,k,v,full,w,block,eps,method)
    return Row(seed,n,d,block,scenario,eps,method,read,read/(n/block),cos,mse,stopped)

def summarize(rows):
    out={'rows':len(rows),'scenarios':{}}
    for s in sorted({r.scenario for r in rows}):
        out['scenarios'][s]={}
        for m in sorted({r.method for r in rows}):
            xs=[r for r in rows if r.scenario==s and r.method==m]
            out['scenarios'][s][m]={
                'read_fraction_mean':float(np.mean([r.read_fraction for r in xs])),
                'cosine_mean':float(np.mean([r.cosine_to_full for r in xs])),
                'mse_mean':float(np.mean([r.mse_to_full for r in xs])),
                'stop_rate':float(np.mean([r.stopped for r in xs]))}
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,default=Path('artifacts/probe-results/REV0006_ART_RUNTIME_TERMINATION_SMOKE')); ap.add_argument('--seeds',type=int,default=32); args=ap.parse_args()
    rows=[]
    for seed in range(args.seeds):
      for scenario in ['front_loaded','tail_surprise','diffuse','late_direction_flip']:
       for eps in [0.002,0.01,0.05]:
        for method in ['sequential','recency_first','attention_mass_desc']:
         rows.append(run(seed,384,48,16,scenario,eps,method))
    args.out.parent.mkdir(parents=True,exist_ok=True); csv_path=args.out.with_suffix('.csv'); json_path=args.out.with_suffix('.json')
    with csv_path.open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=list(asdict(rows[0]).keys())); wr.writeheader(); [wr.writerow(asdict(r)) for r in rows]
    sm=summarize(rows); sm.update({'probe':'attention_runtime_termination','csv':str(csv_path),'interpretation':'Early termination works when contribution order exposes important blocks before stabilization; late direction flips are the trap.'}); json_path.write_text(json.dumps(sm,indent=2),encoding='utf-8'); print(json.dumps(sm,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
