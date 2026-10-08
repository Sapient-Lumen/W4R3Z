#pragma once

#include <string>
#include <string_view>

namespace anonsync {

// Canonicalize SQLite schema text only across syntactically irrelevant ASCII
// whitespace and keyword/identifier case outside quoted tokens. String
// literals and quoted identifiers are preserved byte-for-byte because their
// case and whitespace can change semantics.
[[nodiscard]] std::string canonicalize_sqlite_schema_sql_or_throw(
    std::string_view sql);

}  // namespace anonsync
