#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

struct Data {
    uint64_t rows=0, n=0, dk=0, dv=0;
    std::vector<double> q, k, v;
    std::vector<int32_t> regime, example, head, layer, trace_batch, group_example, group_example_head;
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
    if (std::strncmp(magic, "CTMLTR66", 8) != 0) throw std::runtime_error("bad magic");
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
    read_vec(f, d.example, d.rows);
    read_vec(f, d.head, d.rows);
    read_vec(f, d.layer, d.rows);
    read_vec(f, d.trace_batch, d.rows);
    read_vec(f, d.group_example, d.rows);
    read_vec(f, d.group_example_head, d.rows);
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

struct Agg {
    int rows = 0;
    double sel = 0.0, mass = 0.0, rel = 0.0, cos = 0.0, qual = 0.0;
};

static void add(Agg& a, const RowResult& r) {
    a.rows += 1;
    a.sel += r.selected_count;
    a.mass += r.mass;
    a.rel += r.rel_l2;
    a.cos += r.cosine;
    a.qual += r.quality ? 1.0 : 0.0;
}

static void metrics(const std::vector<double>& dense, const std::vector<double>& sparse, double& rel_l2, double& cosine) {
    double dn = 0.0, sn = 0.0, dot = 0.0, err = 0.0;
    for (size_t j = 0; j < dense.size(); ++j) {
        const double a = dense[j], b = sparse[j];
        dn += a*a; sn += b*b; dot += a*b; double diff = b - a; err += diff*diff;
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
        got += mass[static_cast<size_t>(b)]; threshold_bin = b;
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
    std::sort(selected.begin(), selected.end());
    return selected;
}

static std::vector<uint32_t> union_supports(const std::vector<std::vector<uint32_t>>& supports, const std::vector<uint64_t>& rows) {
    std::vector<uint32_t> uni;
    for (uint64_t r : rows) {
        const auto& s = supports[static_cast<size_t>(r)];
        uni.insert(uni.end(), s.begin(), s.end());
    }
    std::sort(uni.begin(), uni.end());
    uni.erase(std::unique(uni.begin(), uni.end()), uni.end());
    return uni;
}

static double jaccard(const std::vector<uint32_t>& a, const std::vector<uint32_t>& b) {
    size_t ia = 0, ib = 0, inter = 0, uni = 0;
    while (ia < a.size() || ib < b.size()) {
        if (ib >= b.size() || (ia < a.size() && a[ia] < b[ib])) { ++uni; ++ia; }
        else if (ia >= a.size() || b[ib] < a[ia]) { ++uni; ++ib; }
        else { ++inter; ++uni; ++ia; ++ib; }
    }
    return uni ? static_cast<double>(inter) / static_cast<double>(uni) : 1.0;
}

static RowResult sparse_from_probs_selected(const Data& d, uint64_t r, const std::vector<double>& probs, const std::vector<uint32_t>& selected, std::vector<double>& out, const std::vector<double>* dense_ref) {
    const double* vals = d.v.data() + r * d.n * d.dv;
    double mass = 0.0;
    for (uint32_t i : selected) mass += probs[i];
    std::fill(out.begin(), out.end(), 0.0);
    for (uint32_t i : selected) {
        const double w = probs[i] / std::max(1e-300, mass);
        const double* vi = vals + static_cast<uint64_t>(i) * d.dv;
        for (uint64_t j = 0; j < d.dv; ++j) out[j] += w * vi[j];
    }
    RowResult res; res.selected_count = static_cast<int>(selected.size()); res.mass = mass; res.checksum = std::accumulate(out.begin(), out.end(), 0.0);
    if (dense_ref) { metrics(*dense_ref, out, res.rel_l2, res.cosine); res.quality = (res.mass >= 0.95 && res.cosine >= 0.995 && res.rel_l2 <= 0.18); }
    return res;
}

static RowResult sparse_from_selected_qk_only(const Data& d, uint64_t r, const std::vector<uint32_t>& selected, std::vector<double>& out, const std::vector<double>* dense_ref, const std::vector<double>* dense_probs) {
    std::fill(out.begin(), out.end(), 0.0);
    if (selected.empty()) { RowResult res; return res; }
    std::vector<double> scores(selected.size());
    double mx = -std::numeric_limits<double>::infinity();
    for (size_t p = 0; p < selected.size(); ++p) { scores[p] = qk_score(d, r, selected[p]); mx = std::max(mx, scores[p]); }
    double z = 0.0;
    for (double& x : scores) { x = std::exp(std::max(-80.0, std::min(0.0, x - mx))); z += x; }
    const double* vals = d.v.data() + r * d.n * d.dv;
    double mass = 0.0;
    for (size_t p = 0; p < selected.size(); ++p) {
        const uint32_t i = selected[p];
        const double w = scores[p] / std::max(1e-300, z);
        if (dense_probs) mass += (*dense_probs)[i];
        const double* vi = vals + static_cast<uint64_t>(i) * d.dv;
        for (uint64_t j = 0; j < d.dv; ++j) out[j] += w * vi[j];
    }
    RowResult res; res.selected_count = static_cast<int>(selected.size()); res.mass = mass; res.checksum = std::accumulate(out.begin(), out.end(), 0.0);
    if (dense_ref) { metrics(*dense_ref, out, res.rel_l2, res.cosine); res.quality = (res.mass >= 0.95 && res.cosine >= 0.995 && res.rel_l2 <= 0.18); }
    return res;
}

static RowResult dense_qk_online_row(const Data& d, uint64_t r, std::vector<double>& out) {
    std::vector<double> scores, probs;
    compute_scores_probs(d, r, scores, probs);
    dense_from_probs(d, r, probs, out);
    RowResult res; res.selected_count = static_cast<int>(d.n); res.mass = 1.0; res.quality = true; res.checksum = std::accumulate(out.begin(), out.end(), 0.0); return res;
}

struct Timing { double ms = 0.0; double checksum = 0.0; };

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

static std::vector<std::vector<uint64_t>> make_groups(const std::vector<int32_t>& ids) {
    std::map<int32_t, std::vector<uint64_t>> m;
    for (uint64_t r = 0; r < ids.size(); ++r) m[ids[static_cast<size_t>(r)]].push_back(r);
    std::vector<std::vector<uint64_t>> groups;
    for (auto& kv : m) groups.push_back(kv.second);
    return groups;
}

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

static double speedup(double base_ms, double path_ms) { return path_ms > 0.0 ? base_ms / path_ms : 0.0; }

int main(int argc, char** argv) {
    if (argc < 5) { std::cerr << "usage: trace_packet_support_reuse <input.bin> <repeats> <target_mass> <hist_bins>\n"; return 2; }
    try {
        Data d = load_bin(argv[1]);
        int repeats = std::max(1, std::stoi(argv[2]));
        double target_mass = std::stod(argv[3]);
        int hist_bins = std::max(2, std::stoi(argv[4]));
        std::vector<std::vector<double>> dense_probs(static_cast<size_t>(d.rows));
        std::vector<std::vector<double>> dense_ref(static_cast<size_t>(d.rows), std::vector<double>(static_cast<size_t>(d.dv), 0.0));
        std::vector<std::vector<uint32_t>> fresh_supports(static_cast<size_t>(d.rows));
        std::vector<double> scores, probs;
        std::vector<double> out(static_cast<size_t>(d.dv), 0.0);
        for (uint64_t r = 0; r < d.rows; ++r) {
            compute_scores_probs(d, r, scores, probs);
            dense_probs[static_cast<size_t>(r)] = probs;
            dense_from_probs(d, r, probs, dense_ref[static_cast<size_t>(r)]);
            fresh_supports[static_cast<size_t>(r)] = histogram_mass_select(probs, target_mass, hist_bins);
        }
        auto groups_example = make_groups(d.group_example);
        auto groups_example_head = make_groups(d.group_example_head);

        auto eval_fresh = [&]() {
            Agg a;
            for (uint64_t r = 0; r < d.rows; ++r) {
                add(a, sparse_from_probs_selected(d, r, dense_probs[static_cast<size_t>(r)], fresh_supports[static_cast<size_t>(r)], out, &dense_ref[static_cast<size_t>(r)]));
            }
            return a;
        };
        auto eval_anchor = [&](const std::vector<std::vector<uint64_t>>& groups, double& qk_frac, double& jac, double& union_frac) {
            Agg a; double qk = 0.0, jac_sum = 0.0, jac_n = 0.0, uni_sum = 0.0;
            for (const auto& g : groups) {
                uint64_t anchor = g.front();
                const auto& support = fresh_supports[static_cast<size_t>(anchor)];
                auto uni = union_supports(fresh_supports, g);
                uni_sum += static_cast<double>(uni.size()) / static_cast<double>(d.n);
                for (uint64_t r : g) {
                    qk += (r == anchor) ? static_cast<double>(d.n) : static_cast<double>(support.size());
                    if (r != anchor) { jac_sum += jaccard(support, fresh_supports[static_cast<size_t>(r)]); jac_n += 1.0; }
                    if (r == anchor) add(a, sparse_from_probs_selected(d, r, dense_probs[static_cast<size_t>(r)], support, out, &dense_ref[static_cast<size_t>(r)]));
                    else add(a, sparse_from_selected_qk_only(d, r, support, out, &dense_ref[static_cast<size_t>(r)], &dense_probs[static_cast<size_t>(r)]));
                }
            }
            qk_frac = qk / (static_cast<double>(d.rows) * static_cast<double>(d.n));
            jac = jac_n > 0.0 ? jac_sum / jac_n : 1.0;
            union_frac = uni_sum / static_cast<double>(std::max<size_t>(1, groups.size()));
            return a;
        };
        auto eval_union = [&](const std::vector<std::vector<uint64_t>>& groups, double& qk_frac, double& union_frac) {
            Agg a; double qk = 0.0, uni_sum = 0.0;
            for (const auto& g : groups) {
                auto uni = union_supports(fresh_supports, g);
                uni_sum += static_cast<double>(uni.size()) / static_cast<double>(d.n);
                for (uint64_t r : g) {
                    qk += static_cast<double>(uni.size());
                    add(a, sparse_from_selected_qk_only(d, r, uni, out, &dense_ref[static_cast<size_t>(r)], &dense_probs[static_cast<size_t>(r)]));
                }
            }
            qk_frac = qk / (static_cast<double>(d.rows) * static_cast<double>(d.n));
            union_frac = uni_sum / static_cast<double>(std::max<size_t>(1, groups.size()));
            return a;
        };

        Agg fresh_a = eval_fresh();
        double ex_qk=0.0, ex_j=0.0, ex_uni=0.0; Agg ex_a = eval_anchor(groups_example, ex_qk, ex_j, ex_uni);
        double exh_qk=0.0, exh_j=0.0, exh_uni=0.0; Agg exh_a = eval_anchor(groups_example_head, exh_qk, exh_j, exh_uni);
        double union_ex_qk=0.0, union_ex_frac=0.0; Agg union_ex_a = eval_union(groups_example, union_ex_qk, union_ex_frac);

        // Warmup.
        (void)time_path(d, 3, [](const Data& d, uint64_t r, std::vector<double>& out){ return dense_qk_online_row(d, r, out); });
        (void)time_path(d, 3, [&](const Data& d, uint64_t r, std::vector<double>& out){ std::vector<double> s,p; compute_scores_probs(d,r,s,p); auto sel=histogram_mass_select(p,target_mass,hist_bins); return sparse_from_probs_selected(d,r,p,sel,out,nullptr); });
        auto time_anchor = [&](const std::vector<std::vector<uint64_t>>& groups) {
            volatile double guard = 0.0;
            std::vector<double> tout(static_cast<size_t>(d.dv), 0.0), s, p;
            auto t0 = std::chrono::steady_clock::now();
            for (int rep=0; rep<repeats; ++rep) {
                for (const auto& g : groups) {
                    uint64_t anchor = g.front();
                    compute_scores_probs(d, anchor, s, p);
                    auto support = histogram_mass_select(p, target_mass, hist_bins);
                    auto res0 = sparse_from_probs_selected(d, anchor, p, support, tout, nullptr);
                    guard += (tout[(anchor + rep) % tout.size()] + 1e-9*res0.selected_count) * 1e-12;
                    for (size_t gi=1; gi<g.size(); ++gi) {
                        uint64_t r = g[gi];
                        auto res = sparse_from_selected_qk_only(d, r, support, tout, nullptr, nullptr);
                        guard += (tout[(r + rep) % tout.size()] + 1e-9*res.selected_count) * 1e-12;
                    }
                }
            }
            auto t1 = std::chrono::steady_clock::now();
            return Timing{std::chrono::duration<double, std::milli>(t1-t0).count(), static_cast<double>(guard)};
        };
        auto time_union = [&](const std::vector<std::vector<uint64_t>>& groups) {
            volatile double guard = 0.0;
            std::vector<double> tout(static_cast<size_t>(d.dv), 0.0), s, p;
            auto t0 = std::chrono::steady_clock::now();
            for (int rep=0; rep<repeats; ++rep) {
                for (const auto& g : groups) {
                    std::vector<std::vector<uint32_t>> local;
                    local.reserve(g.size());
                    for (uint64_t r : g) { compute_scores_probs(d, r, s, p); local.push_back(histogram_mass_select(p, target_mass, hist_bins)); }
                    std::vector<uint32_t> uni;
                    for (const auto& ls : local) uni.insert(uni.end(), ls.begin(), ls.end());
                    std::sort(uni.begin(), uni.end()); uni.erase(std::unique(uni.begin(), uni.end()), uni.end());
                    for (uint64_t r : g) {
                        auto res = sparse_from_selected_qk_only(d, r, uni, tout, nullptr, nullptr);
                        guard += (tout[(r + rep) % tout.size()] + 1e-9*res.selected_count) * 1e-12;
                    }
                }
            }
            auto t1 = std::chrono::steady_clock::now();
            return Timing{std::chrono::duration<double, std::milli>(t1-t0).count(), static_cast<double>(guard)};
        };

        Timing dense_t = time_path(d, repeats, [](const Data& d, uint64_t r, std::vector<double>& out){ return dense_qk_online_row(d, r, out); });
        Timing fresh_t = time_path(d, repeats, [&](const Data& d, uint64_t r, std::vector<double>& out){ std::vector<double> s,p; compute_scores_probs(d,r,s,p); auto sel=histogram_mass_select(p,target_mass,hist_bins); return sparse_from_probs_selected(d,r,p,sel,out,nullptr); });
        Timing ex_t = time_anchor(groups_example);
        Timing exh_t = time_anchor(groups_example_head);
        Timing union_t = time_union(groups_example);

        std::cout << std::setprecision(12);
        std::cout << "{\n";
        std::cout << "\"rows\":" << d.rows << ",\"n_tokens\":" << d.n << ",\"d_key\":" << d.dk << ",\"d_value\":" << d.dv << ",\"repeats\":" << repeats << ",\"target_mass\":" << target_mass << ",\"hist_bins\":" << hist_bins << ",\n";
        std::cout << "\"groups\":{\"example_groups\":" << groups_example.size() << ",\"example_head_groups\":" << groups_example_head.size() << "},\n";
        std::cout << "\"timing\":{"
                  << "\"dense_qk_online_ms\":" << dense_t.ms << ","
                  << "\"fresh_hist_index_ms\":" << fresh_t.ms << ","
                  << "\"reuse_example_anchor_hist_ms\":" << ex_t.ms << ","
                  << "\"reuse_example_head_anchor_hist_ms\":" << exh_t.ms << ","
                  << "\"union_example_hist_upper_bound_ms\":" << union_t.ms << "},\n";
        std::cout << "\"speedups_vs_dense\":{"
                  << "\"fresh_hist_index\":" << speedup(dense_t.ms, fresh_t.ms) << ","
                  << "\"reuse_example_anchor_hist\":" << speedup(dense_t.ms, ex_t.ms) << ","
                  << "\"reuse_example_head_anchor_hist\":" << speedup(dense_t.ms, exh_t.ms) << ","
                  << "\"union_example_hist_upper_bound\":" << speedup(dense_t.ms, union_t.ms) << "},\n";
        std::cout << "\"all_rows\":{\"fresh_hist_index\":"; emit_agg(fresh_a, d.n);
        std::cout << ",\"reuse_example_anchor_hist\":"; emit_agg(ex_a, d.n);
        std::cout << ",\"reuse_example_head_anchor_hist\":"; emit_agg(exh_a, d.n);
        std::cout << ",\"union_example_hist_upper_bound\":"; emit_agg(union_ex_a, d.n);
        std::cout << "},\n";
        std::cout << "\"accounting\":{"
                  << "\"support_reuse_overhead_paid_in_timed_loop\":true,"
                  << "\"selectors_use_values\":false,"
                  << "\"selectors_use_dense_outputs\":false,"
                  << "\"fresh_hist_qk_dot_fraction\":1.0,"
                  << "\"reuse_example_anchor_qk_dot_fraction\":" << ex_qk << ","
                  << "\"reuse_example_head_anchor_qk_dot_fraction\":" << exh_qk << ","
                  << "\"union_example_hist_qk_dot_fraction\":" << union_ex_qk << ","
                  << "\"reuse_example_anchor_jaccard_mean\":" << ex_j << ","
                  << "\"reuse_example_head_anchor_jaccard_mean\":" << exh_j << ","
                  << "\"reuse_example_anchor_union_fraction\":" << ex_uni << ","
                  << "\"reuse_example_head_anchor_union_fraction\":" << exh_uni << ","
                  << "\"union_example_hist_selected_fraction\":" << union_ex_frac << ","
                  << "\"union_support_uses_all_group_rows\":true,"
                  << "\"union_support_non_promotional_upper_bound\":true,"
                  << "\"no_global_score_storage_required_for_anchor_reuse\":true"
                  << "}\n";
        std::cout << "}\n";
    } catch (const std::exception& e) {
        std::cerr << "error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
