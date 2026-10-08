#include "sync_atomic_file_publication.hpp"

#if defined(__linux__)
#include "self_exec_test_process.hpp"
#endif

#include <algorithm>
#include <cerrno>
#include <charconv>
#include <barrier>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <mutex>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <utility>
#include <vector>

#if !defined(_WIN32)
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#endif

#if defined(__linux__)
#include <fcntl.h>
#include <linux/fs.h>
#include <stdio.h>
#endif

namespace {

namespace fs = std::filesystem;

class TestState final {
public:
    void check(bool condition, const std::string& label) {
        ++total_;
        if (condition) {
            ++passed_;
            return;
        }
        std::cerr << "FAIL: " << label << '\n';
    }

    [[nodiscard]] int finish() const {
        std::cout << "sync atomic file publication: " << passed_ << "/"
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
            path_ = base / ("anonsync-atomic-publication-test-" +
                            std::to_string(process_id()) + "-" +
                            std::to_string(seed) + "-" +
                            std::to_string(attempt));
            std::error_code ec;
            if (fs::create_directory(path_, ec)) return;
            if (ec && ec != std::errc::file_exists) {
                throw std::runtime_error("temporary directory create failed: " +
                                         ec.message());
            }
        }
        throw std::runtime_error("could not reserve a test directory");
    }

    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;

    ~TemporaryDirectory() {
        std::error_code ignored;
        fs::remove_all(path_, ignored);
    }

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    static std::uint64_t process_id() noexcept {
#if defined(_WIN32)
        return 0;
#else
        return static_cast<std::uint64_t>(::getpid());
#endif
    }

    fs::path path_;
};

std::string read_binary(const fs::path& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("could not open " + path.string());
    return std::string(std::istreambuf_iterator<char>(in),
                       std::istreambuf_iterator<char>());
}

void write_binary(const fs::path& path, const std::string& payload) {
    std::ofstream out(path, std::ios::binary | std::ios::trunc);
    if (!out) throw std::runtime_error("could not create " + path.string());
    out.write(payload.data(), static_cast<std::streamsize>(payload.size()));
    if (!out) throw std::runtime_error("could not write " + path.string());
}

#if !defined(_WIN32)
[[nodiscard]] anonsync::SyncPosixRegularFileSnapshotMetadata
observe_regular_file_or_throw(const fs::path& path, std::string_view label) {
    const int descriptor =
        ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (descriptor < 0) {
        throw std::runtime_error(
            std::string(label) + " open failed");
    }
    try {
        const auto observed =
            anonsync::observe_sync_posix_regular_file_descriptor_or_throw(
                descriptor,
                anonsync::SyncPosixDescriptorLinkPolicy::stable_named_object,
                std::string(label));
        if (::close(descriptor) != 0) {
            throw std::runtime_error(
                std::string(label) + " close failed");
        }
        return observed;
    } catch (...) {
        (void)::close(descriptor);
        throw;
    }
}
#endif

std::size_t publication_temp_count(const fs::path& root) {
    std::size_t count = 0;
    for (const auto& entry : fs::directory_iterator(root)) {
        const std::string name = entry.path().filename().string();
        if (name.starts_with(".anonsync-publish-v1-") &&
            name.ends_with(".tmp")) {
            ++count;
        }
    }
    return count;
}

template <typename Function>
bool throws_with(Function&& function, const std::string& needle) {
    try {
        std::forward<Function>(function)();
    } catch (const std::exception& error) {
        return std::string(error.what()).find(needle) != std::string::npos;
    }
    return false;
}

template <typename Function>
bool throws_publication_with_outcome(
    Function&& function,
    const std::string& needle,
    anonsync::SyncAtomicFilePublicationOutcome expected_outcome) {
    try {
        std::forward<Function>(function)();
    } catch (const anonsync::SyncAtomicFilePublicationError& error) {
        return error.outcome() == expected_outcome &&
               std::string(error.what()).find(needle) != std::string::npos;
    }
    return false;
}

std::string patterned_payload(std::size_t bytes, char seed) {
    std::string out(bytes, '\0');
    for (std::size_t index = 0; index != out.size(); ++index) {
        out[index] = static_cast<char>(seed + static_cast<char>(index % 17));
    }
    return out;
}

