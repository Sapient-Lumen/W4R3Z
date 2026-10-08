#include "local_jsonl_replay_namespace.hpp"

#if !defined(_WIN32)

#include "local_jsonl_replay_publication.hpp"
#include "sync_posix_descriptor_snapshot.hpp"

#include <algorithm>
#include <cerrno>
#include <charconv>
#include <cstring>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>

#include <fcntl.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace anonsync::persistence {
namespace {

namespace fs = std::filesystem;

class ScopedFd final {
public:
    ScopedFd() noexcept = default;
    explicit ScopedFd(int descriptor) noexcept : descriptor_(descriptor) {}
    ~ScopedFd() { reset(); }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& other) noexcept : descriptor_(other.release()) {}
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) reset(other.release());
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return descriptor_; }
    [[nodiscard]] int release() noexcept {
        const int out = descriptor_;
        descriptor_ = -1;
        return out;
    }
    void reset(int descriptor = -1) noexcept {
        if (descriptor_ >= 0) (void)::close(descriptor_);
        descriptor_ = descriptor;
    }

private:
    int descriptor_ = -1;
};

[[noreturn]] void throw_errno(const std::string& label,
                              const std::string& operation,
                              const fs::path& path,
                              int error_number = errno) {
    throw std::runtime_error(label + " " + operation + " failed for " +
                             path.generic_string() + ": " +
                             std::strerror(error_number));
}

[[nodiscard]] bool same_identity(const struct stat& left,
                                 const struct stat& right) noexcept {
    return left.st_dev == right.st_dev && left.st_ino == right.st_ino;
}


[[nodiscard]] int regular_open_flags(int flags) noexcept {
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
#ifdef O_NONBLOCK
    flags |= O_NONBLOCK;
#endif
#ifdef O_NOCTTY
    flags |= O_NOCTTY;
#endif
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
    return flags;
}

void set_close_on_exec_or_throw(int descriptor,
                                const std::string& label,
                                const fs::path& path) {
#ifndef O_CLOEXEC
    const int old_flags = ::fcntl(descriptor, F_GETFD);
    if (old_flags < 0 ||
        ::fcntl(descriptor, F_SETFD, old_flags | FD_CLOEXEC) != 0) {
        throw_errno(label, "close-on-exec setup", path);
    }
#else
    (void)descriptor;
    (void)label;
    (void)path;
#endif
}

[[nodiscard]] fs::path absolute_normal_path_or_throw(
    const fs::path& raw_path,
    const std::string& label) {
    if (raw_path.empty()) {
        throw std::runtime_error(label + " path is required");
    }
    validate_local_jsonl_replay_ledger_path_or_throw(
        raw_path.generic_string());
    for (const fs::path& component : raw_path) {
        if (component == "..") {
            throw std::runtime_error(
                label + " path must not contain a parent traversal component");
        }
    }
    std::error_code error;
    fs::path absolute = fs::absolute(raw_path, error);
    if (error) {
        throw std::runtime_error(label +
                                 " path could not be made absolute: " +
                                 error.message());
    }
    absolute = absolute.lexically_normal();
    if (!absolute.is_absolute() || absolute.filename().empty() ||
        absolute.filename() == "." || absolute.filename() == "..") {
        throw std::runtime_error(label + " path must name a file");
    }
    validate_local_jsonl_replay_ledger_path_or_throw(
        absolute.generic_string());
    const std::string basename = absolute.filename().string();
    if (basename.empty() || basename == "." || basename == ".." ||
        basename.find('/') != std::string::npos ||
        basename.find('\0') != std::string::npos) {
        throw std::runtime_error(label + " basename is invalid");
    }
    return absolute;
}

struct MemberIdentity final {
    bool exists = false;
    struct stat status {};
};

[[nodiscard]] MemberIdentity inspect_regular_member_allow_links_or_throw(
    int parent_descriptor,
    const std::string& basename,
    const fs::path& display_path,
    const std::string& label) {
    struct stat status {};
    if (::fstatat(parent_descriptor, basename.c_str(), &status,
                  AT_SYMLINK_NOFOLLOW) != 0) {
        const int error = errno;
        if (error == ENOENT) return {};
        throw_errno(label, "inspection", display_path, error);
    }
    if (S_ISLNK(status.st_mode)) {
        throw std::runtime_error(label + " refuses a symbolic-link path: " +
                                 display_path.generic_string());
    }
    if (!S_ISREG(status.st_mode)) {
        throw std::runtime_error(label + " path is not a regular file: " +
                                 display_path.generic_string());
    }
    MemberIdentity out;
    out.exists = true;
    out.status = status;
    return out;
}

[[nodiscard]] MemberIdentity inspect_member_or_throw(
    int parent_descriptor,
    const std::string& basename,
    const fs::path& display_path,
    const std::string& label) {
    MemberIdentity out = inspect_regular_member_allow_links_or_throw(
        parent_descriptor, basename, display_path, label);
    if (out.exists && out.status.st_nlink != 1) {
        throw std::runtime_error(label +
                                 " refuses a multiply-linked path: " +
                                 display_path.generic_string());
    }
    return out;
}

