#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

struct Data {
    uint64_t rows=0, n=0, dk=0, dv=0;
    std::vector<double> q, k, v;
    std::vector<int32_t> regime;
};

template <typename T>
static void read_vec(std::ifstream& f, std::vector<T>& dst, uint64_t count) {
    dst.resize(static_cast<size_t>(count));
    f.read(reinterpret_cast<char*>(dst.data()), static_cast<std::streamsize>(sizeof(T) * count));
    if (!f) throw std::runtime_error("short read");
}

static Data load_bin(const std::string& path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) throw std::runtime_error("cannot open input bin");
    char magic[8];
    f.read(magic, 8);
    if (std::strncmp(magic, "CTMLTR65", 8) != 0) throw std::runtime_error("bad magic");
    Data d;
    f.read(reinterpret_cast<char*>(&d.rows), sizeof(uint64_t));
    f.read(reinterpret_cast<char*>(&d.n), sizeof(uint64_t));
    f.read(reinterpret_cast<char*>(&d.dk), sizeof(uint64_t));
    f.read(reinterpret_cast<char*>(&d.dv), sizeof(uint64_t));
    if (!f || d.rows == 0 || d.n == 0 || d.dk == 0 || d.dv == 0) throw std::runtime_error("bad header");
    read_vec(f, d.q, d.rows * d.dk);
    read_vec(f, d.k, d.rows * d.n * d.dk);
    read_vec(f, d.v, d.rows * d.n * d.dv);
    read_vec(f, d.regime, d.rows);
    return d;
}

static inline double qk_score(const Data& d, uint64_t r, uint64_t i) {
    const double* q = d.q.data() + r * d.dk;
    const double* k = d.k.data() + (r * d.n + i) * d.dk;
    double acc = 0.0;
    for (uint64_t j = 0; j < d.dk; ++j) acc += q[j] * k[j];
    return acc / std::sqrt(static_cast<double>(d.dk));
}

static void compute_scores_probs(const Data& d, uint64_t r, std::vector<double>& scores, std::vector<double>& probs) {
    scores.resize(static_cast<size_t>(d.n));
    probs.resize(static_cast<size_t>(d.n));
    double mx = -std::numeric_limits<double>::infinity();
    for (uint64_t i = 0; i < d.n; ++i) { scores[i] = qk_score(d, r, i); mx = std::max(mx, scores[i]); }
    double z = 0.0;
    for (uint64_t i = 0; i < d.n; ++i) { probs[i] = std::exp(std::max(-80.0, std::min(0.0, scores[i] - mx))); z += probs[i]; }
    for (uint64_t i = 0; i < d.n; ++i) probs[i] /= std::max(1e-300, z);
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
        const double a = dense[j], b = sparse[j];
        dn += a*a; sn += b*b; dot += a*b; double diff=b-a; err += diff*diff;
    }
    dn = std::sqrt(dn); sn = std::sqrt(sn); err = std::sqrt(err);
    rel_l2 = err / std::max(1e-12, dn);
    cosine = dot / std::max(1e-12, dn * sn);
    cosine = std::max(-1.0, std::min(1.0, cosine));
}

static void dense_from_probs(const Data& d, uint64_t r, const std::vector<double>& probs, std::vector<double>& out) {
    std::fill(out.begin(), out.end(), 0.0);
    const double* vals = d.v.data() + r * d.n * d.dv;
    for (uint64_t i = 0; i < d.n; ++i) {
        const double p = probs[i];
        const double* vi = vals + i * d.dv;
        for (uint64_t j = 0; j < d.dv; ++j) out[j] += p * vi[j];
    }
}

static RowResult dense_qk_online_row(const Data& d, uint64_t r, std::vector<double>& out) {
    std::vector<double> scores, probs;
    compute_scores_probs(d, r, scores, probs);
    dense_from_probs(d, r, probs, out);
    RowResult res; res.selected_count = static_cast<int>(d.n); res.mass = 1.0; res.quality = true; res.checksum = std::accumulate(out.begin(), out.end(), 0.0); return res;
}

static RowResult qk_only_row(const Data& d, uint64_t r, std::vector<double>& out) {
    std::vector<double> scores, probs;
    compute_scores_probs(d, r, scores, probs);
    std::fill(out.begin(), out.end(), 0.0);
    for (uint64_t i = 0; i < d.n; ++i) out[i % out.size()] += probs[i] * 1e-9;
    RowResult res; res.selected_count = 0; res.mass = 0.0; res.checksum = std::accumulate(out.begin(), out.end(), 0.0); return res;
}

