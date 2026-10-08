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

template<class T>
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
    if (std::strncmp(magic, "CTMLTR68", 8) != 0) throw std::runtime_error("bad magic");
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

static void dense_from_probs(const Data& d, uint64_t r, const std::vector<double>& probs, std::vector<double>& out) {
    std::fill(out.begin(), out.end(), 0.0);
    const double* vals = d.v.data() + r * d.n * d.dv;
    for (uint64_t i = 0; i < d.n; ++i) {
        const double w = probs[i];
        const double* vi = vals + i * d.dv;
        for (uint64_t j = 0; j < d.dv; ++j) out[j] += w * vi[j];
    }
}

struct SelectResult {
    std::vector<uint32_t> idx;
    int threshold_bin = -1;
    int boundary_candidates = 0;
    int boundary_selected = 0;
    double selected_mass = 0.0;
};

static SelectResult exact_sort_topp_select(const std::vector<double>& probs, double target_mass) {
    std::vector<uint32_t> idx(probs.size());
    std::iota(idx.begin(), idx.end(), 0);
    std::sort(idx.begin(), idx.end(), [&](uint32_t a, uint32_t b){ return probs[a] > probs[b]; });
    double mass = 0.0;
    size_t keep = 0;
    for (; keep < idx.size(); ++keep) {
        mass += probs[idx[keep]];
        if (mass >= target_mass) { keep += 1; break; }
    }
    idx.resize(std::max<size_t>(1, keep));
    std::sort(idx.begin(), idx.end());
    SelectResult r; r.idx = std::move(idx); r.selected_mass = mass; r.boundary_candidates = static_cast<int>(probs.size()); r.boundary_selected = static_cast<int>(r.idx.size());
    return r;
}

static void build_bins(const std::vector<double>& probs, int bins, std::vector<int>& bin_id, std::vector<double>& bin_mass) {
    bins = std::max(2, bins);
    const double maxp = *std::max_element(probs.begin(), probs.end());
    bin_id.resize(probs.size());
    bin_mass.assign(static_cast<size_t>(bins), 0.0);
    if (maxp <= 0.0) {
        std::fill(bin_id.begin(), bin_id.end(), bins - 1);
        bin_mass[static_cast<size_t>(bins - 1)] = 1.0;
        return;
    }
    for (size_t i = 0; i < probs.size(); ++i) {
        int b = static_cast<int>(std::floor((probs[i] / maxp) * static_cast<double>(bins - 1)));
        b = std::max(0, std::min(bins - 1, b));
        bin_id[i] = b;
        bin_mass[static_cast<size_t>(b)] += probs[i];
    }
}

static int find_threshold_bin(const std::vector<double>& bin_mass, double target_mass) {
    double got = 0.0;
    int threshold_bin = 0;
    for (int b = static_cast<int>(bin_mass.size()) - 1; b >= 0; --b) {
        got += bin_mass[static_cast<size_t>(b)];
        threshold_bin = b;
        if (got >= target_mass) break;
    }
    return threshold_bin;
}

static SelectResult histogram_mass_select(const std::vector<double>& probs, double target_mass, int bins) {
    SelectResult r;
    std::vector<int> bin_id;
    std::vector<double> bin_mass;
    build_bins(probs, bins, bin_id, bin_mass);
    const int tb = find_threshold_bin(bin_mass, target_mass);
    r.threshold_bin = tb;
    r.idx.reserve(probs.size());
    for (uint32_t i = 0; i < probs.size(); ++i) {
        if (bin_id[i] >= tb) { r.idx.push_back(i); r.selected_mass += probs[i]; }
        if (bin_id[i] == tb) ++r.boundary_candidates;
    }
    r.boundary_selected = r.boundary_candidates;
    if (r.idx.empty()) {
        r.idx.push_back(static_cast<uint32_t>(std::distance(probs.begin(), std::max_element(probs.begin(), probs.end()))));
        r.selected_mass = probs[r.idx[0]];
    }
    std::sort(r.idx.begin(), r.idx.end());
    return r;
}

