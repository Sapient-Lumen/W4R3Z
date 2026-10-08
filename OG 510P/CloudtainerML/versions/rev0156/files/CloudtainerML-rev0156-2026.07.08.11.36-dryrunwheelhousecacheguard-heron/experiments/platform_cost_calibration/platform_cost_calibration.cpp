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

// rev0057 native CPU primitive cost calibration.
//
// Purpose: rev0056 showed the adaptive router only beats the dense-score
// histogram if QK dots are assigned a high proxy weight.  This microbenchmark
// measures a narrow CPU-path ratio for the exact router dimensions and for a
// wider attention-like dimension.  It is intentionally *not* a GPU/fused-kernel
// timing claim.  It prices primitive vector operations used by the proxy model:
//   - one QK dot vector over D floats;
//   - one value-vector accumulation over D floats;
//   - one sparse/gather value-vector accumulation over D floats;
//   - one block-metadata centroid dot over D floats.
//
// The wrapper combines these measured ratios with the rev0056 cost frontier.

static volatile double GLOBAL_SINK = 0.0;

struct XorShift64 {
    uint64_t x;
    explicit XorShift64(uint64_t seed) : x(seed ? seed : 0xC0FFEE123456789ull) {}
    uint64_t next_u64() {
        x ^= x << 7;
        x ^= x >> 9;
        return x;
    }
    float uniform() { return static_cast<float>((next_u64() >> 40) * (1.0 / 16777216.0)); }
    float normal() {
        float u1 = std::max(1e-7f, uniform());
        float u2 = uniform();
        return std::sqrt(-2.0f * std::log(u1)) * std::cos(6.28318530718f * u2);
    }
};

struct Measurement {
    std::string primitive;
    int seq = 0;
    int d = 0;
    int selected = 0;
    int rows = 0;
    int repeats = 0;
    double elapsed_ns = 0.0;
    double vectors = 0.0;
    double ns_per_vector = 0.0;
    double checksum = 0.0;
};

static std::string esc(const std::string& s) {
    std::string out;
    for (char c : s) {
        if (c == '"') out += "\\\"";
        else out += c;
    }
    return out;
}

struct Data {
    int seq;
    int d;
    int rows;
    int selected;
    std::vector<float> q;
    std::vector<float> k;
    std::vector<float> v;
    std::vector<float> probs;
    std::vector<int> gather;
    std::vector<float> centroids;
    std::vector<float> radii;
};

Data make_data(int seq, int d, int rows, int selected, uint64_t seed) {
    XorShift64 rng(seed);
    Data a{seq, d, rows, selected};
    a.q.resize(rows * d);
    a.k.resize(rows * seq * d);
    a.v.resize(rows * seq * d);
    a.probs.resize(rows * seq);
    a.gather.resize(rows * selected);
    int blocks = (seq + 7) / 8;
    a.centroids.resize(rows * blocks * d);
    a.radii.resize(rows * blocks);
    for (float& x : a.q) x = 0.1f * rng.normal();
    for (float& x : a.k) x = 0.1f * rng.normal();
    for (float& x : a.v) x = 0.1f * rng.normal();
    for (int r = 0; r < rows; ++r) {
        float z = 0.0f;
        for (int t = 0; t < seq; ++t) {
            float w = 0.05f + rng.uniform();
            a.probs[r * seq + t] = w;
            z += w;
        }
        for (int t = 0; t < seq; ++t) a.probs[r * seq + t] /= z;
        int stride = 17 + (r % 11);
        for (int j = 0; j < selected; ++j) a.gather[r * selected + j] = (r * 13 + j * stride + 7) % seq;
        for (int b = 0; b < blocks; ++b) {
            for (int dd = 0; dd < d; ++dd) a.centroids[(r * blocks + b) * d + dd] = 0.1f * rng.normal();
            a.radii[r * blocks + b] = 0.1f + rng.uniform();
        }
    }
    return a;
}

Measurement time_qk_dot(const Data& a, int repeats) {
    double local = 0.0;
    const auto t0 = std::chrono::steady_clock::now();
    for (int rep = 0; rep < repeats; ++rep) {
        for (int r = 0; r < a.rows; ++r) {
            const float* q = &a.q[r * a.d];
            for (int token = 0; token < a.seq; ++token) {
                const float* k = &a.k[(r * a.seq + token) * a.d];
                float dot = 0.0f;
                for (int dd = 0; dd < a.d; ++dd) dot += q[dd] * k[dd];
                local += dot;
            }
        }
    }
    const auto t1 = std::chrono::steady_clock::now();
    GLOBAL_SINK += local;
    double elapsed = std::chrono::duration<double, std::nano>(t1 - t0).count();
    double vectors = static_cast<double>(repeats) * a.rows * a.seq;
    return {"qk_dot_sequential", a.seq, a.d, a.seq, a.rows, repeats, elapsed, vectors, elapsed / vectors, local};
}