void validate_opened_regular_or_throw(int descriptor,
                                      const std::string& label,
                                      const fs::path& display_path,
                                      bool normalize_permissions) {
    set_close_on_exec_or_throw(descriptor, label, display_path);
    struct stat status {};
    if (::fstat(descriptor, &status) != 0) {
        throw_errno(label, "opened-object fstat", display_path);
    }
    if (!S_ISREG(status.st_mode)) {
        throw std::runtime_error(label +
                                 " opened object is not a regular file: " +
                                 display_path.generic_string());
    }
    if (status.st_nlink != 1) {
        throw std::runtime_error(label +
                                 " opened object is not single-link: " +
                                 display_path.generic_string());
    }
    if (normalize_permissions && ::fchmod(descriptor, 0600) != 0) {
        throw_errno(label, "permission normalization", display_path);
    }
}

void require_descriptor_matches_name_or_throw(
    int descriptor,
    const MemberIdentity& named,
    const std::string& label,
    const fs::path& display_path) {
    struct stat opened {};
    if (::fstat(descriptor, &opened) != 0) {
        throw_errno(label, "opened-object fstat", display_path);
    }
    if (!named.exists || !same_identity(opened, named.status)) {
        throw std::runtime_error(label +
                                 " path changed while it was opened: " +
                                 display_path.generic_string());
    }
}

[[nodiscard]] int linkat_nointr(int old_directory,
                                const char* old_name,
                                int new_directory,
                                const char* new_name) noexcept {
    int result = -1;
    do {
        result = ::linkat(old_directory, old_name, new_directory, new_name, 0);
    } while (result != 0 && errno == EINTR);
    return result;
}

[[nodiscard]] int renameat_nointr(int old_directory,
                                  const char* old_name,
                                  int new_directory,
                                  const char* new_name) noexcept {
    int result = -1;
    do {
        result =
            ::renameat(old_directory, old_name, new_directory, new_name);
    } while (result != 0 && errno == EINTR);
    return result;
}

[[nodiscard]] int unlinkat_nointr(int directory,
                                  const char* name) noexcept {
    int result = -1;
    do {
        result = ::unlinkat(directory, name, 0);
    } while (result != 0 && errno == EINTR);
    return result;
}


}  // namespace

LocalJsonlReplayOpenFile::~LocalJsonlReplayOpenFile() {
    require_current_owner_noexcept();
    if (descriptor_ >= 0) (void)::close(descriptor_);
}

LocalJsonlReplayOpenFile::LocalJsonlReplayOpenFile(
    LocalJsonlReplayOpenFile&& other) noexcept {
    other.require_current_owner_noexcept();
    transfer_from_noexcept(other);
}

LocalJsonlReplayOpenFile& LocalJsonlReplayOpenFile::operator=(
    LocalJsonlReplayOpenFile&& other) noexcept {
    require_current_owner_noexcept();
    other.require_current_owner_noexcept();
    if (this == &other) return *this;
    if (descriptor_ >= 0) (void)::close(descriptor_);
    transfer_from_noexcept(other);
    return *this;
}

