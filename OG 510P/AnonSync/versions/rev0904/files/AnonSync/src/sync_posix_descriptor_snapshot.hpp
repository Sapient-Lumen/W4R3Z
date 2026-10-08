#pragma once

#if !defined(_WIN32)

#include <cstdint>
#include <string>
#include <utility>

namespace anonsync {

enum class SyncPosixDescriptorLinkPolicy : unsigned char {
    stable_named_object,
    exactly_one,
};

// Freezes one exact observation of a caller-owned POSIX descriptor. The
// descriptor remains borrowed: this owner never closes it and uses pread(2),
// so the caller's shared file offset is not consumed or rewritten.
class FrozenSyncPosixRegularFileSnapshot final {
public:
    [[nodiscard]] static FrozenSyncPosixRegularFileSnapshot
    freeze_borrowed_descriptor_or_throw(
        int descriptor,
        std::uint64_t maximum_bytes,
        SyncPosixDescriptorLinkPolicy link_policy,
        const std::string& label);

    [[nodiscard]] const std::string& bytes() const noexcept { return bytes_; }
    [[nodiscard]] std::string take_bytes() && { return std::move(bytes_); }

private:
    explicit FrozenSyncPosixRegularFileSnapshot(std::string bytes)
        : bytes_(std::move(bytes)) {}

    std::string bytes_;
};

}  // namespace anonsync

#endif
