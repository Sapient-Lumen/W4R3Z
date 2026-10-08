// CloudtainerML rev0023: native dynamic short convolution toy wind tunnel.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <string>
#include <vector>

static std::string q(const std::string& s){ return "\"" + s + "\""; }
struct Regime { std::string name; double locality, burst, aliasing, semantic, no_locality; };
struct Method { std::string name; int width; double adapt, static_bias, cost; };
struct Row { std::string regime, method; int width; double retrieval_error, compute_units, robustness, score; };

int main(int argc, char** argv){
    std::string out = argc > 1 ? argv[1] : "REV0023_DYNAMIC_SHORT_CONVOLUTION_SMOKE.json";
    std::vector<Regime> regimes = {
        {"associative_recall_with_neighbor_hint", 0.85, 0.15, 0.25, 0.65, 0.00},
        {"bursty_local_distractors", 0.70, 0.85, 0.45, 0.50, 0.00},
        {"qkv_aliasing_needs_directional_filter", 0.55, 0.35, 0.90, 0.35, 0.00},
        {"mostly_global_no_locality", 0.05, 0.25, 0.20, 0.80, 0.95},
        {"smooth_topic_runs", 0.95, 0.10, 0.15, 0.45, 0.00},
        {"ragged_mixed_scale", 0.50, 0.65, 0.55, 0.55, 0.10}
    };
    std::vector<Method> methods = {
        {"plain_attention_baseline", 1, 0.00, 0.00, 1.00},
        {"static_short_conv_qkv", 3, 0.00, 0.75, 1.12},
        {"dynamic_short_conv_qkv", 3, 0.72, 0.25, 1.22},
        {"dynamic_short_conv_every_linear", 5, 0.92, 0.12, 1.45},
        {"oracle_input_filter", 5, 1.00, 0.00, 1.62}
    };
    std::vector<double> budgets = {1.05, 1.18, 1.30, 1.50, 1.75};
    std::vector<Row> rows;
    for(const auto& rg : regimes){
        for(double budget : budgets){
            for(const auto& m : methods){
                double active = std::min(1.0, budget / m.cost);
                double local_gain = rg.locality * (0.20 + 0.72 * m.adapt + 0.35 * m.static_bias) * active;
                double alias_penalty = rg.aliasing * (0.42 * m.static_bias + 0.16 * (1.0 - m.adapt));
                double burst_penalty = rg.burst * (0.28 * m.static_bias + 0.20 * (m.width>3?0.5:1.0)) * (1.0 - 0.45*m.adapt);
                double global_loss = rg.no_locality * (0.30 * m.adapt + 0.10 * m.static_bias);
                double semantic_gain = rg.semantic * (m.name=="plain_attention_baseline" ? 0.30 : 0.22 + 0.08*m.adapt);
                double raw_error = 1.0 - local_gain - semantic_gain + alias_penalty + burst_penalty + global_loss;
                if(m.name=="oracle_input_filter") raw_error = 0.55 * raw_error - 0.10 * rg.locality;
                raw_error = std::max(0.02, std::min(1.80, raw_error));
                double compute_units = m.cost * active;
                double robustness = 1.0 / (1.0 + raw_error + 0.25*alias_penalty + 0.15*burst_penalty);
                double score = raw_error + 0.12 * compute_units + 0.20 * std::max(0.0, m.cost - budget);
                rows.push_back({rg.name, m.name, m.width, raw_error, compute_units, robustness, score});
            }
        }
    }
    std::map<std::string,int> winners, nonoracle;
    for(const auto& rg: regimes){ for(double budget: budgets){ const Row* best=nullptr; const Row* best_no=nullptr; for(const auto& r: rows){ if(r.regime!=rg.name || std::abs((r.compute_units < budget ? r.compute_units : budget)-budget)>budget+1.0){} } for(const auto& r: rows){ if(r.regime==rg.name){ // group by implicit budget not stored; use score proximity loop below too costly? OK: budget groups share repeated row order.
            }
        } } }
    // Recompute winners by row block: regimes x budgets x methods.
    size_t idx=0;
    for(const auto& rg: regimes){ (void)rg; for(double budget: budgets){ (void)budget; const Row* best=nullptr; const Row* best_no=nullptr; for(size_t j=0;j<methods.size();++j){ const Row& r=rows[idx++]; if(!best || r.score<best->score) best=&r; if(r.method!="oracle_input_filter" && (!best_no || r.score<best_no->score)) best_no=&r; } if(best) winners[best->method]++; if(best_no) nonoracle[best_no->method]++; } }
    std::ofstream f(out); f << std::fixed << std::setprecision(6);
    f << "{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"dynamic_short_convolution\",\n";
    f << "  \"summary\": {\n    \"row_count\": " << rows.size() << ",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {";
    bool first=true; for(auto& kv:winners){ if(!first) f << ", "; first=false; f << q(kv.first) << ": " << kv.second; }
    f << "},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto& kv:nonoracle){ if(!first) f << ", "; first=false; f << q(kv.first) << ": " << kv.second; }
    f << "},\n    \"interpretation\": \"Dynamic short convolution earns its keep when local neighbor evidence is real and aliasing is directional; static convolution is cheaper but brittle, and no-locality regimes punish dynamic filtering.\"\n  },\n  \"rows\": [\n";
    for(size_t i=0;i<rows.size();++i){ const auto& r=rows[i]; f << "    {\"regime\": " << q(r.regime) << ", \"method\": " << q(r.method) << ", \"width\": " << r.width << ", \"retrieval_error\": " << r.retrieval_error << ", \"compute_units\": " << r.compute_units << ", \"robustness\": " << r.robustness << ", \"score\": " << r.score << "}" << (i+1==rows.size()?"\n":",\n"); }
    f << "  ]\n}\n"; std::cout << "wrote " << out << " rows=" << rows.size() << "\n"; return 0;
}
