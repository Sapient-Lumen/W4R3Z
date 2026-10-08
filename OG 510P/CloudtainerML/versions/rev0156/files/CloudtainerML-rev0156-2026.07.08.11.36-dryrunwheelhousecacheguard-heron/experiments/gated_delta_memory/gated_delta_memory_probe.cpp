// CloudtainerML rev0023: decoupled erase/write fast-weight memory probe.
// Toy test inspired by Gated DeltaNet-2's claim that erase and write should not
// be forced through one scalar gate. We create changing key-value associations
// where stale channels and useful channels differ, then compare memory updates.

#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <sstream>
#include <string>
#include <vector>

struct Vec{std::vector<double>x;Vec(){}explicit Vec(int d):x(d,0.0){}}; struct Mat{int d;std::vector<double>a;Mat(int d_=0):d(d_),a(d_*d_,0.0){} double& operator()(int i,int j){return a[i*d+j];} double operator()(int i,int j)const{return a[i*d+j];}};
static double dot(const Vec& a,const Vec& b){double s=0;for(size_t i=0;i<a.x.size();++i)s+=a.x[i]*b.x[i];return s;} static double norm(const Vec& a){return std::sqrt(std::max(1e-30,dot(a,a)));} static void normalize(Vec& v){double n=norm(v);for(double& z:v.x)z/=n;} static Vec randn_vec(std::mt19937_64& rng,int d,double s=1.0){std::normal_distribution<double>nd(0,s);Vec v(d);for(double& z:v.x)z=nd(rng);normalize(v);return v;} static Vec noisy(std::mt19937_64& rng,const Vec& b,double s){std::normal_distribution<double>nd(0,s);Vec v((int)b.x.size());for(size_t i=0;i<b.x.size();++i)v.x[i]=b.x[i]+nd(rng);normalize(v);return v;}
static Vec read(const Mat& M,const Vec& k){Vec y(M.d);for(int i=0;i<M.d;++i){double s=0;for(int j=0;j<M.d;++j)s+=M(i,j)*k.x[j];y.x[i]=s;}return y;}
static void write_outer(Mat& M,const Vec& k,const Vec& v,double decay,const std::vector<double>& erase,const std::vector<double>& write){
    int d=M.d; for(double& z:M.a) z*=decay; // broad decay
    // erase old key-side coordinates, then commit selected value-side coordinates.
    for(int i=0;i<d;++i) for(int j=0;j<d;++j) M(i,j)*=(1.0-erase[j]*std::abs(k.x[j]));
    for(int i=0;i<d;++i) for(int j=0;j<d;++j) M(i,j)+=write[i]*v.x[i]*k.x[j];
}
struct Row{std::string regime,policy;double error=0,cosine=0,write_rate=0;int n=0;}; static std::string esc(const std::string&s){std::string o;for(char c:s){if(c=='"')o+="\\\"";else if(c=='\\')o+="\\\\";else o+=c;}return o;}

