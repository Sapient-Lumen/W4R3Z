#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

// rev0046 selector-only CPU timing probe.
// This measures selection kernels only, not attention matrix multiplication or
// GPU kernels. It is meant to replace vague Python timing with a named native
// CPU baseline while keeping the promotion blocker honest.

struct XorShift64 {
    uint64_t x;
    explicit XorShift64(uint64_t seed) : x(seed ? seed : 88172645463325252ull) {}
    uint64_t next_u64() {
        x ^= x << 7;
        x ^= x >> 9;
        return x;
    }
    double uniform() {
        return (next_u64() >> 11) * (1.0 / 9007199254740992.0);
    }
    double normal() {
        double u1 = std::max(1e-12, uniform());
        double u2 = uniform();
        return std::sqrt(-2.0 * std::log(u1)) * std::cos(6.283185307179586 * u2);
    }
};

struct Row {
    std::vector<double> scores;
    std::vector<double> norms;
};

static constexpr int N = 1024;
static constexpr int ROWS = 256;
static constexpr int REPEATS = 80;
static constexpr int K = 32;
static constexpr int BINS = 32;
static constexpr double TARGET_MASS = 0.95;
static constexpr double VALUE_BOUND = 0.15;
static constexpr int EXCEPTION_CAP = 64;

Row make_row(int regime, int row_id) {
    XorShift64 rng(0xC10DULL + 1009ull * regime + 9176ull * row_id);
    Row r;
    r.scores.assign(N, 0.0);
    r.norms.assign(N, 1.0);
    if (regime == 0) { // peaked bounded
        for (int i = 0; i < N; ++i) r.scores[i] = 0.08 * rng.normal();
        for (int j = 0; j < 48; ++j) {
            int idx = (j * 7919 + row_id * 17) % N;
            r.scores[idx] = 7.0 + 0.15 * rng.normal();
        }
    } else if (regime == 1) { // broad bounded
        for (int i = 0; i < N; ++i) r.scores[i] = 0.22 * rng.normal();
    } else { // peaked plus tail norm spikes
        for (int i = 0; i < N; ++i) r.scores[i] = 0.08 * rng.normal();
        for (int j = 0; j < 48; ++j) {
            int idx = (j * 7919 + row_id * 17) % N;
            r.scores[idx] = 7.0 + 0.15 * rng.normal();
        }
        for (int j = 0; j < 4; ++j) {
            int idx = (N - 1 - ((row_id * 13 + j * 37) % (N / 2)));
            r.scores[idx] = -0.2 - 0.05 * j;
            r.norms[idx] = 1700.0 + 120.0 * j;
        }
    }
    return r;
}

std::vector<double> softmax_probs(const std::vector<double>& scores) {
    double m = *std::max_element(scores.begin(), scores.end());
    std::vector<double> w(scores.size());
    double z = 0.0;
    for (size_t i = 0; i < scores.size(); ++i) {
        w[i] = std::exp(std::max(-80.0, std::min(0.0, scores[i] - m)));
        z += w[i];
    }
    for (double &v : w) v /= z;
    return w;
}

int exact_topk_count(const Row& r) {
    std::vector<int> idx(N);
    std::iota(idx.begin(), idx.end(), 0);
    std::nth_element(idx.begin(), idx.begin() + K, idx.end(), [&](int a, int b) { return r.scores[a] > r.scores[b]; });
    return K;
}

std::vector<char> histogram_mask(const Row& r, int& selected_count) {
    const auto& scores = r.scores;
    double max_score = *std::max_element(scores.begin(), scores.end());
    double width = 16.0 / BINS;
    std::vector<int> bin(N);
    std::vector<double> mass_by_bin(BINS + 1, 0.0);
    double z = 0.0;
    std::vector<double> weights(N);
    for (int i = 0; i < N; ++i) {
        double rel = std::max(0.0, max_score - scores[i]);
        int b = static_cast<int>(std::floor(rel / width));
        if (b < 0) b = 0;
        if (b > BINS) b = BINS;
        bin[i] = b;
        weights[i] = std::exp(std::max(-80.0, std::min(0.0, scores[i] - max_score)));
        z += weights[i];
    }
    for (int i = 0; i < N; ++i) mass_by_bin[bin[i]] += weights[i] / z;
    double cum = 0.0;
    int cutoff = BINS;
    for (int b = 0; b <= BINS; ++b) {
        cum += mass_by_bin[b];
        if (cum >= TARGET_MASS) { cutoff = b; break; }
    }
    std::vector<char> mask(N, 0);
    selected_count = 0;
    for (int i = 0; i < N; ++i) if (bin[i] <= cutoff) { mask[i] = 1; ++selected_count; }
    return mask;
}

