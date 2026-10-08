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
    std::vector<double> probs;  // rows * n, dense softmax from QK, for value-only ceiling only
    std::vector<uint8_t> topp96_mask; // rows * n, exact Top-p 0.96 oracle mask, selected from full QK scores outside timed selector
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
    if (std::string(magic, magic + 8) != "CTMLTR63") throw std::runtime_error("bad magic");
    Data d;
    read_exact(f, &d.rows, 1); read_exact(f, &d.n, 1); read_exact(f, &d.dk, 1); read_exact(f, &d.dv, 1);
    if (d.rows == 0 || d.n == 0 || d.dk == 0 || d.dv == 0) throw std::runtime_error("zero shape");
    d.q.resize(d.rows * d.dk);
    d.k.resize(d.rows * d.n * d.dk);
    d.v.resize(d.rows * d.n * d.dv);
    d.probs.resize(d.rows * d.n);
    d.topp96_mask.resize(d.rows * d.n);
    d.regime.resize(d.rows);
    read_exact(f, d.q.data(), d.q.size());
    read_exact(f, d.k.data(), d.k.size());
    read_exact(f, d.v.data(), d.v.size());
    read_exact(f, d.probs.data(), d.probs.size());
    read_exact(f, d.topp96_mask.data(), d.topp96_mask.size());
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

static void metrics(const std::vector<double>& dense, const std::vector<double>& sparse, double& rel_l2, double& cosine) {
    double dn = 0.0, sn = 0.0, dot = 0.0, err = 0.0;
    for (size_t j = 0; j < dense.size(); ++j) {
        double a = dense[j], b = sparse[j];
        dn += a * a; sn += b * b; dot += a * b; double diff = b - a; err += diff * diff;
    }
    dn = std::sqrt(dn); sn = std::sqrt(sn); err = std::sqrt(err);
    rel_l2 = err / std::max(1e-12, dn);
    cosine = dot / std::max(1e-12, dn * sn);
    cosine = std::max(-1.0, std::min(1.0, cosine));
}

static RowResult dense_qk_online_row(const Data& d, uint64_t r, std::vector<double>& out) {
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
    RowResult res; res.selected_count = static_cast<int>(n); res.mass = 1.0; res.quality = true; res.checksum = std::accumulate(out.begin(), out.end(), 0.0); return res;
}

static RowResult qk_scores_only_row(const Data& d, uint64_t r, std::vector<double>& out) {
    double mx = -std::numeric_limits<double>::infinity();
    double guard = 0.0;
    for (uint64_t i = 0; i < d.n; ++i) { double s = qk_score(d, r, i); mx = std::max(mx, s); guard += s * 1e-9; }
    out[0] = mx * 1e-9 + guard;
    RowResult res; res.selected_count = static_cast<int>(d.n); res.mass = 1.0; res.quality = true; res.checksum = out[0]; return res;
}

static RowResult dense_value_only_row(const Data& d, uint64_t r, std::vector<double>& out) {
    const uint64_t n = d.n, dv = d.dv;
    const double* vals = d.v.data() + r * n * dv;
    const double* probs = d.probs.data() + r * n;
    std::fill(out.begin(), out.end(), 0.0);
    for (uint64_t i = 0; i < n; ++i) {
        double p = probs[i];
        const double* vi = vals + i * dv;
        for (uint64_t j = 0; j < dv; ++j) out[j] += p * vi[j];
    }
    RowResult res; res.selected_count = static_cast<int>(n); res.mass = 1.0; res.quality = true; res.checksum = std::accumulate(out.begin(), out.end(), 0.0); return res;
}

static RowResult oracle_topp96_value_only_row(const Data& d, uint64_t r, std::vector<double>& out, const std::vector<double>* dense_ref = nullptr) {
    const uint64_t n = d.n, dv = d.dv;
    const double* vals = d.v.data() + r * n * dv;
    const double* probs = d.probs.data() + r * n;
    const uint8_t* mask = d.topp96_mask.data() + r * n;
    double mass = 0.0; int selected = 0;
    for (uint64_t i = 0; i < n; ++i) if (mask[i]) { mass += probs[i]; selected++; }
    std::fill(out.begin(), out.end(), 0.0);
    for (uint64_t i = 0; i < n; ++i) if (mask[i]) {
        double p = probs[i] / std::max(1e-300, mass);
        const double* vi = vals + i * dv;
        for (uint64_t j = 0; j < dv; ++j) out[j] += p * vi[j];
    }
    RowResult res; res.selected_count = selected; res.mass = mass; res.checksum = std::accumulate(out.begin(), out.end(), 0.0);
    if (dense_ref) { metrics(*dense_ref, out, res.rel_l2, res.cosine); res.quality = (res.mass >= 0.95 && res.cosine >= 0.995 && res.rel_l2 <= 0.18); }
    return res;
}

