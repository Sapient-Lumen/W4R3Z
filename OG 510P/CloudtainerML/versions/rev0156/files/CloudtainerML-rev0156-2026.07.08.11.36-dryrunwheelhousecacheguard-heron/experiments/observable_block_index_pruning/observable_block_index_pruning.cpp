#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <sstream>
#include <string>
#include <vector>

// rev0052 observable block-index pruning probe.
//
// rev0051 showed that block upper-bound pruning can skip exact token QK scores
// in a tight clustered synthetic regime, but that result used generator-side
// block centroids/radii.  This revision moves the claim to an observable index:
// centroids and radii are computed from the key cache itself, before seeing any
// query, and the benchmark accounts for index build cost separately from query
// path timing.  It also includes a sampled-radius negative control, because a
// too-cheap approximate index can look sparse while its upper bounds are false.
//
// This remains a native CPU row/cache microbenchmark, not a GPU/fused-kernel or
// public-model trace claim.

struct XorShift64 {
    uint64_t x;
    explicit XorShift64(uint64_t seed) : x(seed ? seed : 88172645463325252ull) {}
    uint64_t next_u64() { x ^= x << 7; x ^= x >> 9; return x; }
    double uniform() { return (next_u64() >> 11) * (1.0 / 9007199254740992.0); }
    double normal() {
        double u1 = std::max(1e-12, uniform());
        double u2 = uniform();
        return std::sqrt(-2.0 * std::log(u1)) * std::cos(6.283185307179586 * u2);
    }
};

static constexpr int N = 2048;
static constexpr int DK = 64;
static constexpr int DV = 64;
static constexpr int BLOCK = 32;
static constexpr int BLOCKS = N / BLOCK;
static constexpr int QUERIES = 96;
static constexpr int REPEATS = 5;
static constexpr int BINS = 32;
static constexpr int BUILD_REUSE_QUERIES = 32;
static constexpr int SAMPLED_RADIUS_TOKENS = 4;
static constexpr double TARGET_MASS = 0.95;
static constexpr double QUALITY_COSINE = 0.995;
static constexpr double QUALITY_REL_L2 = 0.18;
static constexpr double SQRT_DK = 8.0;

volatile double global_sink = 0.0;

struct KeyCache {
    std::string regime;
    std::vector<double> keys;       // N * DK
    std::vector<double> values;     // N * DV
    std::vector<double> true_center; // BLOCKS * DK, only used to generate queries/diagnostics
};

struct QuerySet {
    std::vector<std::vector<double>> queries;
};

struct BlockIndex {
    std::string name;
    std::vector<double> centroids; // BLOCKS * DK
    std::vector<double> radii;     // BLOCKS
    bool observable_from_key_cache = true;
    bool uses_generator_oracle_bounds = false;
    bool unsafe_sampled_radius = false;
    long long build_dk_ops = 0;
    long long build_ns = 0;
};

struct Output {
    std::vector<double> y;
    std::vector<int> selected;
    int qk_dot_products = 0;
    int score_reads = 0;
    int block_bound_dots = 0;
    int exact_token_score_dots = 0;
    int opened_blocks = 0;
    double asserted_lower_bound_mass_certificate = 1.0;
    double bound_violation_rate = 0.0;
    bool exact_dense_scores_required = false;
};

struct MetricAcc {
    double true_mass = 0.0;
    double asserted_cert = 0.0;
    double bound_violation_rate = 0.0;
    double rel_l2 = 0.0;
    double cosine = 0.0;
    double selected = 0.0;
    double qk_dots = 0.0;
    double score_reads = 0.0;
    double opened_blocks = 0.0;
    int quality_pass = 0;
    int rows = 0;
};

struct SummaryRow {
    std::string regime;
    std::string method;
    double mean_ns_per_query = 0.0;
    double dense_ns_per_query = 0.0;
    double speedup_vs_dense_query_only = 1.0;
    double speedup_vs_dense_with_index_reuse_32 = 1.0;
    double index_build_ns_per_cache = 0.0;
    double index_build_dk_ops_per_cache = 0.0;
    MetricAcc acc;
    bool exact_dense_scores_required = false;
    bool computes_all_qk_scores_before_selection = false;
    bool observable_index_from_key_cache = false;
    bool uses_generator_oracle_bounds = false;
    bool unsafe_sampled_radius = false;
    bool block_upper_bound_pruning = false;
    bool selection_uses_values = false;
    bool selection_uses_dense_output = false;
    bool bound_is_certified = true;
    bool is_gpu_kernel_claim = false;
};

