#include "bzip4/pinned_file.hpp"

#include <algorithm>
#include <cerrno>
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

[[noreturn]] void throw_errno(
    std::string_view operation,
    const std::filesystem::path& path,
    int error_number = errno) {
    throw std::system_error(
        error_number,
        std::generic_category(),
        std::string(operation) + ": " + path.string());
}

struct FileFingerprint {
    dev_t device{};
    ino_t inode{};
    off_t size{};
    time_t mtime_seconds{};
    long mtime_nanoseconds{};
    time_t ctime_seconds{};
    long ctime_nanoseconds{};

    [[nodiscard]] bool operator==(const FileFingerprint&) const noexcept = default;
};

[[nodiscard]] FileFingerprint fingerprint(const struct stat& status) noexcept {
    return {
        status.st_dev,
        status.st_ino,
        status.st_size,
        status.st_mtim.tv_sec,
        status.st_mtim.tv_nsec,
        status.st_ctim.tv_sec,
        status.st_ctim.tv_nsec,
    };
}

[[nodiscard]] bool current_fingerprint(
    int descriptor,
    FileFingerprint& output,
    int& error_number) noexcept {
    struct stat status{};
    if (::fstat(descriptor, &status) != 0) {
        error_number = errno;
        return false;
    }
    output = fingerprint(status);
    error_number = 0;
    return true;
}

} // namespace

class PinnedFile::Impl final {
public:
    explicit Impl(const std::filesystem::path& path) : path_(path) {
        descriptor_ = ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
        if (descriptor_ < 0) {
            throw_errno("open pinned input", path_);
        }

        struct stat status{};
        if (::fstat(descriptor_, &status) != 0) {
            const int saved = errno;
            (void)::close(descriptor_);
            descriptor_ = -1;
            throw_errno("fstat pinned input", path_, saved);
        }
        if (!S_ISREG(status.st_mode) || status.st_size < 0) {
            (void)::close(descriptor_);
            descriptor_ = -1;
            throw std::runtime_error("pinned input is not a regular file: " + path_.string());
        }
        initial_ = fingerprint(status);
        size_ = static_cast<std::uint64_t>(status.st_size);
    }

    ~Impl() {
        if (descriptor_ >= 0) {
            (void)::close(descriptor_);
        }
    }

    Impl(const Impl&) = delete;
    Impl& operator=(const Impl&) = delete;

    [[nodiscard]] std::uint64_t size() const noexcept { return size_; }

    [[nodiscard]] bool read_exact(
        std::uint64_t offset,
        std::span<std::byte> output) const noexcept {
        if (offset > size_ || output.size() > size_ - offset ||
            offset > static_cast<std::uint64_t>(std::numeric_limits<off_t>::max())) {
            return false;
        }

        std::size_t done = 0;
        while (done < output.size()) {
            const std::uint64_t position = offset + done;
            if (position > static_cast<std::uint64_t>(std::numeric_limits<off_t>::max())) {
                return false;
            }
            const std::size_t request = std::min<std::size_t>(
                output.size() - done,
                static_cast<std::size_t>(std::numeric_limits<ssize_t>::max()));
            const ssize_t count = ::pread(
                descriptor_,
                output.data() + static_cast<std::ptrdiff_t>(done),
                request,
                static_cast<off_t>(position));
            if (count < 0 && errno == EINTR) {
                continue;
            }
            if (count <= 0) {
                return false;
            }
            done += static_cast<std::size_t>(count);
        }
        return true;
    }

    [[nodiscard]] std::vector<std::byte> read(
        std::uint64_t offset,
        std::size_t size) const {
        std::vector<std::byte> output(size);
        read_into(offset, output);
        return output;
    }

    void read_into(
        std::uint64_t offset,
        std::span<std::byte> output) const {
        if (offset > size_ || output.size() > size_ - offset) {
            throw std::out_of_range(
                "read range exceeds pinned input snapshot: " + path_.string());
        }
        if (!read_exact(offset, output)) {
            throw std::runtime_error("short read from pinned input: " + path_.string());
        }
    }

    [[nodiscard]] std::vector<std::byte> read_all() const {
        if (size_ > std::numeric_limits<std::size_t>::max()) {
            throw std::runtime_error("pinned input is too large for this process: " + path_.string());
        }
        std::vector<std::byte> output = read(0, static_cast<std::size_t>(size_));
        require_unchanged();
        return output;
    }

    [[nodiscard]] bool unchanged() const noexcept {
        FileFingerprint current{};
        int ignored = 0;
        return current_fingerprint(descriptor_, current, ignored) && current == initial_;
    }

    void require_unchanged() const {
        FileFingerprint current{};
        int error_number = 0;
        if (!current_fingerprint(descriptor_, current, error_number)) {
            throw_errno("recheck pinned input", path_, error_number);
        }
        if (current != initial_) {
            throw std::runtime_error(
                "pinned input changed while it was being read: " + path_.string());
        }
    }

private:
    int descriptor_{-1};
    std::filesystem::path path_;
    FileFingerprint initial_{};
    std::uint64_t size_{};
};

PinnedFile::PinnedFile(const std::filesystem::path& path)
    : impl_(std::make_unique<Impl>(path)) {}

PinnedFile::~PinnedFile() = default;

std::uint64_t PinnedFile::size() const noexcept {
    return impl_->size();
}

bool PinnedFile::read_exact(
    std::uint64_t offset,
    std::span<std::byte> output) const noexcept {
    return impl_->read_exact(offset, output);
}

void PinnedFile::read_into(
    std::uint64_t offset,
    std::span<std::byte> output) const {
    impl_->read_into(offset, output);
}

std::vector<std::byte> PinnedFile::read(
    std::uint64_t offset,
    std::size_t size) const {
    return impl_->read(offset, size);
}

std::vector<std::byte> PinnedFile::read_all() const {
    return impl_->read_all();
}

bool PinnedFile::unchanged() const noexcept {
    return impl_->unchanged();
}

void PinnedFile::require_unchanged() const {
    impl_->require_unchanged();
}

} // namespace bzip4
