// CloudtainerML rev0016: move-the-query versus move-the-cache cost model.
// A dependency-free cost frontier for cross-instance sparse/latent attention.
// This asks when a small routed query row is cheaper than fetching selected KV
// chunks to the requester. It is not a reproduction of cross-node H100 results.

#include <algorithm>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

struct Row { std::string fabric, arch, policy; int blocks,batch; double query_kb, block_kb, us; };
static std::string esc(const std::string& s){ std::string o; for(char c:s){ if(c=='"') o+="\\\""; else if(c=='\\') o+="\\\\"; else o+=c; } return o; }

int main(int argc, char** argv){
    std::string out="artifacts/probe-results/REV0016_QUERY_MOVE_CACHE_SMOKE.json"; if(argc>1) out=argv[1]; auto t0=std::chrono::high_resolution_clock::now();
    struct Fabric{std::string name; double latency_us, GBs;}; std::vector<Fabric> fabrics={{"nvlink_like",4.0,450.0},{"ibgda_like",18.0,90.0},{"ethernet_like",75.0,25.0}};
    struct Arch{std::string name; double query_kb, block_kb, compute_us_per_block;}; std::vector<Arch> archs={{"mha_full_kv",16.0,512.0,1.40},{"gqa_compressed",8.0,192.0,0.90},{"mla_latent",1.0,64.0,0.55},{"ultra_latent",0.5,24.0,0.45}};
    std::vector<int> blocks_grid={1,2,4,8,16,32}; std::vector<int> batch_grid={1,4,16,64}; std::vector<Row> rows; std::map<std::string,int> winners;
    for(auto& fb:fabrics) for(auto& ar:archs) for(int b:blocks_grid) for(int batch:batch_grid){
        double cache_kb=ar.block_kb*b*batch; double query_kb=ar.query_kb*batch; double return_kb=ar.query_kb*batch; // output payload roughly query-sized in latent mode
        double move_cache_us=fb.latency_us + cache_kb/1e6/fb.GBs*1e6 + ar.compute_us_per_block*b*batch;
        double move_query_us=fb.latency_us + (query_kb+return_kb)/1e6/fb.GBs*1e6 + ar.compute_us_per_block*b*batch*1.08; // remote compute + small merge overhead
        double local_prefill_us=(cache_kb*3.0)/1e6/fb.GBs*1e6 + ar.compute_us_per_block*b*batch*1.25;
        std::string win="move_cache"; double best=move_cache_us; if(move_query_us<best){best=move_query_us; win="move_query";} if(local_prefill_us<best){best=local_prefill_us; win="recompute_local";} winners[win]++;
        rows.push_back({fb.name,ar.name,"move_cache",b,batch,ar.query_kb,ar.block_kb,move_cache_us}); rows.push_back({fb.name,ar.name,"move_query",b,batch,ar.query_kb,ar.block_kb,move_query_us}); rows.push_back({fb.name,ar.name,"recompute_local",b,batch,ar.query_kb,ar.block_kb,local_prefill_us});
    }
    auto t1=std::chrono::high_resolution_clock::now(); double sec=std::chrono::duration<double>(t1-t0).count(); std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0016\",\n  \"probe\": \"query_move_cache_cost\",\n";
    f<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<sec<<", \"primary_metric\": {\"name\": \"estimated_us\", \"direction\": \"lower_is_better\", \"winner_field\": \"winner_counts\"}, \"winner_counts\": {"; bool first=true; for(auto& kv:winners){ if(!first) f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second; } f<<"}},\n  \"rows\": [\n";
    for(size_t i=0;i<rows.size();++i){ auto& r=rows[i]; if(i) f<<",\n"; f<<"    {\"fabric\": \""<<esc(r.fabric)<<"\", \"architecture\": \""<<esc(r.arch)<<"\", \"policy\": \""<<esc(r.policy)<<"\", \"selected_blocks\": "<<r.blocks<<", \"batch\": "<<r.batch<<", \"query_kb\": "<<r.query_kb<<", \"block_kb\": "<<r.block_kb<<", \"estimated_us\": "<<r.us<<"}"; }
    f<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
