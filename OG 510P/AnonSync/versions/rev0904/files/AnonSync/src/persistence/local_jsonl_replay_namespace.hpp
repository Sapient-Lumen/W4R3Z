#pragma once

#if !defined(_WIN32)

#include "local_jsonl_replay_directory_authority.hpp"
#include "sync_process_incarnation.hpp"
#include "sync_thread_incarnation.hpp"

#include <cstdint>
#include <filesystem>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>

namespace anonsync::persistence {

class LocalJsonlReplayLockContention final : public std::runtime_error {
public:
    explicit LocalJsonlReplayLockContention(const std::string& message)
        : std::runtime_error(message) {}
};

// The journal publication uses one fsynced staging inode and a no-overwrite
// hard-link publication edge. A crash may therefore expose both reserved names
// for the same inode before the staging name is retired. That linked pair is a
// valid, recoverable intermediate state; every other multiply-linked or
// two-name topology is rejected.
enum class LocalJsonlReplayJournalPublicationState {
    absent,
    staging_only,
    journal_only,
    linked_pair,
};

// Move-only, process- and thread-bound ownership of one opened regular file.
// It closes on scope exit, never silently reports a requested close as
// successful, and may
// not be destroyed by a fork child that inherited the descriptor.
class LocalJsonlReplayOpenFile final {
public:
    LocalJsonlReplayOpenFile() = default;
    ~LocalJsonlReplayOpenFile();
    LocalJsonlReplayOpenFile(const LocalJsonlReplayOpenFile&) = delete;
    LocalJsonlReplayOpenFile& operator=(const LocalJsonlReplayOpenFile&) = delete;
    LocalJsonlReplayOpenFile(LocalJsonlReplayOpenFile&& other) noexcept;
    LocalJsonlReplayOpenFile& operator=(
        LocalJsonlReplayOpenFile&& other) noexcept;

    [[nodiscard]] int descriptor() const noexcept;
    void write_all_or_throw(const std::string& bytes,
                            const std::string& label);
    void fsync_or_throw(const std::string& label);
    void close_or_throw(const std::string& label);

private:
    friend class LocalJsonlReplayNamespace;
    LocalJsonlReplayOpenFile(
        int descriptor,
        SyncProcessIncarnation process_id,
        SyncThreadIncarnation thread_id) noexcept
        : process_id_(process_id),
          thread_id_(thread_id),
          descriptor_(descriptor) {}

    void require_current_owner_noexcept() const noexcept;
    void require_current_owner_or_throw(std::string_view label) const;
    void transfer_from_noexcept(LocalJsonlReplayOpenFile& other) noexcept;

    SyncProcessIncarnation process_id_;
    SyncThreadIncarnation thread_id_;
    int descriptor_ = -1;
};

// Retained single-thread-affine authority over one local JSONL replay-ledger
// namespace. The input path is resolved exactly once. Every later operation is relative to a kept
// parent-directory descriptor and first proves that the absolute parent path
// still names that exact directory. The flock descriptor is owned here too,
// so a fork child cannot accidentally unlock its parent's ledger. A failed
// directory or retained-lock reproof permanently revokes the namespace object;
// restoring visible names later cannot erase an interval of lost authority.
// Throwing operations reject foreign-thread use before touching mutable state;
// noexcept moves, accessors, lock release, and destruction fail stopped. This
// affinity proof does not make concurrent object-lifetime races valid C++.
class LocalJsonlReplayNamespace final {
public:
    LocalJsonlReplayNamespace() = default;
    ~LocalJsonlReplayNamespace();
    LocalJsonlReplayNamespace(const LocalJsonlReplayNamespace&) = delete;
    LocalJsonlReplayNamespace& operator=(
        const LocalJsonlReplayNamespace&) = delete;
    LocalJsonlReplayNamespace(LocalJsonlReplayNamespace&& other) noexcept;
    LocalJsonlReplayNamespace& operator=(
        LocalJsonlReplayNamespace&& other) noexcept;

    [[nodiscard]] static LocalJsonlReplayNamespace open_or_throw(
        const std::filesystem::path& ledger_path,
        const std::string& label = "durable replay ledger");

    [[nodiscard]] const std::string& absolute_parent_path() const noexcept;
    [[nodiscard]] const std::string& absolute_ledger_path() const noexcept;
    [[nodiscard]] const std::string& absolute_journal_path() const noexcept;
    [[nodiscard]] const std::string& absolute_journal_staging_path() const noexcept;
    [[nodiscard]] const std::string& absolute_lock_path() const noexcept;
    [[nodiscard]] const LocalJsonlReplayDirectoryAttestation&
    directory_attestation() const noexcept;

    void verify_namespace_or_throw(
        const std::string& label = "durable replay ledger") const;

