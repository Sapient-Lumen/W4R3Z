// CloudtainerML rev0016: native token-vs-precision KV cache frontier probe.
// Dependency-free C++17 microkernel. This is a synthetic wind tunnel, not a
// reproduction of any paper. It asks whether fixed cache bytes should buy more
// low-bit tokens or fewer high-bit tokens under adversarial attention regimes.
// Build: g++ -O3 -std=c++17 token_precision_frontier.cpp -o token_precision_frontier

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
struct World { std::vector<Vec> k, v; Vec q; int target=0; double temp=0.1; std::vector<double> age, sponsor; };
struct Row { std::string scenario, policy; int budget4=0; double rel_error=0, cosine=0, dropped_mass=0, target_ret=0, tokens=0, mean_bits=0; int n=0; };

static double dot(const Vec& a, const Vec& b){ double s=0; for(size_t i=0;i<a.x.size();++i) s+=a.x[i]*b.x[i]; return s; }
static double norm(const Vec& a){ return std::sqrt(std::max(1e-30, dot(a,a))); }
static Vec add_scaled(const Vec& a, const Vec& b, double wa, double wb){ Vec z((int)a.x.size()); for(size_t i=0;i<a.x.size();++i) z.x[i]=wa*a.x[i]+wb*b.x[i]; return z; }
static void normalize(Vec& a){ double n=norm(a); for(double& z:a.x) z/=n; }
static Vec randn_vec(std::mt19937_64& rng, int d, double sigma=1.0){ std::normal_distribution<double> nd(0.0,sigma); Vec v(d); for(double& z:v.x) z=nd(rng); return v; }
static Vec noisy(std::mt19937_64& rng, const Vec& base, double sigma){ Vec v((int)base.x.size()); std::normal_distribution<double> nd(0.0,sigma); for(size_t i=0;i<base.x.size();++i) v.x[i]=base.x[i]+nd(rng); normalize(v); return v; }

static Vec quantize(const Vec& v, int bits){
    if(bits>=16) return v;
    double mx=0; for(double z:v.x) mx=std::max(mx,std::abs(z));
    if(mx<1e-12) return v;
    int levels=(1<<(bits-1))-1; if(levels<1) levels=1;
    Vec q((int)v.x.size());
    for(size_t i=0;i<v.x.size();++i){ double r=std::round(v.x[i]/mx*levels); r=std::max((double)-levels,std::min((double)levels,r)); q.x[i]=r/levels*mx; }
    return q;
}

static std::vector<double> softmax_logits(const std::vector<double>& logits){
    double mx=*std::max_element(logits.begin(), logits.end()); double z=0; std::vector<double> p(logits.size());
    for(size_t i=0;i<logits.size();++i){ p[i]=std::exp(logits[i]-mx); z+=p[i]; }
    for(double& x:p) x/=std::max(1e-30,z); return p;
}
static Vec attention(const Vec& q, const std::vector<Vec>& k, const std::vector<Vec>& v, double temp, std::vector<double>* out_attn=nullptr){
    int d=(int)q.x.size(); Vec out(d); if(k.empty()) return out;
    std::vector<double> logits(k.size()); for(size_t i=0;i<k.size();++i) logits[i]=dot(q,k[i])/std::max(1e-9,temp);
    std::vector<double> p=softmax_logits(logits); if(out_attn) *out_attn=p;
    for(size_t i=0;i<v.size();++i) for(int j=0;j<d;++j) out.x[j]+=p[i]*v[i].x[j];
    return out;
}