static SelectResult boundary_refined_histogram_select(const std::vector<double>& probs, double target_mass, int bins) {
    SelectResult r;
    std::vector<int> bin_id;
    std::vector<double> bin_mass;
    build_bins(probs, bins, bin_id, bin_mass);
    const int tb = find_threshold_bin(bin_mass, target_mass);
    r.threshold_bin = tb;
    std::vector<uint32_t> boundary;
    double mass_above = 0.0;
    for (uint32_t i = 0; i < probs.size(); ++i) {
        if (bin_id[i] > tb) { r.idx.push_back(i); mass_above += probs[i]; }
        else if (bin_id[i] == tb) { boundary.push_back(i); }
    }
    r.boundary_candidates = static_cast<int>(boundary.size());
    std::sort(boundary.begin(), boundary.end(), [&](uint32_t a, uint32_t b){ return probs[a] > probs[b]; });
    double mass = mass_above;
    for (uint32_t i : boundary) {
        if (mass >= target_mass && !r.idx.empty()) break;
        r.idx.push_back(i);
        mass += probs[i];
        ++r.boundary_selected;
    }
    if (r.idx.empty()) {
        r.idx.push_back(static_cast<uint32_t>(std::distance(probs.begin(), std::max_element(probs.begin(), probs.end()))));
        mass = probs[r.idx[0]];
        r.boundary_selected = std::max(1, r.boundary_selected);
    }
    std::sort(r.idx.begin(), r.idx.end());
    r.selected_mass = mass;
    return r;
}

struct RowResult {
    int selected_count = 0;
    double mass = 0.0;
    double rel_l2 = 0.0;
    double cosine = 0.0;
    bool quality = false;
    double checksum = 0.0;
    int threshold_bin = -1;
    int boundary_candidates = 0;
    int boundary_selected = 0;
};

static void metrics(const std::vector<double>& dense, const std::vector<double>& sparse, double& rel_l2, double& cosine) {
    double dn = 0.0, sn = 0.0, dot = 0.0, err = 0.0;
    for (size_t j = 0; j < dense.size(); ++j) {
        const double a = dense[j], b = sparse[j];
        dn += a*a; sn += b*b; dot += a*b; const double diff = b - a; err += diff*diff;
    }
    dn = std::sqrt(dn); sn = std::sqrt(sn); err = std::sqrt(err);
    rel_l2 = err / std::max(1e-12, dn);
    cosine = dot / std::max(1e-12, dn * sn);
    cosine = std::max(-1.0, std::min(1.0, cosine));
}

static RowResult sparse_index_from_selected(const Data& d, uint64_t r, const std::vector<double>& probs, const SelectResult& selected, std::vector<double>& out, const std::vector<double>* dense_ref) {
    const double* vals = d.v.data() + r * d.n * d.dv;
    double mass = 0.0;
    for (uint32_t i : selected.idx) mass += probs[i];
    std::fill(out.begin(), out.end(), 0.0);
    for (uint32_t i : selected.idx) {
        const double w = probs[i] / std::max(1e-300, mass);
        const double* vi = vals + static_cast<uint64_t>(i) * d.dv;
        for (uint64_t j = 0; j < d.dv; ++j) out[j] += w * vi[j];
    }
    RowResult rr;
    rr.selected_count = static_cast<int>(selected.idx.size());
    rr.mass = mass;
    rr.threshold_bin = selected.threshold_bin;
    rr.boundary_candidates = selected.boundary_candidates;
    rr.boundary_selected = selected.boundary_selected;
    rr.checksum = std::accumulate(out.begin(), out.end(), 0.0);
    if (dense_ref) {
        metrics(*dense_ref, out, rr.rel_l2, rr.cosine);
        rr.quality = (rr.mass >= 0.95 && rr.cosine >= 0.995 && rr.rel_l2 <= 0.18);
    }
    return rr;
}

static RowResult sparse_packed_from_selected(const Data& d, uint64_t r, const std::vector<double>& probs, const SelectResult& selected, std::vector<double>& out, const std::vector<double>* dense_ref) {
    std::vector<double> pbuf(selected.idx.size());
    std::vector<double> vbuf(selected.idx.size() * static_cast<size_t>(d.dv));
    const double* vals = d.v.data() + r * d.n * d.dv;
    double mass = 0.0;
    for (size_t p = 0; p < selected.idx.size(); ++p) {
        const uint32_t i = selected.idx[p];
        pbuf[p] = probs[i];
        mass += pbuf[p];
        const double* vi = vals + static_cast<uint64_t>(i) * d.dv;
        double* vo = vbuf.data() + p * d.dv;
        for (uint64_t j = 0; j < d.dv; ++j) vo[j] = vi[j];
    }
    std::fill(out.begin(), out.end(), 0.0);
    for (size_t p = 0; p < selected.idx.size(); ++p) {
        const double w = pbuf[p] / std::max(1e-300, mass);
        const double* vi = vbuf.data() + p * d.dv;
        for (uint64_t j = 0; j < d.dv; ++j) out[j] += w * vi[j];
    }
    RowResult rr;
    rr.selected_count = static_cast<int>(selected.idx.size());
    rr.mass = mass;
    rr.threshold_bin = selected.threshold_bin;
    rr.boundary_candidates = selected.boundary_candidates;
    rr.boundary_selected = selected.boundary_selected;
    rr.checksum = std::accumulate(out.begin(), out.end(), 0.0);
    if (dense_ref) {
        metrics(*dense_ref, out, rr.rel_l2, rr.cosine);
        rr.quality = (rr.mass >= 0.95 && rr.cosine >= 0.995 && rr.rel_l2 <= 0.18);
    }
    return rr;
}