static double norm_vec(const std::vector<double>& v, int off, int len) {
    double s = 0.0;
    for (int i = 0; i < len; ++i) s += v[off + i] * v[off + i];
    return std::sqrt(s);
}

static void normalize_block(std::vector<double>& v, int off, int len) {
    double n = norm_vec(v, off, len);
    if (n < 1e-12) { v[off] = 1.0; return; }
    for (int i = 0; i < len; ++i) v[off + i] /= n;
}

static double l2_norm(const std::vector<double>& v) {
    double s = 0.0;
    for (double x : v) s += x * x;
    return std::sqrt(s);
}

static double dist_key_to_centroid(const std::vector<double>& keys, int token, const std::vector<double>& centroids, int block) {
    double s = 0.0;
    int ko = token * DK;
    int co = block * DK;
    for (int d = 0; d < DK; ++d) {
        double diff = keys[ko + d] - centroids[co + d];
        s += diff * diff;
    }
    return std::sqrt(s);
}

static double q_dot_key(const std::vector<double>& q, const KeyCache& c, int token) {
    double s = 0.0;
    int off = token * DK;
    for (int d = 0; d < DK; ++d) s += q[d] * c.keys[off + d];
    return s / SQRT_DK;
}

static double q_dot_centroid(const std::vector<double>& q, const BlockIndex& idx, int block) {
    double s = 0.0;
    int off = block * DK;
    for (int d = 0; d < DK; ++d) s += q[d] * idx.centroids[off + d];
    return s / SQRT_DK;
}

static KeyCache make_cache(int regime_id) {
    XorShift64 rng(0x52000000ULL + 9973ull * regime_id);
    KeyCache c;
    const char* names[] = {
        "tight_clustered_peaked_queries",
        "tight_clustered_multipeak_queries",
        "broad_unstructured_queries",
        "loose_clustered_peaked_queries"
    };
    c.regime = names[regime_id];
    c.keys.assign(N * DK, 0.0);
    c.values.assign(N * DV, 0.0);
    c.true_center.assign(BLOCKS * DK, 0.0);

    for (int b = 0; b < BLOCKS; ++b) {
        for (int d = 0; d < DK; ++d) c.true_center[b * DK + d] = rng.normal();
        normalize_block(c.true_center, b * DK, DK);
    }

    double amp = 8.0;
    double noise_sigma = 0.035;
    if (regime_id == 2) { amp = 1.0; noise_sigma = 1.35; }
    if (regime_id == 3) { amp = 8.0; noise_sigma = 2.10; }

    for (int b = 0; b < BLOCKS; ++b) {
        for (int j = 0; j < BLOCK; ++j) {
            int t = b * BLOCK + j;
            for (int d = 0; d < DK; ++d) {
                double noise = noise_sigma * rng.normal();
                if (regime_id == 2) {
                    c.keys[t * DK + d] = rng.normal();
                } else {
                    c.keys[t * DK + d] = amp * c.true_center[b * DK + d] + noise;
                }
            }
            double vscale = 0.75 + 0.15 * rng.uniform();
            for (int d = 0; d < DV; ++d) c.values[t * DV + d] = vscale * rng.normal();
        }
    }
    return c;
}

