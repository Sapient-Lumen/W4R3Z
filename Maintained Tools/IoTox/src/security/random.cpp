#include "iotox/security/random.hpp"

#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <string>
#include <sys/random.h>
#include <unistd.h>

namespace iotox::security {
namespace {

Status read_urandom(std::span<std::uint8_t> output) {
    int descriptor = -1;
    do {
        descriptor = ::open("/dev/urandom", O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        return Status{ErrorCode::io_error,
                      "unable to open /dev/urandom: " + std::string(std::strerror(errno))};
    }

    std::size_t offset = 0U;
    while (offset < output.size()) {
        const ssize_t count = ::read(
            descriptor, output.data() + static_cast<std::ptrdiff_t>(offset),
            output.size() - offset);
        if (count < 0 && errno == EINTR) {
            continue;
        }
        if (count < 0) {
            const int saved_errno = errno;
            (void)::close(descriptor);
            return Status{ErrorCode::io_error,
                          "unable to read /dev/urandom: " +
                              std::string(std::strerror(saved_errno))};
        }
        if (count == 0) {
            (void)::close(descriptor);
            return Status{ErrorCode::io_error,
                          "/dev/urandom returned an unexpected end of file"};
        }
        offset += static_cast<std::size_t>(count);
    }

    if (::close(descriptor) != 0) {
        return Status{ErrorCode::io_error,
                      "unable to close /dev/urandom: " +
                          std::string(std::strerror(errno))};
    }
    return Status::success();
}

bool all_zero(std::span<const std::uint8_t> bytes) {
    for (const std::uint8_t byte : bytes) {
        if (byte != 0U) {
            return false;
        }
    }
    return true;
}

}  // namespace

Status fill_random(std::span<std::uint8_t> output) {
    std::size_t offset = 0U;
    while (offset < output.size()) {
        const ssize_t count = ::getrandom(
            output.data() + static_cast<std::ptrdiff_t>(offset),
            output.size() - offset, 0U);
        if (count < 0 && errno == EINTR) {
            continue;
        }
        if (count < 0 && (errno == ENOSYS || errno == EPERM || errno == EAGAIN)) {
            return read_urandom(output.subspan(offset));
        }
        if (count < 0) {
            return Status{ErrorCode::io_error,
                          "getrandom failed: " + std::string(std::strerror(errno))};
        }
        if (count == 0) {
            return Status{ErrorCode::io_error,
                          "getrandom returned zero bytes before the buffer was full"};
        }
        offset += static_cast<std::size_t>(count);
    }
    return Status::success();
}

Result<std::uint64_t> random_u64_nonzero() {
    for (std::size_t attempt = 0U; attempt < 4U; ++attempt) {
        std::array<std::uint8_t, 8U> bytes{};
        const Status status = fill_random(bytes);
        if (!status.ok()) {
            return status;
        }
        if (all_zero(bytes)) {
            continue;
        }
        std::uint64_t value = 0U;
        for (const std::uint8_t byte : bytes) {
            value = (value << 8U) | byte;
        }
        if (value != 0U) {
            return value;
        }
    }
    return Status{ErrorCode::internal_error,
                  "operating-system random source repeatedly produced a zero identifier"};
}

Result<std::array<std::uint8_t, 16U>> random_nonce_128() {
    for (std::size_t attempt = 0U; attempt < 4U; ++attempt) {
        std::array<std::uint8_t, 16U> nonce{};
        const Status status = fill_random(nonce);
        if (!status.ok()) {
            return status;
        }
        if (!all_zero(nonce)) {
            return nonce;
        }
    }
    return Status{ErrorCode::internal_error,
                  "operating-system random source repeatedly produced a zero session nonce"};
}

}  // namespace iotox::security
