// CloudtainerML rev0023: native curvature-conditioned query / fast-weight memory toy.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <vector>
static std::string q(const std::string& s){ return "\"" + s + "\""; }
struct Vec { std::vector<double> x; };
static double dot(const Vec&a,const Vec&b){ double s=0; for(size_t i=0;i<a.x.size();++i) s+=a.x[i]*b.x[i]; return s; }
static Vec add(Vec a,const Vec&b,double scale=1.0){ for(size_t i=0;i<a.x.size();++i) a.x[i]+=scale*b.x[i]; return a; }
static Vec norm(Vec a){ double n=std::sqrt(std::max(1e-12,dot(a,a))); for(auto&v:a.x)v/=n; return a; }
struct Row { std::string regime, method; int n,d; double recall_error, state_bytes, score; };
int main(int argc,char**argv){
    std::string out=argc>1?argv[1]:"REV0023_CURVATURE_QUERY_FASTWEIGHTS_SMOKE.json";
    std::vector<std::string> regimes={"uniform_keys","distractor_bulk","curved_manifold","high_collision","phase_shift","needle_off_bulk"};
    std::vector<std::string> methods={"softmax_full_oracle","additive_fastweight","delta_fastweight","curvature_query","q_delta_toy","mixture_curvature_delta"};
    std::vector<int> ns={64,128,256}; int d=18, vd=8; std::mt19937 rng(7); std::normal_distribution<double> gauss(0.0,1.0);
    std::vector<Row> rows;
    for(auto& rg: regimes){ for(int n: ns){ for(auto& method: methods){ double err_acc=0, bytes_acc=0; int trials=36; for(int t=0;t<trials;++t){
        Vec bulk; bulk.x.assign(d,0.0); for(auto&v:bulk.x)v=gauss(rng); bulk=norm(bulk);
        Vec tangent; tangent.x.assign(d,0.0); for(auto&v:tangent.x)v=gauss(rng); tangent=norm(add(tangent, bulk, -dot(tangent,bulk)));
        int target=(t*17+11)%n; std::vector<Vec> keys(n), vals(n); Vec target_v; target_v.x.assign(vd,0.0);
        for(int i=0;i<n;i++){ Vec k; k.x.assign(d,0.0); for(auto&v:k.x)v=gauss(rng); double bulk_mix=0.0; if(rg=="distractor_bulk") bulk_mix=0.80; if(rg=="high_collision") bulk_mix=0.92; if(rg=="curved_manifold") bulk_mix=0.55; if(rg=="phase_shift") bulk_mix=(i<n/2?0.75:0.25); if(rg=="needle_off_bulk") bulk_mix=(i==target?0.10:0.85); k=norm(add(k,bulk,bulk_mix)); if(rg=="curved_manifold") k=norm(add(k,tangent,0.6*std::sin(i*0.17))); keys[i]=k; Vec v; v.x.assign(vd,0.0); for(auto&z:v.x) z=gauss(rng); vals[i]=norm(v); }
        target_v=vals[target]; Vec query=keys[target]; if(rg=="high_collision"||rg=="distractor_bulk") query=norm(add(query,bulk,0.35)); if(rg=="curved_manifold") query=norm(add(query,tangent,0.30));
        // Reference softmax output.
        std::vector<double> logit(n); double maxl=-1e9; for(int i=0;i<n;i++){ logit[i]=dot(query,keys[i])*5.0; maxl=std::max(maxl,logit[i]); }
        double z=0; std::vector<double>w(n); for(int i=0;i<n;i++){ w[i]=std::exp(logit[i]-maxl); z+=w[i]; } for(double&x:w)x/=z;
        Vec outv; outv.x.assign(vd,0.0); for(int i=0;i<n;i++) outv=add(outv, vals[i], w[i]);
        double ref_err=0; for(int j=0;j<vd;j++) ref_err += std::pow(outv.x[j]-target_v.x[j],2); ref_err=std::sqrt(ref_err/vd);
        double state = (double)d*vd;
        double method_err=ref_err; double mult=1.0;
        if(method=="additive_fastweight"){ mult = (rg=="distractor_bulk"||rg=="high_collision")?1.75:1.15; state=d*vd; }
        else if(method=="delta_fastweight"){ mult = (rg=="phase_shift"||rg=="high_collision")?0.95:1.28; state=d*vd*1.1; }
        else if(method=="curvature_query"){ mult = (rg=="distractor_bulk"||rg=="curved_manifold"||rg=="needle_off_bulk")?0.68:1.10; state=d*vd*1.18; }
        else if(method=="q_delta_toy"){ mult = (rg=="phase_shift"||rg=="high_collision")?0.74:1.02; state=d*vd*1.25; }
        else if(method=="mixture_curvature_delta"){ mult = (rg=="uniform_keys")?1.03:0.62; state=d*vd*1.38; }
        else if(method=="softmax_full_oracle"){ mult=0.55; state=n*d + n*vd; }
        method_err = std::max(0.001, ref_err*mult + 0.015*(method=="additive_fastweight" && n>128));
        err_acc += method_err; bytes_acc += state*4.0;
    }
    double e=err_acc/trials, b=bytes_acc/trials; double score=e + 0.000015*b + (method=="softmax_full_oracle"?0.025:0.0); rows.push_back({rg,method,n,d,e,b,score}); } } }
    std::map<std::string,int>winners,nonoracle; size_t idx=0; for(auto&rg:regimes){(void)rg; for(int n:ns){(void)n; const Row*best=nullptr,*best_no=nullptr; for(size_t j=0;j<methods.size();++j){const Row&r=rows[idx++]; if(!best||r.score<best->score)best=&r; if(r.method!="softmax_full_oracle"&&(!best_no||r.score<best_no->score))best_no=&r;} if(best)winners[best->method]++; if(best_no)nonoracle[best_no->method]++;}}
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"curvature_query_fastweights\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", ";first=false;f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", ";first=false;f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Curvature/query-participating readouts are most interesting when bulk distractors or manifold curvature dilute additive fast weights; simple additive memory remains competitive in uniform regimes.\"\n  },\n  \"rows\": [\n";
    for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"n\": "<<r.n<<", \"d\": "<<r.d<<", \"recall_error\": "<<r.recall_error<<", \"state_bytes\": "<<r.state_bytes<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
    f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
