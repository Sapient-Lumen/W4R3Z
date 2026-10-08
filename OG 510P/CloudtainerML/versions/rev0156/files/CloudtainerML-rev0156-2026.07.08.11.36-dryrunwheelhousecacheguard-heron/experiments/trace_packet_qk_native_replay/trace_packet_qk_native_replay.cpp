#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

struct Data {
    uint64_t rows = 0, n = 0, dk = 0, dv = 0;
    std::vector<double> q;      // rows * dk
    std::vector<double> k;      // rows * n * dk
    std::vector<double> v;      // rows * n * dv
    std::vector<int32_t> regime;
};

template <typename T>
static void read_exact(std::ifstream& f, T* ptr, size_t count) {
    f.read(reinterpret_cast<char*>(ptr), static_cast<std::streamsize>(sizeof(T) * count));
    if (!f) throw std::runtime_error("short read");
}

static Data load_bin(const std::string& path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) throw std::runtime_error("cannot open input");
    char magic[8];
    f.read(magic, 8);
    if (std::string(magic, magic + 8) != "CTMLTR62") throw std::runtime_error("bad magic");
    Data d;
    read_exact(f, &d.rows, 1); read_exact(f, &d.n, 1); read_exact(f, &d.dk, 1); read_exact(f, &d.dv, 1);
    if (d.rows == 0 || d.n == 0 || d.dk == 0 || d.dv == 0) throw std::runtime_error("zero shape");
    d.q.resize(d.rows * d.dk);
    d.k.resize(d.rows * d.n * d.dk);
    d.v.resize(d.rows * d.n * d.dv);
    d.regime.resize(d.rows);
    read_exact(f, d.q.data(), d.q.size());
    read_exact(f, d.k.data(), d.k.size());
    read_exact(f, d.v.data(), d.v.size());
    read_exact(f, d.regime.data(), d.regime.size());
    return d;
}

static inline double qk_score(const Data& d, uint64_t r, uint64_t i) {
    const double* q = d.q.data() + r * d.dk;
    const double* k = d.k.data() + (r * d.n + i) * d.dk;
    double acc = 0.0;
    for (uint64_t j = 0; j < d.dk; ++j) acc += q[j] * k[j];
    return acc / std::sqrt(static_cast<double>(d.dk));
}

struct RowResult {
    int selected_count = 0;
    double mass = 0.0;
    double rel_l2 = 0.0;
    double cosine = 0.0;
    bool quality = false;
    double checksum = 0.0;
};

static double output_metrics(const std::vector<double>& dense, const std::vector<double>& sparse, double& rel_l2, double& cosine) {
    double dn = 0.0, sn = 0.0, dot = 0.0, err = 0.0;
    for (size_t j = 0; j < dense.size(); ++j) {
        double a = dense[j], b = sparse[j];
        dn += a * a; sn += b * b; dot += a * b; double diff = b - a; err += diff * diff;
    }
    dn = std::sqrt(dn); sn = std::sqrt(sn); err = std::sqrt(err);
    rel_l2 = err / std::max(1e-12, dn);
    cosine = dot / std::max(1e-12, dn * sn);
    if (cosine > 1.0) cosine = 1.0;
    if (cosine < -1.0) cosine = -1.0;
    return std::accumulate(sparse.begin(), sparse.end(), 0.0);
}

static RowResult dense_qk_row(const Data& d, uint64_t r, std::vector<double>& out, std::vector<double>* scores_out = nullptr) {
    const uint64_t n = d.n, dv = d.dv;
    std::vector<double> scores(n);
    double mx = -std::numeric_limits<double>::infinity();
    for (uint64_t i = 0; i < n; ++i) { scores[i] = qk_score(d, r, i); mx = std::max(mx, scores[i]); }
    double z = 0.0;
    for (uint64_t i = 0; i < n; ++i) { scores[i] = std::exp(std::max(-80.0, std::min(0.0, scores[i] - mx))); z += scores[i]; }
    std::fill(out.begin(), out.end(), 0.0);
    const double* vals = d.v.data() + r * n * dv;
    for (uint64_t i = 0; i < n; ++i) {
        double p = scores[i] / z;
        const double* vi = vals + i * dv;
        for (uint64_t j = 0; j < dv; ++j) out[j] += p * vi[j];
    }
    if (scores_out) *scores_out = scores;
    RowResult res; res.selected_count = static_cast<int>(n); res.mass = 1.0; res.quality = true; res.checksum = std::accumulate(out.begin(), out.end(), 0.0); return res;
}

