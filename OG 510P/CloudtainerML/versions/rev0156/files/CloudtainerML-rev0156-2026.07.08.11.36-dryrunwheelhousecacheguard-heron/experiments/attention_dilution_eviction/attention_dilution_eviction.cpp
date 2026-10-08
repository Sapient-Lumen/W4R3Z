// CloudtainerML rev0023: native attention-dilution eviction performance toy.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <vector>
static std::string q(const std::string&s){return "\""+s+"\"";}
struct Token{double utility, attention, recency, geom, noisy_gate; int useful;};
struct Row{std::string regime,method; int budget; double useful_recall, distractor_rate, output_quality, cost_ratio, score;};
int main(int argc,char**argv){ std::string out=argc>1?argv[1]:"REV0023_ATTENTION_DILUTION_EVICTION_SMOKE.json"; std::mt19937 rng(22024); std::normal_distribution<double> nd(0,1); std::uniform_real_distribution<double> ud(0,1);
  struct Reg{std::string name; int L,useful; double distractor_attention, utility_noise, cost_w;};
  std::vector<Reg> regs={{"full_cache_dilutes",512,12,0.55,0.12,0.12},{"recency_works",512,16,0.20,0.18,0.20},{"buried_evidence",1024,10,0.65,0.10,0.14},{"geometric_signal",768,18,0.35,0.08,0.16},{"cost_tight",1024,20,0.30,0.16,0.42}}; std::vector<int> budgets={16,32,64,128}; std::vector<Row> rows;
  for(auto&rg:regs) for(int B:budgets){ std::vector<Token> toks(rg.L); for(int i=0;i<rg.L;i++){ toks[i].recency=(double)i/(rg.L-1); toks[i].useful=0; toks[i].utility=0.02*ud(rng); toks[i].attention=rg.distractor_attention*ud(rng); toks[i].geom=ud(rng)*0.25; }
    for(int j=0;j<rg.useful;j++){ int idx = (rg.name=="recency_works") ? rg.L-1-j*3 : (17 + (j*rg.L/rg.useful*37)%rg.L); toks[idx].useful=1; toks[idx].utility=1.0+0.25*ud(rng); toks[idx].attention=0.15+0.45*ud(rng); toks[idx].geom=0.75+0.20*ud(rng); }
    for(auto&t:toks)t.noisy_gate=t.utility+rg.utility_noise*nd(rng);
    std::vector<std::string> methods={"full_cache","recency_topk","attention_topk","geometric_proxy","learned_retention_gate","oracle_future_utility"};
    for(auto&m:methods){ std::vector<int> idx(rg.L); for(int i=0;i<rg.L;i++)idx[i]=i; auto score=[&](int i){const auto&t=toks[i]; if(m=="recency_topk")return t.recency; if(m=="attention_topk")return t.attention; if(m=="geometric_proxy")return t.geom; if(m=="learned_retention_gate")return t.noisy_gate; if(m=="oracle_future_utility")return t.utility; return 1.0;}; if(m!="full_cache") std::partial_sort(idx.begin(),idx.begin()+std::min(B,rg.L),idx.end(),[&](int a,int b){return score(a)>score(b);}); int keep=(m=="full_cache")?rg.L:std::min(B,rg.L); double useful=0,distr=0,util=0; for(int k=0;k<keep;k++){auto&t=toks[idx[k]]; if(t.useful){useful++; util+=t.utility;} else distr++;} double recall=useful/(rg.useful+1e-12); double dr=distr/std::max(1,keep); double dilution=(m=="full_cache")?0.55:0.18; double quality=recall - dilution*dr + 0.08*util/(rg.useful+1e-12); double cost=(double)keep/rg.L; double sc=(1.0-quality)+rg.cost_w*cost; rows.push_back({rg.name,m,B,recall,dr,quality,cost,sc}); }
  }
  std::map<std::string,int>winners,nonoracle; for(auto&rg:regs) for(int B:budgets){ const Row*b=nullptr,*bn=nullptr; for(auto&r:rows) if(r.regime==rg.name&&r.budget==B){ if(!b||r.score<b->score)b=&r; if(r.method!="oracle_future_utility"&&(!bn||r.score<bn->score))bn=&r;} if(b)winners[b->method]++; if(bn)nonoracle[bn->method]++;}
  std::ofstream f(out); f<<std::fixed<<std::setprecision(7); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"attention_dilution_eviction\",\n";
  f<<"  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", ";first=false;f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", ";first=false;f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Full cache can lose under attention dilution and equal-cost scoring; learned/global retention is a performance hypothesis, not just a compression fallback.\"\n  },\n  \"rows\": [\n";
  for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"budget\": "<<r.budget<<", \"useful_recall\": "<<r.useful_recall<<", \"distractor_rate\": "<<r.distractor_rate<<", \"output_quality\": "<<r.output_quality<<", \"cost_ratio\": "<<r.cost_ratio<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
  f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0; }