static QuerySet make_queries(const KeyCache& c, int regime_id) {
    XorShift64 rng(0x52100000ULL + 100003ull * regime_id);
    QuerySet qs;
    qs.queries.reserve(QUERIES);
    for (int row = 0; row < QUERIES; ++row) {
        std::vector<double> q(DK, 0.0);
        int b0 = (row * 13 + 7) % BLOCKS;
        int b1 = (b0 + 17) % BLOCKS;
        int b2 = (b0 + 37) % BLOCKS;
        if (regime_id == 0 || regime_id == 3) {
            for (int d = 0; d < DK; ++d) q[d] = 10.0 * c.true_center[b0 * DK + d] + 0.02 * rng.normal();
        } else if (regime_id == 1) {
            for (int d = 0; d < DK; ++d) q[d] = (10.0 / std::sqrt(3.0)) * (c.true_center[b0 * DK + d] + c.true_center[b1 * DK + d] + c.true_center[b2 * DK + d]) + 0.02 * rng.normal();
        } else {
            for (int d = 0; d < DK; ++d) q[d] = rng.normal();
        }
        qs.queries.push_back(std::move(q));
    }
    return qs;
}

static BlockIndex build_observable_mean_radius_index(const KeyCache& c) {
    BlockIndex idx;
    idx.name = "observable_mean_radius_block_pruned_0p95_sparse";
    idx.centroids.assign(BLOCKS * DK, 0.0);
    idx.radii.assign(BLOCKS, 0.0);
    auto start = std::chrono::steady_clock::now();
    long long ops = 0;
    for (int b = 0; b < BLOCKS; ++b) {
        for (int j = 0; j < BLOCK; ++j) {
            int t = b * BLOCK + j;
            for (int d = 0; d < DK; ++d) {
                idx.centroids[b * DK + d] += c.keys[t * DK + d];
                ++ops;
            }
        }
        for (int d = 0; d < DK; ++d) idx.centroids[b * DK + d] /= BLOCK;
        double rad = 0.0;
        for (int j = 0; j < BLOCK; ++j) {
            int t = b * BLOCK + j;
            rad = std::max(rad, dist_key_to_centroid(c.keys, t, idx.centroids, b));
            ops += DK;
        }
        idx.radii[b] = rad + 1e-9;
    }
    auto stop = std::chrono::steady_clock::now();
    idx.build_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(stop - start).count();
    idx.build_dk_ops = ops;
    return idx;
}

static BlockIndex build_sampled_radius_index(const KeyCache& c) {
    BlockIndex idx;
    idx.name = "unsafe_sampled_radius4_block_pruned_0p95_sparse";
    idx.observable_from_key_cache = true;
    idx.unsafe_sampled_radius = true;
    idx.centroids.assign(BLOCKS * DK, 0.0);
    idx.radii.assign(BLOCKS, 0.0);
    auto start = std::chrono::steady_clock::now();
    long long ops = 0;
    for (int b = 0; b < BLOCKS; ++b) {
        // The centroid is observable and uses the full block, but the radius is
        // incorrectly estimated from only four tokens.  That makes this a clear
        // negative control: it may prune more, but its upper bound can be false.
        for (int j = 0; j < BLOCK; ++j) {
            int t = b * BLOCK + j;
            for (int d = 0; d < DK; ++d) { idx.centroids[b * DK + d] += c.keys[t * DK + d]; ++ops; }
        }
        for (int d = 0; d < DK; ++d) idx.centroids[b * DK + d] /= BLOCK;
        double rad = 0.0;
        for (int j = 0; j < SAMPLED_RADIUS_TOKENS; ++j) {
            int t = b * BLOCK + j;
            rad = std::max(rad, dist_key_to_centroid(c.keys, t, idx.centroids, b));
            ops += DK;
        }
        idx.radii[b] = 0.25 * rad + 1e-9;
    }
    auto stop = std::chrono::steady_clock::now();
    idx.build_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(stop - start).count();
    idx.build_dk_ops = ops;
    return idx;
}

static std::vector<double> compute_scores_dense(const std::vector<double>& q, const KeyCache& c) {
    std::vector<double> scores(N);
    for (int i = 0; i < N; ++i) scores[i] = q_dot_key(q, c, i);
    return scores;
}

static std::vector<double> softmax_probs(const std::vector<double>& scores) {
    double m = *std::max_element(scores.begin(), scores.end());
    std::vector<double> probs(scores.size());
    double z = 0.0;
    for (size_t i = 0; i < scores.size(); ++i) { double e = std::exp(std::max(-80.0, scores[i] - m)); probs[i] = e; z += e; }
    if (z <= 0.0 || !std::isfinite(z)) { std::fill(probs.begin(), probs.end(), 1.0 / scores.size()); }
    else { for (double& p : probs) p /= z; }
    return probs;
}

