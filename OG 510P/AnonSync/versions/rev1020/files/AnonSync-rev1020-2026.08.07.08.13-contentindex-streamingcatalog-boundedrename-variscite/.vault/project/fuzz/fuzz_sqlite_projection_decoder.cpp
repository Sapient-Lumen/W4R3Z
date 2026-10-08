#include "canonical_projection_verifier.hpp"
#include "sqlite_projection_decoder.hpp"

#include <sqlite3.h>

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <string_view>
#include <utility>

using namespace anonsync::persistence;

namespace {

[[noreturn]] void invariant_failure(int line) noexcept {
    std::fprintf(stderr, "projection decoder fuzz invariant failed at line %d\n", line);
    std::abort();
}

void fuzz_require_at(bool condition, int line) noexcept {
    if (!condition) invariant_failure(line);
}

#define fuzz_require(condition) fuzz_require_at((condition), __LINE__)

class ByteCursor final {
public:
    ByteCursor(const std::uint8_t* data, std::size_t size) noexcept
        : data_(data), size_(size) {}

    std::uint8_t byte() noexcept {
        if (offset_ >= size_) return 0;
        return data_[offset_++];
    }

    std::uint64_t u64() noexcept {
        std::uint64_t value = 0;
        for (unsigned shift = 0; shift < 64; shift += 8) {
            value |= static_cast<std::uint64_t>(byte()) << shift;
        }
        return value;
    }

    std::string bytes(std::size_t maximum) {
        const std::size_t requested = static_cast<std::size_t>(byte()) %
            (maximum + 1);
        const std::size_t available = size_ - offset_;
        const std::size_t count = requested < available ? requested : available;
        std::string value(
            reinterpret_cast<const char*>(data_ + offset_), count);
        offset_ += count;
        return value;
    }

private:
    const std::uint8_t* data_;
    std::size_t size_;
    std::size_t offset_{};
};

class ProjectionFixture final {
public:
    ProjectionFixture() {
        const int open_result = sqlite3_open_v2(
            ":memory:",
            &database_,
            SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE,
            nullptr);
        fuzz_require(open_result == SQLITE_OK && database_ != nullptr);

        constexpr const char* kSql =
            "SELECT ?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12;";
        fuzz_require(sqlite3_prepare_v2(
                         database_, kSql, -1, &statement_, nullptr) == SQLITE_OK);
        fuzz_require(statement_ != nullptr);
    }

    ~ProjectionFixture() {
        if (statement_ != nullptr) {
            fuzz_require(sqlite3_finalize(statement_) == SQLITE_OK);
        }
        if (database_ != nullptr) {
            fuzz_require(sqlite3_close(database_) == SQLITE_OK);
        }
    }

    ProjectionFixture(const ProjectionFixture&) = delete;
    ProjectionFixture& operator=(const ProjectionFixture&) = delete;

    sqlite3_stmt* statement() noexcept { return statement_; }

