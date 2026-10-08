// CloudtainerML rev0023: structure-aware on-demand hypergraph memory probe.
// Inspired by DocTrace / hypergraph working memory for long-document QA. This
// toy asks whether following document hierarchy + query-triggered hyperedges can
// recover scattered evidence cheaper than flat retrieval or full scan.

#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <vector>

struct Node{int section=0; double lex=0, sem=0, order=0; bool e1=false,e2=false,decoy=false;};
struct Row{std::string regime,policy;int budget=0;double success=0,cost=0,evidence_hit=0,false_hits=0;int n=0;};
static std::string esc(const std::string&s){std::string o;for(char c:s){if(c=='"')o+="\\\"";else if(c=='\\')o+="\\\\";else o+=c;}return o;}
static double urand(std::mt19937_64&r){return std::generate_canonical<double,53>(r);} 
static std::vector<int> topk(const std::vector<double>&s,int k){k=std::max(0,std::min((int)s.size(),k));std::vector<int>idx(s.size());std::iota(idx.begin(),idx.end(),0);std::partial_sort(idx.begin(),idx.begin()+k,idx.end(),[&](int a,int b){return s[a]>s[b];});idx.resize(k);return idx;}
static std::vector<Node> make_doc(std::mt19937_64&r,const std::string&regime,int sections=24,int per=20){
    std::vector<Node>d(sections*per); for(int s=0;s<sections;s++) for(int i=0;i<per;i++){int id=s*per+i; d[id].section=s; d[id].order=(double)id/(sections*per-1); d[id].lex=urand(r)*0.25; d[id].sem=urand(r)*0.25;}
    int s1=r()%sections, s2=(s1+1+(r()%(sections-1)))%sections; if(regime=="same_section_chain") s2=s1; if(regime=="far_cross_section") s2=(s1+sections/2)%sections; if(regime=="hierarchy_needed") {s2=(s1+3)%sections;}
    int i1=s1*per+(r()%per), i2=s2*per+(r()%per); d[i1].e1=true; d[i2].e2=true; d[i1].sem+=1.0; d[i2].sem+=0.95; d[i1].lex+=0.45; d[i2].lex+=0.35;
    int decoys=(regime=="adversarial_decoys")?80:35; for(int z=0;z<decoys;z++){int id=r()%d.size(); if(d[id].e1||d[id].e2) continue; d[id].decoy=true; d[id].lex+=0.65+0.2*urand(r); d[id].sem+=0.20*urand(r);} 
    if(regime=="order_sensitive"){ d[i1].order=0.15; d[i2].order=0.88; }
    return d;
}
static Row eval(std::mt19937_64&r,const std::string&regime,const std::string&policy,int budget){
    auto d=make_doc(r,regime); int n=d.size(); std::vector<double>s(n),sec_score(24,0.0); std::set<int>chosen;
    auto add=[&](int idx){if((int)chosen.size()<budget) chosen.insert(idx);};
    if(policy=="flat_lexical_topk"){for(int i=0;i<n;i++)s[i]=d[i].lex; for(int i:topk(s,budget))add(i);} 
    else if(policy=="flat_semantic_topk"){for(int i=0;i<n;i++)s[i]=d[i].sem; for(int i:topk(s,budget))add(i);} 
    else if(policy=="hierarchy_sections_then_local"){for(int i=0;i<n;i++)sec_score[d[i].section]+=0.55*d[i].sem+0.45*d[i].lex; for(int sec:topk(sec_score,std::max(1,budget/8))){std::vector<double>local(n,-1e9); for(int i=0;i<n;i++)if(d[i].section==sec)local[i]=0.55*d[i].sem+0.45*d[i].lex; for(int i:topk(local,std::max(2,budget/std::max(1,budget/8))))add(i);}}
    else if(policy=="hypergraph_trace"){for(int i=0;i<n;i++)s[i]=0.45*d[i].lex+0.55*d[i].sem; for(int i:topk(s,std::max(3,budget/4)))add(i); std::vector<double>sec(24,0); for(int id:chosen){sec[d[id].section]+=1.0+d[id].sem; if(d[id].section>0)sec[d[id].section-1]+=0.25; if(d[id].section<23)sec[d[id].section+1]+=0.25;} for(int sc:topk(sec,std::max(1,budget/12))){std::vector<double>local(n,-1e9); for(int i=0;i<n;i++) if(d[i].section==sc || std::abs(d[i].section-sc)==1) local[i]=0.35*d[i].lex+0.65*d[i].sem+0.10*(1.0-std::abs(d[i].order-0.5)); for(int i:topk(local,budget-(int)chosen.size()))add(i);} }
    else if(policy=="experience_trace_reuse"){ // previous successful plan biases neighbor sections but can be stale.
        int anchor=(regime=="adversarial_decoys")?3:12; for(int i=0;i<n;i++)s[i]=0.35*d[i].lex+0.55*d[i].sem+0.30*std::exp(-0.5*std::abs(d[i].section-anchor)); for(int i:topk(s,budget))add(i);
    } else if(policy=="oracle_evidence"){for(int i=0;i<n;i++) if(d[i].e1||d[i].e2) add(i); for(int i=0;i<n && (int)chosen.size()<budget;i++) add(i);} 
    bool h1=false,h2=false; double fp=0; for(int id:chosen){h1=h1||d[id].e1; h2=h2||d[id].e2; fp+=d[id].decoy?1.0:0.0;} Row row; row.regime=regime; row.policy=policy; row.budget=budget; row.success=(h1&&h2)?1:0; row.evidence_hit=(h1?0.5:0)+(h2?0.5:0); row.false_hits=fp; row.cost=chosen.size(); row.n=1; return row;
}
static void acc(Row&a,const Row&b){a.success+=b.success;a.cost+=b.cost;a.evidence_hit+=b.evidence_hit;a.false_hits+=b.false_hits;a.n++;}
int main(int argc,char**argv){std::string out="artifacts/probe-results/REV0023_HYPERGRAPH_MEMORY_TRACE_SMOKE.json"; if(argc>1) out=argv[1]; auto t0=std::chrono::high_resolution_clock::now(); std::vector<std::string>regs={"same_section_chain","far_cross_section","hierarchy_needed","order_sensitive","adversarial_decoys"}; std::vector<std::string>pol={"flat_lexical_topk","flat_semantic_topk","hierarchy_sections_then_local","hypergraph_trace","experience_trace_reuse","oracle_evidence"}; std::vector<int>bud={8,16,32,64}; std::map<std::string,Row>rows; std::map<std::string,int>winners; for(int seed=0;seed<64;seed++){std::mt19937_64 rng(5555+seed*17); for(auto&r:regs)for(int b:bud){double best=-1;std::string win; for(auto&p:pol){Row x=eval(rng,r,p,b); std::string key=r+"|"+p+"|"+std::to_string(b); if(!rows.count(key)){rows[key]=x; rows[key].success=rows[key].cost=rows[key].evidence_hit=rows[key].false_hits=0; rows[key].n=0;} acc(rows[key],x); double score=x.success-0.002*x.cost-0.01*x.false_hits; if(score>best){best=score;win=p;}} winners[win]++;}}
 double sec=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count(); std::ofstream f(out); f<<std::fixed<<std::setprecision(6); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"hypergraph_memory_trace\",\n  \"config\": {\"seeds\": 64, \"nodes\": 480},\n  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<sec<<", \"primary_metric\": {\"name\": \"success_rate\", \"direction\": \"higher_is_better\", \"winner_field\": \"winner_counts\"}, \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second;} f<<"}},\n  \"rows\": [\n"; int c=0; for(auto&kv:rows){auto r=kv.second; double n=std::max(1,r.n); if(c++)f<<",\n"; f<<"    {\"regime\": \""<<esc(r.regime)<<"\", \"policy\": \""<<esc(r.policy)<<"\", \"budget\": "<<r.budget<<", \"success_rate\": "<<r.success/n<<", \"evidence_hit_rate\": "<<r.evidence_hit/n<<", \"mean_cost\": "<<r.cost/n<<", \"mean_false_hits\": "<<r.false_hits/n<<"}";} f<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n";}