Measurement time_value_accum_sequential(const Data& a, int repeats) {
    double local = 0.0;
    std::vector<float> y(a.rows * a.d, 0.0f);
    const auto t0 = std::chrono::steady_clock::now();
    for (int rep = 0; rep < repeats; ++rep) {
        for (int r = 0; r < a.rows; ++r) {
            float* out = &y[r * a.d];
            for (int dd = 0; dd < a.d; ++dd) out[dd] = 0.0f;
            for (int token = 0; token < a.seq; ++token) {
                float p = a.probs[r * a.seq + token];
                const float* v = &a.v[(r * a.seq + token) * a.d];
                for (int dd = 0; dd < a.d; ++dd) out[dd] += p * v[dd];
            }
            local += out[(r + rep) % a.d];
        }
    }
    const auto t1 = std::chrono::steady_clock::now();
    GLOBAL_SINK += local;
    double elapsed = std::chrono::duration<double, std::nano>(t1 - t0).count();
    double vectors = static_cast<double>(repeats) * a.rows * a.seq;
    return {"value_accumulate_sequential", a.seq, a.d, a.seq, a.rows, repeats, elapsed, vectors, elapsed / vectors, local};
}

Measurement time_value_accum_gather(const Data& a, int repeats) {
    double local = 0.0;
    std::vector<float> y(a.rows * a.d, 0.0f);
    const auto t0 = std::chrono::steady_clock::now();
    for (int rep = 0; rep < repeats; ++rep) {
        for (int r = 0; r < a.rows; ++r) {
            float* out = &y[r * a.d];
            for (int dd = 0; dd < a.d; ++dd) out[dd] = 0.0f;
            for (int j = 0; j < a.selected; ++j) {
                int token = a.gather[r * a.selected + j];
                float p = a.probs[r * a.seq + token];
                const float* v = &a.v[(r * a.seq + token) * a.d];
                for (int dd = 0; dd < a.d; ++dd) out[dd] += p * v[dd];
            }
            local += out[(r + rep) % a.d];
        }
    }
    const auto t1 = std::chrono::steady_clock::now();
    GLOBAL_SINK += local;
    double elapsed = std::chrono::duration<double, std::nano>(t1 - t0).count();
    double vectors = static_cast<double>(repeats) * a.rows * a.selected;
    return {"value_accumulate_sparse_gather", a.seq, a.d, a.selected, a.rows, repeats, elapsed, vectors, elapsed / vectors, local};
}

Measurement time_block_centroid_dot(const Data& a, int repeats) {
    double local = 0.0;
    int blocks = (a.seq + 7) / 8;
    const auto t0 = std::chrono::steady_clock::now();
    for (int rep = 0; rep < repeats; ++rep) {
        for (int r = 0; r < a.rows; ++r) {
            const float* q = &a.q[r * a.d];
            for (int b = 0; b < blocks; ++b) {
                const float* c = &a.centroids[(r * blocks + b) * a.d];
                float dot = 0.0f;
                for (int dd = 0; dd < a.d; ++dd) dot += q[dd] * c[dd];
                dot += a.radii[r * blocks + b];
                local += dot;
            }
        }
    }
    const auto t1 = std::chrono::steady_clock::now();
    GLOBAL_SINK += local;
    double elapsed = std::chrono::duration<double, std::nano>(t1 - t0).count();
    double vectors = static_cast<double>(repeats) * a.rows * blocks;
    return {"block_centroid_bound_dot", a.seq, a.d, blocks, a.rows, repeats, elapsed, vectors, elapsed / vectors, local};
}

int main(int argc, char** argv) {
    std::string out_path = argc > 1 ? argv[1] : "";
    std::vector<Measurement> rows;
    const int rows_count = 2048;
    const int repeats = 256;
    const int seq = 48;
    for (int d : {8, 64}) {
        int selected = d == 8 ? 16 : 32;
        Data a = make_data(seq, d, rows_count, selected, 0x5700ULL + static_cast<uint64_t>(d));
        // Warm-up one pass per primitive to reduce first-touch effects.
        time_qk_dot(a, 8);
        time_value_accum_sequential(a, 8);
        time_value_accum_gather(a, 8);
        time_block_centroid_dot(a, 8);
        rows.push_back(time_qk_dot(a, repeats));
        rows.push_back(time_value_accum_sequential(a, repeats));
        rows.push_back(time_value_accum_gather(a, repeats));
        rows.push_back(time_block_centroid_dot(a, repeats));
    }
    std::ostringstream os;
    os << std::fixed << std::setprecision(9);
    os << "{\n";
    os << "  \"artifact\": \"REV0057_PLATFORM_PRIMITIVE_COST_NATIVE\",\n";
    os << "  \"probe\": \"platform_cost_calibration_native\",\n";
    os << "  \"scope\": \"native CPU primitive timing; not a fused attention kernel, GPU kernel, or throughput claim\",\n";
    os << "  \"global_sink\": " << GLOBAL_SINK << ",\n";
    os << "  \"rows\": [\n";
    for (size_t i = 0; i < rows.size(); ++i) {
        const auto& m = rows[i];
        os << "    {\"primitive\": \"" << esc(m.primitive) << "\", \"seq\": " << m.seq
           << ", \"d\": " << m.d << ", \"selected\": " << m.selected
           << ", \"rows\": " << m.rows << ", \"repeats\": " << m.repeats
           << ", \"elapsed_ns\": " << m.elapsed_ns << ", \"vectors\": " << m.vectors
           << ", \"ns_per_vector\": " << m.ns_per_vector << ", \"checksum\": " << m.checksum << "}";
        if (i + 1 != rows.size()) os << ",";
        os << "\n";
    }
    os << "  ]\n";
    os << "}\n";
    if (out_path.empty()) {
        std::cout << os.str();
    } else {
        std::ofstream f(out_path);
        f << os.str();
    }
    return 0;
}
