#include "sync_atomic_file_publication.hpp"
#include "sync_atomic_file_publication_internal.hpp"

#if defined(__linux__)
#include "self_exec_test_process.hpp"
#endif

#include <algorithm>
#include <cerrno>
#include <chrono>
#include <charconv>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#if !defined(_WIN32)
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#endif

namespace {

namespace fs = std::filesystem;
using anonsync::SyncAtomicFilePublicationError;
using anonsync::SyncAtomicFilePublicationOutcome;
using anonsync::SyncAtomicFilePublicationResidue;
using anonsync::atomic_file_publication_detail::AtomicFilePublicationCutpoint;
using anonsync::atomic_file_publication_detail::AtomicFilePublicationObservation;

class TestState final {
public:
    void check(bool condition, const std::string& label) {
        ++total_;
        if (condition) {
            ++passed_;
        } else {
            std::cerr << "FAIL: " << label << '\n';
        }
    }

    int finish() const {
        std::cout << "sync atomic publication cutpoints: " << passed_ << "/"
                  << total_ << " checks passed\n";
        return passed_ == total_ ? 0 : 1;
    }

private:
    int total_ = 0;
    int passed_ = 0;
};

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
        const fs::path base = fs::temp_directory_path();
        const auto seed = static_cast<std::uint64_t>(
            std::chrono::steady_clock::now().time_since_epoch().count());
        for (std::uint64_t attempt = 0; attempt != 4096; ++attempt) {
            path_ = base / ("anonsync-atomic-cutpoint-" +
                            std::to_string(seed) + "-" +
                            std::to_string(attempt));
            std::error_code ec;
            if (fs::create_directory(path_, ec)) return;
        }
        throw std::runtime_error("could not create cutpoint test directory");
    }

    ~TemporaryDirectory() {
        std::error_code ec;
        fs::remove_all(path_, ec);
    }

    const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
};

void write_binary(const fs::path& path, const std::string& bytes) {
    std::ofstream out(path, std::ios::binary | std::ios::trunc);
    if (!out) throw std::runtime_error("could not open test file for write");
    out.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    if (!out) throw std::runtime_error("could not write test file");
}

std::string read_binary(const fs::path& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("could not open test file for read");
    return std::string(std::istreambuf_iterator<char>(in),
                       std::istreambuf_iterator<char>());
}

std::vector<fs::path> publication_temps(const fs::path& directory) {
    std::vector<fs::path> result;
    for (const fs::directory_entry& entry : fs::directory_iterator(directory)) {
        const std::string name = entry.path().filename().string();
        if (name.rfind(".anonsync-publish-v1-", 0) == 0 &&
            name.size() >= 4 && name.substr(name.size() - 4) == ".tmp") {
            result.push_back(entry.path());
        }
    }
    std::sort(result.begin(), result.end());
    return result;
}

#if !defined(_WIN32)
bool is_private_regular_file_with_size(const fs::path& path,
                                       std::uintmax_t expected_size) {
    struct stat status_buffer {};
    if (::lstat(path.c_str(), &status_buffer) != 0 ||
        !S_ISREG(status_buffer.st_mode) ||
        (status_buffer.st_mode & 0077) != 0) {
        return false;
    }
    std::error_code ec;
    return fs::file_size(path, ec) == expected_size && !ec;
}
#endif

constexpr int kCrashExitBase = 120;
constexpr std::string_view kCrashHelper =
    "--anonsync-atomic-publication-crash-helper-v1";

const std::string& old_generation_payload() {
    static const std::string payload = "{\"generation\":\"old\"}\n";
    return payload;
}

const std::string& new_generation_payload() {
    static const std::string payload(256 * 1024 + 17, 'N');
    return payload;
}

const std::vector<AtomicFilePublicationCutpoint>& posix_cutpoints() {
    static const std::vector<AtomicFilePublicationCutpoint> points = {
        AtomicFilePublicationCutpoint::TempReserved,
        AtomicFilePublicationCutpoint::PayloadWritten,
        AtomicFilePublicationCutpoint::TempFileSynced,
        AtomicFilePublicationCutpoint::TempNameRevalidated,
        AtomicFilePublicationCutpoint::ParentDirectoryRevalidated,
        AtomicFilePublicationCutpoint::FinalEntryRevalidated,
        AtomicFilePublicationCutpoint::NamespacePublished,
        AtomicFilePublicationCutpoint::DirectorySynced,
        AtomicFilePublicationCutpoint::ParentDirectoryPostpublicationRevalidated,
        AtomicFilePublicationCutpoint::TempDescriptorClosed,
        AtomicFilePublicationCutpoint::ParentDirectoryDescriptorClosed,
    };
    return points;
}

