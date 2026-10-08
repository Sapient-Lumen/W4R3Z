#include "sync_conflict_resolution.hpp"

#include "sha256_digest.hpp"

#include <array>
#include <charconv>
#include <stdexcept>
#include <string_view>
#include <system_error>

namespace anonsync {
namespace {

[[nodiscard]] bool kind_is_valid(SyncConflictValueKind kind) noexcept {
    return kind == SyncConflictValueKind::File ||
           kind == SyncConflictValueKind::Tombstone;
}

[[nodiscard]] std::string_view kind_text(
    SyncConflictValueKind kind) noexcept {
    return kind == SyncConflictValueKind::Tombstone ? "tombstone" : "file";
}

void append_framed_component(
    Sha256DigestBuilder& digest,
    std::string_view component) {
    std::array<char, 32> decimal{};
    const auto converted = std::to_chars(
        decimal.data(), decimal.data() + decimal.size(), component.size());
    if (converted.ec != std::errc{}) {
        throw std::runtime_error(
            "sync conflict identity length formatting failed");
    }
    digest.update(std::string_view(
        decimal.data(),
        static_cast<std::size_t>(converted.ptr - decimal.data())));
    digest.update(":");
    digest.update(component);
}

void validate_conflict_scope_or_throw(
    const std::string& folder_id,
    const std::string& canonical_path) {
    if (folder_id.empty() || folder_id.size() > 128U) {
        throw std::invalid_argument(
            "sync conflict identity requires a bounded folder id");
    }
    if (canonical_path.empty() || canonical_path.size() > 4096U) {
        throw std::invalid_argument(
            "sync conflict identity requires a bounded canonical path");
    }
    const auto has_control = [](const std::string& value) {
        for (const unsigned char byte : value) {
            if (byte < 0x20U || byte == 0x7fU) return true;
        }
        return false;
    };
    if (has_control(folder_id) || has_control(canonical_path)) {
        throw std::invalid_argument(
            "sync conflict identity scope contains a control byte");
    }
}

[[nodiscard]] bool local_version_wins(
    SyncConflictValueKind local_kind,
    const std::string& local_version_digest,
    SyncConflictValueKind remote_kind,
    const std::string& remote_version_digest) noexcept {
    if (local_kind != remote_kind) {
        return local_kind == SyncConflictValueKind::Tombstone;
    }

    // A digest order is independent of transport direction, wall clocks,
    // locale, current publisher, and delivery order. The losing file is
    // preserved, so this tie-break does not discard user bytes.
    return local_version_digest > remote_version_digest;
}

}  // namespace

SyncConflictResolution resolve_sync_conflict_or_throw(
    SyncConflictValueKind local_kind,
    const std::string& local_version_digest,
    SyncConflictValueKind remote_kind,
    const std::string& remote_version_digest) {
    if (!kind_is_valid(local_kind) || !kind_is_valid(remote_kind)) {
        throw std::invalid_argument(
            "sync conflict resolution requires known value kinds");
    }
    if (!is_lowercase_sha256_hex(local_version_digest) ||
        !is_lowercase_sha256_hex(remote_version_digest)) {
        throw std::invalid_argument(
            "sync conflict resolution requires lowercase SHA-256 version digests");
    }
    if (local_version_digest == remote_version_digest) {
        throw std::invalid_argument(
            "sync conflict resolution requires distinct version digests");
    }

    SyncConflictResolution out;
    if (local_version_digest < remote_version_digest) {
        out.canonical_first_kind = local_kind;
        out.canonical_first_version_digest = local_version_digest;
        out.canonical_second_kind = remote_kind;
        out.canonical_second_version_digest = remote_version_digest;
    } else {
        out.canonical_first_kind = remote_kind;
        out.canonical_first_version_digest = remote_version_digest;
        out.canonical_second_kind = local_kind;
        out.canonical_second_version_digest = local_version_digest;
    }

    const bool local_wins = local_version_wins(
        local_kind,
        local_version_digest,
        remote_kind,
        remote_version_digest);
    if (local_wins) {
        out.disposition = SyncConflictDisposition::PublishLocalWinner;
        out.winner_kind = local_kind;
        out.loser_kind = remote_kind;
        out.winner_version_digest = local_version_digest;
        out.loser_version_digest = remote_version_digest;
        return out;
    }

    out.winner_kind = remote_kind;
    out.loser_kind = local_kind;
    out.winner_version_digest = remote_version_digest;
    out.loser_version_digest = local_version_digest;
    out.disposition = local_kind == SyncConflictValueKind::File
        ? SyncConflictDisposition::PreserveLocalFileThenApplyRemoteWinner
        : SyncConflictDisposition::ApplyRemoteWinner;
    return out;
}

std::string make_sync_conflict_set_id_or_throw(
    const std::string& folder_id,
    const std::string& canonical_path,
    SyncConflictValueKind local_kind,
    const std::string& local_version_digest,
    SyncConflictValueKind remote_kind,
    const std::string& remote_version_digest) {
    validate_conflict_scope_or_throw(folder_id, canonical_path);
    const SyncConflictResolution resolution = resolve_sync_conflict_or_throw(
        local_kind,
        local_version_digest,
        remote_kind,
        remote_version_digest);

    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-conflict-set-v2");
    append_framed_component(digest, "folder_id");
    append_framed_component(digest, folder_id);
    append_framed_component(digest, "canonical_path");
    append_framed_component(digest, canonical_path);
    append_framed_component(digest, "canonical_first_kind");
    append_framed_component(digest, kind_text(resolution.canonical_first_kind));
    append_framed_component(digest, "canonical_first_version_digest");
    append_framed_component(
        digest, resolution.canonical_first_version_digest);
    append_framed_component(digest, "canonical_second_kind");
    append_framed_component(digest, kind_text(resolution.canonical_second_kind));
    append_framed_component(digest, "canonical_second_version_digest");
    append_framed_component(
        digest, resolution.canonical_second_version_digest);
    return "conflict-" + digest.finish_hex().substr(0, 32);
}

}  // namespace anonsync