static RowResult oracle_topp96_qk_included_row(const Data& d, uint64_t r, std::vector<double>& out, const std::vector<double>* dense_ref = nullptr) {
    // Unrealistic upper bound: exact Top-p mask is supplied as an oracle side input.
    // This still computes every QK score and every softmax weight, but pays zero selector/search cost.
    const uint64_t n = d.n, dv = d.dv;
    const uint8_t* mask = d.topp96_mask.data() + r * n;
    std::vector<double> scores(n);
    double mx = -std::numeric_limits<double>::infinity();
    for (uint64_t i = 0; i < n; ++i) { scores[i] = qk_score(d, r, i); mx = std::max(mx, scores[i]); }
    double z = 0.0;
    for (uint64_t i = 0; i < n; ++i) { scores[i] = std::exp(std::max(-80.0, std::min(0.0, scores[i] - mx))); z += scores[i]; }
    double selected_z = 0.0, mass = 0.0; int selected = 0;
    for (uint64_t i = 0; i < n; ++i) if (mask[i]) { selected_z += scores[i]; mass += scores[i] / z; selected++; }
    std::fill(out.begin(), out.end(), 0.0);
    const double* vals = d.v.data() + r * n * dv;
    for (uint64_t i = 0; i < n; ++i) if (mask[i]) {
        double p = scores[i] / std::max(1e-300, selected_z);
        const double* vi = vals + i * dv;
        for (uint64_t j = 0; j < dv; ++j) out[j] += p * vi[j];
    }
    RowResult res; res.selected_count = selected; res.mass = mass; res.checksum = std::accumulate(out.begin(), out.end(), 0.0);
    if (dense_ref) { metrics(*dense_ref, out, res.rel_l2, res.cosine); res.quality = (res.mass >= 0.95 && res.cosine >= 0.995 && res.rel_l2 <= 0.18); }
    return res;
}

struct Timing { double ms; double checksum; };

