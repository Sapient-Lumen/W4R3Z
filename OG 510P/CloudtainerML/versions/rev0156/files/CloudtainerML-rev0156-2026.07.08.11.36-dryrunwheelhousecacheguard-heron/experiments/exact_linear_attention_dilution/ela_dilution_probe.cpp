// CloudtainerML rev0023: native linear-attention dilution/discriminability toy.
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
struct Row{std::string regime,method; int length, dim; double target_mass, output_error, cost_ratio, score;};
static double dot(const std::vector<double>&a,const std::vector<double>&b){double s=0; for(size_t i=0;i<a.size();++i)s+=a[i]*b[i]; return s;}
static double l2(const std::vector<double>&a,const std::vector<double>&b){double s=0; for(size_t i=0;i<a.size();++i){double d=a[i]-b[i];s+=d*d;} return s;}
int main(int argc,char**argv){
  std::string out=argc>1?argv[1]:"REV0023_ELA_DILUTION_PROBE_SMOKE.json"; std::mt19937 rng(22023); std::normal_distribution<double> nd(0,1);
  struct Reg{std::string name; double temp, noise, decoy, value_noise, cost_w;};
  std::vector<Reg> regs={{"sharp_needle",0.35,0.15,0.10,0.05,0.05},{"many_near_decoys",0.55,0.20,0.65,0.05,0.06},{"smooth_semantic",1.25,0.40,0.25,0.10,0.08},{"long_dilution",0.75,0.25,0.35,0.08,0.14},{"cost_dominated",0.85,0.30,0.30,0.08,0.32}};
  std::vector<int> lengths={64,128,256,512}; const int D=16; std::vector<Row> rows;
  for(auto&rg:regs) for(int L:lengths){
    std::vector<double> query(D), target(D), target_val(D); for(int d=0;d<D;d++){query[d]=nd(rng); target[d]=query[d]+rg.noise*nd(rng); target_val[d]=nd(rng);} int target_idx=L/3;
    std::vector<std::vector<double>> keys(L,std::vector<double>(D)), vals(L,std::vector<double>(D));
    for(int i=0;i<L;i++) for(int d=0;d<D;d++){ double mix=(i%17==0)?rg.decoy:0.0; keys[i][d]=mix*query[d]+(1-mix)*nd(rng); vals[i][d]=rg.value_noise*nd(rng); }
    keys[target_idx]=target; vals[target_idx]=target_val;
    std::vector<std::string> methods={"softmax_full","relu_linear_kernel","sqeuclid_positive_kernel","hadamard_exp_proxy","sparse_lowrank_mix","exact_kernel_oracle"};
    for(auto&m:methods){ std::vector<double> w(L); double denom=0; for(int i=0;i<L;i++){ double s=dot(query,keys[i])/std::sqrt((double)D); double wi=0; if(m=="softmax_full") wi=std::exp(s/rg.temp); else if(m=="relu_linear_kernel") wi=std::pow(std::max(0.0,1.0+s),2.0); else if(m=="sqeuclid_positive_kernel") wi=std::exp(-0.40*l2(query,keys[i])/D); else if(m=="hadamard_exp_proxy"){ double prod=1.0; for(int d=0;d<D;d++) prod*=std::exp(0.015*query[d]*keys[i][d]); wi=prod; } else if(m=="sparse_lowrank_mix"){ double lin=std::pow(std::max(0.0,1.0+s),2.0); double local=(std::abs(i-target_idx)<5)?1.0:0.0; wi=lin+2.5*local; } else if(m=="exact_kernel_oracle") wi=(i==target_idx)?1.0:1e-9; w[i]=wi; denom+=wi; }
      std::vector<double> outv(D,0); for(int i=0;i<L;i++){ double p=w[i]/(denom+1e-12); for(int d=0;d<D;d++) outv[d]+=p*vals[i][d]; }
      double err=std::sqrt(l2(outv,target_val)/(l2(target_val,std::vector<double>(D,0))+1e-12)); double mass=w[target_idx]/(denom+1e-12); double cr=1.0; if(m=="relu_linear_kernel"||m=="sqeuclid_positive_kernel"||m=="hadamard_exp_proxy") cr=0.26; else if(m=="sparse_lowrank_mix") cr=0.38; else if(m=="exact_kernel_oracle") cr=0.06; double score=err + 0.7*(1.0-mass) + rg.cost_w*cr; rows.push_back({rg.name,m,L,D,mass,err,cr,score}); }
  }
  std::map<std::string,int>winners,nonoracle; for(auto&rg:regs) for(int L:lengths){const Row*b=nullptr,*bn=nullptr; for(auto&r:rows) if(r.regime==rg.name&&r.length==L){if(!b||r.score<b->score)b=&r; if(r.method!="exact_kernel_oracle"&&(!bn||r.score<bn->score))bn=&r;} if(b)winners[b->method]++; if(bn)nonoracle[bn->method]++;}
  std::ofstream f(out); f<<std::fixed<<std::setprecision(7); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"exact_linear_attention_dilution\",\n";
  f<<"  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", ";first=false;f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", ";first=false;f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Linear/positive kernels need discriminability, not just linear complexity; target-mass dilution is the cheap falsifier before any tiny trained ELA-like block.\"\n  },\n  \"rows\": [\n";
  for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"length\": "<<r.length<<", \"dim\": "<<r.dim<<", \"target_mass\": "<<r.target_mass<<", \"output_error\": "<<r.output_error<<", \"cost_ratio\": "<<r.cost_ratio<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
  f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0; }
