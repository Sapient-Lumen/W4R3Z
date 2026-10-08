// CloudtainerML rev0024: native attention-sink mechanism diagnostic toy.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <string>
#include <vector>
static std::string q(const std::string&s){return "\""+s+"\"";}
struct Regime{std::string name; double nop, broadcast, decoy, mixed, value_norm_signal;};
struct Method{std::string name; double nop_fit, broadcast_fit, diagnostic, overhead;};
struct Row{std::string regime, method; double diagnostic_f1, task_error, overhead, score;};
int main(int argc,char**argv){
 std::string out=argc>1?argv[1]:"REV0024_ATTENTION_SINK_MECHANISM_SMOKE.json";
 std::vector<Regime> regimes={{"pure_nop_suppression",0.92,0.05,0.12,0.08,0.90},{"pure_broadcast_sink",0.05,0.94,0.10,0.06,0.15},{"mixed_sink_same_stripe",0.48,0.52,0.22,0.90,0.55},{"decoy_vertical_stripe",0.10,0.18,0.92,0.35,0.35},{"late_layer_broadcast",0.20,0.78,0.18,0.40,0.25},{"early_layer_trashcan",0.72,0.18,0.28,0.42,0.82}};
 std::vector<Method> methods={{"no_intervention",0.00,0.00,0.00,0.00},{"sink_gate_only",0.86,0.18,0.55,0.05},{"register_tokens_only",0.18,0.86,0.48,0.08},{"gate_plus_register",0.78,0.78,0.82,0.12},{"value_norm_diagnostic_then_choose",0.72,0.72,0.90,0.10},{"wrong_universal_register",0.05,0.65,0.15,0.08},{"oracle_mechanism_switch",0.96,0.96,1.00,0.15}};
 std::vector<double> sink_strength={0.25,0.50,0.75,1.00}; std::vector<Row> rows;
 for(auto&rg:regimes){for(double s:sink_strength){for(auto&m:methods){
   double nop_match=rg.nop*m.nop_fit; double broadcast_match=rg.broadcast*m.broadcast_fit;
   double misfit=rg.nop*(1.0-m.nop_fit)*0.42 + rg.broadcast*(1.0-m.broadcast_fit)*0.42 + rg.decoy*(0.32+0.30*(1.0-m.diagnostic));
   double diag_signal=rg.value_norm_signal*m.diagnostic + (1.0-rg.value_norm_signal)*m.diagnostic*0.62;
   double diagnostic_f1=std::max(0.0,std::min(1.0,0.18+0.55*m.diagnostic+0.20*diag_signal-0.30*rg.decoy*(1.0-m.diagnostic)));
   double gain=s*(0.42*nop_match+0.42*broadcast_match+0.18*diagnostic_f1);
   double task_error=std::max(0.01,0.98-gain+misfit+0.18*rg.mixed*std::abs(m.nop_fit-m.broadcast_fit));
   if(m.name=="oracle_mechanism_switch") task_error=std::max(0.005,task_error*0.45-0.04*s);
   double score=task_error+0.10*m.overhead+0.06*(1.0-diagnostic_f1);
   rows.push_back({rg.name,m.name,diagnostic_f1,task_error,m.overhead,score});
 }}}
 std::map<std::string,int>winners,nonoracle; size_t idx=0; for(auto&rg:regimes){(void)rg; for(double s:sink_strength){(void)s; const Row*best=nullptr; const Row*bestNo=nullptr; for(size_t j=0;j<methods.size();++j){const Row&r=rows[idx++]; if(!best||r.score<best->score)best=&r; if(r.method!="oracle_mechanism_switch"&&(!bestNo||r.score<bestNo->score))bestNo=&r;} if(best)winners[best->method]++; if(bestNo)nonoracle[bestNo->method]++;}}
 std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
 f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0024\",\n  \"probe\": \"attention_sink_mechanism\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"The same vertical attention-sink signature can mean NOP suppression or broadcast; cheap diagnostics matter before choosing gating, registers, or both.\"\n  },\n  \"rows\": [\n";
 for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"diagnostic_f1\": "<<r.diagnostic_f1<<", \"task_error\": "<<r.task_error<<", \"overhead\": "<<r.overhead<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
 f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0; }
