#include "bzip4/atomic_file.hpp"

#include <algorithm>
#include <atomic>
#include <cerrno>
#include <cstdio>
#include <fcntl.h>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace bzip4 {
namespace {

[[noreturn]] void throw_errno(std::string_view operation, int error_number = errno) {
    throw std::system_error(error_number, std::generic_category(), std::string(operation));
}

[[nodiscard]] std::string path_component(const std::filesystem::path& path) {
    const std::string value = path.native();
    if (value.empty() || value == "." || value == ".." || value.find('\0') != std::string::npos ||
        value.find('/') != std::string::npos) {
        throw std::invalid_argument("atomic output requires a nonempty destination filename");
    }
    return value;
}

[[nodiscard]] std::string make_temporary_name(std::uint64_t serial) {
    char buffer[96]{};
    const int count = std::snprintf(
        buffer, sizeof(buffer), ".bzip4-tmp-%lld-%llu",
        static_cast<long long>(::getpid()),
        static_cast<unsigned long long>(serial));
    if (count <= 0 || static_cast<std::size_t>(count) >= sizeof(buffer)) {
        throw std::runtime_error("unable to format temporary output name");
    }
    return {buffer, static_cast<std::size_t>(count)};
}

} // namespace

class AtomicFileWriter::Impl final {
public:
    explicit Impl(const std::filesystem::path& destination, std::uint32_t permissions)
        : destination_name_(path_component(destination.filename())) {
        if ((permissions & ~0777U) != 0U) {
            throw std::invalid_argument("atomic output permissions must fit POSIX mode bits");
        }

        const std::filesystem::path parent = destination.has_parent_path()
            ? destination.parent_path() : std::filesystem::path{"."};
        directory_fd_ = ::open(parent.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC);
        if (directory_fd_ < 0) {
            throw_errno("open output directory");
        }

        try {
            static std::atomic<std::uint64_t> next_serial{0};
            for (unsigned attempt = 0; attempt < 256U; ++attempt) {
                const std::uint64_t serial = next_serial.fetch_add(1, std::memory_order_relaxed);
                temporary_name_ = make_temporary_name(serial);
                file_fd_ = ::openat(
                    directory_fd_, temporary_name_.c_str(),
                    O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC,
                    static_cast<mode_t>(permissions));
                if (file_fd_ >= 0) {
                    return;
                }
                if (errno != EEXIST) {
                    throw_errno("create temporary output");
                }
            }
            throw std::runtime_error("unable to allocate a unique temporary output name");
        } catch (...) {
            if (file_fd_ >= 0) {
                (void)::close(file_fd_);
                file_fd_ = -1;
            }
            // No temporary name is owned until openat(O_EXCL) succeeds. In
            // particular, never unlink a colliding name created by another
            // process while unwinding constructor failure.
            close_directory();
            throw;
        }
    }

    ~Impl() {
        if (file_fd_ >= 0) {
            (void)::close(file_fd_);
            file_fd_ = -1;
        }
        if (!published_ && directory_fd_ >= 0 && !temporary_name_.empty()) {
            (void)::unlinkat(directory_fd_, temporary_name_.c_str(), 0);
        }
        close_directory();
    }

    Impl(const Impl&) = delete;
    Impl& operator=(const Impl&) = delete;

    void write(std::span<const std::byte> bytes) {
        if (published_ || file_fd_ < 0) {
            throw std::logic_error("cannot write after atomic output publication");
        }
        if (bytes.size() > std::numeric_limits<std::uint64_t>::max() - bytes_written_) {
            throw std::overflow_error("atomic output byte counter overflow");
        }

        std::size_t offset = 0;
        while (offset < bytes.size()) {
            const std::size_t remaining = bytes.size() - offset;
            const std::size_t request = std::min<std::size_t>(
                remaining, static_cast<std::size_t>(std::numeric_limits<ssize_t>::max()));
            const ssize_t count = ::write(
                file_fd_, bytes.data() + static_cast<std::ptrdiff_t>(offset), request);
            if (count < 0 && errno == EINTR) {
                continue;
            }
            if (count < 0) {
                throw_errno("write temporary output");
            }
            if (count == 0) {
                throw std::runtime_error("write temporary output made no progress");
            }
            offset += static_cast<std::size_t>(count);
        }
        bytes_written_ += static_cast<std::uint64_t>(bytes.size());
    }

    void commit() {
        if (published_) {
            throw std::logic_error("atomic output has already been published");
        }
        if (file_fd_ < 0) {
            throw std::logic_error("atomic output staging file is not open");
        }

        if (::fsync(file_fd_) != 0) {
            throw_errno("fsync temporary output");
        }

        const int close_result = ::close(file_fd_);
        const int close_error = errno;
        // Do not retry close(): after EINTR, whether the descriptor remains open
        // is platform-dependent, and retrying could close a reused descriptor.
        file_fd_ = -1;
        if (close_result != 0) {
            throw_errno("close temporary output", close_error);
        }

        if (::renameat(
                directory_fd_, temporary_name_.c_str(),
                directory_fd_, destination_name_.c_str()) != 0) {
            throw_errno("publish atomic output");
        }

        // Publication has happened. From this point the destructor must never
        // unlink the name, even when the durability flush fails.
        published_ = true;
        temporary_name_.clear();

        if (::fsync(directory_fd_) != 0) {
            throw_errno("fsync output directory after publication");
        }
        durable_ = true;
    }

    [[nodiscard]] std::uint64_t bytes_written() const noexcept { return bytes_written_; }
    [[nodiscard]] bool published() const noexcept { return published_; }
    [[nodiscard]] bool durable() const noexcept { return durable_; }

private:
    void close_directory() noexcept {
        if (directory_fd_ >= 0) {
            (void)::close(directory_fd_);
            directory_fd_ = -1;
        }
    }

    int directory_fd_{-1};
    int file_fd_{-1};
    std::string destination_name_;
    std::string temporary_name_;
    std::uint64_t bytes_written_{};
    bool published_{};
    bool durable_{};
};

AtomicFileWriter::AtomicFileWriter(
    const std::filesystem::path& destination,
    std::uint32_t permissions)
    : impl_(std::make_unique<Impl>(destination, permissions)) {}

AtomicFileWriter::~AtomicFileWriter() = default;

void AtomicFileWriter::write(std::span<const std::byte> bytes) {
    impl_->write(bytes);
}

void AtomicFileWriter::commit() {
    impl_->commit();
}

std::uint64_t AtomicFileWriter::bytes_written() const noexcept {
    return impl_->bytes_written();
}

bool AtomicFileWriter::published() const noexcept {
    return impl_->published();
}

bool AtomicFileWriter::durable() const noexcept {
    return impl_->durable();
}

} // namespace bzip4
