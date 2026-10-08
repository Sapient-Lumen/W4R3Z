#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <string>
#include <vector>

// rev0050 value-norm sidecar CPU path probe.
// Measures whether the value-norm exception repair from rev0046/rev0047 is still
// plausible when its metadata path is accounted for.  It explicitly separates:
//   1. score-only mass histogram selection;
//   2. value-norm exception selection using a precomputed norm sidecar;
//   3. value-norm exception selection that computes norms from V on the query path.
// The last mode is intentionally a negative control: it reads all V vectors during
// selection and therefore is not a deployable sparse path.

struct XorShift64 {
    uint64_t x;
    explicit XorShift64(uint64_t seed) : x(seed ? seed : 88172645463325252ull) {}
    uint64_t next_u64() {
        x ^= x << 7;
        x ^= x >> 9;
        return x;
    }
    double uniform() { return (next_u64() >> 11) * (1.0 / 9007199254740992.0); }
    double normal() {
        double u1 = std::max(1e-12, uniform());
        double u2 = uniform();
        return std::sqrt(-2.0 * std::log(u1)) * std::cos(6.283185307179586 * u2);
    }
};

static constexpr int N = 1024;
static constexpr int DK = 64;
static constexpr int DV = 64;
static constexpr int ROWS = 96;
static constexpr int REPEATS = 20;
static constexpr int K = 32;
static constexpr int BINS = 32;
static constexpr double TARGET_MASS = 0.95;
static constexpr double VALUE_BOUND = 0.25;
static constexpr int EXCEPTION_CAP = 64;
static constexpr double QUALITY_COSINE = 0.995;
static constexpr double QUALITY_REL_L2 = 0.18;

struct Row {
    std::vector<double> q;
    std::vector<double> keys;
    std::vector<double> values;
    std::vector<double> norms; // precomputed sidecar
};

struct Selection {
    std::vector<int> idx;
    int norm_metadata_reads = 0;
    int value_reads_for_selection = 0;
    int exceptions_added = 0;
    double bound = 0.0;
};

struct Output {
    std::vector<double> y;
    int selected = 0;
    double mass = 1.0;
    int norm_metadata_reads = 0;
    int value_reads_for_selection = 0;
    int exceptions_added = 0;
};

static inline double clamp_exp_arg(double x) {
    if (x < -80.0) return -80.0;
    if (x > 0.0) return 0.0;
    return x;
}

void set_score_key(Row& r, int token, double desired_score, XorShift64& rng) {
    r.keys[token * DK] = desired_score;
    for (int d = 1; d < DK; ++d) r.keys[token * DK + d] = 0.01 * rng.normal();
}

void set_random_value(Row& r, int token, XorShift64& rng, double scale = 1.0) {
    double norm2 = 0.0;
    for (int d = 0; d < DV; ++d) {
        double v = scale * rng.normal();
        r.values[token * DV + d] = v;
        norm2 += v * v;
    }
    r.norms[token] = std::sqrt(norm2);
}

void set_spike_value(Row& r, int token, double magnitude, int dim) {
    for (int d = 0; d < DV; ++d) r.values[token * DV + d] = 0.0;
    r.values[token * DV + (dim % DV)] = magnitude;
    r.norms[token] = std::abs(magnitude);
}

