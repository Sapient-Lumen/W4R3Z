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

struct Data {
    uint64_t rows{}, n{}, dv{};
    std::vector<double> scores;
    std::vector<double> values;
    std::vector<int32_t> regime;
};

static bool read_exact(std::ifstream& in, char* dst, size_t bytes) {
    in.read(dst, static_cast<std::streamsize>(bytes));
    return static_cast<size_t>(in.gcount()) == bytes;
}

template <class T>
static bool read_vec(std::ifstream& in, std::vector<T>& v) {
    if (v.empty()) return true;
    return read_exact(in, reinterpret_cast<char*>(v.data()), sizeof(T) * v.size());
}

static Data load_bin(const std::string& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("cannot open input bin");
    char magic[8];
    if (!read_exact(in, magic, 8)) throw std::runtime_error("bad header");
    std::string m(magic, magic + 8);
    if (m != "CTMLTR61") throw std::runtime_error("bad magic");
    Data d;
    if (!read_exact(in, reinterpret_cast<char*>(&d.rows), sizeof(uint64_t))) throw std::runtime_error("missing rows");
    if (!read_exact(in, reinterpret_cast<char*>(&d.n), sizeof(uint64_t))) throw std::runtime_error("missing n");
    if (!read_exact(in, reinterpret_cast<char*>(&d.dv), sizeof(uint64_t))) throw std::runtime_error("missing dv");
    d.scores.resize(d.rows * d.n);
    d.values.resize(d.rows * d.n * d.dv);
    d.regime.resize(d.rows);
    if (!read_vec(in, d.scores)) throw std::runtime_error("missing scores");
    if (!read_vec(in, d.values)) throw std::runtime_error("missing values");
    if (!read_vec(in, d.regime)) throw std::runtime_error("missing regime ids");
    return d;
}

struct RowHistResult {
    int selected_count{};
    double mass{};
    double rel_l2{};
    double cosine{};
    bool quality{};
    uint64_t score_reads{};
    uint64_t value_reads{};
    double checksum{};
};

static void dense_row(const Data& d, uint64_t r, std::vector<double>& out) {
    const uint64_t n = d.n, dv = d.dv;
    const double* s = d.scores.data() + r * n;
    const double* v = d.values.data() + r * n * dv;
    double mx = s[0];
    for (uint64_t i = 1; i < n; ++i) mx = std::max(mx, s[i]);
    std::vector<double> w(n);
    double z = 0.0;
    for (uint64_t i = 0; i < n; ++i) {
        double e = std::exp(std::max(-80.0, std::min(0.0, s[i] - mx)));
        w[i] = e;
        z += e;
    }
    std::fill(out.begin(), out.end(), 0.0);
    double inv = z > 0.0 ? 1.0 / z : 1.0 / static_cast<double>(n);
    for (uint64_t i = 0; i < n; ++i) {
        double p = w[i] * inv;
        const double* vi = v + i * dv;
        for (uint64_t j = 0; j < dv; ++j) out[j] += p * vi[j];
    }
}

