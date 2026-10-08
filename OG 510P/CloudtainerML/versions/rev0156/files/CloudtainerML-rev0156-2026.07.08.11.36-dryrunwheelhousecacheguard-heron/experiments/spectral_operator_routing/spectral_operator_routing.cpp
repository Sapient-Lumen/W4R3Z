// CloudtainerML rev0028 — Spectral/operator routing wind tunnel.
// Inspired by Chiaroscuro/CHIAR-style spectral entropy routing. Symbolic C++ probe, not a paper reproduction.
#include <bits/stdc++.h>
using namespace std;
static string q(const string&s){string o="\""; for(char c:s){ if(c=='"'||c=='\\') o+='\\'; o+=c;} return o+'"';}
struct Regime{string name; double lowfreq, highfreq, local, longrange, entropy, alias, naturalistic; int n;};
struct Method{string name; double dct, rbf, attn, router, adapt, cost, rbf_overhead, collapse_bias; bool oracle=false;};
struct Row{string regime, method; int budget_pct; double quality, error, flops, budget_over, route_miss, alias_error, regret, score;};
int main(int argc,char**argv){
 string out=argc>1?argv[1]:"REV0028_SPECTRAL_OPERATOR_ROUTING_SMOKE.json";
 vector<Regime> regs={{"smooth_naturalistic_long",0.88,0.10,0.34,0.70,0.28,0.10,0.95,2048},{"synthetic_pattern_match",0.18,0.88,0.22,0.78,0.82,0.62,0.05,1024},{"local_bursty_reviews",0.52,0.30,0.86,0.35,0.50,0.22,0.70,1536},{"mixed_frequency_code",0.45,0.60,0.55,0.72,0.72,0.58,0.42,2048},{"small_dataset_noisy",0.38,0.44,0.48,0.35,0.68,0.48,0.18,512},{"periodic_alias_trap",0.25,0.74,0.30,0.82,0.76,0.92,0.25,2048},{"redundant_low_entropy",0.92,0.06,0.70,0.42,0.14,0.06,0.88,4096}};
 vector<Method> meth={{"full_attention",0.18,0.10,1.00,0.0,0.10,1.00,0.0,0.0,false},{"dct_only",0.86,0.06,0.08,0.0,0.05,0.22,0.0,0.75,false},{"rbf_only",0.14,0.82,0.06,0.0,0.05,0.35,0.15,0.10,false},{"dct_attention_fixed",0.78,0.04,0.55,0.18,0.15,0.48,0.0,0.48,false},{"three_operator_router",0.66,0.45,0.54,0.55,0.38,0.74,0.22,0.18,false},{"spectral_entropy_router",0.72,0.22,0.58,0.72,0.50,0.55,0.06,0.35,false},{"collapse_dct_attention",0.84,0.04,0.62,0.62,0.44,0.40,0.0,0.62,false},{"cheap_entropy_then_attention",0.55,0.05,0.74,0.50,0.40,0.62,0.0,0.28,false},{"oracle_operator_mix",1.00,1.00,1.00,1.00,1.00,0.50,0.0,0.0,true}};
 vector<int> budgets={25,40,55,70,100}; vector<Row> rows; map<string,int>winners, nonoracle;
 for(auto&rg:regs){ for(int bp:budgets){ double budget=bp/100.0; vector<Row> cand; for(auto&m:meth){
   double dct_match=m.dct*(0.82*rg.lowfreq+0.20*rg.naturalistic+0.12*rg.longrange-0.22*rg.alias);
   double rbf_match=m.rbf*(0.74*rg.highfreq+0.30*rg.local+0.16*rg.alias-0.18*rg.naturalistic);
   double attn_match=m.attn*(0.50*rg.highfreq+0.38*rg.longrange+0.25*rg.local+0.22*rg.entropy);
   double route = m.router*(0.35+0.40*rg.entropy+0.25*m.adapt) - 0.16*m.collapse_bias*rg.highfreq;
   double quality=max(0.0,min(1.0,0.08+dct_match+rbf_match+attn_match+route));
   double route_miss=max(0.0,rg.entropy*(0.52*(1.0-m.router)+0.18*m.collapse_bias) + rg.alias*(0.28*(1.0-m.rbf)) - 0.12*m.adapt);
   double alias_error=max(0.0,rg.alias*(0.55*(1.0-m.rbf)+0.25*(1.0-m.attn)+0.16*m.collapse_bias));
   double flops=m.cost*(0.65+0.35*log2((double)rg.n)/12.0) + m.rbf_overhead;
   double budget_over=max(0.0,flops-budget);
   if(m.oracle){ quality=0.97-0.04*rg.alias+0.02*rg.naturalistic; route_miss=0.02*rg.entropy; alias_error=0.03*rg.alias; flops=min(0.88,budget+0.05); budget_over=max(0.0,flops-budget); }
   double error=max(0.0,1.0-quality+0.32*route_miss+0.25*alias_error);
   double regret=max(0.0,error-(m.oracle?error:0.08));
   double score=error + 0.55*budget_over + 0.08*flops + 0.10*alias_error;
   cand.push_back({rg.name,m.name,bp,quality,error,flops,budget_over,route_miss,alias_error,regret,score});
 }
 auto best=min_element(cand.begin(),cand.end(),[](const Row&a,const Row&b){return a.score<b.score;}); winners[best->method]++;
 auto bestNo=min_element(cand.begin(),cand.end(),[](const Row&a,const Row&b){if(a.method=="oracle_operator_mix")return false; if(b.method=="oracle_operator_mix")return true; return a.score<b.score;}); nonoracle[bestNo->method]++; rows.insert(rows.end(),cand.begin(),cand.end()); }}
 ofstream f(out); f<<fixed<<setprecision(6);
 f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0028\",\n  \"probe\": \"spectral_operator_routing\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"DCT+attention-style collapse is a useful discovery in smooth/naturalistic regimes, but alias/high-frequency synthetic cases need either full attention or explicit anti-alias repair.\",\n    \"screen_regret_fields\": [\"budget_over\", \"route_miss\", \"alias_error\", \"regret\", \"flops\"]\n  },\n  \"rows\": [\n";
 for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"budget_pct\": "<<r.budget_pct<<", \"quality\": "<<r.quality<<", \"error\": "<<r.error<<", \"flops\": "<<r.flops<<", \"budget_over\": "<<r.budget_over<<", \"route_miss\": "<<r.route_miss<<", \"alias_error\": "<<r.alias_error<<", \"regret\": "<<r.regret<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
 f<<"  ]\n}\n"; cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n";
}