enum class PathKind { Dense, QKOnly, CoarseHistIndex, RefinedHistIndex, RefinedHistPacked, ExactSortIndex };

static RowResult path_row(const Data& d, uint64_t r, PathKind kind, double target_mass, int bins, std::vector<double>& out, const std::vector<double>* dense_ref) {
    std::vector<double> scores, probs;
    compute_scores_probs(d, r, scores, probs);
    if (kind == PathKind::Dense) {
        dense_from_probs(d, r, probs, out);
        RowResult rr; rr.selected_count = static_cast<int>(d.n); rr.mass = 1.0; rr.quality = true; rr.checksum = std::accumulate(out.begin(), out.end(), 0.0); return rr;
    }
    if (kind == PathKind::QKOnly) {
        std::fill(out.begin(), out.end(), 0.0);
        for (uint64_t i = 0; i < d.n; ++i) out[i % out.size()] += probs[i] * 1e-9;
        RowResult rr; rr.checksum = std::accumulate(out.begin(), out.end(), 0.0); return rr;
    }
    SelectResult sel;
    if (kind == PathKind::CoarseHistIndex) sel = histogram_mass_select(probs, target_mass, bins);
    else if (kind == PathKind::ExactSortIndex) sel = exact_sort_topp_select(probs, target_mass);
    else sel = boundary_refined_histogram_select(probs, target_mass, bins);
    if (kind == PathKind::RefinedHistPacked) return sparse_packed_from_selected(d, r, probs, sel, out, dense_ref);
    return sparse_index_from_selected(d, r, probs, sel, out, dense_ref);
}

struct Timing { double ms = 0.0; double checksum = 0.0; };

template<class Fn>
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

struct Agg {
    int rows=0; double sel=0, mass=0, rel=0, cos=0, qual=0, boundary_candidates=0, boundary_selected=0, threshold_bin=0;
};
static void add(Agg& a, const RowResult& r) {
    a.rows++; a.sel += r.selected_count; a.mass += r.mass; a.rel += r.rel_l2; a.cos += r.cosine; a.qual += r.quality ? 1.0 : 0.0;
    a.boundary_candidates += r.boundary_candidates; a.boundary_selected += r.boundary_selected; a.threshold_bin += r.threshold_bin;
}
static void emit_agg(const Agg& a, uint64_t n) {
    const double rows = std::max(1, a.rows);
    std::cout << "{\"rows\":" << a.rows
              << ",\"mean_selected_count\":" << a.sel / rows
              << ",\"mean_selected_fraction\":" << (a.sel / rows) / static_cast<double>(n)
              << ",\"mean_mass_retained\":" << a.mass / rows
              << ",\"mean_rel_l2\":" << a.rel / rows
              << ",\"mean_cosine\":" << a.cos / rows
              << ",\"quality_rate\":" << a.qual / rows
              << ",\"mean_boundary_candidates\":" << a.boundary_candidates / rows
              << ",\"mean_boundary_candidate_fraction\":" << (a.boundary_candidates / rows) / static_cast<double>(n)
              << ",\"mean_boundary_selected\":" << a.boundary_selected / rows
              << ",\"mean_threshold_bin\":" << a.threshold_bin / rows << "}";
}
static const char* regime_name(int32_t id) {
    if (id == 0) return "low_support_lt12";
    if (id == 1) return "mid_support_12_28";
    if (id == 2) return "high_support_ge28";
    return "unknown";
}