static std::vector<double> output_from_selected(const KeyCache& c, const std::vector<double>& scores, const std::vector<int>& selected) {
    std::vector<double> y(DV, 0.0);
    if (selected.empty()) return y;
    double m = -std::numeric_limits<double>::infinity();
    for (int idx : selected) m = std::max(m, scores[idx]);
    double z = 0.0;
    for (int idx : selected) z += std::exp(std::max(-80.0, scores[idx] - m));
    if (z <= 0.0 || !std::isfinite(z)) return y;
    for (int idx : selected) {
        double p = std::exp(std::max(-80.0, scores[idx] - m)) / z;
        int off = idx * DV;
        for (int d = 0; d < DV; ++d) y[d] += p * c.values[off + d];
    }
    return y;
}

static std::vector<int> mass_histogram_indices(const std::vector<double>& scores, double target_mass) {
    double max_score = *std::max_element(scores.begin(), scores.end());
    std::vector<double> weights(N);
    double z = 0.0;
    for (int i = 0; i < N; ++i) { weights[i] = std::exp(std::max(-80.0, scores[i] - max_score)); z += weights[i]; }
    double width = 16.0 / static_cast<double>(BINS);
    std::vector<double> mass(BINS + 1, 0.0);
    std::vector<int> bid(N, BINS);
    for (int i = 0; i < N; ++i) {
        double rel = std::max(0.0, max_score - scores[i]);
        int b = static_cast<int>(std::floor(rel / std::max(width, 1e-12)));
        if (b < 0) b = 0;
        if (b > BINS) b = BINS;
        bid[i] = b;
        mass[b] += weights[i] / z;
    }
    double cum = 0.0;
    int cutoff = BINS;
    for (int b = 0; b <= BINS; ++b) { cum += mass[b]; if (cum >= target_mass) { cutoff = b; break; } }
    std::vector<int> sel;
    sel.reserve(N);
    for (int i = 0; i < N; ++i) if (bid[i] <= cutoff) sel.push_back(i);
    return sel;
}

static Output dense_full_attention(const std::vector<double>& q, const KeyCache& c) {
    Output o;
    std::vector<double> scores = compute_scores_dense(q, c);
    o.selected.resize(N);
    std::iota(o.selected.begin(), o.selected.end(), 0);
    o.y = output_from_selected(c, scores, o.selected);
    o.qk_dot_products = N;
    o.score_reads = N;
    o.exact_token_score_dots = N;
    o.exact_dense_scores_required = true;
    return o;
}

static Output dense_score_mass_hist_sparse(const std::vector<double>& q, const KeyCache& c) {
    Output o;
    std::vector<double> scores = compute_scores_dense(q, c);
    o.selected = mass_histogram_indices(scores, TARGET_MASS);
    o.y = output_from_selected(c, scores, o.selected);
    o.qk_dot_products = N;
    o.score_reads = 2 * N;
    o.exact_token_score_dots = N;
    o.exact_dense_scores_required = true;
    return o;
}

static double block_bound_violation_rate_for_query(const std::vector<double>& q, const KeyCache& c, const BlockIndex& idx) {
    double qnorm = l2_norm(q);
    int violations = 0;
    for (int b = 0; b < BLOCKS; ++b) {
        double ub = q_dot_centroid(q, idx, b) + (qnorm * idx.radii[b] / SQRT_DK);
        for (int j = 0; j < BLOCK; ++j) {
            int t = b * BLOCK + j;
            double s = q_dot_key(q, c, t);
            if (s > ub + 1e-8) { ++violations; break; }
        }
    }
    return static_cast<double>(violations) / static_cast<double>(BLOCKS);
}

