// CloudtainerML rev0027 — MoE router Manifold Power Iteration wind tunnel.
// Native symbolic probe inspired by arXiv:2606.12397. Tests router/expert alignment, not real MoE training.
#include <bits/stdc++.h>
using namespace std;
static string q(const string&s){string o="\""; for(char c:s){ if(c=='"'||c=='\\') o+='\\'; o+=c;} return o+'"';}
struct Regime{string name; double singular_gap, token_alignment, rare_domain, drift, noise, load_pressure;};
struct Method{string name; double alignment, adapt, balance, rare, overhead, stability; bool oracle=false;};
struct Row{string regime, method; int experts; double top1, alignment, imbalance, tail_miss, overhead, stability_loss, score;};
int main(int argc,char**argv){
 string out=argc>1?argv[1]:"REV0027_MANIFOLD_POWER_ROUTER_SMOKE.json";
 vector<Regime> regimes={{"dominant_principal_direction",0.96,0.88,0.05,0.05,0.08,0.22},{"weak_singular_gap",0.28,0.65,0.12,0.08,0.18,0.24},{"rare_secondary_domain",0.74,0.70,0.88,0.08,0.14,0.42},{"router_distribution_drift",0.70,0.74,0.18,0.86,0.18,0.36},{"load_balance_pressure",0.80,0.72,0.25,0.18,0.16,0.92},{"noisy_lowrank_experts",0.55,0.60,0.18,0.22,0.54,0.34},{"multi_direction_experts",0.40,0.58,0.38,0.32,0.24,0.48}};
 vector<Method> methods={{"random_router",0.04,0.08,0.30,0.08,0.00,0.30,false},{"centroid_router",0.42,0.18,0.34,0.18,0.02,0.46,false},{"load_balanced_router",0.35,0.24,0.78,0.20,0.06,0.50,false},{"one_step_power_retract",0.70,0.42,0.42,0.24,0.08,0.82,false},{"mpi_two_step",0.82,0.58,0.46,0.30,0.12,0.78,false},{"mpi_balance_repair",0.76,0.62,0.82,0.54,0.16,0.74,false},{"stale_power_router",0.78,0.22,0.38,0.22,0.07,0.55,false},{"oracle_router",1.00,1.00,0.98,1.00,0.25,0.96,true}};
 vector<int> experts={4,8,16,32}; vector<Row> rows; map<string,int>winners, nonoracle;
 for(const auto&rg:regimes){ for(int E:experts){ vector<Row> cand; double e_bonus=min(1.0,log2((double)E)/5.0); for(const auto&m:methods){
   double align = min(1.0, max(0.0, 0.10 + 0.72*m.alignment*rg.singular_gap + 0.18*m.adapt*rg.token_alignment - 0.22*rg.noise*(1.0-m.stability)) );
   double drift_loss = rg.drift*(0.28*(1.0-m.adapt)+0.10*(1.0-m.stability));
   double rare_miss = max(0.0, rg.rare_domain*(0.58*(1.0-m.rare)+0.22*(1.0-m.balance)) - 0.04*e_bonus);
   double imbalance = max(0.0, min(1.0, rg.load_pressure*(0.75*(1.0-m.balance)+0.12*(1.0-e_bonus)) + 0.08*(1.0-m.stability)) );
   double top1 = max(0.0, min(1.0, 0.34 + 0.48*align + 0.10*m.balance + 0.08*e_bonus - rare_miss - drift_loss - 0.10*imbalance));
   if(m.oracle){ align=0.98; top1=min(0.995,0.92+0.04*e_bonus-0.04*rg.noise); rare_miss=0.02*rg.rare_domain; imbalance=0.05*rg.load_pressure; }
   double stability_loss=max(0.0,0.30*rg.noise*(1.0-m.stability)+0.16*rg.drift*(1.0-m.adapt));
   double score=(1.0-top1)+0.20*imbalance+0.18*rare_miss+0.08*m.overhead+0.10*stability_loss;
   cand.push_back({rg.name,m.name,E,top1,align,imbalance,rare_miss,m.overhead,stability_loss,score});
 }
 auto best=min_element(cand.begin(),cand.end(),[](const Row&a,const Row&b){return a.score<b.score;}); winners[best->method]++;
 auto bestNo=min_element(cand.begin(),cand.end(),[](const Row&a,const Row&b){ if(a.method=="oracle_router") return false; if(b.method=="oracle_router") return true; return a.score<b.score;}); nonoracle[bestNo->method]++; rows.insert(rows.end(),cand.begin(),cand.end()); }}
 ofstream f(out); f<<fixed<<setprecision(6);
 f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0027\",\n  \"probe\": \"manifold_power_router\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"MPI-style router alignment helps when expert matrices have a usable principal direction, but balance/rare-domain repair matters whenever top singular direction is not the whole expert identity.\",\n    \"screen_regret_fields\": [\"imbalance\", \"tail_miss\", \"overhead\", \"stability_loss\"]\n  },\n  \"rows\": [\n";
 for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"experts\": "<<r.experts<<", \"top1_assignment\": "<<r.top1<<", \"router_expert_alignment\": "<<r.alignment<<", \"imbalance\": "<<r.imbalance<<", \"tail_miss\": "<<r.tail_miss<<", \"overhead\": "<<r.overhead<<", \"stability_loss\": "<<r.stability_loss<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
 f<<"  ]\n}\n"; cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n";
}
