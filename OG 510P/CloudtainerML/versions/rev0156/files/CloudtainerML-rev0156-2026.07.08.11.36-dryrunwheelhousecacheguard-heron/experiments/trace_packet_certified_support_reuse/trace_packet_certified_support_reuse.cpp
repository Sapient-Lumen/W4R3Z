#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

struct Data {
    uint64_t rows=0, n=0, dk=0, dv=0;
    std::vector<double> q, k, v;
    std::vector<int32_t> group_example;
};

template <typename T> static void read_vec(std::ifstream& f, std::vector<T>& x, uint64_t count) {
    x.resize(static_cast<size_t>(count));
    f.read(reinterpret_cast<char*>(x.data()), static_cast<std::streamsize>(sizeof(T)*count));
    if (!f) throw std::runtime_error("short binary input");
}

static Data load_bin(const std::string& path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) throw std::runtime_error("cannot open input");
    char magic[8]; f.read(magic, 8);
    if (std::string(magic, magic+8) != "CTMLTR69") throw std::runtime_error("bad magic");
    Data d;
    f.read(reinterpret_cast<char*>(&d.rows), 8);
    f.read(reinterpret_cast<char*>(&d.n), 8);
    f.read(reinterpret_cast<char*>(&d.dk), 8);
    f.read(reinterpret_cast<char*>(&d.dv), 8);
    read_vec(f, d.q, d.rows*d.dk);
    read_vec(f, d.k, d.rows*d.n*d.dk);
    read_vec(f, d.v, d.rows*d.n*d.dv);
    read_vec(f, d.group_example, d.rows);
    return d;
}

static inline double qk_score(const Data& d, uint64_t r, uint64_t i) {
    const double* q = d.q.data() + r*d.dk;
    const double* k = d.k.data() + (r*d.n + i)*d.dk;
    double acc = 0.0;
    for (uint64_t j=0;j<d.dk;++j) acc += q[j]*k[j];
    return acc / std::sqrt(static_cast<double>(d.dk));
}

static double q_norm(const Data& d, uint64_t r) {
    const double* q = d.q.data() + r*d.dk;
    double s=0.0; for (uint64_t j=0;j<d.dk;++j) s += q[j]*q[j];
    return std::sqrt(s);
}

static double q_distance(const Data& d, uint64_t a, uint64_t r) {
    const double* qa = d.q.data() + a*d.dk;
    const double* qr = d.q.data() + r*d.dk;
    double s=0.0; for (uint64_t j=0;j<d.dk;++j) { double z=qr[j]-qa[j]; s += z*z; }
    return std::sqrt(s);
}

static double key_norm(const Data& d, uint64_t r, uint64_t i) {
    const double* k = d.k.data() + (r*d.n + i)*d.dk;
    double s=0.0; for (uint64_t j=0;j<d.dk;++j) s += k[j]*k[j];
    return std::sqrt(s);
}

static double key_drift_norm(const Data& d, uint64_t a, uint64_t r, uint64_t i) {
    const double* ka = d.k.data() + (a*d.n + i)*d.dk;
    const double* kr = d.k.data() + (r*d.n + i)*d.dk;
    double s=0.0; for (uint64_t j=0;j<d.dk;++j) { double z=kr[j]-ka[j]; s += z*z; }
    return std::sqrt(s);
}

static void compute_scores_probs(const Data& d, uint64_t r, std::vector<double>& scores, std::vector<double>& probs) {
    scores.assign(static_cast<size_t>(d.n), 0.0);
    probs.assign(static_cast<size_t>(d.n), 0.0);
    double mx = -1e300;
    for (uint64_t i=0;i<d.n;++i) { scores[i] = qk_score(d,r,i); mx = std::max(mx, scores[i]); }
    double z=0.0;
    for (uint64_t i=0;i<d.n;++i) { probs[i] = std::exp(std::max(-80.0, std::min(0.0, scores[i]-mx))); z += probs[i]; }
    for (uint64_t i=0;i<d.n;++i) probs[i] /= std::max(1e-300, z);
}