double value_norm_bound(const Row& r, const std::vector<double>& probs, const std::vector<char>& mask) {
    double mass = 0.0, selected_weighted_norm = 0.0, omitted_weighted_norm = 0.0;
    for (int i = 0; i < N; ++i) {
        if (mask[i]) { mass += probs[i]; selected_weighted_norm += probs[i] * r.norms[i]; }
        else { omitted_weighted_norm += probs[i] * r.norms[i]; }
    }
    double selected_expected_norm = (mass > 0.0) ? selected_weighted_norm / mass : 0.0;
    return (1.0 - mass) * selected_expected_norm + omitted_weighted_norm;
}

int histogram_count(const Row& r) {
    int selected = 0;
    (void)histogram_mask(r, selected);
    return selected;
}

int value_norm_exception_count(const Row& r) {
    int selected = 0;
    std::vector<char> mask = histogram_mask(r, selected);
    std::vector<double> probs = softmax_probs(r.scores);
    double bound = value_norm_bound(r, probs, mask);
    std::vector<int> tail;
    tail.reserve(N);
    for (int i = 0; i < N; ++i) if (!mask[i]) tail.push_back(i);
    std::sort(tail.begin(), tail.end(), [&](int a, int b) { return probs[a] * r.norms[a] > probs[b] * r.norms[b]; });
    int exceptions = 0;
    for (int idx : tail) {
        if (bound <= VALUE_BOUND || exceptions >= EXCEPTION_CAP) break;
        mask[idx] = 1;
        ++selected;
        ++exceptions;
        bound = value_norm_bound(r, probs, mask);
    }
    return selected;
}

template <typename Fn>
double time_ns_per_row(const std::vector<Row>& rows, Fn fn, double& mean_selected) {
    volatile int sink = 0;
    int64_t total_selected = 0;
    auto start = std::chrono::steady_clock::now();
    for (int rep = 0; rep < REPEATS; ++rep) {
        for (const Row& r : rows) {
            int c = fn(r);
            sink += c;
            total_selected += c;
        }
    }
    auto stop = std::chrono::steady_clock::now();
    (void)sink;
    double ns = std::chrono::duration_cast<std::chrono::nanoseconds>(stop - start).count();
    mean_selected = static_cast<double>(total_selected) / (REPEATS * rows.size());
    return ns / (REPEATS * rows.size());
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: attention_selector_cpu_microbench <output.json>\n";
        return 2;
    }
    std::vector<std::string> regimes = {"peaked_bounded", "broad_bounded", "peaked_tail_norm_spikes"};
    std::ofstream out(argv[1]);
    out << std::fixed << std::setprecision(3);
    out << "{\n";
    out << "  \"project\": \"CloudtainerML\",\n";
    out << "  \"probe\": \"attention_selector_cpu_microbench\",\n";
    out << "  \"kind\": \"cpp_attention_selector_cpu_microbench\",\n";
    out << "  \"timing_scope\": \"selector_only_native_cpu_not_attention_kernel\",\n";
    out << "  \"N\": " << N << ", \"rows_per_regime\": " << ROWS << ", \"repeats\": " << REPEATS << ",\n";
    out << "  \"target_mass\": " << TARGET_MASS << ", \"value_norm_bound\": " << VALUE_BOUND << ",\n";
    out << "  \"rows\": [\n";
    bool first = true;
    for (int regime = 0; regime < 3; ++regime) {
        std::vector<Row> rows;
        rows.reserve(ROWS);
        for (int i = 0; i < ROWS; ++i) rows.push_back(make_row(regime, i));
        struct Method { std::string name; double ns; double selected; };
        std::vector<Method> methods;
        double sel = 0.0;
        double ns = time_ns_per_row(rows, exact_topk_count, sel);
        methods.push_back({"exact_topk_32_nth_element", ns, sel});
        ns = time_ns_per_row(rows, histogram_count, sel);
        methods.push_back({"mass_histogram_0p95_bins32", ns, sel});
        ns = time_ns_per_row(rows, value_norm_exception_count, sel);
        methods.push_back({"value_norm_exception_mass_0p95_bins32", ns, sel});
        for (const auto& m : methods) {
            if (!first) out << ",\n";
            first = false;
            out << "    {\"regime\": \"" << regimes[regime] << "\", \"method\": \"" << m.name
                << "\", \"mean_ns_per_row\": " << m.ns << ", \"mean_selected_count\": " << m.selected
                << ", \"selected_fraction\": " << (m.selected / N) << "}";
        }
    }
    out << "\n  ]\n";
    out << "}\n";
    return 0;
}
