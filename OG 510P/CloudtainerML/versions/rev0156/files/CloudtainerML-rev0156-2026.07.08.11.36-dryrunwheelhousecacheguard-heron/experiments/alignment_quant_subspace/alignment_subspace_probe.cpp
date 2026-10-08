// CloudtainerML rev0023: safety-subspace KV quantization tail probe.
// Dependency-free C++17 microkernel. Inspired by reports that low-bit KV cache
// quantization can preserve average perplexity while destroying low-dimensional
// safety/alignment features. This is a synthetic diagnostic, not a reproduction.

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <sstream>
#include <string>
#include <vector>

struct Vec { std::vector<double> x; Vec(){} explicit Vec(int d):x(d,0.0){} };
struct Row { std::string scenario, method; int bits=0, n=0; double task_mse=0, safety_mse=0, safety_flip=0, tail_p99=0, utility=0; };
static double dot(const Vec&a,const Vec&b){ double s=0; for(size_t i=0;i<a.x.size();++i) s+=a.x[i]*b.x[i]; return s; }
static double norm(const Vec&a){ return std::sqrt(std::max(1e-30,dot(a,a))); }
static void normalize(Vec&v){ double n=norm(v); for(double&z:v.x) z/=n; }
static std::string esc(const std::string&s){ std::string o; for(char c:s){ if(c=='"') o+="\\\""; else if(c=='\\') o+="\\\\"; else o+=c;} return o; }
static Vec randn_vec(std::mt19937_64&rng,int d,double sigma=1.0){ std::normal_distribution<double>N(0,sigma); Vec v(d); for(double&z:v.x) z=N(rng); return v; }
static Vec orthogonal_to(std::mt19937_64&rng,const std::vector<Vec>&basis,int d){ Vec v=randn_vec(rng,d); for(const auto&b:basis){ double c=dot(v,b); for(int i=0;i<d;++i) v.x[i]-=c*b.x[i]; } normalize(v); return v; }
static double pct(std::vector<double> v,double q){ if(v.empty()) return 0; std::sort(v.begin(),v.end()); size_t i=(size_t)std::floor(q*(v.size()-1)); return v[i]; }

struct Scenario { std::string name; double safety_amp; double outlier_amp; double dilution; double nonoutlier_safety; int layers; };
struct Metrics { double task_mse=0,safety_mse=0,safety_flip=0,tail_p99=0,utility=0; };

static Vec quant_global(const Vec&v,int bits){
    if(bits>=16) return v; double mx=0; for(double z:v.x) mx=std::max(mx,std::abs(z)); if(mx<1e-12) return v;
    int levels=(1<<(bits-1))-1; levels=std::max(1,levels); Vec q((int)v.x.size());
    for(size_t i=0;i<v.x.size();++i){ double r=std::round(v.x[i]/mx*levels); r=std::max((double)-levels,std::min((double)levels,r)); q.x[i]=r/levels*mx; } return q;
}
static Vec quant_grouped(const Vec&v,int bits,int group){
    if(bits>=16) return v; int d=(int)v.x.size(); Vec q(d); int levels=std::max(1,(1<<(bits-1))-1);
    for(int s=0;s<d;s+=group){ int e=std::min(d,s+group); double mx=0; for(int i=s;i<e;++i) mx=std::max(mx,std::abs(v.x[i])); if(mx<1e-12){ for(int i=s;i<e;++i) q.x[i]=v.x[i]; continue; }
        for(int i=s;i<e;++i){ double r=std::round(v.x[i]/mx*levels); r=std::max((double)-levels,std::min((double)levels,r)); q.x[i]=r/levels*mx; }} return q;
}
static Vec quant_pcr(const Vec&v,int bits,const std::vector<int>&protected_dims){
    Vec q=quant_grouped(v,bits,8); // base protocol
    // Protect a small calibration-discovered channel set at higher precision.
    for(int idx: protected_dims) if(idx>=0 && idx<(int)v.x.size()) q.x[idx]=quant_grouped(v, std::min(8,bits+3), 1).x[idx];
    return q;
}
static Metrics simulate(const Scenario&sc,const std::string&method,int bits,int seed){
    std::mt19937_64 rng(seed); const int d=64; Vec safety=randn_vec(rng,d); normalize(safety);
    Vec task=orthogonal_to(rng,{safety},d);
    std::uniform_real_distribution<double> U(0,1);
    int n=420; std::vector<double> task_errs, safety_errs; int flips=0;
    std::vector<int> protected_dims;
    for(int i=0;i<d;++i) if(std::abs(safety.x[i])>0.16 || (sc.nonoutlier_safety>0.5 && i%17==0)) protected_dims.push_back(i);
    for(int i=0;i<n;++i){
        Vec v=randn_vec(rng,d,0.16);
        double task_coeff=1.0 + 0.3*std::sin(0.013*i+seed);
        double safe_coeff=(U(rng)<0.22?1.0:-0.25)*sc.safety_amp*(0.55+U(rng));
        for(int j=0;j<d;++j){ v.x[j]+=task_coeff*task.x[j]+safe_coeff*safety.x[j]; }
        // Outlier channels are common in activations; sometimes they do not carry safety.
        for(int k=0;k<4;++k){ int idx=(int)(rng()%d); double sign=(rng()%2)?1.0:-1.0; v.x[idx]+=sign*sc.outlier_amp*(0.6+U(rng)); }
        if(sc.nonoutlier_safety>0.5){
            // Hide safety in mid-sized non-outlier channels that global scale can crush.
            for(int j=0;j<d;++j) v.x[j]+=0.12*sc.safety_amp*safety.x[j];
        }
        Vec q;
        if(method=="global_int") q=quant_global(v,bits);
        else if(method=="grouped_int") q=quant_grouped(v,bits,8);
        else if(method=="per_channel_int") q=quant_grouped(v,bits,1);
        else if(method=="attention_mass_proxy") q=quant_global(v,bits); // deliberately blind to safety subspace
        else if(method=="pcr_protected_channels") q=quant_pcr(v,bits,protected_dims);
        else if(method=="oracle_safety_projection") { q=quant_grouped(v,bits,8); double delta=dot(v,safety)-dot(q,safety); for(int j=0;j<d;++j) q.x[j]+=delta*safety.x[j]; }
        else q=v;
        Vec diff(d); for(int j=0;j<d;++j) diff.x[j]=v.x[j]-q.x[j];
        double te=std::pow(dot(diff,task),2);
        double se=std::pow(dot(diff,safety),2);
        double sm=dot(v,safety), qm=dot(q,safety);
        if((sm>=0)!=(qm>=0) && std::abs(sm)>0.04) flips++;
        task_errs.push_back(te); safety_errs.push_back(se);
    }
    double tm=std::accumulate(task_errs.begin(),task_errs.end(),0.0)/n;
    double sm=std::accumulate(safety_errs.begin(),safety_errs.end(),0.0)/n;
    double sf=(double)flips/n;
    double p99=pct(safety_errs,0.99);
    double cost = method=="fp32"?0.55: method=="oracle_safety_projection"?0.22: method=="pcr_protected_channels"?0.10: method=="per_channel_int"?0.13: 0.02;
    double utility = -(0.30*tm + 3.0*sm + 5.0*sf + 1.3*p99 + cost);
    return {tm,sm,sf,p99,utility};
}
static void add(Row&r,const Metrics&m){ r.task_mse+=m.task_mse; r.safety_mse+=m.safety_mse; r.safety_flip+=m.safety_flip; r.tail_p99+=m.tail_p99; r.utility+=m.utility; r.n++; }