Row make_row(int regime, int row_id) {
    XorShift64 rng(0xA77E5000ULL + 1000003ull * regime + 9176ull * row_id);
    Row r;
    r.q.assign(DK, 0.0);
    r.q[0] = std::sqrt(static_cast<double>(DK));
    r.keys.assign(N * DK, 0.0);
    r.values.assign(N * DV, 0.0);
    r.norms.assign(N, 1.0);

    std::vector<double> scores(N, 0.0);
    if (regime == 0) { // peaked_bounded: sparse-friendly.
        for (int i = 0; i < N; ++i) scores[i] = 0.08 * rng.normal();
        for (int j = 0; j < 48; ++j) {
            int idx = (j * 7919 + row_id * 17) % N;
            scores[idx] = 7.0 + 0.15 * rng.normal();
        }
    } else if (regime == 1) { // broad_bounded: sparse-hostile.
        for (int i = 0; i < N; ++i) scores[i] = 0.22 * rng.normal();
    } else { // peaked_tail_norm_spikes: mass-only fails unless norm sidecar catches exceptions.
        for (int i = 0; i < N; ++i) scores[i] = 0.08 * rng.normal();
        for (int j = 0; j < 48; ++j) {
            int idx = (j * 7919 + row_id * 17) % N;
            scores[idx] = 7.0 + 0.15 * rng.normal();
        }
        for (int j = 0; j < 4; ++j) {
            int idx = N - 1 - ((row_id * 13 + j * 37) % (N / 2));
            scores[idx] = 1.0 - 0.05 * j;
        }
    }
    for (int i = 0; i < N; ++i) {
        set_score_key(r, i, scores[i], rng);
        set_random_value(r, i, rng, 1.0);
    }
    if (regime == 2) {
        for (int j = 0; j < 4; ++j) {
            int idx = N - 1 - ((row_id * 13 + j * 37) % (N / 2));
            set_spike_value(r, idx, 18000.0 + 900.0 * j, j);
        }
    }
    return r;
}

std::vector<double> compute_scores(const Row& r) {
    std::vector<double> scores(N, 0.0);
    const double inv_sqrt = 1.0 / std::sqrt(static_cast<double>(DK));
    for (int i = 0; i < N; ++i) {
        double dot = 0.0;
        const double* kp = &r.keys[i * DK];
        for (int d = 0; d < DK; ++d) dot += r.q[d] * kp[d];
        scores[i] = dot * inv_sqrt;
    }
    return scores;
}

std::vector<double> compute_norms_from_values(const Row& r) {
    std::vector<double> norms(N, 0.0);
    for (int i = 0; i < N; ++i) {
        double s = 0.0;
        const double* vp = &r.values[i * DV];
        for (int d = 0; d < DV; ++d) s += vp[d] * vp[d];
        norms[i] = std::sqrt(s);
    }
    return norms;
}

std::vector<double> softmax_probs(const std::vector<double>& scores) {
    double m = *std::max_element(scores.begin(), scores.end());
    std::vector<double> p(scores.size());
    double z = 0.0;
    for (size_t i = 0; i < scores.size(); ++i) {
        p[i] = std::exp(clamp_exp_arg(scores[i] - m));
        z += p[i];
    }
    if (!(z > 0.0) || !std::isfinite(z)) {
        double u = 1.0 / scores.size();
        std::fill(p.begin(), p.end(), u);
        return p;
    }
    for (double& x : p) x /= z;
    return p;
}

Selection select_topk(const std::vector<double>& scores) {
    std::vector<int> idx(N);
    std::iota(idx.begin(), idx.end(), 0);
    std::nth_element(idx.begin(), idx.begin() + K, idx.end(), [&](int a, int b) { return scores[a] > scores[b]; });
    idx.resize(K);
    std::sort(idx.begin(), idx.end());
    return {idx, 0, 0, 0, 0.0};
}

Selection select_histogram_mass(const std::vector<double>& scores) {
    double max_score = *std::max_element(scores.begin(), scores.end());
    double width = 16.0 / BINS;
    std::vector<int> bin(N);
    std::vector<double> mass_by_bin(BINS + 1, 0.0);
    std::vector<double> weights(N);
    double z = 0.0;
    for (int i = 0; i < N; ++i) {
        double rel = std::max(0.0, max_score - scores[i]);
        int b = static_cast<int>(std::floor(rel / width));
        if (b < 0) b = 0;
        if (b > BINS) b = BINS;
        bin[i] = b;
        weights[i] = std::exp(clamp_exp_arg(scores[i] - max_score));
        z += weights[i];
    }
    for (int i = 0; i < N; ++i) mass_by_bin[bin[i]] += weights[i] / z;
    double cum = 0.0;
    int cutoff = BINS;
    for (int b = 0; b <= BINS; ++b) {
        cum += mass_by_bin[b];
        if (cum >= TARGET_MASS) { cutoff = b; break; }
    }
    Selection s;
    s.idx.reserve(N);
    for (int i = 0; i < N; ++i) if (bin[i] <= cutoff) s.idx.push_back(i);
    return s;
}

