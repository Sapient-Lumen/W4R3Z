// CloudtainerML rev0023: native phase-boundary optimizer probe.
// C++17, dependency-free. Inspired by the Centaur/autoresearch lesson: pure
// LLM/domain priors are not enough, pure black-box search is often wasteful;
// hybrid optimizer state + domain-biased proposals can be better for choosing
// probe constants. This is a toy optimizer arena over synthetic phase diagrams,
// not a reproduction of the paper.

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

struct X { double a=0,b=0; };
struct Eval { double score=0, regret=0; };
struct Row { std::string landscape, method; int budget=0; double best=0, regret=0, calls=0; int n=0; };

static double clamp(double x,double lo,double hi){return std::max(lo,std::min(hi,x));}
static double sq(double x){return x*x;}
static std::string esc(const std::string& s){std::string o; for(char c:s){if(c=='"')o+="\\\"";else if(c=='\\')o+="\\\\";else o+=c;} return o;}

static double objective(const std::string& land, X x){
    x.a=clamp(x.a,0,1); x.b=clamp(x.b,0,1);
    if(land=="smooth_cache_phase"){
        return 1.15*std::exp(-30*sq(x.a-0.76)-18*sq(x.b-0.32)) + 0.25*std::exp(-70*sq(x.a-0.2)-40*sq(x.b-0.8));
    }
    if(land=="needle_ridge"){
        double ridge=std::exp(-120*sq(x.a+0.55*x.b-0.92));
        double gate=1.0/(1.0+std::exp(-45*(x.a-0.34)));
        return ridge*gate + 0.08*std::sin(24*x.b+3*x.a);
    }
    if(land=="deceptive_plateau"){
        double plateau=0.62*std::exp(-3.0*(sq(x.a-0.35)+sq(x.b-0.35)));
        double spike=1.25*std::exp(-180*sq(x.a-0.87)-120*sq(x.b-0.74));
        return plateau+spike;
    }
    if(land=="checker_aliasing"){
        double base=0.35*std::exp(-10*(sq(x.a-0.65)+sq(x.b-0.55)));
        double teeth=0.22*(std::sin(41*x.a)*std::sin(37*x.b)+1.0);
        double island=0.95*std::exp(-95*sq(x.a-0.18)-80*sq(x.b-0.82));
        return base+teeth+island;
    }
    return std::exp(-10*(sq(x.a-0.5)+sq(x.b-0.5)));
}

static double approx_optimum(const std::string& land){
    double best=-1e9; for(int i=0;i<=500;i++) for(int j=0;j<=500;j++){ X x{double(i)/500.0,double(j)/500.0}; best=std::max(best,objective(land,x)); } return best;
}
static X randx(std::mt19937_64& rng){ std::uniform_real_distribution<double> U(0,1); return {U(rng),U(rng)}; }
static X domain_prior(const std::string& land, std::mt19937_64& rng){
    std::normal_distribution<double> N(0,0.12);
    if(land=="smooth_cache_phase") return {clamp(0.72+N(rng),0,1),clamp(0.36+N(rng),0,1)};
    if(land=="needle_ridge") return {clamp(0.58+N(rng),0,1),clamp(0.58+N(rng),0,1)};
    if(land=="deceptive_plateau") return {clamp(0.38+N(rng),0,1),clamp(0.38+N(rng),0,1)}; // intentionally biased to plateau
    if(land=="checker_aliasing") return {clamp(0.50+N(rng),0,1),clamp(0.50+N(rng),0,1)};
    return randx(rng);
}
static std::vector<X> grid_points(int budget){
    int side=std::max(2,(int)std::floor(std::sqrt((double)budget)));
    std::vector<X> xs; for(int i=0;i<side;i++) for(int j=0;j<side;j++) xs.push_back({(i+0.5)/side,(j+0.5)/side});
    while((int)xs.size()<budget){ double t=(xs.size()+0.5)/budget; xs.push_back({t,0.61803398875*xs.size()-std::floor(0.61803398875*xs.size())}); }
    xs.resize(budget); return xs;
}
static Eval run_method(const std::string& land, const std::string& method, int budget, int seed, double opt){
    std::mt19937_64 rng(seed); double best=-1e9; std::vector<X> archive;
    auto eval=[&](X x){ x.a=clamp(x.a,0,1); x.b=clamp(x.b,0,1); archive.push_back(x); double y=objective(land,x); if(y>best) best=y; return y; };
    if(method=="grid") for(auto x:grid_points(budget)) eval(x);
    else if(method=="random") for(int i=0;i<budget;i++) eval(randx(rng));
    else if(method=="domain_prior") for(int i=0;i<budget;i++) eval(domain_prior(land,rng));
    else if(method=="cross_entropy"){
        double ma=0.5, mb=0.5, sa=0.35, sb=0.35; std::normal_distribution<double> N(0,1); int used=0;
        while(used<budget){ std::vector<std::pair<double,X>> batch; int bs=std::min(24,budget-used); for(int i=0;i<bs;i++){ X x{clamp(ma+sa*N(rng),0,1),clamp(mb+sb*N(rng),0,1)}; batch.push_back({eval(x),x}); used++; }
            std::sort(batch.begin(),batch.end(),[](auto&u,auto&v){return u.first>v.first;}); int elite=std::max(2,(int)batch.size()/4); double na=0,nb=0; for(int i=0;i<elite;i++){na+=batch[i].second.a; nb+=batch[i].second.b;} na/=elite; nb/=elite; double va=0,vb=0; for(int i=0;i<elite;i++){va+=sq(batch[i].second.a-na); vb+=sq(batch[i].second.b-nb);} ma=0.75*ma+0.25*na; mb=0.75*mb+0.25*nb; sa=clamp(std::sqrt(va/std::max(1,elite))+0.03,0.04,0.45); sb=clamp(std::sqrt(vb/std::max(1,elite))+0.03,0.04,0.45); }
    } else if(method=="centaur_state_prior"){
        // Mix optimizer-state CEM with a few domain-prior proposals and occasional random escape.
        double ma=0.5, mb=0.5, sa=0.35, sb=0.35; std::normal_distribution<double> N(0,1); std::uniform_real_distribution<double> U(0,1); int used=0;
        while(used<budget){ std::vector<std::pair<double,X>> batch; int bs=std::min(24,budget-used); for(int i=0;i<bs;i++){ X x; double r=U(rng); if(r<0.25) x=domain_prior(land,rng); else if(r<0.35) x=randx(rng); else x={clamp(ma+sa*N(rng),0,1),clamp(mb+sb*N(rng),0,1)}; batch.push_back({eval(x),x}); used++; }
            std::sort(batch.begin(),batch.end(),[](auto&u,auto&v){return u.first>v.first;}); int elite=std::max(2,(int)batch.size()/4); double na=0,nb=0; for(int i=0;i<elite;i++){na+=batch[i].second.a; nb+=batch[i].second.b;} na/=elite; nb/=elite; ma=0.55*ma+0.45*na; mb=0.55*mb+0.45*nb; double va=0,vb=0; for(int i=0;i<elite;i++){va+=sq(batch[i].second.a-na); vb+=sq(batch[i].second.b-nb);} sa=clamp(0.75*sa+0.25*(std::sqrt(va/std::max(1,elite))+0.04),0.04,0.45); sb=clamp(0.75*sb+0.25*(std::sqrt(vb/std::max(1,elite))+0.04),0.04,0.45); }
    }
    return {best,opt-best};
}
static void accum(Row& a,const Row& b){a.best+=b.best; a.regret+=b.regret; a.calls+=b.calls; a.n++;}