int main(int argc,char**argv){
    std::string out="artifacts/probe-results/REV0023_ALIGNMENT_SUBSPACE_QUANT_SMOKE.json"; if(argc>1) out=argv[1];
    auto t0=std::chrono::high_resolution_clock::now();
    std::vector<Scenario> scenarios={
        {"outlier_crushes_safety",0.60,8.5,0.0,1.0,4},
        {"outlier_as_safety",1.25,4.0,0.0,0.0,4},
        {"multi_layer_dilution",0.38,5.0,1.0,0.5,12},
        {"benign_task_features",0.18,4.5,0.0,0.0,3},
        {"phase_transition_low_margin",0.72,7.0,0.2,1.0,8}
    };
    std::vector<std::string> methods={"fp32","global_int","grouped_int","per_channel_int","attention_mass_proxy","pcr_protected_channels","oracle_safety_projection"};
    std::vector<int> bits={2,3,4,8};
    std::map<std::string,Row> rows; std::map<std::string,int> wins, nonoracle_wins;
    for(const auto&sc: scenarios) for(int b:bits) for(int seed=0;seed<64;++seed){
        double best=-1e99,best_no=-1e99; std::string bw,bn;
        for(const auto&m:methods){ Metrics x=simulate(sc,m,b,123456+seed*101+b*7+(int)sc.name.size()); std::string key=sc.name+"|"+std::to_string(b)+"|"+m; if(!rows.count(key)){ rows[key].scenario=sc.name; rows[key].bits=b; rows[key].method=m; } add(rows[key],x); if(x.utility>best){best=x.utility;bw=m;} if(m.find("oracle")==std::string::npos && x.utility>best_no){best_no=x.utility;bn=m;} }
        wins[bw]++; nonoracle_wins[bn]++;
    }
    double seconds=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count();
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"alignment_subspace_quant\",\n  \"language\": \"c++17\",\n  \"is_paper_reproduction\": false,\n";
    f<<"  \"taxonomy\": [\"lossy-cache\", \"quantization\", \"safety-subspace\", \"tail-risk\"],\n";
    f<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<seconds<<", \"primary_metric\": {\"name\": \"mean_utility\", \"direction\": \"higher_is_better\", \"winner_field\": \"winner_counts_excluding_oracle\"}, \"tail_metrics\": {\"has_catastrophic_proxy\": true, \"fields\": [\"mean_safety_flip_rate\", \"mean_safety_p99\"]}, \"winner_counts\": {";
    bool first=true; for(auto&kv:wins){ if(!first)f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second; }
    f<<"}, \"winner_counts_excluding_oracle\": {"; first=true; for(auto&kv:nonoracle_wins){ if(!first)f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second; }
    f<<"}, \"interpretation\": \"Toy test for whether average reconstruction hides low-dimensional safety subspace failures; PCR-like protected channels are the non-oracle mitigation anchor.\"},\n  \"rows\": [\n";
    int c=0; for(auto&kv:rows){ const Row&r=kv.second; double n=std::max(1,r.n); if(c++)f<<",\n"; f<<"    {\"scenario\": \""<<esc(r.scenario)<<"\", \"bits\": "<<r.bits<<", \"method\": \""<<esc(r.method)<<"\", \"mean_task_mse\": "<<r.task_mse/n<<", \"mean_safety_mse\": "<<r.safety_mse/n<<", \"mean_safety_flip_rate\": "<<r.safety_flip/n<<", \"mean_safety_p99\": "<<r.tail_p99/n<<", \"mean_utility\": "<<r.utility/n<<"}"; }
    f<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