static RowResult materialized_hist_qk_row(const Data& d, uint64_t r, std::vector<double>& out, std::vector<double>* dense_ref = nullptr) {
    constexpr int bins = 32;
    constexpr double target_mass = 0.95;
    constexpr double max_delta = 16.0;
    const uint64_t n = d.n, dv = d.dv;
    std::vector<double> scores(n);
    double mx = -std::numeric_limits<double>::infinity();
    for (uint64_t i = 0; i < n; ++i) { scores[i] = qk_score(d, r, i); mx = std::max(mx, scores[i]); }
    const double width = max_delta / static_cast<double>(bins);
    std::vector<double> weights(n);
    std::vector<int> bin_ids(n);
    std::vector<double> mass_by_bin(bins + 1, 0.0);
    double z = 0.0;
    for (uint64_t i = 0; i < n; ++i) {
        double rel = std::max(0.0, mx - scores[i]);
        int bid = static_cast<int>(std::floor(rel / std::max(width, 1e-12)));
        bid = std::max(0, std::min(bins, bid));
        bin_ids[i] = bid;
        double e = std::exp(std::max(-80.0, std::min(0.0, scores[i] - mx)));
        weights[i] = e; z += e; mass_by_bin[bid] += e;
    }
    int cutoff = bins; double cum = 0.0;
    for (int b = 0; b <= bins; ++b) { cum += mass_by_bin[b] / z; if (cum >= target_mass) { cutoff = b; break; } }
    std::fill(out.begin(), out.end(), 0.0);
    double sel_z = 0.0, exact_mass = 0.0; int selected = 0;
    for (uint64_t i = 0; i < n; ++i) if (bin_ids[i] <= cutoff) { selected++; sel_z += weights[i]; exact_mass += weights[i] / z; }
    const double* vals = d.v.data() + r * n * dv;
    if (sel_z > 0.0) {
        for (uint64_t i = 0; i < n; ++i) if (bin_ids[i] <= cutoff) {
            double p = weights[i] / sel_z;
            const double* vi = vals + i * dv;
            for (uint64_t j = 0; j < dv; ++j) out[j] += p * vi[j];
        }
    }
    RowResult res; res.selected_count = selected; res.mass = exact_mass; res.checksum = std::accumulate(out.begin(), out.end(), 0.0);
    if (dense_ref) { output_metrics(*dense_ref, out, res.rel_l2, res.cosine); res.quality = (res.mass >= 0.95 && res.cosine >= 0.995 && res.rel_l2 <= 0.18); }
    return res;
}