int main(int argc,char**argv){
    std::string out="artifacts/probe-results/REV0023_NATIVE_HPO_PHASE_SMOKE.json"; if(argc>1) out=argv[1]; auto t0=std::chrono::high_resolution_clock::now();
    std::vector<std::string> lands={"smooth_cache_phase","needle_ridge","deceptive_plateau","checker_aliasing"};
    std::vector<std::string> methods={"grid","random","domain_prior","cross_entropy","centaur_state_prior"};
    std::vector<int> budgets={24,48,96,192}; std::map<std::string,double> opt; for(auto&l:lands) opt[l]=approx_optimum(l);
    std::map<std::string,Row> rows; std::map<std::string,int> winners;
    for(int seed=0; seed<16; ++seed) for(auto& l:lands) for(int b:budgets){ double best=-1e9; std::string win; for(auto&m:methods){ Eval e=run_method(l,m,b,10000+seed*131+b*7,opt[l]); Row r; r.landscape=l; r.method=m; r.budget=b; r.best=e.score; r.regret=e.regret; r.calls=b; std::string key=l+"|"+m+"|"+std::to_string(b); if(!rows.count(key)){rows[key]=r; rows[key].best=rows[key].regret=rows[key].calls=0; rows[key].n=0;} accum(rows[key],r); if(e.score>best){best=e.score; win=m;} } winners[win]++; }
    double sec=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count();
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"native_hpo_phase\",\n";
    f<<"  \"config\": {\"seeds\": 16, \"budgets\": [24,48,96,192], \"landscapes\": 4},\n";
    f<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<sec<<", \"primary_metric\": {\"name\": \"mean_regret_to_dense_grid_optimum\", \"direction\": \"lower_is_better\", \"winner_field\": \"winner_counts\"}, \"winner_counts\": {";
    bool first=true; for(auto&kv:winners){ if(!first) f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second; } f<<"}},\n  \"rows\": [\n";
    int c=0; for(auto&kv:rows){Row r=kv.second; double n=std::max(1,r.n); if(c++) f<<",\n"; f<<"    {\"landscape\": \""<<esc(r.landscape)<<"\", \"method\": \""<<esc(r.method)<<"\", \"budget\": "<<r.budget<<", \"mean_best_score\": "<<r.best/n<<", \"mean_regret_to_dense_grid_optimum\": "<<r.regret/n<<", \"mean_calls\": "<<r.calls/n<<"}";}
    f<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
