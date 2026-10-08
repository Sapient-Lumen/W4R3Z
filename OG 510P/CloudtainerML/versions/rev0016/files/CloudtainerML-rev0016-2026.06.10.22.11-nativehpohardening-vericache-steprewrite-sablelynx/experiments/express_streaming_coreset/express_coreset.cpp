// CloudtainerML rev0016: Express-style streaming coreset toy probe.
// This is NOT a reproduction of Express/Thinformer. It is a CPU-only,
// dependency-free stress probe for the hypothesis that streaming weighted
// cache objects can preserve causal attention outputs better than recency or
// uniform retention at equal cache size.
// Build: g++ -O3 -std=c++17 express_coreset.cpp -o express_coreset

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <sstream>
#include <string>
#include <vector>

struct Vec {
    std::vector<double> x;
    Vec() = default;
    explicit Vec(int d) : x(d, 0.0) {}
};

static double dot(const Vec& a, const Vec& b) {
    double s = 0.0;
    for (size_t i = 0; i < a.x.size(); ++i) s += a.x[i] * b.x[i];
    return s;
}

static double mse(const Vec& a, const Vec& b) {
    double s = 0.0;
    for (size_t i = 0; i < a.x.size(); ++i) {
        double e = a.x[i] - b.x[i];
        s += e * e;
    }
    return s / std::max<size_t>(1, a.x.size());
}

struct KV {
    Vec k;
    Vec v;
    int idx = 0;
    double weight = 1.0;
    double salience = 0.0;
};

static Vec attention(const Vec& q, const std::vector<KV>& cache, double scale) {
    Vec out((int)q.x.size());
    if (cache.empty()) return out;
    std::vector<double> logits(cache.size());
    double mx = -1e300;
    for (size_t i = 0; i < cache.size(); ++i) {
        double w = std::max(1e-12, cache[i].weight);
        logits[i] = dot(q, cache[i].k) * scale + std::log(w);
        if (logits[i] > mx) mx = logits[i];
    }
    double z = 0.0;
    for (double& l : logits) { l = std::exp(l - mx); z += l; }
    for (size_t i = 0; i < cache.size(); ++i) {
        double p = logits[i] / std::max(1e-12, z);
        for (size_t j = 0; j < out.x.size(); ++j) out.x[j] += p * cache[i].v.x[j];
    }
    return out;
}

static Vec randn_vec(std::mt19937_64& rng, int d, double sigma=1.0) {
    std::normal_distribution<double> nd(0.0, sigma);
    Vec v(d);
    for (double& z : v.x) z = nd(rng);
    return v;
}

static Vec noisy_copy(std::mt19937_64& rng, const Vec& base, double sigma) {
    Vec v((int)base.x.size());
    std::normal_distribution<double> nd(0.0, sigma);
    for (size_t i = 0; i < base.x.size(); ++i) v.x[i] = base.x[i] + nd(rng);
    return v;
}

static std::vector<KV> select_recent(const std::vector<KV>& hist, int budget) {
    int n = (int)hist.size();
    int start = std::max(0, n - budget);
    return std::vector<KV>(hist.begin() + start, hist.end());
}

static std::vector<KV> select_uniform(const std::vector<KV>& hist, int budget) {
    int n = (int)hist.size();
    if (n <= budget) return hist;
    std::vector<KV> out;
    out.reserve(budget);
    for (int i = 0; i < budget; ++i) {
        int j = (int)std::llround((double)i * (n - 1) / std::max(1, budget - 1));
        out.push_back(hist[j]);
    }
    return out;
}

static std::vector<KV> select_salience(const std::vector<KV>& hist, const Vec& q, int budget, double scale) {
    std::vector<KV> out = hist;
    for (auto& kv : out) kv.salience = dot(q, kv.k) * scale;
    if ((int)out.size() > budget) {
        std::nth_element(out.begin(), out.begin() + budget, out.end(), [](const KV& a, const KV& b){ return a.salience > b.salience; });
        out.resize(budget);
        std::sort(out.begin(), out.end(), [](const KV& a, const KV& b){ return a.idx < b.idx; });
    }
    return out;
}

class ExpressToy {
  public:
    explicit ExpressToy(int budget) : budget_(budget) {}
    void update(const KV& kv) {
        cache_.push_back(kv);
        if ((int)cache_.size() > 2 * budget_) compress_once();
    }
    const std::vector<KV>& cache() const { return cache_; }
  private:
    int budget_;
    std::vector<KV> cache_;
    void compress_once() {
        std::sort(cache_.begin(), cache_.end(), [](const KV& a, const KV& b){ return a.idx < b.idx; });
        std::vector<KV> next;
        next.reserve(budget_ + 1);
        for (size_t i = 0; i < cache_.size(); i += 2) {
            if (i + 1 >= cache_.size()) { next.push_back(cache_[i]); break; }
            const KV& a = cache_[i];
            const KV& b = cache_[i+1];
            // Deterministic balanced halving surrogate: keep the member closer to the pair's
            // key-value centroid, then carry the pair's total weight. This is deliberately
            // simple and inspectable, not a kernel-halving implementation.
            double da = 0.0, db = 0.0;
            for (size_t j = 0; j < a.k.x.size(); ++j) {
                double mk = 0.5 * (a.k.x[j] + b.k.x[j]);
                double mv = 0.5 * (a.v.x[j] + b.v.x[j]);
                double ea = a.k.x[j] - mk, eb = b.k.x[j] - mk;
                double eva = a.v.x[j] - mv, evb = b.v.x[j] - mv;
                da += ea*ea + eva*eva;
                db += eb*eb + evb*evb;
            }
            KV kept = (da <= db) ? a : b;
            kept.weight = a.weight + b.weight;
            next.push_back(kept);
        }
        cache_.swap(next);
        if ((int)cache_.size() > budget_) cache_.resize(budget_);
    }
};