void exercise_same_payload_threads(TestState& state, const fs::path& root) {
    constexpr std::size_t kThreadCount = 10;
    constexpr std::size_t kRounds = 10;
    const fs::path final_path = root / "same-payload.json";
    const std::string payload = patterned_payload(1024 * 1024, 'A');
    std::barrier start(static_cast<std::ptrdiff_t>(kThreadCount));
    std::mutex error_mutex;
    std::vector<std::string> errors;
    std::vector<std::thread> threads;
    threads.reserve(kThreadCount);
    for (std::size_t thread_index = 0; thread_index != kThreadCount;
         ++thread_index) {
        threads.emplace_back([&, thread_index] {
            start.arrive_and_wait();
            for (std::size_t round = 0; round != kRounds; ++round) {
                try {
                    anonsync::write_sync_json_file_atomically_no_symlink_or_throw(
                        final_path, payload,
                        "same-payload thread " +
                            std::to_string(thread_index));
                } catch (const std::exception& error) {
                    std::lock_guard lock(error_mutex);
                    errors.emplace_back(error.what());
                }
            }
        });
    }
    for (auto& thread : threads) thread.join();
    if (!errors.empty()) {
        std::cerr << "first same-payload publication error: " << errors.front()
                  << '\n';
    }
    state.check(errors.empty(),
                "all same-process same-payload writers succeed");
    state.check(read_binary(final_path) == payload,
                "same-payload final bytes are exact");
    state.check(publication_temp_count(root) == 0,
                "same-payload campaign leaves no owned temp residue");
}

void exercise_distinct_payload_threads(TestState& state,
                                       const fs::path& root) {
    constexpr std::size_t kThreadCount = 8;
    constexpr std::size_t kRounds = 6;
    const fs::path final_path = root / "distinct-payload.json";
    std::vector<std::string> candidates;
    for (std::size_t index = 0; index != kThreadCount; ++index) {
        std::string payload = patterned_payload(256 * 1024 + index * 97,
                                                static_cast<char>('a' + index));
        payload.replace(0, 16, "writer-" + std::to_string(index) + "-begin");
        payload += "-writer-" + std::to_string(index) + "-end";
        candidates.push_back(std::move(payload));
    }

    std::barrier start(static_cast<std::ptrdiff_t>(kThreadCount));
    std::mutex error_mutex;
    std::vector<std::string> errors;
    std::vector<std::thread> threads;
    threads.reserve(kThreadCount);
    for (std::size_t index = 0; index != kThreadCount; ++index) {
        threads.emplace_back([&, index] {
            start.arrive_and_wait();
            for (std::size_t round = 0; round != kRounds; ++round) {
                try {
                    anonsync::write_sync_json_file_atomically_no_symlink_or_throw(
                        final_path, candidates[index],
                        "distinct-payload thread " + std::to_string(index));
                } catch (const std::exception& error) {
                    std::lock_guard lock(error_mutex);
                    errors.emplace_back(error.what());
                }
            }
        });
    }
    for (auto& thread : threads) thread.join();
    const std::string observed = read_binary(final_path);
    const bool is_complete_candidate =
        std::find(candidates.begin(), candidates.end(), observed) !=
        candidates.end();
    if (!errors.empty()) {
        std::cerr << "first distinct-payload publication error: "
                  << errors.front() << '\n';
    }
    state.check(errors.empty(),
                "all same-process distinct-payload writers succeed");
    state.check(is_complete_candidate,
                "distinct-payload final bytes equal one complete writer");
    state.check(publication_temp_count(root) == 0,
                "distinct-payload campaign leaves no owned temp residue");
}

#if defined(__linux__)
constexpr std::string_view kAtomicWriterHelper =
    "--anonsync-atomic-publication-writer-helper-v1";
constexpr std::string_view kStartGatePayload = "go\n";

[[nodiscard]] int parse_writer_index_or_throw(std::string_view text) {
    int value = -1;
    const auto parsed =
        std::from_chars(text.data(), text.data() + text.size(), value);
    if (parsed.ec != std::errc{} ||
        parsed.ptr != text.data() + text.size() || value < 0 || value >= 8) {
        throw std::runtime_error("invalid atomic writer helper index");
    }
    return value;
}

void require_absolute_normal_path_or_throw(const fs::path& path,
                                           std::string_view label) {
    if (!path.is_absolute() || path != path.lexically_normal() ||
        path.filename().empty()) {
        throw std::runtime_error(std::string(label) +
                                 " must be an absolute normalized path");
    }
}

