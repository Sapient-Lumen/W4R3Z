// CloudtainerML rev0027 — Sparse/low-rank/hybrid attention frontier probe.
// Inspired by Sparse Frontier + Scatterbrain-style sparse/low-rank complementarity; symbolic native phase scan.
#include <bits/stdc++.h>
using namespace std; static string q(const string&s){string o="\"";for(char c:s){if(c=='"'||c=='\\')o+='\\';o+=c;}return o+'"';}
struct Regime{string name; double entropy, clusters, rare_needle, dense_background, hardware_penalty;};
struct Method{string name; double sparse, lowrank, hybrid, switcher, cost, tail_guard; bool oracle=false;};
struct Row{string regime,method,phase; double budget,error,tail,cost,wall_proxy,score;};
int main(int argc,char**argv){string out=argc>1?argv[1]:"REV0027_SPARSE_LOWRANK_HYBRID_FRONTIER_SMOKE.json";
 vector<Regime> regimes={{"low_entropy_needles",0.12,0.35,0.88,0.12,0.20},{"high_entropy_dense_mix",0.92,0.24,0.08,0.88,0.12},{"clustered_mid_entropy",0.54,0.86,0.22,0.48,0.18},{"rare_plus_dense_background",0.72,0.52,0.72,0.76,0.24},{"hardware_unfriendly_sparse",0.34,0.70,0.45,0.28,0.86},{"decode_local_burst",0.26,0.58,0.60,0.22,0.42}};
 vector<Method> methods={{"dense_full",0.0,0.0,0.0,0.0,1.00,1.0,false},{"sparse_topk",0.86,0.10,0.12,0.18,0.38,0.45,false},{"lowrank_kernel",0.14,0.88,0.12,0.18,0.32,0.18,false},{"sparse_plus_lowrank",0.70,0.70,0.88,0.36,0.48,0.70,false},{"entropy_switch",0.62,0.62,0.58,0.82,0.42,0.52,false},{"oracle_frontier",1.00,1.00,1.00,1.00,0.58,1.00,true}};
 vector<string> phases={"prefill","decode"}; vector<double> budgets={0.25,0.40,0.55,0.70}; vector<Row> rows; map<string,int>winners,nonoracle;
 for(auto&rg:regimes) for(auto&phase:phases) for(double b:budgets){ vector<Row>cand; for(auto&m:methods){
   double sparse_fit=(1.0-rg.entropy)*m.sparse + rg.clusters*0.20*m.sparse;
   double low_fit=rg.entropy*m.lowrank + rg.dense_background*0.20*m.lowrank;
   double hyb_fit=rg.clusters*m.hybrid*0.30 + min(rg.entropy,1.0-rg.entropy)*m.hybrid*0.45;
   double switch_bonus=m.switcher*0.18*(1.0-abs(rg.entropy-0.5)*1.6);
   double approx_gain=0.20+0.42*sparse_fit+0.40*low_fit+hyb_fit+switch_bonus;
   double err=max(0.0, 1.05-approx_gain-0.25*b);
   double tail=rg.rare_needle*(0.50*(1.0-m.tail_guard)+0.28*(1.0-m.sparse)) + rg.dense_background*0.16*(1.0-m.lowrank);
   double sparse_overhead=rg.hardware_penalty*m.sparse*(phase=="prefill"?0.22:0.10);
   double cost=m.cost*(phase=="prefill"?1.0:0.62)+sparse_overhead+0.14*(1.0-b);
   double wall=cost + 0.18*rg.hardware_penalty*(m.sparse>0.5?1.0:0.2);
   if(m.oracle){err*=0.24; tail*=0.20; wall*=0.72;}
   if(m.name=="dense_full"){err=0.02; tail=0.01; wall=1.0;}
   double score=err+0.62*tail+0.32*wall+0.05*(1.0-b);
   cand.push_back({rg.name,m.name,phase,b,err,tail,cost,wall,score});
 }
 auto best=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){return a.score<b.score;}); winners[best->method]++;
 auto bestNo=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){if(a.method=="oracle_frontier")return false;if(b.method=="oracle_frontier")return true;return a.score<b.score;}); nonoracle[bestNo->method]++; rows.insert(rows.end(),cand.begin(),cand.end());}
 ofstream f(out); f<<fixed<<setprecision(6); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0027\",\n  \"probe\": \"sparse_lowrank_hybrid_frontier\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Sparse and low-rank methods win different entropy regimes; hybrid/switching only deserves promotion when it beats dense under wall-proxy and rare-needle tail terms.\",\n    \"screen_regret_fields\": [\"tail_error\", \"wall_proxy\", \"hardware_penalty\", \"phase\"]\n  },\n  \"rows\": [\n";
 for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"phase\": "<<q(r.phase)<<", \"method\": "<<q(r.method)<<", \"budget\": "<<r.budget<<", \"approx_error\": "<<r.error<<", \"tail_error\": "<<r.tail<<", \"cost\": "<<r.cost<<", \"wall_proxy\": "<<r.wall_proxy<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
 f<<"  ]\n}\n"; cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n";
}