static RowHistResult hist_row(const Data& d, uint64_t r, std::vector<double>& sparse_out, std::vector<double>* dense_ref=nullptr) {
    constexpr int bins = 32;
    constexpr double target_mass = 0.95;
    constexpr double max_delta = 16.0;
    const uint64_t n = d.n, dv = d.dv;
    const double* s = d.scores.data() + r * n;
    const double* v = d.values.data() + r * n * dv;
    double mx = s[0];
    for (uint64_t i = 1; i < n; ++i) mx = std::max(mx, s[i]);
    std::vector<double> weights(n);
    std::vector<int> bin_ids(n);
    double z = 0.0;
    const double width = max_delta / static_cast<double>(bins);
    std::vector<double> mass_by_bin(bins + 1, 0.0);
    for (uint64_t i = 0; i < n; ++i) {
        double rel = std::max(0.0, mx - s[i]);
        int bid = static_cast<int>(std::floor(rel / std::max(width, 1e-12)));
        bid = std::max(0, std::min(bins, bid));
        bin_ids[i] = bid;
        double e = std::exp(std::max(-80.0, std::min(0.0, s[i] - mx)));
        weights[i] = e;
        z += e;
        mass_by_bin[bid] += e;
    }
    int cutoff = bins;
    double cum = 0.0;
    if (z <= 0.0 || !std::isfinite(z)) {
        cutoff = bins;
    } else {
        for (int b = 0; b <= bins; ++b) {
            cum += mass_by_bin[b] / z;
            if (cum >= target_mass) { cutoff = b; break; }
        }
    }
    std::vector<uint8_t> keep(n, 0);
    int selected = 0;
    double selected_z = 0.0;
    double exact_mass = 0.0;
    for (uint64_t i = 0; i < n; ++i) {
        if (bin_ids[i] <= cutoff) {
            keep[i] = 1;
            selected++;
            selected_z += weights[i];
            exact_mass += weights[i] / z;
        }
    }
    std::fill(sparse_out.begin(), sparse_out.end(), 0.0);
    if (selected_z > 0.0) {
        for (uint64_t i = 0; i < n; ++i) if (keep[i]) {
            double p = weights[i] / selected_z;
            const double* vi = v + i * dv;
            for (uint64_t j = 0; j < dv; ++j) sparse_out[j] += p * vi[j];
        }
    }
    RowHistResult res;
    res.selected_count = selected;
    res.mass = exact_mass;
    res.score_reads = 2 * n;
    res.value_reads = selected;
    res.checksum = std::accumulate(sparse_out.begin(), sparse_out.end(), 0.0);
    if (dense_ref) {
        double dense_norm = 0.0, sparse_norm = 0.0, dot = 0.0, err = 0.0;
        for (uint64_t j = 0; j < dv; ++j) {
            double a = (*dense_ref)[j];
            double b = sparse_out[j];
            dense_norm += a * a;
            sparse_norm += b * b;
            dot += a * b;
            double diff = b - a;
            err += diff * diff;
        }
        dense_norm = std::sqrt(dense_norm);
        sparse_norm = std::sqrt(sparse_norm);
        err = std::sqrt(err);
        res.rel_l2 = err / std::max(1e-12, dense_norm);
        res.cosine = dot / std::max(1e-12, dense_norm * sparse_norm);
        if (res.cosine > 1.0) res.cosine = 1.0;
        if (res.cosine < -1.0) res.cosine = -1.0;
        res.quality = (res.mass >= 0.95 && res.cosine >= 0.995 && res.rel_l2 <= 0.18);
    }
    return res;
}

struct Timing { double ms; double checksum; };

static Timing time_dense(const Data& d, int repeats) {
    std::vector<double> out(d.dv, 0.0);
    volatile double guard = 0.0;
    auto t0 = std::chrono::steady_clock::now();
    for (int rep = 0; rep < repeats; ++rep) {
        for (uint64_t r = 0; r < d.rows; ++r) {
            dense_row(d, r, out);
            guard += out[(r + rep) % d.dv] * 1e-12;
        }
    }
    auto t1 = std::chrono::steady_clock::now();
    return {std::chrono::duration<double, std::milli>(t1 - t0).count(), static_cast<double>(guard)};
}

static Timing time_hist(const Data& d, int repeats) {
    std::vector<double> out(d.dv, 0.0);
    volatile double guard = 0.0;
    auto t0 = std::chrono::steady_clock::now();
    for (int rep = 0; rep < repeats; ++rep) {
        for (uint64_t r = 0; r < d.rows; ++r) {
            auto res = hist_row(d, r, out, nullptr);
            guard += (out[(r + rep) % d.dv] + 1e-9 * res.selected_count) * 1e-12;
        }
    }
    auto t1 = std::chrono::steady_clock::now();
    return {std::chrono::duration<double, std::milli>(t1 - t0).count(), static_cast<double>(guard)};
}

static std::string regime_name(int32_t id) {
    if (id == 0) return "low_support_lt12";
    if (id == 1) return "mid_support_12_28";
    if (id == 2) return "high_support_ge28";
    return "unknown";
}