bool is_prepublication(AtomicFilePublicationCutpoint point) {
    return point == AtomicFilePublicationCutpoint::TempReserved ||
           point == AtomicFilePublicationCutpoint::PayloadWritten ||
           point == AtomicFilePublicationCutpoint::TempFileSynced ||
           point == AtomicFilePublicationCutpoint::TempNameRevalidated ||
           point == AtomicFilePublicationCutpoint::ParentDirectoryRevalidated ||
           point == AtomicFilePublicationCutpoint::FinalEntryRevalidated;
}

SyncAtomicFilePublicationOutcome expected_outcome(
    AtomicFilePublicationCutpoint point) {
    if (is_prepublication(point)) {
        return SyncAtomicFilePublicationOutcome::NotPublished;
    }
    if (point == AtomicFilePublicationCutpoint::NamespacePublished) {
        return SyncAtomicFilePublicationOutcome::PublishedDurabilityIndeterminate;
    }
    return SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced;
}

SyncAtomicFilePublicationResidue expected_residue(
    AtomicFilePublicationCutpoint point) {
    return is_prepublication(point)
               ? SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain
               : SyncAtomicFilePublicationResidue::None;
}

struct RecordingContext {
    std::vector<AtomicFilePublicationObservation> observations;
};

void record_observer(const AtomicFilePublicationObservation& observation,
                     void* raw_context) {
    static_cast<RecordingContext*>(raw_context)
        ->observations.push_back(observation);
}

class InjectedFrontierFailure final : public std::runtime_error {
public:
    explicit InjectedFrontierFailure(const std::string& message)
        : std::runtime_error(message) {}
};

struct ThrowContext {
    AtomicFilePublicationCutpoint target;
    bool fired = false;
    AtomicFilePublicationObservation observation{
        AtomicFilePublicationCutpoint::TempReserved,
        SyncAtomicFilePublicationOutcome::NotPublished,
        SyncAtomicFilePublicationResidue::None};
};

void throw_observer(const AtomicFilePublicationObservation& observation,
                    void* raw_context) {
    auto& context = *static_cast<ThrowContext*>(raw_context);
    if (observation.cutpoint != context.target) return;
    context.fired = true;
    context.observation = observation;
    throw InjectedFrontierFailure(
        std::string("injected frontier failure at ") +
        anonsync::atomic_file_publication_detail::
            atomic_file_publication_cutpoint_name(observation.cutpoint));
}

bool has_injected_nested_cause(const std::exception& error) {
    try {
        std::rethrow_if_nested(error);
    } catch (const InjectedFrontierFailure&) {
        return true;
    } catch (const std::exception& nested) {
        return has_injected_nested_cause(nested);
    } catch (...) {
    }
    return false;
}

#if !defined(_WIN32)
struct CrashContext {
    AtomicFilePublicationCutpoint target;
    int exit_code;
};

void crash_observer(const AtomicFilePublicationObservation& observation,
                    void* raw_context) {
    const auto& context = *static_cast<CrashContext*>(raw_context);
    if (observation.cutpoint == context.target) {
        ::_exit(context.exit_code);
    }
}

#if defined(__linux__)
[[nodiscard]] std::size_t parse_crash_point_index_or_throw(
    std::string_view text) {
    std::size_t value = 0;
    const auto parsed =
        std::from_chars(text.data(), text.data() + text.size(), value);
    if (parsed.ec != std::errc{} ||
        parsed.ptr != text.data() + text.size() ||
        value >= posix_cutpoints().size()) {
        throw std::runtime_error("invalid atomic crash cutpoint index");
    }
    return value;
}

