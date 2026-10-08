// CloudtainerML rev0016: VeriCache-style guard wind tunnel.
// Toy C++17 simulator for lossy KV divergence during long decode plus selective
// verification/recompute. Not a paper reproduction. It asks whether a cheap
// guard can turn lossy cache behavior into effectively lossless behavior only on
// risky steps such as low-margin choices, accumulated drift, and tool-call sites.

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
#include <sstream>
#include <string>
#include <vector>

struct Row { std::string scenario, method; int steps=0; double compression=0, verify_cost=0, accuracy=0, catastrophic=0, recompute_frac=0, utility=0; int n=0; };
static double clamp(double x,double lo,double hi){ return std::max(lo,std::min(hi,x)); }
static double logistic(double x){ return 1.0/(1.0+std::exp(-x)); }
static std::string esc(const std::string& s){ std::string o; for(char c:s){ if(c=='"') o+="\\\""; else if(c=='\\') o+="\\\\"; else o+=c; } return o; }
static double randn(std::mt19937_64& rng){ static thread_local std::normal_distribution<double> N(0,1); return N(rng); }

struct ScenarioCfg { std::string name; int steps; double base_margin; double ambiguity; double drift_rate; double critical_rate; double tool_bias; double compression; };
struct Outcome { double accuracy=0, catastrophic=0, recompute_frac=0, utility=0; };

static Outcome simulate(const ScenarioCfg& c, const std::string& method, int seed){
    std::mt19937_64 rng(seed);
    std::uniform_real_distribution<double> U(0,1);
    int wrong=0, catastrophic=0, recompute=0;
    double drift=0.0;
    int critical_seen=0;
    for(int t=1; t<=c.steps; ++t){
        bool critical = U(rng) < c.critical_rate || (c.tool_bias>0 && (t % std::max(7,(int)std::round(22.0/c.tool_bias)) == 0));
        if(critical) critical_seen++;
        double local_margin = clamp(c.base_margin + 0.55*std::sin(0.13*t+0.17*seed) + 0.35*randn(rng)*c.ambiguity - (critical?0.28:0.0), 0.03, 2.5);
        double quant_noise = c.compression * (0.42 + 0.024*std::sqrt((double)t) + 0.55*drift) * (0.65 + 0.45*std::abs(randn(rng)));
        double p_wrong = logistic(2.0*(quant_noise - local_margin));
        bool verify=false;
        if(method=="full_kv") verify=true;
        else if(method=="lossy_no_guard") verify=false;
        else if(method=="periodic_refresh") verify=(t%32==0 || critical && t%16==0);
        else if(method=="margin_guard") verify=(local_margin < 0.42 || drift > 2.0);
        else if(method=="drift_guard") verify=(drift > 1.6);
        else if(method=="vericache_toy_guard") verify=(local_margin < 0.50 || drift > 1.25 || critical);
        else if(method=="oracle_risk_guard") verify=(quant_noise > 0.75*local_margin || critical);
        if(verify){ recompute++; drift *= 0.18; p_wrong *= 0.02; }
        bool is_wrong = U(rng) < p_wrong;
        if(is_wrong){ wrong++; drift += critical ? 0.85 : 0.32; if(critical) catastrophic++; }
        else { drift = 0.985*drift + 0.015*c.compression; }
    }
    double acc = 1.0 - (double)wrong/std::max(1,c.steps);
    double cat = critical_seen? (double)catastrophic/critical_seen : 0.0;
    double rf = (double)recompute/std::max(1,c.steps);
    // Small cost for recompute, high penalty for catastrophic divergence.
    double utility = acc - 2.4*cat - 0.16*rf;
    if(method=="full_kv") utility -= 0.18; // exact but expensive resident cache anchor
    return {acc,cat,rf,utility};
}

static void add(Row& a,const Outcome& o){ a.accuracy+=o.accuracy; a.catastrophic+=o.catastrophic; a.recompute_frac+=o.recompute_frac; a.utility+=o.utility; a.n++; }

int main(int argc, char** argv){
    std::string out="artifacts/probe-results/REV0016_VERICACHE_GUARD_SMOKE.json"; if(argc>1) out=argv[1];
    auto t0=std::chrono::high_resolution_clock::now();
    std::vector<ScenarioCfg> scenarios={
        {"long_code_tool_calls", 384, 0.68, 1.00, 1.00, 0.055, 1.40, 1.00},
        {"smooth_story_decode", 512, 1.15, 0.45, 0.55, 0.012, 0.20, 0.85},
        {"low_margin_math", 320, 0.42, 1.25, 1.15, 0.040, 0.75, 1.10},
        {"rare_tool_needles", 640, 0.90, 0.75, 0.85, 0.018, 2.30, 0.95},
        {"aggressive_2bit_cache", 384, 0.62, 1.10, 1.45, 0.046, 1.00, 1.55}
    };
    std::vector<std::string> methods={"full_kv","lossy_no_guard","periodic_refresh","margin_guard","drift_guard","vericache_toy_guard","oracle_risk_guard"};
    std::map<std::string,Row> rows; std::map<std::string,int> winners, nonoracle_winners;
    for(const auto& sc: scenarios){
        for(int seed=0; seed<80; ++seed){
            double best=-1e9, best_no=-1e9; std::string win, win_no;
            for(const auto& m: methods){
                Outcome o=simulate(sc,m,9000+seed*37+(int)sc.steps);
                std::string key=sc.name+"|"+m;
                if(!rows.count(key)){ rows[key].scenario=sc.name; rows[key].method=m; rows[key].steps=sc.steps; rows[key].compression=sc.compression; }
                add(rows[key],o);
                if(o.utility>best){ best=o.utility; win=m; }
                if(m.find("oracle")==std::string::npos && o.utility>best_no){ best_no=o.utility; win_no=m; }
            }
            winners[win]++; nonoracle_winners[win_no]++;
        }
    }
    double seconds=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count();
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0016\",\n  \"probe\": \"vericache_guard\",\n";
    f<<"  \"language\": \"c++17\",\n  \"is_paper_reproduction\": false,\n";
    f<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<seconds<<", \"primary_metric\": {\"name\": \"mean_utility\", \"direction\": \"higher_is_better\", \"winner_field\": \"winner_counts_excluding_oracle\"}, \"winner_counts\": {";
    bool first=true; for(auto&kv:winners){ if(!first) f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second; }
    f<<"}, \"winner_counts_excluding_oracle\": {"; first=true; for(auto&kv:nonoracle_winners){ if(!first) f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second; }
    f<<"}, \"interpretation\": \"Toy guard makes lossy KV safer by spending exact recompute only on low-margin, drifted, or critical tool-call steps.\"},\n  \"rows\": [\n";
    int c=0; for(auto&kv: rows){ const Row&r=kv.second; double n=std::max(1,r.n); if(c++) f<<",\n"; f<<"    {\"scenario\": \""<<esc(r.scenario)<<"\", \"method\": \""<<esc(r.method)<<"\", \"steps\": "<<r.steps<<", \"compression\": "<<r.compression<<", \"mean_accuracy\": "<<r.accuracy/n<<", \"mean_catastrophic_rate\": "<<r.catastrophic/n<<", \"mean_recompute_frac\": "<<r.recompute_frac/n<<", \"mean_utility\": "<<r.utility/n<<"}"; }
    f<<"\n  ]\n}\n";
    std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n";
    return 0;
}
