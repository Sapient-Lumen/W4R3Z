// CloudtainerML rev0024: native beyond-FLOPs real-speed guard toy for pruning/sparsity screens.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <string>
#include <vector>
static std::string q(const std::string&s){return "\""+s+"\"";}
struct Regime{std::string name; double seq, batch, gemm, kernel_overhead, memory_bound, dynamic_overhead;};
struct Method{std::string name; double flops_saved, gemm_aligned, memory_saved, dynamic, quality_loss;};
struct Row{std::string regime, method; double sparsity, flops_proxy, wall_time_proxy, quality_loss, speedup_gap, score;};
int main(int argc,char**argv){
 std::string out=argc>1?argv[1]:"REV0024_REAL_SPEED_FLOPS_GUARD_SMOKE.json";
 std::vector<Regime> regimes={{"short_prompt_batch",0.15,0.80,0.90,0.40,0.22,0.15},{"long_prefill_memory_bound",0.92,0.55,0.70,0.30,0.88,0.25},{"decode_batch_one",0.55,0.05,0.40,0.52,0.80,0.50},{"ffn_dominated_midcontext",0.40,0.50,0.95,0.28,0.45,0.25},{"attention_dominated_very_long",1.00,0.35,0.55,0.35,0.95,0.38},{"kernel_overhead_trap",0.50,0.30,0.35,0.92,0.50,0.85}};
 std::vector<Method> methods={{"dense_baseline",0.00,1.00,0.00,0.00,0.00},{"unstructured_weight_prune",0.55,0.15,0.15,0.05,0.08},{"semi_structured_2_4",0.45,0.72,0.22,0.05,0.05},{"channel_prune_gemm_aligned",0.38,0.92,0.28,0.02,0.06},{"dynamic_token_skip",0.52,0.40,0.48,0.85,0.10},{"low_rank_factorized",0.32,0.65,0.36,0.12,0.07},{"paged_sparse_attention",0.62,0.55,0.70,0.55,0.12}};
 std::vector<double> sparsities={0.25,0.50,0.70,0.85}; std::vector<Row> rows;
 for(auto&rg:regimes){for(double sp:sparsities){for(auto&m:methods){
  double flops_proxy=1.0-m.flops_saved*sp;
  double useful_compute_gain=m.flops_saved*sp*(0.25+0.75*m.gemm_aligned)*rg.gemm;
  double memory_gain=m.memory_saved*sp*rg.memory_bound*(0.55+0.45*rg.seq);
  double dyn_penalty=m.dynamic*rg.dynamic_overhead*(0.25+0.55*rg.kernel_overhead+0.25*(1.0-rg.batch));
  double kernel_penalty=(1.0-m.gemm_aligned)*rg.kernel_overhead*sp*0.35;
  double wall_time_proxy=std::max(0.10,1.0-useful_compute_gain-memory_gain+dyn_penalty+kernel_penalty);
  if(m.name=="dense_baseline") { flops_proxy=1.0; wall_time_proxy=1.0; }
  double quality=m.quality_loss*(0.5+sp)*(0.65+0.35*rg.seq);
  double theoretical_speed=1.0/std::max(0.05,flops_proxy);
  double actual_speed=1.0/std::max(0.05,wall_time_proxy);
  double speedup_gap=std::max(0.0,theoretical_speed-actual_speed);
  double score=wall_time_proxy+0.55*quality+0.08*speedup_gap;
  rows.push_back({rg.name,m.name,sp,flops_proxy,wall_time_proxy,quality,speedup_gap,score});
 }}}
 std::map<std::string,int>winners,nonoracle; size_t idx=0; for(auto&rg:regimes){(void)rg; for(double sp:sparsities){(void)sp; const Row*best=nullptr; for(size_t j=0;j<methods.size();++j){const Row&r=rows[idx++]; if(!best||r.score<best->score)best=&r;} if(best)winners[best->method]++; }}
 std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
 f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0024\",\n  \"probe\": \"real_speed_flops_guard\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Cheap pruning screens need wall-time proxies and kernel/GEMM alignment, because FLOP wins can reverse under dynamic routing overhead or non-GEMM kernels.\"\n  },\n  \"rows\": [\n";
 for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"sparsity\": "<<r.sparsity<<", \"flops_proxy\": "<<r.flops_proxy<<", \"wall_time_proxy\": "<<r.wall_time_proxy<<", \"quality_loss\": "<<r.quality_loss<<", \"speedup_gap\": "<<r.speedup_gap<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
 f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0; }
