#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <random>
#include <sstream>
#include <string>
#include <vector>

using Clock = std::chrono::steady_clock;

static constexpr int N = 1024;
static constexpr int D = 64;
static constexpr int DV = 64;
static constexpr int ROWS_PER_REGIME = 64;
static constexpr int REPEATS = 4;
static constexpr int HIST_BINS = 64;
static constexpr double TARGET_MASS = 0.95;
static constexpr double MAX_DELTA = 16.0;
static constexpr double INV_SQRT_D = 1.0 / 8.0;

struct Row {
    std::vector<float> q;
    std::vector<float> k;  // N * D
    std::vector<float> v;  // N * DV
};

struct MethodOutput {
    std::vector<double> out;
    int selected = 0;
    double mass = 1.0;
    long long qk_dots = 0;
    long long value_reads = 0;
    long long score_writes = 0;
    long long score_reads = 0;
    int score_passes = 1;
    bool materializes_scores = false;
    bool materialization_free_streaming = false;
    bool uses_dense_output_for_selection = false;
    bool uses_values_for_selection = false;
    double checksum = 0.0;
};

struct Accum {
    std::string regime;
    std::string method;
    double ns_total = 0.0;
    int rows = 0;
    double selected_sum = 0.0;
    double mass_sum = 0.0;
    double rel_l2_sum = 0.0;
    double cosine_sum = 0.0;
    double quality_sum = 0.0;
    double qk_sum = 0.0;
    double value_sum = 0.0;
    double score_writes_sum = 0.0;
    double score_reads_sum = 0.0;
    int score_passes = 0;
    bool materializes_scores = false;
    bool materialization_free_streaming = false;
    double dense_ns_per_row = 0.0;
};

static inline float dot_score(const float* q, const float* k) {
    float s = 0.0f;
    for (int d = 0; d < D; ++d) s += q[d] * k[d];
    return s * static_cast<float>(INV_SQRT_D);
}

static double norm2(const std::vector<double>& x) {
    double s = 0.0;
    for (double a : x) s += a * a;
    return std::sqrt(s);
}

static double cosine(const std::vector<double>& a, const std::vector<double>& b) {
    double num = 0.0, aa = 0.0, bb = 0.0;
    for (int i = 0; i < (int)a.size(); ++i) {
        num += a[i] * b[i]; aa += a[i] * a[i]; bb += b[i] * b[i];
    }
    double den = std::sqrt(std::max(aa, 0.0)) * std::sqrt(std::max(bb, 0.0));
    if (den <= 1e-30) return 0.0;
    double c = num / den;
    return std::max(-1.0, std::min(1.0, c));
}

static Row make_row(const std::string& regime, std::mt19937& rng, int row_id) {
    std::normal_distribution<float> nd(0.0f, 1.0f);
    Row r;
    r.q.resize(D); r.k.resize(N * D); r.v.resize(N * DV);
    for (int d = 0; d < D; ++d) r.q[d] = nd(rng);
    // Keep q norm close to sqrt(D) so q-parallel key multipliers map to predictable scores.
    double qn = 0.0;
    for (float x : r.q) qn += double(x) * double(x);
    qn = std::sqrt(qn);
    for (int d = 0; d < D; ++d) r.q[d] = static_cast<float>(r.q[d] * (std::sqrt((double)D) / std::max(qn, 1e-9)));

    int support = 64;
    float support_amp = 0.25f;
    float background_amp = -0.05f;
    float noise = 0.05f;
    bool value_tail = false;
    if (regime == "peaked_low_support") { support = 32; support_amp = 0.62f; background_amp = -0.22f; noise = 0.035f; }
    else if (regime == "medium_support") { support = 192; support_amp = 0.22f; background_amp = -0.035f; noise = 0.10f; }
    else if (regime == "broad_high_entropy") { support = 0; support_amp = 0.0f; background_amp = 0.0f; noise = 0.12f; }
    else if (regime == "value_tail_outlier") { support = 64; support_amp = 0.50f; background_amp = -0.50f; noise = 0.02f; value_tail = true; }

    for (int i = 0; i < N; ++i) {
        float amp;
        if (regime == "broad_high_entropy") amp = 0.0f;
        else if (i < support) amp = support_amp;
        else amp = background_amp;
        for (int d = 0; d < D; ++d) {
            float eps = noise * nd(rng);
            r.k[i * D + d] = amp * r.q[d] + eps;
        }
        for (int j = 0; j < DV; ++j) {
            r.v[i * DV + j] = nd(rng) / std::sqrt((float)DV);
        }
    }
    if (value_tail) {
        int tail = N - 1;
        // Low-score tail omitted by mass-only thresholds, but with huge value norm.
        for (int d = 0; d < D; ++d) r.k[tail * D + d] = 0.0f + 0.01f * nd(rng);
        for (int j = 0; j < DV; ++j) r.v[tail * DV + j] = 0.0f;
        r.v[tail * DV + (row_id % DV)] = 4500.0f;
    }
    return r;
}