static void finalize_quality(const std::vector<double>* dense_ref, std::vector<double>& out, RowResult& res) {
    res.checksum = std::accumulate(out.begin(), out.end(), 0.0);
    if (dense_ref) {
        metrics(*dense_ref, out, res.rel_l2, res.cosine);
        res.quality = (res.mass >= 0.95 && res.cosine >= 0.995 && res.rel_l2 <= 0.18);
    }
}

static std::vector<uint32_t> exact_sort_topp_select(const std::vector<double>& probs, double target_mass) {
    std::vector<uint32_t> idx(probs.size());
    std::iota(idx.begin(), idx.end(), 0);
    std::sort(idx.begin(), idx.end(), [&](uint32_t a, uint32_t b){ return probs[a] > probs[b]; });
    double mass = 0.0;
    size_t keep = 0;
    for (; keep < idx.size(); ++keep) { mass += probs[idx[keep]]; if (mass >= target_mass) { keep += 1; break; } }
    idx.resize(std::max<size_t>(1, keep));
    std::sort(idx.begin(), idx.end());
    return idx;
}

static std::vector<uint32_t> histogram_mass_select(const std::vector<double>& probs, double target_mass, int bins) {
    bins = std::max(2, bins);
    double maxp = *std::max_element(probs.begin(), probs.end());
    if (maxp <= 0.0) {
        std::vector<uint32_t> all(probs.size()); std::iota(all.begin(), all.end(), 0); return all;
    }
    std::vector<double> mass(static_cast<size_t>(bins), 0.0);
    for (size_t i = 0; i < probs.size(); ++i) {
        int b = static_cast<int>(std::floor((probs[i] / maxp) * static_cast<double>(bins - 1)));
        b = std::max(0, std::min(bins - 1, b));
        mass[static_cast<size_t>(b)] += probs[i];
    }
    double got = 0.0;
    int threshold_bin = 0;
    for (int b = bins - 1; b >= 0; --b) {
        got += mass[static_cast<size_t>(b)];
        threshold_bin = b;
        if (got >= target_mass) break;
    }
    std::vector<uint32_t> selected;
    selected.reserve(probs.size());
    for (uint32_t i = 0; i < probs.size(); ++i) {
        int b = static_cast<int>(std::floor((probs[i] / maxp) * static_cast<double>(bins - 1)));
        b = std::max(0, std::min(bins - 1, b));
        if (b >= threshold_bin) selected.push_back(i);
    }
    if (selected.empty()) selected.push_back(static_cast<uint32_t>(std::distance(probs.begin(), std::max_element(probs.begin(), probs.end()))));
    return selected;
}

static RowResult sparse_index_from_selected(const Data& d, uint64_t r, const std::vector<double>& probs, const std::vector<uint32_t>& selected, std::vector<double>& out, const std::vector<double>* dense_ref) {
    const double* vals = d.v.data() + r * d.n * d.dv;
    double mass = 0.0;
    for (uint32_t i : selected) mass += probs[i];
    std::fill(out.begin(), out.end(), 0.0);
    for (uint32_t i : selected) {
        const double w = probs[i] / std::max(1e-300, mass);
        const double* vi = vals + static_cast<uint64_t>(i) * d.dv;
        for (uint64_t j = 0; j < d.dv; ++j) out[j] += w * vi[j];
    }
    RowResult res; res.selected_count = static_cast<int>(selected.size()); res.mass = mass; finalize_quality(dense_ref, out, res); return res;
}

static RowResult sparse_packed_from_selected(const Data& d, uint64_t r, const std::vector<double>& probs, const std::vector<uint32_t>& selected, std::vector<double>& out, const std::vector<double>* dense_ref) {
    std::vector<double> pbuf(selected.size());
    std::vector<double> vbuf(selected.size() * static_cast<size_t>(d.dv));
    const double* vals = d.v.data() + r * d.n * d.dv;
    double mass = 0.0;
    for (size_t p = 0; p < selected.size(); ++p) {
        const uint32_t i = selected[p];
        pbuf[p] = probs[i];
        mass += pbuf[p];
        const double* vi = vals + static_cast<uint64_t>(i) * d.dv;
        double* vo = vbuf.data() + p * d.dv;
        for (uint64_t j = 0; j < d.dv; ++j) vo[j] = vi[j];
    }
    std::fill(out.begin(), out.end(), 0.0);
    for (size_t p = 0; p < selected.size(); ++p) {
        const double w = pbuf[p] / std::max(1e-300, mass);
        const double* vi = vbuf.data() + p * d.dv;
        for (uint64_t j = 0; j < d.dv; ++j) out[j] += w * vi[j];
    }
    RowResult res; res.selected_count = static_cast<int>(selected.size()); res.mass = mass; finalize_quality(dense_ref, out, res); return res;
}

