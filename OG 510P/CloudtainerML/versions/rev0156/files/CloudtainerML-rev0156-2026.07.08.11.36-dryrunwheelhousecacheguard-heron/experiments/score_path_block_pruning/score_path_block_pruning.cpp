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

// rev0051 score-path block-pruning probe.
//
// Prior sparse-attention probes mostly assumed that QK scores were already
// available.  That can create a false speed story: a selector may save V reads
// while still paying dense score computation.  This benchmark separates that
// cost by comparing:
//   1. dense full attention;
//   2. mass-histogram sparse attention after dense QK scoring;
//   3. block upper-bound pruning that can skip exact QK scores for unopened
//      blocks while certifying a lower bound on retained softmax mass.
//
// It is still a native CPU row microbenchmark, not a GPU/fused-kernel claim.

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
static constexpr int ROWS = 80;
static constexpr int REPEATS = 7;
static constexpr int BINS = 32;
static constexpr double TARGET_MASS = 0.95;
static constexpr double QUALITY_COSINE = 0.995;
static constexpr double QUALITY_REL_L2 = 0.18;
static constexpr double SQRT_DK = 8.0;

volatile double global_sink = 0.0;

struct Row {
    std::string regime;
    std::vector<double> q;
    std::vector<double> keys;      // N * DK
    std::vector<double> values;    // N * DV
    std::vector<double> centroids; // BLOCKS * DK
    std::vector<double> radii;     // BLOCKS
};

struct Output {
    std::vector<double> y;
    std::vector<int> selected;
    int qk_dot_products = 0;
    int score_reads = 0;
    int block_bound_dots = 0;
    int exact_token_score_dots = 0;
    int opened_blocks = 0;
    double lower_bound_mass_certificate = 1.0;
    bool exact_dense_scores_required = false;
};

struct MetricAcc {
    double true_mass = 0.0;
    double lower_cert = 0.0;
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
    double mean_ns_per_row = 0.0;
    double dense_ns_per_row = 0.0;
    double speedup_vs_dense = 1.0;
    MetricAcc acc;
    bool exact_dense_scores_required = false;
    bool computes_all_qk_scores_before_selection = false;
    bool block_upper_bound_pruning = false;
    bool selection_uses_values = false;
    bool selection_uses_dense_output = false;
    bool is_gpu_kernel_claim = false;
};

static double dot(const std::vector<double>& a, int a0, const std::vector<double>& b, int b0) {
    double s = 0.0;
    for (int d = 0; d < DK; ++d) s += a[a0 + d] * b[b0 + d];
    return s;
}

static double q_dot_key(const Row& r, int token) {
    double s = 0.0;
    int off = token * DK;
    for (int d = 0; d < DK; ++d) s += r.q[d] * r.keys[off + d];
    return s / SQRT_DK;
}

static double q_dot_centroid(const Row& r, int block) {
    double s = 0.0;
    int off = block * DK;
    for (int d = 0; d < DK; ++d) s += r.q[d] * r.centroids[off + d];
    return s / SQRT_DK;
}

static double norm_vec(const std::vector<double>& v, int off, int len) {
    double s = 0.0;
    for (int i = 0; i < len; ++i) s += v[off + i] * v[off + i];
    return std::sqrt(s);
}

static void normalize_block(std::vector<double>& v, int off, int len) {
    double n = norm_vec(v, off, len);
    if (n < 1e-12) {
        v[off] = 1.0;
        return;
    }
    for (int i = 0; i < len; ++i) v[off + i] /= n;
}

