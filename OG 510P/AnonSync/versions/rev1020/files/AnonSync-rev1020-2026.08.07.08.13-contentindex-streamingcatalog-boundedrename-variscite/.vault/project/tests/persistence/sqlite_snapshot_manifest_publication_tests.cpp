#include "sha256_digest.hpp"
#include "sqlite_snapshot_manifest_publication.hpp"

#include <iostream>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>

namespace {

using anonsync::persistence::FrozenSqliteSnapshotManifestV2Payload;
using anonsync::persistence::SqliteSnapshotManifestPayloadFields;
using anonsync::persistence::SqliteSnapshotManifestSignatureFields;
using anonsync::persistence::SqliteSnapshotManifestV2Publication;
using anonsync::persistence::encode_sqlite_snapshot_manifest_v2_json_or_throw;
using anonsync::persistence::sqlite_snapshot_manifest_v2_signing_input_or_throw;

class HostileNumberFacet final : public std::num_put<char> {
protected:
    iter_type do_put(iter_type out,
                     std::ios_base&,
                     char_type,
                     long value) const override {
        const std::string text = "locale(" + std::to_string(value) + ")";
        for (const char c : text) *out++ = c;
        return out;
    }
    iter_type do_put(iter_type out,
                     std::ios_base&,
                     char_type,
                     unsigned long value) const override {
        const std::string text = "locale(" + std::to_string(value) + ")";
        for (const char c : text) *out++ = c;
        return out;
    }
    iter_type do_put(iter_type out,
                     std::ios_base&,
                     char_type,
                     long long value) const override {
        const std::string text = "locale(" + std::to_string(value) + ")";
        for (const char c : text) *out++ = c;
        return out;
    }
    iter_type do_put(iter_type out,
                     std::ios_base&,
                     char_type,
                     unsigned long long value) const override {
        const std::string text = "locale(" + std::to_string(value) + ")";
        for (const char c : text) *out++ = c;
        return out;
    }
};

class ScopedGlobalLocale final {
public:
    explicit ScopedGlobalLocale(const std::locale& replacement)
        : previous_(std::locale::global(replacement)) {}
    ScopedGlobalLocale(const ScopedGlobalLocale&) = delete;
    ScopedGlobalLocale& operator=(const ScopedGlobalLocale&) = delete;
    ~ScopedGlobalLocale() { std::locale::global(previous_); }

private:
    std::locale previous_;
};

void require(bool condition, const std::string& message, int& checks) {
    if (!condition) throw std::runtime_error(message);
    ++checks;
}

template <typename Callable>
void require_throws(Callable&& callable, const std::string& message, int& checks) {
    try {
        callable();
    } catch (const std::exception&) {
        ++checks;
        return;
    }
    throw std::runtime_error(message);
}

SqliteSnapshotManifestPayloadFields valid_fields() {
    SqliteSnapshotManifestPayloadFields fields;
    fields.manifest_revision_id = "rev0842";
    fields.parent_revision = "rev0841";
    fields.manifest_issued_at = "2026-07-19T12:34:56Z";
    fields.snapshot_sha256 = std::string(64, '1');
    fields.backend_name = "sqlite-wal";
    fields.backend_profile_backend_name = "sqlite-wal";
    fields.schema_version = 10;
    fields.entry_material_version =
        "anonsync-replay-ledger-entry-v7-ledger-instance-bound-transition-intent";
    fields.hash_algorithm = "sha256";
    fields.commit_protocol = "sqlite-wal-begin-immediate-full-sync";
    fields.line_count = 7000;
    fields.head_hash = std::string(64, '2');
    fields.expected_revision = "rev0842";
    fields.source_controls_revision = "rev0842-controls";
    fields.manifest_subject = "rev0842 local SQLite snapshot";
    fields.durability_ceiling =
        "local durable snapshot only; not remote replication evidence";
    return fields;
}

SqliteSnapshotManifestV2Publication publication_from(
    SqliteSnapshotManifestPayloadFields fields,
    std::string kid = "snapshot-root-A",
    std::string signature = "AbCdEf0123_-") {
    auto frozen = FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(
        std::move(fields));
    const std::string signing_input =
        sqlite_snapshot_manifest_v2_signing_input_or_throw(frozen);
    return SqliteSnapshotManifestV2Publication::bind_or_throw(
        std::move(frozen), anonsync::sha256_hex(signing_input),
        SqliteSnapshotManifestSignatureFields{
            std::move(kid), std::move(signature)});
}

std::string unchecked_parent_v2_signing_input(
    const SqliteSnapshotManifestPayloadFields& fields) {
    std::ostringstream out;
    out.imbue(std::locale::classic());
    out << "anonsync-sqlite-snapshot-manifest-v2\n"
        << fields.manifest_revision_id << '\n'
        << fields.parent_revision << '\n'
        << fields.manifest_issued_at << '\n'
        << fields.snapshot_sha256 << '\n'
        << fields.backend_name << '\n'
        << fields.backend_profile_backend_name << '\n'
        << fields.schema_version << '\n'
        << fields.entry_material_version << '\n'
        << fields.hash_algorithm << '\n'
        << fields.commit_protocol << '\n'
        << fields.line_count << '\n'
        << fields.head_hash << '\n'
        << fields.expected_revision << '\n'
        << fields.source_controls_revision << '\n'
        << fields.manifest_subject << '\n'
        << fields.durability_ceiling << '\n';
    return out.str();
}

}  // namespace

