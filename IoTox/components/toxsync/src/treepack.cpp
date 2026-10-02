#include "toxsync/treepack.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <fstream>
#include <memory>
#include <queue>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <type_traits>
#include <utility>
#include <vector>

namespace toxsync {
namespace {
constexpr std::array<char, 8> kMagic{'T', 'X', 'T', 'R', 'E', 'E', '1', '\0'};
constexpr std::uint32_t kVersion = 1U;
constexpr std::uint8_t kEnd = 0U;
constexpr std::uint8_t kDirectory = 1U;
constexpr std::uint8_t kFile = 2U;
constexpr std::size_t kEntryHeaderBytes = 20U;
std::atomic<std::uint64_t> g_sort_sequence{1U};

void write_u8(std::ostream& out, std::uint8_t value) {
    out.put(static_cast<char>(value));
}

template <typename T>
void write_le(std::ostream& out, T value) {
    static_assert(std::is_unsigned_v<T>);
    for (std::size_t i = 0; i < sizeof(T); ++i) {
        out.put(static_cast<char>(value >> (i * 8U)));
    }
}

template <typename T>
T read_le(std::istream& in) {
    static_assert(std::is_unsigned_v<T>);
    std::uint64_t value{};
    for (std::size_t i = 0; i < sizeof(T); ++i) {
        const int ch = in.get();
        if (ch == std::char_traits<char>::eof()) {
            throw std::runtime_error("truncated toxsync treepack");
        }
        value |= static_cast<std::uint64_t>(static_cast<unsigned char>(ch))
                 << (i * 8U);
    }
    return static_cast<T>(value);
}

std::string portable_relative(const std::filesystem::path& root,
                              const std::filesystem::path& path) {
    const auto relative = std::filesystem::relative(path, root);
    if (relative.empty() || relative.is_absolute()) {
        throw std::runtime_error("treepack could not derive a relative path");
    }
    std::string text = relative.generic_string();
    if (text.empty() || text == "." || text.front() == '/' ||
        text.find('\0') != std::string::npos) {
        throw std::runtime_error("treepack encountered an invalid relative path");
    }
    for (const auto& component : relative) {
        if (component == ".." || component == ".") {
            throw std::runtime_error("treepack path traversal rejected");
        }
    }
    return text;
}

std::filesystem::path safe_destination_path(const std::filesystem::path& root,
                                            std::string_view text) {
    if (text.empty() || text.front() == '/' ||
        text.find('\\') != std::string_view::npos ||
        text.find('\0') != std::string_view::npos) {
        throw std::runtime_error("treepack contains an unsafe path");
    }
    std::filesystem::path relative(text);
    if (relative.is_absolute()) {
        throw std::runtime_error("treepack contains an absolute path");
    }
    for (const auto& component : relative) {
        if (component == ".." || component == "." || component.empty()) {
            throw std::runtime_error("treepack contains path traversal");
        }
    }
    return root / relative;
}

bool executable(const std::filesystem::file_status& status) {
    using P = std::filesystem::perms;
    const auto permissions = status.permissions();
    return (permissions & (P::owner_exec | P::group_exec | P::others_exec)) !=
           P::none;
}

void copy_exact(std::istream& input, std::ostream& output, std::uint64_t bytes) {
    std::array<char, 256U * 1024U> buffer{};
    while (bytes != 0U) {
        const auto count = static_cast<std::streamsize>(
            std::min<std::uint64_t>(bytes, buffer.size()));
        input.read(buffer.data(), count);
        if (input.gcount() != count) {
            throw std::runtime_error("treepack input ended unexpectedly");
        }
        output.write(buffer.data(), count);
        if (!output) throw std::runtime_error("treepack output write failed");
        bytes -= static_cast<std::uint64_t>(count);
    }
}

void ensure_empty_destination(const std::filesystem::path& destination) {
    if (std::filesystem::exists(destination)) {
        if (!std::filesystem::is_directory(destination) ||
            std::filesystem::directory_iterator(destination) !=
                std::filesystem::directory_iterator{}) {
            throw std::runtime_error(
                "treepack destination must be absent or empty");
        }
    } else {
        std::filesystem::create_directories(destination);
    }
    std::filesystem::permissions(
        destination, std::filesystem::perms::owner_all,
        std::filesystem::perm_options::replace);
}

class TemporarySortDirectory final {
  public:
    TemporarySortDirectory() = default;
    ~TemporarySortDirectory() {
        if (!path_.empty()) {
            std::error_code ignored;
            std::filesystem::remove_all(path_, ignored);
        }
    }
    TemporarySortDirectory(const TemporarySortDirectory&) = delete;
    TemporarySortDirectory& operator=(const TemporarySortDirectory&) = delete;

