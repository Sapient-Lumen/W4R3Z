// CloudtainerML rev0025: dynamic-short-convolution repair/HPO toy after rev0023 locality caveat.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <string>
#include <vector>
static std::string q(const std::string&s){return "\""+s+"\"";}
struct Regime{std::string name; double local_key, global_key, alias, burst, cost_sensitive, shift;};
struct Method{std::string name; double local_mix, dynamic, global_bypass, anti_alias, gate_cost, kernel_eff;};
struct Row{std::string regime, method; int width; double accuracy, cost, alias_error, score;};
int main(int argc,char**argv){
  std::string out=argc>1?argv[1]:"REV0025_DYNCONV_REPAIR_HPO_SMOKE.json";
  std::vector<Regime> regimes={{"clean_local_associative",0.92,0.20,0.12,0.25,0.35,0.10},{"mostly_global_lookup",0.18,0.94,0.20,0.25,0.42,0.10},{"local_aliasing_trap",0.80,0.35,0.92,0.30,0.50,0.18},{"bursty_distractors",0.65,0.55,0.45,0.92,0.60,0.22},{"distribution_shifted_keys",0.58,0.55,0.42,0.40,0.46,0.88},{"kernel_overhead_shortseq",0.70,0.25,0.25,0.20,0.95,0.12}};
  std::vector<Method> methods={{"vanilla_attention",0.00,0.00,1.00,0.50,0.00,1.00},{"static_short_conv",0.70,0.00,0.10,0.18,0.04,0.95},{"dynamic_short_conv",0.80,0.78,0.12,0.30,0.16,0.82},{"dynamic_plus_global_bypass",0.74,0.70,0.76,0.36,0.22,0.78},{"dynamic_antialias_gate",0.72,0.66,0.48,0.82,0.28,0.72},{"hpo_switch_conv_or_bypass",0.68,0.72,0.88,0.74,0.30,0.70},{"oracle_regime_switch",1.00,1.00,1.00,1.00,0.36,0.70}};
  std::vector<int> widths={3,5,9,17}; std::vector<Row> rows;
  for(auto&rg:regimes){for(int w:widths){double width_fit=std::min(1.0,std::log2((double)w+1.0)/4.0); for(auto&m:methods){
    double local_acc=rg.local_key*(0.25+0.52*m.local_mix*width_fit+0.16*m.dynamic);
    double global_acc=rg.global_key*(0.25+0.52*m.global_bypass+0.10*(m.name=="vanilla_attention"));
    double shift_acc=rg.shift*(0.10+0.30*m.dynamic+0.24*m.global_bypass);
    double alias_error=rg.alias*(0.42*m.local_mix*(1.0-m.anti_alias)+0.18*(1.0-m.global_bypass)) + rg.burst*(0.18*(1.0-m.anti_alias));
    double accuracy=std::max(0.0,std::min(1.0,0.25+local_acc+global_acc+shift_acc-0.60*alias_error));
    if(m.name=="oracle_regime_switch") accuracy=0.94-0.03*rg.alias-0.02*rg.cost_sensitive;
    double cost=0.55+0.05*w + 0.30*m.gate_cost + 0.18*(1.0-m.kernel_eff) + 0.12*m.dynamic;
    if(m.name=="vanilla_attention") cost=0.82+0.05*rg.global_key;
    double score=(1.0-accuracy)+0.22*cost*rg.cost_sensitive+0.20*alias_error;
    rows.push_back({rg.name,m.name,w,accuracy,cost,alias_error,score});
  }}}
  std::map<std::string,int>winners,nonoracle; size_t idx=0; for(auto&rg:regimes){(void)rg; for(int w:widths){(void)w; const Row*best=nullptr; const Row*bestNo=nullptr; for(size_t j=0;j<methods.size();++j){const Row&r=rows[idx++]; if(!best||r.score<best->score)best=&r; if(r.method!="oracle_regime_switch"&&(!bestNo||r.score<bestNo->score))bestNo=&r;} if(best)winners[best->method]++; if(bestNo)nonoracle[bestNo->method]++; }}
  std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
  f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0025\",\n  \"probe\": \"dynconv_repair_hpo\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Dynamic short convolution should be treated as a conditional local-mixing primitive: global bypass and anti-alias gates matter more than wider kernels in the hard regimes.\"\n  },\n  \"rows\": [\n";
  for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"width\": "<<r.width<<", \"accuracy\": "<<r.accuracy<<", \"cost\": "<<r.cost<<", \"alias_error\": "<<r.alias_error<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
  f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0; }
