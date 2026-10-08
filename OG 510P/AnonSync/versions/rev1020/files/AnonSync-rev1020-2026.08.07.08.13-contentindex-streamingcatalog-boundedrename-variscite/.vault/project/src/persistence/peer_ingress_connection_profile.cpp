#include "persistence/peer_ingress_connection_profile.hpp"

#include <sqlite3.h>

#include <cstring>
#include <new>
#include <string>
#include <utility>

namespace anonsync {
namespace persistence {
namespace {

unsigned char ascii_lower(unsigned char value) noexcept {
    if (value >= static_cast<unsigned char>('A') &&
        value <= static_cast<unsigned char>('Z')) {
        return static_cast<unsigned char>(
            value + (static_cast<unsigned char>('a') -
                     static_cast<unsigned char>('A')));
    }
    return value;
}

bool has_file_uri_scheme(const char* filename) noexcept {
    constexpr char scheme[] = "file:";
    if (filename == nullptr) {
        return false;
    }
    for (std::size_t index = 0; index + 1 < sizeof(scheme); ++index) {
        const unsigned char actual =
            static_cast<unsigned char>(filename[index]);
        if (actual == 0 ||
            ascii_lower(actual) !=
                static_cast<unsigned char>(scheme[index])) {
            return false;
        }
    }
    return true;
}

bool filename_is_durable_file_candidate(const char* filename) noexcept {
    if (filename == nullptr || filename[0] == '\0') {
        return false;
    }
    // SQLite reserves :memory: and may assign semantics to more leading-colon
    // names in future versions. A crash-reconstructible checkpoint must never
    // depend on those process-local or future-special namespaces.
    if (filename[0] == ':') {
        return false;
    }
    // URI interpretation can be enabled globally at compile/start time even
    // when SQLITE_OPEN_URI is absent. Reject the scheme itself so query
    // parameters cannot override VFS, access, cache, immutable, or nolock
    // behavior behind this profile's back.
    return !has_file_uri_scheme(filename);
}

int allowed_application_open_flags() noexcept {
    int allowed = SQLITE_OPEN_READONLY |
                  SQLITE_OPEN_READWRITE |
                  SQLITE_OPEN_CREATE |
                  SQLITE_OPEN_FULLMUTEX |
                  SQLITE_OPEN_PRIVATECACHE;
#ifdef SQLITE_OPEN_EXRESCODE
    allowed |= SQLITE_OPEN_EXRESCODE;
#endif
#ifdef SQLITE_OPEN_NOFOLLOW
    allowed |= SQLITE_OPEN_NOFOLLOW;
#endif
    return allowed;
}

bool requested_access_is_canonical(int flags) noexcept {
    const int access = flags &
        (SQLITE_OPEN_READONLY | SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE);
    return access == SQLITE_OPEN_READONLY ||
           access == SQLITE_OPEN_READWRITE ||
           access == (SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE);
}

bool requested_profile_is_canonical(int flags) noexcept {
    if (!requested_access_is_canonical(flags)) {
        return false;
    }
    if ((flags & SQLITE_OPEN_FULLMUTEX) == 0) {
        return false;
    }
    if ((flags & (SQLITE_OPEN_URI |
                  SQLITE_OPEN_MEMORY |
                  SQLITE_OPEN_NOMUTEX |
                  SQLITE_OPEN_SHAREDCACHE)) != 0) {
        return false;
    }
    return (flags & ~allowed_application_open_flags()) == 0;
}

bool observed_access_matches(int flags, int observed_read_only) noexcept {
    if (observed_read_only != 0 && observed_read_only != 1) {
        return false;
    }
    const bool requested_read_only = (flags & SQLITE_OPEN_READONLY) != 0;
    return requested_read_only == (observed_read_only == 1);
}

int close_unpublished(sqlite3* database) noexcept {
    if (database == nullptr) {
        return SQLITE_OK;
    }
    // Nothing can have escaped this sealed boundary, so a strict close should
    // succeed. Retain close_v2 only as a leak-prevention fallback if SQLite
    // reports an unexpected internal dependent object.
    const int close_result = sqlite3_close(database);
    if (close_result != SQLITE_OK) {
        (void)sqlite3_close_v2(database);
    }
    return close_result;
}

int fail_verification(sqlite3* database,
                      sqlite3** published_database,
                      int result) noexcept {
    const int close_result = close_unpublished(database);
    *published_database = nullptr;
    return close_result == SQLITE_OK ? result : close_result;
}

}  // namespace

int open_verified_sqlite_database(const char* filename,
                                  sqlite3** published_database,
                                  int flags,
                                  const char* requested_vfs) noexcept {
    return open_verified_sqlite_database(
        filename, published_database, flags, requested_vfs, nullptr);
}

int open_verified_sqlite_database(const char* filename,
                                  sqlite3** published_database,
                                  int flags,
                                  const char* requested_vfs,
                                  SqliteConnectionEvidence* evidence) noexcept {
    if (published_database == nullptr) {
        return SQLITE_MISUSE;
    }
    *published_database = nullptr;
    if (evidence != nullptr) {
        *evidence = SqliteConnectionEvidence{};
    }

    if (!filename_is_durable_file_candidate(filename) ||
        !requested_profile_is_canonical(flags)) {
        return SQLITE_MISUSE;
    }

    sqlite3_vfs* const selected_vfs = sqlite3_vfs_find(requested_vfs);
    if (selected_vfs == nullptr || selected_vfs->zName == nullptr ||
        selected_vfs->zName[0] == '\0') {
        return SQLITE_CANTOPEN;
    }

    std::string pinned_vfs_name;
    try {
        // The registration owns zName. Copy it before opening so later error
        // paths do not depend on a borrowed registration string.
        pinned_vfs_name = selected_vfs->zName;
    } catch (const std::bad_alloc&) {
        return SQLITE_NOMEM;
    } catch (...) {
        return SQLITE_ERROR;
    }

    // PRIVATECACHE overrides any process-global shared-cache setting. The
    // requested flags remain separately visible in the evidence record.
    const int effective_flags = flags | SQLITE_OPEN_PRIVATECACHE;

    sqlite3* candidate = nullptr;
    const int open_result = sqlite3_open_v2(
        filename, &candidate, effective_flags, pinned_vfs_name.c_str());
    if (open_result != SQLITE_OK) {
        // sqlite3_open_v2 usually returns a handle carrying its best diagnostic
        // even on failure. Existing callers own/close that handle and may read
        // sqlite3_errmsg(), but no verification bit is minted for it.
        *published_database = candidate;
        return open_result;
    }
    if (candidate == nullptr) {
        return SQLITE_CANTOPEN;
    }

    const char* const observed_main_filename =
        sqlite3_db_filename(candidate, "main");
    if (observed_main_filename == nullptr ||
        observed_main_filename[0] == '\0') {
        return fail_verification(
            candidate, published_database, SQLITE_CANTOPEN);
    }

    const int observed_read_only = sqlite3_db_readonly(candidate, "main");
    if (!observed_access_matches(effective_flags, observed_read_only)) {
        return fail_verification(
            candidate, published_database, SQLITE_CANTOPEN);
    }

    // FULLMUTEX is requested, but a concrete connection mutex is the observed
    // proof that the opened generation actually materialized serialized mode.
    if (sqlite3_db_mutex(candidate) == nullptr) {
        return fail_verification(
            candidate, published_database, SQLITE_MISUSE);
    }

    // VFSNAME is diagnostic-only. VFS_POINTER is the authority check: it must
    // identify the exact object selected before open, defeating URI VFS
    // overrides and same-name substitutions during the open boundary.
    sqlite3_vfs* observed_vfs = nullptr;
    const int vfs_pointer_result = sqlite3_file_control(
        candidate, "main", SQLITE_FCNTL_VFS_POINTER, &observed_vfs);
    if (vfs_pointer_result != SQLITE_OK || observed_vfs != selected_vfs) {
        return fail_verification(
            candidate, published_database, SQLITE_CANTOPEN);
    }

    char* observed_vfs_stack = nullptr;
    bool vfs_name_diagnostic_available = false;
    if (evidence != nullptr) {
        const int vfs_name_result = sqlite3_file_control(
            candidate, "main", SQLITE_FCNTL_VFSNAME, &observed_vfs_stack);
        vfs_name_diagnostic_available =
            vfs_name_result == SQLITE_OK && observed_vfs_stack != nullptr;
    }

    if (evidence != nullptr) {
        try {
            SqliteConnectionEvidence completed;
            completed.requested_flags = flags;
            completed.effective_flags = effective_flags;
            completed.observed_read_only = observed_read_only;
            completed.requested_vfs_was_explicit = requested_vfs != nullptr;
            completed.file_backing_verified = true;
            completed.access_mode_verified = true;
            completed.serialized_mutex_verified = true;
            completed.vfs_identity_verified = true;
            completed.vfs_name_diagnostic_available =
                vfs_name_diagnostic_available;
            completed.pinned_vfs_name = pinned_vfs_name;
            completed.observed_main_filename = observed_main_filename;
            if (observed_vfs_stack != nullptr) {
                completed.observed_vfs_stack = observed_vfs_stack;
            }
            *evidence = std::move(completed);
        } catch (const std::bad_alloc&) {
            sqlite3_free(observed_vfs_stack);
            return fail_verification(
                candidate, published_database, SQLITE_NOMEM);
        } catch (...) {
            sqlite3_free(observed_vfs_stack);
            return fail_verification(
                candidate, published_database, SQLITE_ERROR);
        }
    }

    sqlite3_free(observed_vfs_stack);
    *published_database = candidate;
    return SQLITE_OK;
}

}  // namespace persistence
}  // namespace anonsync