int run_atomic_crash_helper(int argc, char** argv) {
    try {
        anonsync::test::verify_self_exec_child_boundary_or_throw();
        if (argc != 5 || argv == nullptr || argv[1] == nullptr ||
            std::string_view(argv[1]) != kCrashHelper) {
            throw std::runtime_error("invalid atomic crash helper instruction");
        }
        const std::size_t index = parse_crash_point_index_or_throw(argv[2]);
        const AtomicFilePublicationCutpoint point = posix_cutpoints()[index];
        const std::string expected_name =
            anonsync::atomic_file_publication_detail::
                atomic_file_publication_cutpoint_name(point);
        if (std::string_view(argv[3]) != expected_name) {
            throw std::runtime_error("atomic crash cutpoint name mismatch");
        }
        const fs::path final_path(argv[4]);
        if (!final_path.is_absolute() ||
            final_path != final_path.lexically_normal() ||
            final_path.filename() != "report.json" ||
            read_binary(final_path) != old_generation_payload() ||
            !publication_temps(final_path.parent_path()).empty()) {
            throw std::runtime_error(
                "atomic crash helper initial-state binding failed");
        }
        CrashContext context{
            point, kCrashExitBase + static_cast<int>(index)};
        anonsync::atomic_file_publication_detail::
            write_sync_json_file_atomically_with_observer_or_throw(
                final_path, new_generation_payload(),
                "self-exec crash cutpoint trace", &crash_observer, &context);
        return 98;
    } catch (const std::exception& error) {
        std::cerr << "atomic crash helper failed: " << error.what() << '\n';
        return 96;
    }
}
#endif

struct RebindContext {
    fs::path parent;
    fs::path displaced_parent;
    AtomicFilePublicationCutpoint target;
    bool fired = false;
};

void rebind_parent_observer(
    const AtomicFilePublicationObservation& observation,
    void* raw_context) {
    auto& context = *static_cast<RebindContext*>(raw_context);
    if (observation.cutpoint != context.target) return;
    fs::rename(context.parent, context.displaced_parent);
    fs::create_directory(context.parent);
    context.fired = true;
}

struct StaleTypedContext {
    AtomicFilePublicationCutpoint target;
    bool fired = false;
};

void throw_stale_typed_observer(
    const AtomicFilePublicationObservation& observation,
    void* raw_context) {
    auto& context = *static_cast<StaleTypedContext*>(raw_context);
    if (observation.cutpoint != context.target) return;
    context.fired = true;
    throw SyncAtomicFilePublicationError(
        SyncAtomicFilePublicationOutcome::NotPublished,
        "injected stale typed publication outcome");
}

bool has_stale_typed_nested_cause(const std::exception& error) {
    try {
        std::rethrow_if_nested(error);
    } catch (const SyncAtomicFilePublicationError& nested) {
        return nested.outcome() ==
                   SyncAtomicFilePublicationOutcome::NotPublished &&
               std::string(nested.what()).find("stale typed") !=
                   std::string::npos;
    } catch (const std::exception& nested) {
        return has_stale_typed_nested_cause(nested);
    } catch (...) {
    }
    return false;
}

struct TempModeMutationContext {
    fs::path parent;
    bool fired = false;
};

void widen_temp_mode_observer(
    const AtomicFilePublicationObservation& observation,
    void* raw_context) {
    auto& context = *static_cast<TempModeMutationContext*>(raw_context);
    if (observation.cutpoint != AtomicFilePublicationCutpoint::TempFileSynced) {
        return;
    }
    const std::vector<fs::path> temps = publication_temps(context.parent);
    if (temps.size() != 1) {
        throw std::runtime_error(
            "mode mutation expected exactly one publication temp");
    }
    if (::chmod(temps.front().c_str(), 0644) != 0) {
        throw std::runtime_error("mode mutation chmod failed");
    }
    context.fired = true;
}

struct CompetingCreateContext {
    fs::path final_path;
    std::string competing_payload;
    bool fired = false;
};

void create_competing_final_observer(
    const AtomicFilePublicationObservation& observation,
    void* raw_context) {
    auto& context = *static_cast<CompetingCreateContext*>(raw_context);
    if (observation.cutpoint !=
        AtomicFilePublicationCutpoint::FinalEntryRevalidated) {
        return;
    }
    write_binary(context.final_path, context.competing_payload);
    context.fired = true;
}
#endif

}  // namespace