int main(int argc, char** argv) {
    if (argc < 5) { std::cerr << "usage: trace_packet_boundary_refined_selector <input.bin> <repeats> <target_mass> <hist_bins>\n"; return 2; }
    try {
        Data d = load_bin(argv[1]);
        int repeats = std::max(1, std::stoi(argv[2]));
        double target_mass = std::stod(argv[3]);
        int bins = std::max(2, std::stoi(argv[4]));
        auto run = [&](PathKind k, const std::vector<double>* ref){ return [&](const Data& d, uint64_t r, std::vector<double>& out){ return path_row(d, r, k, target_mass, bins, out, ref); }; };
        (void)time_path(d, 3, [&](const Data& d, uint64_t r, std::vector<double>& out){ return path_row(d,r,PathKind::Dense,target_mass,bins,out,nullptr); });
        (void)time_path(d, 3, [&](const Data& d, uint64_t r, std::vector<double>& out){ return path_row(d,r,PathKind::CoarseHistIndex,target_mass,bins,out,nullptr); });
        (void)time_path(d, 3, [&](const Data& d, uint64_t r, std::vector<double>& out){ return path_row(d,r,PathKind::RefinedHistIndex,target_mass,bins,out,nullptr); });
        (void)time_path(d, 3, [&](const Data& d, uint64_t r, std::vector<double>& out){ return path_row(d,r,PathKind::RefinedHistPacked,target_mass,bins,out,nullptr); });
        (void)time_path(d, 3, [&](const Data& d, uint64_t r, std::vector<double>& out){ return path_row(d,r,PathKind::ExactSortIndex,target_mass,bins,out,nullptr); });
        auto dense = time_path(d, repeats, [&](const Data& d, uint64_t r, std::vector<double>& out){ return path_row(d,r,PathKind::Dense,target_mass,bins,out,nullptr); });
        auto qk_only = time_path(d, repeats, [&](const Data& d, uint64_t r, std::vector<double>& out){ return path_row(d,r,PathKind::QKOnly,target_mass,bins,out,nullptr); });
        auto coarse = time_path(d, repeats, [&](const Data& d, uint64_t r, std::vector<double>& out){ return path_row(d,r,PathKind::CoarseHistIndex,target_mass,bins,out,nullptr); });
        auto refined = time_path(d, repeats, [&](const Data& d, uint64_t r, std::vector<double>& out){ return path_row(d,r,PathKind::RefinedHistIndex,target_mass,bins,out,nullptr); });
        auto refined_packed = time_path(d, repeats, [&](const Data& d, uint64_t r, std::vector<double>& out){ return path_row(d,r,PathKind::RefinedHistPacked,target_mass,bins,out,nullptr); });
        auto exact = time_path(d, repeats, [&](const Data& d, uint64_t r, std::vector<double>& out){ return path_row(d,r,PathKind::ExactSortIndex,target_mass,bins,out,nullptr); });

        Agg coarse_all, refined_all, refined_packed_all, exact_all;
        Agg coarse_reg[3], refined_reg[3], refined_packed_reg[3], exact_reg[3];
        double worst_refined_rel = -1.0; int worst_refined_row = -1;
        double total_overshoot = 0.0, total_refined_vs_exact_delta = 0.0;
        std::vector<double> dense_out(d.dv, 0.0), out(d.dv, 0.0);
        for (uint64_t r = 0; r < d.rows; ++r) {
            std::vector<double> scores, probs;
            compute_scores_probs(d, r, scores, probs);
            dense_from_probs(d, r, probs, dense_out);
            auto csel = histogram_mass_select(probs, target_mass, bins);
            auto rsel = boundary_refined_histogram_select(probs, target_mass, bins);
            auto esel = exact_sort_topp_select(probs, target_mass);
            auto cr = sparse_index_from_selected(d, r, probs, csel, out, &dense_out);
            auto rr = sparse_index_from_selected(d, r, probs, rsel, out, &dense_out);
            auto rp = sparse_packed_from_selected(d, r, probs, rsel, out, &dense_out);
            auto er = sparse_index_from_selected(d, r, probs, esel, out, &dense_out);
            add(coarse_all, cr); add(refined_all, rr); add(refined_packed_all, rp); add(exact_all, er);
            if (d.regime[r] >= 0 && d.regime[r] < 3) { add(coarse_reg[d.regime[r]], cr); add(refined_reg[d.regime[r]], rr); add(refined_packed_reg[d.regime[r]], rp); add(exact_reg[d.regime[r]], er); }
            total_overshoot += static_cast<double>(csel.idx.size()) - static_cast<double>(esel.idx.size());
            total_refined_vs_exact_delta += static_cast<double>(rsel.idx.size()) - static_cast<double>(esel.idx.size());
            if (rr.rel_l2 > worst_refined_rel) { worst_refined_rel = rr.rel_l2; worst_refined_row = static_cast<int>(r); }
        }

        const double dense_ms = std::max(1e-12, dense.ms);
        std::cout << std::setprecision(12);
        std::cout << "{\n";
        std::cout << "  \"native_binary\": \"trace_packet_boundary_refined_selector\",\n";
        std::cout << "  \"rows\": " << d.rows << ",\n";
        std::cout << "  \"n_tokens\": " << d.n << ",\n";
        std::cout << "  \"d_key\": " << d.dk << ",\n";
        std::cout << "  \"d_value\": " << d.dv << ",\n";
        std::cout << "  \"repeats\": " << repeats << ",\n";
        std::cout << "  \"target_mass\": " << target_mass << ",\n";
        std::cout << "  \"histogram_bins\": " << bins << ",\n";
        std::cout << "  \"timing\": {\n";
        std::cout << "    \"dense_qk_online_ms\": " << dense.ms << ",\n";
        std::cout << "    \"qk_only_ms\": " << qk_only.ms << ",\n";
        std::cout << "    \"coarse_hist_index_qk_included_ms\": " << coarse.ms << ",\n";
        std::cout << "    \"refined_hist_index_qk_included_ms\": " << refined.ms << ",\n";
        std::cout << "    \"refined_hist_packed_qk_included_ms\": " << refined_packed.ms << ",\n";
        std::cout << "    \"exact_sort_index_qk_included_ms\": " << exact.ms << ",\n";
        std::cout << "    \"coarse_hist_index_speedup_vs_dense\": " << dense_ms / coarse.ms << ",\n";
        std::cout << "    \"refined_hist_index_speedup_vs_dense\": " << dense_ms / refined.ms << ",\n";
        std::cout << "    \"refined_hist_packed_speedup_vs_dense\": " << dense_ms / refined_packed.ms << ",\n";
        std::cout << "    \"exact_sort_index_speedup_vs_dense\": " << dense_ms / exact.ms << ",\n";
        std::cout << "    \"qk_only_fraction_of_dense\": " << qk_only.ms / dense_ms << "\n";
        std::cout << "  },\n";
        std::cout << "  \"accounting\": {\"selector_layout_cost_paid_in_timed_loop\":true,\"selectors_use_values\":false,\"selectors_use_dense_outputs\":false,\"qk_dot_fraction_deployable_sparse\":1.0,\"boundary_bucket_sort_paid\":true,\"row_local_score_prob_storage_required\":true,\"global_score_storage_required\":false,\"promotion_allowed\":false},\n";
        std::cout << "  \"all_rows\": {\n";
        std::cout << "    \"coarse_hist_index\": "; emit_agg(coarse_all, d.n); std::cout << ",\n";
        std::cout << "    \"refined_hist_index\": "; emit_agg(refined_all, d.n); std::cout << ",\n";
        std::cout << "    \"refined_hist_packed\": "; emit_agg(refined_packed_all, d.n); std::cout << ",\n";
        std::cout << "    \"exact_sort_index\": "; emit_agg(exact_all, d.n); std::cout << "\n";
        std::cout << "  },\n";
        std::cout << "  \"by_regime\": {\n";
        for (int i = 0; i < 3; ++i) {
            std::cout << "    \"" << regime_name(i) << "\": {\"coarse_hist_index\":"; emit_agg(coarse_reg[i], d.n); std::cout << ",\"refined_hist_index\":"; emit_agg(refined_reg[i], d.n); std::cout << ",\"refined_hist_packed\":"; emit_agg(refined_packed_reg[i], d.n); std::cout << ",\"exact_sort_index\":"; emit_agg(exact_reg[i], d.n); std::cout << "}" << (i == 2 ? "\n" : ",\n");
        }
        std::cout << "  },\n";
        std::cout << "  \"overshoot\": {\"coarse_minus_exact_mean_selected_count\":" << total_overshoot / static_cast<double>(d.rows) << ",\"refined_minus_exact_mean_selected_count\":" << total_refined_vs_exact_delta / static_cast<double>(d.rows) << "},\n";
        std::cout << "  \"worst_rows\": {\"refined_hist_index\":{\"row_id\":" << worst_refined_row << ",\"rel_l2\":" << worst_refined_rel << "}},\n";
        std::cout << "  \"checksums\": {\"dense\":" << dense.checksum << ",\"qk_only\":" << qk_only.checksum << ",\"coarse_hist_index\":" << coarse.checksum << ",\"refined_hist_index\":" << refined.checksum << ",\"refined_hist_packed\":" << refined_packed.checksum << ",\"exact_sort_index\":" << exact.checksum << "}\n";
        std::cout << "}\n";
    } catch (const std::exception& e) { std::cerr << "error: " << e.what() << "\n"; return 1; }
    return 0;
}
