// CloudtainerML rev0023: carried-forward native probe, current-revision emission.
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

static std::string q(const std::string& s){ return "\"" + s + "\""; }
struct Row{ std::string regime, method; int n, samples; double mse, value_rows_read, score; };

int main(int argc, char** argv){
    std::string out = argc>1 ? argv[1] : "REV0023_STOCHASTIC_SPARSE_ATTENTION_SMOKE.json";
    std::mt19937 rng(1414);
    std::normal_distribution<double> nd(0.0,1.0);
    std::uniform_real_distribution<double> uni(0.0,1.0);
    const int D=16;
    struct Regime{ std::string name; double concentration; double tail_value_scale; double entropy_bonus; };
    std::vector<Regime> regimes={{"peaked_attention",4.0,1.0,0.0},{"flat_attention",0.2,1.0,0.0},{"rare_high_value_tail",1.5,5.0,0.3},{"mid_entropy",1.0,1.0,0.0}};
    std::vector<int> Ns={256,1024,4096};
    std::vector<int> Ss={8,16,32,64,128};
    std::vector<Row> rows;
    for(const auto& rg:regimes) for(int N:Ns){
        std::vector<double> logits(N), w(N), values(N*D), exact(D,0.0);
        for(int i=0;i<N;i++){
            logits[i]=rg.concentration*nd(rng);
            if(rg.name=="peaked_attention" && i<4) logits[i]+=8.0;
            if(rg.name=="rare_high_value_tail" && i>N-8) logits[i]-=3.0;
            double scale=(rg.name=="rare_high_value_tail" && i>N-8)?rg.tail_value_scale:1.0;
            for(int d=0;d<D;d++) values[i*D+d]=scale*nd(rng);
        }
        double mx=*std::max_element(logits.begin(),logits.end()), z=0;
        for(int i=0;i<N;i++){ w[i]=std::exp(logits[i]-mx); z+=w[i]; }
        for(int i=0;i<N;i++){ w[i]/=z; for(int d=0;d<D;d++) exact[d]+=w[i]*values[i*D+d]; }
        std::discrete_distribution<int> post(w.begin(), w.end());
        for(int S:Ss){
            auto add_row=[&](const std::string& method, double mse, double read){ double score=mse + 0.00005*read; rows.push_back({rg.name,method,N,S,mse,read,score}); };
            // top-k exact sparse baseline
            std::vector<int> idx(N); std::iota(idx.begin(),idx.end(),0); std::partial_sort(idx.begin(), idx.begin()+std::min(S,N), idx.end(), [&](int a,int b){return w[a]>w[b];});
            std::vector<double> top(D,0.0); double topmass=0; for(int j=0;j<std::min(S,N);j++){ int i=idx[j]; topmass+=w[i]; for(int d=0;d<D;d++) top[d]+=w[i]*values[i*D+d]; }
            if(topmass>1e-12) for(double& x: top) x/=topmass;
            double mse=0, denom=0; for(int d=0;d<D;d++){ mse+=(top[d]-exact[d])*(top[d]-exact[d]); denom+=exact[d]*exact[d]+1e-9; } add_row("topk_renorm",mse/denom,S);
            // post-softmax Monte Carlo: unbiased for value aggregation if scaled average; variance can be high.
            std::vector<double> mc(D,0.0); int trials=64;
            for(int tr=0;tr<trials;tr++){
                std::vector<double> acc(D,0.0); for(int s=0;s<S;s++){ int i=post(rng); for(int d=0;d<D;d++) acc[d]+=values[i*D+d]; }
                for(int d=0;d<D;d++) mc[d]+=acc[d]/S;
            }
            for(double& x: mc) x/=trials; mse=0; denom=0; for(int d=0;d<D;d++){ mse+=(mc[d]-exact[d])*(mc[d]-exact[d]); denom+=exact[d]*exact[d]+1e-9; } add_row("santa_postsoftmax_mc",mse/denom,S);
            // stratified proxy: split cumulative mass into S bins and sample one per bin.
            std::vector<double> strat(D,0.0); trials=64; std::vector<double> cdf(N); std::partial_sum(w.begin(),w.end(),cdf.begin());
            for(int tr=0;tr<trials;tr++){
                std::vector<double> acc(D,0.0); for(int s=0;s<S;s++){ double u=(s+uni(rng))/S; int i=std::lower_bound(cdf.begin(),cdf.end(),u)-cdf.begin(); if(i>=N) i=N-1; for(int d=0;d<D;d++) acc[d]+=values[i*D+d]; }
                for(int d=0;d<D;d++) strat[d]+=acc[d]/S;
            }
            for(double& x: strat) x/=trials; mse=0; denom=0; for(int d=0;d<D;d++){ mse+=(strat[d]-exact[d])*(strat[d]-exact[d]); denom+=exact[d]*exact[d]+1e-9; } add_row("stratified_mc",mse/denom,S);
            // value-aware oracle-ish sampler to expose rare high-value traps.
            std::vector<double> score(N); for(int i=0;i<N;i++){ double vn=0; for(int d=0;d<D;d++) vn+=values[i*D+d]*values[i*D+d]; score[i]=w[i]*std::sqrt(vn); }
            std::iota(idx.begin(),idx.end(),0); std::partial_sort(idx.begin(), idx.begin()+std::min(S,N), idx.end(), [&](int a,int b){return score[a]>score[b];});
            std::vector<double> va(D,0.0); double mass=0; for(int j=0;j<std::min(S,N);j++){ int i=idx[j]; mass+=w[i]; for(int d=0;d<D;d++) va[d]+=w[i]*values[i*D+d]; } if(mass>1e-12) for(double& x: va)x/=mass;
            mse=0; denom=0; for(int d=0;d<D;d++){ mse+=(va[d]-exact[d])*(va[d]-exact[d]); denom+=exact[d]*exact[d]+1e-9; } add_row("value_aware_topk",mse/denom,S);
        }
    }
    std::map<std::string,int> winners;
    for(const auto& rg:regimes) for(int N:Ns) for(int S:Ss){ const Row* best=nullptr; for(const auto& r:rows) if(r.regime==rg.name&&r.n==N&&r.samples==S){ if(!best||r.score<best->score) best=&r; } if(best) winners[best->method]++; }
    std::ofstream f(out); f<<std::fixed<<std::setprecision(7);
    f << "{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"stochastic_sparse_attention\",\n";
    f << "  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto& kv:winners){ if(!first) f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second; } f << "},\n";
    f << "    \"interpretation\": \"SANTA-like post-softmax sampling is attractive on bandwidth, but top-k/stratified/value-aware methods win in different synthetic regimes. Rare high-value tails are the adversarial case.\"\n  },\n  \"rows\": [\n";
    for(size_t i=0;i<rows.size();++i){ const auto& r=rows[i]; f << "    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"n\": "<<r.n<<", \"samples\": "<<r.samples<<", \"mse\": "<<r.mse<<", \"value_rows_read\": "<<r.value_rows_read<<", \"score\": "<<r.score<<"}" << (i+1==rows.size()?"\n":",\n"); }
    f << "  ]\n}\n"; std::cout << "wrote " << out << " rows=" << rows.size() << "\n"; return 0;
}