template <typename Fn>
static Timing time_path(const Data& d, int repeats, Fn fn) {
    std::vector<double> out(std::max<uint64_t>(1, d.dv), 0.0);
    volatile double guard = 0.0;
    auto t0 = std::chrono::steady_clock::now();
    for (int rep = 0; rep < repeats; ++rep) {
        for (uint64_t r = 0; r < d.rows; ++r) {
            auto res = fn(d, r, out);
            guard += (out[(r + rep) % out.size()] + 1e-9 * res.selected_count + res.mass * 1e-12) * 1e-12;
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
    if (argc < 3) { std::cerr << "usage: trace_packet_speed_envelope <input.bin> <repeats>\n"; return 2; }
    try {
        Data d = load_bin(argv[1]);
        int repeats = std::max(1, std::stoi(argv[2]));
        // Warm-up all paths.
        (void)time_path(d, 4, [](const Data& d, uint64_t r, std::vector<double>& out){ return dense_qk_online_row(d, r, out); });
        (void)time_path(d, 4, [](const Data& d, uint64_t r, std::vector<double>& out){ return qk_scores_only_row(d, r, out); });
        (void)time_path(d, 4, [](const Data& d, uint64_t r, std::vector<double>& out){ return dense_value_only_row(d, r, out); });
        (void)time_path(d, 4, [](const Data& d, uint64_t r, std::vector<double>& out){ return oracle_topp96_value_only_row(d, r, out, nullptr); });
        (void)time_path(d, 4, [](const Data& d, uint64_t r, std::vector<double>& out){ return oracle_topp96_qk_included_row(d, r, out, nullptr); });

        auto dense = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return dense_qk_online_row(d, r, out); });
        auto qkonly = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return qk_scores_only_row(d, r, out); });
        auto dense_v = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return dense_value_only_row(d, r, out); });
        auto oracle_v = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return oracle_topp96_value_only_row(d, r, out, nullptr); });
        auto oracle_qk = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return oracle_topp96_qk_included_row(d, r, out, nullptr); });

        std::vector<double> dense_out(d.dv, 0.0), sparse_out(d.dv, 0.0);
        struct Agg { int rows=0; double sel=0, mass=0, rel=0, cos=0, qual=0; };
        Agg all, regs[3];
        double worst_rel = -1.0; int worst_row = -1;
        for (uint64_t r = 0; r < d.rows; ++r) {
            dense_qk_online_row(d, r, dense_out);
            auto res = oracle_topp96_value_only_row(d, r, sparse_out, &dense_out);
            auto add = [&](Agg& a, const RowResult& x) { a.rows++; a.sel += x.selected_count; a.mass += x.mass; a.rel += x.rel_l2; a.cos += x.cosine; a.qual += x.quality ? 1.0 : 0.0; };
            add(all, res);
            if (d.regime[r] >= 0 && d.regime[r] < 3) add(regs[d.regime[r]], res);
            if (res.rel_l2 > worst_rel) { worst_rel = res.rel_l2; worst_row = static_cast<int>(r); }
        }
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
        std::cout << "  \"native_binary\": \"trace_packet_speed_envelope\",\n";
        std::cout << "  \"rows\": " << d.rows << ",\n";
        std::cout << "  \"n_tokens\": " << d.n << ",\n";
        std::cout << "  \"d_key\": " << d.dk << ",\n";
        std::cout << "  \"d_value\": " << d.dv << ",\n";
        std::cout << "  \"repeats\": " << repeats << ",\n";
        std::cout << "  \"timing\": {\n";
        std::cout << "    \"dense_qk_online_ms\": " << dense.ms << ",\n";
        std::cout << "    \"qk_scores_only_ms\": " << qkonly.ms << ",\n";
        std::cout << "    \"dense_value_only_ms\": " << dense_v.ms << ",\n";
        std::cout << "    \"oracle_topp96_value_only_ms\": " << oracle_v.ms << ",\n";
        std::cout << "    \"oracle_topp96_qk_included_ms\": " << oracle_qk.ms << ",\n";
        std::cout << "    \"dense_qk_online_us_per_row\": " << dense.ms * 1000.0 / (static_cast<double>(d.rows) * repeats) << ",\n";
        std::cout << "    \"oracle_topp96_qk_included_us_per_row\": " << oracle_qk.ms * 1000.0 / (static_cast<double>(d.rows) * repeats) << ",\n";
        std::cout << "    \"oracle_topp96_qk_included_speedup_vs_dense\": " << dense.ms / std::max(1e-12, oracle_qk.ms) << ",\n";
        std::cout << "    \"oracle_topp96_value_only_speedup_vs_dense_value_only\": " << dense_v.ms / std::max(1e-12, oracle_v.ms) << ",\n";
        std::cout << "    \"qk_scores_only_fraction_of_dense_online_time\": " << qkonly.ms / std::max(1e-12, dense.ms) << "\n";
        std::cout << "  },\n";
        std::cout << "  \"accounting\": {\"qk_dot_fraction_dense\":1.0,\"qk_dot_fraction_oracle_topp96_qk_included\":1.0,\"selector_cost_oracle_topp96_qk_included\":0.0,\"oracle_mask_supplied\":true,\"oracle_mask_is_promotional\":false,\"score_storage_required_for_oracle_qk_included\":true},\n";
        std::cout << "  \"all_rows\": "; emit_agg(all); std::cout << ",\n";
        std::cout << "  \"by_regime\": {\n";
        for (int i = 0; i < 3; ++i) { std::cout << "    \"" << regime_name(i) << "\": "; emit_agg(regs[i]); std::cout << (i == 2 ? "\n" : ",\n"); }
        std::cout << "  },\n";
        std::cout << "  \"worst_row\": {\"row_id\":" << worst_row << ",\"rel_l2\":" << worst_rel << "},\n";
        std::cout << "  \"checksums\": {\"dense\":" << dense.checksum << ",\"qkonly\":" << qkonly.checksum << ",\"dense_value_only\":" << dense_v.checksum << ",\"oracle_value_only\":" << oracle_v.checksum << ",\"oracle_qk_included\":" << oracle_qk.checksum << "}\n";
        std::cout << "}\n";
    } catch (const std::exception& e) { std::cerr << "error: " << e.what() << "\n"; return 1; }
    return 0;
}