static Output block_pruned_attention(const std::vector<double>& q, const KeyCache& c, const BlockIndex& idx) {
    Output o;
    double qnorm = l2_norm(q);
    std::vector<double> ub(BLOCKS);
    std::vector<int> order(BLOCKS);
    for (int b = 0; b < BLOCKS; ++b) {
        ub[b] = q_dot_centroid(q, idx, b) + (qnorm * idx.radii[b] / SQRT_DK);
        order[b] = b;
    }
    std::sort(order.begin(), order.end(), [&](int a, int b) { return ub[a] > ub[b]; });
    std::vector<char> opened_block(BLOCKS, 0);
    std::vector<double> exact_scores(N, -std::numeric_limits<double>::infinity());
    std::vector<int> opened_tokens;
    opened_tokens.reserve(N);
    double cert = 0.0;
    int opened_count = 0;
    for (int oi = 0; oi < BLOCKS; ++oi) {
        int b = order[oi];
        if (!opened_block[b]) {
            opened_block[b] = 1;
            ++opened_count;
            for (int j = 0; j < BLOCK; ++j) {
                int t = b * BLOCK + j;
                exact_scores[t] = q_dot_key(q, c, t);
                opened_tokens.push_back(t);
            }
        }
        double m = -std::numeric_limits<double>::infinity();
        for (int t : opened_tokens) m = std::max(m, exact_scores[t]);
        for (int bb = 0; bb < BLOCKS; ++bb) if (!opened_block[bb]) m = std::max(m, ub[bb]);
        double opened_w = 0.0;
        for (int t : opened_tokens) opened_w += std::exp(std::max(-80.0, exact_scores[t] - m));
        double unopened_upper_w = 0.0;
        for (int bb = 0; bb < BLOCKS; ++bb) if (!opened_block[bb]) unopened_upper_w += BLOCK * std::exp(std::max(-80.0, ub[bb] - m));
        cert = opened_w / std::max(1e-300, opened_w + unopened_upper_w);
        if (cert >= TARGET_MASS) break;
    }
    o.selected = opened_tokens;
    o.y = output_from_selected(c, exact_scores, o.selected);
    o.qk_dot_products = BLOCKS + static_cast<int>(opened_tokens.size());
    o.block_bound_dots = BLOCKS;
    o.exact_token_score_dots = static_cast<int>(opened_tokens.size());
    o.score_reads = static_cast<int>(opened_tokens.size());
    o.opened_blocks = opened_count;
    o.asserted_lower_bound_mass_certificate = cert;
    o.bound_violation_rate = block_bound_violation_rate_for_query(q, c, idx);
    o.exact_dense_scores_required = false;
    return o;
}

static void add_quality(MetricAcc& acc, const KeyCache& c, const std::vector<double>& dense_y, const std::vector<double>& dense_scores, const Output& out) {
    std::vector<double> probs = softmax_probs(dense_scores);
    double mass = 0.0;
    for (int idx : out.selected) mass += probs[idx];
    std::vector<double> diff(DV, 0.0);
    double dotp = 0.0;
    for (int d = 0; d < DV; ++d) { diff[d] = out.y[d] - dense_y[d]; dotp += out.y[d] * dense_y[d]; }
    double dense_norm = std::max(1e-12, l2_norm(dense_y));
    double out_norm = std::max(1e-12, l2_norm(out.y));
    double rel = l2_norm(diff) / dense_norm;
    double cos = std::max(-1.0, std::min(1.0, dotp / (dense_norm * out_norm)));
    bool pass = (mass >= TARGET_MASS && cos >= QUALITY_COSINE && rel <= QUALITY_REL_L2);
    acc.true_mass += mass;
    acc.asserted_cert += out.asserted_lower_bound_mass_certificate;
    acc.bound_violation_rate += out.bound_violation_rate;
    acc.rel_l2 += rel;
    acc.cosine += cos;
    acc.selected += static_cast<double>(out.selected.size());
    acc.qk_dots += static_cast<double>(out.qk_dot_products);
    acc.score_reads += static_cast<double>(out.score_reads);
    acc.opened_blocks += static_cast<double>(out.opened_blocks);
    acc.quality_pass += pass ? 1 : 0;
    acc.rows += 1;
    global_sink += out.y.empty() ? 0.0 : out.y[0] * 1e-12;
}

using DenseMethod = Output(*)(const std::vector<double>&, const KeyCache&);

