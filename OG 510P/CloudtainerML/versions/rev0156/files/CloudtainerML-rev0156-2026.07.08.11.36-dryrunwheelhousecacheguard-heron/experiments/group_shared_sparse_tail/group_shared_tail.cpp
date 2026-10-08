// CloudtainerML rev0025: HASTE-style group-shared fixed fan-in sparse tail versus irregular sparsity.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <string>
#include <vector>
static std::string q(const std::string&s){return "\""+s+"\"";}
struct Regime{std::string name; double tail_mass, group_semantics, feature_reuse, long_tail, kernel_sensitive, head_gradient;};
struct Method{std::string name; double structure, reuse, dense_head, irregular, aux, quality, memory;};
struct Row{std::string regime, method; double fanin, precision_at_k, wall_proxy, memory_proxy, kernel_penalty, score;};
int main(int argc,char**argv){
  std::string out=argc>1?argv[1]:"REV0025_GROUP_SHARED_SPARSE_TAIL_SMOKE.json";
  std::vector<Regime> regimes={{"semantic_label_groups",0.70,0.92,0.86,0.78,0.55,0.70},{"random_label_groups",0.72,0.12,0.28,0.75,0.55,0.65},{"head_labels_dominate",0.25,0.50,0.55,0.20,0.42,0.92},{"extreme_tail_noisy",0.92,0.45,0.35,0.96,0.70,0.55},{"kernel_overhead_trap",0.80,0.65,0.72,0.82,0.96,0.62},{"dense_quality_gap",0.60,0.58,0.50,0.62,0.45,0.25}};
  std::vector<Method> methods={{"dense_output",0.00,1.00,1.00,0.00,0.00,1.00,1.00},{"random_fixed_fanin",0.05,0.18,0.00,0.90,0.00,0.58,0.28},{"unshared_fixed_fanin",0.25,0.28,0.05,0.75,0.15,0.66,0.32},{"group_shared_fanin",0.72,0.88,0.10,0.20,0.20,0.78,0.34},{"dense_head_sparse_tail",0.70,0.82,0.82,0.18,0.10,0.84,0.42},{"group_shared_plus_aux",0.76,0.86,0.65,0.20,0.55,0.86,0.44},{"oracle_group_sparse",1.00,1.00,0.95,0.05,0.50,0.96,0.38}};
  std::vector<double> fanins={0.05,0.10,0.20,0.35}; std::vector<Row> rows;
  for(auto&rg:regimes){for(double fi:fanins){for(auto&m:methods){
    double tail_quality=rg.tail_mass*(0.20+0.55*m.structure*rg.group_semantics+0.22*m.quality*std::sqrt(fi/0.35));
    double head_quality=(1.0-rg.tail_mass)*(0.30+0.55*m.dense_head+0.10*m.quality);
    double grad_quality=rg.head_gradient*(0.10*m.dense_head+0.12*m.aux);
    double long_tail_loss=rg.long_tail*(0.40*(1.0-m.structure)+0.16*(1.0-m.dense_head))*(0.90-fi);
    double precision=std::max(0.0,std::min(1.0,head_quality+tail_quality+grad_quality-long_tail_loss));
    if(m.name=="dense_output") precision=0.92-0.05*rg.long_tail+0.04*rg.head_gradient;
    if(m.name=="oracle_group_sparse") precision=0.94-0.02*(1.0-rg.group_semantics);
    double reuse_gain=m.reuse*rg.feature_reuse*(0.40+0.60*rg.group_semantics);
    double irregular_pen=m.irregular*rg.kernel_sensitive*(0.35+0.55*(1.0-rg.feature_reuse));
    double kernel_penalty=std::max(0.0, irregular_pen - 0.30*reuse_gain);
    double wall=1.0 - 0.58*(1.0-fi)*(0.25+0.75*reuse_gain) + 0.32*kernel_penalty + 0.10*m.aux;
    if(m.name=="dense_output") wall=1.0;
    double memory=0.20+fi*(0.55+0.25*m.memory)+0.10*m.dense_head;
    if(m.name=="dense_output") memory=1.0;
    double score=(1.0-precision)+0.32*wall+0.12*memory+0.18*kernel_penalty;
    rows.push_back({rg.name,m.name,fi,precision,wall,memory,kernel_penalty,score});
  }}}
  std::map<std::string,int>winners,nonoracle; size_t idx=0; for(auto&rg:regimes){(void)rg; for(double fi:fanins){(void)fi; const Row*best=nullptr; const Row*bestNo=nullptr; for(size_t j=0;j<methods.size();++j){const Row&r=rows[idx++]; if(!best||r.score<best->score)best=&r; if(r.method!="oracle_group_sparse"&&(!bestNo||r.score<bestNo->score))bestNo=&r;} if(best)winners[best->method]++; if(bestNo)nonoracle[bestNo->method]++;}}
  std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
  f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0025\",\n  \"probe\": \"group_shared_sparse_tail\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Group-shared sparse tails need both semantic grouping and feature reuse; random groups and irregular sparsity lose the speed/quality trade when kernel overhead is modeled.\"\n  },\n  \"rows\": [\n";
  for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"fanin\": "<<r.fanin<<", \"precision_at_k\": "<<r.precision_at_k<<", \"wall_proxy\": "<<r.wall_proxy<<", \"memory_proxy\": "<<r.memory_proxy<<", \"kernel_penalty\": "<<r.kernel_penalty<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
  f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