static std::vector<uint32_t> histogram_mass_select(const std::vector<double>& probs, double target_mass, int bins) {
    bins = std::max(2,bins);
    double maxp = *std::max_element(probs.begin(), probs.end());
    if (maxp <= 0.0) { std::vector<uint32_t> all(probs.size()); std::iota(all.begin(), all.end(), 0); return all; }
    std::vector<double> mass(static_cast<size_t>(bins), 0.0);
    for (size_t i=0;i<probs.size();++i) {
        int b = static_cast<int>(std::floor((probs[i]/maxp)*static_cast<double>(bins-1)));
        b = std::max(0, std::min(bins-1, b)); mass[static_cast<size_t>(b)] += probs[i];
    }
    double got=0.0; int threshold_bin=0;
    for (int b=bins-1;b>=0;--b) { got += mass[static_cast<size_t>(b)]; threshold_bin=b; if (got >= target_mass) break; }
    std::vector<uint32_t> sel;
    for (uint32_t i=0;i<probs.size();++i) {
        int b = static_cast<int>(std::floor((probs[i]/maxp)*static_cast<double>(bins-1)));
        b = std::max(0, std::min(bins-1, b)); if (b >= threshold_bin) sel.push_back(i);
    }
    if (sel.empty()) sel.push_back(static_cast<uint32_t>(std::distance(probs.begin(), std::max_element(probs.begin(), probs.end()))));
    std::sort(sel.begin(), sel.end()); return sel;
}

static void dense_from_probs(const Data& d, uint64_t r, const std::vector<double>& probs, std::vector<double>& out) {
    std::fill(out.begin(), out.end(), 0.0);
    const double* vals = d.v.data() + r*d.n*d.dv;
    for (uint64_t i=0;i<d.n;++i) {
        const double* vi = vals + i*d.dv;
        double p=probs[static_cast<size_t>(i)];
        for (uint64_t j=0;j<d.dv;++j) out[static_cast<size_t>(j)] += p*vi[j];
    }
}

static void metrics(const std::vector<double>& dense, const std::vector<double>& sparse, double& rel, double& cos) {
    double dn=0.0, sn=0.0, dot=0.0, err=0.0;
    for (size_t j=0;j<dense.size();++j) { double a=dense[j], b=sparse[j]; dn+=a*a; sn+=b*b; dot+=a*b; double diff=b-a; err+=diff*diff; }
    dn=std::sqrt(dn); sn=std::sqrt(sn); err=std::sqrt(err);
    rel = err/std::max(1e-12, dn); cos = dot/std::max(1e-12, dn*sn); cos=std::max(-1.0,std::min(1.0,cos));
}

struct RowResult { int selected=0; double mass=0.0, rel=0.0, cos=0.0, checksum=0.0; bool quality=false; };
struct Agg { int rows=0; double sel=0.0, mass=0.0, rel=0.0, cos=0.0, qual=0.0; };
static void add(Agg& a, const RowResult& r) { a.rows++; a.sel += r.selected; a.mass += r.mass; a.rel += r.rel; a.cos += r.cos; a.qual += r.quality ? 1.0 : 0.0; }

static RowResult sparse_from_probs_selected(const Data& d, uint64_t r, const std::vector<double>& probs, const std::vector<uint32_t>& selected, std::vector<double>& out, const std::vector<double>* dense_ref) {
    const double* vals = d.v.data() + r*d.n*d.dv;
    double mass=0.0; for (uint32_t i: selected) mass += probs[i];
    std::fill(out.begin(), out.end(), 0.0);
    for (uint32_t i: selected) {
        double w = probs[i]/std::max(1e-300, mass);
        const double* vi = vals + static_cast<uint64_t>(i)*d.dv;
        for (uint64_t j=0;j<d.dv;++j) out[static_cast<size_t>(j)] += w*vi[j];
    }
    RowResult rres; rres.selected = static_cast<int>(selected.size()); rres.mass=mass; rres.checksum = std::accumulate(out.begin(), out.end(), 0.0);
    if (dense_ref) { metrics(*dense_ref, out, rres.rel, rres.cos); rres.quality = (rres.mass >= 0.95 && rres.cos >= 0.995 && rres.rel <= 0.18); }
    return rres;
}

