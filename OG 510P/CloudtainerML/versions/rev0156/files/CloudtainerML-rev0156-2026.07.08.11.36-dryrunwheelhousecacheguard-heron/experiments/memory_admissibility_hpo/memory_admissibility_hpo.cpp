// CloudtainerML rev0023: Memory admissibility/HPO gate phase diagram.
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
#include <sstream>
#include <string>
#include <vector>

struct Mem { double sim=0, trust=0, domain=0, provenance=0, correction=0, poison=0, utility=0, age=0, authority=0; };
struct Row { std::string regime, policy; int budget=0, n=0; double attack=0, recall=0, false_reject=0, poisoned=0, cost=0, utility=0, cat=0; };
static std::string esc(const std::string&s){std::string o; for(char c:s){if(c=='"')o+="\\\""; else if(c=='\\')o+="\\\\"; else o+=c;} return o;}
static double clamp(double x,double lo,double hi){return std::max(lo,std::min(hi,x));}
static double rnd(std::mt19937_64&r,double a=0,double b=1){return std::uniform_real_distribution<double>(a,b)(r);} 

static std::vector<Mem> make_memories(const std::string&reg, std::mt19937_64&rng, int m){
    std::vector<Mem> v; v.reserve(m+8);
    for(int i=0;i<m;i++){
        Mem c; c.sim=rnd(rng,0.04,0.86); c.trust=rnd(rng,0.45,0.95); c.domain=rnd(rng,0.45,1.0); c.provenance=rnd(rng,0.35,0.98); c.correction=rnd(rng,0.0,0.35); c.poison=0; c.utility=rnd(rng,0.06,0.84); c.age=rnd(rng,0.0,1.0); c.authority=rnd(rng,0.35,0.98);
        if(i%11==0){ c.utility+=rnd(rng,0.25,0.45); c.provenance+=0.04; }
        v.push_back(c);
    }
    int pcount = (reg=="benign")?0:(reg=="single_sleeper"?1:(reg=="cross_domain"?3:4));
    for(int j=0;j<pcount;j++){
        Mem p; p.poison=rnd(rng,0.70,1.0); p.sim=rnd(rng, reg=="single_sleeper"?0.86:0.62, 0.99); p.utility=rnd(rng,0.15,0.60); p.age=rnd(rng, reg=="stale_correction"?0.78:0.1, 1.0); p.authority=rnd(rng,0.1,0.65);
        p.trust = (reg=="tool_claim"?rnd(rng,0.25,0.55):rnd(rng,0.35,0.76));
        p.domain = (reg=="cross_domain"?rnd(rng,0.05,0.34):rnd(rng,0.52,0.96));
        p.provenance = (reg=="unsourced_belief"?rnd(rng,0.02,0.28):rnd(rng,0.12,0.54));
        p.correction = (reg=="stale_correction"?rnd(rng,0.70,1.0):rnd(rng,0.0,0.18));
        v.push_back(p);
    }
    if(reg=="stale_correction"){
        for(int j=0;j<3;j++){ Mem c; c.sim=rnd(rng,0.45,0.78); c.trust=rnd(rng,0.72,0.98); c.domain=rnd(rng,0.6,1); c.provenance=rnd(rng,0.75,1); c.correction=rnd(rng,0.75,1); c.poison=0; c.utility=rnd(rng,0.55,0.95); c.age=rnd(rng,0.0,0.4); c.authority=rnd(rng,0.70,1); v.push_back(c); }
    }
    return v;
}

static double score(const Mem&m,const std::string&pol,double tau,double lambda){
    if(pol=="similarity_only") return m.sim;
    if(pol=="static_memgate") return m.sim + 0.52*m.domain + 0.36*m.trust + 0.28*m.provenance - 0.65*m.poison;
    if(pol=="admissibility_contract") return m.sim + 0.62*m.domain + 0.55*m.trust + 0.48*m.provenance + 0.30*m.authority + 0.42*m.correction - 1.00*m.poison - 0.25*m.age;
    if(pol=="hpo_threshold_gate") return m.sim + tau*m.domain + 0.55*m.trust + lambda*m.provenance + 0.35*m.correction - 0.85*m.poison - 0.18*m.age;
    if(pol=="conservative_contract") return m.sim + 0.50*m.domain + 0.70*m.trust + 0.82*m.provenance + 0.62*m.correction - 1.25*m.poison - 0.35*(1.0-m.authority);
    if(pol=="oracle_boundary") return m.utility - 12.0*m.poison + 1.5*m.correction;
    return m.sim;
}