void LocalJsonlReplayOpenFile::require_current_owner_noexcept() const
    noexcept {
    if (process_id_.valid() &&
        !sync_process_incarnation_is_current(process_id_)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    if (thread_id_.valid() &&
        !sync_thread_incarnation_is_current(thread_id_)) {
        fail_stop_on_sync_thread_capability_violation_noexcept();
    }
}

void LocalJsonlReplayOpenFile::require_current_owner_or_throw(
    std::string_view label) const {
    require_sync_process_incarnation_or_fail_stop(process_id_, label);
    require_sync_thread_incarnation_or_throw(thread_id_, label);
}

void LocalJsonlReplayOpenFile::transfer_from_noexcept(
    LocalJsonlReplayOpenFile& other) noexcept {
    process_id_ = other.process_id_;
    thread_id_ = other.thread_id_;
    descriptor_ = other.descriptor_;
    other.process_id_ = {};
    other.thread_id_ = {};
    other.descriptor_ = -1;
}

int LocalJsonlReplayOpenFile::descriptor() const noexcept {
    require_current_owner_noexcept();
    return descriptor_;
}

void LocalJsonlReplayOpenFile::write_all_or_throw(
    const std::string& bytes,
    const std::string& label) {
    require_current_owner_or_throw(label);
    if (descriptor_ < 0) {
        throw std::logic_error(label + " file is closed");
    }
    const char* cursor = bytes.data();
    std::size_t remaining = bytes.size();
    while (remaining > 0) {
        const std::size_t request = std::min<std::size_t>(
            remaining,
            static_cast<std::size_t>(
                std::numeric_limits<ssize_t>::max()));
        const ssize_t written = ::write(descriptor_, cursor, request);
        if (written < 0) {
            if (errno == EINTR) continue;
            throw std::runtime_error(label + " write failed: " +
                                     std::strerror(errno));
        }
        if (written == 0) {
            throw std::runtime_error(label + " write made no progress");
        }
        cursor += written;
        remaining -= static_cast<std::size_t>(written);
    }
}

void LocalJsonlReplayOpenFile::fsync_or_throw(const std::string& label) {
    require_current_owner_or_throw(label);
    if (descriptor_ < 0) {
        throw std::logic_error(label + " file is closed");
    }
    if (::fsync(descriptor_) != 0) {
        throw std::runtime_error(label + " fsync failed: " +
                                 std::strerror(errno));
    }
}

void LocalJsonlReplayOpenFile::close_or_throw(const std::string& label) {
    require_current_owner_or_throw(label);
    if (descriptor_ < 0) return;
    const int descriptor = descriptor_;
    descriptor_ = -1;
    if (::close(descriptor) != 0) {
        throw std::runtime_error(label + " close failed: " +
                                 std::strerror(errno));
    }
}

LocalJsonlReplayNamespace::~LocalJsonlReplayNamespace() {
    require_current_owner_noexcept();
    release_lock_noexcept();
}

LocalJsonlReplayNamespace::LocalJsonlReplayNamespace(
    LocalJsonlReplayNamespace&& other) noexcept {
    other.require_current_owner_noexcept();
    transfer_from_noexcept(other);
}

LocalJsonlReplayNamespace& LocalJsonlReplayNamespace::operator=(
    LocalJsonlReplayNamespace&& other) noexcept {
    require_current_owner_noexcept();
    other.require_current_owner_noexcept();
    if (this == &other) return *this;
    release_lock_noexcept();
    transfer_from_noexcept(other);
    return *this;
}

LocalJsonlReplayNamespace LocalJsonlReplayNamespace::open_or_throw(
    const fs::path& raw_ledger_path,
    const std::string& label) {
    LocalJsonlReplayNamespace out;
    out.process_id_ = current_sync_process_incarnation_noexcept();
    out.thread_id_ = current_sync_thread_incarnation_noexcept();
    out.ledger_path_ = absolute_normal_path_or_throw(raw_ledger_path, label);
    fs::path parent_path = out.ledger_path_.parent_path();
    if (parent_path.empty()) parent_path = "/";
    out.directory_authority_ =
        LocalJsonlReplayDirectoryAuthority::open_or_throw(
            parent_path, label + " parent directory");
    out.ledger_basename_ = out.ledger_path_.filename().string();
    out.journal_basename_ = out.ledger_basename_ + ".journal";
    out.journal_staging_basename_ =
        out.ledger_basename_ + ".journal.stage";
    out.lock_basename_ = out.ledger_basename_ + ".lock";
    out.temporary_prefix_ = out.ledger_basename_ + ".tmp.";
    out.journal_path_ = out.directory_authority_.path() / out.journal_basename_;
    out.journal_staging_path_ =
        out.directory_authority_.path() / out.journal_staging_basename_;
    out.lock_path_ = out.directory_authority_.path() / out.lock_basename_;
    out.ledger_path_text_ = out.ledger_path_.generic_string();
    out.journal_path_text_ = out.journal_path_.generic_string();
    out.journal_staging_path_text_ =
        out.journal_staging_path_.generic_string();
    out.lock_path_text_ = out.lock_path_.generic_string();
    validate_local_jsonl_replay_ledger_path_or_throw(out.journal_path_text_);
    validate_local_jsonl_replay_ledger_path_or_throw(
        out.journal_staging_path_text_);
    validate_local_jsonl_replay_ledger_path_or_throw(out.lock_path_text_);

    auto require_name = [&](const std::string& name,
                            const std::string& kind) {
        if (name.empty() || name == "." || name == ".." ||
            name.find('/') != std::string::npos ||
            name.find('\0') != std::string::npos) {
            throw std::runtime_error(label + " " + kind +
                                     " basename is invalid");
        }
        if (out.directory_authority_.name_maximum_no_verify() >= 0 &&
            name.size() > static_cast<std::size_t>(
                              out.directory_authority_
                                  .name_maximum_no_verify())) {
            throw std::runtime_error(label + " " + kind +
                                     " basename exceeds NAME_MAX");
        }
    };
    require_name(out.ledger_basename_, "ledger");
    require_name(out.journal_basename_, "journal");
    require_name(out.journal_staging_basename_, "journal staging");
    require_name(out.lock_basename_, "lock");
    out.verify_namespace_or_throw(label + " initial namespace proof");
    return out;
}

void LocalJsonlReplayNamespace::require_current_owner_noexcept() const
    noexcept {
    if (process_id_.valid() &&
        !sync_process_incarnation_is_current(process_id_)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    if (thread_id_.valid() &&
        !sync_thread_incarnation_is_current(thread_id_)) {
        fail_stop_on_sync_thread_capability_violation_noexcept();
    }
}

void LocalJsonlReplayNamespace::require_current_owner_or_throw(
    std::string_view label) const {
    if (!process_id_.valid()) {
        throw std::logic_error(std::string(label) +
                               " namespace authority is not initialized");
    }
    require_sync_process_incarnation_or_fail_stop(process_id_, label);
    require_sync_thread_incarnation_or_throw(thread_id_, label);
}

void LocalJsonlReplayNamespace::transfer_from_noexcept(
    LocalJsonlReplayNamespace& other) noexcept {
    process_id_ = other.process_id_;
    thread_id_ = other.thread_id_;
    ledger_path_ = std::move(other.ledger_path_);
    journal_path_ = std::move(other.journal_path_);
    journal_staging_path_ = std::move(other.journal_staging_path_);
    lock_path_ = std::move(other.lock_path_);
    ledger_basename_ = std::move(other.ledger_basename_);
    journal_basename_ = std::move(other.journal_basename_);
    journal_staging_basename_ =
        std::move(other.journal_staging_basename_);
    lock_basename_ = std::move(other.lock_basename_);
    temporary_prefix_ = std::move(other.temporary_prefix_);
    ledger_path_text_ = std::move(other.ledger_path_text_);
    journal_path_text_ = std::move(other.journal_path_text_);
    journal_staging_path_text_ =
        std::move(other.journal_staging_path_text_);
    lock_path_text_ = std::move(other.lock_path_text_);
    directory_authority_ = std::move(other.directory_authority_);
    lock_descriptor_ = other.lock_descriptor_;
    revoked_ = other.revoked_;
    other.clear_moved_from_noexcept();
}

void LocalJsonlReplayNamespace::clear_moved_from_noexcept() noexcept {
    process_id_ = {};
    thread_id_ = {};
    ledger_path_.clear();
    journal_path_.clear();
    journal_staging_path_.clear();
    lock_path_.clear();
    ledger_basename_.clear();
    journal_basename_.clear();
    journal_staging_basename_.clear();
    lock_basename_.clear();
    temporary_prefix_.clear();
    ledger_path_text_.clear();
    journal_path_text_.clear();
    journal_staging_path_text_.clear();
    lock_path_text_.clear();
    lock_descriptor_ = -1;
    revoked_ = false;
}

const std::string& LocalJsonlReplayNamespace::absolute_parent_path() const
    noexcept {
    require_current_owner_noexcept();
    return directory_authority_.absolute_path();
}

const LocalJsonlReplayDirectoryAttestation&
LocalJsonlReplayNamespace::directory_attestation() const noexcept {
    require_current_owner_noexcept();
    return directory_authority_.attestation();
}

const std::string& LocalJsonlReplayNamespace::absolute_ledger_path() const
    noexcept {
    require_current_owner_noexcept();
    return ledger_path_text_;
}

const std::string& LocalJsonlReplayNamespace::absolute_journal_path() const
    noexcept {
    require_current_owner_noexcept();
    return journal_path_text_;
}

const std::string&
LocalJsonlReplayNamespace::absolute_journal_staging_path() const noexcept {
    require_current_owner_noexcept();
    return journal_staging_path_text_;
}

const std::string& LocalJsonlReplayNamespace::absolute_lock_path() const
    noexcept {
    require_current_owner_noexcept();
    return lock_path_text_;
}

void LocalJsonlReplayNamespace::verify_namespace_or_throw(
    const std::string& label) const {
    require_current_owner_or_throw(label);
    if (revoked_) {
        throw std::runtime_error(label + " namespace authority is revoked");
    }
    try {
        directory_authority_.verify_or_throw(label + " directory authority");
        // A pathname lock is authority only while its name still denotes the
        // exact open file description on which flock was acquired. An
        // unlink/recreate attack otherwise leaves this process holding a lock
        // on an orphaned inode while a second writer acquires the replacement
        // lock pathname.
        if (lock_descriptor_ >= 0) {
            const MemberIdentity named_lock = inspect_member_or_throw(
                directory_authority_.descriptor_no_verify(), lock_basename_,
                lock_path_, label + " retained lock");
            require_descriptor_matches_name_or_throw(
                lock_descriptor_, named_lock, label + " retained lock",
                lock_path_);
        }
    } catch (...) {
        revoked_ = true;
        throw;
    }
}

bool LocalJsonlReplayNamespace::member_exists_or_throw(
    const std::string& basename,
    const fs::path& display_path,
    const std::string& label) const {
    verify_namespace_or_throw(label + " namespace recheck");
    return inspect_member_or_throw(
               directory_authority_.descriptor_no_verify(), basename,
               display_path, label)
        .exists;
}

bool LocalJsonlReplayNamespace::ledger_exists_or_throw(
    const std::string& label) const {
    return member_exists_or_throw(ledger_basename_, ledger_path_, label);
}

bool LocalJsonlReplayNamespace::journal_exists_or_throw(
    const std::string& label) const {
    return member_exists_or_throw(journal_basename_, journal_path_, label);
}

bool LocalJsonlReplayNamespace::journal_staging_exists_or_throw(
    const std::string& label) const {
    return member_exists_or_throw(journal_staging_basename_,
                                  journal_staging_path_, label);
}

LocalJsonlReplayJournalPublicationState
LocalJsonlReplayNamespace::journal_publication_state_or_throw(
    const std::string& label) const {
    verify_namespace_or_throw(label + " namespace recheck");

    const auto inspect_pair = [&] {
        return std::pair{
            inspect_regular_member_allow_links_or_throw(
                directory_authority_.descriptor_no_verify(), journal_basename_, journal_path_,
                label + " journal"),
            inspect_regular_member_allow_links_or_throw(
                directory_authority_.descriptor_no_verify(), journal_staging_basename_,
                journal_staging_path_, label + " staging")};
    };
    const auto [journal_before, staging_before] = inspect_pair();
    const auto [journal_after, staging_after] = inspect_pair();

    const auto stable = [](const MemberIdentity& before,
                           const MemberIdentity& after) {
        return before.exists == after.exists &&
               (!before.exists ||
                (same_identity(before.status, after.status) &&
                 before.status.st_nlink == after.status.st_nlink));
    };
    if (!stable(journal_before, journal_after) ||
        !stable(staging_before, staging_after)) {
        throw std::runtime_error(
            label + " names changed while publication topology was inspected");
    }

    if (!journal_after.exists && !staging_after.exists) {
        return LocalJsonlReplayJournalPublicationState::absent;
    }
    if (journal_after.exists && !staging_after.exists) {
        if (journal_after.status.st_nlink != 1) {
            throw std::runtime_error(
                label + " final journal has unauthorized hard links");
        }
        return LocalJsonlReplayJournalPublicationState::journal_only;
    }
    if (!journal_after.exists && staging_after.exists) {
        if (staging_after.status.st_nlink != 1) {
            throw std::runtime_error(
                label + " staging journal has unauthorized hard links");
        }
        return LocalJsonlReplayJournalPublicationState::staging_only;
    }
    if (!same_identity(journal_after.status, staging_after.status) ||
        journal_after.status.st_nlink != 2 ||
        staging_after.status.st_nlink != 2) {
        throw std::runtime_error(
            label +
            " journal and staging names do not form the one authorized linked pair");
    }
    return LocalJsonlReplayJournalPublicationState::linked_pair;
}

void LocalJsonlReplayNamespace::require_owned_temporary_name_or_throw(
    const std::string& temporary_name,
    const std::string& label) const {
    require_current_owner_or_throw(label);
    if (temporary_name.size() <= temporary_prefix_.size() ||
        temporary_name.compare(0, temporary_prefix_.size(),
                               temporary_prefix_) != 0 ||
        temporary_name.find('/') != std::string::npos ||
        temporary_name.find('\0') != std::string::npos ||
        temporary_name == "." || temporary_name == "..") {
        throw std::runtime_error(
            label + " name is outside the retained ledger family");
    }
    if (temporary_name.size() >
        kLocalJsonlReplayMaximumTemporaryNameBytes) {
        throw std::runtime_error(label + " name exceeds publication budget");
    }
    if (directory_authority_.name_maximum_no_verify() >= 0 &&
        temporary_name.size() >
            static_cast<std::size_t>(directory_authority_.name_maximum_no_verify())) {
        throw std::runtime_error(label + " name exceeds NAME_MAX");
    }

    // Recovery may delete only a name that this implementation itself could
    // mint. A prefix-only check would let a forged journal nominate an
    // unrelated family-looking file for retirement.
    const std::string_view suffix(
        temporary_name.data() + temporary_prefix_.size(),
        temporary_name.size() - temporary_prefix_.size());
    const std::size_t separator = suffix.find('.');
    if (separator == std::string_view::npos || separator == 0 ||
        separator + 1 >= suffix.size() ||
        suffix.find('.', separator + 1) != std::string_view::npos) {
        throw std::runtime_error(label + " name grammar is invalid");
    }
    const auto parse_positive_decimal = [&](std::string_view text,
                                            std::uint64_t maximum,
                                            std::string_view field) {
        if (text.empty() || (text.size() > 1 && text.front() == '0')) {
            throw std::runtime_error(
                label + " " + std::string(field) +
                " is not canonical positive decimal");
        }
        std::uint64_t value = 0;
        const auto [end_pointer, error] = std::from_chars(
            text.data(), text.data() + text.size(), value, 10);
        if (error != std::errc{} ||
            end_pointer != text.data() + text.size() || value == 0 ||
            value > maximum) {
            throw std::runtime_error(label + " " + std::string(field) +
                                     " is invalid");
        }
    };
    parse_positive_decimal(
        suffix.substr(0, separator),
        static_cast<std::uint64_t>(
            std::numeric_limits<std::int64_t>::max()),
        "process id");
    parse_positive_decimal(
        suffix.substr(separator + 1),
        static_cast<std::uint64_t>(
            kLocalJsonlReplayMaximumEntryCount) + 1U,
        "sequence");
}

std::string LocalJsonlReplayNamespace::make_temporary_name_or_throw(
    std::int64_t process_id,
    std::int64_t sequence,
    const std::string& label) const {
    require_current_owner_or_throw(label);
    if (process_id <= 0 || sequence <= 0) {
        throw std::runtime_error(label + " identity is invalid");
    }
    const std::string name =
        temporary_prefix_ + std::to_string(process_id) + "." +
        std::to_string(sequence);
    require_owned_temporary_name_or_throw(name, label);
    return name;
}

bool LocalJsonlReplayNamespace::temporary_exists_or_throw(
    const std::string& temporary_name,
    const std::string& label) const {
    require_owned_temporary_name_or_throw(temporary_name, label);
    return member_exists_or_throw(temporary_name,
                                  directory_authority_.path() / temporary_name, label);
}

void LocalJsonlReplayNamespace::verify_descriptor_bound_or_throw(
    const std::string& basename,
    const fs::path& display_path,
    int descriptor,
    const std::string& label) const {
    verify_namespace_or_throw(label + " namespace recheck");
    const MemberIdentity named = inspect_member_or_throw(
        directory_authority_.descriptor_no_verify(), basename, display_path, label);
    require_descriptor_matches_name_or_throw(descriptor, named, label,
                                             display_path);
}

std::string LocalJsonlReplayNamespace::read_existing_member_or_throw(
    const std::string& basename,
    const fs::path& display_path,
    std::uint64_t maximum_bytes,
    const std::string& label) const {
    verify_namespace_or_throw(label + " namespace recheck");
    const MemberIdentity before = inspect_member_or_throw(
        directory_authority_.descriptor_no_verify(), basename, display_path, label);
    if (!before.exists) {
        throw std::runtime_error(label + " does not exist: " +
                                 display_path.generic_string());
    }
    ScopedFd descriptor(::openat(directory_authority_.descriptor_no_verify(), basename.c_str(),
                                 regular_open_flags(O_RDONLY)));
    if (descriptor.get() < 0) throw_errno(label, "open", display_path);
    validate_opened_regular_or_throw(descriptor.get(), label, display_path,
                                     false);
    require_descriptor_matches_name_or_throw(descriptor.get(), before, label,
                                             display_path);
    std::string bytes =
        FrozenSyncPosixRegularFileSnapshot::freeze_borrowed_descriptor_or_throw(
            descriptor.get(), maximum_bytes,
            SyncPosixDescriptorLinkPolicy::exactly_one, label)
            .take_bytes();
    verify_descriptor_bound_or_throw(basename, display_path, descriptor.get(),
                                     label + " final binding");
    return bytes;
}

std::string LocalJsonlReplayNamespace::read_ledger_or_empty_or_throw(
    std::uint64_t maximum_bytes,
    const std::string& label) const {
    if (!ledger_exists_or_throw(label)) return "";
    return read_existing_member_or_throw(ledger_basename_, ledger_path_,
                                         maximum_bytes, label);
}

std::string LocalJsonlReplayNamespace::read_journal_or_throw(
    std::uint64_t maximum_bytes,
    const std::string& label) const {
    return read_existing_member_or_throw(journal_basename_, journal_path_,
                                         maximum_bytes, label);
}

std::optional<std::string>
LocalJsonlReplayNamespace::read_temporary_if_present_or_throw(
    const std::string& temporary_name,
    std::uint64_t maximum_bytes,
    const std::string& label) const {
    require_owned_temporary_name_or_throw(temporary_name, label);
    if (!temporary_exists_or_throw(temporary_name, label)) {
        return std::nullopt;
    }
    return read_existing_member_or_throw(
        temporary_name, directory_authority_.path() / temporary_name, maximum_bytes, label);
}

void LocalJsonlReplayNamespace::acquire_lock_or_throw(
    const std::string& label) {
    require_current_owner_or_throw(label);
    release_lock_noexcept();
    verify_namespace_or_throw(label + " namespace recheck");
    (void)inspect_member_or_throw(directory_authority_.descriptor_no_verify(), ledger_basename_,
                                  ledger_path_, label + " ledger");
    (void)journal_publication_state_or_throw(
        label + " journal publication");

    ScopedFd descriptor;
    for (int attempt = 0; attempt < 3 && descriptor.get() < 0; ++attempt) {
        const MemberIdentity before = inspect_member_or_throw(
            directory_authority_.descriptor_no_verify(), lock_basename_, lock_path_, label);
        if (before.exists) {
            descriptor.reset(::openat(directory_authority_.descriptor_no_verify(),
                                      lock_basename_.c_str(),
                                      regular_open_flags(O_RDWR)));
            if (descriptor.get() < 0) {
                if (errno == ENOENT) continue;
                throw_errno(label, "open", lock_path_);
            }
            validate_opened_regular_or_throw(descriptor.get(), label,
                                             lock_path_, true);
            require_descriptor_matches_name_or_throw(
                descriptor.get(), before, label, lock_path_);
        } else {
            descriptor.reset(::openat(
                directory_authority_.descriptor_no_verify(), lock_basename_.c_str(),
                regular_open_flags(O_RDWR | O_CREAT | O_EXCL), 0600));
            if (descriptor.get() < 0) {
                if (errno == EEXIST) continue;
                throw_errno(label, "creation", lock_path_);
            }
            validate_opened_regular_or_throw(descriptor.get(), label,
                                             lock_path_, true);
        }
    }
    if (descriptor.get() < 0) {
        throw std::runtime_error(label +
                                 " namespace changed repeatedly");
    }

    if (::flock(descriptor.get(), LOCK_EX | LOCK_NB) != 0) {
        const int error = errno;
        if (error == EWOULDBLOCK || error == EAGAIN) {
            throw LocalJsonlReplayLockContention(
                label + " contention: " + std::strerror(error));
        }
        throw_errno(label, "flock", lock_path_, error);
    }
    try {
        verify_descriptor_bound_or_throw(lock_basename_, lock_path_,
                                         descriptor.get(),
                                         label + " acquired binding");
    } catch (...) {
        (void)::flock(descriptor.get(), LOCK_UN);
        throw;
    }
    lock_descriptor_ = descriptor.release();
}

void LocalJsonlReplayNamespace::release_lock_noexcept() noexcept {
    require_current_owner_noexcept();
    if (lock_descriptor_ >= 0) {
        (void)::flock(lock_descriptor_, LOCK_UN);
        (void)::close(lock_descriptor_);
        lock_descriptor_ = -1;
    }
}

LocalJsonlReplayOpenFile
LocalJsonlReplayNamespace::create_exclusive_member_or_throw(
    const std::string& basename,
    const fs::path& display_path,
    const std::string& label) {
    verify_namespace_or_throw(label + " namespace recheck");
    if (inspect_member_or_throw(directory_authority_.descriptor_no_verify(), basename, display_path,
                                label)
            .exists) {
        throw std::runtime_error(label + " path already exists: " +
                                 display_path.generic_string());
    }
    ScopedFd descriptor(::openat(
        directory_authority_.descriptor_no_verify(), basename.c_str(),
        regular_open_flags(O_WRONLY | O_CREAT | O_EXCL), 0600));
    if (descriptor.get() < 0) {
        throw_errno(label, "exclusive creation", display_path);
    }
    validate_opened_regular_or_throw(descriptor.get(), label, display_path,
                                     true);
    verify_descriptor_bound_or_throw(basename, display_path, descriptor.get(),
                                     label + " created binding");
    return LocalJsonlReplayOpenFile(
        descriptor.release(), process_id_, thread_id_);
}

LocalJsonlReplayOpenFile
LocalJsonlReplayNamespace::create_journal_staging_exclusive_or_throw(
    const std::string& label) {
    return create_exclusive_member_or_throw(
        journal_staging_basename_, journal_staging_path_, label);
}

LocalJsonlReplayOpenFile
LocalJsonlReplayNamespace::create_temporary_exclusive_or_throw(
    const std::string& temporary_name,
    const std::string& label) {
    require_owned_temporary_name_or_throw(temporary_name, label);
    return create_exclusive_member_or_throw(
        temporary_name, directory_authority_.path() / temporary_name, label);
}

void LocalJsonlReplayNamespace::
verify_journal_staging_descriptor_bound_or_throw(
    int descriptor,
    const std::string& label) const {
    verify_descriptor_bound_or_throw(journal_staging_basename_,
                                     journal_staging_path_, descriptor,
                                     label);
}

void LocalJsonlReplayNamespace::verify_temporary_descriptor_bound_or_throw(
    const std::string& temporary_name,
    int descriptor,
    const std::string& label) const {
    require_owned_temporary_name_or_throw(temporary_name, label);
    verify_descriptor_bound_or_throw(temporary_name,
                                     directory_authority_.path() / temporary_name,
                                     descriptor, label);
}

void LocalJsonlReplayNamespace::
publish_open_journal_staging_to_journal_or_throw(
    int staging_descriptor,
    const std::string& label) const {
    verify_descriptor_bound_or_throw(
        journal_staging_basename_, journal_staging_path_, staging_descriptor,
        label + " pre-publication");
    if (journal_exists_or_throw(label + " destination precheck")) {
        throw std::runtime_error(label +
                                 " destination already exists: " +
                                 journal_path_.generic_string());
    }
    if (!journal_staging_exists_or_throw(label + " staging precheck")) {
        throw std::runtime_error(
            label + " requires one staging name and no final journal");
    }

    // linkat() is a descriptor-relative, atomic no-overwrite publication edge:
    // unlike rename(), it never replaces an existing recovery witness. The
    // short two-link interval is an explicit recoverable state, then unlinkat()
    // retires the staging name before the caller's directory fsync barrier.
    if (linkat_nointr(directory_authority_.descriptor_no_verify(),
                      journal_staging_basename_.c_str(),
                      directory_authority_.descriptor_no_verify(),
                      journal_basename_.c_str()) != 0) {
        const int error = errno;
        if (error == EEXIST) {
            throw std::runtime_error(label +
                                     " destination already exists: " +
                                     journal_path_.generic_string());
        }
        throw_errno(label, "hard-link publication", journal_path_, error);
    }

    if (journal_publication_state_or_throw(label + " linked publication") !=
        LocalJsonlReplayJournalPublicationState::linked_pair) {
        throw std::runtime_error(
            label + " did not create the authorized linked journal pair");
    }
    const MemberIdentity linked_journal =
        inspect_regular_member_allow_links_or_throw(
            directory_authority_.descriptor_no_verify(), journal_basename_, journal_path_,
            label + " linked final journal");
    require_descriptor_matches_name_or_throw(
        staging_descriptor, linked_journal, label + " linked final journal",
        journal_path_);

    if (unlinkat_nointr(directory_authority_.descriptor_no_verify(),
                        journal_staging_basename_.c_str()) != 0) {
        throw_errno(label, "staging-name retirement", journal_staging_path_);
    }
    verify_descriptor_bound_or_throw(journal_basename_, journal_path_,
                                     staging_descriptor,
                                     label + " final publication");
    if (inspect_regular_member_allow_links_or_throw(
            directory_authority_.descriptor_no_verify(), journal_staging_basename_,
            journal_staging_path_, label + " retired staging recheck")
            .exists) {
        throw std::runtime_error(label +
                                 " staging name survived publication");
    }
}

void LocalJsonlReplayNamespace::
complete_linked_journal_publication_or_throw(
    const std::string& label) const {
    if (journal_publication_state_or_throw(label + " initial proof") !=
        LocalJsonlReplayJournalPublicationState::linked_pair) {
        throw std::runtime_error(
            label + " requires the authorized linked journal pair");
    }

    ScopedFd journal_descriptor(::openat(
        directory_authority_.descriptor_no_verify(), journal_basename_.c_str(),
        regular_open_flags(O_RDONLY)));
    if (journal_descriptor.get() < 0) {
        throw_errno(label, "linked final journal open", journal_path_);
    }
    set_close_on_exec_or_throw(journal_descriptor.get(), label, journal_path_);
    struct stat opened {};
    if (::fstat(journal_descriptor.get(), &opened) != 0) {
        throw_errno(label, "linked final journal fstat", journal_path_);
    }
    if (!S_ISREG(opened.st_mode) || opened.st_nlink != 2) {
        throw std::runtime_error(
            label + " linked final descriptor topology changed");
    }
    const MemberIdentity journal =
        inspect_regular_member_allow_links_or_throw(
            directory_authority_.descriptor_no_verify(), journal_basename_, journal_path_,
            label + " linked final journal");
    const MemberIdentity staging =
        inspect_regular_member_allow_links_or_throw(
            directory_authority_.descriptor_no_verify(), journal_staging_basename_,
            journal_staging_path_, label + " linked staging journal");
    if (!journal.exists || !staging.exists ||
        !same_identity(journal.status, staging.status) ||
        !same_identity(opened, journal.status) || journal.status.st_nlink != 2 ||
        staging.status.st_nlink != 2) {
        throw std::runtime_error(
            label + " linked journal topology changed before completion");
    }

    if (unlinkat_nointr(directory_authority_.descriptor_no_verify(),
                        journal_staging_basename_.c_str()) != 0) {
        throw_errno(label, "linked staging-name retirement",
                    journal_staging_path_);
    }
    verify_descriptor_bound_or_throw(
        journal_basename_, journal_path_, journal_descriptor.get(),
        label + " completed final journal");
    if (inspect_regular_member_allow_links_or_throw(
            directory_authority_.descriptor_no_verify(), journal_staging_basename_,
            journal_staging_path_, label + " completed staging recheck")
            .exists) {
        throw std::runtime_error(
            label + " staging name survived linked publication recovery");
    }
}

void LocalJsonlReplayNamespace::rename_open_temporary_over_ledger_or_throw(
    const std::string& temporary_name,
    int temporary_descriptor,
    const std::string& label) const {
    require_owned_temporary_name_or_throw(temporary_name, label);
    const fs::path temporary_path = directory_authority_.path() / temporary_name;
    verify_descriptor_bound_or_throw(temporary_name, temporary_path,
                                     temporary_descriptor,
                                     label + " pre-rename");
    (void)inspect_member_or_throw(directory_authority_.descriptor_no_verify(), ledger_basename_,
                                  ledger_path_, label + " destination");
    if (renameat_nointr(directory_authority_.descriptor_no_verify(),
                        temporary_name.c_str(),
                        directory_authority_.descriptor_no_verify(),
                        ledger_basename_.c_str()) != 0) {
        throw_errno(label, "rename", ledger_path_);
    }
    verify_descriptor_bound_or_throw(ledger_basename_, ledger_path_,
                                     temporary_descriptor,
                                     label + " post-rename");
    if (inspect_member_or_throw(directory_authority_.descriptor_no_verify(), temporary_name,
                                temporary_path,
                                label + " old-name recheck")
            .exists) {
        throw std::runtime_error(label +
                                 " temporary name survived rename");
    }
}

bool LocalJsonlReplayNamespace::unlink_member_if_present_or_throw(
    const std::string& basename,
    const fs::path& display_path,
    const std::string& label) const {
    verify_namespace_or_throw(label + " namespace recheck");
    if (!inspect_member_or_throw(
             directory_authority_.descriptor_no_verify(), basename,
             display_path, label)
             .exists) {
        return false;
    }
    if (unlinkat_nointr(directory_authority_.descriptor_no_verify(), basename.c_str()) != 0) {
        if (errno == ENOENT) return false;
        throw_errno(label, "unlink", display_path);
    }
    verify_namespace_or_throw(label + " post-unlink namespace recheck");
    return true;
}

bool LocalJsonlReplayNamespace::unlink_journal_if_present_or_throw(
    const std::string& label) const {
    return unlink_member_if_present_or_throw(
        journal_basename_, journal_path_, label);
}

bool LocalJsonlReplayNamespace::
unlink_journal_staging_if_present_or_throw(
    const std::string& label) const {
    return unlink_member_if_present_or_throw(
        journal_staging_basename_, journal_staging_path_, label);
}

bool LocalJsonlReplayNamespace::unlink_temporary_if_present_or_throw(
    const std::string& temporary_name,
    const std::string& label) const {
    require_owned_temporary_name_or_throw(temporary_name, label);
    return unlink_member_if_present_or_throw(
        temporary_name, directory_authority_.path() / temporary_name, label);
}

void LocalJsonlReplayNamespace::fsync_directory_or_throw(
    std::string_view phase) const {
    const std::string label =
        "durable replay ledger parent directory " + std::string(phase);
    verify_namespace_or_throw(label + " pre-fsync");
    if (::fsync(directory_authority_.descriptor_no_verify()) != 0) {
        throw_errno(label, "fsync", directory_authority_.path());
    }
    verify_namespace_or_throw(label + " post-fsync");
}

}  // namespace anonsync::persistence

#endif
