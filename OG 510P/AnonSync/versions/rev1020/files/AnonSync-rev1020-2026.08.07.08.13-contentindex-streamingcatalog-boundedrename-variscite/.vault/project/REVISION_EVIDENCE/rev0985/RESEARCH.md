# rev0985 research notes

A SQLite image deserialized as immutable and read-only does not necessarily report `sqlite3_db_readonly("main") == 1`, because the filename-free in-memory database is not the same backend condition as a named read-only file. Rev0985 therefore keeps named-file native read-only attestation and detached-image behavioral write denial as distinct, shared profiles.

The five artifacts are independently transactionally consistent but do not share a cross-database cutpoint. A complete-share backup still needs an explicit higher-level capture and recovery model binding payload reachability and bytes, the five databases, credentials, configuration, recovery epochs, and partial-set failure. Rev0985 intentionally does not infer that model from five successful component copies.