    const std::filesystem::path& ensure() {
        if (!path_.empty()) return path_;
        const auto base = std::filesystem::temp_directory_path();
        for (unsigned int attempt = 0; attempt < 128U; ++attempt) {
            const auto sequence = g_sort_sequence.fetch_add(1U);
            const auto ticks = static_cast<unsigned long long>(
                std::chrono::steady_clock::now().time_since_epoch().count());
            auto candidate = base /
                ("toxsync-treepack-sort-" + std::to_string(ticks) + "-" +
                 std::to_string(sequence));
            std::error_code error;
            if (std::filesystem::create_directory(candidate, error)) {
                std::filesystem::permissions(
                    candidate,
                    std::filesystem::perms::owner_all,
                    std::filesystem::perm_options::replace,
                    error);
                if (error) {
                    std::filesystem::remove_all(candidate, error);
                    throw std::runtime_error(
                        "cannot make treepack sort directory private");
                }
                path_ = std::move(candidate);
                return path_;
            }
            if (error && error != std::errc::file_exists) {
                throw std::runtime_error(
                    "cannot create treepack sort directory: " +
                    error.message());
            }
        }
        throw std::runtime_error("cannot allocate a treepack sort directory");
    }

  private:
    std::filesystem::path path_;
};

void write_run_record(std::ostream& output, std::string_view path) {
    if (path.size() > std::numeric_limits<std::uint32_t>::max()) {
        throw std::runtime_error("treepack sort path cannot be encoded");
    }
    write_le<std::uint32_t>(output, static_cast<std::uint32_t>(path.size()));
    output.write(path.data(), static_cast<std::streamsize>(path.size()));
    if (!output) throw std::runtime_error("treepack sort-run write failed");
}

class RunReader final {
  public:
    RunReader(std::filesystem::path path, std::uint32_t max_path_bytes)
        : input_(std::move(path), std::ios::binary),
          max_path_bytes_(max_path_bytes) {
        if (!input_) throw std::runtime_error("cannot open treepack sort run");
    }

    bool next(std::string& output) {
        const int next = input_.peek();
        if (next == std::char_traits<char>::eof()) {
            if (!input_.eof()) {
                throw std::runtime_error("cannot inspect treepack sort run");
            }
            return false;
        }
        const auto length = read_le<std::uint32_t>(input_);
        if (length == 0U || length > max_path_bytes_) {
            throw std::runtime_error("treepack sort run has invalid path length");
        }
        output.assign(length, '\0');
        input_.read(output.data(), static_cast<std::streamsize>(length));
        if (static_cast<std::uint32_t>(input_.gcount()) != length) {
            throw std::runtime_error("truncated treepack sort run");
        }
        return true;
    }