static RowResult streaming_recompute_hist_row(const Data& d, uint64_t r, std::vector<double>& out, std::vector<double>* dense_ref = nullptr) {
    constexpr int bins = 32;
    constexpr double target_mass = 0.95;
    constexpr double max_delta = 16.0;
    const uint64_t n = d.n, dv = d.dv;
    double mx = -std::numeric_limits<double>::infinity();
    for (uint64_t i = 0; i < n; ++i) mx = std::max(mx, qk_score(d, r, i));
    const double width = max_delta / static_cast<double>(bins);
    std::vector<double> mass_by_bin(bins + 1, 0.0);
    double z = 0.0;
    for (uint64_t i = 0; i < n; ++i) {
        double sc = qk_score(d, r, i);
        double rel = std::max(0.0, mx - sc);
        int bid = static_cast<int>(std::floor(rel / std::max(width, 1e-12)));
        bid = std::max(0, std::min(bins, bid));
        double e = std::exp(std::max(-80.0, std::min(0.0, sc - mx)));
        z += e; mass_by_bin[bid] += e;
    }
    int cutoff = bins; double cum = 0.0;
    for (int b = 0; b <= bins; ++b) { cum += mass_by_bin[b] / z; if (cum >= target_mass) { cutoff = b; break; } }
    std::fill(out.begin(), out.end(), 0.0);
    double sel_z = 0.0, exact_mass = 0.0; int selected = 0;
    const double* vals = d.v.data() + r * n * dv;
    // First recompute selected denominator.
    for (uint64_t i = 0; i < n; ++i) {
        double sc = qk_score(d, r, i);
        double rel = std::max(0.0, mx - sc);
        int bid = static_cast<int>(std::floor(rel / std::max(width, 1e-12)));
        bid = std::max(0, std::min(bins, bid));
        if (bid <= cutoff) {
            double e = std::exp(std::max(-80.0, std::min(0.0, sc - mx)));
            selected++; sel_z += e; exact_mass += e / z;
        }
    }
    // Fourth pass computes selected values using the sparse normalizer.
    for (uint64_t i = 0; i < n; ++i) {
        double sc = qk_score(d, r, i);
        double rel = std::max(0.0, mx - sc);
        int bid = static_cast<int>(std::floor(rel / std::max(width, 1e-12)));
        bid = std::max(0, std::min(bins, bid));
        if (bid <= cutoff) {
            double e = std::exp(std::max(-80.0, std::min(0.0, sc - mx)));
            double p = e / std::max(1e-300, sel_z);
            const double* vi = vals + i * dv;
            for (uint64_t j = 0; j < dv; ++j) out[j] += p * vi[j];
        }
    }
    RowResult res; res.selected_count = selected; res.mass = exact_mass; res.checksum = std::accumulate(out.begin(), out.end(), 0.0);
    if (dense_ref) { output_metrics(*dense_ref, out, res.rel_l2, res.cosine); res.quality = (res.mass >= 0.95 && res.cosine >= 0.995 && res.rel_l2 <= 0.18); }
    return res;
}

struct Timing { double ms; double checksum; };

