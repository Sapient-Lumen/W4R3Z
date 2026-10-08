# Trailing-page authority reproducer

The permanent source is
`tests/persistence/sqlite_snapshot_geometry_binding_test.cpp`.

It creates a canonical SQLite database, appends one full ignored page, proves
ordinary SQLite still returns the original row and page count, copies the
logical database with `sqlite3_backup`, proves the suffix is discarded, and
then proves the production seal rejects before creating a staging directory.
