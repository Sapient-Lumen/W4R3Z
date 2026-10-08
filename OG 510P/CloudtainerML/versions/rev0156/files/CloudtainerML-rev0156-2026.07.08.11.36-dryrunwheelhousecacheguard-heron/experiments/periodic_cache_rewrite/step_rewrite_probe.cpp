// CloudtainerML rev0023: periodic/step-boundary cache rewrite probe.
// Toy C++17 simulator inspired by cache processors that rewrite KV state at
// reasoning-step boundaries. It tests whether explicit delimiters/events are a
// useful compression clock compared with continuous eviction.

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
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

struct Row { std::string regime, method; int budget=0, facts=0, hops=0, n=0; double success=0, retained=0, rewrite_cost=0, utility=0; };
static double clamp(double x,double lo,double hi){ return std::max(lo,std::min(hi,x)); }
static std::string esc(const std::string& s){ std::string o; for(char c:s){ if(c=='"') o+="\\\""; else if(c=='\\') o+="\\\\"; else o+=c; } return o; }

struct Regime { std::string name; int steps, facts_per_step, budget, query_hops; double delimiter_noise, distractor_rate, recurrent_fact_rate; };

static std::vector<int> choose_top(const std::vector<double>& score, int budget){
    std::vector<int> idx(score.size()); std::iota(idx.begin(),idx.end(),0);
    std::partial_sort(idx.begin(), idx.begin()+std::min(budget,(int)idx.size()), idx.end(), [&](int a,int b){ return score[a]>score[b]; });
    idx.resize(std::min(budget,(int)idx.size())); return idx;
}
static double run_once(const Regime& r, const std::string& method, int seed, double& retained_frac, double& rewrite_cost){
    std::mt19937_64 rng(seed); std::uniform_real_distribution<double> U(0,1); std::normal_distribution<double> N(0,1);
    int total=r.steps*r.facts_per_step; std::vector<int> fact_step(total); std::vector<double> sal(total), importance(total), recurrence(total,0.0);
    for(int s=0;s<r.steps;s++) for(int j=0;j<r.facts_per_step;j++){ int id=s*r.facts_per_step+j; fact_step[id]=s; importance[id]=0.2+0.8*U(rng); sal[id]=importance[id]*(0.4+0.6*U(rng)); if(U(rng)<r.recurrent_fact_rate) recurrence[id]=0.8+0.4*U(rng); }
    // Multi-hop query mostly needs one fact from each of the last/earlier reasoning steps.
    std::set<int> needed;
    for(int h=0; h<r.query_hops; ++h){ int step = std::max(0, r.steps-1 - h*(std::max(1,r.steps/(r.query_hops+1)))); int base=step*r.facts_per_step; int id=base + (seed+h*17)%r.facts_per_step; needed.insert(id); }
    if(r.name=="early_premise_late_use") needed.insert((seed%r.facts_per_step));
    if(r.name=="recurrent_definition") for(int i=0;i<total;i++) if(recurrence[i]>0.9 && (int)needed.size()<r.query_hops+2) needed.insert(i);

    std::vector<double> score(total,0.0); rewrite_cost=0.0;
    if(method=="continuous_eviction"){
        for(int i=0;i<total;i++){ double recency=1.0/(1.0 + (r.steps-1-fact_step[i])); score[i]=0.65*sal[i]+1.15*recency+0.25*recurrence[i]; }
    } else if(method=="fixed_periodic_rewrite"){
        for(int i=0;i<total;i++){ int boundary=(fact_step[i]/3)*3; double local=1.0/(1.0+std::abs(fact_step[i]-boundary)); score[i]=0.55*sal[i]+0.85*local+0.55*importance[i]; } rewrite_cost=0.10*r.steps/3.0;
    } else if(method=="step_boundary_rewrite"){
        for(int i=0;i<total;i++){ double delimiter_ok=1.0-r.delimiter_noise + r.delimiter_noise*U(rng); score[i]=0.52*sal[i]+1.05*importance[i]*delimiter_ok+0.65*recurrence[i]; } rewrite_cost=0.055*r.steps;
    } else if(method=="attention_reconsolidate"){
        for(int i=0;i<total;i++){ bool maybe_needed=needed.count(i) || U(rng)<0.08+r.distractor_rate; score[i]=0.45*sal[i]+0.75*importance[i]+(maybe_needed?1.05:0.0)+0.45*recurrence[i]; } rewrite_cost=0.08*r.steps;
    } else if(method=="oracle_step_rewrite"){
        for(int i=0;i<total;i++){ score[i]=0.35*sal[i]+0.35*importance[i]+(needed.count(i)?5.0:0.0)+0.5*recurrence[i]; } rewrite_cost=0.12*r.steps;
    }
    std::vector<int> kept=choose_top(score,r.budget); std::set<int> K(kept.begin(),kept.end());
    int have=0; for(int id:needed) if(K.count(id)) have++;
    retained_frac=(double)have/std::max(1,(int)needed.size());
    double success=std::pow(retained_frac, 0.85) * (1.0 - 0.08*r.delimiter_noise);
    if(retained_frac<0.999 && r.name=="strict_chain") success*=0.25;
    return clamp(success,0,1);
}
static void add(Row&a,double success,double retained,double cost){a.success+=success; a.retained+=retained; a.rewrite_cost+=cost; a.utility+=success-0.015*cost; a.n++;}

