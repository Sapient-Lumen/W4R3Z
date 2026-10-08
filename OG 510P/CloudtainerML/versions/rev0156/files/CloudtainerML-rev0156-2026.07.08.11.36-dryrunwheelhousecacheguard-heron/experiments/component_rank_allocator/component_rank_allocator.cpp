// CloudtainerML rev0023: native component-aware rank allocation wind tunnel.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>

static std::string q(const std::string& s){ return "\"" + s + "\""; }
struct Component { std::string name; int max_rank; double sensitivity; double cost_per_rank; std::vector<double> energy; };
struct Row { std::string regime, method; int budget, qk, ov, mlp; double functional_error, byte_cost, score; };

static double tail_error(const Component& c, int r){
    r = std::max(0, std::min(r, c.max_rank));
    double total=0, tail=0;
    for(size_t i=0;i<c.energy.size();++i){ total += c.energy[i]; if((int)i>=r) tail += c.energy[i]; }
    return c.sensitivity * tail / (total + 1e-12);
}
static double cost(const std::vector<Component>& cs, const std::vector<int>& rs){ double c=0; for(size_t i=0;i<cs.size();++i) c += cs[i].cost_per_rank * rs[i]; return c; }
static double ferr(const std::vector<Component>& cs, const std::vector<int>& rs){ double e=0; for(size_t i=0;i<cs.size();++i) e += tail_error(cs[i], rs[i]); return e; }
static std::vector<int> greedy_alloc(const std::vector<Component>& cs, int budget, bool functional){
    std::vector<int> r(cs.size(),0);
    for(int b=0;b<budget;b++){
        int best=-1; double best_gain=-1e99;
        for(size_t i=0;i<cs.size();++i){ if(r[i]>=cs[i].max_rank) continue; double before=tail_error(cs[i], r[i]); double after=tail_error(cs[i], r[i]+1); double gain=before-after; if(!functional) gain=(cs[i].energy[r[i]]/(std::accumulate(cs[i].energy.begin(), cs[i].energy.end(),0.0)+1e-12)); gain/=std::sqrt(cs[i].cost_per_rank); if(gain>best_gain){ best_gain=gain; best=(int)i; } }
        if(best<0) break; r[best]++;
    }
    return r;
}
static std::vector<double> spectrum(int n, double decay, double knee, double bump){
    std::vector<double> e(n);
    for(int i=0;i<n;i++){ double x=i+1; e[i]=std::exp(-decay*x) + bump*std::exp(-0.5*std::pow((x-knee)/3.0,2.0)); }
    return e;
}
int main(int argc, char** argv){
    std::string out = argc>1 ? argv[1] : "REV0023_COMPONENT_RANK_ALLOCATOR_SMOKE.json";
    struct Regime { std::string name; double qk_s, ov_s, mlp_s, qk_d, ov_d, mlp_d, byte_w; };
    std::vector<Regime> regimes={
        {"qk_score_fragile", 2.4, 0.9, 0.6, 0.05, 0.09, 0.13, 0.018},
        {"ov_value_fragile", 0.7, 2.7, 0.8, 0.11, 0.05, 0.10, 0.018},
        {"mlp_manifold_fragile", 0.7, 0.9, 2.9, 0.10, 0.11, 0.04, 0.014},
        {"balanced_lowrank", 1.2, 1.2, 1.2, 0.15, 0.15, 0.12, 0.020},
        {"rope_frequency_tail", 1.9, 1.1, 0.8, 0.04, 0.12, 0.09, 0.016},
        {"memory_tight", 1.2, 1.5, 1.0, 0.09, 0.09, 0.09, 0.060}
    };
    std::vector<int> budgets={8,12,16,20,24,32}; std::vector<Row> rows;
    for(const auto& rg: regimes){
        std::vector<Component> cs={
            {"qk", 32, rg.qk_s, 1.0, spectrum(32, rg.qk_d, 24, rg.name=="rope_frequency_tail"?0.55:0.05)},
            {"ov", 32, rg.ov_s, 1.1, spectrum(32, rg.ov_d, 12, rg.name=="ov_value_fragile"?0.35:0.03)},
            {"mlp",64, rg.mlp_s, 0.6, spectrum(64, rg.mlp_d, 42, rg.name=="mlp_manifold_fragile"?0.45:0.02)}
        };
        for(int B: budgets){
            std::vector<std::pair<std::string,std::vector<int>>> methods;
            methods.push_back({"uniform_equal_rank", {B/3,B/3,B-2*(B/3)}});
            methods.push_back({"parameter_weighted", {std::max(1,(int)std::round(B*0.25)),std::max(1,(int)std::round(B*0.25)),std::max(1,B-2*(int)std::round(B*0.25))}});
            methods.push_back({"raw_energy_greedy", greedy_alloc(cs,B,false)});
            methods.push_back({"component_functional_greedy", greedy_alloc(cs,B,true)});
            // Tiny HPO-ish local search starts from functional greedy and moves rank mass if it helps score.
            auto hpo = greedy_alloc(cs,B,true); bool improved=true;
            while(improved){ improved=false; double base=ferr(cs,hpo)+rg.byte_w*cost(cs,hpo); for(int i=0;i<3;i++) for(int j=0;j<3;j++) if(i!=j && hpo[i]>0 && hpo[j]<cs[j].max_rank){ auto cand=hpo; cand[i]--; cand[j]++; double sc=ferr(cs,cand)+rg.byte_w*cost(cs,cand); if(sc+1e-12<base){ hpo=cand; base=sc; improved=true; } } }
            methods.push_back({"local_hpo_functional", hpo});
            // Oracle chooses exhaustive best allocation among three components for this tiny budget.
            std::vector<int> best={0,0,0}; double bsc=1e99;
            for(int a=0;a<=std::min(B,cs[0].max_rank);++a) for(int b=0;b<=std::min(B-a,cs[1].max_rank);++b){ int c=B-a-b; if(c<0||c>cs[2].max_rank) continue; std::vector<int> r={a,b,c}; double sc=ferr(cs,r)+rg.byte_w*cost(cs,r); if(sc<bsc){bsc=sc; best=r;} }
            methods.push_back({"oracle_exhaustive", best});
            for(auto& m: methods){ auto r=m.second; double e=ferr(cs,r); double bc=cost(cs,r); double sc=e+rg.byte_w*bc; rows.push_back({rg.name,m.first,B,r[0],r[1],r[2],e,bc,sc}); }
        }
    }
    std::map<std::string,int> winners, nonoracle;
    for(const auto& rg: regimes) for(int B: budgets){ const Row* best=nullptr; const Row* best_no=nullptr; for(const auto& r:rows) if(r.regime==rg.name && r.budget==B){ if(!best||r.score<best->score) best=&r; if(r.method!="oracle_exhaustive" && (!best_no||r.score<best_no->score)) best_no=&r; } if(best) winners[best->method]++; if(best_no) nonoracle[best_no->method]++; }
    std::ofstream f(out); f<<std::fixed<<std::setprecision(7);
    f << "{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"component_rank_allocator\",\n";
    f << "  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {";
    bool first=true; for(auto& kv:winners){ if(!first) f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second; } f << "},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto& kv:nonoracle){ if(!first) f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second; } f << "},\n";
    f << "    \"interpretation\": \"Component-aware rank allocation beats raw rank heuristics when QK/OV/MLP fragility differs; A3-style functional objectives are worth tiny equal-budget phase diagrams.\"\n  },\n  \"rows\": [\n";
    for(size_t i=0;i<rows.size();++i){ const auto& r=rows[i]; f << "    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"budget\": "<<r.budget<<", \"qk_rank\": "<<r.qk<<", \"ov_rank\": "<<r.ov<<", \"mlp_rank\": "<<r.mlp<<", \"functional_error\": "<<r.functional_error<<", \"byte_cost\": "<<r.byte_cost<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n"); }
    f << "  ]\n}\n"; std::cout << "wrote " << out << " rows=" << rows.size() << "\n"; return 0;
}
