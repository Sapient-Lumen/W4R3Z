#include "toxsync/apply.hpp"

#include "artifact_hasher.hpp"

#include <algorithm>
#include <cerrno>
#include <cstring>
#include <fstream>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#if defined(__unix__) || defined(__APPLE__)
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace toxsync {
namespace {

[[nodiscard]] std::filesystem::path part_path_for(const std::filesystem::path& output) {
    auto path = output;
    path += ".toxsync.part";
    return path;
}

void ensure_parent(const std::filesystem::path& output) {
    const auto parent = output.parent_path();
    if (!parent.empty()) std::filesystem::create_directories(parent);
}

void atomic_replace(const std::filesystem::path& source, const std::filesystem::path& destination) {
#if defined(__unix__) || defined(__APPLE__)
    if (::rename(source.c_str(), destination.c_str()) != 0) {
        throw std::runtime_error("atomic rename failed: " + std::string(std::strerror(errno)));
    }
#else
    std::error_code error;
    std::filesystem::remove(destination, error);
    error.clear();
    std::filesystem::rename(source, destination, error);
    if (error) throw std::runtime_error("rename failed: " + error.message());
#endif
}

class PartialFile final {
public:
    PartialFile(const std::filesystem::path& path, bool preserve)
        : path_(path), path_text_(path.string()) {
#if defined(__unix__) || defined(__APPLE__)
        int flags = O_RDWR | O_CREAT | O_CLOEXEC;
        if (!preserve) flags |= O_TRUNC;
        fd_ = ::open(path.c_str(), flags, S_IRUSR | S_IWUSR);
        if (fd_ < 0) throw std::runtime_error("cannot open partial output: " + path_text_ + ": " + std::strerror(errno));
#else
        if (!preserve || !std::filesystem::exists(path)) {
            std::ofstream create(path, std::ios::binary | std::ios::trunc);
            if (!create) throw std::runtime_error("cannot create partial output: " + path_text_);
        }
        stream_.open(path, std::ios::binary | std::ios::in | std::ios::out);
        if (!stream_) throw std::runtime_error("cannot open partial output: " + path_text_);
#endif
    }

    ~PartialFile() { close_noexcept(); }
    PartialFile(const PartialFile&) = delete;
    PartialFile& operator=(const PartialFile&) = delete;

    [[nodiscard]] std::uint64_t size() const {
#if defined(__unix__) || defined(__APPLE__)
        struct stat status {};
        if (::fstat(fd_, &status) != 0 || status.st_size < 0) {
            throw std::runtime_error("cannot inspect partial output: " + path_text_);
        }
        return static_cast<std::uint64_t>(status.st_size);
#else
        std::error_code error;
        const auto result = std::filesystem::file_size(path_, error);
        if (error) throw std::runtime_error("cannot inspect partial output: " + path_text_);
        return result;
#endif
    }

    void resize(std::uint64_t bytes) {
#if defined(__unix__) || defined(__APPLE__)
        if (bytes > static_cast<std::uint64_t>(std::numeric_limits<off_t>::max()) ||
            ::ftruncate(fd_, static_cast<off_t>(bytes)) != 0) {
            throw std::runtime_error("cannot resize partial output: " + path_text_ + ": " + std::strerror(errno));
        }
#else
        stream_.flush();
        std::filesystem::resize_file(path_, bytes);
#endif
    }

    void set_write_offset(std::uint64_t offset) {
#if defined(__unix__) || defined(__APPLE__)
        if (offset > static_cast<std::uint64_t>(std::numeric_limits<off_t>::max()) ||
            ::lseek(fd_, static_cast<off_t>(offset), SEEK_SET) < 0) {
            throw std::runtime_error("cannot seek partial output: " + path_text_);
        }
#else
        stream_.clear();
        stream_.seekp(static_cast<std::streamoff>(offset), std::ios::beg);
        if (!stream_) throw std::runtime_error("cannot seek partial output: " + path_text_);
#endif
    }

    void read_exact(std::uint64_t offset, std::span<std::byte> output) {
#if defined(__unix__) || defined(__APPLE__)
        std::size_t done{};
        while (done < output.size()) {
            const auto absolute = offset + done;
            if (absolute > static_cast<std::uint64_t>(std::numeric_limits<off_t>::max())) {
                throw std::runtime_error("partial output offset exceeds platform file limits");
            }
            const auto result = ::pread(fd_, output.data() + done, output.size() - done,
                                        static_cast<off_t>(absolute));
            if (result > 0) {
                done += static_cast<std::size_t>(result);
                continue;
            }
            if (result < 0 && errno == EINTR) continue;
            throw std::runtime_error("cannot read resumable partial output: " + path_text_);
        }
#else
        stream_.clear();
        stream_.seekg(static_cast<std::streamoff>(offset), std::ios::beg);
        stream_.read(reinterpret_cast<char*>(output.data()), static_cast<std::streamsize>(output.size()));
        if (static_cast<std::size_t>(stream_.gcount()) != output.size()) {
            throw std::runtime_error("cannot read resumable partial output: " + path_text_);
        }
#endif
    }

    void write_all(std::span<const std::byte> bytes) {
#if defined(__unix__) || defined(__APPLE__)
        std::size_t done{};
        while (done < bytes.size()) {
            const auto result = ::write(fd_, bytes.data() + done, bytes.size() - done);
            if (result > 0) {
                done += static_cast<std::size_t>(result);
                continue;
            }
            if (result < 0 && errno == EINTR) continue;
            throw std::runtime_error("failed while writing partial output: " + path_text_);
        }
#else
        stream_.write(reinterpret_cast<const char*>(bytes.data()), static_cast<std::streamsize>(bytes.size()));
        if (!stream_) throw std::runtime_error("failed while writing partial output: " + path_text_);
#endif
    }

    void sync(bool enabled) {
#if defined(__unix__) || defined(__APPLE__)
        if (enabled && ::fsync(fd_) != 0) {
            throw std::runtime_error("fsync failed: " + std::string(std::strerror(errno)));
        }
#else
        stream_.flush();
        if (!stream_) throw std::runtime_error("failed while flushing partial output: " + path_text_);
        (void)enabled;
#endif
    }

    void close() {
#if defined(__unix__) || defined(__APPLE__)
        if (fd_ >= 0) {
            if (::close(fd_) != 0) {
                fd_ = -1;
                throw std::runtime_error("cannot close partial output: " + path_text_);
            }
            fd_ = -1;
        }
#else
        stream_.close();
        if (stream_.fail()) throw std::runtime_error("cannot close partial output: " + path_text_);
#endif
    }

private:
    void close_noexcept() noexcept {
#if defined(__unix__) || defined(__APPLE__)
        if (fd_ >= 0) (void)::close(fd_);
        fd_ = -1;
#else
        if (stream_.is_open()) stream_.close();
#endif
    }

    std::filesystem::path path_;
    std::string path_text_;
#if defined(__unix__) || defined(__APPLE__)
    int fd_{-1};
#else
    std::fstream stream_;
#endif
};

[[nodiscard]] std::uint64_t normalized_resume_size(const Index& index,
                                                    const PartialFile& partial,
                                                    bool resume) {
    if (!resume) return 0U;
    auto size = std::min(partial.size(), index.target_size);
    if (size == index.target_size) return size;
    return (size / index.block_size) * index.block_size;
}

void read_source_exact(RangeSource& source,
                       std::uint64_t offset,
                       std::span<std::byte> output,
                       std::size_t& received,
                       std::uint64_t& read_calls) {
    while (received < output.size()) {
        const auto got = source.read_at(offset + received, output.subspan(received));
        ++read_calls;
        if (got == 0U) throw std::runtime_error("range source ended before requested target range");
        if (got > output.size() - received) throw std::runtime_error("range source returned an oversized read");
        received += got;
    }
}

void hash_prefix(PartialFile& partial,
                 std::uint64_t bytes,
                 std::span<std::byte> buffer,
                 detail::ArtifactSha256& digest,
                 ApplyStats& stats) {
    std::uint64_t offset{};
    while (offset < bytes) {
        const auto count = static_cast<std::size_t>(std::min<std::uint64_t>(bytes - offset, buffer.size()));
        auto chunk = buffer.first(count);
        partial.read_exact(offset, chunk);
        ++stats.partial_read_calls;
        digest.update(chunk);
        offset += count;
    }
}

} // namespace

ApplyStats apply_file(const Index& index,
                      const Plan& plan,
                      const std::filesystem::path& basis_path,
                      RangeSource& source,
                      const std::filesystem::path& output,
                      const ApplyOptions& options) {
    index.validate();
    if (plan.basis_offsets.size() != index.blocks.size()) {
        throw std::invalid_argument("plan block count does not match index");
    }
    if (options.io_buffer_bytes == 0U) throw std::invalid_argument("I/O buffer size must be nonzero");

    ensure_parent(output);
    const auto part = part_path_for(output);
    const bool preserve = options.resume && std::filesystem::exists(part);
    PartialFile partial(part, preserve);
    const auto resume_bytes = normalized_resume_size(index, partial, options.resume);
    partial.resize(resume_bytes);
    partial.set_write_offset(resume_bytes);

    const auto block_bytes = static_cast<std::size_t>(index.block_size);
    const auto requested_buffer = std::max(options.io_buffer_bytes, block_bytes);
    const auto buffer_bytes = (requested_buffer / block_bytes) * block_bytes;
    auto buffer = std::make_unique_for_overwrite<std::byte[]>(buffer_bytes);
    ApplyStats stats;
    stats.resumed_bytes = resume_bytes;
    stats.buffer_bytes = buffer_bytes;
    detail::ArtifactSha256 digest;
    hash_prefix(partial, resume_bytes, std::span<std::byte>(buffer.get(), buffer_bytes), digest, stats);
    partial.set_write_offset(resume_bytes);

    bool needs_basis{};
    const auto first_block = resume_bytes == index.target_size
        ? index.blocks.size()
        : static_cast<std::size_t>(resume_bytes / index.block_size);
    for (std::size_t i = first_block; i < plan.basis_offsets.size(); ++i) {
        if (plan.basis_offsets[i] != kMissingBasisOffset) {
            needs_basis = true;
            break;
        }
    }
    std::unique_ptr<FileRangeSource> basis;
    if (needs_basis) basis = std::make_unique<FileRangeSource>(basis_path);

    std::size_t block_index = first_block;
    std::uint64_t target_offset = resume_bytes;
    while (block_index < index.blocks.size()) {
        std::size_t batch_end = block_index;
        std::size_t batch_length{};
        while (batch_end < index.blocks.size()) {
            const auto length = static_cast<std::size_t>(index.blocks[batch_end].length);
            if (batch_length != 0U && length > buffer_bytes - batch_length) break;
            batch_length += length;
            ++batch_end;
            if (batch_length == buffer_bytes) break;
        }

        std::size_t run_index = block_index;
        std::size_t filled{};
        while (run_index < batch_end) {
            const bool reused = plan.basis_offsets[run_index] != kMissingBasisOffset;
            const auto run_source_offset = reused
                ? plan.basis_offsets[run_index]
                : target_offset + filled;
            std::size_t run_length = index.blocks[run_index].length;
            auto next = run_index + 1U;
            while (next < batch_end) {
                const bool next_reused = plan.basis_offsets[next] != kMissingBasisOffset;
                if (next_reused != reused) break;
                if (reused && plan.basis_offsets[next] != run_source_offset + run_length) break;
                run_length += index.blocks[next].length;
                ++next;
            }

            if (reused) ++stats.basis_runs;
            else ++stats.source_runs;
            auto chunk = std::span<std::byte>(buffer.get() + filled, run_length);
            std::size_t received{};
            try {
                if (reused) {
                    read_source_exact(*basis, run_source_offset, chunk, received,
                                      stats.basis_read_calls);
                } else {
                    read_source_exact(source, run_source_offset, chunk, received,
                                      stats.source_read_calls);
                }
            } catch (...) {
                const auto checkpoint = ((filled + received) / block_bytes) * block_bytes;
                if (checkpoint != 0U) {
                    partial.write_all(std::span<const std::byte>(buffer.get(), checkpoint));
                }
                throw;
            }
            if (reused) stats.reused_bytes += run_length;
            else stats.fetched_bytes += run_length;
            filled += run_length;
            run_index = next;
        }

        const auto batch = std::span<const std::byte>(buffer.get(), batch_length);
        partial.write_all(batch);
        ++stats.output_write_calls;
        digest.update(batch);
        target_offset += batch_length;
        block_index = batch_end;
    }

    stats.output_digest = digest.finish();
    if (stats.output_digest != index.target_digest) {
        partial.close();
        std::error_code ignored;
        std::filesystem::remove(part, ignored);
        throw std::runtime_error("reconstructed artifact failed SHA-256 verification");
    }
    partial.sync(options.fsync_on_commit);
    if (options.fsync_on_commit) ++stats.sync_calls;
    partial.close();
    atomic_replace(part, output);
    return stats;
}

bool verify_file(const Index& index, const std::filesystem::path& path) {
    std::error_code error;
    if (std::filesystem::file_size(path, error) != index.target_size || error) return false;
    return sha256_file(path.string()) == index.target_digest;
}

} // namespace toxsync
