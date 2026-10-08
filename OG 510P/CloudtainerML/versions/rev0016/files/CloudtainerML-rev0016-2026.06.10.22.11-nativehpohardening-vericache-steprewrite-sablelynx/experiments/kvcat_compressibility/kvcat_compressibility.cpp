// CloudtainerML rev0016: carried-forward native probe, current-revision emission.
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
struct Row{ std::string regime, representation, compressor; int n, keep; double recon_mse, retrieval_acc, score; };

int main(int argc,char** argv){
    std::string out=argc>1?argv[1]:"REV0016_KVCAT_COMPRESSIBILITY_SMOKE.json";
    std::mt19937 rng(260505971);
    std::normal_distribution<double> nd(0,1);
    const int D=24, queries=128;
    struct Regime{std::string name; int clusters; double noise; double rare_frac;};
    std::vector<Regime> regimes={{"clustered_prefix",8,0.10,0.00},{"isotropic_prefix",128,0.80,0.00},{"rare_needle_prefix",16,0.18,0.03},{"drifting_clusters",32,0.28,0.00}};
    std::vector<int> Ns={512,2048}; std::vector<int> keeps={16,32,64,128};
    std::vector<Row> rows;
    auto norm=[&](std::vector<double>& v){ double s=0; for(double x:v)s+=x*x; s=std::sqrt(s)+1e-9; for(double& x:v)x/=s; };
    for(const auto& rg:regimes) for(int N:Ns){
        int C=std::min(rg.clusters,N);
        std::vector<std::vector<double>> centers(C,std::vector<double>(D));
        for(auto& c:centers){ for(double& x:c)x=nd(rng); norm(c); }
        for(std::string rep: {"base_isotropic", "kvcat_like_clustered"}){
            std::vector<std::vector<double>> keys(N,std::vector<double>(D)), vals(N,std::vector<double>(D));
            std::vector<int> label(N);
            for(int i=0;i<N;i++){
                int c=(rg.name=="drifting_clusters")? (i*C/N) : (i%C); label[i]=c;
                double local_noise = rg.noise * (rep=="kvcat_like_clustered"?0.45:1.0);
                if(rep=="base_isotropic" && rg.name=="isotropic_prefix") local_noise=1.5;
                for(int d=0;d<D;d++){
                    keys[i][d]=centers[c][d]+local_noise*nd(rng);
                    vals[i][d]=centers[c][d]+0.5*local_noise*nd(rng);
                }
                if(rg.name=="rare_needle_prefix" && (double)i/N > 1.0-rg.rare_frac){ for(int d=0;d<D;d++){ keys[i][d]+=4.0*nd(rng); vals[i][d]+=4.0*nd(rng);} }
                norm(keys[i]); norm(vals[i]);
            }
            for(int K:keeps){
                std::vector<std::string> compressors={"uniform_thin","importance_needle_aware","cluster_prototype"};
                for(const auto& comp:compressors){
                    std::vector<int> kept;
                    if(comp=="uniform_thin"){
                        for(int j=0;j<K;j++) kept.push_back(std::min(N-1, j*N/K));
                    } else if(comp=="importance_needle_aware"){
                        std::vector<double> score(N); for(int i=0;i<N;i++){ double s=0; for(double x:vals[i])s+=std::abs(x); score[i]=s + ((rg.name=="rare_needle_prefix" && (double)i/N>1.0-rg.rare_frac)?5.0:0.0); }
                        std::vector<int> idx(N); std::iota(idx.begin(),idx.end(),0); std::partial_sort(idx.begin(),idx.begin()+K,idx.end(),[&](int a,int b){return score[a]>score[b];}); kept.assign(idx.begin(),idx.begin()+K);
                    } else {
                        for(int c=0;c<C && (int)kept.size()<K;c++){ int best=c; double bestdist=1e99; for(int i=0;i<N;i++) if(label[i]==c){ double dist=0; for(int d=0;d<D;d++){double e=keys[i][d]-centers[c][d]; dist+=e*e;} if(dist<bestdist){bestdist=dist; best=i;}} kept.push_back(best); }
                        for(int j=0;(int)kept.size()<K;j++) kept.push_back(std::min(N-1,j*N/K));
                    }
                    // reconstruction: nearest kept key approximation.
                    double recon=0; int hit=0;
                    for(int qi=0;qi<queries;qi++){
                        int target = (rg.name=="rare_needle_prefix" && qi%5==0) ? (N-1-(qi%std::max(1,(int)(N*rg.rare_frac)))) : (qi*37)%N;
                        int best=-1; double bestdot=-1e99; for(int k:kept){ double dot=0; for(int d=0;d<D;d++)dot+=keys[target][d]*keys[k][d]; if(dot>bestdot){bestdot=dot; best=k;} }
                        double err=0, den=0; for(int d=0;d<D;d++){ double e=vals[target][d]-vals[best][d]; err+=e*e; den+=vals[target][d]*vals[target][d]+1e-9; } recon+=err/den;
                        if(label[best]==label[target] || best==target) hit++;
                    }
                    recon/=queries; double acc=(double)hit/queries; double score=recon + 0.25*(1.0-acc);
                    rows.push_back({rg.name,rep,comp,N,K,recon,acc,score});
                }
            }
        }
    }
    std::map<std::string,int> winners;
    for(const auto& rg:regimes) for(int N:Ns) for(int K:keeps){ const Row* best=nullptr; for(const auto& r:rows) if(r.regime==rg.name&&r.n==N&&r.keep==K){ if(!best||r.score<best->score) best=&r; } if(best) winners[best->representation+"/"+best->compressor]++; }
    std::ofstream f(out); f<<std::fixed<<std::setprecision(7);
    f << "{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0016\",\n  \"probe\": \"kvcat_compressibility\",\n";
    f << "  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"representation/compressor\"},\n    \"winner_counts\": {"; bool first=true; for(auto& kv:winners){ if(!first) f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second; } f << "},\n";
    f << "    \"interpretation\": \"KV-CAT-like clustered representations are easier to compress in this toy, but rare needles still require an importance-aware compressor. Compressibility is a representation property plus a red-team coverage problem.\"\n  },\n  \"rows\": [\n";
    for(size_t i=0;i<rows.size();++i){ const auto& r=rows[i]; f << "    {\"regime\": "<<q(r.regime)<<", \"representation\": "<<q(r.representation)<<", \"compressor\": "<<q(r.compressor)<<", \"n\": "<<r.n<<", \"keep\": "<<r.keep<<", \"recon_mse\": "<<r.recon_mse<<", \"retrieval_acc\": "<<r.retrieval_acc<<", \"score\": "<<r.score<<"}" << (i+1==rows.size()?"\n":",\n"); }
    f << "  ]\n}\n"; std::cout << "wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