static std::string json_escape(const std::string& s) {
    std::string out;
    for (char c: s) {
        if (c == '"') out += "\\\"";
        else if (c == '\\') out += "\\\\";
        else out += c;
    }
    return out;
}

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "usage: trace_packet_native_replay <input.bin> <repeats>\n";
        return 2;
    }
    try {
        Data d = load_bin(argv[1]);
        int repeats = std::max(1, std::stoi(argv[2]));
        // Warmup.
        (void)time_dense(d, 2);
        (void)time_hist(d, 2);
        auto dense = time_dense(d, repeats);
        auto hist = time_hist(d, repeats);

        std::vector<double> dense_out(d.dv, 0.0), sparse_out(d.dv, 0.0);
        struct Agg { int rows=0; double sel=0, mass=0, rel=0, cos=0, qual=0; };
        Agg all;
        Agg regs[3];
        int worst_row = -1;
        double worst_rel = -1.0;
        for (uint64_t r = 0; r < d.rows; ++r) {
            dense_row(d, r, dense_out);
            auto res = hist_row(d, r, sparse_out, &dense_out);
            auto add = [&](Agg& a) {
                a.rows++;
                a.sel += res.selected_count;
                a.mass += res.mass;
                a.rel += res.rel_l2;
                a.cos += res.cosine;
                a.qual += res.quality ? 1.0 : 0.0;
            };
            add(all);
            if (d.regime[r] >= 0 && d.regime[r] < 3) add(regs[d.regime[r]]);
            if (res.rel_l2 > worst_rel) { worst_rel = res.rel_l2; worst_row = static_cast<int>(r); }
        }
        const double per_row_dense_us = dense.ms * 1000.0 / (static_cast<double>(d.rows) * repeats);
        const double per_row_hist_us = hist.ms * 1000.0 / (static_cast<double>(d.rows) * repeats);
        const double speedup = dense.ms / std::max(1e-12, hist.ms);
        std::cout << std::setprecision(12);
        std::cout << "{\n";
        std::cout << "  \"native_binary\": \"trace_packet_native_replay\",\n";
        std::cout << "  \"rows\": " << d.rows << ",\n";
        std::cout << "  \"n_tokens\": " << d.n << ",\n";
        std::cout << "  \"d_value\": " << d.dv << ",\n";
        std::cout << "  \"repeats\": " << repeats << ",\n";
        std::cout << "  \"timing\": {\n";
        std::cout << "    \"dense_materialized_score_ms\": " << dense.ms << ",\n";
        std::cout << "    \"mass_histogram_materialized_score_ms\": " << hist.ms << ",\n";
        std::cout << "    \"dense_materialized_score_us_per_row\": " << per_row_dense_us << ",\n";
        std::cout << "    \"mass_histogram_materialized_score_us_per_row\": " << per_row_hist_us << ",\n";
        std::cout << "    \"mass_histogram_speedup_vs_dense_score_consumption\": " << speedup << "\n";
        std::cout << "  },\n";
        auto emit_agg = [&](const Agg& a) {
            double rows = std::max(1, a.rows);
            std::cout << "{\"rows\":" << a.rows
                      << ",\"mean_selected_count\":" << a.sel / rows
                      << ",\"mean_selected_fraction\":" << (a.sel / rows) / static_cast<double>(d.n)
                      << ",\"mean_mass_retained\":" << a.mass / rows
                      << ",\"mean_rel_l2\":" << a.rel / rows
                      << ",\"mean_cosine\":" << a.cos / rows
                      << ",\"quality_rate\":" << a.qual / rows << "}";
        };
        std::cout << "  \"all_rows\": "; emit_agg(all); std::cout << ",\n";
        std::cout << "  \"by_regime\": {\n";
        for (int i = 0; i < 3; ++i) {
            std::cout << "    \"" << regime_name(i) << "\": "; emit_agg(regs[i]);
            std::cout << (i == 2 ? "\n" : ",\n");
        }
        std::cout << "  },\n";
        std::cout << "  \"worst_row\": {\"row_id\":" << worst_row << ",\"rel_l2\":" << worst_rel << "},\n";
        std::cout << "  \"checksums\": {\"dense\":" << dense.checksum << ",\"hist\":" << hist.checksum << "}\n";
        std::cout << "}\n";
    } catch (const std::exception& e) {
        std::cerr << "error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