    [[nodiscard]] bool ledger_exists_or_throw(
        const std::string& label = "durable replay ledger") const;
    [[nodiscard]] bool journal_exists_or_throw(
        const std::string& label =
            "durable replay ledger journal") const;
    [[nodiscard]] bool journal_staging_exists_or_throw(
        const std::string& label =
            "durable replay ledger journal staging file") const;
    [[nodiscard]] LocalJsonlReplayJournalPublicationState
    journal_publication_state_or_throw(
        const std::string& label =
            "durable replay ledger journal publication") const;
    [[nodiscard]] bool temporary_exists_or_throw(
        const std::string& temporary_name,
        const std::string& label =
            "durable replay ledger temporary file") const;

    [[nodiscard]] std::string read_ledger_or_empty_or_throw(
        std::uint64_t maximum_bytes,
        const std::string& label = "durable replay ledger") const;
    [[nodiscard]] std::string read_journal_or_throw(
        std::uint64_t maximum_bytes,
        const std::string& label =
            "durable replay ledger journal") const;
    [[nodiscard]] std::optional<std::string>
    read_temporary_if_present_or_throw(
        const std::string& temporary_name,
        std::uint64_t maximum_bytes,
        const std::string& label =
            "durable replay ledger temporary file") const;

    void acquire_lock_or_throw(
        const std::string& label = "durable replay ledger lock");
    void release_lock_noexcept() noexcept;

    [[nodiscard]] LocalJsonlReplayOpenFile
    create_journal_staging_exclusive_or_throw(
        const std::string& label =
            "durable replay ledger journal staging file");
    [[nodiscard]] LocalJsonlReplayOpenFile
    create_temporary_exclusive_or_throw(
        const std::string& temporary_name,
        const std::string& label =
            "durable replay ledger temporary file");

    void verify_journal_staging_descriptor_bound_or_throw(
        int descriptor,
        const std::string& label =
            "durable replay ledger journal staging file") const;
    void verify_temporary_descriptor_bound_or_throw(
        const std::string& temporary_name,
        int descriptor,
        const std::string& label =
            "durable replay ledger temporary file") const;

    void publish_open_journal_staging_to_journal_or_throw(
        int staging_descriptor,
        const std::string& label =
            "durable replay ledger journal publication") const;
    void complete_linked_journal_publication_or_throw(
        const std::string& label =
            "durable replay ledger linked journal publication recovery") const;

    void rename_open_temporary_over_ledger_or_throw(
        const std::string& temporary_name,
        int temporary_descriptor,
        const std::string& label =
            "durable replay ledger atomic replacement") const;

    [[nodiscard]] bool unlink_journal_if_present_or_throw(
        const std::string& label =
            "durable replay ledger journal") const;
    [[nodiscard]] bool unlink_journal_staging_if_present_or_throw(
        const std::string& label =
            "durable replay ledger journal staging file") const;
    [[nodiscard]] bool unlink_temporary_if_present_or_throw(
        const std::string& temporary_name,
        const std::string& label =
            "durable replay ledger temporary file") const;

    void fsync_directory_or_throw(std::string_view phase) const;

    [[nodiscard]] std::string make_temporary_name_or_throw(
        std::int64_t process_id,
        std::int64_t sequence,
        const std::string& label =
            "durable replay ledger temporary file") const;
    void require_owned_temporary_name_or_throw(
        const std::string& temporary_name,
        const std::string& label =
            "durable replay ledger temporary file") const;

private:
    void require_current_owner_noexcept() const noexcept;
    void require_current_owner_or_throw(std::string_view label) const;
    void transfer_from_noexcept(LocalJsonlReplayNamespace& other) noexcept;
    void clear_moved_from_noexcept() noexcept;

    [[nodiscard]] bool member_exists_or_throw(
        const std::string& basename,
        const std::filesystem::path& display_path,
        const std::string& label) const;
    [[nodiscard]] std::string read_existing_member_or_throw(
        const std::string& basename,
        const std::filesystem::path& display_path,
        std::uint64_t maximum_bytes,
        const std::string& label) const;
    [[nodiscard]] LocalJsonlReplayOpenFile
    create_exclusive_member_or_throw(
        const std::string& basename,
        const std::filesystem::path& display_path,
        const std::string& label);
    void verify_descriptor_bound_or_throw(
        const std::string& basename,
        const std::filesystem::path& display_path,
        int descriptor,
        const std::string& label) const;
    [[nodiscard]] bool unlink_member_if_present_or_throw(
        const std::string& basename,
        const std::filesystem::path& display_path,
        const std::string& label) const;

    SyncProcessIncarnation process_id_;
    SyncThreadIncarnation thread_id_;
    std::filesystem::path ledger_path_;
    std::filesystem::path journal_path_;
    std::filesystem::path journal_staging_path_;
    std::filesystem::path lock_path_;
    std::string ledger_basename_;
    std::string journal_basename_;
    std::string journal_staging_basename_;
    std::string lock_basename_;
    std::string temporary_prefix_;
    std::string ledger_path_text_;
    std::string journal_path_text_;
    std::string journal_staging_path_text_;
    std::string lock_path_text_;
    LocalJsonlReplayDirectoryAuthority directory_authority_;
    int lock_descriptor_ = -1;
    mutable bool revoked_ = false;
};

}  // namespace anonsync::persistence

#endif
