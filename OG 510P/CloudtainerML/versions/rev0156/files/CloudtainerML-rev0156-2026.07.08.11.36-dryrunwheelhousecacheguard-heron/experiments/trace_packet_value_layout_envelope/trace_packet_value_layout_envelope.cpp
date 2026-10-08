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
    uint64_t rows = 0, n = 0, dk = 0, dv = 0, total_selected = 0;
    std::vector<double> q;      // rows * dk
    std::vector<double> k;      // rows * n * dk
    std::vector<double> v;      // rows * n * dv
    std::vector<double> probs;  // rows * n, dense softmax from QK
    std::vector<uint8_t> mask;  // rows * n, exact Top-p oracle support
    std::vector<uint64_t> offsets; // rows + 1
    std::vector<uint32_t> rank_indices;   // total_selected, probability-rank order
    std::vector<uint32_t> sorted_indices; // total_selected, key-cache index order
    std::vector<double> packed_probs;     // total_selected, sorted order
    std::vector<double> packed_values;    // total_selected * dv, sorted order
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
    if (std::string(magic, magic + 8) != "CTMLTR64") throw std::runtime_error("bad magic");
    Data d;
    read_exact(f, &d.rows, 1); read_exact(f, &d.n, 1); read_exact(f, &d.dk, 1); read_exact(f, &d.dv, 1); read_exact(f, &d.total_selected, 1);
    if (d.rows == 0 || d.n == 0 || d.dk == 0 || d.dv == 0) throw std::runtime_error("zero shape");
    d.q.resize(d.rows * d.dk);
    d.k.resize(d.rows * d.n * d.dk);
    d.v.resize(d.rows * d.n * d.dv);
    d.probs.resize(d.rows * d.n);
    d.mask.resize(d.rows * d.n);
    d.offsets.resize(d.rows + 1);
    d.rank_indices.resize(d.total_selected);
    d.sorted_indices.resize(d.total_selected);
    d.packed_probs.resize(d.total_selected);
    d.packed_values.resize(d.total_selected * d.dv);
    d.regime.resize(d.rows);
    read_exact(f, d.q.data(), d.q.size());
    read_exact(f, d.k.data(), d.k.size());
    read_exact(f, d.v.data(), d.v.size());
    read_exact(f, d.probs.data(), d.probs.size());
    read_exact(f, d.mask.data(), d.mask.size());
    read_exact(f, d.offsets.data(), d.offsets.size());
    read_exact(f, d.rank_indices.data(), d.rank_indices.size());
    read_exact(f, d.sorted_indices.data(), d.sorted_indices.size());
    read_exact(f, d.packed_probs.data(), d.packed_probs.size());
    read_exact(f, d.packed_values.data(), d.packed_values.size());
    read_exact(f, d.regime.data(), d.regime.size());
    if (d.offsets.front() != 0 || d.offsets.back() != d.total_selected) throw std::runtime_error("bad offsets");
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

static inline void finalize_quality(const std::vector<double>* dense_ref, std::vector<double>& out, RowResult& res) {
    res.checksum = std::accumulate(out.begin(), out.end(), 0.0);
    if (dense_ref) { metrics(*dense_ref, out, res.rel_l2, res.cosine); res.quality = (res.mass >= 0.95 && res.cosine >= 0.995 && res.rel_l2 <= 0.18); }
}

static RowResult mask_scan_sparse_value_only_row(const Data& d, uint64_t r, std::vector<double>& out, const std::vector<double>* dense_ref = nullptr) {
    const uint64_t n = d.n, dv = d.dv;
    const double* vals = d.v.data() + r * n * dv;
    const double* probs = d.probs.data() + r * n;
    const uint8_t* mask = d.mask.data() + r * n;
    double mass = 0.0; int selected = 0;
    for (uint64_t i = 0; i < n; ++i) if (mask[i]) { mass += probs[i]; selected++; }
    std::fill(out.begin(), out.end(), 0.0);
    for (uint64_t i = 0; i < n; ++i) if (mask[i]) {
        double p = probs[i] / std::max(1e-300, mass);
        const double* vi = vals + i * dv;
        for (uint64_t j = 0; j < dv; ++j) out[j] += p * vi[j];
    }
    RowResult res; res.selected_count = selected; res.mass = mass; finalize_quality(dense_ref, out, res); return res;
}

