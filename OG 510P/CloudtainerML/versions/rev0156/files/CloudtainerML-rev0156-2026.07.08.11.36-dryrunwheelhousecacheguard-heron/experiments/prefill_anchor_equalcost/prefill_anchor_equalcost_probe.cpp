// CloudtainerML rev0023: equal-cost sparse prefill chunk-anchor probe.
// Synthetic C++17 probe. Not a paper reproduction.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <string>
#include <vector>
struct Chunk{double semantic, anchor, evidence, middle, distractor; int tokens;};
struct Row{std::string regime,policy; int budget=0,n=0; double recall=0, falsehit=0, cost=0, utility=0;};
static std::string esc(const std::string&s){std::string o; for(char c:s){if(c=='"')o+="\\\""; else if(c=='\\')o+="\\\\"; else o+=c;} return o;}
static double clamp(double x,double a,double b){return std::max(a,std::min(b,x));}
static double rnd(std::mt19937_64&r,double a=0,double b=1){return std::uniform_real_distribution<double>(a,b)(r);} 
static std::vector<Chunk> make_doc(const std::string&reg,std::mt19937_64&rng){
    int n=96; std::vector<Chunk> cs; cs.reserve(n);
    for(int i=0;i<n;i++){double pos=double(i)/(n-1); cs.push_back({rnd(rng,0.05,0.7),rnd(rng,0.05,0.65),0.0,1.0-std::abs(pos-0.5)*2.0,rnd(rng,0,0.2),64});}
    std::vector<int> ev;
    if(reg=="lost_middle") ev={45,47,52}; else if(reg=="boundary_needle") ev={0,1,94}; else if(reg=="distributed_evidence") ev={14,37,61,82}; else if(reg=="adversarial_anchor") ev={30,31,32}; else ev={12,13,14};
    for(int id:ev){cs[id].evidence=1.0; cs[id].semantic += rnd(rng,0.18,0.34); cs[id].anchor += (reg=="adversarial_anchor"?rnd(rng,0.02,0.12):rnd(rng,0.25,0.55));}
    if(reg=="adversarial_anchor"){for(int id:{2,3,4,90,91,92}){cs[id].anchor=rnd(rng,0.85,1.0); cs[id].semantic=rnd(rng,0.55,0.8); cs[id].distractor=1.0;}}
    if(reg=="lost_middle"){for(int i=0;i<n;i++){cs[i].semantic -= 0.20*cs[i].middle;}}
    return cs;
}
static double score(const Chunk&c,const std::string&pol,int i,int n){
    double posedge=(i<4||i>n-5)?1.0:0.0;
    if(pol=="dense_equal_cost") return 1.0 - 1e-5*i;
    if(pol=="topk_semantic") return c.semantic;
    if(pol=="topk_anchor") return 0.55*c.semantic + 0.55*c.anchor;
    if(pol=="anchor_then_expand") return 0.50*c.semantic + 0.65*c.anchor + 0.12*posedge;
    if(pol=="middle_repair") return 0.50*c.semantic + 0.35*c.anchor + 0.30*c.middle;
    if(pol=="distractor_aware") return 0.62*c.semantic + 0.48*c.anchor + 0.22*c.middle - 0.80*c.distractor;
    if(pol=="oracle_chunks") return c.evidence;
    return c.semantic;
}
static void add(Row&r,double rec,double falsehit,double cost,double util){r.n++; r.recall+=rec; r.falsehit+=falsehit; r.cost+=cost; r.utility+=util;}
int main(int argc,char**argv){
    std::string out="artifacts/probe-results/REV0023_PREFILL_ANCHOR_EQUALCOST_SMOKE.json"; if(argc>1) out=argv[1];
    auto t0=std::chrono::high_resolution_clock::now();
    std::vector<std::string> regimes={"lost_middle","boundary_needle","distributed_evidence","adversarial_anchor","easy"};
    std::vector<std::string> policies={"dense_equal_cost","topk_semantic","topk_anchor","anchor_then_expand","middle_repair","distractor_aware","oracle_chunks"};
    std::vector<int> budgets={384,768,1536,3072}; // equal token budgets; each chunk is 64 tokens
    std::map<std::string,Row> rows; std::map<std::string,int>wins;
    for(auto&reg:regimes) for(int budget:budgets) for(int seed=0; seed<96; ++seed){double best=-1e9; std::string bp; for(auto&pol:policies){std::mt19937_64 rng(81011+seed*101+budget*7+reg.size()*17+pol.size()*19); auto cs=make_doc(reg,rng); int n=cs.size(); int k=std::max(1,budget/64); std::vector<int> idx(n); std::iota(idx.begin(),idx.end(),0); std::stable_sort(idx.begin(),idx.end(),[&](int a,int b){return score(cs[a],pol,a,n)>score(cs[b],pol,b,n);}); std::vector<int> selected; int used=0; for(int z=0; z<(int)idx.size() && used+cs[idx[z]].tokens<=budget; ++z){selected.push_back(idx[z]); used+=cs[idx[z]].tokens; if(pol=="anchor_then_expand"){int a=idx[z]; for(int nb:{a-1,a+1}) if(nb>=0&&nb<n && used+64<=budget && std::find(selected.begin(),selected.end(),nb)==selected.end()){selected.push_back(nb); used+=64;}}}
        double ev_total=0, ev_hit=0, falsehit=0; for(auto&c:cs)ev_total+=c.evidence; for(int id:selected){ev_hit+=cs[id].evidence; falsehit+=cs[id].distractor;} double recall=clamp(ev_hit/std::max(1.0,ev_total),0,1); falsehit=clamp(falsehit/std::max(1,(int)selected.size()),0,1); double cost=used; double util=3.0*recall - 0.65*falsehit - 0.00035*cost + (recall>0.99?0.4:0.0); std::string key=reg+"|"+std::to_string(budget)+"|"+pol; if(!rows.count(key)){rows[key].regime=reg; rows[key].budget=budget; rows[key].policy=pol;} add(rows[key],recall,falsehit,cost,util); if(util>best){best=util; bp=pol;}}
        wins[bp]++;}
    double seconds=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count();
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"prefill_anchor_equalcost\",\n  \"language\": \"c++17\",\n  \"is_paper_reproduction\": false,\n";
    f<<"  \"taxonomy\": [\"long-context\", \"prefill\", \"chunk-routing\", \"equal-cost\", \"native\"],\n";
    f<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<seconds<<", \"primary_metric\": {\"name\": \"mean_utility\", \"direction\": \"higher_is_better\", \"winner_field\": \"winner_counts\"}, \"tail_metrics\": {\"has_catastrophic_proxy\": true, \"fields\": [\"mean_recall\", \"mean_false_hit_rate\"]}, \"winner_counts\": {"; bool first=true; for(auto&kv:wins){if(!first)f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second;} f<<"}, \"interpretation\": \"Equal-token-cost chunk selection makes sparse anchors compete fairly with dense prefix processing.\"},\n  \"rows\": [\n";
    int c=0; for(auto&kv:rows){const Row&r=kv.second; double n=std::max(1,r.n); if(c++)f<<",\n"; f<<"    {\"regime\": \""<<esc(r.regime)<<"\", \"budget_tokens\": "<<r.budget<<", \"policy\": \""<<esc(r.policy)<<"\", \"mean_recall\": "<<r.recall/n<<", \"mean_false_hit_rate\": "<<r.falsehit/n<<", \"mean_cost_tokens\": "<<r.cost/n<<", \"mean_utility\": "<<r.utility/n<<"}";}
    f<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