static MethodOutput dense_online(const Row& r) {
    MethodOutput mo; mo.out.assign(DV, 0.0); mo.selected = N; mo.mass = 1.0; mo.qk_dots = N; mo.value_reads = N; mo.score_passes = 1;
    double m = -std::numeric_limits<double>::infinity();
    double l = 0.0;
    for (int i = 0; i < N; ++i) {
        double s = dot_score(r.q.data(), &r.k[i * D]);
        double m2 = std::max(m, s);
        double a = std::exp(m - m2);
        double b = std::exp(s - m2);
        for (int j = 0; j < DV; ++j) mo.out[j] = mo.out[j] * a + double(r.v[i * DV + j]) * b;
        l = l * a + b;
        m = m2;
    }
    if (l > 0.0) for (double& x : mo.out) x /= l;
    for (int j = 0; j < DV; ++j) mo.checksum += mo.out[j] * (j + 1);
    return mo;
}

static int bin_for_delta(double delta) {
    if (delta >= MAX_DELTA) return HIST_BINS - 1;
    int b = (int)std::floor(delta / (MAX_DELTA / HIST_BINS));
    if (b < 0) b = 0;
    if (b >= HIST_BINS) b = HIST_BINS - 1;
    return b;
}

static double threshold_from_bins(const std::vector<double>& bins, double denom) {
    double cum = 0.0;
    double need = TARGET_MASS * denom;
    for (int b = 0; b < HIST_BINS; ++b) {
        cum += bins[b];
        if (cum >= need) return (b + 1) * (MAX_DELTA / HIST_BINS);
    }
    return MAX_DELTA + 1.0;
}

static MethodOutput materialized_histogram_mass(const Row& r) {
    MethodOutput mo; mo.out.assign(DV, 0.0); mo.materializes_scores = true; mo.materialization_free_streaming = false; mo.score_passes = 1;
    std::vector<float> scores(N);
    double max_s = -std::numeric_limits<double>::infinity();
    for (int i = 0; i < N; ++i) { scores[i] = dot_score(r.q.data(), &r.k[i * D]); max_s = std::max(max_s, (double)scores[i]); }
    mo.qk_dots = N; mo.score_writes = N;
    std::vector<double> bins(HIST_BINS, 0.0);
    double denom = 0.0;
    for (int i = 0; i < N; ++i) {
        double w = std::exp((double)scores[i] - max_s);
        denom += w;
        bins[bin_for_delta(max_s - (double)scores[i])] += w;
    }
    double threshold_delta = threshold_from_bins(bins, denom);
    double selected_mass_num = 0.0;
    double sel_max = -std::numeric_limits<double>::infinity();
    for (int i = 0; i < N; ++i) {
        if (max_s - (double)scores[i] <= threshold_delta) { mo.selected++; sel_max = std::max(sel_max, (double)scores[i]); }
    }
    double sel_den = 0.0;
    for (int i = 0; i < N; ++i) {
        double delta = max_s - (double)scores[i];
        if (delta <= threshold_delta) {
            double wdense = std::exp((double)scores[i] - max_s);
            selected_mass_num += wdense;
            double ws = std::exp((double)scores[i] - sel_max);
            sel_den += ws;
            for (int j = 0; j < DV; ++j) mo.out[j] += double(r.v[i * DV + j]) * ws;
        }
    }
    if (sel_den > 0.0) for (double& x : mo.out) x /= sel_den;
    mo.mass = denom > 0.0 ? selected_mass_num / denom : 0.0;
    mo.value_reads = mo.selected;
    mo.score_reads = 2LL * N;
    for (int j = 0; j < DV; ++j) mo.checksum += mo.out[j] * (j + 1);
    return mo;
}