static RowResult sparse_from_selected_qk_only(const Data& d, uint64_t r, const std::vector<uint32_t>& selected, std::vector<double>& out, const std::vector<double>* dense_ref, const std::vector<double>* dense_probs) {
    std::fill(out.begin(), out.end(), 0.0);
    if (selected.empty()) return {};
    std::vector<double> scores(selected.size()); double mx=-1e300;
    for (size_t p=0;p<selected.size();++p) { scores[p]=qk_score(d,r,selected[p]); mx=std::max(mx, scores[p]); }
    double z=0.0; for (double& x: scores) { x=std::exp(std::max(-80.0, std::min(0.0, x-mx))); z += x; }
    const double* vals = d.v.data() + r*d.n*d.dv;
    double mass=0.0;
    for (size_t p=0;p<selected.size();++p) {
        uint32_t i=selected[p]; double w=scores[p]/std::max(1e-300,z);
        if (dense_probs) mass += (*dense_probs)[i];
        const double* vi = vals + static_cast<uint64_t>(i)*d.dv;
        for (uint64_t j=0;j<d.dv;++j) out[static_cast<size_t>(j)] += w*vi[j];
    }
    RowResult rres; rres.selected=static_cast<int>(selected.size()); rres.mass=mass; rres.checksum=std::accumulate(out.begin(), out.end(), 0.0);
    if (dense_ref) { metrics(*dense_ref, out, rres.rel, rres.cos); rres.quality = (rres.mass >= 0.95 && rres.cos >= 0.995 && rres.rel <= 0.18); }
    return rres;
}

struct Cert { bool ok=false; double lower_mass=0.0; double outside_ub=0.0; double selected_z=0.0; };
static Cert certify_reuse(const Data& d, uint64_t anchor, uint64_t r, const std::vector<double>& anchor_scores, const std::vector<uint32_t>& support, double target) {
    std::vector<char> in(static_cast<size_t>(d.n), 0);
    for (uint32_t i: support) in[i]=1;
    const double qd = q_distance(d, anchor, r);
    const double qan = q_norm(d, anchor);
    const double inv = 1.0/std::sqrt(static_cast<double>(d.dk));
    double mx=-1e300;
    std::vector<double> selected_scores; selected_scores.reserve(support.size());
    for (uint32_t i: support) { double s=qk_score(d,r,i); selected_scores.push_back(s); mx=std::max(mx,s); }
    std::vector<double> outside_ubs; outside_ubs.reserve(static_cast<size_t>(d.n-support.size()));
    for (uint64_t i=0;i<d.n;++i) if (!in[static_cast<size_t>(i)]) {
        double ub = anchor_scores[static_cast<size_t>(i)] + (qd*key_norm(d,r,i) + qan*key_drift_norm(d,anchor,r,i))*inv;
        outside_ubs.push_back(ub); mx=std::max(mx,ub);
    }
    double zsel=0.0, zout=0.0;
    for (double s: selected_scores) zsel += std::exp(std::max(-80.0, std::min(0.0, s-mx)));
    for (double ub: outside_ubs) zout += std::exp(std::max(-80.0, std::min(0.0, ub-mx)));
    Cert c; c.selected_z=zsel; c.outside_ub=zout; c.lower_mass = zsel/std::max(1e-300,zsel+zout); c.ok = c.lower_mass >= target; return c;
}

