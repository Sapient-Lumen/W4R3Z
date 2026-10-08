#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <string>
#include <vector>
using namespace std;
struct Row{string regime,method; int seed,n,target; double target_mass,entropy,cost,exp_ops,score,tail_miss;};
vector<double> softmax(vector<double>s){double m=*max_element(s.begin(),s.end()); vector<double>w(s.size()); double z=0; for(size_t i=0;i<s.size();i++){w[i]=exp(s[i]-m); z+=w[i];} for(double &x:w)x/=z; return w;}
vector<double> relu_norm(vector<double>s){vector<double>w(s.size()); double z=0; for(size_t i=0;i<s.size();i++){w[i]=max(0.0,s[i]); z+=w[i];} if(z<=1e-12){for(double&x:w)x=1.0/s.size();} else for(double&x:w)x/=z; return w;}
vector<double> cosine_pow(vector<double>s,double p){vector<double>w(s.size()); double mx=*max_element(s.begin(),s.end()); double mn=*min_element(s.begin(),s.end()); double z=0; for(size_t i=0;i<s.size();i++){double c=cos((s[i]-mx)/(max(1e-6,mx-mn))*1.57079632679); w[i]=pow(max(0.0,c),p); z+=w[i];} if(z<=1e-12){for(double&x:w)x=1.0/s.size();} else for(double&x:w)x/=z; return w;}
vector<double> topk_softmax(vector<double>s,int k){vector<int>idx(s.size()); iota(idx.begin(),idx.end(),0); nth_element(idx.begin(),idx.begin()+min(k,(int)idx.size())-1,idx.end(),[&](int a,int b){return s[a]>s[b];}); vector<double>mask(s.size(),-1e9); for(int i=0;i<min(k,(int)idx.size());i++)mask[idx[i]]=s[idx[i]]; return softmax(mask);}
double entropy(const vector<double>&w){double e=0; for(double x:w) if(x>1e-12)e-=x*log(x); return e;}
int main(int argc,char**argv){string rev="rev0032",out="artifacts/probe-results/REV0032_OSCILLATOR_ATTENTION_PROXY_SMOKE.json"; for(int i=1;i<argc;i++){string a=argv[i]; if(a=="--revision"&&i+1<argc)rev=argv[++i]; else if(a=="--out"&&i+1<argc)out=argv[++i];}
 vector<string> regs={"sharp_winner","broad_semantic","negative_scores","alias_decoys","tail_needle"}; vector<string> meth={"softmax_exp","relu_noexp","cosine_relu_proxy","oscillator_pow4_proxy","topk_softmax_k8"}; vector<Row>rows; mt19937 gen(4242); normal_distribution<double>N(0,1);
 for(auto &reg:regs) for(int seed=0;seed<18;seed++){mt19937 rng(900+seed*13+reg.size()); int n=64,target=seed%n; vector<double>s(n); for(int i=0;i<n;i++)s[i]=0.4*N(rng); s[target]+=2.0; if(reg=="sharp_winner")s[target]+=2.2; if(reg=="broad_semantic"){for(int j=0;j<n;j++) if(abs(j-target)<=5)s[j]+=1.2-0.15*abs(j-target);} if(reg=="negative_scores"){for(double &x:s)x-=1.6; s[target]+=2.8;} if(reg=="alias_decoys"){for(int d=0;d<5;d++)s[(target+7+11*d)%n]+=2.1;} if(reg=="tail_needle"){s[target]+=0.8; for(int d=0;d<10;d++)s[(target+3+d*5)%n]+=1.0+0.15*d;}
   for(auto&m:meth){vector<double>w; double cost=1.0,exp_ops=0; if(m=="softmax_exp"){w=softmax(s); cost=1.0; exp_ops=n;} else if(m=="relu_noexp"){w=relu_norm(s); cost=0.42;} else if(m=="cosine_relu_proxy"){w=cosine_pow(s,1.0); cost=0.55;} else if(m=="oscillator_pow4_proxy"){w=cosine_pow(s,4.0); cost=0.78;} else {w=topk_softmax(s,8); cost=0.65; exp_ops=8;} double tm=w[target]; Row r{reg,m,seed,n,target,tm,entropy(w),cost,exp_ops,(1.0-tm)+0.08*cost+0.002*exp_ops,tm<0.05?1.0:0.0}; rows.push_back(r);} }
 map<string,int>wins; for(auto&reg:regs)for(int seed=0;seed<18;seed++){Row*best=nullptr; for(auto&r:rows) if(r.regime==reg&&r.seed==seed){if(!best||r.score<best->score)best=&r;} if(best)wins[best->method]++;}
 ofstream f(out); f<<fixed<<setprecision(6); f<<"{\n  \"project\":\"CloudtainerML\",\n  \"revision\":\""<<rev<<"\",\n  \"probe\":\"oscillator_attention_proxy\",\n";
 f<<"  \"summary\":{\n    \"primary_metric\":{\"name\":\"score\",\"direction\":\"lower_is_better\",\"winner_field\":\"method\"},\n    \"winner_counts\":{"; bool first=true; for(auto&kv:wins){if(!first)f<<",";first=false;f<<"\""<<kv.first<<"\":"<<kv.second;} f<<"},\n    \"interpretation\":\"No-exp cosine/oscillator-style attention can be competitive when scores are broad or exponentials are charged, but top-k/softmax dominate sharp and tail-needle regimes; treat physical-substrate attention as a cost-regime question.\",\n    \"screen_regret_fields\":[\"target_mass\",\"entropy\",\"cost\",\"exp_ops\",\"tail_miss\",\"score\"]\n  },\n  \"rows\":[\n";
 for(size_t i=0;i<rows.size();i++){auto&r=rows[i]; f<<"    {\"regime\":\""<<r.regime<<"\",\"method\":\""<<r.method<<"\",\"seed\":"<<r.seed<<",\"n\":"<<r.n<<",\"target\":"<<r.target<<",\"target_mass\":"<<r.target_mass<<",\"entropy\":"<<r.entropy<<",\"cost\":"<<r.cost<<",\"exp_ops\":"<<r.exp_ops<<",\"tail_miss\":"<<r.tail_miss<<",\"score\":"<<r.score<<"}"<<(i+1<rows.size()?",":"")<<"\n";}
 f<<"  ]\n}\n"; cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; }
