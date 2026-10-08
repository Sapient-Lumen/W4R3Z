#!/usr/bin/env python3
"""CloudtainerML rev0034 — tiny trained routing-absorption probe.

A small PyTorch lookup/copy task. This is not a paper reproduction.
It tests whether a learned sparse gate trained jointly with attention survives
hard top-k deployment, and whether a posthoc gate trained on a frozen dense
attention geometry can be more reliable than an end-to-end soft gate.
"""
from __future__ import annotations
import argparse, json, math, random, time
from pathlib import Path
from typing import Dict, List

import torch
torch.set_num_threads(1)
import torch.nn as nn
import torch.nn.functional as F

REV = "rev0034"
REVUP = "REV0034"

class LookupData:
    def __init__(self, n_keys=12, ctx_len=10, device="cpu", duplicate_prob=0.0, noise_values=False):
        self.n_keys=n_keys; self.ctx_len=ctx_len; self.device=device; self.duplicate_prob=duplicate_prob; self.noise_values=noise_values
        self.dim=2*n_keys+2
    def batch(self, bs:int):
        n=self.n_keys; L=self.ctx_len; D=self.dim; dev=self.device
        x=torch.zeros(bs,L+1,D,device=dev)
        keys=torch.randint(0,n,(bs,L),device=dev)
        vals=torch.randint(0,n,(bs,L),device=dev)
        tp=torch.randint(0,L,(bs,),device=dev)
        if self.duplicate_prob>0:
            dup_mask=torch.rand(bs,device=dev)<self.duplicate_prob
            dup_pos=torch.randint(0,L,(bs,),device=dev)
            bidx=torch.arange(bs,device=dev)
            keys[bidx[dup_mask],dup_pos[dup_mask]]=keys[bidx[dup_mask],tp[dup_mask]]
            vals[bidx[dup_mask],dup_pos[dup_mask]]=vals[bidx[dup_mask],tp[dup_mask]]
        b=torch.arange(bs,device=dev).unsqueeze(1).expand(bs,L)
        pos=torch.arange(L,device=dev).unsqueeze(0).expand(bs,L)
        x[b,pos,keys]=1.0
        x[b,pos,n+vals]=1.0
        x[:,:L,2*n]=1.0
        qkey=keys[torch.arange(bs,device=dev),tp]
        labels=vals[torch.arange(bs,device=dev),tp]
        x[torch.arange(bs,device=dev),L,qkey]=1.0
        x[:,L,2*n+1]=1.0
        return x,labels,tp

class AttentionLookup(nn.Module):
    def __init__(self, dim:int, n_keys:int, d_model=48, gated=False, k_select=3):
        super().__init__(); self.n_keys=n_keys; self.gated=gated; self.k_select=k_select
        self.wq=nn.Linear(dim,d_model,bias=False); self.wk=nn.Linear(dim,d_model,bias=False); self.wv=nn.Linear(dim,d_model,bias=False)
        self.out=nn.Linear(d_model,n_keys)
        # Gate can see context key, query key, their elementwise product, and context value.
        gate_in=4*n_keys+1
        self.gate=nn.Sequential(nn.Linear(gate_in,64),nn.Tanh(),nn.Linear(64,1))
    def gate_logits(self,x):
        n=self.n_keys; ctx=x[:,:-1,:]; q=x[:,-1:,:]
        ck=ctx[:,:,:n]; qk=q[:,:,:n].expand_as(ck); prod=ck*qk; cv=ctx[:,:,n:2*n]
        pos=torch.linspace(0,1,ctx.shape[1],device=x.device).view(1,-1,1).expand(ctx.shape[0],-1,1)
        return self.gate(torch.cat([ck,qk,prod,cv,pos],dim=-1)).squeeze(-1)
    def forward(self,x, mode="dense", hard=False, random_mask=False, target_pos=None):
        ctx=x[:,:-1,:]; qtok=x[:,-1:,:]
        q=self.wq(qtok); k=self.wk(ctx); v=self.wv(ctx)
        scores=(q*k).sum(-1)/math.sqrt(k.shape[-1])
        gate_logits=None; keep_mask=None
        if random_mask:
            B,L=scores.shape; keep_mask=torch.zeros_like(scores,dtype=torch.bool)
            for b in range(B): keep_mask[b,torch.randperm(L,device=x.device)[:self.k_select]]=True
            scores=scores.masked_fill(~keep_mask,-1e4)
        elif mode=="oracle" and target_pos is not None:
            B,L=scores.shape; keep_mask=torch.zeros_like(scores,dtype=torch.bool); keep_mask[torch.arange(B,device=x.device),target_pos]=True
            scores=scores.masked_fill(~keep_mask,-1e4)
        elif self.gated and mode in {"soft_gate","hard_gate"}:
            gate_logits=self.gate_logits(x)
            if hard or mode=="hard_gate":
                top=torch.topk(gate_logits,k=min(self.k_select,gate_logits.shape[1]),dim=1).indices
                keep_mask=torch.zeros_like(scores,dtype=torch.bool); keep_mask.scatter_(1,top,True)
                scores=scores.masked_fill(~keep_mask,-1e4)
            else:
                # Soft deployment during training: this is where co-adaptation can hide hard-mask fragility.
                g=torch.sigmoid(gate_logits)
                scores=scores+torch.log(g+1e-4)
        att=F.softmax(scores,dim=-1)
        y=(att.unsqueeze(-1)*v).sum(1)
        logits=self.out(y)
        aux={"att":att,"gate_logits":gate_logits,"keep_mask":keep_mask}
        return logits, aux