template <typename Fn>
static Timing time_path(const Data& d, int repeats, Fn fn) {
    std::vector<double> out(d.dv, 0.0);
    volatile double guard = 0.0;
    auto t0 = std::chrono::steady_clock::now();
    for (int rep = 0; rep < repeats; ++rep) {
        for (uint64_t r = 0; r < d.rows; ++r) {
            auto res = fn(d, r, out);
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

int main(int argc, char** argv) {
    if (argc < 3) { std::cerr << "usage: trace_packet_qk_native_replay <input.bin> <repeats>\n"; return 2; }
    try {
        Data d = load_bin(argv[1]);
        int repeats = std::max(1, std::stoi(argv[2]));
        (void)time_path(d, 2, [](const Data& d, uint64_t r, std::vector<double>& out){ return dense_qk_row(d, r, out, nullptr); });
        (void)time_path(d, 2, [](const Data& d, uint64_t r, std::vector<double>& out){ return materialized_hist_qk_row(d, r, out, nullptr); });
        (void)time_path(d, 1, [](const Data& d, uint64_t r, std::vector<double>& out){ return streaming_recompute_hist_row(d, r, out, nullptr); });
        auto dense = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return dense_qk_row(d, r, out, nullptr); });
        auto mat = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return materialized_hist_qk_row(d, r, out, nullptr); });
        auto stream = time_path(d, std::max(1, repeats / 3), [](const Data& d, uint64_t r, std::vector<double>& out){ return streaming_recompute_hist_row(d, r, out, nullptr); });
        std::vector<double> dense_out(d.dv, 0.0), sparse_out(d.dv, 0.0), stream_out(d.dv, 0.0);
        struct Agg { int rows=0; double sel=0, mass=0, rel=0, cos=0, qual=0; };
        Agg all, regs[3], stream_all;
        int worst_row = -1; double worst_rel = -1.0;
        for (uint64_t r = 0; r < d.rows; ++r) {
            dense_qk_row(d, r, dense_out, nullptr);
            auto res = materialized_hist_qk_row(d, r, sparse_out, &dense_out);
            auto sres = streaming_recompute_hist_row(d, r, stream_out, &dense_out);
            auto add = [&](Agg& a, const RowResult& x) { a.rows++; a.sel += x.selected_count; a.mass += x.mass; a.rel += x.rel_l2; a.cos += x.cosine; a.qual += x.quality ? 1.0 : 0.0; };
            add(all, res); add(stream_all, sres);
            if (d.regime[r] >= 0 && d.regime[r] < 3) add(regs[d.regime[r]], res);
            if (res.rel_l2 > worst_rel) { worst_rel = res.rel_l2; worst_row = static_cast<int>(r); }
        }
        double mat_speed = dense.ms / std::max(1e-12, mat.ms);
        double stream_scaled_ms = stream.ms * (static_cast<double>(repeats) / static_cast<double>(std::max(1, repeats / 3)));
        double stream_speed = dense.ms / std::max(1e-12, stream_scaled_ms);
        std::cout << std::setprecision(12);
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
        std::cout << "{\n";
        std::cout << "  \"native_binary\": \"trace_packet_qk_native_replay\",\n";
        std::cout << "  \"rows\": " << d.rows << ",\n";
        std::cout << "  \"n_tokens\": " << d.n << ",\n";
        std::cout << "  \"d_key\": " << d.dk << ",\n";
        std::cout << "  \"d_value\": " << d.dv << ",\n";
        std::cout << "  \"repeats\": " << repeats << ",\n";
        std::cout << "  \"timing\": {\n";
        std::cout << "    \"dense_qk_online_ms\": " << dense.ms << ",\n";
        std::cout << "    \"mass_histogram_materialized_qk_ms\": " << mat.ms << ",\n";
        std::cout << "    \"streaming_recompute_histogram_scaled_ms\": " << stream_scaled_ms << ",\n";
        std::cout << "    \"dense_qk_online_us_per_row\": " << dense.ms * 1000.0 / (static_cast<double>(d.rows) * repeats) << ",\n";
        std::cout << "    \"mass_histogram_materialized_qk_us_per_row\": " << mat.ms * 1000.0 / (static_cast<double>(d.rows) * repeats) << ",\n";
        std::cout << "    \"streaming_recompute_histogram_us_per_row\": " << stream_scaled_ms * 1000.0 / (static_cast<double>(d.rows) * repeats) << ",\n";
        std::cout << "    \"mass_histogram_speedup_vs_dense_qk_online\": " << mat_speed << ",\n";
        std::cout << "    \"streaming_recompute_speedup_vs_dense_qk_online\": " << stream_speed << "\n";
        std::cout << "  },\n";
        std::cout << "  \"qk_accounting\": {\"dense_qk_dot_fraction\":1.0,\"materialized_histogram_qk_dot_fraction\":1.0,\"streaming_recompute_histogram_qk_dot_fraction\":4.0,\"materialized_score_storage_required\":true,\"streaming_score_storage_required\":false},\n";
        std::cout << "  \"all_rows\": "; emit_agg(all); std::cout << ",\n";
        std::cout << "  \"streaming_all_rows\": "; emit_agg(stream_all); std::cout << ",\n";
        std::cout << "  \"by_regime\": {\n";
        for (int i = 0; i < 3; ++i) { std::cout << "    \"" << regime_name(i) << "\": "; emit_agg(regs[i]); std::cout << (i == 2 ? "\n" : ",\n"); }
        std::cout << "  },\n";
        std::cout << "  \"worst_row\": {\"row_id\":" << worst_row << ",\"rel_l2\":" << worst_rel << "},\n";
        std::cout << "  \"checksums\": {\"dense\":" << dense.checksum << ",\"materialized_histogram\":" << mat.checksum << ",\"streaming_histogram\":" << stream.checksum << "}\n";
        std::cout << "}\n";
    } catch (const std::exception& e) { std::cerr << "error: " << e.what() << "\n"; return 1; }
    return 0;
}