static Row run_once(int seed,const std::string& regime,const std::string& policy){
    const int d=32, keys=64, T=512; std::mt19937_64 rng(seed); std::vector<Vec>K(keys),V(keys); for(auto& k:K)k=randn_vec(rng,d); for(auto& v:V)v=randn_vec(rng,d); Mat M(d); int writes=0;
    for(int t=0;t<T;++t){int id=(int)(rng()%keys); if(regime=="periodic_overwrite") id=t%keys; if(regime=="bursty_stale") id=(t%100<70)?(t%8):(int)(rng()%keys); Vec k=noisy(rng,K[id],0.03); Vec newv=noisy(rng,V[id],0.18); if(t%37==0 || regime=="periodic_overwrite") V[id]=newv; Vec old=read(M,k); double stale=norm(old); std::vector<double> erase(d,0.0), wr(d,0.0);
        if(policy=="no_erase_write_all"){std::fill(wr.begin(),wr.end(),1.0);} else if(policy=="tied_scalar_delta"){double g=std::min(1.0,0.35+0.10*stale);std::fill(erase.begin(),erase.end(),g);std::fill(wr.begin(),wr.end(),g);} else if(policy=="write_gate_only"){double g=std::min(1.0,0.35+0.10*norm(newv));std::fill(wr.begin(),wr.end(),g);} else if(policy=="decoupled_channel_gates"){for(int i=0;i<d;++i){erase[i]=std::min(1.0,std::abs(k.x[i])*2.2);wr[i]=std::min(1.0,std::abs(newv.x[i])*2.2);}} else if(policy=="oracle_changed_channels"){for(int i=0;i<d;++i){erase[i]=std::abs(k.x[i])>0.12?1.0:0.0;wr[i]=std::abs(newv.x[i])>0.12?1.0:0.0;}} write_outer(M,k,newv,0.996,erase,wr); writes++; }
    double err=0,cos=0; for(int id=0;id<keys;++id){Vec y=read(M,K[id]); Vec diff((int)y.x.size()); for(size_t i=0;i<y.x.size();++i)diff.x[i]=y.x[i]-V[id].x[i]; err += norm(diff)/std::max(1e-12,norm(V[id])); cos += dot(y,V[id])/(norm(y)*norm(V[id])+1e-12); }
    Row r; r.regime=regime; r.policy=policy; r.error=err/keys; r.cosine=cos/keys; r.write_rate=(double)writes/T; r.n=1; return r;
}
static void accum(Row&a,const Row&b){a.error+=b.error;a.cosine+=b.cosine;a.write_rate+=b.write_rate;a.n++;}
int main(int argc,char**argv){std::string out="artifacts/probe-results/REV0023_GATED_DELTA_MEMORY_SMOKE.json";if(argc>1)out=argv[1];auto t0=std::chrono::high_resolution_clock::now();std::vector<std::string> regimes={"periodic_overwrite","bursty_stale","random_updates"};std::vector<std::string> policies={"no_erase_write_all","tied_scalar_delta","write_gate_only","decoupled_channel_gates","oracle_changed_channels"};std::map<std::string,Row> table;for(int seed=0;seed<24;++seed)for(auto&rg:regimes)for(auto&po:policies){Row r=run_once(9000+seed*131,rg,po);std::string key=rg+"|"+po;if(!table.count(key)){table[key]=r;table[key].n=0;table[key].error=table[key].cosine=table[key].write_rate=0;}accum(table[key],r);}std::map<std::string,int>winners;for(auto&rg:regimes){double best=1e300;std::string bp;for(auto&po:policies){auto&r=table[rg+"|"+po];double e=r.error/std::max(1,r.n);if(e<best){best=e;bp=po;}}winners[bp]++;}auto t1=std::chrono::high_resolution_clock::now();double sec=std::chrono::duration<double>(t1-t0).count();std::ofstream f(out);f<<std::fixed<<std::setprecision(6);f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"gated_delta_memory\",\n";f<<"  \"summary\": {\"row_count\": "<<table.size()<<", \"seconds\": "<<sec<<", \"primary_metric\": {\"name\": \"mean_retrieval_rel_error\", \"direction\": \"lower_is_better\", \"winner_field\": \"winner_counts\"}, \"winner_counts\": {";bool first=true;for(auto&kv:winners){if(!first)f<<", ";first=false;f<<"\""<<esc(kv.first)<<"\": "<<kv.second;}f<<"}},\n  \"rows\": [\n";int c=0;for(auto&kv:table){auto r=kv.second;double n=std::max(1,r.n);if(c++)f<<",\n";f<<"    {\"regime\": \""<<esc(r.regime)<<"\", \"policy\": \""<<esc(r.policy)<<"\", \"mean_retrieval_rel_error\": "<<r.error/n<<", \"mean_cosine\": "<<r.cosine/n<<", \"write_rate\": "<<r.write_rate/n<<"}";}f<<"\n  ]\n}\n";std::cerr<<"wrote "<<out<<" rows="<<table.size()<<"\n";return 0;}
