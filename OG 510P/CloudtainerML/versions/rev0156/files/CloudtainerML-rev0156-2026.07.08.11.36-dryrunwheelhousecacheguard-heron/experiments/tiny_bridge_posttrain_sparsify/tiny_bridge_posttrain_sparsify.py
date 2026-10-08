#!/usr/bin/env python3
from __future__ import annotations
import json, math, random, copy
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
REV = json.loads((ROOT/'CUBE-META.json').read_text()).get('revision','rev0038')
REVUP = REV.upper()
OUT = ROOT/'artifacts'/'probe-results'
OUT.mkdir(parents=True, exist_ok=True)

torch.set_num_threads(1)
SEED = 3838
random.seed(SEED)
torch.manual_seed(SEED)
DEVICE = torch.device('cpu')

L=16; BLOCK=4; VOCAB=17; D=40; BATCH=96
DENSE_STEPS=120; GATE_STEPS=110; HARD_FT_STEPS=45
TARGET_POS=torch.tensor([5,9,13],dtype=torch.long,device=DEVICE)
SOURCE_POS=TARGET_POS-2
BOUNDARY_POS=TARGET_POS-1

def fixed_block_mask() -> torch.Tensor:
    m=torch.zeros(L,L,dtype=torch.bool)
    for i in range(L):
        for j in range(i+1):
            if i//BLOCK == j//BLOCK: m[i,j]=True
    return m

