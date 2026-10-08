// CloudtainerML rev0028 — Probabilistic MoE subset-routing exploration wind tunnel.
// Inspired by ProbMoE/SIMPLE-style differentiable subset routing. Symbolic C++ probe only.
#include <bits/stdc++.h>
using namespace std; static string q(const string&s){string o="\""; for(char c:s){if(c=='"'||c=='\\')o+='\\'; o+=c;} return o+'"';}
struct Regime{string name; double margin, rare, complement, noise, load, drift;};
struct Method{string name; double exploit, explore, pairwise, balance, adapt, overhead; bool oracle=false;};
struct Row{string regime, method; int k; double expected_loss, rare_miss, subset_regret, load_violation, exploration_cost, score;};
int main(int argc,char**argv){string out=argc>1?argv[1]:"REV0028_PROBMOE_SUBSET_EXPLORATION_SMOKE.json";
 vector<Regime> regs={{"easy_high_margin",0.92,0.04,0.10,0.08,0.20,0.06},{"rare_expert_needed",0.62,0.88,0.20,0.18,0.42,0.10},{"complementary_pair",0.55,0.28,0.90,0.18,0.36,0.12},{"noisy_router_logits",0.42,0.20,0.28,0.82,0.28,0.18},{"load_pressure",0.60,0.30,0.34,0.20,0.94,0.15},{"distribution_drift",0.50,0.35,0.42,0.28,0.48,0.90}};
 vector<Method> ms={{"deterministic_topk",0.82,0.04,0.12,0.18,0.08,0.00,false},{"load_balanced_topk",0.62,0.10,0.18,0.78,0.12,0.04,false},{"dot_assignment_router",0.70,0.18,0.30,0.62,0.20,0.07,false},{"star_subspace_router",0.66,0.24,0.24,0.46,0.55,0.08,false},{"probmoe_simple",0.58,0.64,0.50,0.46,0.32,0.12,false},{"probmoe_annealed",0.68,0.58,0.64,0.52,0.50,0.15,false},{"probmoe_balance_repair",0.62,0.52,0.60,0.82,0.48,0.18,false},{"oracle_subset",1.00,1.00,1.00,1.00,1.00,0.25,true}};
 vector<int> ks={1,2,4}; vector<Row> rows; map<string,int>winners,nonoracle;
 for(auto&rg:regs)for(int k:ks){vector<Row> cand; double kbonus=log2(k+1)/2.6; for(auto&m:ms){
  double base=1.12-0.46*m.exploit*rg.margin-0.28*m.adapt*(1-rg.drift)-0.16*kbonus;
  double rare_miss=max(0.0,rg.rare*(0.70*(1-m.explore)+0.25*(1-m.balance))-0.10*kbonus);
  double pair_miss=max(0.0,rg.complement*(0.62*(1-m.pairwise)+0.16*(k<2)));
  double noise_pen=rg.noise*(0.22*(1-m.explore)+0.16*(1-m.adapt));
  double load_violation=max(0.0,rg.load*(0.60*(1-m.balance)+0.08*k)-0.05*m.explore);
  double drift_pen=rg.drift*(0.28*(1-m.adapt)+0.10*(1-m.explore));
  double loss=max(0.0,base+rare_miss+pair_miss+noise_pen+drift_pen);
  if(m.oracle){loss=0.08+0.03*rg.noise; rare_miss=0.02*rg.rare; pair_miss=0.02*rg.complement; load_violation=0.03*rg.load;}
  double exploration_cost=m.overhead+0.03*k;
  double subset_regret=rare_miss+pair_miss+0.5*drift_pen;
  double score=loss+0.22*load_violation+0.18*subset_regret+0.10*exploration_cost;
  cand.push_back({rg.name,m.name,k,loss,rare_miss,subset_regret,load_violation,exploration_cost,score});}
 auto best=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){return a.score<b.score;}); winners[best->method]++;
 auto bestNo=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){if(a.method=="oracle_subset")return false;if(b.method=="oracle_subset")return true;return a.score<b.score;}); nonoracle[bestNo->method]++; rows.insert(rows.end(),cand.begin(),cand.end());}
 ofstream f(out); f<<fixed<<setprecision(6); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0028\",\n  \"probe\": \"probmoe_subset_exploration\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Stochastic subset exploration is most useful in rare/complementary/noisy routing regimes; deterministic top-k remains hard to beat in high-margin cases.\",\n    \"screen_regret_fields\": [\"rare_miss\", \"subset_regret\", \"load_violation\", \"exploration_cost\"]\n  },\n  \"rows\": [\n";
 for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"k\": "<<r.k<<", \"expected_loss\": "<<r.expected_loss<<", \"rare_miss\": "<<r.rare_miss<<", \"subset_regret\": "<<r.subset_regret<<", \"load_violation\": "<<r.load_violation<<", \"exploration_cost\": "<<r.exploration_cost<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
 f<<"  ]\n}\n"; cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n";}