int main(int argc, char** argv) {
#if defined(__linux__)
    if (argc >= 2 && argv != nullptr && argv[1] != nullptr &&
        std::string_view(argv[1]) == kCrashHelper) {
        return run_atomic_crash_helper(argc, argv);
    }
#endif
    try {
        if (argc != 1) {
            throw std::runtime_error("unexpected cutpoint test arguments");
        }
        TestState state;
        TemporaryDirectory root;
        const fs::path final_path = root.path() / "report.json";
        const std::string& old_payload = old_generation_payload();
        const std::string& new_payload = new_generation_payload();

#if defined(_WIN32)
        state.check(true,
                    "POSIX cutpoint ordering is not executed on Windows");
#else
        RecordingContext recording;
        write_binary(final_path, old_payload);
        anonsync::atomic_file_publication_detail::
            write_sync_json_file_atomically_with_observer_or_throw(
                final_path, new_payload, "normal cutpoint trace",
                &record_observer, &recording);
        state.check(recording.observations.size() == posix_cutpoints().size(),
                    "normal publication visits every reviewed frontier");
        bool order_matches = recording.observations.size() ==
                             posix_cutpoints().size();
        bool classifications_match = order_matches;
        bool residue_matches = order_matches;
        for (std::size_t index = 0;
             index < recording.observations.size() &&
             index < posix_cutpoints().size();
             ++index) {
            const auto& observed = recording.observations[index];
            order_matches = order_matches &&
                            observed.cutpoint == posix_cutpoints()[index];
            classifications_match =
                classifications_match &&
                observed.outcome == expected_outcome(observed.cutpoint);
            residue_matches =
                residue_matches &&
                observed.residue == expected_residue(observed.cutpoint);
        }
        state.check(order_matches,
                    "normal publication frontier order is exact");
        state.check(classifications_match,
                    "every frontier carries the expected typed outcome");
        state.check(residue_matches,
                    "every frontier reports exact possible temp-residue state");
        state.check(read_binary(final_path) == new_payload,
                    "normal observed publication preserves exact bytes");
        state.check(publication_temps(root.path()).empty(),
                    "normal observed publication leaves no temp residue");

        const fs::path immutable_parent = root.path() / "immutable-race";
        fs::create_directory(immutable_parent);
        const fs::path immutable_final = immutable_parent / "receipt.json";
        const std::string competing_payload =
            "{\"creator\":\"competing-authority\"}\n";
        CompetingCreateContext competing_context{
            immutable_final, competing_payload};
        bool competing_error_caught = false;
        SyncAtomicFilePublicationOutcome competing_outcome =
            SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced;
        SyncAtomicFilePublicationResidue competing_residue =
            SyncAtomicFilePublicationResidue::None;
        std::string competing_message;
        try {
            anonsync::atomic_file_publication_detail::
                write_sync_json_file_atomically_create_new_with_observer_or_throw(
                    immutable_final, new_payload,
                    "immutable competing-create trace",
                    &create_competing_final_observer, &competing_context);
        } catch (const SyncAtomicFilePublicationError& error) {
            competing_error_caught = true;
            competing_outcome = error.outcome();
            competing_residue = error.residue();
            competing_message = error.what();
        }
        state.check(competing_context.fired && competing_error_caught,
                    "create-new race reaches the exact post-revalidation frontier");
        state.check(
            competing_outcome == SyncAtomicFilePublicationOutcome::NotPublished &&
                competing_residue ==
                    SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain,
            "create-new race is typed as no namespace effect by this attempt");
        state.check(
            competing_message.find("atomic create-new publication failed") !=
                    std::string::npos &&
                competing_message.find("temporary artifact may remain") !=
                    std::string::npos,
            "create-new race reports no-replace denial and exact residue state");
        state.check(read_binary(immutable_final) == competing_payload,
                    "create-new race preserves the competing creator's exact bytes");
        const std::vector<fs::path> competing_temps =
            publication_temps(immutable_parent);
        state.check(
            competing_temps.size() == 1 &&
                is_private_regular_file_with_size(competing_temps.front(), 0),
            "create-new race leaves one sanitized private writer-owned residue");
        for (const fs::path& temp : competing_temps) fs::remove(temp);

        const fs::path rebind_parent = root.path() / "rebind-parent";
        const fs::path displaced_parent = root.path() / "rebind-displaced";
        fs::create_directory(rebind_parent);
        const fs::path rebind_final = rebind_parent / "report.json";
        write_binary(rebind_final, old_payload);
        RebindContext rebind_context{
            rebind_parent,
            displaced_parent,
            AtomicFilePublicationCutpoint::TempNameRevalidated};
        bool rebind_typed = false;
        SyncAtomicFilePublicationOutcome rebind_outcome =
            SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced;
        SyncAtomicFilePublicationResidue rebind_residue =
            SyncAtomicFilePublicationResidue::None;
        std::string rebind_message;
        try {
            anonsync::atomic_file_publication_detail::
                write_sync_json_file_atomically_with_observer_or_throw(
                    rebind_final, new_payload, "parent rebind trace",
                    &rebind_parent_observer, &rebind_context);
        } catch (const SyncAtomicFilePublicationError& error) {
            rebind_typed = true;
            rebind_outcome = error.outcome();
            rebind_residue = error.residue();
            rebind_message = error.what();
        }
        state.check(rebind_context.fired && rebind_typed,
                    "parent rebind is detected after temp synchronization");
        state.check(
            rebind_outcome == SyncAtomicFilePublicationOutcome::NotPublished &&
                rebind_residue ==
                    SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain &&
                rebind_message.find(
                    "no longer names the retained directory identity") !=
                    std::string::npos &&
                rebind_message.find("temporary artifact may remain") !=
                    std::string::npos,
            "parent rebind failure reports outcome and possible residue");
        state.check(!fs::exists(rebind_parent / "report.json"),
                    "rebound configured parent receives no publication");
        state.check(read_binary(displaced_parent / "report.json") == old_payload,
                    "detached original parent retains prior final generation");
        const std::vector<fs::path> rebind_temps =
            publication_temps(displaced_parent);
        state.check(publication_temps(rebind_parent).empty() &&
                        rebind_temps.size() == 1 &&
                        is_private_regular_file_with_size(rebind_temps.front(), 0),
                    "parent rebind leaves one sanitized private residue in the retained directory");
        for (const fs::path& temp : rebind_temps) fs::remove(temp);

        const fs::path late_rebind_parent = root.path() / "late-rebind-parent";
        const fs::path late_displaced_parent =
            root.path() / "late-rebind-displaced";
        fs::create_directory(late_rebind_parent);
        const fs::path late_rebind_final = late_rebind_parent / "report.json";
        write_binary(late_rebind_final, old_payload);
        RebindContext late_rebind_context{
            late_rebind_parent,
            late_displaced_parent,
            AtomicFilePublicationCutpoint::DirectorySynced};
        bool late_rebind_typed = false;
        SyncAtomicFilePublicationOutcome late_rebind_outcome =
            SyncAtomicFilePublicationOutcome::NotPublished;
        SyncAtomicFilePublicationResidue late_rebind_residue =
            SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain;
        std::string late_rebind_message;
        try {
            anonsync::atomic_file_publication_detail::
                write_sync_json_file_atomically_with_observer_or_throw(
                    late_rebind_final, new_payload, "late parent rebind trace",
                    &rebind_parent_observer, &late_rebind_context);
        } catch (const SyncAtomicFilePublicationError& error) {
            late_rebind_typed = true;
            late_rebind_outcome = error.outcome();
            late_rebind_residue = error.residue();
            late_rebind_message = error.what();
        }
        state.check(late_rebind_context.fired && late_rebind_typed,
                    "post-sync parent rebind cannot return false success");
        state.check(
            late_rebind_outcome ==
                    SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced &&
                late_rebind_residue == SyncAtomicFilePublicationResidue::None &&
                late_rebind_message.find(
                    "no longer names the retained directory identity") !=
                    std::string::npos,
            "post-sync parent rebind preserves published-and-synced outcome");
        state.check(!fs::exists(late_rebind_parent / "report.json"),
                    "late replacement parent receives no guessed publication");
        state.check(read_binary(late_displaced_parent / "report.json") ==
                        new_payload,
                    "late detached parent contains the exact synced generation");
        state.check(publication_temps(late_rebind_parent).empty() &&
                        publication_temps(late_displaced_parent).empty(),
                    "postpublication rebind leaves no temp residue");

        StaleTypedContext stale_typed_context{
            AtomicFilePublicationCutpoint::NamespacePublished};
        bool stale_typed_outer_caught = false;
        bool stale_typed_nested = false;
        SyncAtomicFilePublicationOutcome stale_typed_outer_outcome =
            SyncAtomicFilePublicationOutcome::NotPublished;
        SyncAtomicFilePublicationResidue stale_typed_outer_residue =
            SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain;
        try {
            anonsync::atomic_file_publication_detail::
                write_sync_json_file_atomically_with_observer_or_throw(
                    final_path, new_payload, "stale typed trace",
                    &throw_stale_typed_observer, &stale_typed_context);
        } catch (const SyncAtomicFilePublicationError& error) {
            stale_typed_outer_caught = true;
            stale_typed_outer_outcome = error.outcome();
            stale_typed_outer_residue = error.residue();
            stale_typed_nested = has_stale_typed_nested_cause(error);
        }
        state.check(stale_typed_context.fired && stale_typed_outer_caught,
                    "already-typed nested failures are recomposed");
        state.check(
            stale_typed_outer_outcome ==
                    SyncAtomicFilePublicationOutcome::PublishedDurabilityIndeterminate &&
                stale_typed_outer_residue == SyncAtomicFilePublicationResidue::None,
            "outer typed status reflects the actual completed effects");
        state.check(stale_typed_nested,
                    "stale typed failure remains available as nested evidence");

        const fs::path mode_parent = root.path() / "mode-mutation-parent";
        fs::create_directory(mode_parent);
        const fs::path mode_final = mode_parent / "report.json";
        write_binary(mode_final, old_payload);
        TempModeMutationContext mode_context{mode_parent};
        bool mode_error_caught = false;
        SyncAtomicFilePublicationOutcome mode_outcome =
            SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced;
        SyncAtomicFilePublicationResidue mode_residue =
            SyncAtomicFilePublicationResidue::None;
        std::string mode_message;
        try {
            anonsync::atomic_file_publication_detail::
                write_sync_json_file_atomically_with_observer_or_throw(
                    mode_final, new_payload, "temp mode mutation trace",
                    &widen_temp_mode_observer, &mode_context);
        } catch (const SyncAtomicFilePublicationError& error) {
            mode_error_caught = true;
            mode_outcome = error.outcome();
            mode_residue = error.residue();
            mode_message = error.what();
        }
        state.check(mode_context.fired && mode_error_caught,
                    "widened temp permissions are detected before rename");
        state.check(
            mode_outcome == SyncAtomicFilePublicationOutcome::NotPublished &&
                mode_residue ==
                    SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain &&
                mode_message.find("private singly linked") != std::string::npos &&
                mode_message.find("temporary artifact may remain") !=
                    std::string::npos,
            "temp permission mutation is typed not-published with residue");
        state.check(read_binary(mode_final) == old_payload,
                    "temp permission mutation preserves prior generation");
        const std::vector<fs::path> mode_temps = publication_temps(mode_parent);
        state.check(mode_temps.size() == 1 &&
                        is_private_regular_file_with_size(mode_temps.front(), 0),
                    "temp permission mutation leaves one re-privatized empty residue");
        for (const fs::path& temp : mode_temps) fs::remove(temp);

        for (AtomicFilePublicationCutpoint point : posix_cutpoints()) {
            write_binary(final_path, old_payload);
            for (const fs::path& temp : publication_temps(root.path())) {
                fs::remove(temp);
            }
            ThrowContext context{point};
            bool typed_error_caught = false;
            bool nested_cause = false;
            SyncAtomicFilePublicationOutcome actual_outcome =
                SyncAtomicFilePublicationOutcome::NotPublished;
            SyncAtomicFilePublicationResidue actual_residue =
                SyncAtomicFilePublicationResidue::None;
            std::string message;
            try {
                anonsync::atomic_file_publication_detail::
                    write_sync_json_file_atomically_with_observer_or_throw(
                        final_path, new_payload, "throw cutpoint trace",
                        &throw_observer, &context);
            } catch (const SyncAtomicFilePublicationError& error) {
                typed_error_caught = true;
                actual_outcome = error.outcome();
                actual_residue = error.residue();
                message = error.what();
                nested_cause = has_injected_nested_cause(error);
            }
            const std::string point_name =
                anonsync::atomic_file_publication_detail::
                    atomic_file_publication_cutpoint_name(point);
            state.check(context.fired && typed_error_caught,
                        point_name + " throw is classified by typed error");
            state.check(actual_outcome == expected_outcome(point),
                        point_name + " throw reports exact effect outcome");
            state.check(actual_residue == expected_residue(point),
                        point_name + " throw reports exact residue state");
            state.check(message.find(point_name) != std::string::npos &&
                            nested_cause &&
                            (!is_prepublication(point) ||
                             message.find("temporary artifact may remain") !=
                                 std::string::npos),
                        point_name + " throw preserves diagnostic and nested cause");
            state.check(read_binary(final_path) ==
                            (is_prepublication(point) ? old_payload : new_payload),
                        point_name + " throw leaves the expected visible generation");
            const std::vector<fs::path> caught_temps =
                publication_temps(root.path());
            state.check(
                is_prepublication(point)
                    ? caught_temps.size() == 1 &&
                          is_private_regular_file_with_size(caught_temps.front(), 0)
                    : caught_temps.empty(),
                point_name +
                    (is_prepublication(point)
                         ? " caught failure leaves one sanitized private residue"
                         : " caught postpublication failure leaves no temp residue"));
            for (const fs::path& temp : caught_temps) fs::remove(temp);
        }

#if defined(__linux__)
        const fs::path crash_executable =
            anonsync::test::current_self_executable_or_throw();
        for (std::size_t index = 0; index < posix_cutpoints().size(); ++index) {
            const AtomicFilePublicationCutpoint point = posix_cutpoints()[index];
            write_binary(final_path, old_payload);
            for (const fs::path& temp : publication_temps(root.path())) {
                fs::remove(temp);
            }
            const int exit_code = kCrashExitBase + static_cast<int>(index);
            const std::string point_name =
                anonsync::atomic_file_publication_detail::
                    atomic_file_publication_cutpoint_name(point);
            anonsync::test::SelfExecTestProcess child =
                anonsync::test::spawn_self_exec_test_process_or_throw(
                    crash_executable,
                    {std::string(kCrashHelper), std::to_string(index),
                     point_name, final_path.string()});
            child.wait_for_exact_exit(
                exit_code, std::chrono::seconds(10),
                point_name + " atomic publication crash helper");
            state.check(true,
                        point_name + " process exits at the exact frontier");

            const std::vector<fs::path> temps = publication_temps(root.path());
            if (is_prepublication(point)) {
                state.check(read_binary(final_path) == old_payload,
                            point_name + " crash preserves prior final generation");
                state.check(temps.size() == 1,
                            point_name + " crash leaves exactly one private temp");
                bool temp_shape_ok = false;
                bool temp_size_ok = false;
                if (temps.size() == 1) {
                    struct stat status_buffer {};
                    temp_shape_ok =
                        ::lstat(temps[0].c_str(), &status_buffer) == 0 &&
                        S_ISREG(status_buffer.st_mode) &&
                        (status_buffer.st_mode & 0077) == 0;
                    const std::uintmax_t expected_size =
                        point == AtomicFilePublicationCutpoint::TempReserved
                            ? 0
                            : static_cast<std::uintmax_t>(new_payload.size());
                    std::error_code size_ec;
                    temp_size_ok = fs::file_size(temps[0], size_ec) ==
                                       expected_size &&
                                   !size_ec;
                }
                state.check(temp_shape_ok,
                            point_name + " crash residue is private regular file");
                state.check(temp_size_ok,
                            point_name + " crash residue has frontier-exact size");
                for (const fs::path& temp : temps) fs::remove(temp);
            } else {
                state.check(read_binary(final_path) == new_payload,
                            point_name + " crash exposes complete new generation");
                state.check(temps.empty(),
                            point_name + " post-rename crash leaves no temp name");
                state.check(true,
                            point_name + " post-rename state needs no residue shape check");
                state.check(true,
                            point_name + " post-rename state needs no residue size check");
            }
        }
#endif
#endif

        return state.finish();
    } catch (const std::exception& error) {
        std::cerr << "FATAL: " << error.what() << '\n';
        return 2;
    }
}