  private:
    std::ifstream input_;
    std::uint32_t max_path_bytes_{};
};

struct MergeNode {
    std::string path;
    std::size_t reader{};
};

struct MergeNodeGreater {
    bool operator()(const MergeNode& left, const MergeNode& right) const {
        return left.path > right.path;
    }
};

template <typename Callback>
void merge_runs(const std::vector<std::filesystem::path>& runs,
                std::uint32_t max_path_bytes,
                Callback&& callback) {
    std::vector<std::unique_ptr<RunReader>> readers;
    readers.reserve(runs.size());
    std::vector<MergeNode> queue;
    queue.reserve(runs.size());
    for (const auto& run : runs) {
        readers.push_back(std::make_unique<RunReader>(run, max_path_bytes));
        std::string first;
        if (readers.back()->next(first)) {
            queue.push_back(MergeNode{std::move(first), readers.size() - 1U});
            std::push_heap(queue.begin(), queue.end(), MergeNodeGreater{});
        }
    }

    std::string previous;
    while (!queue.empty()) {
        std::pop_heap(queue.begin(), queue.end(), MergeNodeGreater{});
        auto node = std::move(queue.back());
        queue.pop_back();
        if (!previous.empty() && node.path <= previous) {
            throw std::runtime_error(
                "treepack source paths are not strictly canonical");
        }
        previous = node.path;
        callback(node.path);
        std::string next;
        if (readers[node.reader]->next(next)) {
            queue.push_back(MergeNode{std::move(next), node.reader});
            std::push_heap(queue.begin(), queue.end(), MergeNodeGreater{});
        }
    }
}

std::filesystem::path spill_run(
    std::vector<std::string>& paths,
    TemporarySortDirectory& temporary,
    std::uint64_t run_number) {
    std::sort(paths.begin(), paths.end());
    if (std::adjacent_find(paths.begin(), paths.end()) != paths.end()) {
        throw std::runtime_error("treepack source contains duplicate paths");
    }
    const auto path = temporary.ensure() /
                      ("run-" + std::to_string(run_number) + ".bin");
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("cannot create treepack sort run");
    for (const auto& entry : paths) write_run_record(output, entry);
    output.flush();
    if (!output) throw std::runtime_error("cannot flush treepack sort run");
    paths.clear();
    return path;
}

void validate_limits(const TreePackLimits& limits) {
    if (limits.max_entries == 0U || limits.max_file_size == 0U ||
        limits.max_artifact_bytes < 16U + kEntryHeaderBytes ||
        limits.max_path_bytes == 0U || limits.sort_memory_bytes == 0U ||
        limits.max_open_sort_runs < 2U) {
        throw std::invalid_argument("invalid toxsync treepack limits");
    }
}

} // namespace

TreePackStats pack_tree(const std::filesystem::path& root,
                        const std::filesystem::path& artifact,
                        const TreePackLimits& limits) {
    validate_limits(limits);
    if (!std::filesystem::is_directory(root)) {
        throw std::runtime_error("treepack root is not a directory");
    }

    TemporarySortDirectory temporary;
    std::vector<std::string> paths;
    std::vector<std::filesystem::path> runs;
    std::uint64_t buffered_bytes{};
    std::uint64_t entry_count{};
    TreePackStats stats;

    auto spill = [&] {
        if (paths.empty()) return;
        runs.push_back(spill_run(paths, temporary, runs.size()));
        ++stats.sort_runs;
        buffered_bytes = 0U;
    };

    for (std::filesystem::recursive_directory_iterator iterator(root), end;
         iterator != end; ++iterator) {
        const auto status = iterator->symlink_status();
        if (std::filesystem::is_symlink(status)) {
            throw std::runtime_error("treepack v1 rejects symbolic links");
        }
        if (!std::filesystem::is_directory(status) &&
            !std::filesystem::is_regular_file(status)) {
            throw std::runtime_error(
                "treepack v1 rejects special filesystem entries");
        }
        auto relative = portable_relative(root, iterator->path());
        if (relative.size() > limits.max_path_bytes) {
            throw std::runtime_error("treepack path limit exceeded");
        }
        ++entry_count;
        if (entry_count > limits.max_entries) {
            throw std::runtime_error("treepack entry limit exceeded");
        }
        // Account the canonical bytes, not an implementation-defined string
        // allocation. Product adapters can therefore choose a bound that is
        // guaranteed to keep this sort in memory without depending on the
        // standard library's growth policy.
        buffered_bytes += sizeof(std::string) + relative.size();
        paths.push_back(std::move(relative));
        stats.peak_sort_buffer_bytes = std::max(
            stats.peak_sort_buffer_bytes, buffered_bytes);
        if (buffered_bytes >= limits.sort_memory_bytes && paths.size() > 1U) {
            spill();
        }
    }

    if (!runs.empty()) {
        spill();
        const auto maximum_open = static_cast<std::size_t>(
            limits.max_open_sort_runs);
        std::uint64_t next_run_number = runs.size();
        while (runs.size() > maximum_open) {
            std::vector<std::filesystem::path> merged;
            merged.reserve((runs.size() + maximum_open - 1U) / maximum_open);
            for (std::size_t first = 0; first < runs.size();
                 first += maximum_open) {
                const auto last = std::min(runs.size(), first + maximum_open);
                std::vector<std::filesystem::path> group(
                    runs.begin() + static_cast<std::ptrdiff_t>(first),
                    runs.begin() + static_cast<std::ptrdiff_t>(last));
                const auto output_path = temporary.ensure() /
                    ("merge-" + std::to_string(next_run_number++) + ".bin");
                std::ofstream output(output_path,
                                     std::ios::binary | std::ios::trunc);
                if (!output) {
                    throw std::runtime_error(
                        "cannot create treepack merged sort run");
                }
                merge_runs(group, limits.max_path_bytes,
                           [&](std::string_view value) {
                               write_run_record(output, value);
                           });
                output.flush();
                if (!output) {
                    throw std::runtime_error(
                        "cannot flush treepack merged sort run");
                }
                for (const auto& old : group) {
                    std::error_code ignored;
                    std::filesystem::remove(old, ignored);
                }
                merged.push_back(output_path);
            }
            runs = std::move(merged);
            ++stats.sort_merge_passes;
        }
    } else {
        std::sort(paths.begin(), paths.end());
        if (std::adjacent_find(paths.begin(), paths.end()) != paths.end()) {
            throw std::runtime_error("treepack source contains duplicate paths");
        }
    }

    std::ofstream output(artifact, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("cannot create treepack artifact");
    output.write(kMagic.data(), static_cast<std::streamsize>(kMagic.size()));
    write_le<std::uint32_t>(output, kVersion);
    write_le<std::uint32_t>(output, 0U);
    std::uint64_t encoded_bytes = 16U;

    auto emit = [&](std::string_view relative) {
        const auto path = root / std::filesystem::path(relative);
        const auto status = std::filesystem::symlink_status(path);
        if (std::filesystem::is_symlink(status)) {
            throw std::runtime_error("treepack source changed into a symlink");
        }
        const bool is_directory = std::filesystem::is_directory(status);
        if (!is_directory && !std::filesystem::is_regular_file(status)) {
            throw std::runtime_error("treepack source entry disappeared or changed type");
        }
        const auto size = is_directory ? 0U : std::filesystem::file_size(path);
        if (size > limits.max_file_size) {
            throw std::runtime_error("treepack file limit exceeded");
        }
        const std::uint64_t fixed = kEntryHeaderBytes;
        const std::uint64_t path_bytes = relative.size();
        if (path_bytes > limits.max_artifact_bytes - fixed ||
            size > limits.max_artifact_bytes - fixed - path_bytes) {
            throw std::runtime_error("treepack artifact limit exceeded");
        }
        const std::uint64_t entry_bytes = fixed + path_bytes + size;
        if (entry_bytes > limits.max_artifact_bytes - kEntryHeaderBytes ||
            encoded_bytes > limits.max_artifact_bytes -
                                kEntryHeaderBytes - entry_bytes) {
            throw std::runtime_error("treepack artifact limit exceeded");
        }
        encoded_bytes += entry_bytes;
        write_u8(output, is_directory ? kDirectory : kFile);
        write_u8(output, executable(status) ? 1U : 0U);
        write_le<std::uint16_t>(output, 0U);
        write_le<std::uint32_t>(
            output, static_cast<std::uint32_t>(relative.size()));
        write_le<std::uint64_t>(output, size);
        write_le<std::uint32_t>(output, 0U);
        output.write(relative.data(),
                     static_cast<std::streamsize>(relative.size()));
        if (!output) throw std::runtime_error("treepack metadata write failed");
        if (is_directory) {
            ++stats.directories;
        } else {
            std::ifstream input(path, std::ios::binary);
            if (!input) {
                throw std::runtime_error("cannot read treepack source file");
            }
            copy_exact(input, output, size);
            ++stats.files;
            stats.content_bytes += size;
        }
    };

    if (runs.empty()) {
        for (const auto& path : paths) emit(path);
    } else {
        merge_runs(runs, limits.max_path_bytes, emit);
    }

    write_u8(output, kEnd);
    for (std::size_t i = 1; i < kEntryHeaderBytes; ++i) write_u8(output, 0U);
    output.flush();
    if (!output) throw std::runtime_error("treepack artifact flush failed");
    stats.artifact_bytes = std::filesystem::file_size(artifact);
    if (stats.artifact_bytes != encoded_bytes + kEntryHeaderBytes ||
        stats.artifact_bytes > limits.max_artifact_bytes) {
        throw std::runtime_error("treepack artifact size accounting failed");
    }
    return stats;
}

TreePackStats unpack_tree(const std::filesystem::path& artifact,
                          const std::filesystem::path& destination,
                          const TreePackLimits& limits) {
    validate_limits(limits);
    std::error_code artifact_error;
    const auto artifact_bytes = std::filesystem::file_size(
        artifact, artifact_error);
    if (artifact_error || artifact_bytes > limits.max_artifact_bytes) {
        throw std::runtime_error("treepack artifact size rejected");
    }
    ensure_empty_destination(destination);
    std::ifstream input(artifact, std::ios::binary);
    if (!input) throw std::runtime_error("cannot open treepack artifact");
    std::array<char, 8> magic{};
    input.read(magic.data(), static_cast<std::streamsize>(magic.size()));
    if (magic != kMagic) throw std::runtime_error("invalid toxsync treepack magic");
    if (read_le<std::uint32_t>(input) != kVersion ||
        read_le<std::uint32_t>(input) != 0U) {
        throw std::runtime_error("unsupported toxsync treepack header");
    }

    TreePackStats stats;
    std::string previous;
    while (true) {
        const auto type = read_le<std::uint8_t>(input);
        const auto flags = read_le<std::uint8_t>(input);
        const auto reserved16 = read_le<std::uint16_t>(input);
        const auto path_size = read_le<std::uint32_t>(input);
        const auto content_size = read_le<std::uint64_t>(input);
        const auto reserved32 = read_le<std::uint32_t>(input);
        if (type == kEnd) {
            if (flags != 0U || reserved16 != 0U || path_size != 0U ||
                content_size != 0U || reserved32 != 0U) {
                throw std::runtime_error("invalid treepack end marker");
            }
            break;
        }
        if (type != kDirectory && type != kFile) {
            throw std::runtime_error("unknown treepack entry type");
        }
        if ((flags & ~1U) != 0U || reserved16 != 0U || reserved32 != 0U) {
            throw std::runtime_error("treepack reserved bits are nonzero");
        }
        if (path_size == 0U || path_size > limits.max_path_bytes) {
            throw std::runtime_error("treepack path size rejected");
        }
        if (content_size > limits.max_file_size ||
            (type == kDirectory && content_size != 0U)) {
            throw std::runtime_error("treepack content size rejected");
        }
        std::string relative(path_size, '\0');
        input.read(relative.data(), static_cast<std::streamsize>(relative.size()));
        if (static_cast<std::size_t>(input.gcount()) != relative.size()) {
            throw std::runtime_error("truncated treepack path");
        }
        if (!previous.empty() && relative <= previous) {
            throw std::runtime_error("treepack paths are not strictly canonical");
        }
        previous = relative;
        if (stats.directories + stats.files >= limits.max_entries) {
            throw std::runtime_error("treepack entry limit exceeded");
        }
        const auto output_path = safe_destination_path(destination, relative);
        if (type == kDirectory) {
            std::filesystem::create_directories(output_path);
            std::filesystem::permissions(
                output_path, std::filesystem::perms::owner_all,
                std::filesystem::perm_options::replace);
            ++stats.directories;
        } else {
            std::filesystem::create_directories(output_path.parent_path());
            std::filesystem::permissions(
                output_path.parent_path(), std::filesystem::perms::owner_all,
                std::filesystem::perm_options::replace);
            std::ofstream output(output_path, std::ios::binary | std::ios::trunc);
            if (!output) throw std::runtime_error("cannot create unpacked file");
            copy_exact(input, output, content_size);
            output.close();
            using P = std::filesystem::perms;
            std::filesystem::permissions(
                output_path,
                P::owner_read | P::owner_write |
                    ((flags & 1U) != 0U ? P::owner_exec : P::none),
                std::filesystem::perm_options::replace);
            ++stats.files;
            stats.content_bytes += content_size;
        }
    }
    if (input.peek() != std::char_traits<char>::eof()) {
        throw std::runtime_error("treepack has trailing bytes");
    }
    stats.artifact_bytes = artifact_bytes;
    return stats;
}

} // namespace toxsync