int main() {
    int checks = 0;
    try {
        const auto fields = valid_fields();
        auto frozen =
            FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(fields);
        const std::string signing_input =
            sqlite_snapshot_manifest_v2_signing_input_or_throw(frozen);
        require(signing_input.starts_with(
                    "anonsync-sqlite-snapshot-manifest-v2\nrev0842\nrev0841\n"),
                "snapshot signing domain or revision order changed", checks);
        require(signing_input.find("\n10\n") != std::string::npos,
                "snapshot schema version spelling changed", checks);
        require(signing_input.find("\n7000\n") != std::string::npos,
                "snapshot line_count spelling changed", checks);

        {
            const std::locale hostile(std::locale::classic(),
                                      new HostileNumberFacet);
            const ScopedGlobalLocale restore(hostile);
            const std::string locale_signing =
                sqlite_snapshot_manifest_v2_signing_input_or_throw(frozen);
            const std::string locale_json =
                encode_sqlite_snapshot_manifest_v2_json_or_throw(
                    publication_from(fields));
            require(locale_signing == signing_input,
                    "snapshot signing bytes depend on the global locale", checks);
            require(locale_json.find("\"schema_version\": 10") !=
                        std::string::npos,
                    "snapshot JSON schema_version depends on locale", checks);
            require(locale_json.find("\"line_count\": 7000") !=
                        std::string::npos,
                    "snapshot JSON line_count depends on locale", checks);
            require(locale_json.find("locale(") == std::string::npos,
                    "snapshot JSON contains hostile locale output", checks);
        }

        {
            auto source = valid_fields();
            auto snapshot =
                FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(source);
            const std::string before =
                sqlite_snapshot_manifest_v2_signing_input_or_throw(snapshot);
            source.line_count = 9000;
            source.manifest_subject = "mutated broad object";
            const std::string after =
                sqlite_snapshot_manifest_v2_signing_input_or_throw(snapshot);
            require(before == after,
                    "frozen snapshot payload changed after source mutation", checks);
            require(snapshot.fields().line_count == 7000 &&
                        snapshot.fields().manifest_subject ==
                            "rev0842 local SQLite snapshot",
                    "frozen snapshot payload retained source aliases", checks);
        }

        {
            auto left = valid_fields();
            auto right = valid_fields();
            left.expected_revision = "A\nB";
            left.source_controls_revision = "C";
            right.expected_revision = "A";
            right.source_controls_revision = "B\nC";
            require(left.expected_revision != right.expected_revision &&
                        left.source_controls_revision !=
                            right.source_controls_revision,
                    "collision witness tuples are not distinct", checks);
            require(unchecked_parent_v2_signing_input(left) ==
                        unchecked_parent_v2_signing_input(right),
                    "parent newline-delimited collision witness did not collide",
                    checks);
            require_throws(
                [&] {
                    (void)FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(
                        left);
                },
                "snapshot payload accepted a delimiter-bearing expected revision",
                checks);
            require_throws(
                [&] {
                    (void)FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(
                        right);
                },
                "snapshot payload accepted a delimiter-bearing source revision",
                checks);
        }

        {
            auto escaped = valid_fields();
            escaped.manifest_subject = "quoted \"snapshot\" and slash \\";
            const std::string json =
                encode_sqlite_snapshot_manifest_v2_json_or_throw(
                    publication_from(std::move(escaped), "kid-A", "A_b-9"));
            require(json.starts_with("{\n") && json.ends_with("}\n"),
                    "snapshot JSON object framing changed", checks);
            require(json.find("anonsync-sqlite-snapshot-manifest-payload-v2") !=
                        std::string::npos,
                    "snapshot JSON omitted payload format", checks);
            require(json.find(R"(quoted \"snapshot\" and slash \\)") !=
                        std::string::npos,
                    "snapshot JSON did not escape subject bytes", checks);
            require(json.size() <=
                        anonsync::persistence::
                            kSqliteSnapshotManifestMaximumJsonBytes,
                    "snapshot JSON exceeded its declared byte ceiling", checks);
        }

        {
            auto maximum = valid_fields();
            maximum.line_count =
                anonsync::persistence::
                    kSqliteSnapshotManifestMaximumExactJsonInteger;
            const auto maximum_payload =
                FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(maximum);
            require(sqlite_snapshot_manifest_v2_signing_input_or_throw(
                        maximum_payload)
                        .find("\n9007199254740991\n") != std::string::npos,
                    "snapshot payload lost maximum exact JSON integer", checks);
            maximum.line_count += 1;
            require_throws(
                [&] {
                    (void)FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(
                        maximum);
                },
                "snapshot payload accepted an inexact JSON integer", checks);
        }

        {
            auto bad = valid_fields();
            bad.line_count = 0;
            require_throws(
                [&] {
                    (void)FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(
                        bad);
                },
                "snapshot payload accepted zero line_count", checks);
            bad = valid_fields();
            bad.manifest_issued_at = "2026-02-30T00:00:00Z";
            require_throws(
                [&] {
                    (void)FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(
                        bad);
                },
                "snapshot payload accepted an impossible UTC date", checks);
            bad = valid_fields();
            bad.snapshot_sha256 = std::string(64, 'A');
            require_throws(
                [&] {
                    (void)FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(
                        bad);
                },
                "snapshot payload accepted uppercase digest text", checks);
            bad = valid_fields();
            bad.head_hash = "GENESIS";
            require_throws(
                [&] {
                    (void)FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(
                        bad);
                },
                "positive snapshot payload accepted GENESIS head", checks);
            bad = valid_fields();
            bad.schema_version = 9;
            require_throws(
                [&] {
                    (void)FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(
                        bad);
                },
                "snapshot payload accepted wrong schema version", checks);
            bad = valid_fields();
            bad.commit_protocol = "best-effort";
            require_throws(
                [&] {
                    (void)FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(
                        bad);
                },
                "snapshot payload accepted wrong commit protocol", checks);
        }

        {
            auto bad = valid_fields();
            bad.manifest_subject = std::string("bad-\xc3\x28", 6);
            require_throws(
                [&] {
                    (void)FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(
                        bad);
                },
                "snapshot payload accepted malformed UTF-8", checks);
            bad = valid_fields();
            bad.durability_ceiling.assign(
                anonsync::persistence::
                        kSqliteSnapshotManifestMaximumDurabilityCeilingBytes +
                    1,
                'c');
            require_throws(
                [&] {
                    (void)FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(
                        bad);
                },
                "snapshot payload accepted oversized durability text", checks);
        }

        {
            require_throws(
                [&] {
                    (void)publication_from(valid_fields(),
                                           std::string(257, 'k'));
                },
                "snapshot publication accepted oversized signer kid", checks);
            require_throws(
                [&] {
                    (void)publication_from(valid_fields(), "kid\nline");
                },
                "snapshot publication accepted control-bearing signer kid",
                checks);
            require_throws(
                [&] {
                    (void)publication_from(valid_fields(), "kid",
                                           "has=padding");
                },
                "snapshot publication accepted padded signature", checks);
            require_throws(
                [&] {
                    auto payload =
                        FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(
                            valid_fields());
                    (void)SqliteSnapshotManifestV2Publication::bind_or_throw(
                        std::move(payload), std::string(64, 'f'),
                        SqliteSnapshotManifestSignatureFields{"kid", "Ab_9"});
                },
                "snapshot publication accepted digest for another payload",
                checks);
        }

        std::cout << "SQLite snapshot manifest publication: " << checks
                  << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "SQLite snapshot manifest publication: " << error.what()
                  << '\n';
        return 1;
    }
}