double value_norm_bound(const std::vector<double>& probs, const std::vector<double>& norms, const std::vector<char>& mask) {
    double mass = 0.0, selected_weighted_norm = 0.0, omitted_weighted_norm = 0.0;
    for (int i = 0; i < N; ++i) {
        if (mask[i]) { mass += probs[i]; selected_weighted_norm += probs[i] * norms[i]; }
        else { omitted_weighted_norm += probs[i] * norms[i]; }
    }
    double selected_expected_norm = (mass > 0.0) ? selected_weighted_norm / mass : 0.0;
    return (1.0 - mass) * selected_expected_norm + omitted_weighted_norm;
}

Selection select_value_norm_exception_with_norms(const std::vector<double>& scores, const std::vector<double>& norms, bool sidecar_norms, int value_reads_for_selection) {
    Selection base = select_histogram_mass(scores);
    std::vector<char> mask(N, 0);
    for (int i : base.idx) mask[i] = 1;
    std::vector<double> probs = softmax_probs(scores);

    // rev0050 refactor: compute certificate aggregates once and update them in O(1)
    // per exception. The previous diagnostic implementation rescanned all N tokens
    // after every exception, which made the repair look less deployable than its
    // certificate semantics require.
    double mass = 0.0;
    double selected_weighted_norm = 0.0;
    double omitted_weighted_norm = 0.0;
    for (int i = 0; i < N; ++i) {
        double contrib = probs[i] * norms[i];
        if (mask[i]) { mass += probs[i]; selected_weighted_norm += contrib; }
        else { omitted_weighted_norm += contrib; }
    }
    auto current_bound = [&]() {
        double selected_expected_norm = (mass > 0.0) ? selected_weighted_norm / mass : 0.0;
        return (1.0 - mass) * selected_expected_norm + omitted_weighted_norm;
    };
    double bound = current_bound();

    std::vector<int> tail;
    tail.reserve(N);
    for (int i = 0; i < N; ++i) if (!mask[i]) tail.push_back(i);
    std::sort(tail.begin(), tail.end(), [&](int a, int b) { return probs[a] * norms[a] > probs[b] * norms[b]; });
    int exceptions = 0;
    for (int idx : tail) {
        if (bound <= VALUE_BOUND || exceptions >= EXCEPTION_CAP) break;
        mask[idx] = 1;
        base.idx.push_back(idx);
        double contrib = probs[idx] * norms[idx];
        mass += probs[idx];
        selected_weighted_norm += contrib;
        omitted_weighted_norm -= contrib;
        if (omitted_weighted_norm < 0.0) omitted_weighted_norm = 0.0;
        ++exceptions;
        bound = current_bound();
    }
    std::sort(base.idx.begin(), base.idx.end());
    base.idx.erase(std::unique(base.idx.begin(), base.idx.end()), base.idx.end());
    base.norm_metadata_reads = sidecar_norms ? N : 0;
    base.value_reads_for_selection = value_reads_for_selection;
    base.exceptions_added = exceptions;
    base.bound = bound;
    return base;
}

Selection select_value_norm_exception_sidecar(const std::vector<double>& scores, const Row& r) {
    return select_value_norm_exception_with_norms(scores, r.norms, true, 0);
}

Selection select_value_norm_exception_on_the_fly(const std::vector<double>& scores, const Row& r) {
    std::vector<double> norms = compute_norms_from_values(r);
    return select_value_norm_exception_with_norms(scores, norms, false, N);
}

Output accumulate_dense(const Row& r, const std::vector<double>& scores) {
    std::vector<double> probs = softmax_probs(scores);
    Output o;
    o.y.assign(DV, 0.0);
    o.selected = N;
    o.mass = 1.0;
    for (int i = 0; i < N; ++i) {
        const double* vp = &r.values[i * DV];
        double pi = probs[i];
        for (int d = 0; d < DV; ++d) o.y[d] += pi * vp[d];
    }
    return o;
}

