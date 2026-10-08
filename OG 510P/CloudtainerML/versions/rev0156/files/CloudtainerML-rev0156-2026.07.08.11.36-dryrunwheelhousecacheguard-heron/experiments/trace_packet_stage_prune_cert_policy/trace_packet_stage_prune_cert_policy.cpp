#include <algorithm>
#include <cassert>
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
#include <stdexcept>
#include <string>
#include <vector>

struct Data {
    uint64_t rows=0, n=0, dk=0, dv=0;
    std::vector<double> q, k, v;
    std::vector<int32_t> group_example;
};

static void read_exact(std::ifstream& f, char* p, size_t n) {
    f.read(p, static_cast<std::streamsize>(n));
    if (!f) throw std::runtime_error("short read");
}

template <typename T> static void read_vec(std::ifstream& f, std::vector<T>& x, size_t n) {
    x.resize(n);
    read_exact(f, reinterpret_cast<char*>(x.data()), sizeof(T)*n);
}

static Data load_bin(const std::string& path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) throw std::runtime_error("cannot open input");
    char magic[8]; read_exact(f, magic, 8);
    if (std::memcmp(magic, "CTMLTR71", 8) != 0) throw std::runtime_error("bad magic");
    Data d;
    read_exact(f, reinterpret_cast<char*>(&d.rows), sizeof(uint64_t));
    read_exact(f, reinterpret_cast<char*>(&d.n), sizeof(uint64_t));
    read_exact(f, reinterpret_cast<char*>(&d.dk), sizeof(uint64_t));
    read_exact(f, reinterpret_cast<char*>(&d.dv), sizeof(uint64_t));
    read_vec(f, d.q, static_cast<size_t>(d.rows*d.dk));
    read_vec(f, d.k, static_cast<size_t>(d.rows*d.n*d.dk));
    read_vec(f, d.v, static_cast<size_t>(d.rows*d.n*d.dv));
    read_vec(f, d.group_example, static_cast<size_t>(d.rows));
    return d;
}

static inline double qk_score(const Data& d, uint64_t r, uint64_t i) {
    const double* q = d.q.data() + r*d.dk;
    const double* k = d.k.data() + (r*d.n+i)*d.dk;
    double s=0.0;
    for (uint64_t j=0;j<d.dk;++j) s += q[j]*k[j];
    return s/std::sqrt(static_cast<double>(d.dk));
}

static inline double q_norm(const Data& d, uint64_t r) {
    const double* q = d.q.data() + r*d.dk;
    double s=0.0; for (uint64_t j=0;j<d.dk;++j) s += q[j]*q[j];
    return std::sqrt(s);
}

static inline double q_distance(const Data& d, uint64_t a, uint64_t r) {
    const double* qa = d.q.data() + a*d.dk;
    const double* qr = d.q.data() + r*d.dk;
    double s=0.0; for (uint64_t j=0;j<d.dk;++j) { double x=qr[j]-qa[j]; s += x*x; }
    return std::sqrt(s);
}

static inline double key_norm_i(const Data& d, uint64_t r, uint64_t i) {
    const double* k = d.k.data() + (r*d.n+i)*d.dk;
    double s=0.0; for (uint64_t j=0;j<d.dk;++j) s += k[j]*k[j];
    return std::sqrt(s);
}

static inline double key_drift_norm_i(const Data& d, uint64_t a, uint64_t r, uint64_t i) {
    const double* ka = d.k.data() + (a*d.n+i)*d.dk;
    const double* kr = d.k.data() + (r*d.n+i)*d.dk;
    double s=0.0; for (uint64_t j=0;j<d.dk;++j) { double x=kr[j]-ka[j]; s += x*x; }
    return std::sqrt(s);
}

