#include "toxsync/range_source.hpp"

#include <cerrno>
#include <fstream>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>

#if defined(__unix__) || defined(__APPLE__)
#include <fcntl.h>
#include <unistd.h>
#endif

namespace toxsync {

void RangeSource::read_many(std::span<RangeRead> reads) {
    for (auto& read : reads) {
        std::size_t done{};
        while (done < read.output.size()) {
            const auto count = read_at(read.offset + done, read.output.subspan(done));
            if (count == 0U) {
                throw std::runtime_error("range source ended before requested target range");
            }
            if (count > read.output.size() - done) {
                throw std::runtime_error("range source returned an oversized read");
            }
            done += count;
        }
    }
}

class FileRangeSource::Impl final {
public:
    explicit Impl(const std::filesystem::path& path)
        : path_text(path.string()) {
#if defined(__unix__) || defined(__APPLE__)
        fd = ::open(path.c_str(), O_RDONLY | O_CLOEXEC);
        if (fd < 0) throw std::runtime_error("cannot open range source: " + path_text);
#else
        input.open(path, std::ios::binary);
        if (!input) throw std::runtime_error("cannot open range source: " + path_text);
#endif
    }

    ~Impl() {
#if defined(__unix__) || defined(__APPLE__)
        if (fd >= 0) (void)::close(fd);
#endif
    }

    std::string path_text;
#if defined(__unix__) || defined(__APPLE__)
    int fd{-1};
#else
    std::ifstream input;
#endif
};

FileRangeSource::FileRangeSource(const std::filesystem::path& path) : impl_(new Impl(path)) {}
FileRangeSource::~FileRangeSource() { delete impl_; }
FileRangeSource::FileRangeSource(FileRangeSource&& other) noexcept : impl_(std::exchange(other.impl_, nullptr)) {}
FileRangeSource& FileRangeSource::operator=(FileRangeSource&& other) noexcept {
    if (this != &other) {
        delete impl_;
        impl_ = std::exchange(other.impl_, nullptr);
    }
    return *this;
}

std::size_t FileRangeSource::read_at(std::uint64_t offset, std::span<std::byte> output) {
    if (impl_ == nullptr) throw std::runtime_error("range source was moved from");
    if (output.empty()) return 0U;
#if defined(__unix__) || defined(__APPLE__)
    if (offset > static_cast<std::uint64_t>(std::numeric_limits<off_t>::max())) {
        throw std::runtime_error("range source offset exceeds platform file limits");
    }
    for (;;) {
        const auto result = ::pread(impl_->fd, output.data(), output.size(), static_cast<off_t>(offset));
        if (result >= 0) return static_cast<std::size_t>(result);
        if (errno == EINTR) continue;
        throw std::runtime_error("range source read failed: " + impl_->path_text);
    }
#else
    impl_->input.clear();
    impl_->input.seekg(static_cast<std::streamoff>(offset), std::ios::beg);
    if (!impl_->input) throw std::runtime_error("range source seek failed: " + impl_->path_text);
    impl_->input.read(reinterpret_cast<char*>(output.data()), static_cast<std::streamsize>(output.size()));
    const auto count = impl_->input.gcount();
    if (count < 0) throw std::runtime_error("range source read failed: " + impl_->path_text);
    return static_cast<std::size_t>(count);
#endif
}

} // namespace toxsync
