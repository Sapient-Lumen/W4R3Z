// CloudtainerML rev0023: FlowTracer-style attention-DAG credit probe.
// Dependency-free C++17 graph simulator. It tests whether answer-targeted flow
// through an attention-induced DAG better identifies useful reasoning tokens than
// uniform, local-attention, or recency heuristics. Synthetic only.

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
#include <string>
#include <vector>

struct Edge{int u,v; double w;};
struct Row{std::string scenario,method; int nodes=0,n=0; double precision=0,recall=0,f1=0,noise_credit=0,utility=0;};
static std::string esc(const std::string&s){std::string o; for(char c:s){ if(c=='"')o+="\\\""; else if(c=='\\')o+="\\\\"; else o+=c;} return o;}
static double clamp(double x,double a,double b){return std::max(a,std::min(b,x));}
static std::vector<int> topk(const std::vector<double>&s,int k){std::vector<int>idx(s.size());std::iota(idx.begin(),idx.end(),0); k=std::min(k,(int)idx.size()); std::partial_sort(idx.begin(),idx.begin()+k,idx.end(),[&](int a,int b){return s[a]>s[b];}); idx.resize(k); return idx;}
struct Graph{int n=0,answer=0; std::vector<Edge> edges; std::vector<int> gold; std::vector<double> local_attn, recency;};
static Graph make_graph(int seed,const std::string&scenario){
    std::mt19937_64 rng(seed); std::uniform_real_distribution<double>U(0,1); int n=90; if(scenario=="long_bridge") n=130; if(scenario=="short_direct") n=70; Graph g; g.n=n; g.answer=n-1; g.local_attn.assign(n,0); g.recency.assign(n,0);
    int chain= scenario=="branchy_decoy"?10: scenario=="long_bridge"?16: scenario=="formatting_flood"?8:6;
    int pos=2+(rng()%6); g.gold.push_back(pos);
    for(int i=1;i<chain;i++){ pos += 3 + (rng()%std::max(3,n/(chain+5))); if(pos>=n-2) pos=n-2-i; g.gold.push_back(pos); }
    std::sort(g.gold.begin(),g.gold.end()); g.gold.erase(std::unique(g.gold.begin(),g.gold.end()),g.gold.end());
    for(int v=1; v<n; ++v){
        int m=2+(rng()%5); for(int j=0;j<m;++j){ int u=(int)(rng()%v); double w=0.02+0.10*U(rng); g.edges.push_back({u,v,w}); g.local_attn[u]+=w; }
        if(scenario=="formatting_flood" && v>n/2){ int u=v-1; g.edges.push_back({u,v,0.18+0.12*U(rng)}); g.local_attn[u]+=0.18; }
    }
    for(size_t i=1;i<g.gold.size();++i){ int u=g.gold[i-1], v=g.gold[i]; double w= scenario=="weak_bridge"?0.12:0.45; g.edges.push_back({u,v,w}); g.local_attn[u]+=w; }
    if(!g.gold.empty()){ int u=g.gold.back(); g.edges.push_back({u,g.answer,0.78}); g.local_attn[u]+=0.78; }
    if(scenario=="branchy_decoy"){
        int start=5; for(int i=0;i<12;i++){ int u=start+i*3; int v=std::min(n-2,u+2); if(u<v){ g.edges.push_back({u,v,0.65}); g.local_attn[u]+=0.65; }}
    }
    if(scenario=="spurious_answer_local"){
        for(int u=n-10; u<n-1; ++u){ g.edges.push_back({u,g.answer,0.34+0.12*U(rng)}); g.local_attn[u]+=0.34; }
    }
    for(int i=0;i<n;i++) g.recency[i]=(double)i/n;
    return g;
}
static std::vector<double> reverse_reach_flow(const Graph&g){
    std::vector<std::vector<std::pair<int,double>>> pred(g.n); for(auto&e:g.edges) pred[e.v].push_back({e.u,e.w});
    std::vector<double> flow(g.n,0); flow[g.answer]=1.0;
    for(int v=g.n-1; v>=1; --v){ double z=0; for(auto&p:pred[v]) z+=std::max(0.0,p.second); if(z<=0) continue; for(auto&p:pred[v]) flow[p.first]+=flow[v]*(std::max(0.0,p.second)/z); }
    flow[g.answer]=0; return flow;
}
static std::vector<double> path_backbone(const Graph&g){
    std::vector<std::vector<std::pair<int,double>>> pred(g.n); for(auto&e:g.edges) pred[e.v].push_back({e.u,e.w});
    std::vector<double> best(g.n,-1e9); std::vector<int> next(g.n,-1); best[g.answer]=0;
    for(int v=g.n-1; v>=1; --v) for(auto&p:pred[v]){ double cand=best[v]+std::log(std::max(1e-9,p.second)); if(cand>best[p.first]){best[p.first]=cand; next[p.first]=v;} }
    std::vector<double>s(g.n,0); for(int u=0;u<g.n;u++){ if(best[u]>-1e8) s[u]=std::exp(best[u]); } return s;
}
static void eval(const Graph&g,const std::string&method,Row&r){
    std::vector<double> score(g.n,0); int k=std::max(3,(int)g.gold.size());
    if(method=="uniform") std::fill(score.begin(),score.end(),1.0);
    else if(method=="local_attention_mass") score=g.local_attn;
    else if(method=="recency") score=g.recency;
    else if(method=="max_path_backbone") score=path_backbone(g);
    else if(method=="flowtrace_toy") score=reverse_reach_flow(g);
    else if(method=="oracle_gold") for(int u:g.gold) score[u]=1.0;
    auto pick=topk(score,k); std::set<int>P(pick.begin(),pick.end()),G(g.gold.begin(),g.gold.end()); int tp=0; for(int u:P) if(G.count(u)) tp++;
    double prec=P.empty()?0:(double)tp/P.size(); double rec=G.empty()?0:(double)tp/G.size(); double f1=(prec+rec)>0?2*prec*rec/(prec+rec):0; double noise=0; for(int u:P) if(!G.count(u)) noise++;
    double util=f1 - 0.08*noise; r.precision+=prec; r.recall+=rec; r.f1+=f1; r.noise_credit+=noise; r.utility+=util; r.n++;
}
int main(int argc,char**argv){
    std::string out="artifacts/probe-results/REV0023_FLOWTRACE_CREDIT_SMOKE.json"; if(argc>1) out=argv[1]; auto t0=std::chrono::high_resolution_clock::now();
    std::vector<std::string> scenarios={"short_direct","long_bridge","weak_bridge","branchy_decoy","formatting_flood","spurious_answer_local"};
    std::vector<std::string> methods={"uniform","recency","local_attention_mass","max_path_backbone","flowtrace_toy","oracle_gold"};
    std::map<std::string,Row> rows; std::map<std::string,int>wins,nonoracle;
    for(auto&sc:scenarios) for(int seed=0; seed<120; ++seed){ Graph g=make_graph(7000+seed*17,sc); double b=-9,bn=-9; std::string wm,wn; std::map<std::string,double> u;
        for(auto&m:methods){ std::string key=sc+"|"+m; if(!rows.count(key)){ rows[key].scenario=sc; rows[key].method=m; rows[key].nodes=g.n;} eval(g,m,rows[key]); u[m]=rows[key].utility/std::max(1,rows[key].n); }
        for(auto&m:methods){ double val=u[m]; if(val>b){b=val;wm=m;} if(m.find("oracle")==std::string::npos && val>bn){bn=val;wn=m;} } wins[wm]++; nonoracle[wn]++;
    }
    double seconds=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count();
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"flowtrace_credit\",\n  \"language\": \"c++17\",\n  \"is_paper_reproduction\": false,\n  \"taxonomy\": [\"reasoning-credit\", \"attention-dag\", \"rl-signal\"],\n";
    f<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<seconds<<", \"primary_metric\": {\"name\": \"mean_f1\", \"direction\": \"higher_is_better\", \"winner_field\": \"winner_counts_excluding_oracle\"}, \"winner_counts\": {"; bool first=true; for(auto&kv:wins){if(!first)f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second;} f<<"}, \"winner_counts_excluding_oracle\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second;} f<<"}, \"interpretation\": \"Answer-targeted flow is tested against local mass and recency for reasoning token credit assignment.\"},\n  \"rows\": [\n";
    int c=0; for(auto&kv:rows){ const Row&r=kv.second; double n=std::max(1,r.n); if(c++)f<<",\n"; f<<"    {\"scenario\": \""<<esc(r.scenario)<<"\", \"method\": \""<<esc(r.method)<<"\", \"nodes\": "<<r.nodes<<", \"mean_precision\": "<<r.precision/n<<", \"mean_recall\": "<<r.recall/n<<", \"mean_f1\": "<<r.f1/n<<", \"mean_noise_credit\": "<<r.noise_credit/n<<", \"mean_utility\": "<<r.utility/n<<"}"; }
    f<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