static RowResult index_sparse_value_only_row(const Data& d, uint64_t r, std::vector<double>& out, bool sorted, const std::vector<double>* dense_ref = nullptr) {
    const uint64_t n = d.n, dv = d.dv;
    const double* vals = d.v.data() + r * n * dv;
    const double* probs = d.probs.data() + r * n;
    uint64_t begin = d.offsets[r], end = d.offsets[r+1];
    const uint32_t* idxs = (sorted ? d.sorted_indices.data() : d.rank_indices.data()) + begin;
    double mass = 0.0; int selected = static_cast<int>(end - begin);
    for (uint64_t p = 0; p < end - begin; ++p) mass += probs[idxs[p]];
    std::fill(out.begin(), out.end(), 0.0);
    for (uint64_t p = 0; p < end - begin; ++p) {
        uint32_t i = idxs[p];
        double w = probs[i] / std::max(1e-300, mass);
        const double* vi = vals + static_cast<uint64_t>(i) * dv;
        for (uint64_t j = 0; j < dv; ++j) out[j] += w * vi[j];
    }
    RowResult res; res.selected_count = selected; res.mass = mass; finalize_quality(dense_ref, out, res); return res;
}

static RowResult packed_sparse_value_only_row(const Data& d, uint64_t r, std::vector<double>& out, const std::vector<double>* dense_ref = nullptr) {
    const uint64_t dv = d.dv;
    uint64_t begin = d.offsets[r], end = d.offsets[r+1];
    double mass = 0.0; int selected = static_cast<int>(end - begin);
    for (uint64_t p = begin; p < end; ++p) mass += d.packed_probs[p];
    std::fill(out.begin(), out.end(), 0.0);
    for (uint64_t p = begin; p < end; ++p) {
        double w = d.packed_probs[p] / std::max(1e-300, mass);
        const double* vi = d.packed_values.data() + p * dv;
        for (uint64_t j = 0; j < dv; ++j) out[j] += w * vi[j];
    }
    RowResult res; res.selected_count = selected; res.mass = mass; finalize_quality(dense_ref, out, res); return res;
}

static RowResult oracle_qk_included_index_sorted_row(const Data& d, uint64_t r, std::vector<double>& out, const std::vector<double>* dense_ref = nullptr) {
    const uint64_t n = d.n, dv = d.dv;
    uint64_t begin = d.offsets[r], end = d.offsets[r+1];
    const uint32_t* idxs = d.sorted_indices.data() + begin;
    std::vector<double> scores(n);
    double mx = -std::numeric_limits<double>::infinity();
    for (uint64_t i = 0; i < n; ++i) { scores[i] = qk_score(d, r, i); mx = std::max(mx, scores[i]); }
    double z = 0.0;
    for (uint64_t i = 0; i < n; ++i) { scores[i] = std::exp(std::max(-80.0, std::min(0.0, scores[i] - mx))); z += scores[i]; }
    double selected_z = 0.0; int selected = static_cast<int>(end - begin);
    for (uint64_t p = 0; p < end - begin; ++p) selected_z += scores[idxs[p]];
    std::fill(out.begin(), out.end(), 0.0);
    const double* vals = d.v.data() + r * n * dv;
    for (uint64_t p = 0; p < end - begin; ++p) {
        uint32_t i = idxs[p];
        double w = scores[i] / std::max(1e-300, selected_z);
        const double* vi = vals + static_cast<uint64_t>(i) * dv;
        for (uint64_t j = 0; j < dv; ++j) out[j] += w * vi[j];
    }
    RowResult res; res.selected_count = selected; res.mass = selected_z / std::max(1e-300, z); finalize_quality(dense_ref, out, res); return res;
}

