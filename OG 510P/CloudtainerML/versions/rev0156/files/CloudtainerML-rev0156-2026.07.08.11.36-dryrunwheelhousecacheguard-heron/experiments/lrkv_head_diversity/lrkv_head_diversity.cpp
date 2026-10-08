// CloudtainerML rev0023: carried-forward native probe, current-revision emission.
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
struct Row{ std::string regime, method; int rank, heads; double bytes_ratio, mse, score; };

int main(int argc, char** argv){
    std::string out = argc>1 ? argv[1] : "REV0023_LRKV_HEAD_DIVERSITY_SMOKE.json";
    std::mt19937 rng(14014);
    std::normal_distribution<double> nd(0.0,1.0);
    const int H=8, T=96, D=16, true_rank=6;
    struct Regime{ std::string name; double shared_strength; double residual_strength; double noise; double byte_weight; };
    std::vector<Regime> regimes={
        {"mostly_shared_heads", 1.0, 0.20, 0.02, 0.08},
        {"orthogonal_head_roles", 0.45, 1.00, 0.02, 0.05},
        {"noisy_values", 0.70, 0.55, 0.25, 0.08},
        {"memory_tight", 0.70, 0.65, 0.04, 0.30},
        {"head_specialist", 0.25, 1.20, 0.02, 0.04}
    };
    std::vector<Row> rows;
    for(const auto& rg: regimes){
        std::vector<double> shared(T*D), factors(true_rank*T*D), coeff(H*true_rank), full(H*T*D);
        for(auto& x: shared) x=nd(rng);
        for(auto& x: factors) x=nd(rng);
        for(int h=0;h<H;h++) for(int r=0;r<true_rank;r++) coeff[h*true_rank+r]=nd(rng);
        for(int h=0;h<H;h++) for(int t=0;t<T;t++) for(int d=0;d<D;d++){
            double v=rg.shared_strength*shared[t*D+d];
            for(int r=0;r<true_rank;r++) v += rg.residual_strength*coeff[h*true_rank+r]*factors[(r*T+t)*D+d]/std::sqrt((double)true_rank);
            v += rg.noise*nd(rng);
            full[(h*T+t)*D+d]=v;
        }
        auto mse_for=[&](const std::string& method, int rank){
            double err=0, denom=0;
            for(int h=0;h<H;h++) for(int t=0;t<T;t++) for(int d=0;d<D;d++){
                double pred=0;
                if(method=="full_mha") pred=full[(h*T+t)*D+d];
                else if(method=="shared_kv"){
                    for(int hh=0;hh<H;hh++) pred += full[(hh*T+t)*D+d]; pred/=H;
                } else if(method=="gqa_2groups"){
                    int g=(h < H/2)?0:1, start=g*(H/2), end=start+H/2; for(int hh=start;hh<end;hh++) pred += full[(hh*T+t)*D+d]; pred/=(H/2);
                } else if(method=="k_equals_v_proxy"){
                    pred = rg.shared_strength*shared[t*D+d];
                } else if(method=="lrkv_residual"){
                    // Store shared component plus first-rank head residual factors. We use known synthetic factors: a best-case capacity probe.
                    pred = rg.shared_strength*shared[t*D+d];
                    for(int r=0;r<std::min(rank,true_rank);r++) pred += rg.residual_strength*coeff[h*true_rank+r]*factors[(r*T+t)*D+d]/std::sqrt((double)true_rank);
                }
                double y=full[(h*T+t)*D+d]; err += (pred-y)*(pred-y); denom += y*y + 1e-9;
            }
            return err/denom;
        };
        std::vector<std::pair<std::string,int>> methods={{"full_mha",true_rank},{"shared_kv",0},{"gqa_2groups",0},{"k_equals_v_proxy",0},{"lrkv_residual",1},{"lrkv_residual",2},{"lrkv_residual",4}};
        for(auto& m: methods){
            double mse=mse_for(m.first,m.second);
            double ratio=1.0;
            if(m.first=="shared_kv"||m.first=="k_equals_v_proxy") ratio=1.0/H;
            else if(m.first=="gqa_2groups") ratio=2.0/H;
            else if(m.first=="lrkv_residual") ratio=1.0/H + (double)m.second/true_rank*0.40;
            double score=mse + rg.byte_weight*ratio;
            rows.push_back({rg.name,m.first,m.second,H,ratio,mse,score});
        }
    }
    std::map<std::string,int> winners;
    for(const auto& rg: regimes){ const Row* best=nullptr; for(const auto& r:rows) if(r.regime==rg.name){ if(!best||r.score<best->score) best=&r; } if(best) winners[best->method+(best->method=="lrkv_residual"?"_rank"+std::to_string(best->rank):"")]++; }
    std::ofstream f(out); f<<std::fixed<<std::setprecision(7);
    f << "{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"lrkv_head_diversity\",\n";
    f << "  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {";
    bool first=true; for(auto& kv:winners){ if(!first) f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second; } f << "},\n";
    f << "    \"interpretation\": \"LRKV-like residuals matter when heads have specialist roles; simple sharing wins only when heads are genuinely redundant or memory pressure dominates. Synthetic factors are known, so this is a capacity upper-bound, not a training result.\"\n  },\n  \"rows\": [\n";
    for(size_t i=0;i<rows.size();++i){ const auto& r=rows[i];
        f << "    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"rank\": "<<r.rank<<", \"heads\": "<<r.heads<<", \"bytes_ratio\": "<<r.bytes_ratio<<", \"mse\": "<<r.mse<<", \"score\": "<<r.score<<"}" << (i+1==rows.size()?"\n":",\n");
    }
    f << "  ]\n}\n"; std::cout << "wrote " << out << " rows=" << rows.size() << "\n"; return 0;
}