static std::vector<std::vector<uint64_t>> make_groups(const std::vector<int32_t>& ids) {
    std::map<int32_t, std::vector<uint64_t>> m;
    for (uint64_t r=0;r<ids.size();++r) m[ids[static_cast<size_t>(r)]].push_back(r);
    std::vector<std::vector<uint64_t>> g; for (auto& kv: m) if (!kv.second.empty()) g.push_back(kv.second); return g;
}

static void emit_agg(const Agg& a, uint64_t n) {
    double rows = std::max(1, a.rows);
    std::cout << "{\"rows\":" << a.rows
              << ",\"mean_selected_count\":" << a.sel/rows
              << ",\"mean_selected_fraction\":" << (a.sel/rows)/static_cast<double>(n)
              << ",\"mean_mass_retained\":" << a.mass/rows
              << ",\"mean_rel_l2\":" << a.rel/rows
              << ",\"mean_cosine\":" << a.cos/rows
              << ",\"quality_rate\":" << a.qual/rows << "}";
}

struct EvalExtras { int reused=0, fallback=0, false_cert=0, candidates=0; double lower_mass=0.0; double qk=0.0; double bound_scans=0.0; };
struct Timing { double ms=0.0; double guard=0.0; };
static double speedup(double base, double path) { return path > 0.0 ? base/path : 0.0; }

template <typename Fn> static Timing time_path(const Data& d, int repeats, Fn fn) {
    std::vector<double> out(static_cast<size_t>(d.dv),0.0); volatile double guard=0.0;
    auto t0 = std::chrono::steady_clock::now();
    for (int rep=0; rep<repeats; ++rep) for (uint64_t r=0;r<d.rows;++r) { auto rr=fn(r,out); guard += (out[(r+rep)%out.size()] + 1e-9*rr.selected + 1e-12*rr.mass)*1e-12; }
    auto t1 = std::chrono::steady_clock::now();
    return {std::chrono::duration<double,std::milli>(t1-t0).count(), static_cast<double>(guard)};
}

