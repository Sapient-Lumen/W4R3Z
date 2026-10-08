#pragma once

#include "anonsync_core_internal.hpp"

#include <algorithm>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>

namespace anonsync::sync_checkpoint_internal {

inline bool ascii_lower_alnum(char c) noexcept {
    return (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9');
}

inline bool valid_portable_sync_id(const std::string& value) noexcept {
    if (value.empty() || value.size() > 128) return false;
    if (!ascii_lower_alnum(value.front()) ||
        !ascii_lower_alnum(value.back())) {
        return false;
    }
    for (char c : value) {
        if (ascii_lower_alnum(c) || c == '.' || c == '_' || c == '-') continue;
        return false;
    }
    return true;
}

inline std::string checkpoint_resume_transfer_worker_lease_id_or_throw(
    const std::string& session_id,
    const std::string& worker_id,
    const std::string& peer_id,
    const std::string& peer_session_id,
    std::uint64_t worker_lease_epoch) {
    if (!valid_portable_sync_id(session_id) ||
        !valid_portable_sync_id(worker_id) ||
        !valid_portable_sync_id(peer_id) ||
        !valid_portable_sync_id(peer_session_id)) {
        throw std::runtime_error(
            "sync session checkpoint resume transfer worker lease id requires portable sync ids");
    }
    if (worker_lease_epoch == 0) {
        throw std::runtime_error(
            "sync session checkpoint resume transfer worker lease epoch must be positive");
    }
    const std::string material = length_prefixed_security_tuple(
        "anonsync-sync-checkpoint-resume-transfer-worker-lease-v1",
        {
            {"session_id", session_id},
            {"worker_id", worker_id},
            {"peer_id", peer_id},
            {"peer_session_id", peer_session_id},
            {"worker_lease_epoch", std::to_string(worker_lease_epoch)},
        });
    return "sync-resume-transfer-lease:v1:" + sha256_hex(material);
}

inline std::vector<std::string> unique_resume_transfer_execution_keys_or_throw(
    const std::vector<std::string>& execution_keys,
    const std::string& context) {
    std::vector<std::string> unique;
    unique.reserve(execution_keys.size());
    for (const auto& key : execution_keys) {
        if (!key.starts_with("sync-resume-transfer-execute:v1:")) {
            throw std::runtime_error(
                context + " execution key filter contains a key in the wrong namespace");
        }
        if (std::find(unique.begin(), unique.end(), key) == unique.end()) {
            unique.push_back(key);
        }
    }
    return unique;
}

}  // namespace anonsync::sync_checkpoint_internal
