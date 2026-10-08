#pragma once

#include <string>

struct sqlite3;

namespace anonsync::sync_checkpoint_owner_schema_internal {

// Create the sticky owner-mode table only when the durable main-schema object
// is genuinely absent, then attest the exact authority-bearing schema before
// any owner row is interpreted or migrated. Existing lookalike tables, views,
// indexes, triggers, TEMP shadows, and foreign-key drift fail closed.
void ensure_checkpoint_owner_schema_or_throw(
    sqlite3* db,
    const std::string& context);

// Re-attest the owner authority schema on the caller's current SQLite
// transaction snapshot. The mode table is mandatory; the legacy owner-lock
// table remains optional so a genuinely pre-owner database can still be read
// as unowned, but any present owner-lock object must match the reviewed schema
// exactly.
void attest_checkpoint_owner_schema_or_throw(
    sqlite3* db,
    const std::string& context);

}  // namespace anonsync::sync_checkpoint_owner_schema_internal