int main(int argc, char** argv) {
    if (argc < 5) { std::cerr << "usage: trace_packet_certified_support_reuse <input.bin> <repeats> <target_mass> <hist_bins>\n"; return 2; }
    try {
        Data d = load_bin(argv[1]);
        int repeats = std::max(1, std::stoi(argv[2]));
        double target = std::stod(argv[3]);
        int bins = std::max(2, std::stoi(argv[4]));
        std::vector<std::vector<double>> dense_probs(d.rows), dense_scores(d.rows), dense_ref(d.rows, std::vector<double>(d.dv,0.0));
        std::vector<std::vector<uint32_t>> fresh_supports(d.rows);
        std::vector<double> s,p,out(d.dv,0.0);
        for (uint64_t r=0;r<d.rows;++r) { compute_scores_probs(d,r,s,p); dense_scores[r]=s; dense_probs[r]=p; dense_from_probs(d,r,p,dense_ref[r]); fresh_supports[r]=histogram_mass_select(p,target,bins); }
        auto groups = make_groups(d.group_example);

        Agg fresh_a, raw_a, cert_a; EvalExtras raw_e, cert_e;
        for (uint64_t r=0;r<d.rows;++r) add(fresh_a, sparse_from_probs_selected(d,r,dense_probs[r],fresh_supports[r],out,&dense_ref[r]));
        for (const auto& g: groups) {
            uint64_t anchor = g.front(); const auto& support = fresh_supports[anchor];
            for (uint64_t r: g) {
                if (r == anchor) { add(raw_a, sparse_from_probs_selected(d,r,dense_probs[r],support,out,&dense_ref[r])); raw_e.qk += d.n; }
                else { add(raw_a, sparse_from_selected_qk_only(d,r,support,out,&dense_ref[r],&dense_probs[r])); raw_e.reused++; raw_e.qk += support.size(); }
            }
        }
        for (const auto& g: groups) {
            uint64_t anchor = g.front(); const auto& support = fresh_supports[anchor];
            for (uint64_t r: g) {
                if (r == anchor) { add(cert_a, sparse_from_probs_selected(d,r,dense_probs[r],support,out,&dense_ref[r])); cert_e.qk += d.n; }
                else {
                    cert_e.candidates++; Cert c = certify_reuse(d, anchor, r, dense_scores[anchor], support, target);
                    cert_e.lower_mass += c.lower_mass; cert_e.bound_scans += static_cast<double>(d.n - support.size());
                    if (c.ok) {
                        auto rr = sparse_from_selected_qk_only(d,r,support,out,&dense_ref[r],&dense_probs[r]); add(cert_a, rr); cert_e.reused++; cert_e.qk += support.size(); if (!rr.quality) cert_e.false_cert++;
                    } else {
                        add(cert_a, sparse_from_probs_selected(d,r,dense_probs[r],fresh_supports[r],out,&dense_ref[r])); cert_e.fallback++; cert_e.qk += d.n;
                    }
                }
            }
        }

        auto dense_row = [&](uint64_t r, std::vector<double>& outv){ std::vector<double> ss,pp; compute_scores_probs(d,r,ss,pp); dense_from_probs(d,r,pp,outv); RowResult rr; rr.selected=d.n; rr.mass=1.0; rr.quality=true; return rr; };
        auto fresh_row = [&](uint64_t r, std::vector<double>& outv){ std::vector<double> ss,pp; compute_scores_probs(d,r,ss,pp); auto sel=histogram_mass_select(pp,target,bins); return sparse_from_probs_selected(d,r,pp,sel,outv,nullptr); };
        (void)time_path(d, 2, dense_row); (void)time_path(d, 2, fresh_row);
        Timing dense_t = time_path(d,repeats,dense_row);
        Timing fresh_t = time_path(d,repeats,fresh_row);

        auto time_group_raw = [&]() {
            volatile double guard=0.0; std::vector<double> outv(d.dv,0.0), ss, pp;
            auto t0=std::chrono::steady_clock::now();
            for (int rep=0; rep<repeats; ++rep) for (const auto& g: groups) {
                uint64_t anchor=g.front(); compute_scores_probs(d,anchor,ss,pp); auto support=histogram_mass_select(pp,target,bins);
                auto rr0=sparse_from_probs_selected(d,anchor,pp,support,outv,nullptr); guard += (outv[(anchor+rep)%outv.size()] + 1e-9*rr0.selected)*1e-12;
                for (size_t gi=1; gi<g.size(); ++gi) { uint64_t r=g[gi]; auto rr=sparse_from_selected_qk_only(d,r,support,outv,nullptr,nullptr); guard += (outv[(r+rep)%outv.size()] + 1e-9*rr.selected)*1e-12; }
            }
            auto t1=std::chrono::steady_clock::now(); return Timing{std::chrono::duration<double,std::milli>(t1-t0).count(), static_cast<double>(guard)};
        };
        auto time_group_cert = [&]() {
            volatile double guard=0.0; std::vector<double> outv(d.dv,0.0), ss, pp, ff_s, ff_p;
            auto t0=std::chrono::steady_clock::now();
            for (int rep=0; rep<repeats; ++rep) for (const auto& g: groups) {
                uint64_t anchor=g.front(); compute_scores_probs(d,anchor,ss,pp); auto support=histogram_mass_select(pp,target,bins);
                auto rr0=sparse_from_probs_selected(d,anchor,pp,support,outv,nullptr); guard += (outv[(anchor+rep)%outv.size()] + 1e-9*rr0.selected)*1e-12;
                for (size_t gi=1; gi<g.size(); ++gi) { uint64_t r=g[gi]; Cert c=certify_reuse(d,anchor,r,ss,support,target); RowResult rr; if (c.ok) rr=sparse_from_selected_qk_only(d,r,support,outv,nullptr,nullptr); else { compute_scores_probs(d,r,ff_s,ff_p); auto sel=histogram_mass_select(ff_p,target,bins); rr=sparse_from_probs_selected(d,r,ff_p,sel,outv,nullptr); } guard += (outv[(r+rep)%outv.size()] + 1e-9*rr.selected)*1e-12; }
            }
            auto t1=std::chrono::steady_clock::now(); return Timing{std::chrono::duration<double,std::milli>(t1-t0).count(), static_cast<double>(guard)};
        };
        Timing raw_t = time_group_raw();
        Timing cert_t = time_group_cert();
        double total_dense_qk = static_cast<double>(d.rows)*static_cast<double>(d.n);
        std::cout << std::setprecision(12) << "{\n";
        std::cout << "\"rows\":" << d.rows << ",\"n_tokens\":" << d.n << ",\"d_key\":" << d.dk << ",\"d_value\":" << d.dv << ",\"repeats\":" << repeats << ",\"target_mass\":" << target << ",\"hist_bins\":" << bins << ",\n";
        std::cout << "\"groups\":{\"example_groups\":" << groups.size() << "},\n";
        std::cout << "\"timing\":{\"dense_qk_online_ms\":" << dense_t.ms << ",\"fresh_hist_index_ms\":" << fresh_t.ms << ",\"uncertified_anchor_reuse_ms\":" << raw_t.ms << ",\"certified_anchor_reuse_ms\":" << cert_t.ms << "},\n";
        std::cout << "\"speedups_vs_dense\":{\"fresh_hist_index\":" << speedup(dense_t.ms,fresh_t.ms) << ",\"uncertified_anchor_reuse\":" << speedup(dense_t.ms,raw_t.ms) << ",\"certified_anchor_reuse\":" << speedup(dense_t.ms,cert_t.ms) << "},\n";
        std::cout << "\"all_rows\":{\"fresh_hist_index\":"; emit_agg(fresh_a,d.n); std::cout << ",\"uncertified_anchor_reuse\":"; emit_agg(raw_a,d.n); std::cout << ",\"certified_anchor_reuse\":"; emit_agg(cert_a,d.n); std::cout << "},\n";
        std::cout << "\"certificate\":{"
                  << "\"observable_q_key_bound\":true,"
                  << "\"uses_query_distance\":true,\"uses_key_norms\":true,\"uses_key_drift_norms\":true,"
                  << "\"uses_values\":false,\"uses_dense_outputs\":false,"
                  << "\"candidate_reuse_rows\":" << cert_e.candidates << ","
                  << "\"certified_reuse_rows\":" << cert_e.reused << ","
                  << "\"fallback_rows\":" << cert_e.fallback << ","
                  << "\"false_certified_quality_failures\":" << cert_e.false_cert << ","
                  << "\"certified_reuse_rate\":" << (cert_e.candidates ? static_cast<double>(cert_e.reused)/cert_e.candidates : 0.0) << ","
                  << "\"fallback_rate\":" << (cert_e.candidates ? static_cast<double>(cert_e.fallback)/cert_e.candidates : 0.0) << ","
                  << "\"mean_certified_lower_mass_over_candidates\":" << (cert_e.candidates ? cert_e.lower_mass/cert_e.candidates : 0.0) << "},\n";
        std::cout << "\"accounting\":{"
                  << "\"fallback_paid_in_timed_loop\":true,\"certificate_bound_paid_in_timed_loop\":true,"
                  << "\"uncertified_qk_dot_fraction\":" << raw_e.qk/total_dense_qk << ","
                  << "\"certified_qk_dot_fraction\":" << cert_e.qk/total_dense_qk << ","
                  << "\"certified_bound_metadata_scan_fraction\":" << cert_e.bound_scans/total_dense_qk << ","
                  << "\"fresh_hist_qk_dot_fraction\":1.0,"
                  << "\"all_paths_local_cpu_only\":true,\"public_pretrained_trace_loaded\":false,\"gpu_fused_kernel_measured\":false"
                  << "}\n";
        std::cout << "}\n";
    } catch (const std::exception& e) { std::cerr << "error: " << e.what() << "\n"; return 1; }
    return 0;
}
