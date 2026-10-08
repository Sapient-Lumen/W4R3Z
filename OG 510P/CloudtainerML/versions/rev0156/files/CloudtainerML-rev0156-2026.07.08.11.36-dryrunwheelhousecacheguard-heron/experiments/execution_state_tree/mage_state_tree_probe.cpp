// CloudtainerML rev0023: execution-state-tree memory probe inspired by Mage-style state management.
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
struct Row{std::string regime,policy; int budget=0,n=0; double success=0, integrity=0, contamination=0, cost=0, utility=0;};
static std::string esc(const std::string&s){std::string o; for(char c:s){if(c=='"')o+="\\\""; else if(c=='\\')o+="\\\\"; else o+=c;} return o;}
static double clamp(double x,double a,double b){return std::max(a,std::min(b,x));}
static double rnd(std::mt19937_64&r,double a=0,double b=1){return std::uniform_real_distribution<double>(a,b)(r);} 
struct Eval{double success, integrity, contamination, cost, utility;};
static Eval eval(const std::string&reg,const std::string&pol,int budget,int seed){
    std::mt19937_64 rng(72001 + seed*97 + budget*11 + reg.size()*19 + pol.size()*31);
    int steps = reg=="long_dependency"?80:reg=="noisy_trace"?72:reg=="error_branching"?64:48;
    int errors = reg=="error_branching"?8:reg=="noisy_trace"?6:reg=="sibling_hint"?5:3;
    double dep = reg=="long_dependency"?0.95:reg=="sibling_hint"?0.75:0.55;
    double noise = reg=="noisy_trace"?0.65:reg=="error_branching"?0.45:0.22;
    double path=0, contam=0, hint=0, cost=0;
    if(pol=="full_context") { path=0.96; contam=0.16+0.05*errors; hint=0.45; cost=steps; }
    else if(pol=="semantic_retrieval") { path=0.42+0.15*rnd(rng); contam=0.34+0.18*noise; hint=0.45+0.18*rnd(rng); cost=budget*1.1; }
    else if(pol=="flat_summary") { path=0.58; contam=0.18+0.14*noise; hint=0.18; cost=budget*0.62; }
    else if(pol=="active_path_tree") { path=0.72+0.10*dep; contam=0.18+0.10*noise; hint=0.38; cost=budget*0.82; }
    else if(pol=="tree_maintain_revise") { path=0.78+0.13*dep; contam=0.07+0.07*noise; hint=0.48; cost=budget*1.02; }
    else if(pol=="tree_plus_sibling_hints") { path=0.74+0.11*dep; contam=0.12+0.06*noise; hint=reg=="sibling_hint"?0.82:0.52; cost=budget*1.12; }
    else if(pol=="oracle_active_path") { path=0.99; contam=0.01; hint=0.9; cost=budget*1.45; }
    if(reg=="error_branching" && pol=="full_context") contam += 0.28;
    if(reg=="long_dependency" && pol=="semantic_retrieval") path -= 0.18;
    if(reg=="sibling_hint" && pol=="tree_plus_sibling_hints") path += 0.08;
    if(reg=="easy") { path += 0.10; contam *= 0.55; }
    path=clamp(path*(0.92+0.16*rnd(rng)),0,1); contam=clamp(contam*(0.85+0.3*rnd(rng)),0,1); hint=clamp(hint,0,1);
    double integrity = clamp(path*(1.0-contam)*(0.82+0.18*hint),0,1);
    double success = 1.0/(1.0+std::exp(-(integrity-0.48)*8.0));
    double utility = 2.6*success + 1.6*integrity - 1.7*contam - 0.012*cost;
    return {success,integrity,contam,cost,utility};
}
static void add(Row&r,const Eval&e){r.n++; r.success+=e.success; r.integrity+=e.integrity; r.contamination+=e.contamination; r.cost+=e.cost; r.utility+=e.utility;}
int main(int argc,char**argv){
    std::string out="artifacts/probe-results/REV0023_MAGE_STATE_TREE_PROBE_SMOKE.json"; if(argc>1) out=argv[1];
    auto t0=std::chrono::high_resolution_clock::now();
    std::vector<std::string> regimes={"error_branching","long_dependency","sibling_hint","noisy_trace","easy"};
    std::vector<std::string> policies={"full_context","semantic_retrieval","flat_summary","active_path_tree","tree_maintain_revise","tree_plus_sibling_hints","oracle_active_path"};
    std::vector<int> budgets={16,32,64}; std::map<std::string,Row> rows; std::map<std::string,int>wins;
    for(auto&reg:regimes) for(int budget:budgets) for(int seed=0; seed<120; ++seed){double best=-1e9; std::string bp; for(auto&pol:policies){Eval e=eval(reg,pol,budget,seed); std::string key=reg+"|"+std::to_string(budget)+"|"+pol; if(!rows.count(key)){rows[key].regime=reg; rows[key].budget=budget; rows[key].policy=pol;} add(rows[key],e); if(e.utility>best){best=e.utility; bp=pol;}} wins[bp]++;}
    double seconds=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count();
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"mage_state_tree_probe\",\n  \"language\": \"c++17\",\n  \"is_paper_reproduction\": false,\n";
    f<<"  \"taxonomy\": [\"agent-memory\", \"execution-state\", \"tree-memory\", \"error-isolation\", \"native\"],\n";
    f<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<seconds<<", \"primary_metric\": {\"name\": \"mean_utility\", \"direction\": \"higher_is_better\", \"winner_field\": \"winner_counts\"}, \"tail_metrics\": {\"has_catastrophic_proxy\": true, \"fields\": [\"mean_error_contamination\", \"mean_state_integrity\"]}, \"winner_counts\": {"; bool first=true; for(auto&kv:wins){if(!first)f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second;} f<<"}, \"interpretation\": \"Tests whether active path/tree state beats similarity retrieval when traces branch, contain errors, or require long dependency integrity.\"},\n  \"rows\": [\n";
    int c=0; for(auto&kv:rows){auto&r=kv.second; double n=std::max(1,r.n); if(c++)f<<",\n"; f<<"    {\"regime\": \""<<esc(r.regime)<<"\", \"budget\": "<<r.budget<<", \"policy\": \""<<esc(r.policy)<<"\", \"mean_success\": "<<r.success/n<<", \"mean_state_integrity\": "<<r.integrity/n<<", \"mean_error_contamination\": "<<r.contamination/n<<", \"mean_cost\": "<<r.cost/n<<", \"mean_utility\": "<<r.utility/n<<"}";}
    f<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