int main(int argc,char**argv){
    std::string out="artifacts/probe-results/REV0023_PERIODIC_CACHE_REWRITE_SMOKE.json"; if(argc>1) out=argv[1]; auto t0=std::chrono::high_resolution_clock::now();
    std::vector<Regime> regimes={
        {"strict_chain", 10, 14, 28, 5, 0.08, 0.20, 0.08},
        {"early_premise_late_use", 12, 12, 26, 4, 0.04, 0.35, 0.05},
        {"noisy_delimiters", 10, 12, 24, 4, 0.42, 0.35, 0.10},
        {"recurrent_definition", 14, 10, 26, 5, 0.10, 0.25, 0.25},
        {"mostly_local", 8, 16, 30, 3, 0.12, 0.15, 0.03}
    };
    std::vector<std::string> methods={"continuous_eviction","fixed_periodic_rewrite","step_boundary_rewrite","attention_reconsolidate","oracle_step_rewrite"};
    std::map<std::string,Row> rows; std::map<std::string,int> winners, nonoracle;
    for(const auto&r:regimes) for(int seed=0; seed<96; ++seed){ double best=-1e9,bestno=-1e9; std::string win,winno; for(const auto&m:methods){ double retained=0,cost=0; double succ=run_once(r,m,2000+seed*41,retained,cost); std::string key=r.name+"|"+m+"|"+std::to_string(r.budget); if(!rows.count(key)){ rows[key].regime=r.name; rows[key].method=m; rows[key].budget=r.budget; rows[key].facts=r.steps*r.facts_per_step; rows[key].hops=r.query_hops; } add(rows[key],succ,retained,cost); double util=succ-0.015*cost; if(util>best){best=util;win=m;} if(m.find("oracle")==std::string::npos && util>bestno){bestno=util;winno=m;} } winners[win]++; nonoracle[winno]++; }
    double seconds=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count();
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"periodic_cache_rewrite\",\n  \"language\": \"c++17\",\n  \"is_paper_reproduction\": false,\n";
    f<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<seconds<<", \"primary_metric\": {\"name\": \"mean_utility\", \"direction\": \"higher_is_better\", \"winner_field\": \"winner_counts_excluding_oracle\"}, \"winner_counts\": {";
    bool first=true; for(auto&kv:winners){ if(!first) f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second; }
    f<<"}, \"winner_counts_excluding_oracle\": {"; first=true; for(auto&kv:nonoracle){ if(!first) f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second; }
    f<<"}, \"interpretation\": \"Tests whether rewrite clocks aligned with reasoning steps preserve chain state better than continuous eviction.\"},\n  \"rows\": [\n";
    int c=0; for(auto&kv: rows){ const Row&r=kv.second; double n=std::max(1,r.n); if(c++) f<<",\n"; f<<"    {\"regime\": \""<<esc(r.regime)<<"\", \"method\": \""<<esc(r.method)<<"\", \"budget\": "<<r.budget<<", \"facts\": "<<r.facts<<", \"hops\": "<<r.hops<<", \"mean_success\": "<<r.success/n<<", \"mean_needed_retained\": "<<r.retained/n<<", \"mean_rewrite_cost\": "<<r.rewrite_cost/n<<", \"mean_utility\": "<<r.utility/n<<"}"; }
    f<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