def train_dense(data, steps=140, bs=128, lr=3e-3):
    m=AttentionLookup(data.dim,data.n_keys,gated=False).to(data.device); opt=torch.optim.AdamW(m.parameters(),lr=lr,weight_decay=1e-4)
    for _ in range(steps):
        x,y,tp=data.batch(bs); logits,_=m(x); loss=F.cross_entropy(logits,y)
        opt.zero_grad(); loss.backward(); opt.step()
    return m

def train_gated(data, steps=160, bs=128, lr=3e-3, init_from=None, freeze_base=False):
    m=AttentionLookup(data.dim,data.n_keys,gated=True).to(data.device)
    if init_from is not None:
        m.wq.load_state_dict(init_from.wq.state_dict()); m.wk.load_state_dict(init_from.wk.state_dict()); m.wv.load_state_dict(init_from.wv.state_dict()); m.out.load_state_dict(init_from.out.state_dict())
    if freeze_base:
        for module in [m.wq,m.wk,m.wv,m.out]:
            for p in module.parameters(): p.requires_grad=False
    opt=torch.optim.AdamW([p for p in m.parameters() if p.requires_grad],lr=lr,weight_decay=1e-4)
    for _ in range(steps):
        x,y,tp=data.batch(bs); logits,aux=m(x,mode="soft_gate")
        loss=F.cross_entropy(logits,y)
        if aux.get("gate_logits") is not None:
            # tiny budget pressure: discourage always-open soft masks.
            loss=loss+0.012*torch.sigmoid(aux["gate_logits"]).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return m

@torch.no_grad()
def evaluate(model,data,mode="dense",bs=384,batches=3,random_mask=False,hard=False):
    total=0; correct=0; target_kept=0; gate_entropy=[]; losses=[]
    for _ in range(batches):
        x,y,tp=data.batch(bs); logits,aux=model(x,mode=mode,hard=hard,random_mask=random_mask,target_pos=tp)
        losses.append(F.cross_entropy(logits,y).item())
        pred=logits.argmax(-1); correct+=(pred==y).sum().item(); total+=bs
        km=aux.get("keep_mask")
        if km is not None:
            target_kept+=km[torch.arange(bs,device=x.device),tp].float().sum().item()
        else:
            target_kept+=bs
        gl=aux.get("gate_logits")
        if gl is not None:
            p=torch.sigmoid(gl); ent=-(p*torch.log(p+1e-6)+(1-p)*torch.log(1-p+1e-6)).mean().item(); gate_entropy.append(ent)
    return {"acc":correct/total,"loss":sum(losses)/len(losses),"target_keep":target_kept/total,"gate_entropy":(sum(gate_entropy)/len(gate_entropy) if gate_entropy else None)}

