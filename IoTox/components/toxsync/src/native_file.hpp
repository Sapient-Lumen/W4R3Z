#pragma once

#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <limits>
#include <span>
#include <stdexcept>
#include <string>
#include <utility>

#if defined(__unix__) || defined(__APPLE__)
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace toxsync::detail {

enum class NativeOpenMode : std::uint8_t {
    read_only,
    read_write_create,
    read_write_create_exclusive,
    read_write_truncate,
};

class NativeFile final {
public:
    NativeFile() = default;

    NativeFile(const std::filesystem::path& path,
               NativeOpenMode mode,
               unsigned permissions = 0600U)
        : path_(path), path_text_(path.string()) {
#if defined(__unix__) || defined(__APPLE__)
        int flags = O_CLOEXEC;
        switch (mode) {
            case NativeOpenMode::read_only:
                flags |= O_RDONLY;
                break;
            case NativeOpenMode::read_write_create:
                flags |= O_RDWR | O_CREAT;
                break;
            case NativeOpenMode::read_write_create_exclusive:
                flags |= O_RDWR | O_CREAT | O_EXCL;
#if defined(O_NOFOLLOW)
                flags |= O_NOFOLLOW;
#endif
                break;
            case NativeOpenMode::read_write_truncate:
                flags |= O_RDWR | O_CREAT | O_TRUNC;
                break;
        }
        descriptor_ = ::open(path.c_str(), flags, static_cast<mode_t>(permissions));
        if (descriptor_ < 0) {
            throw std::runtime_error("cannot open file '" + path_text_ + "': " +
                                     std::strerror(errno));
        }
#else
        std::ios::openmode flags = std::ios::binary;
        switch (mode) {
            case NativeOpenMode::read_only:
                flags |= std::ios::in;
                break;
            case NativeOpenMode::read_write_create:
                if (!std::filesystem::exists(path)) {
                    std::ofstream create(path, std::ios::binary | std::ios::trunc);
                    if (!create) {
                        throw std::runtime_error("cannot create file '" + path_text_ + "'");
                    }
                }
                flags |= std::ios::in | std::ios::out;
                break;
            case NativeOpenMode::read_write_create_exclusive:
                if (std::filesystem::exists(path)) {
                    throw std::runtime_error("file already exists: '" + path_text_ + "'");
                }
                flags |= std::ios::in | std::ios::out | std::ios::trunc;
                break;
            case NativeOpenMode::read_write_truncate:
                flags |= std::ios::in | std::ios::out | std::ios::trunc;
                break;
        }
        stream_.open(path, flags);
        if (!stream_) throw std::runtime_error("cannot open file '" + path_text_ + "'");
        (void)permissions;
#endif
    }

    ~NativeFile() { close_noexcept(); }
    NativeFile(const NativeFile&) = delete;
    NativeFile& operator=(const NativeFile&) = delete;

    NativeFile(NativeFile&& other) noexcept { move_from(std::move(other)); }
    NativeFile& operator=(NativeFile&& other) noexcept {
        if (this != &other) {
            close_noexcept();
            move_from(std::move(other));
        }
        return *this;
    }

    [[nodiscard]] bool open() const noexcept {
#if defined(__unix__) || defined(__APPLE__)
        return descriptor_ >= 0;
#else
        return stream_.is_open();
#endif
    }

    [[nodiscard]] std::uint64_t size() const {
        require_open();
#if defined(__unix__) || defined(__APPLE__)
        struct stat status {};
        if (::fstat(descriptor_, &status) != 0 || status.st_size < 0) {
            throw_error("cannot inspect file size");
        }
        return static_cast<std::uint64_t>(status.st_size);
#else
        std::error_code error;
        const auto result = std::filesystem::file_size(path_, error);
        if (error) throw std::runtime_error("cannot inspect file size '" + path_text_ + "': " + error.message());
        return result;
#endif
    }

    [[nodiscard]] std::size_t read_at(std::uint64_t offset,
                                      std::span<std::byte> output) {
        require_open();
        if (output.empty()) return 0U;
#if defined(__unix__) || defined(__APPLE__)
        const auto platform_offset = checked_offset(offset);
        for (;;) {
            const ssize_t result = ::pread(descriptor_, output.data(), output.size(), platform_offset);
            if (result >= 0) return static_cast<std::size_t>(result);
            if (errno == EINTR) continue;
            throw_error("file read failed");
        }
#else
        if (offset > static_cast<std::uint64_t>(std::numeric_limits<std::streamoff>::max()) ||
            output.size() > static_cast<std::size_t>(std::numeric_limits<std::streamsize>::max())) {
            throw std::runtime_error("file read exceeds platform stream limits: " + path_text_);
        }
        stream_.clear();
        stream_.seekg(static_cast<std::streamoff>(offset), std::ios::beg);
        if (!stream_) throw std::runtime_error("file seek failed: " + path_text_);
        stream_.read(reinterpret_cast<char*>(output.data()),
                     static_cast<std::streamsize>(output.size()));
        const auto count = stream_.gcount();
        if (count < 0) throw std::runtime_error("file read failed: " + path_text_);
        return static_cast<std::size_t>(count);
#endif
    }

    void read_exact_at(std::uint64_t offset, std::span<std::byte> output) {
        std::size_t done{};
        while (done < output.size()) {
            const auto count = read_at(offset + done, output.subspan(done));
            if (count == 0U) {
                throw std::runtime_error("file ended before requested range: " + path_text_);
            }
            if (count > output.size() - done) {
                throw std::runtime_error("file returned oversized read: " + path_text_);
            }
            done += count;
        }
    }

    void write_exact_at(std::uint64_t offset, std::span<const std::byte> input) {
        require_open();
        std::size_t done{};
        while (done < input.size()) {
#if defined(__unix__) || defined(__APPLE__)
            const auto platform_offset = checked_offset(offset + done);
            const ssize_t result = ::pwrite(descriptor_, input.data() + done,
                                            input.size() - done, platform_offset);
            if (result > 0) {
                done += static_cast<std::size_t>(result);
                continue;
            }
            if (result < 0 && errno == EINTR) continue;
            throw_error("file write failed");
#else
            if (offset + done > static_cast<std::uint64_t>(std::numeric_limits<std::streamoff>::max()) ||
                input.size() - done > static_cast<std::size_t>(std::numeric_limits<std::streamsize>::max())) {
                throw std::runtime_error("file write exceeds platform stream limits: " + path_text_);
            }
            stream_.clear();
            stream_.seekp(static_cast<std::streamoff>(offset + done), std::ios::beg);
            if (!stream_) throw std::runtime_error("file write seek failed: " + path_text_);
            stream_.write(reinterpret_cast<const char*>(input.data() + done),
                          static_cast<std::streamsize>(input.size() - done));
            if (!stream_) throw std::runtime_error("file write failed: " + path_text_);
            done = input.size();
#endif
        }
    }

    void resize(std::uint64_t bytes) {
        require_open();
#if defined(__unix__) || defined(__APPLE__)
        const auto platform_size = checked_offset(bytes);
        if (::ftruncate(descriptor_, platform_size) != 0) {
            throw_error("cannot resize file");
        }
#else
        stream_.flush();
        std::filesystem::resize_file(path_, bytes);
#endif
    }

    void sync() {
        require_open();
#if defined(__unix__) || defined(__APPLE__)
        if (::fsync(descriptor_) != 0) throw_error("fsync failed");
#else
        stream_.flush();
        if (!stream_) throw std::runtime_error("flush failed: " + path_text_);
#endif
    }

    void advise_sequential() noexcept {
#if defined(__unix__) || defined(__APPLE__)
#if defined(POSIX_FADV_SEQUENTIAL)
        if (descriptor_ >= 0) {
            (void)::posix_fadvise(descriptor_, 0, 0, POSIX_FADV_SEQUENTIAL);
        }
#endif
#endif
    }

    void advise_random() noexcept {
#if defined(__unix__) || defined(__APPLE__)
#if defined(POSIX_FADV_RANDOM)
        if (descriptor_ >= 0) {
            (void)::posix_fadvise(descriptor_, 0, 0, POSIX_FADV_RANDOM);
        }
#endif
#endif
    }

    void advise_dont_need(std::uint64_t offset, std::uint64_t length) noexcept {
#if defined(__unix__) || defined(__APPLE__)
#if defined(POSIX_FADV_DONTNEED)
        if (descriptor_ >= 0 &&
            offset <= static_cast<std::uint64_t>(std::numeric_limits<off_t>::max()) &&
            length <= static_cast<std::uint64_t>(std::numeric_limits<off_t>::max())) {
            (void)::posix_fadvise(descriptor_, static_cast<off_t>(offset),
                                 static_cast<off_t>(length), POSIX_FADV_DONTNEED);
        }
#else
        (void)offset;
        (void)length;
#endif
#else
        (void)offset;
        (void)length;
#endif
    }

    void close() {
#if defined(__unix__) || defined(__APPLE__)
        if (descriptor_ >= 0) {
            const int descriptor = std::exchange(descriptor_, -1);
            if (::close(descriptor) != 0) throw_error("cannot close file");
        }
#else
        if (stream_.is_open()) {
            stream_.close();
            if (stream_.fail()) throw std::runtime_error("cannot close file: " + path_text_);
        }
#endif
    }

    [[nodiscard]] const std::filesystem::path& path() const noexcept { return path_; }
    [[nodiscard]] const std::string& path_text() const noexcept { return path_text_; }

private:
#if defined(__unix__) || defined(__APPLE__)
    [[nodiscard]] static off_t checked_offset(std::uint64_t offset) {
        if (offset > static_cast<std::uint64_t>(std::numeric_limits<off_t>::max())) {
            throw std::runtime_error("file offset exceeds platform limits");
        }
        return static_cast<off_t>(offset);
    }
#endif

    [[noreturn]] void throw_error(const char* action) const {
        const int saved = errno;
        throw std::runtime_error(std::string(action) + " '" + path_text_ + "': " +
                                 std::strerror(saved));
    }

    void require_open() const {
        if (!open()) throw std::runtime_error("file is closed or moved from: " + path_text_);
    }

    void close_noexcept() noexcept {
#if defined(__unix__) || defined(__APPLE__)
        if (descriptor_ >= 0) (void)::close(descriptor_);
        descriptor_ = -1;
#else
        if (stream_.is_open()) stream_.close();
#endif
    }

    void move_from(NativeFile&& other) noexcept {
        path_ = std::move(other.path_);
        path_text_ = std::move(other.path_text_);
#if defined(__unix__) || defined(__APPLE__)
        descriptor_ = std::exchange(other.descriptor_, -1);
#else
        stream_ = std::move(other.stream_);
#endif
    }

    std::filesystem::path path_{};
    std::string path_text_{};
#if defined(__unix__) || defined(__APPLE__)
    int descriptor_{-1};
#else
    std::fstream stream_{};
#endif
};

} // namespace toxsync::detail
