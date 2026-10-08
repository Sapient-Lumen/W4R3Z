// CloudtainerML rev0023: persistent-memory provenance phase sweep.
// C++17 synthetic red-team for the memory-sycophancy lane. It hardens the earlier
// trap by sweeping misbelief rate, correction retention, and high-stakes rate.

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

struct Row { std::string regime, policy; double misbelief=0, correction_loss=0, highstakes=0, accuracy=0, sycophancy=0, abstain=0, utility=0; int n=0; };
static std::string esc(const std::string&s){std::string o;for(char c:s){if(c=='"')o+="\\\"";else if(c=='\\')o+="\\\\";else o+=c;}return o;}
static double clamp(double x,double lo,double hi){return std::max(lo,std::min(hi,x));}

struct Phase { std::string regime; double misbelief, correction_loss, highstakes, ambiguity; };
struct Outcome { double acc=0, syc=0, abst=0, util=0; };

static Outcome run_policy(const Phase& ph,const std::string& policy,int seed){
    std::mt19937_64 rng(seed); std::uniform_real_distribution<double> U(0,1); std::normal_distribution<double> N(0,1);
    int trials=256, correct=0, syco=0, abst=0;
    for(int i=0;i<trials;i++){
        bool user_misbelief=U(rng)<ph.misbelief;
        bool correction_stored=U(rng)<(1.0-ph.correction_loss);
        bool high=U(rng)<ph.highstakes;
        bool ambiguous=U(rng)<ph.ambiguity;
        bool answer=false, abstain=false;
        if(policy=="no_persistent_memory"){
            double base=0.78 - 0.10*ambiguous - 0.04*high;
            answer=U(rng)<base; abstain=!answer && high && U(rng)<0.25;
        } else if(policy=="belief_snippet_memory"){
            if(user_misbelief && !correction_stored){ answer=false; }
            else answer=U(rng)<(0.90-0.08*ambiguous);
        } else if(policy=="recency_memory"){
            bool recency_overwrites_correction = user_misbelief && U(rng)<0.45;
            if(user_misbelief && (!correction_stored || recency_overwrites_correction)) answer=false; else answer=U(rng)<0.86;
        } else if(policy=="provenance_balanced_memory"){
            if(user_misbelief && !correction_stored){ abstain=high || U(rng)<0.45; answer=!abstain && U(rng)<0.55; }
            else answer=U(rng)<(0.92-0.04*ambiguous);
        } else if(policy=="skeptical_highstakes_memory"){
            if(high && user_misbelief && !correction_stored){ abstain=U(rng)<0.82; answer=false; }
            else if(user_misbelief && !correction_stored){ answer=U(rng)<0.58; }
            else answer=U(rng)<0.88;
        } else if(policy=="correction_linked_memory"){
            double linked_loss=0.35*ph.correction_loss; // stores correction and belief as paired evidence, not isolated snippets
            bool linked_correction=U(rng)<(1.0-linked_loss);
            if(user_misbelief && !linked_correction){ abstain=high && U(rng)<0.55; answer=!abstain && U(rng)<0.60; }
            else answer=U(rng)<0.91;
        } else if(policy=="oracle_provenance"){
            answer=true;
        }
        if(abstain) abst++;
        if(answer) correct++;
        if(user_misbelief && !answer && !abstain) syco++;
    }
    double acc=(double)correct/trials, s=(double)syco/trials, a=(double)abst/trials;
    double util=acc - (1.2+1.8*ph.highstakes)*s - 0.18*a;
    return {acc,s,a,util};
}
static void add(Row& r,const Outcome&o){r.accuracy+=o.acc;r.sycophancy+=o.syc;r.abstain+=o.abst;r.utility+=o.util;r.n++;}

int main(int argc,char**argv){
    std::string out="artifacts/probe-results/REV0023_MEMORY_PROVENANCE_PHASE_SMOKE.json"; if(argc>1) out=argv[1]; auto t0=std::chrono::high_resolution_clock::now();
    std::vector<Phase> phases;
    for(double m: {0.05,0.15,0.30,0.50}) for(double cl:{0.05,0.25,0.55,0.80}) for(double hs:{0.05,0.25,0.60}){
        std::string reg = hs>0.5?"highstakes":(m>0.35?"misbelief_heavy":(cl>0.5?"correction_lossy":"benign"));
        phases.push_back({reg,m,cl,hs,0.18+0.22*m});
    }
    std::vector<std::string> policies={"no_persistent_memory","belief_snippet_memory","recency_memory","provenance_balanced_memory","skeptical_highstakes_memory","correction_linked_memory","oracle_provenance"};
    std::map<std::string,Row> rows; std::map<std::string,int> winners, nonoracle;
    for(const auto&ph:phases){ for(int seed=0; seed<20; ++seed){ double best=-1e9,bestno=-1e9; std::string win,winno; for(const auto&p:policies){ Outcome o=run_policy(ph,p,7000+seed*67+(int)(100*ph.misbelief)); std::ostringstream key; key<<ph.regime<<"|"<<p<<"|"<<ph.misbelief<<"|"<<ph.correction_loss<<"|"<<ph.highstakes; std::string k=key.str(); if(!rows.count(k)){ rows[k].regime=ph.regime; rows[k].policy=p; rows[k].misbelief=ph.misbelief; rows[k].correction_loss=ph.correction_loss; rows[k].highstakes=ph.highstakes; } add(rows[k],o); if(o.util>best){best=o.util;win=p;} if(p.find("oracle")==std::string::npos && o.util>bestno){bestno=o.util;winno=p;} } winners[win]++; nonoracle[winno]++; } }
    double seconds=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count();
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"memory_provenance_phase\",\n  \"language\": \"c++17\",\n  \"is_paper_reproduction\": false,\n";
    f<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<seconds<<", \"primary_metric\": {\"name\": \"mean_utility\", \"direction\": \"higher_is_better\", \"winner_field\": \"winner_counts_excluding_oracle\"}, \"winner_counts\": {"; bool first=true; for(auto&kv:winners){ if(!first) f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second; }
    f<<"}, \"winner_counts_excluding_oracle\": {"; first=true; for(auto&kv:nonoracle){ if(!first) f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second; }
    f<<"}, \"interpretation\": \"Persistent memory needs provenance and correction linkage; otherwise belief snippets can underperform no memory.\"},\n  \"rows\": [\n";
    int c=0; for(auto&kv:rows){ const Row&r=kv.second; double n=std::max(1,r.n); if(c++) f<<",\n"; f<<"    {\"regime\": \""<<esc(r.regime)<<"\", \"policy\": \""<<esc(r.policy)<<"\", \"misbelief_rate\": "<<r.misbelief<<", \"correction_loss\": "<<r.correction_loss<<", \"highstakes_rate\": "<<r.highstakes<<", \"mean_accuracy\": "<<r.accuracy/n<<", \"mean_sycophancy\": "<<r.sycophancy/n<<", \"mean_abstain\": "<<r.abstain/n<<", \"mean_utility\": "<<r.utility/n<<"}"; }
    f<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
