// CloudtainerML rev0023: native tree-sparse feed-forward auto-pruning toy.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <string>
#include <vector>
static std::string q(const std::string& s){ return "\"" + s + "\""; }
struct Regime { std::string name; double skew, shift, rare, balance_need, asymmetry; };
struct Method { std::string name; double active_frac, route_quality, balance, prune, overhead; };
struct Row { std::string regime, method; int leaves; double active_frac, error, compute, dead_path_fraction, score; };
int main(int argc, char** argv){
    std::string out = argc>1 ? argv[1] : "REV0023_TREE_SPARSE_FFN_AUTOPRUNE_SMOKE.json";
    std::vector<Regime> regimes={{"stationary_zipf_experts",0.85,0.05,0.10,0.25,0.55},{"shifting_hot_paths",0.65,0.75,0.15,0.45,0.40},{"rare_skill_tokens",0.55,0.20,0.85,0.70,0.30},{"balanced_uniform_mix",0.10,0.10,0.10,0.90,0.05},{"asymmetric_activation_prunes",0.80,0.15,0.20,0.35,0.95},{"noisy_router_boundary",0.45,0.55,0.35,0.60,0.55}};
    std::vector<Method> methods={{"dense_ffn",1.00,1.00,1.00,0.00,1.00},{"flat_topk_router",0.12,0.72,0.60,0.15,0.18},{"hard_tree_route",0.05,0.66,0.45,0.30,0.08},{"tree_auto_prune",0.04,0.70,0.25,0.72,0.05},{"balanced_temperature_tree",0.07,0.70,0.88,0.18,0.10},{"oracle_adaptive_tree",0.05,0.95,0.82,0.30,0.12}};
    std::vector<int> leaves={64,128,256,512};
    std::vector<Row> rows;
    for(const auto& rg: regimes){ for(int L: leaves){ double logL=std::log2((double)L); for(const auto& m: methods){
        double specialization = rg.skew * (0.45 + 0.45*m.route_quality) + rg.balance_need * (0.20 + 0.50*m.balance);
        double shift_penalty = rg.shift * (0.40*m.prune + 0.20*(1.0-m.balance));
        double rare_penalty = rg.rare * (0.52*m.prune + 0.16*(1.0-m.route_quality));
        double dead_paths = std::max(0.0, std::min(0.95, rg.asymmetry*m.prune*(0.8+0.03*logL) - 0.35*m.balance));
        double capacity_gain = std::min(0.55, 0.08*logL) * (1.0 - 0.6*dead_paths) * m.route_quality;
        double error = std::max(0.015, 1.0 - specialization - capacity_gain + shift_penalty + rare_penalty + 0.25*dead_paths);
        if(m.name=="dense_ffn") { error = std::max(0.02, 0.42 + 0.10*rg.skew + 0.08*rg.shift - 0.015*logL); dead_paths=0.0; }
        if(m.name=="oracle_adaptive_tree") error = std::max(0.01, error*0.55 - 0.05*rg.skew);
        double compute = m.active_frac * L + m.overhead * std::log2((double)L);
        double score = error + 0.006*compute + 0.20*dead_paths;
        rows.push_back({rg.name,m.name,L,m.active_frac,error,compute,dead_paths,score});
    } } }
    std::map<std::string,int> winners, nonoracle; size_t idx=0; for(const auto& rg: regimes){ (void)rg; for(int L: leaves){ (void)L; const Row* best=nullptr; const Row* best_no=nullptr; for(size_t j=0;j<methods.size();++j){ const Row& r=rows[idx++]; if(!best||r.score<best->score) best=&r; if(r.method!="oracle_adaptive_tree"&&(!best_no||r.score<best_no->score)) best_no=&r;} if(best) winners[best->method]++; if(best_no) nonoracle[best_no->method]++; }}
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f << "{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"tree_sparse_ffn_autoprune\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {";
    bool first=true; for(auto& kv:winners){ if(!first) f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second; } f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto& kv:nonoracle){ if(!first) f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second; }
    f << "},\n    \"interpretation\": \"Tree-sparse FFNs are compelling when expert popularity is skewed, but rare skills and shifting hot paths expose auto-pruning as a performance risk unless balance pressure or repair is explicit.\"\n  },\n  \"rows\": [\n";
    for(size_t i=0;i<rows.size();++i){ auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"leaves\": "<<r.leaves<<", \"active_frac\": "<<r.active_frac<<", \"error\": "<<r.error<<", \"compute\": "<<r.compute<<", \"dead_path_fraction\": "<<r.dead_path_fraction<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n"); }
    f << "  ]\n}\n"; std::cout << "wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
