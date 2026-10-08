#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync::persistence {

inline constexpr std::string_view kLocalJsonlReplayEntryMaterialVersion =
    "anonsync-replay-ledger-entry-v3-effect-prepared";
inline constexpr std::string_view kLocalJsonlReplayJournalV2Format =
    "anonsync-replay-ledger-journal-v2";
inline constexpr std::string_view kLocalJsonlReplayJournalV3Format =
    "anonsync-replay-ledger-journal-v3";
inline constexpr std::string_view kLocalJsonlReplayV2CommitProtocol =
    "lock write-journal fsync-journal temp-write fsync rename fsync-dir unlink-journal";
inline constexpr std::string_view kLocalJsonlReplayV3CommitProtocol =
    "lock create-temp write-temp fsync-temp create-journal-stage write-journal-stage fsync-journal-stage link-journal-stage-to-journal unlink-journal-stage fsync-directory rename-temp-to-ledger fsync-directory unlink-journal fsync-directory";

inline constexpr std::int64_t kLocalJsonlReplayMaximumExactJsonInteger =
    9007199254740991LL;
inline constexpr std::size_t kLocalJsonlReplayMaximumEntryJsonBytes =
    64U * 1024U;
inline constexpr std::size_t kLocalJsonlReplayMaximumEntryHashMaterialBytes =
    64U * 1024U;
inline constexpr std::size_t kLocalJsonlReplayMaximumJournalJsonBytes =
    64U * 1024U;
inline constexpr std::size_t kLocalJsonlReplayMaximumLedgerBytes =
    64U * 1024U * 1024U;
inline constexpr std::size_t kLocalJsonlReplayMaximumEntryCount = 200000U;
inline constexpr std::size_t kLocalJsonlReplayMaximumPathBytes = 16U * 1024U;
inline constexpr std::size_t kLocalJsonlReplayMaximumTemporaryNameBytes = 255U;
inline constexpr std::size_t kLocalJsonlReplayMaximumFieldBytes = 16U * 1024U;
inline constexpr std::size_t kLocalJsonlReplayMaximumKindBytes = 64U;
inline constexpr std::size_t kLocalJsonlReplayMaximumActionBytes = 1024U;

// The exact owning representation of every byte in one local JSONL replay row.
// The historical hash material is retained for compatibility, but delimiter-
// bearing controls are excluded so the accepted newline-delimited tuple is
// injective. Production hashes and JSON are both derived from this value.
struct LocalJsonlReplayEntryFields final {
    std::int64_t sequence{};
    std::string previous_hash;
    std::string case_id;
    std::string kind;
    std::string operation_id;
    std::string contract_digest_sha256;
    std::string jti;
    std::string action;
    std::string cloud_event_source;
    std::string cloud_event_id;
    std::string effect_idempotency_key;
    std::string effect_state;
};

class FrozenLocalJsonlReplayEntry final {
public:
    [[nodiscard]] static FrozenLocalJsonlReplayEntry freeze_or_throw(
        LocalJsonlReplayEntryFields fields);

    [[nodiscard]] const LocalJsonlReplayEntryFields& fields() const noexcept {
        return fields_;
    }
    [[nodiscard]] const std::string& entry_hash() const noexcept {
        return entry_hash_;
    }

private:
    FrozenLocalJsonlReplayEntry(LocalJsonlReplayEntryFields fields,
                                std::string entry_hash)
        : fields_(std::move(fields)), entry_hash_(std::move(entry_hash)) {}

    LocalJsonlReplayEntryFields fields_;
    std::string entry_hash_;
};

[[nodiscard]] std::string local_jsonl_replay_entry_hash_material_or_throw(
    const FrozenLocalJsonlReplayEntry& entry);
[[nodiscard]] std::string encode_local_jsonl_replay_entry_json_or_throw(
    const FrozenLocalJsonlReplayEntry& entry);

// Validates the selected ledger namespace spelling with the same UTF-8,
// control-character, and byte-budget contract used by journal publication.
void validate_local_jsonl_replay_ledger_path_or_throw(std::string_view path);

// The journal is a recovery witness for one exact replacement payload. It is
// frozen independently from live backend state and emitted through one
// version-bound canonical encoder. Production mints crash-complete v3 while
// the decoder can retain exact v2 compatibility.
enum class LocalJsonlReplayJournalVersion : unsigned char {
    legacy_v2,
    crash_complete_v3,
};

struct LocalJsonlReplayJournalFields final {
    std::string ledger_path;
    std::string previous_head;
    std::int64_t previous_line_count{};
    std::string previous_payload_sha256;
    std::string next_head;
    std::int64_t next_line_count{};
    std::string last_entry_previous_hash;
    std::string payload_sha256;
    std::string temporary_name;
};

class FrozenLocalJsonlReplayJournal final {
public:
    [[nodiscard]] static FrozenLocalJsonlReplayJournal freeze_v2_or_throw(
        LocalJsonlReplayJournalFields fields);
    [[nodiscard]] static FrozenLocalJsonlReplayJournal freeze_v3_or_throw(
        LocalJsonlReplayJournalFields fields);

    [[nodiscard]] const LocalJsonlReplayJournalFields& fields() const noexcept {
        return fields_;
    }
    [[nodiscard]] LocalJsonlReplayJournalVersion version() const noexcept {
        return version_;
    }
    [[nodiscard]] std::string_view format() const noexcept;
    [[nodiscard]] std::string_view commit_protocol() const noexcept;

private:
    FrozenLocalJsonlReplayJournal(LocalJsonlReplayJournalVersion version,
                                  LocalJsonlReplayJournalFields fields)
        : version_(version), fields_(std::move(fields)) {}

    LocalJsonlReplayJournalVersion version_;
    LocalJsonlReplayJournalFields fields_;
};

[[nodiscard]] std::string encode_local_jsonl_replay_journal_json_or_throw(
    const FrozenLocalJsonlReplayJournal& journal);

}  // namespace anonsync::persistence