void await_private_start_gate_or_throw(const fs::path& gate_path) {
    const auto deadline = std::chrono::steady_clock::now() +
                          std::chrono::seconds(10);
    while (std::chrono::steady_clock::now() < deadline) {
        struct stat named_status {};
        if (::lstat(gate_path.c_str(), &named_status) != 0) {
            if (errno == ENOENT) {
                std::this_thread::sleep_for(std::chrono::milliseconds(2));
                continue;
            }
            throw std::runtime_error("atomic writer gate lstat failed");
        }
        if (!S_ISREG(named_status.st_mode) || named_status.st_nlink != 1 ||
            (named_status.st_mode & 0077) != 0) {
            throw std::runtime_error(
                "atomic writer gate is not one private regular file");
        }
        const int descriptor =
            ::open(gate_path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
        if (descriptor < 0) {
            if (errno == ENOENT) continue;
            throw std::runtime_error("atomic writer gate open failed");
        }
        struct stat opened_status {};
        const bool identity_ok =
            ::fstat(descriptor, &opened_status) == 0 &&
            opened_status.st_dev == named_status.st_dev &&
            opened_status.st_ino == named_status.st_ino &&
            S_ISREG(opened_status.st_mode) && opened_status.st_nlink == 1 &&
            (opened_status.st_mode & 0077) == 0;
        char bytes[4] = {};
        ssize_t total = 0;
        while (identity_ok && total < 4) {
            const ssize_t got =
                ::read(descriptor, bytes + total, sizeof(bytes) - total);
            if (got < 0 && errno == EINTR) continue;
            if (got <= 0) break;
            total += got;
        }
        const int close_result = ::close(descriptor);
        if (!identity_ok || close_result != 0 || total != 3 ||
            std::string_view(bytes, 3) != kStartGatePayload) {
            throw std::runtime_error(
                "atomic writer gate bytes or identity are invalid");
        }
        return;
    }
    throw std::runtime_error("atomic writer gate timed out");
}

int run_atomic_writer_helper(int argc, char** argv) {
    try {
        anonsync::test::verify_self_exec_child_boundary_or_throw();
        if (argc != 5 || argv == nullptr || argv[1] == nullptr ||
            std::string_view(argv[1]) != kAtomicWriterHelper) {
            throw std::runtime_error("invalid atomic writer helper instruction");
        }
        const fs::path final_path(argv[2]);
        const fs::path gate_path(argv[3]);
        require_absolute_normal_path_or_throw(final_path, "final path");
        require_absolute_normal_path_or_throw(gate_path, "gate path");
        if (final_path.parent_path() != gate_path.parent_path() ||
            final_path.filename() != "process-payload.json" ||
            gate_path.filename() != ".process-start-v1") {
            throw std::runtime_error("atomic writer helper path binding failed");
        }
        const int writer_index = parse_writer_index_or_throw(argv[4]);
        await_private_start_gate_or_throw(gate_path);
        anonsync::write_sync_json_file_atomically_no_symlink_or_throw(
            final_path, patterned_payload(512 * 1024, 'K'),
            "same-payload self-exec writer " + std::to_string(writer_index));
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "atomic writer helper failed: " << error.what() << '\n';
        return 96;
    }
}

void publish_start_gate_or_throw(const fs::path& gate_path) {
    const std::string gate_basename = gate_path.filename().string();
    const std::string staged_basename =
        gate_basename + ".staged-" + std::to_string(::getpid());
    int parent_descriptor = ::open(
        gate_path.parent_path().c_str(),
        O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
    if (parent_descriptor < 0) {
        throw std::runtime_error("start gate parent open failed");
    }

    int staged_descriptor = ::openat(
        parent_descriptor, staged_basename.c_str(),
        O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0600);
    if (staged_descriptor < 0) {
        const int error = errno;
        (void)::close(parent_descriptor);
        throw std::runtime_error(
            "start gate staging create failed (errno " +
            std::to_string(error) + ")");
    }

    bool staged_name_exists = true;
    auto cleanup = [&]() noexcept {
        if (staged_descriptor >= 0) {
            (void)::close(staged_descriptor);
            staged_descriptor = -1;
        }
        if (staged_name_exists && parent_descriptor >= 0) {
            (void)::unlinkat(
                parent_descriptor, staged_basename.c_str(), 0);
        }
        if (parent_descriptor >= 0) {
            (void)::close(parent_descriptor);
            parent_descriptor = -1;
        }
    };

    try {
        std::size_t offset = 0;
        while (offset != kStartGatePayload.size()) {
            const ssize_t wrote =
                ::write(staged_descriptor, kStartGatePayload.data() + offset,
                        kStartGatePayload.size() - offset);
            if (wrote < 0 && errno == EINTR) continue;
            if (wrote <= 0) {
                throw std::runtime_error("start gate staging write failed");
            }
            offset += static_cast<std::size_t>(wrote);
        }
        if (::fsync(staged_descriptor) != 0) {
            throw std::runtime_error("start gate staging sync failed");
        }
        const int staged_close_result = ::close(staged_descriptor);
        staged_descriptor = -1;
        if (staged_close_result != 0) {
            throw std::runtime_error("start gate staging close failed");
        }

        int rename_result;
        do {
            rename_result = ::renameat2(
                parent_descriptor, staged_basename.c_str(),
                parent_descriptor, gate_basename.c_str(), RENAME_NOREPLACE);
        } while (rename_result != 0 && errno == EINTR);
        if (rename_result != 0) {
            throw std::runtime_error("start gate atomic publication failed");
        }
        staged_name_exists = false;
        if (::fsync(parent_descriptor) != 0) {
            throw std::runtime_error("start gate directory sync failed");
        }
        const int parent_close_result = ::close(parent_descriptor);
        parent_descriptor = -1;
        if (parent_close_result != 0) {
            throw std::runtime_error("start gate parent close failed");
        }
    } catch (...) {
        cleanup();
        throw;
    }
}

void exercise_same_payload_processes(TestState& state, const fs::path& root) {
    constexpr int kChildCount = 8;
    const fs::path final_path = (root / "process-payload.json").lexically_normal();
    const fs::path gate_path = (root / ".process-start-v1").lexically_normal();
    const fs::path executable =
        anonsync::test::current_self_executable_or_throw();
    std::vector<anonsync::test::SelfExecTestProcess> children;
    children.reserve(kChildCount);
    for (int index = 0; index != kChildCount; ++index) {
        children.push_back(
            anonsync::test::spawn_self_exec_test_process_or_throw(
                executable,
                {std::string(kAtomicWriterHelper), final_path.string(),
                 gate_path.string(), std::to_string(index)}));
    }
    publish_start_gate_or_throw(gate_path);
    for (int index = 0; index != kChildCount; ++index) {
        children[static_cast<std::size_t>(index)].wait_for_exact_exit(
            0, std::chrono::seconds(15),
            "same-payload self-exec writer " + std::to_string(index));
    }
    std::error_code remove_error;
    const bool gate_removed = fs::remove(gate_path, remove_error);
    state.check(gate_removed && !remove_error && !fs::exists(gate_path),
                "cross-process start gate is removed exactly once");
    const std::string payload = patterned_payload(512 * 1024, 'K');
    state.check(true, "all cross-process same-payload writers succeed");
    state.check(read_binary(final_path) == payload,
                "cross-process final bytes are exact");
    state.check(publication_temp_count(root) == 0,
                "cross-process campaign leaves no owned temp residue");
}
#endif

}  // namespace

int main(int argc, char** argv) {
#if defined(__linux__)
    if (argc >= 2 && argv != nullptr && argv[1] != nullptr &&
        std::string_view(argv[1]) == kAtomicWriterHelper) {
        return run_atomic_writer_helper(argc, argv);
    }
#endif
    try {
        if (argc != 1) {
            throw std::runtime_error("unexpected atomic publication test arguments");
        }
        TestState state;
        TemporaryDirectory root;

        const fs::path basic = root.path() / "basic.json";
        anonsync::write_sync_json_file_atomically_no_symlink_or_throw(
            basic, "{\"revision\":1}\n", "basic report");
        state.check(read_binary(basic) == "{\"revision\":1}\n",
                    "new publication preserves exact bytes");
        anonsync::write_sync_json_file_atomically_no_symlink_or_throw(
            basic, "{\"revision\":2}\n", "basic report");
        state.check(read_binary(basic) == "{\"revision\":2}\n",
                    "replacement preserves exact bytes");
#if !defined(_WIN32)
        struct stat basic_status {};
        state.check(::stat(basic.c_str(), &basic_status) == 0 &&
                        (basic_status.st_mode & 0077) == 0,
                    "published file grants no group or other access");
#endif
        state.check(publication_temp_count(root.path()) == 0,
                    "basic publication leaves no owned temp residue");

#if !defined(_WIN32)
        const anonsync::SyncDirectoryAuthority root_authority =
            anonsync::SyncDirectoryAuthority::open_or_throw(
                root.path(), "streamed publication test root");

        const fs::path create_source = root.path() / "create-source.bin";
        const std::string streamed_initial = "streamed-create";
        write_binary(create_source, streamed_initial);
        int create_source_descriptor = ::open(
            create_source.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
        if (create_source_descriptor < 0) {
            throw std::runtime_error("streamed create source open failed");
        }
        const auto create_source_observation =
            anonsync::hash_sync_posix_regular_file_descriptor_or_throw(
                create_source_descriptor, streamed_initial.size(),
                anonsync::SyncPosixDescriptorLinkPolicy::stable_named_object,
                "streamed create source");
        if (::lseek(create_source_descriptor, 3, SEEK_SET) != 3) {
            (void)::close(create_source_descriptor);
            throw std::runtime_error(
                "streamed create source positioning failed");
        }
        const fs::path streamed = root.path() / "streamed.bin";
        anonsync::copy_sync_file_atomically_create_new_from_borrowed_descriptor_under_directory_or_throw(
            root_authority, streamed.filename(), create_source_descriptor,
            create_source_observation.metadata,
            create_source_observation.content_sha256, "streamed create");
        state.check(read_binary(streamed) == streamed_initial,
                    "descriptor source create-new publishes exact bytes");
        state.check(::lseek(create_source_descriptor, 0, SEEK_CUR) == 3,
                    "descriptor source create-new preserves caller offset");
        if (::close(create_source_descriptor) != 0) {
            throw std::runtime_error("streamed create source close failed");
        }

        const auto streamed_before = observe_regular_file_or_throw(
            streamed, "streamed replacement predecessor");
        const fs::path replacement_source =
            root.path() / "replacement-source.bin";
        const std::string streamed_replacement = "streamed-replacement";
        write_binary(replacement_source, streamed_replacement);
        int replacement_source_descriptor = ::open(
            replacement_source.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
        if (replacement_source_descriptor < 0) {
            throw std::runtime_error(
                "streamed replacement source open failed");
        }
        const auto replacement_source_observation =
            anonsync::hash_sync_posix_regular_file_descriptor_or_throw(
                replacement_source_descriptor, streamed_replacement.size(),
                anonsync::SyncPosixDescriptorLinkPolicy::stable_named_object,
                "streamed replacement source");
        anonsync::copy_sync_file_atomically_replace_expected_from_borrowed_descriptor_under_directory_or_throw(
            root_authority, streamed.filename(), replacement_source_descriptor,
            replacement_source_observation.metadata,
            replacement_source_observation.content_sha256, streamed_before,
            "streamed replacement");
        if (::close(replacement_source_descriptor) != 0) {
            throw std::runtime_error(
                "streamed replacement source close failed");
        }
        state.check(read_binary(streamed) == streamed_replacement,
                    "descriptor source conditional replacement publishes exact bytes");

        const fs::path wrong_digest_source =
            root.path() / "wrong-digest-source.bin";
        write_binary(wrong_digest_source, "digest-mismatch");
        int wrong_digest_descriptor = ::open(
            wrong_digest_source.c_str(),
            O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
        if (wrong_digest_descriptor < 0) {
            throw std::runtime_error("wrong-digest source open failed");
        }
        const auto wrong_digest_observation =
            anonsync::hash_sync_posix_regular_file_descriptor_or_throw(
                wrong_digest_descriptor, 15U,
                anonsync::SyncPosixDescriptorLinkPolicy::stable_named_object,
                "wrong-digest source");
        std::string wrong_digest = wrong_digest_observation.content_sha256;
        wrong_digest.front() = wrong_digest.front() == '0' ? '1' : '0';
        const fs::path wrong_digest_final =
            root.path() / "wrong-digest-final.bin";
        state.check(
            throws_publication_with_outcome(
                [&] {
                    anonsync::copy_sync_file_atomically_create_new_from_borrowed_descriptor_under_directory_or_throw(
                        root_authority, wrong_digest_final.filename(),
                        wrong_digest_descriptor,
                        wrong_digest_observation.metadata, wrong_digest,
                        "wrong-digest streamed create");
                },
                "source SHA-256 changed before publication",
                anonsync::SyncAtomicFilePublicationOutcome::NotPublished),
            "descriptor source publication independently verifies content identity");
        state.check(!fs::exists(wrong_digest_final),
                    "digest mismatch never publishes a final name");
        if (::close(wrong_digest_descriptor) != 0) {
            throw std::runtime_error("wrong-digest source close failed");
        }

        const fs::path changed_source = root.path() / "changed-source.bin";
        write_binary(changed_source, "before-change");
        int changed_descriptor = ::open(
            changed_source.c_str(), O_RDWR | O_CLOEXEC | O_NOFOLLOW);
        if (changed_descriptor < 0) {
            throw std::runtime_error("changed source open failed");
        }
        const auto changed_observation =
            anonsync::hash_sync_posix_regular_file_descriptor_or_throw(
                changed_descriptor, 13U,
                anonsync::SyncPosixDescriptorLinkPolicy::stable_named_object,
                "changed source");
        const char mutation = 'X';
        if (::pwrite(changed_descriptor, &mutation, 1U, 13) != 1 ||
            ::fsync(changed_descriptor) != 0) {
            (void)::close(changed_descriptor);
            throw std::runtime_error("changed source mutation failed");
        }
        const fs::path changed_final = root.path() / "changed-final.bin";
        state.check(
            throws_publication_with_outcome(
                [&] {
                    anonsync::copy_sync_file_atomically_create_new_from_borrowed_descriptor_under_directory_or_throw(
                        root_authority, changed_final.filename(),
                        changed_descriptor, changed_observation.metadata,
                        changed_observation.content_sha256,
                        "changed streamed create");
                },
                "source changed before streaming publication",
                anonsync::SyncAtomicFilePublicationOutcome::NotPublished),
            "descriptor source publication rejects a stale source observation");
        state.check(!fs::exists(changed_final),
                    "changed descriptor source never publishes a final name");
        if (::close(changed_descriptor) != 0) {
            throw std::runtime_error("changed source close failed");
        }

        state.check(publication_temp_count(root.path()) == 2,
                    "two rejected descriptor copies retain only their private temp residues");
        for (const auto& entry : fs::directory_iterator(root.path())) {
            const std::string name = entry.path().filename().string();
            if (name.starts_with(".anonsync-publish-v1-") &&
                name.ends_with(".tmp")) {
                fs::remove(entry.path());
            }
        }
        state.check(publication_temp_count(root.path()) == 0,
                    "the test owner removed its two known copy-failure residues");
#endif

        const fs::path immutable = root.path() / "immutable-receipt.json";
        anonsync::preflight_sync_file_create_new_no_symlink_or_throw(
            immutable, "immutable receipt preflight");
        anonsync::write_sync_json_file_atomically_create_new_no_symlink_or_throw(
            immutable, "{\"receipt\":1}\n", "immutable receipt");
        state.check(read_binary(immutable) == "{\"receipt\":1}\n",
                    "create-new publication preserves exact bytes");
#if !defined(_WIN32)
        struct stat immutable_before {};
        struct stat immutable_after {};
        state.check(::stat(immutable.c_str(), &immutable_before) == 0,
                    "create-new publication exposes one inspectable inode");
#endif
        state.check(
            throws_publication_with_outcome(
                [&] {
                    anonsync::preflight_sync_file_create_new_no_symlink_or_throw(
                        immutable, "occupied immutable receipt preflight");
                },
                "immutable create-new final path already exists",
                anonsync::SyncAtomicFilePublicationOutcome::NotPublished),
            "create-new preflight rejects an occupied regular destination");
        state.check(
            throws_publication_with_outcome(
                [&] {
                    anonsync::write_sync_json_file_atomically_create_new_no_symlink_or_throw(
                        immutable, "{\"receipt\":2}\n",
                        "occupied immutable receipt");
                },
                "immutable create-new final path already exists",
                anonsync::SyncAtomicFilePublicationOutcome::NotPublished),
            "create-new publication rejects rather than replacing an existing file");
        state.check(read_binary(immutable) == "{\"receipt\":1}\n",
                    "rejected create-new publication preserves existing bytes");
#if !defined(_WIN32)
        state.check(::stat(immutable.c_str(), &immutable_after) == 0 &&
                        immutable_before.st_dev == immutable_after.st_dev &&
                        immutable_before.st_ino == immutable_after.st_ino,
                    "rejected create-new publication preserves existing inode identity");
#endif

        const fs::path symlink_target = root.path() / "symlink-target.txt";
        const fs::path symlink_final = root.path() / "symlink-final.json";
        write_binary(symlink_target, "do-not-touch");
        std::error_code symlink_ec;
        fs::create_symlink(symlink_target.filename(), symlink_final,
                           symlink_ec);
        if (!symlink_ec) {
            state.check(
                throws_with(
                    [&] {
                        anonsync::write_sync_json_file_atomically_no_symlink_or_throw(
                            symlink_final, "attacker-controlled",
                            "symlink rejection");
                    },
                    "must not be a symlink"),
                "existing final symlink is rejected");
            state.check(
                throws_publication_with_outcome(
                    [&] {
                        anonsync::write_sync_json_file_atomically_no_symlink_or_throw(
                            symlink_final, "attacker-controlled",
                            "typed symlink rejection");
                    },
                    "must not be a symlink",
                    anonsync::SyncAtomicFilePublicationOutcome::NotPublished),
                "existing final symlink rejection is typed not-published");
            state.check(read_binary(symlink_target) == "do-not-touch",
                        "symlink target is not modified");
            state.check(
                throws_publication_with_outcome(
                    [&] {
                        anonsync::preflight_sync_file_create_new_no_symlink_or_throw(
                            symlink_final,
                            "immutable symlink destination preflight");
                    },
                    "must not be a symlink",
                    anonsync::SyncAtomicFilePublicationOutcome::NotPublished),
                "create-new preflight rejects an occupied symlink destination");
            fs::remove(symlink_final);
            const fs::path fresh_after_symlink =
                root.path() / "fresh-after-symlink-denial.json";
            anonsync::preflight_sync_file_create_new_no_symlink_or_throw(
                fresh_after_symlink,
                "fresh immutable destination preflight");
            anonsync::write_sync_json_file_atomically_create_new_no_symlink_or_throw(
                fresh_after_symlink, "fresh-create-new-after-symlink\n",
                "fresh immutable destination after symlink denial");
            state.check(
                !fs::exists(symlink_final) &&
                    read_binary(fresh_after_symlink) ==
                    "fresh-create-new-after-symlink\n",
                "create-new publication succeeds at a distinct fresh name after symlink denial");
            state.check(read_binary(symlink_target) == "do-not-touch",
                        "fresh create-new publication preserves former symlink target");
        } else {
            state.check(true, "symlink creation unavailable; rejection skipped");
            state.check(true,
                        "symlink creation unavailable; typed rejection skipped");
            state.check(true, "symlink creation unavailable; target check skipped");
            state.check(
                true,
                "symlink creation unavailable; create-new preflight rejection skipped");
            state.check(
                true,
                "symlink creation unavailable; create-new after removal skipped");
            state.check(
                true,
                "symlink creation unavailable; former target preservation skipped");
        }

        const fs::path directory_final = root.path() / "directory-final.json";
        fs::create_directory(directory_final);
        state.check(
            throws_with(
                [&] {
                    anonsync::write_sync_json_file_atomically_no_symlink_or_throw(
                        directory_final, "not-a-directory",
                        "directory rejection");
                },
                "absent or a regular file"),
            "existing final directory is rejected");
        state.check(
            throws_publication_with_outcome(
                [&] {
                    anonsync::write_sync_json_file_atomically_no_symlink_or_throw(
                        directory_final, "not-a-directory",
                        "typed directory rejection");
                },
                "absent or a regular file",
                anonsync::SyncAtomicFilePublicationOutcome::NotPublished),
            "existing final directory rejection is typed not-published");
        state.check(fs::is_directory(directory_final),
                    "rejected final directory remains intact");

#if !defined(_WIN32)
        const fs::path parent_real = root.path() / "parent-real";
        const fs::path parent_link = root.path() / "parent-link";
        fs::create_directory(parent_real);
        fs::create_directory_symlink(parent_real.filename(), parent_link,
                                     symlink_ec);
        if (!symlink_ec) {
            state.check(
                throws_with(
                    [&] {
                        anonsync::write_sync_json_file_atomically_no_symlink_or_throw(
                            parent_link / "through-link.json", "blocked",
                            "parent symlink rejection");
                    },
                    "must not be a symlink"),
                "terminal parent-directory symlink is rejected");
            state.check(
                throws_publication_with_outcome(
                    [&] {
                        anonsync::write_sync_json_file_atomically_no_symlink_or_throw(
                            parent_link / "through-link.json", "blocked",
                            "typed parent symlink rejection");
                    },
                    "must not be a symlink",
                    anonsync::SyncAtomicFilePublicationOutcome::NotPublished),
                "parent-directory symlink rejection is typed not-published");
            state.check(!fs::exists(parent_real / "through-link.json"),
                        "rejected parent symlink publishes nothing");
        } else {
            state.check(true,
                        "directory symlink creation unavailable; rejection skipped");
            state.check(
                true,
                "directory symlink creation unavailable; typed rejection skipped");
            state.check(true,
                        "directory symlink creation unavailable; residue skipped");
        }

        const fs::path chain_real = root.path() / "chain-real";
        const fs::path chain_subdirectory = chain_real / "subdirectory";
        const fs::path chain_link = root.path() / "chain-link";
        fs::create_directories(chain_subdirectory);
        std::error_code chain_symlink_ec;
        fs::create_directory_symlink(chain_real.filename(), chain_link,
                                     chain_symlink_ec);
        if (!chain_symlink_ec) {
            state.check(
                throws_publication_with_outcome(
                    [&] {
                        anonsync::write_sync_json_file_atomically_no_symlink_or_throw(
                            chain_link / "subdirectory" / "report.json",
                            "blocked", "intermediate symlink rejection");
                    },
                    "component must not be a symlink",
                    anonsync::SyncAtomicFilePublicationOutcome::NotPublished),
                "intermediate parent-directory symlink is rejected");
            state.check(!fs::exists(chain_subdirectory / "report.json"),
                        "intermediate symlink target receives no publication");
        } else {
            state.check(
                true,
                "intermediate directory symlink unavailable; rejection skipped");
            state.check(
                true,
                "intermediate directory symlink unavailable; target check skipped");
        }

        const std::string legacy_payload = "stale-payload";
        const fs::path legacy_final = root.path() / "legacy-owner.json";
        const fs::path legacy_temp = fs::path(
            legacy_final.string() + ".tmp-" + std::to_string(::getpid()) +
            "-3d09516ea03936d4");
        write_binary(legacy_temp, "unrelated-active-owner");
        anonsync::write_sync_json_file_atomically_no_symlink_or_throw(
            legacy_final, legacy_payload, "legacy temp ownership");
        state.check(read_binary(legacy_final) == legacy_payload,
                    "legacy predictable temp does not block publication");
        state.check(read_binary(legacy_temp) == "unrelated-active-owner",
                    "legacy predictable temp is not deleted or overwritten");
#endif

        exercise_same_payload_threads(state, root.path());
        exercise_distinct_payload_threads(state, root.path());
#if defined(__linux__)
        exercise_same_payload_processes(state, root.path());
#endif

        const fs::path cli_report = root.path() / "cli-report.json";
        anonsync::write_sync_cli_report_json_or_throw(
            cli_report.string(), "{\"cli\":true}\n", "CLI report");
        state.check(read_binary(cli_report) == "{\"cli\":true}\n",
                    "CLI wrapper delegates exact publication");
        const fs::path cli_immutable = root.path() / "cli-immutable.json";
        anonsync::preflight_sync_cli_file_create_new_no_symlink_or_throw(
            cli_immutable.string(), "CLI immutable preflight");
        anonsync::write_sync_cli_immutable_json_create_new_or_throw(
            cli_immutable.string(), "{\"immutable\":true}\n",
            "CLI immutable publication");
        state.check(read_binary(cli_immutable) == "{\"immutable\":true}\n",
                    "CLI immutable wrapper delegates create-new publication");
        state.check(publication_temp_count(root.path()) == 0,
                    "all campaigns leave no module-owned temp residue");
        return state.finish();
    } catch (const std::exception& error) {
        std::cerr << "FATAL: " << error.what() << '\n';
        return 2;
    }
}