static long long time_dense_method(const KeyCache& c, const QuerySet& qs, DenseMethod fn) {
    auto start = std::chrono::steady_clock::now();
    for (int rep = 0; rep < REPEATS; ++rep) {
        for (const auto& q : qs.queries) {
            Output o = fn(q, c);
            if (!o.y.empty()) global_sink += o.y[0] * 1e-9;
        }
    }
    auto stop = std::chrono::steady_clock::now();
    return std::chrono::duration_cast<std::chrono::nanoseconds>(stop - start).count();
}

static long long time_block_method(const KeyCache& c, const QuerySet& qs, const BlockIndex& idx) {
    auto start = std::chrono::steady_clock::now();
    for (int rep = 0; rep < REPEATS; ++rep) {
        for (const auto& q : qs.queries) {
            Output o = block_pruned_attention(q, c, idx);
            if (!o.y.empty()) global_sink += o.y[0] * 1e-9;
        }
    }
    auto stop = std::chrono::steady_clock::now();
    return std::chrono::duration_cast<std::chrono::nanoseconds>(stop - start).count();
}

static std::string fmt(double x) {
    if (!std::isfinite(x)) return "null";
    std::ostringstream ss;
    ss << std::setprecision(10) << x;
    return ss.str();
}

static void emit_row(std::ofstream& out, const SummaryRow& r, bool comma) {
    const MetricAcc& a = r.acc;
    double rows = std::max(1, a.rows);
    out << "    {\n";
    out << "      \"regime\": \"" << r.regime << "\",\n";
    out << "      \"method\": \"" << r.method << "\",\n";
    out << "      \"n_tokens\": " << N << ",\n";
    out << "      \"d_head\": " << DK << ",\n";
    out << "      \"d_value\": " << DV << ",\n";
    out << "      \"block_size\": " << BLOCK << ",\n";
    out << "      \"target_mass\": " << fmt(TARGET_MASS) << ",\n";
    out << "      \"rows\": " << a.rows << ",\n";
    out << "      \"mean_ns_per_query\": " << fmt(r.mean_ns_per_query) << ",\n";
    out << "      \"dense_ns_per_query\": " << fmt(r.dense_ns_per_query) << ",\n";
    out << "      \"speedup_vs_dense_query_only\": " << fmt(r.speedup_vs_dense_query_only) << ",\n";
    out << "      \"speedup_vs_dense_with_index_reuse_32\": " << fmt(r.speedup_vs_dense_with_index_reuse_32) << ",\n";
    out << "      \"index_build_ns_per_cache\": " << fmt(r.index_build_ns_per_cache) << ",\n";
    out << "      \"index_build_dk_ops_per_cache\": " << fmt(r.index_build_dk_ops_per_cache) << ",\n";
    out << "      \"mean_qk_dot_products\": " << fmt(a.qk_dots / rows) << ",\n";
    out << "      \"qk_dot_fraction_vs_dense\": " << fmt((a.qk_dots / rows) / N) << ",\n";
    out << "      \"mean_score_reads\": " << fmt(a.score_reads / rows) << ",\n";
    out << "      \"mean_selected_values\": " << fmt(a.selected / rows) << ",\n";
    out << "      \"selected_value_fraction\": " << fmt((a.selected / rows) / N) << ",\n";
    out << "      \"mean_opened_blocks\": " << fmt(a.opened_blocks / rows) << ",\n";
    out << "      \"opened_block_fraction\": " << fmt((a.opened_blocks / rows) / BLOCKS) << ",\n";
    out << "      \"mean_true_mass_retained\": " << fmt(a.true_mass / rows) << ",\n";
    out << "      \"mean_asserted_lower_bound_mass_certificate\": " << fmt(a.asserted_cert / rows) << ",\n";
    out << "      \"mean_bound_violation_rate\": " << fmt(a.bound_violation_rate / rows) << ",\n";
    out << "      \"mean_attention_rel_l2_error\": " << fmt(a.rel_l2 / rows) << ",\n";
    out << "      \"mean_output_cosine\": " << fmt(a.cosine / rows) << ",\n";
    out << "      \"quality_bar_rate\": " << fmt(static_cast<double>(a.quality_pass) / rows) << ",\n";
    out << "      \"exact_dense_scores_required\": " << (r.exact_dense_scores_required ? "true" : "false") << ",\n";
    out << "      \"computes_all_qk_scores_before_selection\": " << (r.computes_all_qk_scores_before_selection ? "true" : "false") << ",\n";
    out << "      \"observable_index_from_key_cache\": " << (r.observable_index_from_key_cache ? "true" : "false") << ",\n";
    out << "      \"uses_generator_oracle_bounds\": " << (r.uses_generator_oracle_bounds ? "true" : "false") << ",\n";
    out << "      \"unsafe_sampled_radius\": " << (r.unsafe_sampled_radius ? "true" : "false") << ",\n";
    out << "      \"block_upper_bound_pruning\": " << (r.block_upper_bound_pruning ? "true" : "false") << ",\n";
    out << "      \"selection_uses_values\": " << (r.selection_uses_values ? "true" : "false") << ",\n";
    out << "      \"selection_uses_dense_output\": " << (r.selection_uses_dense_output ? "true" : "false") << ",\n";
    out << "      \"bound_is_certified\": " << (r.bound_is_certified ? "true" : "false") << ",\n";
    out << "      \"is_gpu_kernel_claim\": " << (r.is_gpu_kernel_claim ? "true" : "false") << "\n";
    out << "    }" << (comma ? "," : "") << "\n";
}