static World make_world(int seed, const std::string& scenario, int n=512, int d=32){
    std::mt19937_64 rng(seed); World w; w.k.resize(n); w.v.resize(n); w.age.resize(n); w.sponsor.assign(n,0.0);
    for(int i=0;i<n;++i){ w.k[i]=randn_vec(rng,d); normalize(w.k[i]); w.v[i]=randn_vec(rng,d); normalize(w.v[i]); w.age[i]=(double)i/std::max(1,n-1); }
    w.target=(int)(rng()%(n/4)); w.q=noisy(rng,w.k[w.target],0.03); w.temp=0.08; w.sponsor[w.target]=1.0;
    if(scenario=="broad_low_precision_ok"){
        w.temp=0.24; for(int c=0;c<n/6;++c){ int idx=(int)(rng()%n); w.k[idx]=noisy(rng,w.q,0.24); w.v[idx]=noisy(rng,w.v[w.target],0.30); w.sponsor[idx]=0.35; }
    } else if(scenario=="sharp_quant_sensitive"){
        w.temp=0.035; for(int c=0;c<n/32;++c){ int idx=(int)(rng()%n); if(idx==w.target) continue; w.k[idx]=noisy(rng,w.q,0.055); for(double& z:w.v[idx].x) z=-z; }
    } else if(scenario=="dormant_value_outlier"){
        w.q=add_scaled(w.k[w.target], randn_vec(rng,d), 0.38, 0.62); normalize(w.q); w.temp=0.12; for(double& z:w.v[w.target].x) z*=7.0;
        for(int c=0;c<n/24;++c){ int idx=(int)(rng()%n); if(idx==w.target) continue; w.k[idx]=noisy(rng,w.q,0.18); }
    } else if(scenario=="distractor_value_outlier"){
        w.temp=0.09; for(int c=0;c<n/24;++c){ int idx=(int)(rng()%n); if(idx==w.target) continue; for(double& z:w.v[idx].x) z*=9.0; }
    } else if(scenario=="recent_anchor_old_payload"){
        int anchor=n-8; w.k[anchor]=noisy(rng,w.q,0.06); w.v[anchor]=noisy(rng,w.v[w.target],0.65); for(double& z:w.v[w.target].x) z*=4.0; w.sponsor[anchor]=0.65; w.temp=0.07;
    }
    return w;
}

static std::vector<int> topk(const std::vector<double>& score, int k){
    k=std::max(0,std::min((int)score.size(),k)); std::vector<int> idx(score.size()); std::iota(idx.begin(),idx.end(),0);
    std::partial_sort(idx.begin(), idx.begin()+k, idx.end(), [&](int a,int b){return score[a]>score[b];}); idx.resize(k); return idx;
}
struct Plan { std::vector<int> idx; std::vector<int> bits; };
static Plan plan_policy(const World& w, const std::string& policy, int budget4, int d){
    int budget_bits=budget4*2*d*4; int n=(int)w.k.size(); std::vector<double> att(n), val(n), score(n);
    for(int i=0;i<n;++i){ att[i]=dot(w.q,w.k[i]); val[i]=norm(w.v[i]); }
    auto cap=[&](int bits){ return std::max(1,std::min(n,budget_bits/std::max(1,2*d*bits))); };
    auto mk=[&](const std::vector<double>& s, int bits){ Plan p; p.idx=topk(s,cap(bits)); p.bits.assign(p.idx.size(),bits); return p; };
    if(policy=="few_8bit_attention") return mk(att,8);
    if(policy=="more_4bit_attention") return mk(att,4);
    if(policy=="many_2bit_attention") return mk(att,2);
    if(policy=="value_protected_4bit"){ for(int i=0;i<n;++i) score[i]=att[i]+0.30*val[i]; return mk(score,4); }
    if(policy=="semantic_sponsor_4bit"){ for(int i=0;i<n;++i) score[i]=att[i]+1.00*w.sponsor[i]+0.20*val[i]; return mk(score,4); }
    if(policy=="mixed_8_4_2"){
        for(int i=0;i<n;++i) score[i]=att[i]+0.05*w.age[i]+0.08*val[i];
        std::vector<int> order=topk(score,n); Plan p; int rem=budget_bits;
        for(auto [bits, frac] : std::vector<std::pair<int,double>>{{8,0.28},{4,0.42},{2,1.0}}){
            int maxc = bits==2 ? rem/std::max(1,2*d*bits) : (int)((budget_bits*frac)/std::max(1,2*d*bits)); int added=0;
            for(int idx: order){ if(rem<2*d*bits || added>=maxc) break; if(std::find(p.idx.begin(),p.idx.end(),idx)==p.idx.end()){ p.idx.push_back(idx); p.bits.push_back(bits); rem-=2*d*bits; ++added; } }
        } return p;
    }
    if(policy=="oracle_target_4bit"){ score=att; score[w.target]+=1e6; return mk(score,4); }
    return mk(att,4);
}
static Row eval(int seed, const std::string& scenario, const std::string& policy, int budget4){
    World w=make_world(seed,scenario); int d=(int)w.q.x.size(); std::vector<double> ref_attn; Vec ref=attention(w.q,w.k,w.v,w.temp,&ref_attn);
    Plan pl=plan_policy(w,policy,budget4,d); std::vector<Vec> kk,vv; kk.reserve(pl.idx.size()); vv.reserve(pl.idx.size()); double used=0, bit_sum=0;
    for(size_t j=0;j<pl.idx.size();++j){ kk.push_back(quantize(w.k[pl.idx[j]],pl.bits[j])); vv.push_back(quantize(w.v[pl.idx[j]],pl.bits[j])); used += 2*d*pl.bits[j]; bit_sum += pl.bits[j]; }
    Vec out=attention(w.q,kk,vv,w.temp); Vec diff=add_scaled(out,ref,1.0,-1.0);
    double dropped=1.0; for(int idx:pl.idx) dropped-=ref_attn[idx]; bool target=std::find(pl.idx.begin(),pl.idx.end(),w.target)!=pl.idx.end();
    Row r; r.scenario=scenario; r.policy=policy; r.budget4=budget4; r.rel_error=norm(diff)/std::max(1e-12,norm(ref)); r.cosine=dot(out,ref)/(norm(out)*norm(ref)+1e-12); r.dropped_mass=std::max(0.0,dropped); r.target_ret=target?1.0:0.0; r.tokens=(double)pl.idx.size(); r.mean_bits=pl.bits.empty()?0.0:bit_sum/pl.bits.size(); r.n=1; return r;
}
static void accum(Row& a, const Row& b){ a.rel_error+=b.rel_error; a.cosine+=b.cosine; a.dropped_mass+=b.dropped_mass; a.target_ret+=b.target_ret; a.tokens+=b.tokens; a.mean_bits+=b.mean_bits; a.n+=1; }
static std::string esc(const std::string& s){ std::string o; for(char c:s){ if(c=='"') o+="\\\""; else if(c=='\\') o+="\\\\"; else o+=c; } return o; }

