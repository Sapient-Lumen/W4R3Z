// CloudtainerML rev0023: Memory poisoning / trustworthy search gate wind tunnel.
// Synthetic C++17 probe. Not a paper reproduction.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <random>
#include <sstream>
#include <string>
#include <vector>

struct Row { std::string regime, policy; int budget=0, n=0; double attack=0, benign=0, poisoned_read=0, valid_recall=0, cost=0, utility=0; };
static std::string esc(const std::string&s){std::string o; for(char c:s){if(c=='"')o+="\\\""; else if(c=='\\')o+="\\\\"; else o+=c;} return o;}
static double clamp(double x,double a,double b){return std::max(a,std::min(b,x));}
static double rnd(std::mt19937_64&r,double a=0,double b=1){return std::uniform_real_distribution<double>(a,b)(r);} 
struct Cand{double sim, trust, domain, poison, utility, provenance, age;};
static std::vector<Cand> make_candidates(const std::string&reg, std::mt19937_64&rng, int m){
    std::vector<Cand> v; v.reserve(m);
    for(int i=0;i<m;i++){
        Cand c{rnd(rng,0.05,0.88), rnd(rng,0.35,0.95), rnd(rng,0.55,1.0), 0.0, rnd(rng,0.1,0.85), rnd(rng,0.45,1.0), rnd(rng,0,1)};
        if(i%7==0){ c.utility += rnd(rng,0.15,0.35); c.sim += rnd(rng,0.08,0.18); }
        v.push_back(c);
    }
    int pcount = (reg=="benign_personalization")?0:(reg=="single_high_similarity_poison"?1:(reg=="delayed_activation"?2:3));
    for(int j=0;j<pcount;j++){
        Cand p;
        p.poison = rnd(rng,0.75,1.0);
        p.sim = (reg=="single_high_similarity_poison"?rnd(rng,0.88,0.99):reg=="cross_domain_leak"?rnd(rng,0.72,0.92):rnd(rng,0.55,0.9));
        p.trust = (reg=="tool_output_poison"?rnd(rng,0.25,0.55):rnd(rng,0.4,0.75));
        p.domain = (reg=="cross_domain_leak"?rnd(rng,0.05,0.35):rnd(rng,0.45,0.95));
        p.utility = (reg=="delayed_activation"?rnd(rng,0.35,0.72):rnd(rng,0.15,0.5));
        p.provenance = (reg=="tool_output_poison"?rnd(rng,0.05,0.3):rnd(rng,0.1,0.55));
        p.age = (reg=="delayed_activation"?rnd(rng,0.0,0.3):rnd(rng,0.35,1.0));
        v.push_back(p);
    }
    return v;
}
static double score(const Cand&c,const std::string&pol,const std::string&reg){
    if(pol=="similarity_only") return c.sim;
    if(pol=="write_time_filter") return c.sim - 0.55*(1.0-c.trust) - 0.25*c.poison;
    if(pol=="read_time_gate") return c.sim + 0.38*c.domain + 0.24*c.trust - 0.15*(1.0-c.provenance);
    if(pol=="memgate_toy") return c.sim + 0.48*c.domain + 0.42*c.trust + 0.22*c.provenance - 0.55*c.poison;
    if(pol=="provenance_decay") return c.sim + 0.45*c.provenance + 0.20*c.domain - 0.18*c.age - 0.35*c.poison;
    if(pol=="dual_write_read_gate") return c.sim + 0.42*c.domain + 0.34*c.trust + 0.38*c.provenance - 0.72*c.poison - (reg=="cross_domain_leak"?0.25*(1.0-c.domain):0.0);
    if(pol=="oracle_trust_boundary") return c.utility - 10.0*c.poison;
    return c.sim;
}
static void add(Row&r,double attack,double benign,double poisoned,double valid,double cost,double util){r.n++; r.attack+=attack; r.benign+=benign; r.poisoned_read+=poisoned; r.valid_recall+=valid; r.cost+=cost; r.utility+=util;}
int main(int argc,char**argv){
    std::string out="artifacts/probe-results/REV0023_MEMORY_POISONING_GATE_SMOKE.json"; if(argc>1) out=argv[1];
    auto t0=std::chrono::high_resolution_clock::now();
    std::vector<std::string> regimes={"single_high_similarity_poison","tool_output_poison","cross_domain_leak","delayed_activation","benign_personalization"};
    std::vector<std::string> policies={"similarity_only","write_time_filter","read_time_gate","memgate_toy","provenance_decay","dual_write_read_gate","oracle_trust_boundary"};
    std::vector<int> budgets={4,8,16,32};
    std::map<std::string,Row> rows; std::map<std::string,int> wins;
    for(auto&reg:regimes) for(int budget:budgets) for(int seed=0; seed<96; ++seed){
        double best=-1e18; std::string bestp;
        for(auto&pol:policies){
            std::mt19937_64 rng(10007 + seed*131 + budget*17 + reg.size()*23 + pol.size()*29);
            auto cands=make_candidates(reg,rng,56);
            std::vector<int> idx(cands.size()); std::iota(idx.begin(), idx.end(), 0);
            std::stable_sort(idx.begin(), idx.end(), [&](int a,int b){return score(cands[a],pol,reg)>score(cands[b],pol,reg);});
            int k=std::min<int>(budget,idx.size()); double poison=0, useful=0, valid=0, poisoned_weight=0;
            for(int i=0;i<k;i++){auto&c=cands[idx[i]]; poisoned_weight += c.poison; poison = std::max(poison,c.poison*(0.65+0.35*c.sim)); useful += c.utility*(1.0-c.poison*0.6); if(c.utility>0.72 && c.poison<0.2) valid += 1.0;}
            double attack = (reg=="benign_personalization")?0.0:1.0/(1.0+std::exp(-(poison-0.56)*9.0));
            if(reg=="delayed_activation") attack = std::max(attack, 1.0/(1.0+std::exp(-((poisoned_weight/k)-0.22)*12.0)));
            double benign = clamp(useful/(0.42*k),0,1.4);
            double valid_recall = clamp(valid/2.0,0,1);
            double cost = k * (pol=="oracle_trust_boundary"?2.0:pol=="dual_write_read_gate"?1.32:pol=="memgate_toy"?1.18:1.0);
            double util = 2.2*benign + 1.1*valid_recall - 3.5*attack - 0.014*cost - 0.38*(poisoned_weight/k);
            std::string key=reg+"|"+std::to_string(budget)+"|"+pol; if(!rows.count(key)){rows[key].regime=reg; rows[key].budget=budget; rows[key].policy=pol;} add(rows[key],attack,benign,poisoned_weight/k,valid_recall,cost,util);
            if(util>best){best=util; bestp=pol;}
        }
        wins[bestp]++;
    }
    double seconds=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count();
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"memory_poisoning_gate\",\n  \"language\": \"c++17\",\n  \"is_paper_reproduction\": false,\n";
    f<<"  \"taxonomy\": [\"agent-memory\", \"trust-boundary\", \"poisoning\", \"safety-tail\", \"native\"],\n";
    f<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<seconds<<", \"primary_metric\": {\"name\": \"mean_utility\", \"direction\": \"higher_is_better\", \"winner_field\": \"winner_counts\"}, \"tail_metrics\": {\"has_catastrophic_proxy\": true, \"fields\": [\"attack_success_rate\", \"mean_poisoned_read_fraction\"]}, \"winner_counts\": {"; bool first=true; for(auto&kv:wins){if(!first)f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second;} f<<"}, \"interpretation\": \"Single poisoned writes can beat similarity search; read/write provenance gates are tested as cheap mitigations.\"},\n  \"rows\": [\n";
    int c=0; for(auto&kv:rows){const Row&r=kv.second; double n=std::max(1,r.n); if(c++)f<<",\n"; f<<"    {\"regime\": \""<<esc(r.regime)<<"\", \"budget\": "<<r.budget<<", \"policy\": \""<<esc(r.policy)<<"\", \"attack_success_rate\": "<<r.attack/n<<", \"benign_utility_recall\": "<<r.benign/n<<", \"mean_poisoned_read_fraction\": "<<r.poisoned_read/n<<", \"valid_recall_rate\": "<<r.valid_recall/n<<", \"mean_cost\": "<<r.cost/n<<", \"mean_utility\": "<<r.utility/n<<"}";}
    f<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