static Row make_row(int regime_id, int row_id) {
    XorShift64 rng(0x51000000ULL + 1000003ull * regime_id + 7919ull * row_id);
    Row r;
    const char* names[] = {
        "clustered_peaked_tight_bounds",
        "clustered_multipeak_tight_bounds",
        "broad_unstructured_loose_bounds",
        "peaked_but_loose_bounds"
    };
    r.regime = names[regime_id];
    r.q.assign(DK, 0.0);
    r.keys.assign(N * DK, 0.0);
    r.values.assign(N * DV, 0.0);
    r.centroids.assign(BLOCKS * DK, 0.0);
    r.radii.assign(BLOCKS, 0.0);

    for (int b = 0; b < BLOCKS; ++b) {
        for (int d = 0; d < DK; ++d) r.centroids[b * DK + d] = rng.normal();
        normalize_block(r.centroids, b * DK, DK);
    }

    double amp = 8.0;
    double noise_sigma = 0.04;
    if (regime_id == 2) { amp = 1.0; noise_sigma = 1.25; }
    if (regime_id == 3) { amp = 8.0; noise_sigma = 2.20; }

    int target0 = (row_id * 13 + 7) % BLOCKS;
    int target1 = (target0 + 17) % BLOCKS;
    int target2 = (target0 + 37) % BLOCKS;

    if (regime_id == 0 || regime_id == 3) {
        for (int d = 0; d < DK; ++d) r.q[d] = 10.0 * r.centroids[target0 * DK + d] + 0.02 * rng.normal();
    } else if (regime_id == 1) {
        for (int d = 0; d < DK; ++d) {
            r.q[d] = (10.0 / std::sqrt(3.0)) * (r.centroids[target0 * DK + d] + r.centroids[target1 * DK + d] + r.centroids[target2 * DK + d]) + 0.02 * rng.normal();
        }
    } else {
        for (int d = 0; d < DK; ++d) r.q[d] = rng.normal();
    }

    for (int b = 0; b < BLOCKS; ++b) {
        double max_res = 0.0;
        for (int j = 0; j < BLOCK; ++j) {
            int t = b * BLOCK + j;
            double res2 = 0.0;
            for (int d = 0; d < DK; ++d) {
                double noise = noise_sigma * rng.normal();
                double v = amp * r.centroids[b * DK + d] + noise;
                r.keys[t * DK + d] = v;
                res2 += noise * noise;
            }
            max_res = std::max(max_res, std::sqrt(res2));
            double vscale = 0.75 + 0.15 * rng.uniform();
            for (int d = 0; d < DV; ++d) r.values[t * DV + d] = vscale * rng.normal();
        }
        r.radii[b] = max_res + 1e-9;
    }
    return r;
}

static std::vector<double> compute_scores_dense(const Row& r) {
    std::vector<double> scores(N);
    for (int i = 0; i < N; ++i) scores[i] = q_dot_key(r, i);
    return scores;
}

static std::vector<double> softmax_probs(const std::vector<double>& scores) {
    double m = *std::max_element(scores.begin(), scores.end());
    std::vector<double> probs(scores.size());
    double z = 0.0;
    for (size_t i = 0; i < scores.size(); ++i) {
        double e = std::exp(std::max(-80.0, scores[i] - m));
        probs[i] = e;
        z += e;
    }
    if (z <= 0.0 || !std::isfinite(z)) {
        std::fill(probs.begin(), probs.end(), 1.0 / scores.size());
    } else {
        for (double& p : probs) p /= z;
    }
    return probs;
}

static std::vector<double> output_from_selected(const Row& r, const std::vector<double>& scores, const std::vector<int>& selected) {
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
        for (int d = 0; d < DV; ++d) y[d] += p * r.values[off + d];
    }
    return y;
}

static Output dense_full_attention(const Row& r) {
    Output o;
    std::vector<double> scores = compute_scores_dense(r);
    o.selected.resize(N);
    std::iota(o.selected.begin(), o.selected.end(), 0);
    o.y = output_from_selected(r, scores, o.selected);
    o.qk_dot_products = N;
    o.score_reads = N;
    o.exact_token_score_dots = N;
    o.exact_dense_scores_required = true;
    return o;
}

static std::vector<int> mass_histogram_indices(const std::vector<double>& scores, double target_mass) {
    double max_score = *std::max_element(scores.begin(), scores.end());
    std::vector<double> weights(N);
    double z = 0.0;
    for (int i = 0; i < N; ++i) {
        weights[i] = std::exp(std::max(-80.0, scores[i] - max_score));
        z += weights[i];
    }
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
    for (int b = 0; b <= BINS; ++b) {
        cum += mass[b];
        if (cum >= target_mass) { cutoff = b; break; }
    }
    std::vector<int> sel;
    sel.reserve(N);
    for (int i = 0; i < N; ++i) if (bid[i] <= cutoff) sel.push_back(i);
    return sel;
}

static Output dense_score_mass_hist_sparse(const Row& r) {
    Output o;
    std::vector<double> scores = compute_scores_dense(r);
    o.selected = mass_histogram_indices(scores, TARGET_MASS);
    o.y = output_from_selected(r, scores, o.selected);
    o.qk_dot_products = N;
    o.score_reads = 2 * N;
    o.exact_token_score_dots = N;
    o.exact_dense_scores_required = true;
    return o;
}