static MethodOutput streaming_recompute_histogram_mass(const Row& r) {
    MethodOutput mo; mo.out.assign(DV, 0.0); mo.materializes_scores = false; mo.materialization_free_streaming = true; mo.score_passes = 3;
    double max_s = -std::numeric_limits<double>::infinity();
    for (int i = 0; i < N; ++i) max_s = std::max(max_s, (double)dot_score(r.q.data(), &r.k[i * D]));
    std::vector<double> bins(HIST_BINS, 0.0);
    double denom = 0.0;
    for (int i = 0; i < N; ++i) {
        double s = dot_score(r.q.data(), &r.k[i * D]);
        double w = std::exp(s - max_s);
        denom += w;
        bins[bin_for_delta(max_s - s)] += w;
    }
    double threshold_delta = threshold_from_bins(bins, denom);
    double sel_max = -std::numeric_limits<double>::infinity();
    // First half of pass 3: find selected max and dense selected mass.
    double selected_mass_num = 0.0;
    std::vector<char> selected(N, 0);
    for (int i = 0; i < N; ++i) {
        double s = dot_score(r.q.data(), &r.k[i * D]);
        if (max_s - s <= threshold_delta) {
            selected[i] = 1; mo.selected++; sel_max = std::max(sel_max, s); selected_mass_num += std::exp(s - max_s);
        }
    }
    // The selected bitset is on-chip/control metadata for this CPU probe; no global score storage.
    // Accumulate selected values with scores recomputed in a final inner loop.  We charge this as part of pass 3 in qk_dots.
    // To avoid charging a fourth full pass, we do not recompute scores for unselected rows here; selected score recompute is charged explicitly.
    double sel_den = 0.0;
    long long extra_selected_score_recompute = 0;
    for (int i = 0; i < N; ++i) if (selected[i]) {
        double s = dot_score(r.q.data(), &r.k[i * D]);
        ++extra_selected_score_recompute;
        double ws = std::exp(s - sel_max);
        sel_den += ws;
        for (int j = 0; j < DV; ++j) mo.out[j] += double(r.v[i * DV + j]) * ws;
    }
    if (sel_den > 0.0) for (double& x : mo.out) x /= sel_den;
    mo.mass = denom > 0.0 ? selected_mass_num / denom : 0.0;
    mo.value_reads = mo.selected;
    mo.qk_dots = 3LL * N + extra_selected_score_recompute;
    mo.score_reads = 0; mo.score_writes = 0;
    for (int j = 0; j < DV; ++j) mo.checksum += mo.out[j] * (j + 1);
    return mo;
}

static MethodOutput streaming_exact_two_pass_dense(const Row& r) {
    // Dense reference implemented as two-pass streaming softmax.  This is a negative-control
    // schedule: it is materialization-free but recomputes QK once.  It should not be confused
    // with an optimized FlashAttention-like online kernel.
    MethodOutput mo; mo.out.assign(DV, 0.0); mo.selected = N; mo.mass = 1.0; mo.materializes_scores = false; mo.materialization_free_streaming = true; mo.score_passes = 2;
    double max_s = -std::numeric_limits<double>::infinity();
    for (int i = 0; i < N; ++i) max_s = std::max(max_s, (double)dot_score(r.q.data(), &r.k[i * D]));
    double denom = 0.0;
    for (int i = 0; i < N; ++i) {
        double s = dot_score(r.q.data(), &r.k[i * D]);
        double w = std::exp(s - max_s);
        denom += w;
        for (int j = 0; j < DV; ++j) mo.out[j] += double(r.v[i * DV + j]) * w;
    }
    if (denom > 0.0) for (double& x : mo.out) x /= denom;
    mo.qk_dots = 2LL * N; mo.value_reads = N;
    for (int j = 0; j < DV; ++j) mo.checksum += mo.out[j] * (j + 1);
    return mo;
}

using MethodFn = MethodOutput(*)(const Row&);

