// CloudtainerML rev0023: native low-rank-decay spectral grokking dynamics toy.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <string>
#include <vector>
static std::string q(const std::string&s){return "\""+s+"\"";}
struct Row{std::string regime,method; int steps; double eff_rank, signal_retention, noise_retention, generalization_proxy, score;};
static double effrank(const std::vector<double>&s){ double sum=0; for(double x:s) sum+=std::max(0.0,x); if(sum<=0) return 0; double H=0; for(double x:s){ double p=std::max(0.0,x)/sum; if(p>0) H-=p*std::log(p); } return std::exp(H); }
int main(int argc,char**argv){ std::string out=argc>1?argv[1]:"REV0023_LOW_RANK_DECAY_DYNAMICS_SMOKE.json";
  struct Reg{std::string name; int signal_rank; double noise_amp, data_frac, rank_pref, retain_w;};
  std::vector<Reg> regs={{"modular_lowrank_signal",4,0.45,0.35,1.4,1.4},{"tiny_data_memorization",3,0.85,0.18,1.8,1.2},{"high_data_signal",9,0.35,0.70,0.8,1.8},{"scale_invariant_plateau",5,0.65,0.30,1.6,1.3},{"overregularization_trap",12,0.25,0.85,0.5,2.4}};
  std::vector<std::string> methods={"none_after_memorization","l2_radial_decay","lrd_soft_threshold","hybrid_l2_lrd","hard_rank_cut","oracle_spectrum"}; std::vector<int> stepsv={20,50,100,200}; std::vector<Row> rows; const int R=32;
  for(auto&rg:regs) for(int steps:stepsv){ std::vector<double> base(R); for(int i=0;i<R;i++){ double signal=(i<rg.signal_rank)?(1.0-0.035*i):0.0; double noise=rg.noise_amp*std::exp(-0.035*i); base[i]=signal+noise; }
    for(auto&m:methods){ auto s=base; if(m=="none_after_memorization"){} else if(m=="l2_radial_decay"){ double a=std::exp(-0.0025*steps); for(auto&x:s)x*=a; } else if(m=="lrd_soft_threshold"){ double tau=0.0032*steps; for(auto&x:s)x=std::max(0.0,x-tau); } else if(m=="hybrid_l2_lrd"){ double a=std::exp(-0.0012*steps), tau=0.0018*steps; for(auto&x:s)x=std::max(0.0,a*x-tau); } else if(m=="hard_rank_cut"){ int keep=std::max(1,(int)std::round(rg.signal_rank+3-0.01*steps)); for(int i=keep;i<R;i++)s[i]=0; } else if(m=="oracle_spectrum"){ for(int i=rg.signal_rank;i<R;i++)s[i]=0; }
      double sig0=0,sig=0,noi0=0,noi=0; for(int i=0;i<R;i++){ if(i<rg.signal_rank){sig0+=base[i];sig+=s[i];} else {noi0+=base[i];noi+=s[i];} }
      double er=effrank(s); double sr=sig/(sig0+1e-12), nr=noi/(noi0+1e-12); double target=std::max(1.0, rg.signal_rank + (1.0-rg.data_frac)*1.5); double gen=std::abs(er-target)/(target+1e-12) + 0.85*nr + rg.retain_w*std::max(0.0,0.80-sr); double score=gen + 0.03*er; rows.push_back({rg.name,m,steps,er,sr,nr,gen,score}); }
  }
  std::map<std::string,int>winners,nonoracle; for(auto&rg:regs) for(int st:stepsv){ const Row*b=nullptr,*bn=nullptr; for(auto&r:rows) if(r.regime==rg.name&&r.steps==st){ if(!b||r.score<b->score)b=&r; if(r.method!="oracle_spectrum"&&(!bn||r.score<bn->score))bn=&r;} if(b)winners[b->method]++; if(bn)nonoracle[bn->method]++;}
  std::ofstream f(out); f<<std::fixed<<std::setprecision(7); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"low_rank_decay_dynamics\",\n";
  f<<"  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", ";first=false;f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", ";first=false;f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"LRD-like spectral shrinkage is a plausible grokking lever only in low-rank-signal / memorization-noise regimes; overregularization traps need explicit retention metrics.\"\n  },\n  \"rows\": [\n";
  for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"steps\": "<<r.steps<<", \"effective_rank\": "<<r.eff_rank<<", \"signal_retention\": "<<r.signal_retention<<", \"noise_retention\": "<<r.noise_retention<<", \"generalization_proxy\": "<<r.generalization_proxy<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
  f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0; }
