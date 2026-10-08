#pragma once

#if !defined(_WIN32)

#include "sync_directory_authority.hpp"

#include <filesystem>
#include <string>
#include <string_view>

namespace anonsync::persistence {

// Compatibility name for the generic frozen directory attestation. The local
// JSONL backend now delegates to the shared directory authority rather than
// maintaining a second pathname-traversal and revocation implementation.
using LocalJsonlReplayDirectoryAttestation = SyncDirectoryAttestation;

class LocalJsonlReplayDirectoryAuthority final {
public:
    LocalJsonlReplayDirectoryAuthority() = default;
    ~LocalJsonlReplayDirectoryAuthority();
    LocalJsonlReplayDirectoryAuthority(
        const LocalJsonlReplayDirectoryAuthority&) = delete;
    LocalJsonlReplayDirectoryAuthority& operator=(
        const LocalJsonlReplayDirectoryAuthority&) = delete;
    LocalJsonlReplayDirectoryAuthority(
        LocalJsonlReplayDirectoryAuthority&& other) noexcept;
    LocalJsonlReplayDirectoryAuthority& operator=(
        LocalJsonlReplayDirectoryAuthority&& other) noexcept;

    [[nodiscard]] static LocalJsonlReplayDirectoryAuthority open_or_throw(
        const std::filesystem::path& absolute_directory,
        const std::string& label =
            "durable replay ledger parent directory");

    [[nodiscard]] const std::filesystem::path& path() const noexcept;
    [[nodiscard]] const std::string& absolute_path() const noexcept;
    [[nodiscard]] const LocalJsonlReplayDirectoryAttestation& attestation()
        const noexcept;

    void verify_or_throw(
        std::string_view label =
            "durable replay ledger parent directory") const;

private:
    friend class LocalJsonlReplayNamespace;

    [[nodiscard]] int descriptor_no_verify() const noexcept;
    [[nodiscard]] long name_maximum_no_verify() const noexcept;

    SyncDirectoryAuthority authority_;
};

}  // namespace anonsync::persistence

#endif