    void clear() noexcept {
        fuzz_require(sqlite3_reset(statement_) == SQLITE_OK);
        fuzz_require(sqlite3_clear_bindings(statement_) == SQLITE_OK);
    }

private:
    sqlite3* database_{};
    sqlite3_stmt* statement_{};
};

ProjectionFixture& fixture() {
    static ProjectionFixture value;
    return value;
}

void bind_random_value(sqlite3_stmt* statement,
                       int parameter,
                       ByteCursor& cursor) {
    const std::uint8_t kind = cursor.byte() % 6;
    int result = SQLITE_ERROR;
    switch (kind) {
        case 0:
            result = sqlite3_bind_null(statement, parameter);
            break;
        case 1: {
            const std::string value = cursor.bytes(48);
            result = sqlite3_bind_text(
                statement,
                parameter,
                value.data(),
                static_cast<int>(value.size()),
                SQLITE_TRANSIENT);
            break;
        }
        case 2:
            result = sqlite3_bind_int64(
                statement,
                parameter,
                static_cast<sqlite3_int64>(cursor.u64()));
            break;
        case 3: {
            const std::string value = cursor.bytes(48);
            result = sqlite3_bind_blob(
                statement,
                parameter,
                value.data(),
                static_cast<int>(value.size()),
                SQLITE_TRANSIENT);
            break;
        }
        case 4: {
            const std::uint64_t bits = cursor.u64();
            double value = 0.0;
            static_assert(sizeof(value) == sizeof(bits));
            std::memcpy(&value, &bits, sizeof(value));
            result = sqlite3_bind_double(statement, parameter, value);
            break;
        }
        case 5: {
            // Regularly seed the one structured text class accepted by the
            // decoder so coverage does not depend on discovering 64 hex bytes.
            std::string digest(64, '0');
            for (char& character : digest) {
                const std::uint8_t nibble = cursor.byte() & 0x0f;
                character = nibble < 10
                    ? static_cast<char>('0' + nibble)
                    : static_cast<char>('a' + (nibble - 10));
            }
            result = sqlite3_bind_text(
                statement,
                parameter,
                digest.data(),
                static_cast<int>(digest.size()),
                SQLITE_TRANSIENT);
            break;
        }
    }
    fuzz_require(result == SQLITE_OK);
}

ProjectionColumnMap random_columns(ByteCursor& cursor) noexcept {
    const std::uint8_t mode = cursor.byte() % 4;
    if (mode == 0) {
        return {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11};
    }
    if (mode == 1) {
        std::array<int, 12> permutation{
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11};
        for (std::size_t index = permutation.size(); index > 1; --index) {
            const std::size_t swap_with =
                static_cast<std::size_t>(cursor.byte()) % index;
            std::swap(permutation[index - 1], permutation[swap_with]);
        }
        return {
            permutation[0], permutation[1], permutation[2], permutation[3],
            permutation[4], permutation[5], permutation[6], permutation[7],
            permutation[8], permutation[9], permutation[10], permutation[11],
        };
    }
    const auto index = [&cursor]() noexcept {
        return static_cast<int>(cursor.byte() % 18) - 3;
    };
    return {
        index(), index(), index(), index(), index(), index(),
        index(), index(), index(), index(), index(), index(),
    };
}

std::array<std::pair<ProjectionField, int>, 12> mapped_columns(
    const ProjectionColumnMap& columns) noexcept {
    return {{
        {ProjectionField::transport_envelope_idempotency_key,
         columns.transport_envelope_idempotency_key},
        {ProjectionField::transport_instance_id, columns.transport_instance_id},
        {ProjectionField::transport_key_id, columns.transport_key_id},
        {ProjectionField::peer_id, columns.peer_id},
        {ProjectionField::peer_session_id, columns.peer_session_id},
        {ProjectionField::peer_response_batch_idempotency_key,
         columns.peer_response_batch_idempotency_key},
        {ProjectionField::logical_path, columns.logical_path},
        {ProjectionField::payload_digest_sha256, columns.payload_digest_sha256},
        {ProjectionField::response_count, columns.response_count},
        {ProjectionField::total_bytes, columns.total_bytes},
        {ProjectionField::issued_at_epoch, columns.issued_at_epoch},
        {ProjectionField::expires_at_epoch, columns.expires_at_epoch},
    }};
}

void verify_map_preflight(const ProjectionDecodeResult& decoded,
                          const ProjectionColumnMap& columns) {
    const auto mapped = mapped_columns(columns);
    for (std::size_t current = 0; current < mapped.size(); ++current) {
        if (mapped[current].second < 0 || mapped[current].second >= 12) {
            fuzz_require(!decoded);
            fuzz_require(decoded.error().field == mapped[current].first);
            fuzz_require(decoded.error().failure ==
                         ProjectionDecodeFailure::invalid_column_index);
            return;
        }
        for (std::size_t prior = 0; prior < current; ++prior) {
            if (mapped[current].second == mapped[prior].second) {
                fuzz_require(!decoded);
                fuzz_require(decoded.error().field == mapped[current].first);
                fuzz_require(decoded.error().failure ==
                             ProjectionDecodeFailure::duplicate_column_index);
                return;
            }
        }
    }

    if (!decoded) {
        const ProjectionDecodeFailure failure = decoded.error().failure;
        fuzz_require(failure != ProjectionDecodeFailure::invalid_statement);
        fuzz_require(failure != ProjectionDecodeFailure::statement_not_positioned);
        fuzz_require(failure != ProjectionDecodeFailure::invalid_column_index);
        fuzz_require(failure != ProjectionDecodeFailure::duplicate_column_index);
    }
}

void verify_safe_error(const ProjectionDecodeResult& decoded) {
    if (decoded) return;
    const std::string summary = decoded.error().safe_summary();
    fuzz_require(summary.starts_with("sqlite_projection_decode["));
    fuzz_require(summary.size() <= 128);
    fuzz_require(!summary.empty() && summary.back() == ']');
}

}  // namespace

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t* data,
                                      std::size_t size) {
    if (size > 4096) return 0;

    ProjectionFixture& database = fixture();
    database.clear();
    sqlite3_stmt* const statement = database.statement();
    ByteCursor cursor(data, size);

    for (int parameter = 1; parameter <= 12; ++parameter) {
        bind_random_value(statement, parameter, cursor);
    }
    const ProjectionColumnMap columns = random_columns(cursor);
    const std::uint8_t state = cursor.byte() % 5;

    sqlite3_stmt* decode_statement = statement;
    switch (state) {
        case 0:
            decode_statement = nullptr;
            break;
        case 1:
            // Prepared and bound, but no current row.
            break;
        case 2:
            fuzz_require(sqlite3_step(statement) == SQLITE_ROW);
            break;
        case 3:
            fuzz_require(sqlite3_step(statement) == SQLITE_ROW);
            fuzz_require(sqlite3_step(statement) == SQLITE_DONE);
            break;
        case 4:
            fuzz_require(sqlite3_step(statement) == SQLITE_ROW);
            fuzz_require(sqlite3_reset(statement) == SQLITE_OK);
            break;
    }

    const ProjectionDecodeResult decoded =
        SqliteProjectionDecoder::decode(decode_statement, columns);
    verify_safe_error(decoded);

    if (state == 0) {
        fuzz_require(!decoded);
        fuzz_require(decoded.error().failure ==
                     ProjectionDecodeFailure::invalid_statement);
    } else if (state != 2) {
        fuzz_require(!decoded);
        fuzz_require(decoded.error().failure ==
                     ProjectionDecodeFailure::statement_not_positioned);
    } else {
        verify_map_preflight(decoded, columns);
    }

    return 0;
}
