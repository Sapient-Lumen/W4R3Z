// CloudtainerML rev0025: sparse-attention isoFLOPS frontier toy; larger sparse versus smaller dense.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <string>
#include <vector>
static std::string q(const std::string&s){return "\""+s+"\"";}
struct Task{std::string name; double long_need, needle, local, distractor, prefill_hard, decode_flex;};
struct Method{std::string name; double model_scale, sparsity, adapt, token_grain, block_grain, cost_overhead, recall_bias;};
struct Row{std::string task, method, phase; double seq_k, iso_cost, quality, realized_cost, regret, score;};
int main(int argc,char**argv){
  std::string out=argc>1?argv[1]:"REV0025_SPARSE_FRONTIER_ISOFLOPS_SMOKE.json";
  std::vector<Task> tasks={{"local_summarization",0.25,0.10,0.90,0.30,0.25,0.70},{"needle_retrieval",0.95,0.98,0.08,0.65,0.60,0.82},{"multi_region_reasoning",0.88,0.55,0.22,0.86,0.88,0.55},{"distractor_heavy_qa",0.80,0.68,0.30,0.95,0.74,0.65},{"syntax_local_long_doc",0.45,0.12,0.95,0.55,0.35,0.78},{"global_counting",0.92,0.30,0.20,0.55,0.90,0.35}};
  std::vector<Method> methods={{"small_dense",0.70,0.00,0.00,0.00,0.00,0.00,0.85},{"medium_dense",1.00,0.00,0.00,0.00,0.00,0.00,1.00},{"large_dense_overbudget",1.35,0.00,0.00,0.00,0.00,0.00,1.18},{"large_block_sparse",1.35,0.70,0.30,0.10,0.85,0.16,0.72},{"large_token_sparse",1.35,0.78,0.65,0.88,0.10,0.28,0.90},{"large_adaptive_sparse",1.35,0.82,0.88,0.70,0.40,0.34,0.96},{"medium_hybrid_local_global",1.10,0.55,0.55,0.40,0.55,0.20,0.88},{"oracle_sparse",1.35,0.86,1.00,1.00,1.00,0.40,1.05}};
  std::vector<double> seqs={8,32,128,512}; std::vector<std::string> phases={"prefill","decode"}; std::vector<Row> rows;
  for(auto&task:tasks){for(double L:seqs){for(auto&phase:phases){double phase_flex=phase=="decode"?task.decode_flex:(1.0-task.prefill_hard); for(auto&m:methods){
    double dense_cost=m.model_scale*m.model_scale*(0.45+0.55*L/512.0);
    double sparse_cost=dense_cost*(1.0-m.sparsity*(0.40+0.45*phase_flex)) + m.cost_overhead*(0.12+0.18*std::log2(L+1));
    double realized_cost=m.name.find("dense")!=std::string::npos?dense_cost:sparse_cost;
    double support_recall=1.0-m.sparsity*(0.52*task.needle*(1.0-m.token_grain)+0.45*task.distractor*(1.0-m.adapt)+0.36*task.long_need*(phase=="prefill"?task.prefill_hard:0.25)) + 0.20*m.recall_bias + 0.16*m.adapt*phase_flex;
    support_recall=std::max(0.0,std::min(1.05,support_recall));
    double scale_gain=0.30*std::log(std::max(0.5,m.model_scale)+0.5);
    double local_gain=task.local*(0.08+0.18*(m.name.find("hybrid")!=std::string::npos));
    double quality=0.55 + scale_gain + local_gain + 0.34*support_recall - 0.12*m.cost_overhead;
    if(m.name=="large_dense_overbudget") quality+=0.06;
    if(m.name=="oracle_sparse") quality=0.96+0.02*phase_flex-0.02*task.distractor;
    double iso_cost=1.0; // soft budget; overbudget is penalized, not forbidden.
    double over=std::max(0.0,realized_cost-iso_cost); double under=std::max(0.0,iso_cost-realized_cost);
    double regret=std::max(0.0,0.92-quality) + 0.18*over + 0.03*under;
    double score=regret + 0.08*realized_cost;
    rows.push_back({task.name,m.name,phase,L,iso_cost,quality,realized_cost,regret,score});
  }}}}
  std::map<std::string,int>winners,nonoracle; size_t idx=0; for(auto&task:tasks){(void)task; for(double L:seqs){(void)L; for(auto&phase:phases){(void)phase; const Row*best=nullptr; const Row*bestNo=nullptr; for(size_t j=0;j<methods.size();++j){const Row&r=rows[idx++]; if(!best||r.score<best->score)best=&r; if(r.method!="oracle_sparse"&&r.method!="large_dense_overbudget"&&(!bestNo||r.score<bestNo->score))bestNo=&r;} if(best)winners[best->method]++; if(bestNo)nonoracle[bestNo->method]++;}}}
  std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
  f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0025\",\n  \"probe\": \"sparse_frontier_isoflops\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_budgeted_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"IsoFLOPS comparisons are task- and phase-dependent: sparse larger models can win when support recall survives, but prefill/global/counting regimes punish the wrong sparsification granularity.\"\n  },\n  \"rows\": [\n";
  for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"task\": "<<q(r.task)<<", \"method\": "<<q(r.method)<<", \"phase\": "<<q(r.phase)<<", \"seq_k\": "<<r.seq_k<<", \"iso_cost\": "<<r.iso_cost<<", \"quality\": "<<r.quality<<", \"realized_cost\": "<<r.realized_cost<<", \"regret\": "<<r.regret<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
  f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0; }
