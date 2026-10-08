// CloudtainerML rev0023: native gated-subspace inference toy.
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
struct Row{std::string regime,method; double eps, quality_loss, top1_flip, cost_ratio, score; int tokens, corrected;};
int main(int argc,char**argv){
  std::string out=argc>1?argv[1]:"REV0023_GATED_SUBSPACE_INFERENCE_SMOKE.json";
  std::mt19937 rng(22022); std::normal_distribution<double> nd(0,1); std::uniform_real_distribution<double> ud(0,1);
  struct Reg{std::string name; double manifold, residual_tail, rare_rate, residual_importance, noise, latency_w;};
  std::vector<Reg> regs={{"lowrank_manifold",0.92,0.08,0.02,0.7,0.03,0.28},{"residual_spikes",0.78,0.22,0.08,2.4,0.04,0.20},{"flat_manifold",0.60,0.40,0.05,1.2,0.05,0.16},{"strict_exactness",0.86,0.14,0.03,2.0,0.02,0.08},{"bandwidth_tight",0.90,0.10,0.04,1.0,0.03,0.48}};
  std::vector<double> epses={0.02,0.05,0.08,0.12,0.18}; std::vector<Row> rows; const int N=4096;
  for(auto& rg:regs) for(double eps:epses){
    std::vector<double> residual(N), impact(N), cheap(N); std::vector<int> rare(N);
    for(int i=0;i<N;i++){ double r=std::abs(nd(rng))*rg.residual_tail; bool sp=ud(rng)<rg.rare_rate; if(sp) r+=0.35+0.8*ud(rng); residual[i]=r; rare[i]=sp; impact[i]=rg.residual_importance*r*(0.65+0.7*ud(rng)) + (sp?0.55:0.0) + rg.noise*std::abs(nd(rng)); cheap[i]=r + 0.18*std::abs(nd(rng)) + (sp?0.10:0.0); }
    std::vector<std::string> methods={"full_linear","subspace_only","residual_norm_gate","cheap_predictive_gate","two_stage_gate","oracle_error_gate"};
    for(auto&m:methods){ double loss=0, flips=0, cost=0; int corr=0; for(int i=0;i<N;i++){ bool compute=false; if(m=="full_linear") compute=true; else if(m=="subspace_only") compute=false; else if(m=="residual_norm_gate") compute=residual[i]>eps; else if(m=="cheap_predictive_gate") compute=cheap[i]>eps*1.25; else if(m=="two_stage_gate") compute=(residual[i]>eps*0.85)||(cheap[i]>eps*1.55 && rare[i]); else if(m=="oracle_error_gate") compute=impact[i]>eps; if(compute){cost+=1.0; corr++;} else {loss+=impact[i]*impact[i]; if(impact[i]>eps) flips+=1.0;} }
      loss/=N; flips/=N; double cr=0.23 + 0.77*cost/N; double score=loss + 1.7*flips + rg.latency_w*cr; rows.push_back({rg.name,m,eps,loss,flips,cr,score,N,corr}); }
  }
  std::map<std::string,int>winners,nonoracle; for(auto&rg:regs) for(double eps:epses){const Row*b=nullptr,*bn=nullptr; for(auto&r:rows) if(r.regime==rg.name && std::abs(r.eps-eps)<1e-9){if(!b||r.score<b->score)b=&r; if(r.method!="oracle_error_gate"&&(!bn||r.score<bn->score))bn=&r;} if(b)winners[b->method]++; if(bn)nonoracle[bn->method]++;}
  std::ofstream f(out); f<<std::fixed<<std::setprecision(7); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"gated_subspace_inference\",\n";
  f<<"  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", ";first=false;f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", ";first=false;f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Gated subspace inference is promising only if the cheap gate predicts residual output impact, not just residual norm; rare residual spikes are the red-team regime.\"\n  },\n  \"rows\": [\n";
  for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"epsilon\": "<<r.eps<<", \"quality_loss\": "<<r.quality_loss<<", \"top1_flip_rate\": "<<r.top1_flip<<", \"cost_ratio\": "<<r.cost_ratio<<", \"score\": "<<r.score<<", \"tokens\": "<<r.tokens<<", \"residual_corrections\": "<<r.corrected<<"}"<<(i+1==rows.size()?"\n":",\n");}
  f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0; }
