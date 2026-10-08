# rev0770 primary references

Retrieved 2026-07-13.

- SQLite compile-time authorization callbacks:
  https://sqlite.org/c3ref/set_authorizer.html
  - one authorizer per connection;
  - later calls replace it and a null callback disables it;
  - authorization occurs during prepare/reprepare;
  - the correct callback must remain installed through `sqlite3_step()` because
    a schema change can trigger automatic reprepare.
- SQLite database connection client data:
  https://sqlite.org/c3ref/get_clientdata.html
  - named pointer storage exists in SQLite 3.44.0+;
  - the destructor runs on replacement, allocation failure, or connection
    close.
- SQLite database connection mutex:
  https://sqlite.org/c3ref/db_mutex.html
  - a non-null mutex serializes a connection in serialized mode.
- SQLite threading modes:
  https://sqlite.org/threadsafe.html
- SQLite open flags:
  https://sqlite.org/c3ref/open.html
  - `SQLITE_OPEN_FULLMUTEX` selects serialized mode;
  - `SQLITE_OPEN_NOMUTEX` selects multi-thread mode.

The implementation treats these APIs as local ownership mechanisms, not
cryptographic or durable evidence.
