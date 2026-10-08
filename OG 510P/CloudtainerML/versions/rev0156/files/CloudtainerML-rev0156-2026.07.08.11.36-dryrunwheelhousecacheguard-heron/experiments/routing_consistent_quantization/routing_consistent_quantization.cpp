// CloudtainerML rev0028 — Routing-consistent quantization wind tunnel for MoE-ish routers.
// Inspired by VSRAQ/value-and-structure alignment. Symbolic C++ probe only.
#include <bits/stdc++.h>
using namespace std; static string q(const string&s){string o="\""; for(char c:s){if(c=='"'||c=='\\')o+='\\'; o+=c;} return o+'"';}
struct Regime{string name; double margin, value_scale, router_sensitivity, rare, expert_correlation, noise;};
struct Method{string name; double recon, route, structure, mixed, cost; bool oracle=false;};
struct Row{string regime, method; int bits; double output_mse, route_flip_rate, rare_route_miss, bytes_fraction, mismatch_rate, score;};
int main(int argc,char**argv){string out=argc>1?argv[1]:"REV0028_ROUTING_CONSISTENT_QUANTIZATION_SMOKE.json";
 vector<Regime> regs={{"wide_router_margin",0.92,0.45,0.18,0.08,0.70,0.08},{"near_boundary_router",0.18,0.42,0.88,0.22,0.55,0.16},{"rare_expert_tail",0.42,0.38,0.72,0.92,0.40,0.18},{"large_value_outliers",0.58,0.96,0.48,0.20,0.48,0.20},{"correlated_experts",0.66,0.50,0.40,0.20,0.94,0.12},{"noisy_router_training",0.38,0.54,0.66,0.34,0.40,0.78}};
 vector<Method> ms={{"reconstruction_only",0.82,0.05,0.08,0.10,0.00,false},{"per_channel_quant",0.72,0.18,0.16,0.22,0.03,false},{"router_align_loss",0.58,0.76,0.42,0.20,0.08,false},{"value_structure_align",0.72,0.62,0.78,0.25,0.11,false},{"mixed_precision_router_protect",0.68,0.84,0.62,0.78,0.18,false},{"oracle_quant_policy",1.00,1.00,1.00,1.00,0.28,true}};
 vector<int> bits={2,3,4,8}; vector<Row> rows; map<string,int>winners,nonoracle;
 for(auto&rg:regs)for(int b:bits){vector<Row> cand; double qerr=(9.0-b)/7.0; double byte=b/8.0; for(auto&m:ms){
   double mse=max(0.0, qerr*(0.52*(1-m.recon)+0.22*rg.value_scale*(1-m.mixed)+0.10*rg.noise)-0.05*rg.expert_correlation);
   double flip=max(0.0, qerr*rg.router_sensitivity*(0.72*(1-m.route)+0.18*(1-rg.margin)+0.12*rg.noise));
   double rare_miss=max(0.0, rg.rare*qerr*(0.54*(1-m.route)+0.30*(1-m.structure)+0.10*(1-m.mixed)));
   if(m.oracle){mse=0.02*qerr; flip=0.015*rg.router_sensitivity*qerr; rare_miss=0.02*rg.rare*qerr; byte=min(byte+0.08,1.0);}
   double bytes_fraction=min(1.0,byte+m.cost*0.18);
   double mismatch=0.62*flip+0.25*rare_miss+0.13*mse;
   double score=mse+0.85*flip+0.48*rare_miss+0.12*bytes_fraction;
   cand.push_back({rg.name,m.name,b,mse,flip,rare_miss,bytes_fraction,mismatch,score});}
 auto best=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){return a.score<b.score;}); winners[best->method]++;
 auto bestNo=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){if(a.method=="oracle_quant_policy")return false;if(b.method=="oracle_quant_policy")return true;return a.score<b.score;}); nonoracle[bestNo->method]++; rows.insert(rows.end(),cand.begin(),cand.end());}
 ofstream f(out); f<<fixed<<setprecision(6); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0028\",\n  \"probe\": \"routing_consistent_quantization\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Output reconstruction is not enough when router margins are small; route-consistency and mixed router protection become valuable under rare-expert and near-boundary regimes.\",\n    \"screen_regret_fields\": [\"route_flip_rate\", \"rare_route_miss\", \"mismatch_rate\", \"bytes_fraction\"]\n  },\n  \"rows\": [\n";
 for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"bits\": "<<r.bits<<", \"output_mse\": "<<r.output_mse<<", \"route_flip_rate\": "<<r.route_flip_rate<<", \"rare_route_miss\": "<<r.rare_route_miss<<", \"bytes_fraction\": "<<r.bytes_fraction<<", \"mismatch_rate\": "<<r.mismatch_rate<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
 f<<"  ]\n}\n"; cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n";}