static Accum evaluate(const std::string& regime, const std::string& method, const std::vector<Row>& rows, MethodFn fn, const std::vector<std::vector<double>>& dense_refs, double dense_ns_per_row) {
    Accum a; a.regime = regime; a.method = method; a.rows = (int)rows.size(); a.dense_ns_per_row = dense_ns_per_row;
    volatile double guard = 0.0;
    auto t0 = Clock::now();
    std::vector<MethodOutput> first;
    first.reserve(rows.size());
    for (int rep = 0; rep < REPEATS; ++rep) {
        for (int r = 0; r < (int)rows.size(); ++r) {
            MethodOutput mo = fn(rows[r]);
            guard += mo.checksum * 1e-30;
            if (rep == 0) first.push_back(std::move(mo));
        }
    }
    auto t1 = Clock::now();
    a.ns_total = std::chrono::duration<double, std::nano>(t1 - t0).count();
    for (int r = 0; r < (int)rows.size(); ++r) {
        const auto& mo = first[r];
        std::vector<double> diff(DV);
        for (int j = 0; j < DV; ++j) diff[j] = mo.out[j] - dense_refs[r][j];
        double rel = norm2(diff) / std::max(1e-12, norm2(dense_refs[r]));
        double cos = cosine(mo.out, dense_refs[r]);
        bool ok = (mo.mass >= TARGET_MASS && rel <= 0.18 && cos >= 0.995);
        a.selected_sum += mo.selected;
        a.mass_sum += mo.mass;
        a.rel_l2_sum += rel;
        a.cosine_sum += cos;
        a.quality_sum += ok ? 1.0 : 0.0;
        a.qk_sum += (double)mo.qk_dots;
        a.value_sum += (double)mo.value_reads;
        a.score_writes_sum += (double)mo.score_writes;
        a.score_reads_sum += (double)mo.score_reads;
        a.score_passes = mo.score_passes;
        a.materializes_scores = mo.materializes_scores;
        a.materialization_free_streaming = mo.materialization_free_streaming;
    }
    (void)guard;
    return a;
}

static std::string fmt(double x) {
    if (std::isnan(x) || std::isinf(x)) return "null";
    std::ostringstream os; os << std::setprecision(10) << x; return os.str();
}

static void print_accum_json(const Accum& a, bool comma) {
    double rows = std::max(1, a.rows);
    double ns_per_row = a.ns_total / (rows * REPEATS);
    std::cout << "    {\n";
    std::cout << "      \"regime\": \"" << a.regime << "\",\n";
    std::cout << "      \"method\": \"" << a.method << "\",\n";
    std::cout << "      \"rows\": " << a.rows << ",\n";
    std::cout << "      \"repeats\": " << REPEATS << ",\n";
    std::cout << "      \"ns_per_row\": " << fmt(ns_per_row) << ",\n";
    std::cout << "      \"speedup_vs_dense_online\": " << fmt(a.dense_ns_per_row / std::max(1e-12, ns_per_row)) << ",\n";
    std::cout << "      \"mean_selected_values\": " << fmt(a.selected_sum / rows) << ",\n";
    std::cout << "      \"selected_fraction\": " << fmt((a.selected_sum / rows) / N) << ",\n";
    std::cout << "      \"mean_mass_retained\": " << fmt(a.mass_sum / rows) << ",\n";
    std::cout << "      \"mean_rel_l2\": " << fmt(a.rel_l2_sum / rows) << ",\n";
    std::cout << "      \"mean_output_cosine\": " << fmt(a.cosine_sum / rows) << ",\n";
    std::cout << "      \"quality_bar_rate\": " << fmt(a.quality_sum / rows) << ",\n";
    std::cout << "      \"mean_qk_dot_products\": " << fmt(a.qk_sum / rows) << ",\n";
    std::cout << "      \"qk_dot_fraction_vs_dense_online\": " << fmt((a.qk_sum / rows) / N) << ",\n";
    std::cout << "      \"mean_value_reads\": " << fmt(a.value_sum / rows) << ",\n";
    std::cout << "      \"mean_score_memory_writes\": " << fmt(a.score_writes_sum / rows) << ",\n";
    std::cout << "      \"mean_score_memory_reads\": " << fmt(a.score_reads_sum / rows) << ",\n";
    std::cout << "      \"score_passes\": " << a.score_passes << ",\n";
    std::cout << "      \"materializes_scores\": " << (a.materializes_scores ? "true" : "false") << ",\n";
    std::cout << "      \"materialization_free_streaming\": " << (a.materialization_free_streaming ? "true" : "false") << ",\n";
    std::cout << "      \"uses_values_for_selection\": false,\n";
    std::cout << "      \"uses_dense_output_for_selection\": false\n";
    std::cout << "    }" << (comma ? "," : "") << "\n";
}