int main(int argc, char** argv) {
    std::string out_path = argc > 1 ? argv[1] : "artifacts/probe-results/REV0052_OBSERVABLE_BLOCK_INDEX_PRUNING.json";
    std::vector<SummaryRow> summaries;

    for (int regime = 0; regime < 4; ++regime) {
        KeyCache c = make_cache(regime);
        QuerySet qs = make_queries(c, regime);
        BlockIndex obs = build_observable_mean_radius_index(c);
        BlockIndex unsafe = build_sampled_radius_index(c);

        SummaryRow dense{c.regime, "dense_full_attention"};
        SummaryRow hist{c.regime, "dense_score_mass_histogram_0p95_sparse"};
        SummaryRow obsrow{c.regime, obs.name};
        SummaryRow unsaferow{c.regime, unsafe.name};
        dense.exact_dense_scores_required = true;
        dense.computes_all_qk_scores_before_selection = true;
        hist.exact_dense_scores_required = true;
        hist.computes_all_qk_scores_before_selection = true;
        obsrow.observable_index_from_key_cache = true;
        obsrow.block_upper_bound_pruning = true;
        obsrow.bound_is_certified = true;
        unsaferow.observable_index_from_key_cache = true;
        unsaferow.block_upper_bound_pruning = true;
        unsaferow.unsafe_sampled_radius = true;
        unsaferow.bound_is_certified = false;

        for (const auto& q : qs.queries) {
            std::vector<double> dense_scores = compute_scores_dense(q, c);
            std::vector<int> all(N);
            std::iota(all.begin(), all.end(), 0);
            std::vector<double> dense_y = output_from_selected(c, dense_scores, all);

            Output d; d.selected = all; d.y = dense_y; d.qk_dot_products = N; d.score_reads = N; d.exact_token_score_dots = N; d.exact_dense_scores_required = true;
            add_quality(dense.acc, c, dense_y, dense_scores, d);

            Output h = dense_score_mass_hist_sparse(q, c);
            add_quality(hist.acc, c, dense_y, dense_scores, h);

            Output o = block_pruned_attention(q, c, obs);
            add_quality(obsrow.acc, c, dense_y, dense_scores, o);

            Output u = block_pruned_attention(q, c, unsafe);
            add_quality(unsaferow.acc, c, dense_y, dense_scores, u);
        }

        long long dense_ns = time_dense_method(c, qs, dense_full_attention);
        long long hist_ns = time_dense_method(c, qs, dense_score_mass_hist_sparse);
        long long obs_ns = time_block_method(c, qs, obs);
        long long unsafe_ns = time_block_method(c, qs, unsafe);
        double denom = static_cast<double>(REPEATS * QUERIES);
        double dense_per = dense_ns / denom;
        dense.mean_ns_per_query = dense_per; dense.dense_ns_per_query = dense_per; dense.speedup_vs_dense_query_only = 1.0; dense.speedup_vs_dense_with_index_reuse_32 = 1.0;
        hist.mean_ns_per_query = hist_ns / denom; hist.dense_ns_per_query = dense_per; hist.speedup_vs_dense_query_only = dense_per / std::max(1.0, hist.mean_ns_per_query); hist.speedup_vs_dense_with_index_reuse_32 = hist.speedup_vs_dense_query_only;
        obsrow.mean_ns_per_query = obs_ns / denom; obsrow.dense_ns_per_query = dense_per; obsrow.index_build_ns_per_cache = obs.build_ns; obsrow.index_build_dk_ops_per_cache = obs.build_dk_ops; obsrow.speedup_vs_dense_query_only = dense_per / std::max(1.0, obsrow.mean_ns_per_query); obsrow.speedup_vs_dense_with_index_reuse_32 = dense_per / std::max(1.0, obsrow.mean_ns_per_query + obs.build_ns / static_cast<double>(BUILD_REUSE_QUERIES));
        unsaferow.mean_ns_per_query = unsafe_ns / denom; unsaferow.dense_ns_per_query = dense_per; unsaferow.index_build_ns_per_cache = unsafe.build_ns; unsaferow.index_build_dk_ops_per_cache = unsafe.build_dk_ops; unsaferow.speedup_vs_dense_query_only = dense_per / std::max(1.0, unsaferow.mean_ns_per_query); unsaferow.speedup_vs_dense_with_index_reuse_32 = dense_per / std::max(1.0, unsaferow.mean_ns_per_query + unsafe.build_ns / static_cast<double>(BUILD_REUSE_QUERIES));

        summaries.push_back(dense);
        summaries.push_back(hist);
        summaries.push_back(obsrow);
        summaries.push_back(unsaferow);
    }

    std::ofstream out(out_path);
    out << "{\n";
    out << "  \"project\": \"CloudtainerML\",\n";
    out << "  \"revision\": \"rev0052\",\n";
    out << "  \"artifact\": \"REV0052_OBSERVABLE_BLOCK_INDEX_PRUNING\",\n";
    out << "  \"benchmark_scope\": \"native_cpu_key_cache_row_attention_with_observable_block_index\",\n";
    out << "  \"gpu_kernel_claim\": false,\n";
    out << "  \"public_pretrained_trace_loaded\": false,\n";
    out << "  \"target_mass\": " << fmt(TARGET_MASS) << ",\n";
    out << "  \"quality_cosine_bar\": " << fmt(QUALITY_COSINE) << ",\n";
    out << "  \"quality_rel_l2_bar\": " << fmt(QUALITY_REL_L2) << ",\n";
    out << "  \"build_reuse_queries\": " << BUILD_REUSE_QUERIES << ",\n";
    out << "  \"summary\": {\n";
    out << "    \"promotion_allowed\": false,\n";
    out << "    \"primary_claim\": \"observable key-cache block bounds replace generator-side bounds; strong pruning only survives when observable radii are tight\",\n";
    out << "    \"negative_control\": \"unsafe sampled-radius bounds are intentionally present and must not be promoted when bound violations occur\",\n";
    out << "    \"remaining_blockers\": [\"actual_public_pretrained_trace_bundle_missing\", \"gpu_fused_attention_kernel_timing_missing\", \"model_trace_block_bound_tightness_missing\"]\n";
    out << "  },\n";
    out << "  \"rows\": [\n";
    for (size_t i = 0; i < summaries.size(); ++i) emit_row(out, summaries[i], i + 1 < summaries.size());
    out << "  ],\n";
    out << "  \"interpretation\": \"This rev0052 probe removes the generator-bound privilege from the score-path pruning story. Observable mean/radius indexes can still skip exact token scores in tight clustered caches, but broad or loose caches collapse toward dense score work. The sampled-radius negative control demonstrates why approximate bounds need validation: it may report high asserted mass while the upper bound is false.\"\n";
    out << "}\n";
    return 0;
}