static Output block_bound_pruned_sparse(const Row& r) {
    Output o;
    double qnorm = norm_vec(r.q, 0, DK);
    std::vector<double> ub(BLOCKS);
    std::vector<int> order(BLOCKS);
    for (int b = 0; b < BLOCKS; ++b) {
        ub[b] = q_dot_centroid(r, b) + (qnorm * r.radii[b] / SQRT_DK);
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
                exact_scores[t] = q_dot_key(r, t);
                opened_tokens.push_back(t);
            }
        }
        double m = -std::numeric_limits<double>::infinity();
        for (int t : opened_tokens) m = std::max(m, exact_scores[t]);
        for (int bb = 0; bb < BLOCKS; ++bb) if (!opened_block[bb]) m = std::max(m, ub[bb]);
        double opened_w = 0.0;
        for (int t : opened_tokens) opened_w += std::exp(std::max(-80.0, exact_scores[t] - m));
        double unopened_upper_w = 0.0;
        for (int bb = 0; bb < BLOCKS; ++bb) {
            if (!opened_block[bb]) unopened_upper_w += BLOCK * std::exp(std::max(-80.0, ub[bb] - m));
        }
        cert = opened_w / std::max(1e-300, opened_w + unopened_upper_w);
        if (cert >= TARGET_MASS) break;
    }
    o.selected = opened_tokens;
    o.y = output_from_selected(r, exact_scores, o.selected);
    o.qk_dot_products = BLOCKS + static_cast<int>(opened_tokens.size());
    o.block_bound_dots = BLOCKS;
    o.exact_token_score_dots = static_cast<int>(opened_tokens.size());
    o.score_reads = static_cast<int>(opened_tokens.size());
    o.opened_blocks = opened_count;
    o.lower_bound_mass_certificate = cert;
    o.exact_dense_scores_required = false;
    return o;
}

static double l2_norm(const std::vector<double>& v) {
    double s = 0.0;
    for (double x : v) s += x * x;
    return std::sqrt(s);
}

