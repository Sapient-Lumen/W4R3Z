#include "sync_linux_process_resources.hpp"

#if !defined(_WIN32)

#include <atomic>
#include <cstdint>
#include <fcntl.h>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <utility>

#include <unistd.h>

namespace {

std::uint64_t checks = 0U;

void require(bool condition, std::string_view message) {
    ++checks;
    if (!condition) throw std::runtime_error(std::string(message));
}

template <typename Function>
void require_throws(Function&& function, std::string_view message) {
    ++checks;
    try {
        std::forward<Function>(function)();
    } catch (const std::exception&) {
        return;
    }
    throw std::runtime_error(std::string(message));
}

[[nodiscard]] std::string synthetic_smaps_rollup() {
    return
        "1000-2000 ---p 00000000 00:00 0 [rollup]\n"
        "Rss: 100 kB\n"
        "Pss: 80 kB\n"
        "Pss_Dirty: 30 kB\n"
        "Pss_Anon: 40 kB\n"
        "Pss_File: 30 kB\n"
        "Pss_Shmem: 10 kB\n"
        "Shared_Clean: 20 kB\n"
        "Shared_Dirty: 5 kB\n"
        "Private_Clean: 25 kB\n"
        "Private_Dirty: 50 kB\n"
        "Referenced: 90 kB\n"
        "Anonymous: 45 kB\n"
        "KSM: 0 kB\n"
        "LazyFree: 0 kB\n"
        "AnonHugePages: 2 kB\n"
        "ShmemPmdMapped: 0 kB\n"
        "FilePmdMapped: 0 kB\n"
        "Shared_Hugetlb: 3 kB\n"
        "Private_Hugetlb: 4 kB\n"
        "Swap: 6 kB\n"
        "SwapPss: 7 kB\n"
        "Locked: 8 kB\n";
}

void test_strict_smaps_parser() {
    const auto parsed = anonsync::parse_sync_linux_smaps_rollup_or_throw(
        synthetic_smaps_rollup(), "synthetic smaps");
    require(parsed.rss_kib == 100U, "RSS mismatch");
    require(parsed.pss_kib == 80U, "PSS mismatch");
    require(parsed.pss_dirty_kib == 30U, "dirty PSS mismatch");
    require(parsed.pss_anon_kib == 40U, "anonymous PSS mismatch");
    require(parsed.pss_file_kib == 30U, "file PSS mismatch");
    require(parsed.pss_shmem_kib == 10U, "shmem PSS mismatch");
    require(parsed.shared_clean_kib == 20U, "shared clean mismatch");
    require(parsed.shared_dirty_kib == 5U, "shared dirty mismatch");
    require(parsed.private_clean_kib == 25U, "private clean mismatch");
    require(parsed.private_dirty_kib == 50U, "private dirty mismatch");
    require(parsed.private_resident_kib() == 75U,
            "private resident sum mismatch");
    require(parsed.shared_resident_kib() == 25U,
            "shared resident sum mismatch");
    require(parsed.referenced_kib == 90U, "referenced mismatch");
    require(parsed.anonymous_kib == 45U, "anonymous mismatch");
    require(parsed.anonymous_huge_pages_kib == 2U,
            "anonymous huge-page mismatch");
    require(parsed.shared_hugetlb_kib == 3U, "shared hugetlb mismatch");
    require(parsed.private_hugetlb_kib == 4U, "private hugetlb mismatch");
    require(parsed.swap_kib == 6U, "swap mismatch");
    require(parsed.swap_pss_kib == 7U, "swap PSS mismatch");
    require(parsed.locked_kib == 8U, "locked mismatch");

    require_throws(
        [] { (void)anonsync::parse_sync_linux_smaps_rollup_or_throw(""); },
        "empty smaps image was accepted");
    std::string missing = synthetic_smaps_rollup();
    const std::string locked = "Locked: 8 kB\n";
    missing.erase(missing.find(locked), locked.size());
    require_throws(
        [&] { (void)anonsync::parse_sync_linux_smaps_rollup_or_throw(missing); },
        "missing required smaps field was accepted");
    std::string duplicate = synthetic_smaps_rollup();
    duplicate.append("Rss: 100 kB\n");
    require_throws(
        [&] { (void)anonsync::parse_sync_linux_smaps_rollup_or_throw(duplicate); },
        "duplicate smaps field was accepted");
    std::string wrong_unit = synthetic_smaps_rollup();
    wrong_unit.replace(wrong_unit.find("Rss: 100 kB"), 11U, "Rss: 100 KB");
    require_throws(
        [&] { (void)anonsync::parse_sync_linux_smaps_rollup_or_throw(wrong_unit); },
        "noncanonical smaps unit was accepted");
    std::string malformed = synthetic_smaps_rollup();
    malformed.replace(malformed.find("Pss: 80"), 7U, "Pss: +8");
    require_throws(
        [&] { (void)anonsync::parse_sync_linux_smaps_rollup_or_throw(malformed); },
        "noncanonical unsigned smaps value was accepted");
    std::string leading_zero = synthetic_smaps_rollup();
    leading_zero.replace(
        leading_zero.find("Pss_File: 30"), 12U, "Pss_File: 030");
    require_throws(
        [&] {
            (void)anonsync::parse_sync_linux_smaps_rollup_or_throw(
                leading_zero);
        },
        "leading-zero smaps value was accepted");
    std::string overflow = synthetic_smaps_rollup();
    overflow.replace(
        overflow.find("Swap: 6"), 7U,
        "Swap: 18446744073709551616");
    require_throws(
        [&] { (void)anonsync::parse_sync_linux_smaps_rollup_or_throw(overflow); },
        "overflowing smaps value was accepted");
}

void test_live_observation_and_roundtrip() {
    const auto baseline =
        anonsync::observe_sync_linux_process_resources_or_throw("baseline");
    require(baseline.server_pid == static_cast<std::uint64_t>(::getpid()),
            "live snapshot PID mismatch");
    require(baseline.process_start_time_clock_ticks > 0U,
            "live snapshot omitted process start ticks");
    require(baseline.clock_ticks_per_second > 0U,
            "live snapshot omitted clock frequency");
    require(baseline.page_size_bytes > 0U,
            "live snapshot omitted page size");
    require(baseline.sample_monotonic_milliseconds > 0U,
            "live snapshot omitted sample time");
    require(baseline.memory.rss_kib > 0U,
            "live snapshot reported zero RSS");
    require(baseline.memory.pss_kib > 0U,
            "live snapshot reported zero PSS");
    require(baseline.peak_rss_kib > 0U,
            "live snapshot reported zero peak RSS");
    require(baseline.open_file_descriptors > 0U,
            "live snapshot reported zero descriptors");
    require(baseline.threads > 0U,
            "live snapshot reported zero threads");

    const int extra_descriptor = ::open("/dev/null", O_RDONLY | O_CLOEXEC);
    if (extra_descriptor < 0) throw std::runtime_error("open /dev/null failed");
    std::atomic<bool> stop{false};
    std::atomic<bool> started{false};
    std::thread parked([&] {
        started.store(true, std::memory_order_release);
        while (!stop.load(std::memory_order_acquire)) {
            std::this_thread::yield();
        }
    });
    while (!started.load(std::memory_order_acquire)) std::this_thread::yield();
    const auto expanded =
        anonsync::observe_sync_linux_process_resources_or_throw("expanded");
    stop.store(true, std::memory_order_release);
    parked.join();
    const int close_result = ::close(extra_descriptor);
    if (close_result != 0) throw std::runtime_error("close /dev/null failed");
    require(expanded.open_file_descriptors >=
                baseline.open_file_descriptors + 1U,
            "live descriptor observation did not see an opened descriptor");
    require(expanded.threads >= baseline.threads + 1U,
            "live thread observation did not see a parked thread");
    require(expanded.process_start_time_clock_ticks ==
                baseline.process_start_time_clock_ticks,
            "one process produced different start-time identities");

    const std::string rendered =
        anonsync::render_sync_linux_process_resources_response_json(expanded);
    const auto decoded =
        anonsync::parse_sync_linux_process_resources_response_json_or_throw(
            rendered, static_cast<std::uint64_t>(::getpid()), "roundtrip");
    require(decoded == expanded, "resource response did not roundtrip exactly");
    require_throws(
        [&] {
            (void)anonsync::parse_sync_linux_process_resources_response_json_or_throw(
                rendered, static_cast<std::uint64_t>(::getpid()) + 1U,
                "wrong peer");
        },
        "peer PID mismatch was accepted");

    std::string wrong_schema = rendered;
    const std::string schema =
        std::string(anonsync::kSyncLinuxProcessResourcesResponseSchema);
    wrong_schema.replace(
        wrong_schema.find(schema), schema.size(), "wrong.schema");
    require_throws(
        [&] {
            (void)anonsync::parse_sync_linux_process_resources_response_json_or_throw(
                wrong_schema, 0U, "wrong schema");
        },
        "wrong response schema was accepted");

    std::string wrong_computed = rendered;
    const std::string marker = "\"private_resident_kib\":";
    const std::size_t value_begin = wrong_computed.find(marker) + marker.size();
    const std::size_t value_end = wrong_computed.find(',', value_begin);
    wrong_computed.replace(value_begin, value_end - value_begin, "0");
    require_throws(
        [&] {
            (void)anonsync::parse_sync_linux_process_resources_response_json_or_throw(
                wrong_computed, 0U, "wrong computed field");
        },
        "inconsistent computed resident field was accepted");

    std::string duplicate_key = rendered;
    duplicate_key.insert(duplicate_key.size() - 1U, ",\"threads\":1");
    require_throws(
        [&] {
            (void)anonsync::parse_sync_linux_process_resources_response_json_or_throw(
                duplicate_key, 0U, "duplicate key");
        },
        "duplicate response key was accepted");
}

}  // namespace

int main() {
    try {
        test_strict_smaps_parser();
        test_live_observation_and_roundtrip();
        std::cout << "sync Linux process resources tests passed ("
                  << checks << " checks)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync Linux process resources tests failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}

#else

int main() { return 0; }

#endif