static void add(Row&r,double a,double rec,double fr,double p,double cost,double u,double cat){r.n++; r.attack+=a; r.recall+=rec; r.false_reject+=fr; r.poisoned+=p; r.cost+=cost; r.utility+=u; r.cat+=cat;}
int main(int argc,char**argv){
    std::string out="artifacts/probe-results/REV0023_MEMORY_ADMISSIBILITY_HPO_SMOKE.json"; if(argc>1) out=argv[1];
    auto t0=std::chrono::high_resolution_clock::now();
    std::vector<std::string> regimes={"single_sleeper","cross_domain","stale_correction","tool_claim","unsourced_belief","benign"};
    std::vector<std::string> policies={"similarity_only","static_memgate","admissibility_contract","hpo_threshold_gate","conservative_contract","oracle_boundary"};
    std::vector<int> budgets={4,8,16,32};
    std::vector<double> taus={0.15,0.35,0.55,0.75,0.95};
    std::vector<double> lambdas={0.15,0.35,0.60,0.85};
    std::map<std::string,Row> rows; std::map<std::string,int>wins;
    for(auto&reg:regimes) for(int budget:budgets) for(int seed=0; seed<80; ++seed){
        double best=-1e18; std::string bp;
        for(auto&pol:policies){
            double local_best=-1e18; Row local; std::string best_label=pol;
            for(double tau: (pol=="hpo_threshold_gate"?taus:std::vector<double>{0.5})) for(double lambda:(pol=="hpo_threshold_gate"?lambdas:std::vector<double>{0.5})){
                std::mt19937_64 rng(120020 + seed*137 + budget*31 + reg.size()*17 + pol.size()*19 + int(tau*100)*7 + int(lambda*100)*5);
                auto mem=make_memories(reg,rng,58);
                std::vector<int> idx(mem.size()); std::iota(idx.begin(),idx.end(),0);
                std::stable_sort(idx.begin(),idx.end(),[&](int a,int b){return score(mem[a],pol,tau,lambda)>score(mem[b],pol,tau,lambda);});
                int k=std::min<int>(budget,idx.size()); double poison=0, poison_mean=0, recall=0, rejected_valid=0, valid_total=0, cost=0;
                for(auto&m:mem) if(m.utility>0.74 && m.poison<0.15) valid_total++;
                for(int i=0;i<k;i++){auto&m=mem[idx[i]]; poison=std::max(poison,m.poison*(0.65+0.35*m.sim)); poison_mean+=m.poison; if(m.utility>0.74 && m.poison<0.15) recall++; cost += (pol=="oracle_boundary"?2.2:pol=="conservative_contract"?1.55:pol=="hpo_threshold_gate"?1.38:1.0);}
                for(auto&m:mem) if(m.utility>0.74 && m.poison<0.15){ bool kept=false; for(int i=0;i<k;i++) if(&m==&mem[idx[i]]) kept=true; if(!kept) rejected_valid++; }
                double attack=(reg=="benign")?0.0:1.0/(1.0+std::exp(-(poison-0.54)*11.0));
                if(reg=="single_sleeper") attack=std::max(attack, 1.0/(1.0+std::exp(-((poison_mean/k)-0.11)*18.0)));
                double rec=clamp(recall/std::max(1.0,valid_total),0,1); double fr=clamp(rejected_valid/std::max(1.0,valid_total),0,1);
                double cat=(attack>0.55 && rec<0.45)?1.0:0.0;
                double util=2.6*rec - 4.1*attack - 0.85*fr - 0.01*cost - 0.45*(poison_mean/k);
                if(reg=="benign") util += 0.9*rec - 0.4*fr;
                if(util>local_best){ local_best=util; local=Row{reg,pol,budget,1,attack,rec,fr,poison_mean/k,cost,util,cat}; if(pol=="hpo_threshold_gate"){std::ostringstream ss; ss<<pol<<"(tau="<<std::setprecision(2)<<tau<<",lambda="<<lambda<<")"; best_label=ss.str();}}
            }
            std::string key=reg+"|"+std::to_string(budget)+"|"+pol; if(!rows.count(key)){rows[key].regime=reg; rows[key].budget=budget; rows[key].policy=pol;} add(rows[key],local.attack,local.recall,local.false_reject,local.poisoned,local.cost,local.utility,local.cat);
            if(local.utility>best){best=local.utility; bp=best_label;}
        }
        wins[bp]++;
    }
    double seconds=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count();
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"memory_admissibility_hpo\",\n  \"language\": \"c++17\",\n  \"is_paper_reproduction\": false,\n";
    f<<"  \"taxonomy\": [\"agent-memory\", \"trust-boundary\", \"admissibility\", \"poisoning\", \"native\"],\n";
    f<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<seconds<<", \"primary_metric\": {\"name\": \"mean_utility\", \"direction\": \"higher_is_better\", \"winner_field\": \"winner_counts\"}, \"tail_metrics\": {\"has_catastrophic_proxy\": true, \"fields\": [\"attack_success_rate\", \"catastrophic_contract_failure_rate\", \"mean_poisoned_read_fraction\"]}, \"winner_counts\": {";
    bool first=true; for(auto&kv:wins){if(!first) f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second;} f<<"}, \"interpretation\": \"A tiny HPO-style admissibility sweep asks whether trust/provenance gates reduce poisoning without deleting useful memories.\"},\n  \"rows\": [\n";
    int c=0; for(auto&kv:rows){auto&r=kv.second; double n=std::max(1,r.n); if(c++) f<<",\n"; f<<"    {\"regime\": \""<<esc(r.regime)<<"\", \"budget\": "<<r.budget<<", \"policy\": \""<<esc(r.policy)<<"\", \"attack_success_rate\": "<<r.attack/n<<", \"valid_recall_rate\": "<<r.recall/n<<", \"false_reject_rate\": "<<r.false_reject/n<<", \"mean_poisoned_read_fraction\": "<<r.poisoned/n<<", \"mean_cost\": "<<r.cost/n<<", \"mean_utility\": "<<r.utility/n<<", \"catastrophic_contract_failure_rate\": "<<r.cat/n<<"}"; }
    f<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