def run_regime(name, duplicate_prob, seed):
    random.seed(seed); torch.manual_seed(seed)
    data=LookupData(duplicate_prob=duplicate_prob)
    dense=train_dense(data)
    gate_e2e=train_gated(data)
    posthoc=train_gated(data,init_from=dense,freeze_base=True,steps=170,lr=3e-3)
    rows=[]
    def add(method, model, mode="dense", hard=False, random_mask=False, oracle=False):
        ev=evaluate(model,data,mode=("oracle" if oracle else mode),hard=hard,random_mask=random_mask)
        target_miss=1-ev["target_keep"]
        # Simple scalar score: accuracy first, then loss/cost/proxy deployment risk.
        cost={"dense_full":1.0,"oracle_sparse":0.26,"random_sparse":0.26,"learned_gate_soft_train":0.42,"learned_gate_hard_deploy":0.30,"posthoc_gate_hard":0.30}.get(method,0.5)
        deploy_gap=0.0
        row={"regime":name,"method":method,"acc":ev["acc"],"loss":ev["loss"],"target_keep":ev["target_keep"],"target_miss":target_miss,"gate_entropy":ev["gate_entropy"],"cost":cost,"deployment_gap":deploy_gap,"score":(1-ev["acc"])+0.07*cost+0.18*target_miss}
        rows.append(row)
    add("dense_full",dense)
    add("oracle_sparse",dense,oracle=True)
    add("random_sparse",dense,random_mask=True)
    add("learned_gate_soft_train",gate_e2e,mode="soft_gate",hard=False)
    add("learned_gate_hard_deploy",gate_e2e,mode="hard_gate",hard=True)
    add("posthoc_gate_hard",posthoc,mode="hard_gate",hard=True)
    # Fill deployment gap from soft to hard for the e2e model.
    soft=[r for r in rows if r["method"]=="learned_gate_soft_train"][0]
    hardr=[r for r in rows if r["method"]=="learned_gate_hard_deploy"][0]
    hardr["deployment_gap"]=max(0.0,soft["acc"]-hardr["acc"])
    hardr["score"] += 0.22*hardr["deployment_gap"]
    return rows

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",default=f"artifacts/probe-results/{REVUP}_TINY_ROUTING_ABSORPTION_TRAIN_SMOKE.json"); ap.add_argument("--quick",action="store_true")
    args=ap.parse_args(); t0=time.time()
    regimes=[("unique_key_lookup",0.0,3401),("redundant_key_lookup",0.45,3402),("high_redundancy_lookup",0.80,3403)]
    rows=[]
    for r in regimes: rows.extend(run_regime(*r))
    # Winners by score, ignoring oracle for nonoracle.
    winners: Dict[str,int]={}; nonoracle: Dict[str,int]={}
    for reg,_,_ in regimes:
        cand=[r for r in rows if r["regime"]==reg]
        best=min(cand,key=lambda x:x["score"]); winners[best["method"]]=winners.get(best["method"],0)+1
        non=[r for r in cand if r["method"]!="oracle_sparse"]
        nb=min(non,key=lambda x:x["score"]); nonoracle[nb["method"]]=nonoracle.get(nb["method"],0)+1
    agg=[]
    for m in sorted({r["method"] for r in rows}):
        rs=[r for r in rows if r["method"]==m]
        agg.append({"method":m,"mean_acc":sum(r["acc"] for r in rs)/len(rs),"mean_target_keep":sum(r["target_keep"] for r in rs)/len(rs),"mean_score":sum(r["score"] for r in rs)/len(rs)})
    payload={
        "project":"CloudtainerML","revision":REV,"probe":"tiny_routing_absorption_train","kind":"trained_tiny_probe",
        "summary":{
            "row_count":len(rows),"seconds":round(time.time()-t0,3),
            "primary_metric":{"name":"score","direction":"lower_is_better","winner_field":"method"},
            "winner_counts":winners,"nonoracle_winner_counts":nonoracle,
            "aggregate":agg,
            "guard_fields":["deployment_gap","target_miss","target_keep","gate_entropy","cost","score"],
            "interpretation":"Tiny trained lookup/copy probe: compare end-to-end soft sparse gates against hard deployment and posthoc gates on frozen dense geometry. Positive evidence requires hard-gate accuracy, not soft training accuracy."
        },"rows":rows}
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps(payload["summary"],indent=2))
if __name__=="__main__": main()