static RowResult oracle_qk_included_packed_row(const Data& d, uint64_t r, std::vector<double>& out, const std::vector<double>* dense_ref = nullptr) {
    const uint64_t n = d.n, dv = d.dv;
    uint64_t begin = d.offsets[r], end = d.offsets[r+1];
    const uint32_t* idxs = d.sorted_indices.data() + begin;
    std::vector<double> scores(n);
    double mx = -std::numeric_limits<double>::infinity();
    for (uint64_t i = 0; i < n; ++i) { scores[i] = qk_score(d, r, i); mx = std::max(mx, scores[i]); }
    double z = 0.0;
    for (uint64_t i = 0; i < n; ++i) { scores[i] = std::exp(std::max(-80.0, std::min(0.0, scores[i] - mx))); z += scores[i]; }
    double selected_z = 0.0; int selected = static_cast<int>(end - begin);
    for (uint64_t p = 0; p < end - begin; ++p) selected_z += scores[idxs[p]];
    std::fill(out.begin(), out.end(), 0.0);
    for (uint64_t p = begin; p < end; ++p) {
        uint32_t i = d.sorted_indices[p];
        double w = scores[i] / std::max(1e-300, selected_z);
        const double* vi = d.packed_values.data() + p * dv;
        for (uint64_t j = 0; j < dv; ++j) out[j] += w * vi[j];
    }
    RowResult res; res.selected_count = selected; res.mass = selected_z / std::max(1e-300, z); finalize_quality(dense_ref, out, res); return res;
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

static Timing time_packed_build(const Data& d, int repeats) {
    std::vector<double> tmp_probs(d.total_selected, 0.0);
    std::vector<double> tmp_values(d.total_selected * d.dv, 0.0);
    volatile double guard = 0.0;
    auto t0 = std::chrono::steady_clock::now();
    for (int rep = 0; rep < repeats; ++rep) {
        for (uint64_t r = 0; r < d.rows; ++r) {
            uint64_t begin = d.offsets[r], end = d.offsets[r+1];
            const double* vals = d.v.data() + r * d.n * d.dv;
            const double* probs = d.probs.data() + r * d.n;
            for (uint64_t p = begin; p < end; ++p) {
                uint32_t i = d.sorted_indices[p];
                tmp_probs[p] = probs[i];
                const double* vi = vals + static_cast<uint64_t>(i) * d.dv;
                double* vo = tmp_values.data() + p * d.dv;
                for (uint64_t j = 0; j < d.dv; ++j) vo[j] = vi[j];
                guard += tmp_probs[p] * 1e-15 + tmp_values[p * d.dv] * 1e-15;
            }
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
    if (argc < 3) { std::cerr << "usage: trace_packet_value_layout_envelope <input.bin> <repeats>\n"; return 2; }
    try {
        Data d = load_bin(argv[1]);
        int repeats = std::max(1, std::stoi(argv[2]));
        // Warm-up all paths.
        (void)time_path(d, 3, [](const Data& d, uint64_t r, std::vector<double>& out){ return dense_qk_online_row(d, r, out); });
        (void)time_path(d, 3, [](const Data& d, uint64_t r, std::vector<double>& out){ return dense_value_only_row(d, r, out); });
        (void)time_path(d, 3, [](const Data& d, uint64_t r, std::vector<double>& out){ return mask_scan_sparse_value_only_row(d, r, out, nullptr); });
        (void)time_path(d, 3, [](const Data& d, uint64_t r, std::vector<double>& out){ return index_sparse_value_only_row(d, r, out, false, nullptr); });
        (void)time_path(d, 3, [](const Data& d, uint64_t r, std::vector<double>& out){ return index_sparse_value_only_row(d, r, out, true, nullptr); });
        (void)time_path(d, 3, [](const Data& d, uint64_t r, std::vector<double>& out){ return packed_sparse_value_only_row(d, r, out, nullptr); });
        (void)time_path(d, 3, [](const Data& d, uint64_t r, std::vector<double>& out){ return oracle_qk_included_index_sorted_row(d, r, out, nullptr); });
        (void)time_path(d, 3, [](const Data& d, uint64_t r, std::vector<double>& out){ return oracle_qk_included_packed_row(d, r, out, nullptr); });
        (void)time_packed_build(d, 2);

        auto dense_qk = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return dense_qk_online_row(d, r, out); });
        auto dense_v = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return dense_value_only_row(d, r, out); });
        auto mask_scan = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return mask_scan_sparse_value_only_row(d, r, out, nullptr); });
        auto rank_gather = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return index_sparse_value_only_row(d, r, out, false, nullptr); });
        auto sorted_gather = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return index_sparse_value_only_row(d, r, out, true, nullptr); });
        auto packed = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return packed_sparse_value_only_row(d, r, out, nullptr); });
        auto qk_sorted = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return oracle_qk_included_index_sorted_row(d, r, out, nullptr); });
        auto qk_packed = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return oracle_qk_included_packed_row(d, r, out, nullptr); });
        auto pack_build = time_packed_build(d, std::max(1, repeats / 10));
        double pack_build_scaled_ms = pack_build.ms * (static_cast<double>(repeats) / static_cast<double>(std::max(1, repeats / 10)));

        std::vector<double> dense_out(d.dv, 0.0), sparse_out(d.dv, 0.0);
        struct Agg { int rows=0; double sel=0, mass=0, rel=0, cos=0, qual=0; };
        Agg all, regs[3];
        double worst_rel = -1.0; int worst_row = -1;
        for (uint64_t r = 0; r < d.rows; ++r) {
            dense_value_only_row(d, r, dense_out);
            auto res = packed_sparse_value_only_row(d, r, sparse_out, &dense_out);
            auto add = [&](Agg& a, const RowResult& x) { a.rows++; a.sel += x.selected_count; a.mass += x.mass; a.rel += x.rel_l2; a.cos += x.cosine; a.qual += x.quality ? 1.0 : 0.0; };
            add(all, res);
            if (d.regime[r] >= 0 && d.regime[r] < 3) add(regs[d.regime[r]], res);
            if (res.rel_l2 > worst_rel) { worst_rel = res.rel_l2; worst_row = static_cast<int>(r); }
        }

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

        const double dense_v_ms = std::max(1e-12, dense_v.ms);
        const double dense_qk_ms = std::max(1e-12, dense_qk.ms);
        std::cout << std::setprecision(12);
        std::cout << "{\n";
        std::cout << "  \"native_binary\": \"trace_packet_value_layout_envelope\",\n";
        std::cout << "  \"rows\": " << d.rows << ",\n";
        std::cout << "  \"n_tokens\": " << d.n << ",\n";
        std::cout << "  \"d_key\": " << d.dk << ",\n";
        std::cout << "  \"d_value\": " << d.dv << ",\n";
        std::cout << "  \"total_selected\": " << d.total_selected << ",\n";
        std::cout << "  \"repeats\": " << repeats << ",\n";
        std::cout << "  \"timing\": {\n";
        std::cout << "    \"dense_qk_online_ms\": " << dense_qk.ms << ",\n";
        std::cout << "    \"dense_value_only_ms\": " << dense_v.ms << ",\n";
        std::cout << "    \"mask_scan_sparse_value_only_ms\": " << mask_scan.ms << ",\n";
        std::cout << "    \"rank_index_sparse_value_only_ms\": " << rank_gather.ms << ",\n";
        std::cout << "    \"sorted_index_sparse_value_only_ms\": " << sorted_gather.ms << ",\n";
        std::cout << "    \"packed_sparse_value_only_ms\": " << packed.ms << ",\n";
        std::cout << "    \"oracle_topp96_qk_included_sorted_ms\": " << qk_sorted.ms << ",\n";
        std::cout << "    \"oracle_topp96_qk_included_packed_ms\": " << qk_packed.ms << ",\n";
        std::cout << "    \"packed_layout_build_ms\": " << pack_build_scaled_ms << ",\n";
        std::cout << "    \"dense_value_only_us_per_row\": " << dense_v.ms * 1000.0 / (static_cast<double>(d.rows) * repeats) << ",\n";
        std::cout << "    \"packed_sparse_value_only_us_per_row\": " << packed.ms * 1000.0 / (static_cast<double>(d.rows) * repeats) << ",\n";
        std::cout << "    \"mask_scan_sparse_value_only_speedup_vs_dense_value_only\": " << dense_v_ms / mask_scan.ms << ",\n";
        std::cout << "    \"rank_index_sparse_value_only_speedup_vs_dense_value_only\": " << dense_v_ms / rank_gather.ms << ",\n";
        std::cout << "    \"sorted_index_sparse_value_only_speedup_vs_dense_value_only\": " << dense_v_ms / sorted_gather.ms << ",\n";
        std::cout << "    \"packed_sparse_value_only_speedup_vs_dense_value_only\": " << dense_v_ms / packed.ms << ",\n";
        std::cout << "    \"oracle_topp96_qk_included_sorted_speedup_vs_dense\": " << dense_qk_ms / qk_sorted.ms << ",\n";
        std::cout << "    \"oracle_topp96_qk_included_packed_speedup_vs_dense\": " << dense_qk_ms / qk_packed.ms << ",\n";
        std::cout << "    \"packed_layout_build_equivalent_replays\": " << pack_build_scaled_ms / std::max(1e-12, packed.ms) << "\n";
        std::cout << "  },\n";
        std::cout << "  \"accounting\": {\"oracle_support_supplied\":true,\"oracle_support_is_promotional\":false,\"packed_value_layout_supplied\":true,\"packed_value_layout_is_promotional\":false,\"selector_cost_zero_by_construction\":true,\"qk_dot_fraction_qk_included_sparse\":1.0,\"score_storage_required_for_oracle_support\":true,\"packed_layout_build_measured\":true},\n";
        std::cout << "  \"all_rows\": "; emit_agg(all); std::cout << ",\n";
        std::cout << "  \"by_regime\": {\n";
        for (int i = 0; i < 3; ++i) { std::cout << "    \"" << regime_name(i) << "\": "; emit_agg(regs[i]); std::cout << (i == 2 ? "\n" : ",\n"); }
        std::cout << "  },\n";
        std::cout << "  \"worst_row\": {\"row_id\":" << worst_row << ",\"rel_l2\":" << worst_rel << "},\n";
        std::cout << "  \"checksums\": {\"dense_qk\":" << dense_qk.checksum << ",\"dense_value\":" << dense_v.checksum << ",\"mask_scan\":" << mask_scan.checksum << ",\"rank_gather\":" << rank_gather.checksum << ",\"sorted_gather\":" << sorted_gather.checksum << ",\"packed\":" << packed.checksum << ",\"qk_sorted\":" << qk_sorted.checksum << ",\"qk_packed\":" << qk_packed.checksum << ",\"pack_build\":" << pack_build.checksum << "}\n";
        std::cout << "}\n";
    } catch (const std::exception& e) { std::cerr << "error: " << e.what() << "\n"; return 1; }
    return 0;
}
