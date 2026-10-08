#include "local_jsonl_replay_directory_authority.hpp"

#if !defined(_WIN32)

#include <utility>

namespace anonsync::persistence {

LocalJsonlReplayDirectoryAuthority::~LocalJsonlReplayDirectoryAuthority() =
    default;

LocalJsonlReplayDirectoryAuthority::LocalJsonlReplayDirectoryAuthority(
    LocalJsonlReplayDirectoryAuthority&& other) noexcept = default;

LocalJsonlReplayDirectoryAuthority&
LocalJsonlReplayDirectoryAuthority::operator=(
    LocalJsonlReplayDirectoryAuthority&& other) noexcept = default;

LocalJsonlReplayDirectoryAuthority
LocalJsonlReplayDirectoryAuthority::open_or_throw(
    const std::filesystem::path& absolute_directory,
    const std::string& label) {
    LocalJsonlReplayDirectoryAuthority out;
    out.authority_ = SyncDirectoryAuthority::open_or_throw(
        absolute_directory, label);
    return out;
}

const std::filesystem::path& LocalJsonlReplayDirectoryAuthority::path()
    const noexcept {
    return authority_.path();
}

const std::string& LocalJsonlReplayDirectoryAuthority::absolute_path() const
    noexcept {
    return authority_.absolute_path();
}

const LocalJsonlReplayDirectoryAttestation&
LocalJsonlReplayDirectoryAuthority::attestation() const noexcept {
    return authority_.attestation();
}

void LocalJsonlReplayDirectoryAuthority::verify_or_throw(
    std::string_view label) const {
    authority_.verify_or_throw(label);
}

int LocalJsonlReplayDirectoryAuthority::descriptor_no_verify() const noexcept {
    return authority_.descriptor_no_verify();
}

long LocalJsonlReplayDirectoryAuthority::name_maximum_no_verify() const
    noexcept {
    return authority_.name_maximum_no_verify();
}

}  // namespace anonsync::persistence

#endif