enum class PathKind { HistIndex, HistPacked, ExactSortIndex, ExactSortPacked };

static RowResult deployable_sparse_row(const Data& d, uint64_t r, std::vector<double>& out, PathKind kind, double target_mass, int bins, const std::vector<double>* dense_ref) {
    std::vector<double> scores, probs;
    compute_scores_probs(d, r, scores, probs);
    std::vector<uint32_t> selected = (kind == PathKind::HistIndex || kind == PathKind::HistPacked)
        ? histogram_mass_select(probs, target_mass, bins)
        : exact_sort_topp_select(probs, target_mass);
    if (kind == PathKind::HistPacked || kind == PathKind::ExactSortPacked) return sparse_packed_from_selected(d, r, probs, selected, out, dense_ref);
    return sparse_index_from_selected(d, r, probs, selected, out, dense_ref);
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
            guard += (out[(r + rep) % out.size()] + 1e-9 * res.selected_count + 1e-12 * res.mass) * 1e-12;
        }
    }
    auto t1 = std::chrono::steady_clock::now();
    return {std::chrono::duration<double, std::milli>(t1 - t0).count(), static_cast<double>(guard)};
}

struct Agg { int rows=0; double sel=0.0, mass=0.0, rel=0.0, cos=0.0, qual=0.0; };
static void add(Agg& a, const RowResult& r) { a.rows++; a.sel += r.selected_count; a.mass += r.mass; a.rel += r.rel_l2; a.cos += r.cosine; a.qual += r.quality ? 1.0 : 0.0; }

static void emit_agg(const Agg& a, uint64_t n) {
    const double rows = std::max(1, a.rows);
    std::cout << "{\"rows\":" << a.rows
              << ",\"mean_selected_count\":" << a.sel / rows
              << ",\"mean_selected_fraction\":" << (a.sel / rows) / static_cast<double>(n)
              << ",\"mean_mass_retained\":" << a.mass / rows
              << ",\"mean_rel_l2\":" << a.rel / rows
              << ",\"mean_cosine\":" << a.cos / rows
              << ",\"quality_rate\":" << a.qual / rows << "}";
}

static std::string regime_name(int32_t id) {
    if (id == 0) return "low_support_lt12";
    if (id == 1) return "mid_support_12_28";
    if (id == 2) return "high_support_ge28";
    return "unknown";
}

