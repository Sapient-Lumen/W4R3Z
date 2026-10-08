// CloudtainerML rev0024: native oracle-guided sparse prefill gap toy.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <string>
#include <vector>
static std::string q(const std::string&s){return "\""+s+"\"";}
struct Regime{std::string name; double sharpness, multi, block_stability, head_divergence, locality, index_noise;};
struct Method{std::string name; double support_quality, block_share, learned, local_bias, index_cost, dense_cost;};
struct Row{std::string regime, method; double support_frac, recall, oracle_gap, indexer_gap, realization_gap, read_cost, score;};
int main(int argc,char**argv){
 std::string out=argc>1?argv[1]:"REV0024_ORACLE_SPARSE_PREFILL_GAP_SMOKE.json";
 std::vector<Regime> regimes={{"single_sharp_needle",0.94,0.08,0.45,0.25,0.20,0.12},{"multi_evidence_chain",0.55,0.88,0.55,0.35,0.30,0.22},{"block_shared_support",0.62,0.42,0.90,0.16,0.44,0.12},{"head_divergent_evidence",0.70,0.55,0.20,0.92,0.28,0.20},{"local_global_mixture",0.52,0.52,0.55,0.42,0.88,0.15},{"noisy_long_context",0.46,0.70,0.38,0.55,0.20,0.72}};
 std::vector<Method> methods={{"dense_full_prefill",1.00,0.00,0.00,0.00,0.00,1.00},{"oracle_token_topk",1.00,0.00,0.00,0.00,0.02,0.00},{"oracle_block_shared",0.92,0.85,0.00,0.00,0.02,0.00},{"distilled_indexer",0.72,0.20,0.65,0.08,0.09,0.00},{"indexer_plus_local_repair",0.74,0.25,0.72,0.45,0.13,0.00},{"fixed_local_global",0.52,0.50,0.00,0.82,0.03,0.00},{"random_support",0.12,0.00,0.00,0.00,0.01,0.00}};
 std::vector<double> budgets={0.02,0.05,0.10,0.20,0.40}; std::vector<Row> rows;
 for(auto&rg:regimes){ for(double b:budgets){ for(auto&m:methods){
   double budget_factor=std::min(1.0, std::sqrt(b/0.10));
   double token_recall=budget_factor*(0.25+0.75*m.support_quality)*(0.82+0.18*rg.sharpness);
   double block_loss=rg.head_divergence*m.block_share*0.32 + (1.0-rg.block_stability)*m.block_share*0.25;
   double local_gain=rg.locality*m.local_bias*std::min(1.0,budget_factor+0.25);
   double multi_penalty=rg.multi*(1.0-std::min(1.0,budget_factor*1.45))*(0.25+0.25*(1.0-m.support_quality));
   double learned_noise=rg.index_noise*m.learned*(0.18+0.20*(1.0-budget_factor));
   double recall=std::max(0.0,std::min(1.0, token_recall + 0.18*local_gain - block_loss - multi_penalty - learned_noise));
   if(m.name=="dense_full_prefill") recall=1.0;
   if(m.name=="random_support") recall=std::min(0.55, b*(0.8+0.4*rg.multi));
   double oracle_token_recall=std::min(1.0,budget_factor*(0.92+0.08*rg.sharpness) - rg.multi*0.08*(1.0-budget_factor));
   double oracle_gap=std::max(0.0,1.0-oracle_token_recall);
   double indexer_gap=std::max(0.0,oracle_token_recall-recall);
   double realization_gap=std::max(0.0,block_loss + learned_noise + 0.05*m.block_share);
   double read_cost=(m.dense_cost>0?1.0:b) + m.index_cost + 0.04*m.block_share;
   double score=(1.0-recall)+0.20*read_cost+0.08*realization_gap;
   rows.push_back({rg.name,m.name,b,recall,oracle_gap,indexer_gap,realization_gap,read_cost,score});
 } } }
 std::map<std::string,int>winners,nonoracle; size_t idx=0; for(auto&rg:regimes){(void)rg; for(double b:budgets){(void)b; const Row*best=nullptr; const Row*bestNo=nullptr; for(size_t j=0;j<methods.size();++j){const Row&r=rows[idx++]; if(!best||r.score<best->score)best=&r; if(r.method!="oracle_token_topk"&&r.method!="dense_full_prefill"&&(!bestNo||r.score<bestNo->score))bestNo=&r;} if(best)winners[best->method]++; if(bestNo)nonoracle[bestNo->method]++;}}
 std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
 f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0024\",\n  \"probe\": \"oracle_sparse_prefill_gap\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Oracle-guided sparse prefill is best used as a gap decomposition: oracle budget gap, learned-indexer gap, and realization/block-sharing gap often fail for different reasons.\"\n  },\n  \"rows\": [\n";
 for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"support_frac\": "<<r.support_frac<<", \"recall\": "<<r.recall<<", \"oracle_gap\": "<<r.oracle_gap<<", \"indexer_gap\": "<<r.indexer_gap<<", \"realization_gap\": "<<r.realization_gap<<", \"read_cost\": "<<r.read_cost<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
 f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0; }