struct Row { std::string regime, policy; int budget; double mse_sum=0; double target_ret=0; int n=0; };

static std::string escape_json(const std::string& s) {
    std::ostringstream o;
    for (char c : s) {
        if (c == '"') o << "\\\"";
        else if (c == '\\') o << "\\\\";
        else o << c;
    }
    return o.str();
}

static bool contains_target(const std::vector<KV>& cache, int idx) {
    for (const auto& kv : cache) if (kv.idx == idx) return true;
    return false;
}

int main(int argc, char** argv) {
    std::string out_path = "artifacts/probe-results/REV0016_EXPRESS_STREAMING_CORESET_SMOKE.json";
    if (argc > 1) out_path = argv[1];
    const int d = 32;
    const int T = 768;
    const double scale = 1.0 / std::sqrt((double)d);
    const std::vector<int> budgets = {16, 32, 64, 128};
    const std::vector<std::string> regimes = {"uniform_noise", "early_needle", "drifting_clusters", "bursty_relevance"};
    std::vector<Row> rows;
    auto started = std::chrono::high_resolution_clock::now();

    for (const auto& regime : regimes) {
        for (int budget : budgets) {
            for (const std::string policy : {"recent", "uniform", "salience_oracle", "express_toy"}) {
                rows.push_back({regime, policy, budget});
            }
        }
    }

    for (const auto& regime : regimes) {
        for (int budget : budgets) {
            std::mt19937_64 rng(12345 + budget * 991 + (int)regime.size() * 17);
            std::vector<KV> hist;
            hist.reserve(T);
            ExpressToy ex(budget);
            Vec cluster = randn_vec(rng, d, 1.0);
            std::vector<int> needles;
            for (int t = 0; t < T; ++t) {
                if (regime == "drifting_clusters" && t % 96 == 0) cluster = randn_vec(rng, d, 1.0);
                KV kv;
                kv.idx = t;
                if (regime == "drifting_clusters") {
                    kv.k = noisy_copy(rng, cluster, 0.35);
                    kv.v = noisy_copy(rng, cluster, 0.35);
                } else {
                    kv.k = randn_vec(rng, d, 1.0);
                    kv.v = randn_vec(rng, d, 1.0);
                }
                if (regime == "early_needle" && t == 24) {
                    for (double& z : kv.k.x) z *= 3.0;
                    for (double& z : kv.v.x) z *= 3.0;
                    needles.push_back(t);
                }
                if (regime == "bursty_relevance" && t % 137 == 13) needles.push_back(t);
                hist.push_back(kv);
                ex.update(kv);

                if (t < 32) continue;
                int target = t - 1;
                if (regime == "early_needle" && t > 300) target = 24;
                if (regime == "bursty_relevance" && !needles.empty() && (t % 97) < 24) target = needles.back();
                Vec q = noisy_copy(rng, hist[target].k, 0.08);
                Vec ref = attention(q, hist, scale);
                std::vector<std::pair<std::string, std::vector<KV>>> caches;
                caches.push_back({"recent", select_recent(hist, budget)});
                caches.push_back({"uniform", select_uniform(hist, budget)});
                caches.push_back({"salience_oracle", select_salience(hist, q, budget, scale)});
                caches.push_back({"express_toy", ex.cache()});
                for (const auto& cp : caches) {
                    Vec y = attention(q, cp.second, scale);
                    for (auto& r : rows) {
                        if (r.regime == regime && r.policy == cp.first && r.budget == budget) {
                            r.mse_sum += mse(ref, y);
                            r.target_ret += contains_target(cp.second, target) ? 1.0 : 0.0;
                            r.n += 1;
                            break;
                        }
                    }
                }
            }
        }
    }

    auto ended = std::chrono::high_resolution_clock::now();
    double ms = std::chrono::duration<double, std::milli>(ended - started).count();
    std::ofstream f(out_path);
    f << std::fixed << std::setprecision(6);
    f << "{\n";
    f << "  \"project\": \"CloudtainerML\",\n";
    f << "  \"revision\": \"rev0016\",\n";
    f << "  \"probe\": \"express_streaming_coreset_cpp_smoke\",\n";
    f << "  \"language\": \"C++17\",\n";
    f << "  \"is_paper_reproduction\": false,\n";
    f << "  \"summary\": {\n";
    f << "    \"primary_metric\": {\"name\": \"mean_mse_to_full_attention\", \"direction\": \"lower_is_better\"},\n";
    f << "    \"runtime_ms\": " << ms << ",\n";
    f << "    \"interpretation\": \"Toy streaming weighted coreset compared with recency, uniform, and salience-oracle retention. Use as an attention-approximation wind tunnel, not as an Express implementation.\"\n";
    f << "  },\n";
    f << "  \"rows\": [\n";
    for (size_t i = 0; i < rows.size(); ++i) {
        const auto& r = rows[i];
        double mm = r.mse_sum / std::max(1, r.n);
        double tr = r.target_ret / std::max(1, r.n);
        f << "    {\"regime\": \"" << escape_json(r.regime) << "\", \"policy\": \"" << escape_json(r.policy)
          << "\", \"budget\": " << r.budget << ", \"mean_mse_to_full_attention\": " << mm
          << ", \"target_retention_rate\": " << tr << ", \"steps\": " << r.n << "}";
        if (i + 1 < rows.size()) f << ",";
        f << "\n";
    }
    f << "  ]\n";
    f << "}\n";
    std::cerr << "wrote " << out_path << " in " << ms << " ms\n";
    return 0;
}