int main(int argc, char** argv){
    std::string out="artifacts/probe-results/REV0016_NATIVE_TOKEN_PRECISION_FRONTIER_SMOKE.json"; if(argc>1) out=argv[1]; auto t0=std::chrono::high_resolution_clock::now();
    std::vector<std::string> scenarios={"broad_low_precision_ok","sharp_quant_sensitive","dormant_value_outlier","distractor_value_outlier","recent_anchor_old_payload"};
    std::vector<std::string> policies={"few_8bit_attention","more_4bit_attention","many_2bit_attention","value_protected_4bit","semantic_sponsor_4bit","mixed_8_4_2","oracle_target_4bit"};
    std::vector<int> budgets={16,32,64}; std::map<std::string,Row> table;
    for(int seed=0; seed<12; ++seed) for(auto& sc:scenarios) for(int b:budgets) for(auto& po:policies){ Row r=eval(1000+seed*97,sc,po,b); std::string key=sc+"|"+po+"|"+std::to_string(b); if(!table.count(key)){ table[key]=r; table[key].n=0; table[key].rel_error=table[key].cosine=table[key].dropped_mass=table[key].target_ret=table[key].tokens=table[key].mean_bits=0; } accum(table[key],r); }
    std::map<std::string,int> winners; for(auto& sc:scenarios) for(int b:budgets){ double best=1e300; std::string bp; for(auto& po:policies){ auto& r=table[sc+"|"+po+"|"+std::to_string(b)]; double e=r.rel_error/std::max(1,r.n); if(e<best){best=e; bp=po;} } winners[bp]++; }
    auto t1=std::chrono::high_resolution_clock::now(); double sec=std::chrono::duration<double>(t1-t0).count();
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0016\",\n  \"probe\": \"native_token_precision_frontier\",\n";
    f<<"  \"config\": {\"seeds\": 12, \"dimension\": 32, \"tokens\": 512},\n";
    f<<"  \"summary\": {\"row_count\": "<<table.size()<<", \"seconds\": "<<sec<<", \"primary_metric\": {\"name\": \"mean_output_rel_error\", \"direction\": \"lower_is_better\", \"winner_field\": \"winner_counts\"}, \"winner_counts\": {";
    bool first=true; for(auto& kv:winners){ if(!first) f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second; } f<<"}},\n  \"rows\": [\n";
    int c=0; for(auto& kv:table){ auto r=kv.second; double n=std::max(1,r.n); if(c++) f<<",\n"; f<<"    {\"scenario\": \""<<esc(r.scenario)<<"\", \"policy\": \""<<esc(r.policy)<<"\", \"budget_equiv_4bit_tokens\": "<<r.budget4<<", \"mean_output_rel_error\": "<<r.rel_error/n<<", \"mean_output_cosine\": "<<r.cosine/n<<", \"mean_dropped_attention_mass\": "<<r.dropped_mass/n<<", \"target_retention_rate\": "<<r.target_ret/n<<", \"mean_retained_tokens\": "<<r.tokens/n<<", \"mean_bits\": "<<r.mean_bits/n<<"}"; }
    f<<"\n  ]\n}\n";
    std::cerr<<"wrote "<<out<<" rows="<<table.size()<<"\n"; return 0;
}