def candidate_edges():
    edges=[]; true=set()
    for b in range(1,L//BLOCK):
        i=b*BLOCK
        for j in range((b-1)*BLOCK,b*BLOCK): edges.append((i,j))
        true.add((i,i-1))
    return edges,true

CANDIDATES, TRUE_EDGES = candidate_edges()
EDGE_TO_ID={e:i for i,e in enumerate(CANDIDATES)}
BASE_MASK=fixed_block_mask().to(DEVICE)
CAND_MASK=torch.zeros(L,L,dtype=torch.bool,device=DEVICE)
EDGE_ID=torch.full((L,L),-1,dtype=torch.long,device=DEVICE)
for idx,(i,j) in enumerate(CANDIDATES):
    CAND_MASK[i,j]=True; EDGE_ID[i,j]=idx

def make_batch(batch:int):
    x=torch.randint(0,VOCAB,(batch,L),dtype=torch.long,device=DEVICE)
    y=x[:,SOURCE_POS].clone()
    for idx,(src,relay,tgt) in enumerate(zip(SOURCE_POS.tolist(),BOUNDARY_POS.tolist(),TARGET_POS.tolist())):
        for pos in [relay,tgt]:
            same=x[:,pos]==y[:,idx]
            if same.any(): x[same,pos]=(x[same,pos]+1+idx)%VOCAB
    return x,y

def transitive_reach(mask: torch.Tensor, depth:int=2) -> torch.Tensor:
    m=mask.cpu().float(); r=m.clone(); total=r.clone()
    for _ in range(1,depth):
        r=(r@m>0).float(); total=((total+r)>0).float()
    return total.bool()

class BoundaryReader(nn.Module):
    def __init__(self, use_gate: bool=False, init_gate: float=2.0):
        super().__init__()
        self.use_gate=use_gate
        self.value_emb=nn.Embedding(VOCAB,D)
        self.pos_emb=nn.Embedding(L,D)
        self.q=nn.ModuleList([nn.Linear(D,D,bias=False) for _ in range(2)])
        self.k=nn.ModuleList([nn.Linear(D,D,bias=False) for _ in range(2)])
        self.v=nn.ModuleList([nn.Linear(D,D,bias=False) for _ in range(2)])
        self.ff=nn.ModuleList([nn.Sequential(nn.LayerNorm(D),nn.Linear(D,D),nn.GELU(),nn.Linear(D,D)) for _ in range(2)])
        self.out=nn.Linear(D,VOCAB)
        if use_gate: self.edge_logits=nn.Parameter(torch.full((len(CANDIDATES),), init_gate))
        else: self.register_parameter('edge_logits', None)
        self.register_buffer('base_mask', BASE_MASK)
        self.register_buffer('cand_mask', CAND_MASK)
        self.register_buffer('edge_id', EDGE_ID)
    def gate_probs(self):
        if self.edge_logits is None: return torch.ones(len(CANDIDATES),device=DEVICE)
        return torch.sigmoid(self.edge_logits)
    def set_core_requires_grad(self, flag: bool):
        for name,p in self.named_parameters():
            if name != 'edge_logits': p.requires_grad_(flag)
        if self.edge_logits is not None: self.edge_logits.requires_grad_(True)
    def mask_from_edges(self, edges: list[tuple[int,int]]|None=None, threshold: float|None=None):
        m=BASE_MASK.detach().clone()
        if edges is not None:
            for i,j in edges: m[i,j]=True
            return m
        if threshold is None:
            return self.base_mask | self.cand_mask
        probs=self.gate_probs().detach()
        for p,(i,j) in zip(probs,CANDIDATES):
            if float(p)>=threshold: m[i,j]=True
        return m
    def forward(self,x:torch.Tensor, mode:str='dense_candidate', hard_edges:list[tuple[int,int]]|None=None, threshold:float|None=None):
        b=x.shape[0]; pos=torch.arange(L,device=x.device).unsqueeze(0).expand(b,L)
        h=self.value_emb(x)+self.pos_emb(pos)
        last_att=None
        for li in range(2):
            q=self.q[li](h); k=self.k[li](h); v=self.v[li](h)
            scores=q@k.transpose(-1,-2)/math.sqrt(D)
            if mode=='fixed_block':
                mask=self.base_mask
                scores=scores.masked_fill(~mask.unsqueeze(0),-1e9)
            elif mode=='dense_candidate':
                mask=self.base_mask|self.cand_mask
                scores=scores.masked_fill(~mask.unsqueeze(0),-1e9)
            elif mode=='soft_gate':
                mask=self.base_mask|self.cand_mask
                scores=scores.masked_fill(~mask.unsqueeze(0),-1e9)
                gate=self.gate_probs().clamp(1e-5,1.0)
                log_prior=torch.zeros(L,L,device=x.device)
                loc=self.edge_id>=0
                log_prior[loc]=torch.log(gate[self.edge_id[loc]])
                scores=scores+log_prior.unsqueeze(0)
            elif mode in {'hard_edges','threshold_gate'}:
                if mode=='hard_edges': mask=self.mask_from_edges(edges=hard_edges)
                else: mask=self.mask_from_edges(threshold=threshold)
                scores=scores.masked_fill(~mask.unsqueeze(0),-1e9)
            else:
                raise ValueError(mode)
            att=torch.softmax(scores,dim=-1)
            h=h+att@v; h=h+self.ff[li](h); last_att=att
        return self.out(h[:,TARGET_POS,:]), last_att[:,TARGET_POS,:]

def eval_model(model: BoundaryReader, mode:str, hard_edges=None, threshold=None, batch:int=2048):
    model.eval()
    with torch.no_grad():
        x,y=make_batch(batch)
        logits,att=model(x,mode=mode,hard_edges=hard_edges,threshold=threshold)
        pred=logits.argmax(-1); acc=(pred==y).float().mean().item()
        src_mass=att[:,torch.arange(len(TARGET_POS),device=DEVICE),SOURCE_POS].mean(dim=0).cpu().tolist()
    if hard_edges is not None:
        mask=model.mask_from_edges(edges=hard_edges).cpu()
    elif mode=='threshold_gate':
        mask=model.mask_from_edges(threshold=threshold).cpu()
    elif mode=='fixed_block':
        mask=BASE_MASK.cpu()
    else:
        mask=(BASE_MASK|CAND_MASK).cpu()
    reach=transitive_reach(mask,2)
    reachable=sum(bool(reach[int(t),int(s)]) for t,s in zip(TARGET_POS.cpu(),SOURCE_POS.cpu()))/len(TARGET_POS)
    return acc, 1.0-acc, reachable, {str(int(p)):float(v) for p,v in zip(TARGET_POS.cpu().tolist(),src_mass)}

def edge_metrics_from_probs(probs):
    probs=[float(p) for p in probs]
    ranked=[e for _,e in sorted(zip(probs,CANDIDATES),key=lambda pe:-pe[0])]
    topk=ranked[:len(TRUE_EDGES)]
    for threshold in [0.5,0.2,0.05]:
        active=[e for p,e in zip(probs,CANDIDATES) if p>=threshold]
        if threshold==0.5: active05=active
        if threshold==0.2: active02=active
    def prf(edges):
        s=set(edges); tp=len(s&TRUE_EDGES); fp=len(s-TRUE_EDGES); fn=len(TRUE_EDGES-s)
        prec=tp/max(1,tp+fp); rec=tp/max(1,tp+fn); f1=2*prec*rec/max(1e-9,prec+rec)
        return prec,rec,f1
    p,r,f=prf(active05); p2,r2,f2=prf(active02); kp,kr,kf=prf(topk)
    true_probs=[probs[EDGE_TO_ID[e]] for e in sorted(TRUE_EDGES)]
    false_probs=[p for p,e in zip(probs,CANDIDATES) if e not in TRUE_EDGES]
    return {
        'active_edge_count_threshold_0p5':len(active05),'active_edge_count_threshold_0p2':len(active02),
        'edge_f1_threshold_0p5':f,'edge_recall_threshold_0p5':r,'edge_precision_threshold_0p5':p,
        'edge_f1_threshold_0p2':f2,'edge_recall_threshold_0p2':r2,'edge_precision_threshold_0p2':p2,
        'topk_edges':[f'{i}->{j}' for i,j in topk], 'topk_edge_f1':kf, 'topk_edge_recall':kr, 'topk_edge_precision':kp,
        'true_edge_mean_prob':sum(true_probs)/len(true_probs), 'false_edge_mean_prob':sum(false_probs)/len(false_probs),
        'true_false_prob_gap':sum(true_probs)/len(true_probs)-sum(false_probs)/len(false_probs),
        'gate_entropy_proxy':sum(p*(1-p) for p in probs)/len(probs),
        'true_edges':[f'{i}->{j}' for i,j in sorted(TRUE_EDGES)],
    }

def train_dense():
    torch.manual_seed(SEED+1)
    m=BoundaryReader(use_gate=False).to(DEVICE)
    opt=torch.optim.AdamW(m.parameters(),lr=3e-3,weight_decay=1e-4)
    hist=[]
    for step in range(1,DENSE_STEPS+1):
        x,y=make_batch(BATCH); logits,_=m(x,mode='dense_candidate')
        loss=F.cross_entropy(logits.reshape(-1,VOCAB),y.reshape(-1))
        opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
        if step in {1,20,60,120}:
            acc,miss,reach,src=eval_model(m,'dense_candidate',batch=512)
            hist.append({'step':step,'loss':float(loss.item()),'acc':acc})
    return m,hist

def gate_posttrain(dense: BoundaryReader, lam:float, entropy_lam:float, init_gate:float=2.0):
    torch.manual_seed(SEED+int(lam*10000)+int(entropy_lam*10000))
    g=BoundaryReader(use_gate=True,init_gate=init_gate).to(DEVICE)
    # copy core state with non-strict so edge logits are separate
    sd=dense.state_dict()
    g.load_state_dict({k:v for k,v in sd.items() if k in g.state_dict() and g.state_dict()[k].shape==v.shape}, strict=False)
    g.set_core_requires_grad(False)
    opt=torch.optim.AdamW([g.edge_logits],lr=0.16,weight_decay=0.0)
    hist=[]
    for step in range(1,GATE_STEPS+1):
        x,y=make_batch(BATCH); logits,_=g(x,mode='soft_gate')
        ce=F.cross_entropy(logits.reshape(-1,VOCAB),y.reshape(-1))
        probs=g.gate_probs()
        entropy_proxy=(probs*(1-probs)).mean()
        loss=ce+lam*probs.mean()+entropy_lam*entropy_proxy
        opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
        if step in {1,20,55,110}:
            acc,_,_,_=eval_model(g,'soft_gate',batch=512)
            hist.append({'step':step,'ce':float(ce.item()),'acc':acc,'mean_gate':float(probs.mean().item()),'entropy_proxy':float(entropy_proxy.item())})
    probs=g.gate_probs().detach().cpu().tolist()
    em=edge_metrics_from_probs(probs)
    topk=[tuple(map(int,e.split('->'))) for e in em['topk_edges']]
    soft_acc,soft_miss,soft_reach,soft_src=eval_model(g,'soft_gate')
    topk_acc,topk_miss,topk_reach,topk_src=eval_model(g,'hard_edges',hard_edges=topk)
    th05_acc,th05_miss,th05_reach,th05_src=eval_model(g,'threshold_gate',threshold=0.5)
    return g,{
        'method':f'posttrain_gate_lam{lam}_ent{entropy_lam}',
        'lambda':lam,'entropy_lambda':entropy_lam,
        'soft_final_acc':soft_acc,'hard_topk_acc':topk_acc,'hard_threshold_0p5_acc':th05_acc,
        'soft_target_miss':soft_miss,'hard_topk_target_miss':topk_miss,'hard_threshold_0p5_target_miss':th05_miss,
        'soft_depth_reachable_fraction':soft_reach,'hard_topk_depth_reachable_fraction':topk_reach,'hard_threshold_0p5_depth_reachable_fraction':th05_reach,
        'deployment_gap_soft_to_hard_topk':soft_acc-topk_acc,
        'history':hist,
        **em,
    }

def hard_finetune_from(dense: BoundaryReader, hard_edges, label:str):
    m=copy.deepcopy(dense).to(DEVICE)
    opt=torch.optim.AdamW(m.parameters(),lr=2e-3,weight_decay=1e-4)
    hist=[]
    for step in range(1,HARD_FT_STEPS+1):
        x,y=make_batch(BATCH); logits,_=m(x,mode='hard_edges',hard_edges=hard_edges)
        loss=F.cross_entropy(logits.reshape(-1,VOCAB),y.reshape(-1))
        opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
        if step in {1,15,30,45}:
            acc,_,reach,_=eval_model(m,'hard_edges',hard_edges=hard_edges,batch=512)
            hist.append({'step':step,'loss':float(loss.item()),'acc':acc,'depth_reachable_fraction':reach})
    acc,miss,reach,src=eval_model(m,'hard_edges',hard_edges=hard_edges)
    topk_set=set(hard_edges); tp=len(topk_set&TRUE_EDGES); fp=len(topk_set-TRUE_EDGES); fn=len(TRUE_EDGES-topk_set)
    prec=tp/max(1,tp+fp); rec=tp/max(1,tp+fn); f1=2*prec*rec/max(1e-9,prec+rec)
    return {'method':label,'final_acc':acc,'target_miss':miss,'depth_reachable_fraction':reach,'active_edge_count':len(hard_edges),'topk_edge_f1':f1,'history':hist,'source_attention_mass_by_target_pos_last_layer':src}

def main():
    dense,dense_hist=train_dense()
    dense_acc,dense_miss,dense_reach,dense_src=eval_model(dense,'dense_candidate')
    fixed_acc,fixed_miss,fixed_reach,fixed_src=eval_model(dense,'fixed_block')
    rows=[{'method':'dense_candidate_trained','final_acc':dense_acc,'target_miss':dense_miss,'depth_reachable_fraction':dense_reach,'history':dense_hist,'active_edge_count':len(CANDIDATES),'topk_edge_f1':0.0,'deployment_gap':0.0},
          {'method':'fixed_block_same_weights','final_acc':fixed_acc,'target_miss':fixed_miss,'depth_reachable_fraction':fixed_reach,'history':[],'active_edge_count':0,'topk_edge_f1':0.0,'deployment_gap':dense_acc-fixed_acc}]
    gate_rows=[]; best_topk=None; best_score=-1e9
    for lam,ent in [(0.0,0.0),(0.004,0.0),(0.012,0.0),(0.030,0.0),(0.012,0.020),(0.030,0.020),(0.060,0.040)]:
        g,row=gate_posttrain(dense,lam,ent)
        gate_rows.append(row)
        score=row['hard_topk_acc']+0.08*row['topk_edge_f1']-0.02*row['deployment_gap_soft_to_hard_topk']-0.004*row['active_edge_count_threshold_0p2']
        if score>best_score:
            best_score=score; best_topk=[tuple(map(int,e.split('->'))) for e in row['topk_edges']]; best_label=row['method']
    rows += gate_rows
    if best_topk is not None:
        rows.append(hard_finetune_from(dense,best_topk,f'hard_topk_finetune_from_{best_label}'))
        rows.append(hard_finetune_from(dense,sorted(TRUE_EDGES),'oracle_true_bridge_finetune'))
    # Normalize promotion scores for mixed row schemas.
    for r in rows:
        acc=r.get('final_acc',r.get('hard_topk_acc',0.0))
        f1=r.get('topk_edge_f1',0.0)
        gap=r.get('deployment_gap_soft_to_hard_topk',r.get('deployment_gap',0.0))
        active=r.get('active_edge_count',r.get('active_edge_count_threshold_0p2',len(CANDIDATES)))
        r['promotion_score']=acc+0.08*f1-0.03*max(0,gap)-0.003*max(0,active-len(TRUE_EDGES))
    non_oracle=[r for r in rows if 'oracle' not in r['method'] and r['method']!='dense_candidate_trained']
    winner=max(non_oracle,key=lambda r:r['promotion_score'])
    payload={
        'project':'CloudtainerML','revision':REV,'probe':'tiny_bridge_posttrain_sparsify','kind':'trained_tiny_probe',
        'source_ids':['SRC-0348','SRC-0356','SRC-0357'], 'cell_ids':['CELL-349'],
        'summary':{
            'primary_metric':{'name':'promotion_score','direction':'higher_is_better'},
            'winner_excluding_dense_and_oracle':winner['method'],
            'best_hard_topk_acc':max(r.get('hard_topk_acc',r.get('final_acc',0.0)) for r in non_oracle),
            'best_topk_edge_f1':max(r.get('topk_edge_f1',0.0) for r in rows),
            'dense_candidate_acc':dense_acc,
            'fixed_block_acc_same_weights':fixed_acc,
            'guard_fields':['hard_topk_acc','hard_threshold_0p5_acc','deployment_gap_soft_to_hard_topk','topk_edge_f1','edge_f1_threshold_0p5','edge_f1_threshold_0p2','depth_reachable_fraction','hard_topk_depth_reachable_fraction','target_miss','hard_topk_target_miss','active_edge_count_threshold_0p2','gate_entropy_proxy'],
            'interpretation':'Post-training sparse bridge probe: train dense candidate connectivity, freeze core weights, then learn sparse edge priors under exact-copy loss. It asks whether soft top-k bridge preference can be compiled into a hard sparse program with low deployment gap.',
        },
        'rows':rows,
    }
    path=OUT/f'{REVUP}_TINY_BRIDGE_POSTTRAIN_SPARSIFY_SMOKE.json'
    path.write_text(json.dumps(payload,indent=2),encoding='utf-8')
    print(json.dumps(payload['summary'],indent=2))

if __name__=='__main__':
    main()
