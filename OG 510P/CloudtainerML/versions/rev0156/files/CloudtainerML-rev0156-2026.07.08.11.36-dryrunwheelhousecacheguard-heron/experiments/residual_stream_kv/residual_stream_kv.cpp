// CloudtainerML rev0023: residual-stream versus full-KV cache object probe.
// Inspired by the question: if K/V are deterministic projections of residual
// states, when is it better to store residual checkpoints and recompute KV than
// to store every layer's KV? This toy tests exact reconstruction and a byte/time
// cost frontier. It is not a reproduction of KV-Direct.

#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <random>
#include <sstream>
#include <string>
#include <vector>

static double randn(std::mt19937_64& rng){ static thread_local std::normal_distribution<double> nd(0.0,1.0); return nd(rng); }
static std::string esc(const std::string& s){ std::string o; for(char c:s){ if(c=='"') o+="\\\""; else if(c=='\\') o+="\\\\"; else o+=c; } return o; }

struct Row { int tokens,layers,hidden,kv_dim,bytes; std::string policy; double state_mb, rel_bytes, estimated_decode_us, reconstruction_mse; };

int main(int argc, char** argv){
    std::string out="artifacts/probe-results/REV0023_RESIDUAL_STREAM_KV_SMOKE.json"; if(argc>1) out=argv[1]; auto t0=std::chrono::high_resolution_clock::now();
    // Exactness sanity: small random residuals and projections. Store KV versus recompute from residual.
    std::mt19937_64 rng(424242); int Tsmall=64, Lsmall=4, H=32, D=16; std::vector<double> R(Tsmall*Lsmall*H), Wk(Lsmall*H*D), Wv(Lsmall*H*D), K(Tsmall*Lsmall*D), V(Tsmall*Lsmall*D), Kr(K.size()), Vr(V.size());
    for(double& z:R) z=randn(rng); for(double& z:Wk) z=randn(rng)/std::sqrt((double)H); for(double& z:Wv) z=randn(rng)/std::sqrt((double)H);
    auto proj=[&](std::vector<double>& Ko, std::vector<double>& Vo){
        for(int t=0;t<Tsmall;++t) for(int l=0;l<Lsmall;++l) for(int d=0;d<D;++d){ double sk=0,sv=0; for(int h=0;h<H;++h){ double r=R[(t*Lsmall+l)*H+h]; sk+=r*Wk[(l*H+h)*D+d]; sv+=r*Wv[(l*H+h)*D+d]; } Ko[(t*Lsmall+l)*D+d]=sk; Vo[(t*Lsmall+l)*D+d]=sv; }
    }; proj(K,V); proj(Kr,Vr); double mse=0; for(size_t i=0;i<K.size();++i){ double ek=K[i]-Kr[i], ev=V[i]-Vr[i]; mse+=ek*ek+ev*ev; } mse/=std::max<size_t>(1,2*K.size());
    std::vector<int> token_grid={1024,8192,65536,262144}; std::vector<int> layer_grid={8,24,48}; std::vector<int> hidden_grid={768,2048,4096}; int bytes=2; // fp16/bf16 state bytes
    std::vector<Row> rows; const double bandwidth_GBs=900.0; const double flops_TF=40.0; // deliberately CPU/GPU-agnostic rough constants for phase boundary only
    for(int T:token_grid) for(int L:layer_grid) for(int hidden:hidden_grid){ int kv_dim=hidden; double full_bytes=(double)T*L*2*kv_dim*bytes; double residual_bytes=(double)T*hidden*bytes; double window_bytes=(double)std::min(T,4096)*L*2*kv_dim*bytes; double read_us_full=full_bytes/(bandwidth_GBs*1e9)*1e6; double read_us_window=window_bytes/(bandwidth_GBs*1e9)*1e6; double recompute_flops=(double)T*L*2*hidden*hidden; double recompute_us=recompute_flops/(flops_TF*1e12)*1e6;
        rows.push_back({T,L,hidden,kv_dim,bytes,"full_kv",full_bytes/1e6,1.0,read_us_full,mse});
        rows.push_back({T,L,hidden,kv_dim,bytes,"residual_direct_recompute",residual_bytes/1e6,residual_bytes/full_bytes,read_us_full*0.0 + residual_bytes/(bandwidth_GBs*1e9)*1e6 + recompute_us,mse});
        rows.push_back({T,L,hidden,kv_dim,bytes,"window_4096_kv_lossy",window_bytes/1e6,window_bytes/full_bytes,read_us_window,0.0});
    }
    std::map<std::string,int> memory_winners, time_winners; for(int T:token_grid) for(int L:layer_grid) for(int hidden:hidden_grid){ double bm=1e300,bt=1e300; std::string pm,pt; for(auto& r:rows) if(r.tokens==T&&r.layers==L&&r.hidden==hidden){ if(r.state_mb<bm){bm=r.state_mb; pm=r.policy;} if(r.estimated_decode_us<bt){bt=r.estimated_decode_us; pt=r.policy;} } memory_winners[pm]++; time_winners[pt]++; }
    auto t1=std::chrono::high_resolution_clock::now(); double sec=std::chrono::duration<double>(t1-t0).count(); std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"residual_stream_kv\",\n";
    f<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<sec<<", \"exact_reconstruction_mse\": "<<mse<<", \"primary_metric\": {\"name\": \"state_mb\", \"direction\": \"lower_is_better\", \"winner_field\": \"memory_winner_counts\"}, \"memory_winner_counts\": {"; bool first=true; for(auto& kv:memory_winners){ if(!first) f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second; } f<<"}, \"estimated_time_winner_counts\": {"; first=true; for(auto& kv:time_winners){ if(!first) f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second; } f<<"}},\n  \"rows\": [\n";
    for(size_t i=0;i<rows.size();++i){ auto& r=rows[i]; if(i) f<<",\n"; f<<"    {\"tokens\": "<<r.tokens<<", \"layers\": "<<r.layers<<", \"hidden\": "<<r.hidden<<", \"policy\": \""<<esc(r.policy)<<"\", \"state_mb\": "<<r.state_mb<<", \"relative_bytes_vs_full_kv\": "<<r.rel_bytes<<", \"estimated_decode_us\": "<<r.estimated_decode_us<<", \"reconstruction_mse\": "<<r.reconstruction_mse<<"}"; }
    f<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
