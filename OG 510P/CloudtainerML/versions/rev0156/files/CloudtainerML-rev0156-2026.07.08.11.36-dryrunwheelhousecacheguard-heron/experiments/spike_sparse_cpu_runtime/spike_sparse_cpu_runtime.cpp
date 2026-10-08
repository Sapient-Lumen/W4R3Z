// CloudtainerML rev0028 — Spike/activation-sparse CPU runtime proxy.
// Inspired by spike-aware C++ INT8 inference work. Symbolic wall-proxy C++ probe only.
#include <bits/stdc++.h>
using namespace std; static string q(const string&s){string o="\""; for(char c:s){if(c=='"'||c=='\\')o+='\\'; o+=c;} return o+'"';}
struct Regime{string name; double sparsity, burst, locality, batch, cache_pressure, quality_sensitivity;};
struct Method{string name; double exploit, block, fallback, branch, int8, overhead; bool oracle=false;};
struct Row{string regime, method; int hidden; double wall_proxy, speedup_proxy, branch_miss, cache_miss, quality_drop, realized_cost, score;};
int main(int argc,char**argv){string out=argc>1?argv[1]:"REV0028_SPIKE_SPARSE_CPU_RUNTIME_SMOKE.json";
 vector<Regime> regs={{"high_random_sparsity",0.92,0.12,0.30,0.08,0.30,0.20},{"bursty_spikes",0.82,0.88,0.55,0.08,0.42,0.24},{"moderate_structured_sparsity",0.65,0.30,0.82,0.16,0.30,0.18},{"nearly_dense_fallback",0.18,0.25,0.55,0.32,0.25,0.12},{"tiny_batch_high_overhead",0.78,0.44,0.45,0.02,0.36,0.24},{"cache_pressure_long_state",0.72,0.35,0.70,0.08,0.92,0.28},{"quality_sensitive_spikes",0.76,0.48,0.58,0.08,0.44,0.90}};
 vector<Method> ms={{"dense_int8_gemm",0.00,0.00,0.95,0.02,0.92,0.00,false},{"naive_sparse_index",0.62,0.12,0.10,0.78,0.70,0.22,false},{"block_sparse_fixed",0.54,0.76,0.24,0.32,0.82,0.18,false},{"spike_aware_csr",0.82,0.45,0.36,0.42,0.88,0.20,false},{"hybrid_threshold_runtime",0.68,0.62,0.84,0.26,0.86,0.16,false},{"quality_guarded_sparse",0.62,0.54,0.80,0.24,0.80,0.24,false},{"oracle_runtime_switch",1.00,1.00,1.00,0.05,0.95,0.28,true}};
 vector<int> hs={512,1024,2048}; vector<Row> rows; map<string,int>winners,nonoracle;
 for(auto&rg:regs)for(int h:hs){vector<Row> cand; double hscale=log2((double)h)/11.0; for(auto&m:ms){
   double dense_cost=1.0*hscale*(0.80+0.25*rg.cache_pressure);
   double sparse_gain=rg.sparsity*m.exploit*(0.62+0.22*m.block+0.10*rg.locality);
   double overhead=m.overhead*(1.15-0.30*rg.batch)+0.10*m.branch*rg.burst+0.08*(1.0-m.block)*rg.cache_pressure;
   double fallback=max(0.0,(0.40-rg.sparsity))*m.fallback;
   double wall=max(0.05,dense_cost*(1.0-sparse_gain)+overhead-fallback*0.15);
   double branch_miss=max(0.0,m.branch*(0.35+0.45*rg.burst)*(1.0-0.25*m.block));
   double cache_miss=max(0.0,rg.cache_pressure*(0.42*(1.0-m.block)+0.18*(1.0-m.fallback)));
   double quality_drop=max(0.0,rg.quality_sensitivity*(0.24*m.exploit*(1.0-m.fallback)+0.12*(1.0-m.int8)));
   if(m.oracle){wall=min(dense_cost, dense_cost*(1.0-0.75*rg.sparsity)+0.10); branch_miss=0.03*rg.burst; cache_miss=0.05*rg.cache_pressure; quality_drop=0.01*rg.quality_sensitivity;}
   double speedup=dense_cost/wall; double realized=wall+0.16*branch_miss+0.12*cache_miss; double score=wall+0.18*branch_miss+0.12*cache_miss+0.65*quality_drop;
   cand.push_back({rg.name,m.name,h,wall,speedup,branch_miss,cache_miss,quality_drop,realized,score});}
 auto best=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){return a.score<b.score;}); winners[best->method]++;
 auto bestNo=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){if(a.method=="oracle_runtime_switch")return false;if(b.method=="oracle_runtime_switch")return true;return a.score<b.score;}); nonoracle[bestNo->method]++; rows.insert(rows.end(),cand.begin(),cand.end());}
 ofstream f(out); f<<fixed<<setprecision(6); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0028\",\n  \"probe\": \"spike_sparse_cpu_runtime\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Activation sparsity only buys CPU performance when overhead, burstiness, fallback, and quality-sensitive spikes are modeled; dense INT8 remains a hard baseline.\",\n    \"screen_regret_fields\": [\"wall_proxy\", \"branch_miss\", \"cache_miss\", \"quality_drop\", \"realized_cost\"]\n  },\n  \"rows\": [\n";
 for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"hidden\": "<<r.hidden<<", \"wall_proxy\": "<<r.wall_proxy<<", \"speedup_proxy\": "<<r.speedup_proxy<<", \"branch_miss\": "<<r.branch_miss<<", \"cache_miss\": "<<r.cache_miss<<", \"quality_drop\": "<<r.quality_drop<<", \"realized_cost\": "<<r.realized_cost<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
 f<<"  ]\n}\n"; cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n";}