int main(int argc, char** argv) {
    if (argc < 5) { std::cerr << "usage: trace_packet_deployable_selector_layout <input.bin> <repeats> <target_mass> <hist_bins>\n"; return 2; }
    try {
        Data d = load_bin(argv[1]);
        int repeats = std::max(1, std::stoi(argv[2]));
        double target_mass = std::stod(argv[3]);
        int hist_bins = std::max(2, std::stoi(argv[4]));
        // warmup
        (void)time_path(d, 3, [](const Data& d, uint64_t r, std::vector<double>& out){ return dense_qk_online_row(d, r, out); });
        (void)time_path(d, 3, [](const Data& d, uint64_t r, std::vector<double>& out){ return qk_only_row(d, r, out); });
        (void)time_path(d, 3, [&](const Data& d, uint64_t r, std::vector<double>& out){ return deployable_sparse_row(d, r, out, PathKind::HistIndex, target_mass, hist_bins, nullptr); });
        (void)time_path(d, 3, [&](const Data& d, uint64_t r, std::vector<double>& out){ return deployable_sparse_row(d, r, out, PathKind::HistPacked, target_mass, hist_bins, nullptr); });
        (void)time_path(d, 3, [&](const Data& d, uint64_t r, std::vector<double>& out){ return deployable_sparse_row(d, r, out, PathKind::ExactSortIndex, target_mass, hist_bins, nullptr); });
        (void)time_path(d, 3, [&](const Data& d, uint64_t r, std::vector<double>& out){ return deployable_sparse_row(d, r, out, PathKind::ExactSortPacked, target_mass, hist_bins, nullptr); });

        auto dense = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return dense_qk_online_row(d, r, out); });
        auto qk_only = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return qk_only_row(d, r, out); });
        auto hist_index = time_path(d, repeats, [&](const Data& d, uint64_t r, std::vector<double>& out){ return deployable_sparse_row(d, r, out, PathKind::HistIndex, target_mass, hist_bins, nullptr); });
        auto hist_packed = time_path(d, repeats, [&](const Data& d, uint64_t r, std::vector<double>& out){ return deployable_sparse_row(d, r, out, PathKind::HistPacked, target_mass, hist_bins, nullptr); });
        auto sort_index = time_path(d, repeats, [&](const Data& d, uint64_t r, std::vector<double>& out){ return deployable_sparse_row(d, r, out, PathKind::ExactSortIndex, target_mass, hist_bins, nullptr); });
        auto sort_packed = time_path(d, repeats, [&](const Data& d, uint64_t r, std::vector<double>& out){ return deployable_sparse_row(d, r, out, PathKind::ExactSortPacked, target_mass, hist_bins, nullptr); });

        Agg h_all, hp_all, s_all, sp_all;
        Agg h_reg[3], hp_reg[3], s_reg[3], sp_reg[3];
        std::vector<double> dense_out(d.dv, 0.0), out(d.dv, 0.0);
        double worst_hist_rel = -1.0; int worst_hist_row = -1;
        double worst_sort_rel = -1.0; int worst_sort_row = -1;
        for (uint64_t r = 0; r < d.rows; ++r) {
            std::vector<double> scores, probs;
            compute_scores_probs(d, r, scores, probs);
            dense_from_probs(d, r, probs, dense_out);
            auto hsel = histogram_mass_select(probs, target_mass, hist_bins);
            auto ssel = exact_sort_topp_select(probs, target_mass);
            auto hr = sparse_index_from_selected(d, r, probs, hsel, out, &dense_out);
            auto hpr = sparse_packed_from_selected(d, r, probs, hsel, out, &dense_out);
            auto sr = sparse_index_from_selected(d, r, probs, ssel, out, &dense_out);
            auto spr = sparse_packed_from_selected(d, r, probs, ssel, out, &dense_out);
            add(h_all, hr); add(hp_all, hpr); add(s_all, sr); add(sp_all, spr);
            if (d.regime[r] >= 0 && d.regime[r] < 3) {
                add(h_reg[d.regime[r]], hr); add(hp_reg[d.regime[r]], hpr); add(s_reg[d.regime[r]], sr); add(sp_reg[d.regime[r]], spr);
            }
            if (hr.rel_l2 > worst_hist_rel) { worst_hist_rel = hr.rel_l2; worst_hist_row = static_cast<int>(r); }
            if (sr.rel_l2 > worst_sort_rel) { worst_sort_rel = sr.rel_l2; worst_sort_row = static_cast<int>(r); }
        }

        const double dense_ms = std::max(1e-12, dense.ms);
        std::cout << std::setprecision(12);
        std::cout << "{\n";
        std::cout << "  \"native_binary\": \"trace_packet_deployable_selector_layout\",\n";
        std::cout << "  \"rows\": " << d.rows << ",\n";
        std::cout << "  \"n_tokens\": " << d.n << ",\n";
        std::cout << "  \"d_key\": " << d.dk << ",\n";
        std::cout << "  \"d_value\": " << d.dv << ",\n";
        std::cout << "  \"repeats\": " << repeats << ",\n";
        std::cout << "  \"target_mass\": " << target_mass << ",\n";
        std::cout << "  \"histogram_bins\": " << hist_bins << ",\n";
        std::cout << "  \"timing\": {\n";
        std::cout << "    \"dense_qk_online_ms\": " << dense.ms << ",\n";
        std::cout << "    \"qk_only_ms\": " << qk_only.ms << ",\n";
        std::cout << "    \"hist_index_qk_included_ms\": " << hist_index.ms << ",\n";
        std::cout << "    \"hist_packed_qk_included_ms\": " << hist_packed.ms << ",\n";
        std::cout << "    \"exact_sort_index_qk_included_ms\": " << sort_index.ms << ",\n";
        std::cout << "    \"exact_sort_packed_qk_included_ms\": " << sort_packed.ms << ",\n";
        std::cout << "    \"dense_qk_online_us_per_row\": " << dense.ms * 1000.0 / (static_cast<double>(d.rows) * repeats) << ",\n";
        std::cout << "    \"hist_index_qk_included_us_per_row\": " << hist_index.ms * 1000.0 / (static_cast<double>(d.rows) * repeats) << ",\n";
        std::cout << "    \"hist_packed_qk_included_us_per_row\": " << hist_packed.ms * 1000.0 / (static_cast<double>(d.rows) * repeats) << ",\n";
        std::cout << "    \"exact_sort_index_qk_included_us_per_row\": " << sort_index.ms * 1000.0 / (static_cast<double>(d.rows) * repeats) << ",\n";
        std::cout << "    \"exact_sort_packed_qk_included_us_per_row\": " << sort_packed.ms * 1000.0 / (static_cast<double>(d.rows) * repeats) << ",\n";
        std::cout << "    \"hist_index_speedup_vs_dense\": " << dense_ms / hist_index.ms << ",\n";
        std::cout << "    \"hist_packed_speedup_vs_dense\": " << dense_ms / hist_packed.ms << ",\n";
        std::cout << "    \"exact_sort_index_speedup_vs_dense\": " << dense_ms / sort_index.ms << ",\n";
        std::cout << "    \"exact_sort_packed_speedup_vs_dense\": " << dense_ms / sort_packed.ms << ",\n";
        std::cout << "    \"qk_only_fraction_of_dense\": " << qk_only.ms / dense_ms << "\n";
        std::cout << "  },\n";
        std::cout << "  \"accounting\": {\"selector_layout_cost_paid_in_timed_loop\":true,\"selectors_use_values\":false,\"selectors_use_dense_outputs\":false,\"histogram_selector_is_score_only\":true,\"exact_sort_topp_selector_is_score_only\":true,\"qk_dot_fraction_deployable_sparse\":1.0,\"row_local_score_prob_storage_required\":true,\"global_score_storage_required\":false,\"packed_layout_constructed_per_query\":true,\"index_layout_constructed_per_query\":true,\"promotion_allowed\":false},\n";
        std::cout << "  \"all_rows\": {\n";
        std::cout << "    \"hist_index\": "; emit_agg(h_all, d.n); std::cout << ",\n";
        std::cout << "    \"hist_packed\": "; emit_agg(hp_all, d.n); std::cout << ",\n";
        std::cout << "    \"exact_sort_index\": "; emit_agg(s_all, d.n); std::cout << ",\n";
        std::cout << "    \"exact_sort_packed\": "; emit_agg(sp_all, d.n); std::cout << "\n";
        std::cout << "  },\n";
        std::cout << "  \"by_regime\": {\n";
        for (int i = 0; i < 3; ++i) {
            std::cout << "    \"" << regime_name(i) << "\": {\"hist_index\":"; emit_agg(h_reg[i], d.n); std::cout << ",\"hist_packed\":"; emit_agg(hp_reg[i], d.n); std::cout << ",\"exact_sort_index\":"; emit_agg(s_reg[i], d.n); std::cout << ",\"exact_sort_packed\":"; emit_agg(sp_reg[i], d.n); std::cout << "}" << (i == 2 ? "\n" : ",\n");
        }
        std::cout << "  },\n";
        std::cout << "  \"worst_rows\": {\"hist_index\":{\"row_id\":" << worst_hist_row << ",\"rel_l2\":" << worst_hist_rel << "},\"exact_sort_index\":{\"row_id\":" << worst_sort_row << ",\"rel_l2\":" << worst_sort_rel << "}},\n";
        std::cout << "  \"checksums\": {\"dense\":" << dense.checksum << ",\"qk_only\":" << qk_only.checksum << ",\"hist_index\":" << hist_index.checksum << ",\"hist_packed\":" << hist_packed.checksum << ",\"exact_sort_index\":" << sort_index.checksum << ",\"exact_sort_packed\":" << sort_packed.checksum << "}\n";
        std::cout << "}\n";
    } catch (const std::exception& e) { std::cerr << "error: " << e.what() << "\n"; return 1; }
    return 0;
}