Output accumulate_sparse(const Row& r, const std::vector<double>& scores, const Selection& sel) {
    double m = -std::numeric_limits<double>::infinity();
    for (int idx : sel.idx) m = std::max(m, scores[idx]);
    double z = 0.0;
    std::vector<double> weights(sel.idx.size(), 0.0);
    for (size_t j = 0; j < sel.idx.size(); ++j) {
        weights[j] = std::exp(clamp_exp_arg(scores[sel.idx[j]] - m));
        z += weights[j];
    }
    Output o;
    o.y.assign(DV, 0.0);
    o.selected = static_cast<int>(sel.idx.size());
    o.norm_metadata_reads = sel.norm_metadata_reads;
    o.value_reads_for_selection = sel.value_reads_for_selection;
    o.exceptions_added = sel.exceptions_added;
    if (!(z > 0.0) || !std::isfinite(z) || sel.idx.empty()) return o;
    for (size_t j = 0; j < sel.idx.size(); ++j) {
        double pj = weights[j] / z;
        const double* vp = &r.values[sel.idx[j] * DV];
        for (int d = 0; d < DV; ++d) o.y[d] += pj * vp[d];
    }
    std::vector<double> dense_probs = softmax_probs(scores);
    double mass = 0.0;
    for (int idx : sel.idx) mass += dense_probs[idx];
    o.mass = mass;
    return o;
}

Output forward_method(const Row& r, const std::string& method) {
    std::vector<double> scores = compute_scores(r);
    if (method == "dense_full_softmax") return accumulate_dense(r, scores);
    if (method == "mass_histogram_0p95_sparse") return accumulate_sparse(r, scores, select_histogram_mass(scores));
    if (method == "value_norm_exception_sidecar_0p95_sparse") return accumulate_sparse(r, scores, select_value_norm_exception_sidecar(scores, r));
    if (method == "value_norm_exception_onthefly_0p95_sparse") return accumulate_sparse(r, scores, select_value_norm_exception_on_the_fly(scores, r));
    if (method == "exact_topk_32_sparse") return accumulate_sparse(r, scores, select_topk(scores));
    return accumulate_dense(r, scores);
}

double l2_norm(const std::vector<double>& x) {
    double s = 0.0;
    for (double v : x) s += v * v;
    return std::sqrt(s);
}

double cosine(const std::vector<double>& a, const std::vector<double>& b) {
    double dot = 0.0, aa = 0.0, bb = 0.0;
    for (size_t i = 0; i < a.size(); ++i) { dot += a[i] * b[i]; aa += a[i] * a[i]; bb += b[i] * b[i]; }
    double den = std::sqrt(aa) * std::sqrt(bb);
    if (!(den > 1e-12)) return 0.0;
    double c = dot / den;
    if (c > 1.0) c = 1.0;
    if (c < -1.0) c = -1.0;
    return c;
}

struct QualitySummary {
    double mean_selected = 0.0;
    double mean_mass = 0.0;
    double mean_rel_l2 = 0.0;
    double mean_cosine = 0.0;
    double quality_rate = 0.0;
    double mean_norm_reads = 0.0;
    double mean_value_reads_for_selection = 0.0;
    double mean_exceptions_added = 0.0;
};

QualitySummary quality_for(const std::vector<Row>& rows, const std::string& method) {
    QualitySummary q;
    int pass = 0;
    for (const Row& r : rows) {
        Output dense = forward_method(r, "dense_full_softmax");
        Output out = forward_method(r, method);
        std::vector<double> diff(DV, 0.0);
        for (int d = 0; d < DV; ++d) diff[d] = out.y[d] - dense.y[d];
        double rel = l2_norm(diff) / std::max(1e-9, l2_norm(dense.y));
        double cosv = (method == "dense_full_softmax") ? 1.0 : cosine(out.y, dense.y);
        bool ok = (out.mass >= TARGET_MASS && cosv >= QUALITY_COSINE && rel <= QUALITY_REL_L2);
        if (method == "dense_full_softmax") ok = true;
        q.mean_selected += out.selected;
        q.mean_mass += out.mass;
        q.mean_rel_l2 += rel;
        q.mean_cosine += cosv;
        q.mean_norm_reads += out.norm_metadata_reads;
        q.mean_value_reads_for_selection += out.value_reads_for_selection;
        q.mean_exceptions_added += out.exceptions_added;
        if (ok) ++pass;
    }
    double n = static_cast<double>(rows.size());
    q.mean_selected /= n;
    q.mean_mass /= n;
    q.mean_rel_l2 /= n;
    q.mean_cosine /= n;
    q.mean_norm_reads /= n;
    q.mean_value_reads_for_selection /= n;
    q.mean_exceptions_added /= n;
    q.quality_rate = pass / n;
    return q;
}

