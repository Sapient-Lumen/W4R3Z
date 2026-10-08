// CloudtainerML rev0024: native subspace-aware MoE router toy inspired by STAR / MoE routing testbeds.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <string>
#include <vector>
static std::string q(const std::string& s){ return "\"" + s + "\""; }
struct Regime{std::string name; double separability, overlap, noise, shift, rare, load_pressure;};
struct Method{std::string name; double structure, adaptation, balance, exploration, router_cost;};
struct Row{std::string regime, method; int experts; double task_error, imbalance, instability, dispatch_cost, score;};
int main(int argc,char**argv){
    std::string out=argc>1?argv[1]:"REV0024_SUBSPACE_MOE_ROUTER_SMOKE.json";
    std::vector<Regime> regimes={{"clean_domain_clusters",0.92,0.08,0.10,0.05,0.05,0.30},{"overlapping_domains",0.45,0.72,0.22,0.10,0.12,0.50},{"high_dimensional_noise",0.62,0.35,0.82,0.12,0.08,0.40},{"streaming_distribution_shift",0.70,0.25,0.28,0.88,0.15,0.55},{"rare_domain_needles",0.78,0.18,0.25,0.20,0.86,0.72},{"load_balancing_trap",0.60,0.32,0.30,0.18,0.22,0.95}};
    std::vector<Method> methods={{"uniform_balanced_router",0.05,0.00,0.95,0.80,0.08},{"shallow_linear_router",0.38,0.08,0.35,0.20,0.05},{"aux_loss_balanced_router",0.32,0.12,0.82,0.38,0.08},{"subspace_router_static",0.70,0.18,0.52,0.35,0.12},{"star_style_online_subspace",0.82,0.70,0.60,0.55,0.16},{"star_plus_rare_explorer",0.76,0.64,0.70,0.88,0.21},{"oracle_domain_router",1.00,1.00,0.88,1.00,0.28}};
    std::vector<int> expert_counts={4,8,16,32,64};
    std::vector<Row> rows;
    for(auto& rg: regimes){ for(int E: expert_counts){ double cap=std::log2((double)E)/6.0; for(auto& m: methods){
        double specialization = rg.separability*(0.20+0.72*m.structure)*std::min(1.0,0.75+cap);
        double overlap_penalty = rg.overlap*(0.28+0.42*m.structure)*(1.0-0.35*m.balance);
        double noise_penalty = rg.noise*(0.35*(1.0-m.structure)+0.18*m.router_cost);
        double shift_penalty = rg.shift*(0.55*(1.0-m.adaptation)+0.16*(1.0-m.exploration));
        double rare_penalty = rg.rare*(0.48*(1.0-m.exploration)+0.20*(1.0-m.balance));
        double imbalance = std::max(0.0,std::min(1.0, rg.load_pressure*(1.0-m.balance)*(0.65+0.08*std::log2((double)E)) + 0.10*(1.0-m.exploration)));
        double instability = std::max(0.0,std::min(1.0, rg.shift*(0.65*(1.0-m.adaptation)+0.15*m.structure) + rg.noise*(0.22+0.10*m.exploration)));
        double task_error = std::max(0.01, 1.02 - specialization + overlap_penalty + noise_penalty + shift_penalty + rare_penalty + 0.20*imbalance);
        if(m.name=="oracle_domain_router") task_error=std::max(0.005, task_error*0.48 - 0.05*rg.separability);
        double dispatch_cost = (1.0 + m.router_cost*2.0) * std::log2((double)E+1.0);
        double score = task_error + 0.18*imbalance + 0.12*instability + 0.012*dispatch_cost;
        rows.push_back({rg.name,m.name,E,task_error,imbalance,instability,dispatch_cost,score});
    } } }
    std::map<std::string,int> winners, nonoracle; size_t idx=0; for(auto& rg: regimes){(void)rg; for(int E: expert_counts){(void)E; const Row* best=nullptr; const Row* bestNo=nullptr; for(size_t j=0;j<methods.size();++j){ const Row&r=rows[idx++]; if(!best||r.score<best->score) best=&r; if(r.method!="oracle_domain_router"&&(!bestNo||r.score<bestNo->score)) bestNo=&r;} if(best) winners[best->method]++; if(bestNo) nonoracle[bestNo->method]++;}}
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0024\",\n  \"probe\": \"subspace_moe_router\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {";
    bool first=true; for(auto&kv:winners){ if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){ if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;}
    f<<"},\n    \"interpretation\": \"Subspace-aware routing is useful in clean and shifted structure regimes, but rare-domain and load-balancing traps need explicit exploration/balance rather than pure principal-subspace tracking.\"\n  },\n  \"rows\": [\n";
    for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"experts\": "<<r.experts<<", \"task_error\": "<<r.task_error<<", \"imbalance\": "<<r.imbalance<<", \"instability\": "<<r.instability<<", \"dispatch_cost\": "<<r.dispatch_cost<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
    f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
