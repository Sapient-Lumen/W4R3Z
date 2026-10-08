// CloudtainerML rev0016: carried-forward native probe, current-revision emission.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <string>
#include <vector>

struct Row { std::string fabric, policy; int shards, blocks, tokens_per_block; double query_kb, cache_kb, latency_us, score; };
static std::string q(const std::string& s){ return "\"" + s + "\""; }
int main(int argc, char** argv){
    std::string out = argc > 1 ? argv[1] : "REV0016_QUERY_MOVE_PHASE_SCAN_SMOKE.json";
    struct Fabric{ std::string name; double probe_us, bw_gbps, remote_compute_us, local_recompute_us_per_block, merge_us; };
    std::vector<Fabric> fabrics = {
        {"same_socket_cpu", 1.5, 900.0, 2.0, 9.0, 1.0},
        {"pcie_gpu", 8.0, 64.0, 4.0, 20.0, 3.0},
        {"ib_rdma", 18.0, 200.0, 8.0, 28.0, 6.0},
        {"slow_edge_link", 80.0, 20.0, 18.0, 15.0, 12.0}
    };
    std::vector<int> shards_v={2,4,8,16};
    std::vector<int> blocks_v={1,2,4,8,16,32};
    std::vector<int> tpb_v={64,256,1024};
    std::vector<double> query_kb_v={0.5,1.0,4.0,16.0};
    const double kv_kb_per_token=0.25; // latent/cache block proxy, not model-specific.
    std::vector<Row> rows;
    auto transfer_us=[&](double kb, const Fabric& fb){ return (kb*8.0/1e6) / std::max(1e-9, fb.bw_gbps) * 1e6; };
    for(const auto& fb:fabrics) for(int shards: shards_v) for(int blocks: blocks_v) for(int tpb:tpb_v) for(double qkb: query_kb_v){
        double cache_kb = blocks * tpb * kv_kb_per_token;
        double selected_shards = std::min<double>(shards, std::max(1.0, std::ceil(blocks/2.0)));
        // move selected cache blocks to requester.
        double move_cache = fb.probe_us + transfer_us(cache_kb, fb) + 0.8*blocks + fb.merge_us;
        // send compact query to shards, do remote attention, return small partial output.
        double move_query = fb.probe_us + transfer_us(qkb*selected_shards + 2.0*selected_shards, fb) + fb.remote_compute_us*std::log2(1+blocks) + fb.merge_us*std::log2(1+selected_shards);
        // fetch an index page then only fetch cache if index says local not enough.
        double index_then_fetch = fb.probe_us + transfer_us(0.15*cache_kb + qkb, fb) + 0.45*blocks + fb.merge_us;
        // recompute locally, no network transfer, but compute grows with selected blocks.
        double recompute_local = blocks * fb.local_recompute_us_per_block + 0.02 * tpb * blocks;
        rows.push_back({fb.name,"move_cache",shards,blocks,tpb,qkb,cache_kb,move_cache,move_cache});
        rows.push_back({fb.name,"move_query",shards,blocks,tpb,qkb,cache_kb,move_query,move_query});
        rows.push_back({fb.name,"index_then_fetch",shards,blocks,tpb,qkb,cache_kb,index_then_fetch,index_then_fetch});
        rows.push_back({fb.name,"recompute_local",shards,blocks,tpb,qkb,cache_kb,recompute_local,recompute_local});
    }
    std::map<std::string,int> winners;
    for(const auto& fb:fabrics) for(int shards: shards_v) for(int blocks: blocks_v) for(int tpb:tpb_v) for(double qkb: query_kb_v){
        const Row* best=nullptr;
        for(const auto& r:rows) if(r.fabric==fb.name && r.shards==shards && r.blocks==blocks && r.tokens_per_block==tpb && std::abs(r.query_kb-qkb)<1e-9){
            if(!best || r.score < best->score) best=&r;
        }
        if(best) winners[best->policy]++;
    }
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6);
    f << "{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0016\",\n  \"probe\": \"query_move_phase_boundary\",\n";
    f << "  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"latency_us\", \"direction\": \"lower_is_better\", \"winner_field\": \"policy\"},\n    \"winner_counts\": {";
    bool first=true; for(auto& kv:winners){ if(!first) f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second; } f << "},\n";
    f << "    \"interpretation\": \"Sensitivity scan creates an actual phase boundary: query movement wins when query payload is small and cache blocks are large; recompute/local/index can win in slow-link or tiny-block corners.\"\n  },\n  \"rows\": [\n";
    for(size_t i=0;i<rows.size();++i){ const auto& r=rows[i];
        f << "    {\"fabric\": "<<q(r.fabric)<<", \"policy\": "<<q(r.policy)<<", \"shards\": "<<r.shards<<", \"blocks\": "<<r.blocks<<", \"tokens_per_block\": "<<r.tokens_per_block<<", \"query_kb\": "<<r.query_kb<<", \"cache_kb\": "<<r.cache_kb<<", \"latency_us\": "<<r.latency_us<<", \"score\": "<<r.score<<"}" << (i+1==rows.size()?"\n":",\n");
    }
    f << "  ]\n}\n"; std::cout << "wrote " << out << " rows=" << rows.size() << "\n"; return 0;
}
