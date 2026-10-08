// MUC-5 rev0015 C++ probe kernel.
//
// This is intentionally a small, auditable C ABI kernel, not a full game engine.
// It accelerates exact hypergeometric deck probes used by constructor search,
// MAP-Elites screening, and future evolutionary loops.  The long-haul plan is
// to move stable, heavily-profiled referee hot paths into C++ behind the same
// public DecisionFrame contract; this probe kernel is the first measured bridge.

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <exception>

namespace {

long double choose_ld(int n, int k) {
    if (k < 0 || k > n) return 0.0L;
    if (k == 0 || k == n) return 1.0L;
    k = std::min(k, n - k);
    long double out = 1.0L;
    for (int i = 1; i <= k; ++i) {
        out *= static_cast<long double>(n - k + i);
        out /= static_cast<long double>(i);
    }
    return out;
}

long double prob_keepable_land_band(int population, int islands, int draws, int low, int high) {
    const long double denom = choose_ld(population, draws);
    if (denom <= 0.0L) return 0.0L;
    long double total = 0.0L;
    const int lo = std::max(low, 0);
    const int hi = std::min({high, islands, draws});
    for (int lands = lo; lands <= hi; ++lands) {
        total += choose_ld(islands, lands) * choose_ld(population - islands, draws - lands);
    }
    return total / denom;
}

long double prob_card_and_lands(int population, int islands, int card_count, int draws, int min_lands) {
    const long double denom = choose_ld(population, draws);
    if (denom <= 0.0L) return 0.0L;
    const int non_island_non_card = population - islands - card_count;
    long double total = 0.0L;
    for (int lands = min_lands; lands <= std::min(islands, draws); ++lands) {
        for (int c = 1; c <= std::min(card_count, draws - lands); ++c) {
            const int rest = draws - lands - c;
            if (0 <= rest && rest <= non_island_non_card) {
                total += choose_ld(islands, lands) * choose_ld(card_count, c) * choose_ld(non_island_non_card, rest);
            }
        }
    }
    return total / denom;
}

long double prob_force_with_pitch(int population, int islands, int counterspell, int force, int jace, int overlord, int draws) {
    const long double denom = choose_ld(population, draws);
    if (denom <= 0.0L) return 0.0L;
    const int other_blue = counterspell + jace + overlord;
    long double total = 0.0L;
    for (int f = 1; f <= std::min(force, draws); ++f) {
        for (int ob = 0; ob <= std::min(other_blue, draws - f); ++ob) {
            if (f + ob < 2) continue;
            const int land_draws = draws - f - ob;
            if (0 <= land_draws && land_draws <= islands) {
                total += choose_ld(force, f) * choose_ld(other_blue, ob) * choose_ld(islands, land_draws);
            }
        }
    }
    return total / denom;
}

} // namespace

extern "C" {

// Return 1 if the C++ kernel was loaded successfully. Useful for ctypes smoke tests.
int muc5_probe_kernel_version() {
    return 1500;
}

// Fill an n x 7 double table from n x 6 int deck vectors:
// input row = [deck_size, island, counterspell, force, jace, overlord]
// output row = [keepable, force_pitch, cspell_t2, ovl_t3, jace_t4, ovl_t5, crude_score]
// Returns 0 on success, negative on obvious input errors.
int muc5_fill_probe_table(const int* decks, int n, double* out) {
    if (decks == nullptr || out == nullptr || n < 0) return -1;
    try {
        for (int r = 0; r < n; ++r) {
            const int* d = decks + 6 * r;
            const int size = d[0];
            const int islands = d[1];
            const int counterspell = d[2];
            const int force = d[3];
            const int jace = d[4];
            const int overlord = d[5];
            if (!((size == 40 || size == 60) && islands >= 0 && counterspell >= 0 && force >= 0 && jace >= 0 && overlord >= 0 && islands + counterspell + force + jace + overlord == size)) {
                return -2;
            }
            const long double keep = prob_keepable_land_band(size, islands, 7, 2, 5);
            const long double force_pitch = prob_force_with_pitch(size, islands, counterspell, force, jace, overlord, 7);
            const long double cspell_t2 = prob_card_and_lands(size, islands, counterspell, 8, 2);
            const long double ovl_t3 = prob_card_and_lands(size, islands, overlord, 9, 3);
            const long double jace_t4 = prob_card_and_lands(size, islands, jace, 10, 4);
            const long double ovl_t5 = prob_card_and_lands(size, islands, overlord, 11, 5);
            const long double crude = 0.24L * keep + 0.19L * force_pitch + 0.22L * cspell_t2 + 0.12L * ovl_t3 + 0.15L * jace_t4 + 0.08L * ovl_t5;
            double* o = out + 7 * r;
            o[0] = static_cast<double>(keep);
            o[1] = static_cast<double>(force_pitch);
            o[2] = static_cast<double>(cspell_t2);
            o[3] = static_cast<double>(ovl_t3);
            o[4] = static_cast<double>(jace_t4);
            o[5] = static_cast<double>(ovl_t5);
            o[6] = static_cast<double>(crude);
        }
    } catch (...) {
        return -3;
    }
    return 0;
}

} // extern "C"
