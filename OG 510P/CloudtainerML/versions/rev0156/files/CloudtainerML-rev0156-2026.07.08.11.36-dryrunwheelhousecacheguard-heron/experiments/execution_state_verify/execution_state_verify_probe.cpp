// CloudtainerML rev0023: execution-state verification / revise-boundary hardening.
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
struct Row{std::string regime,policy; int budget=0,n=0; double success=0, integrity=0, contam=0, recovery=0, cost=0, utility=0, cat=0;};
static std::string esc(const std::string&s){std::string o; for(char c:s){if(c=='"')o+="\\\""; else if(c=='\\')o+="\\\\"; else o+=c;} return o;}
static double clamp(double x,double a,double b){return std::max(a,std::min(b,x));}
static double rnd(std::mt19937_64&r,double a=0,double b=1){return std::uniform_real_distribution<double>(a,b)(r);} 
struct Eval{double success, integrity, contam, recovery, cost, utility, cat;};
static Eval eval(const std::string&reg,const std::string&pol,int budget,int seed){
    std::mt19937_64 rng(220020 + seed*131 + budget*43 + reg.size()*17 + pol.size()*29);
    double branch = reg=="deep_branch_error"?0.78:reg=="late_tool_failure"?0.55:reg=="false_success"?0.48:reg=="sibling_salvage"?0.70:0.30;
    double longdep = reg=="long_dependency"?0.92:0.45;
    double ambiguity = reg=="false_success"?0.85:reg=="semantic_near_miss"?0.78:0.40;
    double sibling = reg=="sibling_salvage"?0.85:0.30;
    double integrity=0, contam=0, recovery=0, cost=0;
    if(pol=="semantic_retrieval") { integrity=0.42+0.16*rnd(rng); contam=0.30+0.45*ambiguity; recovery=0.24+0.18*sibling; cost=budget*0.80; }
    else if(pol=="full_trace") { integrity=0.75+0.10*longdep; contam=0.20+0.32*branch+0.18*ambiguity; recovery=0.30; cost=budget*2.2; }
    else if(pol=="active_path_tree") { integrity=0.68+0.16*longdep; contam=0.16+0.20*branch; recovery=0.36+0.18*sibling; cost=budget*1.05; }
    else if(pol=="maintain_verify") { integrity=0.74+0.13*longdep; contam=0.09+0.13*branch+0.08*ambiguity; recovery=0.44+0.10*sibling; cost=budget*1.24; }
    else if(pol=="revise_on_failure") { integrity=0.76+0.10*longdep; contam=0.06+0.09*branch+0.10*ambiguity; recovery=0.62+0.26*sibling; cost=budget*1.42; }
    else if(pol=="verify_revise_hpo") { integrity=0.77+0.11*longdep+0.05*sibling; contam=0.05+0.06*branch+0.07*ambiguity; recovery=0.58+0.32*sibling; cost=budget*(1.18+0.22*branch); }
    else if(pol=="oracle_execution_state") { integrity=0.98; contam=0.01; recovery=0.92; cost=budget*1.8; }
    integrity=clamp(integrity*(0.90+0.20*rnd(rng)),0,1); contam=clamp(contam*(0.85+0.30*rnd(rng)),0,1); recovery=clamp(recovery*(0.88+0.24*rnd(rng)),0,1);
    double success=1.0/(1.0+std::exp(-((0.62*integrity+0.28*recovery-0.52*contam)-0.38)*8.5));
    double cat=(contam>0.52 || (reg=="false_success" && success>0.55 && integrity<0.45))?1.0:0.0;
    double utility=2.8*success+1.6*integrity+0.8*recovery-2.3*contam-0.008*cost-1.0*cat;
    return {success,integrity,contam,recovery,cost,utility,cat};
}
static void add(Row&r,const Eval&e){r.n++; r.success+=e.success; r.integrity+=e.integrity; r.contam+=e.contam; r.recovery+=e.recovery; r.cost+=e.cost; r.utility+=e.utility; r.cat+=e.cat;}
int main(int argc,char**argv){
    std::string out="artifacts/probe-results/REV0023_EXECUTION_STATE_VERIFY_SMOKE.json"; if(argc>1) out=argv[1];
    auto t0=std::chrono::high_resolution_clock::now();
    std::vector<std::string> regimes={"deep_branch_error","late_tool_failure","false_success","semantic_near_miss","sibling_salvage","long_dependency"};
    std::vector<std::string> policies={"semantic_retrieval","full_trace","active_path_tree","maintain_verify","revise_on_failure","verify_revise_hpo","oracle_execution_state"};
    std::vector<int> budgets={16,32,64,96}; std::map<std::string,Row> rows; std::map<std::string,int>wins;
    for(auto&reg:regimes) for(int budget:budgets) for(int seed=0;seed<96;++seed){double best=-1e18; std::string bp; for(auto&pol:policies){auto e=eval(reg,pol,budget,seed); std::string key=reg+"|"+std::to_string(budget)+"|"+pol; if(!rows.count(key)){rows[key].regime=reg; rows[key].budget=budget; rows[key].policy=pol;} add(rows[key],e); if(e.utility>best){best=e.utility; bp=pol;}} wins[bp]++;}
    double seconds=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count(); std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"execution_state_verify\",\n  \"language\": \"c++17\",\n  \"is_paper_reproduction\": false,\n";
    f<<"  \"taxonomy\": [\"agent-memory\", \"execution-state\", \"verification\", \"branch-revision\", \"native\"],\n";
    f<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<seconds<<", \"primary_metric\": {\"name\": \"mean_utility\", \"direction\": \"higher_is_better\", \"winner_field\": \"winner_counts\"}, \"tail_metrics\": {\"has_catastrophic_proxy\": true, \"fields\": [\"catastrophic_state_failure_rate\", \"mean_error_contamination\", \"mean_state_integrity\"]}, \"winner_counts\": {";
    bool first=true; for(auto&kv:wins){if(!first)f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second;} f<<"}, \"interpretation\": \"Tests whether Maintain/Revise verification beats semantic retrieval/full-trace baselines under branch errors, false success, and long dependencies.\"},\n  \"rows\": [\n";
    int c=0; for(auto&kv:rows){auto&r=kv.second; double n=std::max(1,r.n); if(c++)f<<",\n"; f<<"    {\"regime\": \""<<esc(r.regime)<<"\", \"budget\": "<<r.budget<<", \"policy\": \""<<esc(r.policy)<<"\", \"mean_success\": "<<r.success/n<<", \"mean_state_integrity\": "<<r.integrity/n<<", \"mean_error_contamination\": "<<r.contam/n<<", \"mean_recovery\": "<<r.recovery/n<<", \"mean_cost\": "<<r.cost/n<<", \"mean_utility\": "<<r.utility/n<<", \"catastrophic_state_failure_rate\": "<<r.cat/n<<"}";}
    f<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
