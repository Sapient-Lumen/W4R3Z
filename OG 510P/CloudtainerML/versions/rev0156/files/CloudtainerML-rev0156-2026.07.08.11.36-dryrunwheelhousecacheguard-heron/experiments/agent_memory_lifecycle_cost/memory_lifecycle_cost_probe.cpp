// CloudtainerML rev0023: agent-memory lifecycle cost frontier probe.
// Synthetic C++17 probe. Not a paper reproduction.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <vector>
struct Row{std::string regime,policy; int queries=0,n=0; double accuracy=0, freshness=0, construction=0, serve=0, total=0, utility=0;};
static std::string esc(const std::string&s){std::string o; for(char c:s){if(c=='"')o+="\\\""; else if(c=='\\')o+="\\\\"; else o+=c;} return o;}
static double clamp(double x,double a,double b){return std::max(a,std::min(b,x));}
static double rnd(std::mt19937_64&r,double a=0,double b=1){return std::uniform_real_distribution<double>(a,b)(r);} 
struct Eval{double acc,fresh,construct,serve,total,utility;};
static Eval eval(const std::string&reg,const std::string&pol,int q,int seed){std::mt19937_64 rng(99001+seed*131+q*17+reg.size()*23+pol.size()*29); double mut=reg=="high_mutation"?0.85:reg=="stale_sessions"?0.65:0.25; double structure=reg=="structure_needed"?0.9:0.35; double fewq= q<80 ? 1.0:0.0; double c=0,s=0,acc=0,fresh=0;
    if(pol=="bm25_flat"){c=1.0; s=0.020*q; acc=0.50+0.05*(1-mut); fresh=0.70;}
    else if(pol=="embed_rag"){c=3.0; s=0.045*q; acc=0.61+0.05*(1-mut); fresh=0.66;}
    else if(pol=="structured_triples"){c=18.0+12.0*structure; s=0.060*q; acc=0.65+0.18*structure-0.04*mut; fresh=0.58;}
    else if(pol=="agentic_control_flow"){c=42.0+20.0*structure; s=0.075*q; acc=0.72+0.14*structure-0.08*mut; fresh=0.52;}
    else if(pol=="on_demand_structure"){c=7.0+0.22*q*structure; s=0.060*q; acc=0.64+0.15*structure-0.03*mut; fresh=0.74-0.12*mut;}
    else if(pol=="freshness_scheduled_hybrid"){c=10.0+0.12*q+8.0*structure; s=0.055*q; acc=0.66+0.14*structure; fresh=0.82-0.04*mut;}
    else if(pol=="oracle_lifecycle") {c=8.0+4.0*structure; s=0.030*q; acc=0.90; fresh=0.92;}
    if(reg=="few_queries") {acc -= 0.03*(c>20);}
    if(reg=="many_queries") {acc += 0.03*(pol!="bm25_flat");}
    if(reg=="stale_sessions") {fresh -= 0.22*(pol=="agentic_control_flow"||pol=="structured_triples"); fresh += 0.12*(pol=="freshness_scheduled_hybrid");}
    acc=clamp(acc*(0.94+0.12*rnd(rng)),0,1); fresh=clamp(fresh*(0.94+0.12*rnd(rng)),0,1); double total=c+s; double utility=4.0*acc+1.6*fresh-0.018*total-0.45*std::max(0.0,0.65-fresh); return {acc,fresh,c,s,total,utility};}
static void add(Row&r,const Eval&e){r.n++; r.accuracy+=e.acc; r.freshness+=e.fresh; r.construction+=e.construct; r.serve+=e.serve; r.total+=e.total; r.utility+=e.utility;}
int main(int argc,char**argv){std::string out="artifacts/probe-results/REV0023_MEMORY_LIFECYCLE_COST_SMOKE.json"; if(argc>1) out=argv[1]; auto t0=std::chrono::high_resolution_clock::now(); std::vector<std::string> regimes={"few_queries","many_queries","high_mutation","structure_needed","stale_sessions"}; std::vector<std::string> policies={"bm25_flat","embed_rag","structured_triples","agentic_control_flow","on_demand_structure","freshness_scheduled_hybrid","oracle_lifecycle"}; std::vector<int> queries={20,80,300,1000}; std::map<std::string,Row> rows; std::map<std::string,int>wins; for(auto&reg:regimes) for(int q:queries) for(int seed=0; seed<96; ++seed){double best=-1e9; std::string bp; for(auto&pol:policies){Eval e=eval(reg,pol,q,seed); std::string key=reg+"|"+std::to_string(q)+"|"+pol; if(!rows.count(key)){rows[key].regime=reg; rows[key].queries=q; rows[key].policy=pol;} add(rows[key],e); if(e.utility>best){best=e.utility; bp=pol;}} wins[bp]++;} double seconds=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count(); std::ofstream f(out); f<<std::fixed<<std::setprecision(6); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"memory_lifecycle_cost\",\n  \"language\": \"c++17\",\n  \"is_paper_reproduction\": false,\n"; f<<"  \"taxonomy\": [\"agent-memory\", \"systems-cost\", \"phase-diagram\", \"lifecycle\", \"native\"],\n"; f<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<seconds<<", \"primary_metric\": {\"name\": \"mean_utility\", \"direction\": \"higher_is_better\", \"winner_field\": \"winner_counts\"}, \"tail_metrics\": {\"has_catastrophic_proxy\": true, \"fields\": [\"mean_freshness\", \"mean_accuracy\"]}, \"winner_counts\": {"; bool first=true; for(auto&kv:wins){if(!first)f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second;} f<<"}, \"interpretation\": \"Memory construction cost can dominate query-time gains; on-demand structure competes with expensive always-on construction.\"},\n  \"rows\": [\n"; int c=0; for(auto&kv:rows){auto&r=kv.second; double n=std::max(1,r.n); if(c++)f<<",\n"; f<<"    {\"regime\": \""<<esc(r.regime)<<"\", \"queries\": "<<r.queries<<", \"policy\": \""<<esc(r.policy)<<"\", \"mean_accuracy\": "<<r.accuracy/n<<", \"mean_freshness\": "<<r.freshness/n<<", \"mean_construction_cost\": "<<r.construction/n<<", \"mean_serve_cost\": "<<r.serve/n<<", \"mean_total_cost\": "<<r.total/n<<", \"mean_utility\": "<<r.utility/n<<"}";} f<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;}