static void compute_scores_probs(const Data& d, uint64_t r, std::vector<double>& scores, std::vector<double>& probs) {
    scores.assign(static_cast<size_t>(d.n), 0.0);
    double mx=-1e300;
    for (uint64_t i=0;i<d.n;++i) { double s=qk_score(d,r,i); scores[static_cast<size_t>(i)] = s; mx = std::max(mx, s); }
    probs.assign(static_cast<size_t>(d.n), 0.0);
    double z=0.0;
    for (uint64_t i=0;i<d.n;++i) { double e=std::exp(std::max(-80.0, std::min(0.0, scores[static_cast<size_t>(i)]-mx))); probs[static_cast<size_t>(i)] = e; z += e; }
    for (double& p: probs) p /= std::max(1e-300, z);
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
        const double p = probs[static_cast<size_t>(i)];
        const double* vi = vals + i*d.dv;
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

struct Sidecar {
    uint64_t B=0, block_size=0;
    std::vector<double> max_key_norm_all;             // rows
    std::vector<double> max_key_norm_block;           // rows*B
    std::vector<double> max_drift_all;                // rows*rows
    std::vector<double> max_drift_block;              // rows*rows*B
    double build_ms=0.0;
};

static inline size_t idx_rb(uint64_t r, uint64_t b, uint64_t B) { return static_cast<size_t>(r*B+b); }
static inline size_t idx_rr(uint64_t a, uint64_t r, uint64_t rows) { return static_cast<size_t>(a*rows+r); }
static inline size_t idx_rrb(uint64_t a, uint64_t r, uint64_t b, uint64_t rows, uint64_t B) { return static_cast<size_t>((a*rows+r)*B+b); }

static Sidecar build_sidecar(const Data& d, uint64_t block_size) {
    Sidecar sc; sc.block_size=std::max<uint64_t>(1, block_size); sc.B=(d.n+sc.block_size-1)/sc.block_size;
    auto t0=std::chrono::steady_clock::now();
    sc.max_key_norm_all.assign(static_cast<size_t>(d.rows), 0.0);
    sc.max_key_norm_block.assign(static_cast<size_t>(d.rows*sc.B), 0.0);
    for (uint64_t r=0;r<d.rows;++r) for (uint64_t i=0;i<d.n;++i) {
        uint64_t b=i/sc.block_size; double kn=key_norm_i(d,r,i);
        sc.max_key_norm_all[static_cast<size_t>(r)] = std::max(sc.max_key_norm_all[static_cast<size_t>(r)], kn);
        sc.max_key_norm_block[idx_rb(r,b,sc.B)] = std::max(sc.max_key_norm_block[idx_rb(r,b,sc.B)], kn);
    }
    sc.max_drift_all.assign(static_cast<size_t>(d.rows*d.rows), 0.0);
    sc.max_drift_block.assign(static_cast<size_t>(d.rows*d.rows*sc.B), 0.0);
    for (uint64_t a=0;a<d.rows;++a) for (uint64_t r=0;r<d.rows;++r) {
        double mall=0.0;
        for (uint64_t i=0;i<d.n;++i) {
            uint64_t b=i/sc.block_size; double dn=key_drift_norm_i(d,a,r,i);
            mall=std::max(mall,dn);
            auto ix=idx_rrb(a,r,b,d.rows,sc.B); sc.max_drift_block[ix]=std::max(sc.max_drift_block[ix],dn);
        }
        sc.max_drift_all[idx_rr(a,r,d.rows)] = mall;
    }
    auto t1=std::chrono::steady_clock::now();
    sc.build_ms=std::chrono::duration<double,std::milli>(t1-t0).count();
    return sc;
}

struct AnchorCache {
    std::vector<double> scores, probs;
    std::vector<uint32_t> support;
    std::vector<char> in;
    int outside_count=0;
    double max_anchor_outside=-1e300;
    std::vector<double> max_anchor_outside_block;
    std::vector<int> outside_count_block;
};

static AnchorCache make_anchor_cache(const Data& d, const Sidecar& sc, uint64_t anchor, double target, int bins) {
    AnchorCache ac; compute_scores_probs(d,anchor,ac.scores,ac.probs); ac.support=histogram_mass_select(ac.probs,target,bins);
    ac.in.assign(static_cast<size_t>(d.n), 0); for (uint32_t i:ac.support) ac.in[static_cast<size_t>(i)]=1;
    ac.max_anchor_outside_block.assign(static_cast<size_t>(sc.B), -1e300);
    ac.outside_count_block.assign(static_cast<size_t>(sc.B), 0);
    for (uint64_t i=0;i<d.n;++i) if (!ac.in[static_cast<size_t>(i)]) {
        uint64_t b=i/sc.block_size; ac.outside_count++; ac.max_anchor_outside=std::max(ac.max_anchor_outside, ac.scores[static_cast<size_t>(i)]);
        ac.max_anchor_outside_block[static_cast<size_t>(b)] = std::max(ac.max_anchor_outside_block[static_cast<size_t>(b)], ac.scores[static_cast<size_t>(i)]);
        ac.outside_count_block[static_cast<size_t>(b)]++;
    }
    if (ac.outside_count==0) ac.max_anchor_outside=-1e300;
    return ac;
}

struct Cert {
    bool ok=false;
    int stage=0;              // 0 fail/fallback, 1 scalar, 2 block, 3 token
    double lower_mass=0.0;
    double qk_dots=0.0;
    double scalar_sidecar_reads=0.0;
    double block_sidecar_reads=0.0;
    double token_bound_scans=0.0;
};

static std::vector<double> selected_scores_for(const Data& d, uint64_t r, const std::vector<uint32_t>& support, double& mx) {
    std::vector<double> ss; ss.reserve(support.size()); mx=-1e300;
    for (uint32_t i:support) { double s=qk_score(d,r,i); ss.push_back(s); mx=std::max(mx,s); }
    return ss;
}

static Cert certify_token_scan(const Data& d, uint64_t anchor, uint64_t r, const AnchorCache& ac, double target) {
    Cert c; c.stage=3;
    double mx; auto selected_scores = selected_scores_for(d,r,ac.support,mx); c.qk_dots += static_cast<double>(ac.support.size());
    const double qd=q_distance(d,anchor,r), qan=q_norm(d,anchor), inv=1.0/std::sqrt(static_cast<double>(d.dk));
    std::vector<double> outside_ubs; outside_ubs.reserve(static_cast<size_t>(std::max(0,ac.outside_count)));
    for (uint64_t i=0;i<d.n;++i) if (!ac.in[static_cast<size_t>(i)]) {
        double ub = ac.scores[static_cast<size_t>(i)] + (qd*key_norm_i(d,r,i) + qan*key_drift_norm_i(d,anchor,r,i))*inv;
        outside_ubs.push_back(ub); mx=std::max(mx,ub); c.token_bound_scans += 1.0;
    }
    double zsel=0.0,zout=0.0;
    for (double s:selected_scores) zsel += std::exp(std::max(-80.0,std::min(0.0,s-mx)));
    for (double ub:outside_ubs) zout += std::exp(std::max(-80.0,std::min(0.0,ub-mx)));
    c.lower_mass=zsel/std::max(1e-300,zsel+zout); c.ok = c.lower_mass>=target; return c;
}

static Cert certify_scalar_only(const Data& d, const Sidecar& sc, uint64_t anchor, uint64_t r, const AnchorCache& ac, double target) {
    Cert c; double mx_sel; auto selected_scores=selected_scores_for(d,r,ac.support,mx_sel); c.qk_dots += static_cast<double>(ac.support.size());
    if (ac.outside_count==0) { c.ok=true; c.stage=1; c.lower_mass=1.0; return c; }
    const double qd=q_distance(d,anchor,r), qan=q_norm(d,anchor), inv=1.0/std::sqrt(static_cast<double>(d.dk));
    c.scalar_sidecar_reads += 2.0; // row max key norm + row/anchor max key-drift scalar
    double ub_all = ac.max_anchor_outside + (qd*sc.max_key_norm_all[static_cast<size_t>(r)] + qan*sc.max_drift_all[idx_rr(anchor,r,d.rows)])*inv;
    double mx=std::max(mx_sel, ub_all);
    double zsel=0.0; for (double s:selected_scores) zsel += std::exp(std::max(-80.0,std::min(0.0,s-mx)));
    double zout=static_cast<double>(ac.outside_count)*std::exp(std::max(-80.0,std::min(0.0,ub_all-mx)));
    c.lower_mass=zsel/std::max(1e-300,zsel+zout);
    if (c.lower_mass>=target) { c.ok=true; c.stage=1; return c; }
    c.ok=false; c.stage=0; return c;
}

static Cert certify_two_stage(const Data& d, const Sidecar& sc, uint64_t anchor, uint64_t r, const AnchorCache& ac, double target) {
    Cert c; double mx_sel; auto selected_scores=selected_scores_for(d,r,ac.support,mx_sel); c.qk_dots += static_cast<double>(ac.support.size());
    if (ac.outside_count==0) { c.ok=true; c.stage=1; c.lower_mass=1.0; return c; }
    const double qd=q_distance(d,anchor,r), qan=q_norm(d,anchor), inv=1.0/std::sqrt(static_cast<double>(d.dk));
    c.scalar_sidecar_reads += 2.0; // row max key norm + row/anchor max key-drift scalar
    double ub_all = ac.max_anchor_outside + (qd*sc.max_key_norm_all[static_cast<size_t>(r)] + qan*sc.max_drift_all[idx_rr(anchor,r,d.rows)])*inv;
    double mx=std::max(mx_sel, ub_all);
    double zsel=0.0; for (double s:selected_scores) zsel += std::exp(std::max(-80.0,std::min(0.0,s-mx)));
    double zout=static_cast<double>(ac.outside_count)*std::exp(std::max(-80.0,std::min(0.0,ub_all-mx)));
    c.lower_mass=zsel/std::max(1e-300,zsel+zout);
    if (c.lower_mass>=target) { c.ok=true; c.stage=1; return c; }
    // Block sidecar refinement. One norm and one drift read per outside-bearing block.
    std::vector<double> ubs; std::vector<int> cnts; ubs.reserve(static_cast<size_t>(sc.B)); cnts.reserve(static_cast<size_t>(sc.B));
    mx=mx_sel; zsel=0.0;
    for (uint64_t b=0;b<sc.B;++b) {
        int cnt=ac.outside_count_block[static_cast<size_t>(b)]; if (cnt<=0) continue;
        double ub = ac.max_anchor_outside_block[static_cast<size_t>(b)] + (qd*sc.max_key_norm_block[idx_rb(r,b,sc.B)] + qan*sc.max_drift_block[idx_rrb(anchor,r,b,d.rows,sc.B)])*inv;
        ubs.push_back(ub); cnts.push_back(cnt); mx=std::max(mx,ub); c.block_sidecar_reads += 2.0;
    }
    for (double s:selected_scores) zsel += std::exp(std::max(-80.0,std::min(0.0,s-mx)));
    zout=0.0; for (size_t j=0;j<ubs.size();++j) zout += static_cast<double>(cnts[j])*std::exp(std::max(-80.0,std::min(0.0,ubs[j]-mx)));
    c.lower_mass=zsel/std::max(1e-300,zsel+zout);
    if (c.lower_mass>=target) { c.ok=true; c.stage=2; return c; }
    c.ok=false; c.stage=0; return c;
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

struct EvalExtras { int reused=0, fallback=0, candidates=0, false_cert=0, scalar=0, block=0, token=0; double lower_mass=0.0; double qk=0.0; double scalar_reads=0.0; double block_reads=0.0; double token_scans=0.0; };
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
    if (argc < 6) { std::cerr << "usage: trace_packet_stage_prune_cert_policy <input.bin> <repeats> <target_mass> <hist_bins> <block_size>\n"; return 2; }
    try {
        Data d=load_bin(argv[1]); int repeats=std::max(1,std::stoi(argv[2])); double target=std::stod(argv[3]); int bins=std::max(2,std::stoi(argv[4])); uint64_t block_size=std::max(1,std::stoi(argv[5]));
        Sidecar sc=build_sidecar(d,block_size);
        std::vector<std::vector<double>> dense_probs(d.rows), dense_scores(d.rows), dense_ref(d.rows, std::vector<double>(d.dv,0.0));
        std::vector<std::vector<uint32_t>> fresh_supports(d.rows);
        std::vector<double> s,p,out(d.dv,0.0);
        for (uint64_t r=0;r<d.rows;++r) { compute_scores_probs(d,r,s,p); dense_scores[r]=s; dense_probs[r]=p; dense_from_probs(d,r,p,dense_ref[r]); fresh_supports[r]=histogram_mass_select(p,target,bins); }
        auto groups=make_groups(d.group_example);

        Agg fresh_a, raw_a, token_a, scalar_a, two_a; EvalExtras raw_e, token_e, scalar_e, two_e;
        for (uint64_t r=0;r<d.rows;++r) add(fresh_a, sparse_from_probs_selected(d,r,dense_probs[r],fresh_supports[r],out,&dense_ref[r]));
        for (const auto& g:groups) {
            uint64_t anchor=g.front(); AnchorCache ac=make_anchor_cache(d,sc,anchor,target,bins);
            for (uint64_t r:g) {
                if (r==anchor) { add(raw_a, sparse_from_probs_selected(d,r,dense_probs[r],ac.support,out,&dense_ref[r])); raw_e.qk += d.n; }
                else { auto rr=sparse_from_selected_qk_only(d,r,ac.support,out,&dense_ref[r],&dense_probs[r]); add(raw_a,rr); raw_e.reused++; raw_e.qk += ac.support.size(); }
            }
        }
        for (const auto& g:groups) {
            uint64_t anchor=g.front(); AnchorCache ac=make_anchor_cache(d,sc,anchor,target,bins);
            for (uint64_t r:g) {
                if (r==anchor) { add(token_a, sparse_from_probs_selected(d,r,dense_probs[r],ac.support,out,&dense_ref[r])); token_e.qk += d.n; }
                else { token_e.candidates++; Cert c=certify_token_scan(d,anchor,r,ac,target); token_e.lower_mass += c.lower_mass; token_e.qk += c.qk_dots; token_e.token_scans += c.token_bound_scans; RowResult rr; if (c.ok) { rr=sparse_from_selected_qk_only(d,r,ac.support,out,&dense_ref[r],&dense_probs[r]); token_e.reused++; token_e.token++; if (!rr.quality) token_e.false_cert++; } else { rr=sparse_from_probs_selected(d,r,dense_probs[r],fresh_supports[r],out,&dense_ref[r]); token_e.fallback++; token_e.qk += d.n; } add(token_a,rr); }
            }
        }
        for (const auto& g:groups) {
            uint64_t anchor=g.front(); AnchorCache ac=make_anchor_cache(d,sc,anchor,target,bins);
            for (uint64_t r:g) {
                if (r==anchor) { add(scalar_a, sparse_from_probs_selected(d,r,dense_probs[r],ac.support,out,&dense_ref[r])); scalar_e.qk += d.n; }
                else { scalar_e.candidates++; Cert c=certify_scalar_only(d,sc,anchor,r,ac,target); scalar_e.lower_mass += c.lower_mass; scalar_e.qk += c.qk_dots; scalar_e.scalar_reads += c.scalar_sidecar_reads; RowResult rr; if (c.ok) { rr=sparse_from_selected_qk_only(d,r,ac.support,out,&dense_ref[r],&dense_probs[r]); scalar_e.reused++; scalar_e.scalar++; if (!rr.quality) scalar_e.false_cert++; } else { rr=sparse_from_probs_selected(d,r,dense_probs[r],fresh_supports[r],out,&dense_ref[r]); scalar_e.fallback++; scalar_e.qk += d.n; } add(scalar_a,rr); }
            }
        }
        for (const auto& g:groups) {
            uint64_t anchor=g.front(); AnchorCache ac=make_anchor_cache(d,sc,anchor,target,bins);
            for (uint64_t r:g) {
                if (r==anchor) { add(two_a, sparse_from_probs_selected(d,r,dense_probs[r],ac.support,out,&dense_ref[r])); two_e.qk += d.n; }
                else { two_e.candidates++; Cert c=certify_two_stage(d,sc,anchor,r,ac,target); two_e.lower_mass += c.lower_mass; two_e.qk += c.qk_dots; two_e.scalar_reads += c.scalar_sidecar_reads; two_e.block_reads += c.block_sidecar_reads; RowResult rr; if (c.ok) { rr=sparse_from_selected_qk_only(d,r,ac.support,out,&dense_ref[r],&dense_probs[r]); two_e.reused++; if (c.stage==1) two_e.scalar++; else if (c.stage==2) two_e.block++; if (!rr.quality) two_e.false_cert++; } else { rr=sparse_from_probs_selected(d,r,dense_probs[r],fresh_supports[r],out,&dense_ref[r]); two_e.fallback++; two_e.qk += d.n; } add(two_a,rr); }
            }
        }

        auto dense_row = [&](uint64_t r, std::vector<double>& outv){ std::vector<double> ss,pp; compute_scores_probs(d,r,ss,pp); dense_from_probs(d,r,pp,outv); RowResult rr; rr.selected=d.n; rr.mass=1.0; rr.quality=true; return rr; };
        auto fresh_row = [&](uint64_t r, std::vector<double>& outv){ std::vector<double> ss,pp; compute_scores_probs(d,r,ss,pp); auto sel=histogram_mass_select(pp,target,bins); return sparse_from_probs_selected(d,r,pp,sel,outv,nullptr); };
        (void)time_path(d,2,dense_row); (void)time_path(d,2,fresh_row);
        Timing dense_t=time_path(d,repeats,dense_row); Timing fresh_t=time_path(d,repeats,fresh_row);

        auto time_group_raw = [&]() {
            volatile double guard=0.0; std::vector<double> outv(d.dv,0.0), ss, pp;
            auto t0=std::chrono::steady_clock::now();
            for (int rep=0; rep<repeats; ++rep) for (const auto& g:groups) {
                uint64_t anchor=g.front(); compute_scores_probs(d,anchor,ss,pp); auto support=histogram_mass_select(pp,target,bins);
                auto rr0=sparse_from_probs_selected(d,anchor,pp,support,outv,nullptr); guard += (outv[(anchor+rep)%outv.size()] + 1e-9*rr0.selected)*1e-12;
                for (size_t gi=1; gi<g.size(); ++gi) { uint64_t r=g[gi]; auto rr=sparse_from_selected_qk_only(d,r,support,outv,nullptr,nullptr); guard += (outv[(r+rep)%outv.size()] + 1e-9*rr.selected)*1e-12; }
            }
            auto t1=std::chrono::steady_clock::now(); return Timing{std::chrono::duration<double,std::milli>(t1-t0).count(), static_cast<double>(guard)};
        };
        auto time_group_token = [&]() {
            volatile double guard=0.0; std::vector<double> outv(d.dv,0.0), ff_s, ff_p;
            auto t0=std::chrono::steady_clock::now();
            for (int rep=0; rep<repeats; ++rep) for (const auto& g:groups) {
                uint64_t anchor=g.front(); AnchorCache ac=make_anchor_cache(d,sc,anchor,target,bins);
                auto rr0=sparse_from_probs_selected(d,anchor,ac.probs,ac.support,outv,nullptr); guard += (outv[(anchor+rep)%outv.size()] + 1e-9*rr0.selected)*1e-12;
                for (size_t gi=1; gi<g.size(); ++gi) { uint64_t r=g[gi]; Cert c=certify_token_scan(d,anchor,r,ac,target); RowResult rr; if (c.ok) rr=sparse_from_selected_qk_only(d,r,ac.support,outv,nullptr,nullptr); else { compute_scores_probs(d,r,ff_s,ff_p); auto sel=histogram_mass_select(ff_p,target,bins); rr=sparse_from_probs_selected(d,r,ff_p,sel,outv,nullptr); } guard += (outv[(r+rep)%outv.size()] + 1e-9*rr.selected)*1e-12; }
            }
            auto t1=std::chrono::steady_clock::now(); return Timing{std::chrono::duration<double,std::milli>(t1-t0).count(), static_cast<double>(guard)};
        };
        auto time_group_scalar = [&]() {
            volatile double guard=0.0; std::vector<double> outv(d.dv,0.0), ff_s, ff_p;
            auto t0=std::chrono::steady_clock::now();
            for (int rep=0; rep<repeats; ++rep) for (const auto& g:groups) {
                uint64_t anchor=g.front(); AnchorCache ac=make_anchor_cache(d,sc,anchor,target,bins);
                auto rr0=sparse_from_probs_selected(d,anchor,ac.probs,ac.support,outv,nullptr); guard += (outv[(anchor+rep)%outv.size()] + 1e-9*rr0.selected)*1e-12;
                for (size_t gi=1; gi<g.size(); ++gi) { uint64_t r=g[gi]; Cert c=certify_scalar_only(d,sc,anchor,r,ac,target); RowResult rr; if (c.ok) rr=sparse_from_selected_qk_only(d,r,ac.support,outv,nullptr,nullptr); else { compute_scores_probs(d,r,ff_s,ff_p); auto sel=histogram_mass_select(ff_p,target,bins); rr=sparse_from_probs_selected(d,r,ff_p,sel,outv,nullptr); } guard += (outv[(r+rep)%outv.size()] + 1e-9*rr.selected)*1e-12; }
            }
            auto t1=std::chrono::steady_clock::now(); return Timing{std::chrono::duration<double,std::milli>(t1-t0).count(), static_cast<double>(guard)};
        };
        auto time_group_two = [&]() {
            volatile double guard=0.0; std::vector<double> outv(d.dv,0.0), ff_s, ff_p;
            auto t0=std::chrono::steady_clock::now();
            for (int rep=0; rep<repeats; ++rep) for (const auto& g:groups) {
                uint64_t anchor=g.front(); AnchorCache ac=make_anchor_cache(d,sc,anchor,target,bins);
                auto rr0=sparse_from_probs_selected(d,anchor,ac.probs,ac.support,outv,nullptr); guard += (outv[(anchor+rep)%outv.size()] + 1e-9*rr0.selected)*1e-12;
                for (size_t gi=1; gi<g.size(); ++gi) { uint64_t r=g[gi]; Cert c=certify_two_stage(d,sc,anchor,r,ac,target); RowResult rr; if (c.ok) rr=sparse_from_selected_qk_only(d,r,ac.support,outv,nullptr,nullptr); else { compute_scores_probs(d,r,ff_s,ff_p); auto sel=histogram_mass_select(ff_p,target,bins); rr=sparse_from_probs_selected(d,r,ff_p,sel,outv,nullptr); } guard += (outv[(r+rep)%outv.size()] + 1e-9*rr.selected)*1e-12; }
            }
            auto t1=std::chrono::steady_clock::now(); return Timing{std::chrono::duration<double,std::milli>(t1-t0).count(), static_cast<double>(guard)};
        };
        Timing raw_t=time_group_raw(); Timing token_t=time_group_token(); Timing scalar_t=time_group_scalar(); Timing two_t=time_group_two();
        const double total_dense_qk=static_cast<double>(d.rows)*static_cast<double>(d.n);
        const double total_candidate_rows=std::max(1, two_e.candidates);
        std::cout << std::setprecision(12) << "{\n";
        std::cout << "\"rows\":"<<d.rows<<",\"n_tokens\":"<<d.n<<",\"d_key\":"<<d.dk<<",\"d_value\":"<<d.dv<<",\"repeats\":"<<repeats<<",\"target_mass\":"<<target<<",\"hist_bins\":"<<bins<<",\"block_size\":"<<block_size<<",\"blocks\":"<<sc.B<<",\n";
        std::cout << "\"groups\":{\"example_groups\":"<<groups.size()<<"},\n";
        std::cout << "\"sidecar\":{\"built_from_key_cache\":true,\"uses_values\":false,\"uses_dense_outputs\":false,\"build_ms\":"<<sc.build_ms<<",\"scalar_sidecar_fields_per_candidate\":2,\"block_sidecar_fields_per_block\":2},\n";
        std::cout << "\"timing\":{\"dense_qk_online_ms\":"<<dense_t.ms<<",\"fresh_hist_index_ms\":"<<fresh_t.ms<<",\"uncertified_anchor_reuse_ms\":"<<raw_t.ms<<",\"full_token_certificate_ms\":"<<token_t.ms<<",\"scalar_only_certificate_ms\":"<<scalar_t.ms<<",\"two_stage_certificate_ms\":"<<two_t.ms<<"},\n";
        std::cout << "\"speedups_vs_dense\":{\"fresh_hist_index\":"<<speedup(dense_t.ms,fresh_t.ms)<<",\"uncertified_anchor_reuse\":"<<speedup(dense_t.ms,raw_t.ms)<<",\"full_token_certificate\":"<<speedup(dense_t.ms,token_t.ms)<<",\"scalar_only_certificate\":"<<speedup(dense_t.ms,scalar_t.ms)<<",\"two_stage_certificate\":"<<speedup(dense_t.ms,two_t.ms)<<"},\n";
        std::cout << "\"all_rows\":{\"fresh_hist_index\":"; emit_agg(fresh_a,d.n); std::cout << ",\"uncertified_anchor_reuse\":"; emit_agg(raw_a,d.n); std::cout << ",\"full_token_certificate\":"; emit_agg(token_a,d.n); std::cout << ",\"scalar_only_certificate\":"; emit_agg(scalar_a,d.n); std::cout << ",\"two_stage_certificate\":"; emit_agg(two_a,d.n); std::cout << "},\n";
        std::cout << "\"certificate\":{"
                  << "\"observable_q_key_bound\":true,\"uses_query_distance\":true,\"uses_key_norms\":true,\"uses_key_drift_norms\":true,\"uses_values\":false,\"uses_dense_outputs\":false,"
                  << "\"candidate_reuse_rows\":"<<two_e.candidates<<","
                  << "\"scalar_only_certified_reuse_rows\":"<<scalar_e.reused<<","
                  << "\"scalar_only_fallback_rows\":"<<scalar_e.fallback<<","
                  << "\"scalar_only_false_certified_quality_failures\":"<<scalar_e.false_cert<<","
                  << "\"two_stage_scalar_certified_rows\":"<<two_e.scalar<<","
                  << "\"two_stage_block_certified_rows\":"<<two_e.block<<","
                  << "\"two_stage_certified_reuse_rows\":"<<two_e.reused<<","
                  << "\"two_stage_fallback_rows\":"<<two_e.fallback<<","
                  << "\"full_token_certified_reuse_rows\":"<<token_e.reused<<","
                  << "\"full_token_fallback_rows\":"<<token_e.fallback<<","
                  << "\"two_stage_false_certified_quality_failures\":"<<two_e.false_cert<<","
                  << "\"full_token_false_certified_quality_failures\":"<<token_e.false_cert<<","
                  << "\"two_stage_certified_reuse_rate\":"<<(static_cast<double>(two_e.reused)/total_candidate_rows)<<","
                  << "\"two_stage_fallback_rate\":"<<(static_cast<double>(two_e.fallback)/total_candidate_rows)<<","
                  << "\"two_stage_scalar_share_of_certified\":"<<(two_e.reused?static_cast<double>(two_e.scalar)/two_e.reused:0.0)<<","
                  << "\"mean_two_stage_lower_mass_over_candidates\":"<<(two_e.candidates?two_e.lower_mass/two_e.candidates:0.0)<<"},\n";
        std::cout << "\"accounting\":{"
                  << "\"fallback_paid_in_timed_loop\":true,\"certificate_bound_paid_in_timed_loop\":true,\"sidecar_build_excluded_from_main_timing_but_reported\":true,"
                  << "\"uncertified_qk_dot_fraction\":"<<raw_e.qk/total_dense_qk<<","
                  << "\"fresh_hist_qk_dot_fraction\":1.0,"
                  << "\"full_token_certificate_qk_dot_fraction\":"<<token_e.qk/total_dense_qk<<","
                  << "\"scalar_only_certificate_qk_dot_fraction\":"<<scalar_e.qk/total_dense_qk<<","
                  << "\"two_stage_certificate_qk_dot_fraction\":"<<two_e.qk/total_dense_qk<<","
                  << "\"full_token_bound_scan_token_fraction\":"<<token_e.token_scans/total_dense_qk<<","
                  << "\"scalar_only_sidecar_read_fraction\":"<<scalar_e.scalar_reads/total_dense_qk<<","
                  << "\"two_stage_scalar_sidecar_read_fraction\":"<<two_e.scalar_reads/total_dense_qk<<","
                  << "\"two_stage_block_sidecar_read_fraction\":"<<two_e.block_reads/total_dense_qk<<","
                  << "\"two_stage_total_sidecar_read_fraction\":"<<(two_e.scalar_reads+two_e.block_reads)/total_dense_qk<<","
                  << "\"sidecar_vs_token_bound_read_reduction\":"<<(token_e.token_scans>0.0 ? 1.0-(two_e.scalar_reads+two_e.block_reads)/token_e.token_scans : 0.0)<<","
                  << "\"scalar_pruned_block_read_reduction_vs_two_stage\":"<<((two_e.scalar_reads+two_e.block_reads)>0.0 ? 1.0 - scalar_e.scalar_reads/(two_e.scalar_reads+two_e.block_reads) : 0.0)<<","
                  << "\"block_stage_extra_certified_rows\":"<<(two_e.block)<<","
                  << "\"all_paths_local_cpu_only\":true,\"public_pretrained_trace_loaded\":false,\"gpu_fused_kernel_measured\":false"
                  << "}\n";
        std::cout << "}\n";
    } catch (const std::exception& e) { std::cerr << "error: "<<e.what()<<"\n"; return 1; }
    return 0;
}
