// CloudtainerML rev0016: carried-forward native probe, current-revision emission.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <sstream>
#include <string>
#include <vector>

struct Row {
    std::string regime, policy;
    int context, checkpoint;
    double memory_mb, recompute_cost, bandwidth_cost, error_risk, score;
    bool exact;
};

static std::string q(const std::string& s){ return "\"" + s + "\""; }
static double sq(double x){ return x*x; }

int main(int argc, char** argv) {
    std::string out = argc > 1 ? argv[1] : "REV0016_RESIDUAL_KV_SENSITIVITY_SMOKE.json";
    const double kv_bytes_per_token = 136.0 * 1024.0;   // paper-scale proxy, not model-specific
    const double resid_bytes_per_token = 5.0 * 1024.0;  // paper-scale proxy, not model-specific
    const double lowrank_bytes_per_token = 2.0 * 1024.0;
    const double mb = 1024.0 * 1024.0;
    struct Regime { std::string name; double bw_weight; double compute_weight; double error_weight; double exact_bonus; };
    std::vector<Regime> regimes = {
        {"memory_bound_decode", 1.15, 0.05, 4.0, -0.25},
        {"compute_expensive_edge", 0.45, 0.75, 4.0, -0.10},
        {"strict_exactness", 0.80, 0.25, 25.0, -1.00},
        {"loss_tolerant_agent", 0.65, 0.10, 1.5, -0.05},
        {"short_context_low_pressure", 0.30, 0.05, 3.0, -0.05}
    };
    std::vector<int> contexts = {2048, 8192, 32768, 131072};
    std::vector<int> checkpoints = {256, 1024, 4096};
    std::vector<Row> rows;
    for (const auto& rg : regimes) {
        for (int n : contexts) {
            for (int ck : checkpoints) {
                std::vector<Row> cand;
                // full KV: exact, no recompute, but huge memory/bandwidth.
                cand.push_back({rg.name, "full_kv", n, ck,
                    n * kv_bytes_per_token / mb,
                    0.0,
                    rg.bw_weight * n * kv_bytes_per_token / mb,
                    0.0,
                    0.0,
                    true});
                // sliding lossy KV: cheap memory, error grows with long-range dependency pressure.
                double win = std::min<double>(n, ck);
                double lost_frac = std::max(0.0, 1.0 - win / std::max(1, n));
                cand.push_back({rg.name, "window_kv_lossy", n, ck,
                    win * kv_bytes_per_token / mb,
                    0.0,
                    rg.bw_weight * win * kv_bytes_per_token / mb,
                    0.04 + 0.95 * lost_frac,
                    0.0,
                    false});
                // residual checkpoint: exact if recomputation deterministic; pay local recompute span.
                double num_ck = std::ceil((double)n / ck);
                double avg_recompute = ck / 2.0;
                cand.push_back({rg.name, "residual_checkpoint_recompute", n, ck,
                    num_ck * resid_bytes_per_token / mb,
                    rg.compute_weight * avg_recompute * 0.0035,
                    rg.bw_weight * num_ck * resid_bytes_per_token / mb,
                    0.0,
                    0.0,
                    true});
                // low-rank residual: tiny object, nonzero reconstruction risk.
                cand.push_back({rg.name, "lowrank_residual_sketch", n, ck,
                    num_ck * lowrank_bytes_per_token / mb,
                    rg.compute_weight * avg_recompute * 0.0022,
                    rg.bw_weight * num_ck * lowrank_bytes_per_token / mb,
                    0.02 + 0.20 * std::log2(std::max(2, n) / 2048.0) / 6.0,
                    0.0,
                    false});
                // hybrid: recent exact KV window + far residual checkpoints.
                double local_win = std::min<double>(n, std::max(256, ck/4));
                cand.push_back({rg.name, "hybrid_recent_kv_far_residual", n, ck,
                    local_win * kv_bytes_per_token / mb + num_ck * resid_bytes_per_token / mb,
                    rg.compute_weight * (ck / 6.0) * 0.0030,
                    rg.bw_weight * (local_win * kv_bytes_per_token + num_ck * resid_bytes_per_token) / mb,
                    0.0,
                    0.0,
                    true});
                for (auto& r : cand) {
                    r.score = r.bandwidth_cost + r.recompute_cost + rg.error_weight * r.error_risk + (r.exact ? rg.exact_bonus : 0.0);
                    rows.push_back(r);
                }
            }
        }
    }
    std::map<std::string,int> winners;
    std::map<std::string, std::string> best_by_slice;
    for (const auto& rg : regimes) for (int n : contexts) for (int ck : checkpoints) {
        const Row* best = nullptr;
        for (const auto& r : rows) if (r.regime==rg.name && r.context==n && r.checkpoint==ck) {
            if (!best || r.score < best->score) best = &r;
        }
        if (best) { winners[best->policy]++; best_by_slice[rg.name + ":" + std::to_string(n) + ":" + std::to_string(ck)] = best->policy; }
    }
    std::ofstream f(out);
    f << std::fixed << std::setprecision(6);
    f << "{\n";
    f << "  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0016\",\n  \"probe\": \"native_residual_kv_sensitivity\",\n";
    f << "  \"summary\": {\n";
    f << "    \"row_count\": " << rows.size() << ",\n";
    f << "    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"policy\"},\n";
    f << "    \"winner_counts\": {";
    bool first=true; for (auto& kv : winners){ if(!first) f << ", "; first=false; f << q(kv.first) << ": " << kv.second; } f << "},\n";
    f << "    \"interpretation\": \"Toy cost sensitivity: residual checkpoints dominate memory-bound exact regimes, but window KV can win when compute is expensive and loss is tolerated. Constants are probes, not measurements.\"\n";
    f << "  },\n  \"rows\": [\n";
    for (size_t i=0;i<rows.size();++i){ const auto& r=rows[i];
        f << "    {\"regime\": "<<q(r.regime)<<", \"context\": "<<r.context<<", \"checkpoint\": "<<r.checkpoint<<", \"policy\": "<<q(r.policy)
          <<", \"memory_mb\": "<<r.memory_mb<<", \"recompute_cost\": "<<r.recompute_cost<<", \"bandwidth_cost\": "<<r.bandwidth_cost
          <<", \"error_risk\": "<<r.error_risk<<", \"exact\": "<<(r.exact?"true":"false")<<", \"score\": "<<r.score<<"}" << (i+1==rows.size()?"\n":",\n");
    }
    f << "  ]\n}\n";
    std::cout << "wrote " << out << " rows=" << rows.size() << "\n";
    return 0;
}