template <typename Fn>
double time_ns_per_row(const std::vector<Row>& rows, Fn fn, double& mean_selected_sink) {
    volatile double sink = 0.0;
    int64_t total_selected = 0;
    auto start = std::chrono::steady_clock::now();
    for (int rep = 0; rep < REPEATS; ++rep) {
        for (const Row& r : rows) {
            Output o = fn(r);
            sink += o.y[0] + 1e-9 * o.selected + 1e-12 * o.norm_metadata_reads;
            total_selected += o.selected;
        }
    }
    auto stop = std::chrono::steady_clock::now();
    (void)sink;
    double ns = std::chrono::duration_cast<std::chrono::nanoseconds>(stop - start).count();
    mean_selected_sink = static_cast<double>(total_selected) / (REPEATS * rows.size());
    return ns / (REPEATS * rows.size());
}

double time_sidecar_build_ns_per_row(const std::vector<Row>& rows, double& mean_norm_sink) {
    volatile double sink = 0.0;
    auto start = std::chrono::steady_clock::now();
    for (int rep = 0; rep < REPEATS; ++rep) {
        for (const Row& r : rows) {
            std::vector<double> norms = compute_norms_from_values(r);
            sink += norms[0];
        }
    }
    auto stop = std::chrono::steady_clock::now();
    (void)sink;
    mean_norm_sink = sink;
    double ns = std::chrono::duration_cast<std::chrono::nanoseconds>(stop - start).count();
    return ns / (REPEATS * rows.size());
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: value_norm_sidecar_cpu_path <output.json>\n";
        return 2;
    }
    std::vector<std::string> regimes = {"peaked_bounded", "broad_bounded", "peaked_tail_norm_spikes"};
    std::vector<std::string> methods = {
        "dense_full_softmax",
        "exact_topk_32_sparse",
        "mass_histogram_0p95_sparse",
        "value_norm_exception_sidecar_0p95_sparse",
        "value_norm_exception_onthefly_0p95_sparse"
    };
    std::ofstream out(argv[1]);
    out << std::fixed << std::setprecision(6);
    out << "{\n";
    out << "  \"project\": \"CloudtainerML\",\n";
    out << "  \"probe\": \"value_norm_sidecar_cpu_path\",\n";
    out << "  \"kind\": \"cpp_native_cpu_row_attention_sidecar_microbench\",\n";
    out << "  \"timing_scope\": \"native_cpu_row_attention_with_sidecar_metadata_accounting_not_gpu_kernel_not_model_throughput\",\n";
    out << "  \"N\": " << N << ", \"d_key\": " << DK << ", \"d_value\": " << DV << ", \"rows_per_regime\": " << ROWS << ", \"repeats\": " << REPEATS << ",\n";
    out << "  \"target_mass\": " << TARGET_MASS << ", \"quality_cosine\": " << QUALITY_COSINE << ", \"quality_rel_l2\": " << QUALITY_REL_L2 << ", \"value_norm_bound\": " << VALUE_BOUND << ",\n";
    out << "  \"sidecar_contract\": {\"precomputed_norm_sidecar_bytes_per_token\": 8, \"on_the_fly_norms_read_value_vectors_for_selection\": true, \"sidecar_selection_reads_value_vectors\": false, \"value_norm_bound_update_mode\": \"incremental_aggregate\"},\n";
    out << "  \"guard_fields\": [\"mean_ns_per_row\", \"speedup_vs_dense\", \"sidecar_build_ns_per_row\", \"speedup_vs_dense_with_sidecar_build_reuse_1\", \"speedup_vs_dense_with_sidecar_build_reuse_8\", \"speedup_vs_dense_with_sidecar_build_reuse_32\", \"mean_value_reads\", \"mean_norm_metadata_reads\", \"mean_value_reads_for_selection\", \"selection_uses_values\", \"uses_precomputed_sidecar\", \"quality_bar_rate\", \"is_gpu_kernel_claim\"],\n";
    out << "  \"rows\": [\n";
    bool first = true;
    for (int regime = 0; regime < static_cast<int>(regimes.size()); ++regime) {
        std::vector<Row> rows;
        rows.reserve(ROWS);
        for (int i = 0; i < ROWS; ++i) rows.push_back(make_row(regime, i));
        double build_sink = 0.0;
        double sidecar_build_ns = time_sidecar_build_ns_per_row(rows, build_sink);
        double dense_ns = 0.0;
        std::vector<double> timings;
        std::vector<QualitySummary> quals;
        timings.reserve(methods.size());
        quals.reserve(methods.size());
        for (const std::string& method : methods) {
            double selected_sink = 0.0;
            double ns = time_ns_per_row(rows, [&](const Row& r) { return forward_method(r, method); }, selected_sink);
            QualitySummary q = quality_for(rows, method);
            if (method == "dense_full_softmax") dense_ns = ns;
            timings.push_back(ns);
            quals.push_back(q);
        }
        for (size_t mi = 0; mi < methods.size(); ++mi) {
            const std::string& method = methods[mi];
            if (!first) out << ",\n";
            first = false;
            const auto& q = quals[mi];
            double speedup = (timings[mi] > 0.0) ? dense_ns / timings[mi] : 0.0;
            bool uses_sidecar = (method == "value_norm_exception_sidecar_0p95_sparse");
            bool selection_uses_values = (method == "value_norm_exception_onthefly_0p95_sparse");
            bool includes_build = false;
            double eff1 = timings[mi] + (uses_sidecar ? sidecar_build_ns : 0.0);
            double eff8 = timings[mi] + (uses_sidecar ? sidecar_build_ns / 8.0 : 0.0);
            double eff32 = timings[mi] + (uses_sidecar ? sidecar_build_ns / 32.0 : 0.0);
            out << "    {\"regime\": \"" << regimes[regime] << "\", \"method\": \"" << method << "\", "
                << "\"mean_ns_per_row\": " << timings[mi] << ", \"speedup_vs_dense\": " << speedup
                << ", \"sidecar_build_ns_per_row\": " << (uses_sidecar ? sidecar_build_ns : 0.0)
                << ", \"timing_includes_sidecar_build\": " << (includes_build ? "true" : "false")
                << ", \"speedup_vs_dense_with_sidecar_build_reuse_1\": " << ((eff1 > 0.0) ? dense_ns / eff1 : 0.0)
                << ", \"speedup_vs_dense_with_sidecar_build_reuse_8\": " << ((eff8 > 0.0) ? dense_ns / eff8 : 0.0)
                << ", \"speedup_vs_dense_with_sidecar_build_reuse_32\": " << ((eff32 > 0.0) ? dense_ns / eff32 : 0.0)
                << ", \"mean_selected_count\": " << q.mean_selected
                << ", \"mean_value_reads\": " << q.mean_selected
                << ", \"mean_norm_metadata_reads\": " << q.mean_norm_reads
                << ", \"mean_value_reads_for_selection\": " << q.mean_value_reads_for_selection
                << ", \"mean_exceptions_added\": " << q.mean_exceptions_added
                << ", \"selected_fraction\": " << (q.mean_selected / N)
                << ", \"mean_mass_retained\": " << q.mean_mass
                << ", \"mean_attention_rel_l2_error\": " << q.mean_rel_l2
                << ", \"mean_output_cosine\": " << q.mean_cosine
                << ", \"quality_bar_rate\": " << q.quality_rate
                << ", \"uses_precomputed_sidecar\": " << (uses_sidecar ? "true" : "false")
                << ", \"selection_uses_values\": " << (selection_uses_values ? "true" : "false")
                << ", \"selection_uses_dense_output\": false"
                << ", \"timing_includes_qk_scores\": true, \"timing_includes_softmax\": true, \"timing_includes_value_accumulation\": true, \"is_gpu_kernel_claim\": false}";
        }
    }
    out << "\n  ]\n";
    out << "}\n";
    return 0;
}