int main() {
    std::vector<std::string> regimes = {"peaked_low_support", "medium_support", "broad_high_entropy", "value_tail_outlier"};
    std::vector<Accum> all;
    for (const std::string& regime : regimes) {
        std::mt19937 rng(20260618u + (unsigned)std::hash<std::string>{}(regime));
        std::vector<Row> rows;
        rows.reserve(ROWS_PER_REGIME);
        for (int i = 0; i < ROWS_PER_REGIME; ++i) rows.push_back(make_row(regime, rng, i));
        std::vector<std::vector<double>> dense_refs;
        dense_refs.reserve(rows.size());
        // Time dense online first.
        Accum dense_tmp; dense_tmp.regime = regime; dense_tmp.method = "dense_online_one_pass"; dense_tmp.rows = (int)rows.size(); dense_tmp.dense_ns_per_row = 1.0;
        volatile double guard = 0.0;
        auto t0 = Clock::now();
        std::vector<MethodOutput> dense_first;
        for (int rep = 0; rep < REPEATS; ++rep) {
            for (int r = 0; r < (int)rows.size(); ++r) {
                MethodOutput mo = dense_online(rows[r]);
                guard += mo.checksum * 1e-30;
                if (rep == 0) dense_first.push_back(std::move(mo));
            }
        }
        auto t1 = Clock::now();
        dense_tmp.ns_total = std::chrono::duration<double, std::nano>(t1 - t0).count();
        for (auto& mo : dense_first) {
            dense_refs.push_back(mo.out);
            dense_tmp.selected_sum += mo.selected; dense_tmp.mass_sum += mo.mass; dense_tmp.rel_l2_sum += 0.0; dense_tmp.cosine_sum += 1.0; dense_tmp.quality_sum += 1.0;
            dense_tmp.qk_sum += mo.qk_dots; dense_tmp.value_sum += mo.value_reads; dense_tmp.score_writes_sum += mo.score_writes; dense_tmp.score_reads_sum += mo.score_reads;
            dense_tmp.score_passes = mo.score_passes; dense_tmp.materializes_scores = mo.materializes_scores; dense_tmp.materialization_free_streaming = mo.materialization_free_streaming;
        }
        double dense_ns_per_row = dense_tmp.ns_total / (std::max(1, dense_tmp.rows) * REPEATS);
        dense_tmp.dense_ns_per_row = dense_ns_per_row;
        all.push_back(dense_tmp);
        all.push_back(evaluate(regime, "materialized_score_histogram_mass_0p95", rows, materialized_histogram_mass, dense_refs, dense_ns_per_row));
        all.push_back(evaluate(regime, "streaming_recompute_histogram_mass_0p95", rows, streaming_recompute_histogram_mass, dense_refs, dense_ns_per_row));
        all.push_back(evaluate(regime, "streaming_two_pass_dense_reference", rows, streaming_exact_two_pass_dense, dense_refs, dense_ns_per_row));
    }

    std::cout << "{\n";
    std::cout << "  \"project\": \"CloudtainerML\",\n";
    std::cout << "  \"native_probe\": \"fused_streaming_schedule\",\n";
    std::cout << "  \"generated_by\": \"experiments/fused_streaming_schedule/fused_streaming_schedule.cpp\",\n";
    std::cout << "  \"rows_per_regime\": " << ROWS_PER_REGIME << ",\n";
    std::cout << "  \"repeats\": " << REPEATS << ",\n";
    std::cout << "  \"n_ctx\": " << N << ",\n";
    std::cout << "  \"d_head\": " << D << ",\n";
    std::cout << "  \"d_value\": " << DV << ",\n";
    std::cout << "  \"target_mass\": " << TARGET_MASS << ",\n";
    std::cout << "  \"quality_bar\": {\"mass\": 0.95, \"cosine\": 0.995, \"rel_l2\": 0.18},\n";
    std::cout << "  \"rows\": [\n";
    for (size_t i = 0; i < all.size(); ++i) print_accum_json(all[i], i + 1 < all.size());
    std::cout << "  ]\n";
    std::cout << "}\n";
    return 0;
}