static void add_quality(MetricAcc& acc, const Row& r, const std::vector<double>& dense_y, const std::vector<double>& dense_scores, const Output& out) {
    std::vector<double> probs = softmax_probs(dense_scores);
    double mass = 0.0;
    for (int idx : out.selected) mass += probs[idx];
    std::vector<double> diff(DV, 0.0);
    double dotp = 0.0;
    for (int d = 0; d < DV; ++d) {
        diff[d] = out.y[d] - dense_y[d];
        dotp += out.y[d] * dense_y[d];
    }
    double dense_norm = std::max(1e-12, l2_norm(dense_y));
    double out_norm = std::max(1e-12, l2_norm(out.y));
    double rel = l2_norm(diff) / dense_norm;
    double cos = std::max(-1.0, std::min(1.0, dotp / (dense_norm * out_norm)));
    bool pass = (mass >= TARGET_MASS && cos >= QUALITY_COSINE && rel <= QUALITY_REL_L2);
    acc.true_mass += mass;
    acc.lower_cert += out.lower_bound_mass_certificate;
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

using MethodFn = Output(*)(const Row&);

static long long time_method(const std::vector<Row>& rows, MethodFn fn) {
    auto start = std::chrono::steady_clock::now();
    for (int rep = 0; rep < REPEATS; ++rep) {
        for (const Row& r : rows) {
            Output o = fn(r);
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
    out << "      \"mean_ns_per_row\": " << fmt(r.mean_ns_per_row) << ",\n";
    out << "      \"dense_ns_per_row\": " << fmt(r.dense_ns_per_row) << ",\n";
    out << "      \"speedup_vs_dense\": " << fmt(r.speedup_vs_dense) << ",\n";
    out << "      \"mean_qk_dot_products\": " << fmt(a.qk_dots / rows) << ",\n";
    out << "      \"qk_dot_fraction_vs_dense\": " << fmt((a.qk_dots / rows) / N) << ",\n";
    out << "      \"mean_score_reads\": " << fmt(a.score_reads / rows) << ",\n";
    out << "      \"mean_selected_values\": " << fmt(a.selected / rows) << ",\n";
    out << "      \"selected_value_fraction\": " << fmt((a.selected / rows) / N) << ",\n";
    out << "      \"mean_opened_blocks\": " << fmt(a.opened_blocks / rows) << ",\n";
    out << "      \"opened_block_fraction\": " << fmt((a.opened_blocks / rows) / BLOCKS) << ",\n";
    out << "      \"mean_true_mass_retained\": " << fmt(a.true_mass / rows) << ",\n";
    out << "      \"mean_lower_bound_mass_certificate\": " << fmt(a.lower_cert / rows) << ",\n";
    out << "      \"mean_attention_rel_l2_error\": " << fmt(a.rel_l2 / rows) << ",\n";
    out << "      \"mean_output_cosine\": " << fmt(a.cosine / rows) << ",\n";
    out << "      \"quality_bar_rate\": " << fmt(static_cast<double>(a.quality_pass) / rows) << ",\n";
    out << "      \"exact_dense_scores_required\": " << (r.exact_dense_scores_required ? "true" : "false") << ",\n";
    out << "      \"computes_all_qk_scores_before_selection\": " << (r.computes_all_qk_scores_before_selection ? "true" : "false") << ",\n";
    out << "      \"block_upper_bound_pruning\": " << (r.block_upper_bound_pruning ? "true" : "false") << ",\n";
    out << "      \"selection_uses_values\": " << (r.selection_uses_values ? "true" : "false") << ",\n";
    out << "      \"selection_uses_dense_output\": " << (r.selection_uses_dense_output ? "true" : "false") << ",\n";
    out << "      \"is_gpu_kernel_claim\": " << (r.is_gpu_kernel_claim ? "true" : "false") << "\n";
    out << "    }" << (comma ? "," : "") << "\n";
}

int main(int argc, char** argv) {
    std::string out_path = argc > 1 ? argv[1] : "artifacts/probe-results/REV0051_SCORE_PATH_BLOCK_PRUNING.json";
    std::vector<SummaryRow> summaries;
    for (int regime = 0; regime < 4; ++regime) {
        std::vector<Row> rows;
        rows.reserve(ROWS);
        for (int i = 0; i < ROWS; ++i) rows.push_back(make_row(regime, i));
        std::string regime_name = rows[0].regime;

        // Quality pass: dense reference is computed only to score methods.
        SummaryRow dense{regime_name, "dense_full_attention"};
        SummaryRow hist{regime_name, "dense_score_mass_histogram_0p95_sparse"};
        SummaryRow block{regime_name, "block_upper_bound_pruned_0p95_sparse"};
        dense.exact_dense_scores_required = true;
        dense.computes_all_qk_scores_before_selection = true;
        hist.exact_dense_scores_required = true;
        hist.computes_all_qk_scores_before_selection = true;
        block.exact_dense_scores_required = false;
        block.computes_all_qk_scores_before_selection = false;
        block.block_upper_bound_pruning = true;

        for (const Row& r : rows) {
            std::vector<double> dense_scores = compute_scores_dense(r);
            std::vector<int> all(N);
            std::iota(all.begin(), all.end(), 0);
            std::vector<double> dense_y = output_from_selected(r, dense_scores, all);
            Output od;
            od.y = dense_y; od.selected = all; od.qk_dot_products = N; od.score_reads = N; od.lower_bound_mass_certificate = 1.0;
            add_quality(dense.acc, r, dense_y, dense_scores, od);
            Output oh = dense_score_mass_hist_sparse(r);
            add_quality(hist.acc, r, dense_y, dense_scores, oh);
            Output ob = block_bound_pruned_sparse(r);
            add_quality(block.acc, r, dense_y, dense_scores, ob);
        }

        long long dense_ns = time_method(rows, dense_full_attention);
        long long hist_ns = time_method(rows, dense_score_mass_hist_sparse);
        long long block_ns = time_method(rows, block_bound_pruned_sparse);
        double denom = static_cast<double>(ROWS * REPEATS);
        dense.mean_ns_per_row = dense_ns / denom;
        hist.mean_ns_per_row = hist_ns / denom;
        block.mean_ns_per_row = block_ns / denom;
        dense.dense_ns_per_row = dense.mean_ns_per_row;
        hist.dense_ns_per_row = dense.mean_ns_per_row;
        block.dense_ns_per_row = dense.mean_ns_per_row;
        dense.speedup_vs_dense = 1.0;
        hist.speedup_vs_dense = dense.mean_ns_per_row / std::max(1e-9, hist.mean_ns_per_row);
        block.speedup_vs_dense = dense.mean_ns_per_row / std::max(1e-9, block.mean_ns_per_row);
        summaries.push_back(dense);
        summaries.push_back(hist);
        summaries.push_back(block);
    }

    int hist_dense_score_rows = 0;
    int block_pruned_rows = 0;
    double peaked_block_qk = 1.0;
    double peaked_block_speed = 0.0;
    double broad_block_qk = 0.0;
    double broad_block_speed = 0.0;
    double loose_block_qk = 0.0;
    for (const auto& s : summaries) {
        if (s.method == "dense_score_mass_histogram_0p95_sparse" && s.computes_all_qk_scores_before_selection) hist_dense_score_rows++;
        if (s.method == "block_upper_bound_pruned_0p95_sparse") {
            block_pruned_rows++;
            double qk_frac = (s.acc.qk_dots / std::max(1, s.acc.rows)) / N;
            if (s.regime == "clustered_peaked_tight_bounds") { peaked_block_qk = qk_frac; peaked_block_speed = s.speedup_vs_dense; }
            if (s.regime == "broad_unstructured_loose_bounds") { broad_block_qk = qk_frac; broad_block_speed = s.speedup_vs_dense; }
            if (s.regime == "peaked_but_loose_bounds") loose_block_qk = qk_frac;
        }
    }

    std::ofstream out(out_path);
    out << std::setprecision(10);
    out << "{\n";
    out << "  \"project\": \"CloudtainerML\",\n";
    out << "  \"revision\": \"rev0051\",\n";
    out << "  \"kind\": \"score_path_block_pruning_cpu_microbench\",\n";
    out << "  \"claim_scope\": \"native CPU single-row attention score-path microbenchmark; not a GPU/fused-kernel or public-model throughput claim\",\n";
    out << "  \"target_mass\": " << fmt(TARGET_MASS) << ",\n";
    out << "  \"rows_per_regime\": " << ROWS << ",\n";
    out << "  \"repeats\": " << REPEATS << ",\n";
    out << "  \"guard_fields\": [\"exact_dense_scores_required\", \"computes_all_qk_scores_before_selection\", \"qk_dot_fraction_vs_dense\", \"selection_uses_values\", \"selection_uses_dense_output\", \"is_gpu_kernel_claim\"],\n";
    out << "  \"summary\": {\n";
    out << "    \"promotion_allowed\": false,\n";
    out << "    \"histogram_rows_that_still_compute_dense_scores\": " << hist_dense_score_rows << ",\n";
    out << "    \"block_pruned_method_rows\": " << block_pruned_rows << ",\n";
    out << "    \"peaked_block_qk_dot_fraction\": " << fmt(peaked_block_qk) << ",\n";
    out << "    \"peaked_block_speedup_vs_dense\": " << fmt(peaked_block_speed) << ",\n";
    out << "    \"broad_block_qk_dot_fraction\": " << fmt(broad_block_qk) << ",\n";
    out << "    \"broad_block_speedup_vs_dense\": " << fmt(broad_block_speed) << ",\n";
    out << "    \"loose_bound_block_qk_dot_fraction\": " << fmt(loose_block_qk) << ",\n";
    out << "    \"main_result\": \"dense-score sparse selectors save value reads but not QK score computation; block bounds can save score dots only in clustered tight-bound regimes and collapse when attention is broad or bounds are loose\"\n";
    out << "  },\n";
    out << "  \"rows\": [\n";
    for (size_t i = 0; i < summaries.size(); ++i) emit_row(out, summaries[i], i + 1 < summaries.size());
    out << "  ],\n";
    out << "  \"remaining_blockers\": [\"actual_public_pretrained_trace_bundle_missing\", \"gpu_fused_attention_kernel_timing_missing\", \"model_trace_block_bound_tightness_missing\"],\n";
    out << "  \"interpretation\": \"rev0051 adds score-path accounting. A selector that starts from all QK scores is not a full sparse-attention systems win; it only sparsifies softmax/V after dense scoring. Conservative block upper bounds provide a deployable route to skip exact token scores, but only when keys are block-clustered tightly enough.\"\n";
    out << "}\n";
    return 0;
}
