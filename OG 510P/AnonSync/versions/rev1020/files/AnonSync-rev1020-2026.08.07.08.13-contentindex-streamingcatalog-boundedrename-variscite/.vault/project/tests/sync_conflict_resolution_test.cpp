#include "sync_conflict_resolution.hpp"

#include <iostream>
#include <stdexcept>
#include <string>

namespace {

void require(bool condition, const std::string& message, int& checks) {
    if (!condition) throw std::runtime_error(message);
    ++checks;
}

template <typename Fn>
void require_throws(Fn&& fn, const std::string& message, int& checks) {
    bool threw = false;
    try {
        fn();
    } catch (const std::exception&) {
        threw = true;
    }
    require(threw, message, checks);
}

}  // namespace

int main() {
    using anonsync::SyncConflictDisposition;
    using anonsync::SyncConflictValueKind;
    using anonsync::make_sync_conflict_set_id_or_throw;
    using anonsync::resolve_sync_conflict_or_throw;

    try {
        int checks = 0;
        const std::string low(64, '1');
        const std::string high(64, 'e');

        const auto local_loser = resolve_sync_conflict_or_throw(
            SyncConflictValueKind::File, low,
            SyncConflictValueKind::File, high);
        const auto reversed = resolve_sync_conflict_or_throw(
            SyncConflictValueKind::File, high,
            SyncConflictValueKind::File, low);

        require(local_loser.disposition ==
                    SyncConflictDisposition::PreserveLocalFileThenApplyRemoteWinner,
                "lower file digest must preserve local loser before remote winner",
                checks);
        require(reversed.disposition ==
                    SyncConflictDisposition::PublishLocalWinner,
                "reversed file conflict must publish the same winner", checks);
        require(local_loser.winner_version_digest == high &&
                    reversed.winner_version_digest == high &&
                    local_loser.loser_version_digest == low &&
                    reversed.loser_version_digest == low,
                "orientation reversal must preserve winner and loser identity",
                checks);
        require(local_loser.canonical_first_version_digest ==
                    reversed.canonical_first_version_digest &&
                    local_loser.canonical_second_version_digest ==
                    reversed.canonical_second_version_digest &&
                    local_loser.canonical_first_kind ==
                    reversed.canonical_first_kind &&
                    local_loser.canonical_second_kind ==
                    reversed.canonical_second_kind,
                "orientation reversal must preserve canonical conflict identity",
                checks);

        const std::string forward_id = make_sync_conflict_set_id_or_throw(
            "folder-alpha", "docs/report.txt",
            SyncConflictValueKind::File, low,
            SyncConflictValueKind::File, high);
        const std::string reverse_id = make_sync_conflict_set_id_or_throw(
            "folder-alpha", "docs/report.txt",
            SyncConflictValueKind::File, high,
            SyncConflictValueKind::File, low);
        require(forward_id == reverse_id &&
                    forward_id.starts_with("conflict-") &&
                    forward_id.size() == 41U,
                "conflict-set identity must be orientation-independent and bounded",
                checks);
        require(forward_id != make_sync_conflict_set_id_or_throw(
                    "folder-alpha", "docs/other.txt",
                    SyncConflictValueKind::File, low,
                    SyncConflictValueKind::File, high),
                "conflict-set identity must bind the canonical path", checks);
        require(forward_id != make_sync_conflict_set_id_or_throw(
                    "folder-bravo", "docs/report.txt",
                    SyncConflictValueKind::File, low,
                    SyncConflictValueKind::File, high),
                "conflict-set identity must bind the folder", checks);
        require(forward_id != make_sync_conflict_set_id_or_throw(
                    "folder-alpha", "docs/report.txt",
                    SyncConflictValueKind::Tombstone, low,
                    SyncConflictValueKind::Tombstone, high),
                "conflict-set identity must bind each canonical value kind",
                checks);

        const auto file_loses_to_delete = resolve_sync_conflict_or_throw(
            SyncConflictValueKind::File, high,
            SyncConflictValueKind::Tombstone, low);
        const auto delete_wins_reversed = resolve_sync_conflict_or_throw(
            SyncConflictValueKind::Tombstone, low,
            SyncConflictValueKind::File, high);
        require(file_loses_to_delete.disposition ==
                    SyncConflictDisposition::PreserveLocalFileThenApplyRemoteWinner &&
                    file_loses_to_delete.winner_kind ==
                        SyncConflictValueKind::Tombstone,
                "tombstone must win while preserving concurrent local file bytes",
                checks);
        require(delete_wins_reversed.disposition ==
                    SyncConflictDisposition::PublishLocalWinner &&
                    delete_wins_reversed.winner_version_digest == low,
                "reversed file/delete race must select the same tombstone",
                checks);

        const auto tombstone_loser = resolve_sync_conflict_or_throw(
            SyncConflictValueKind::Tombstone, low,
            SyncConflictValueKind::Tombstone, high);
        require(tombstone_loser.disposition ==
                    SyncConflictDisposition::ApplyRemoteWinner &&
                    tombstone_loser.winner_version_digest == high,
                "tombstone/tombstone conflict must converge without fake file preservation",
                checks);

        require_throws(
            [&] {
                (void)resolve_sync_conflict_or_throw(
                    SyncConflictValueKind::File, "bad",
                    SyncConflictValueKind::File, high);
            },
            "malformed version digests must be rejected", checks);
        require_throws(
            [&] {
                (void)resolve_sync_conflict_or_throw(
                    SyncConflictValueKind::File, high,
                    SyncConflictValueKind::File, high);
            },
            "identical version digests are not a conflict", checks);
        require_throws(
            [&] {
                (void)resolve_sync_conflict_or_throw(
                    static_cast<SyncConflictValueKind>(99), low,
                    SyncConflictValueKind::File, high);
            },
            "unknown value kinds must fail closed", checks);
        require_throws(
            [&] {
                (void)make_sync_conflict_set_id_or_throw(
                    "folder-alpha", std::string("docs/") + '\n' + "bad",
                    SyncConflictValueKind::File, low,
                    SyncConflictValueKind::File, high);
            },
            "conflict-set scope must reject control bytes", checks);
        require_throws(
            [&] {
                (void)make_sync_conflict_set_id_or_throw(
                    std::string(129, 'f'), "docs/report.txt",
                    SyncConflictValueKind::File, low,
                    SyncConflictValueKind::File, high);
            },
            "conflict-set scope must bound folder identifiers", checks);
        require_throws(
            [&] {
                (void)make_sync_conflict_set_id_or_throw(
                    "folder-alpha", std::string(4097, 'p'),
                    SyncConflictValueKind::File, low,
                    SyncConflictValueKind::File, high);
            },
            "conflict-set scope must bound canonical paths", checks);

        std::cout << "sync conflict resolution tests passed (" << checks
                  << " checks)\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "sync conflict resolution tests failed: " << e.what()
                  << '\n';
        return 1;
    }
}
