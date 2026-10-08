# `IF NOT EXISTS` schema-confusion reproduction

`if_not_exists_schema_confusion.cpp` is a minimal program built against the
bundled SQLite 3.53.3 source. It creates a view named
`sync_session_checkpoint_owner_modes`, then executes the rev0811 bootstrap shape:

```sql
CREATE TABLE IF NOT EXISTS sync_session_checkpoint_owner_modes (...)
```

The retained log records:

- the statement returns `SQLITE_OK`;
- the surviving `sqlite_schema` object type is still `view`; and
- `SCHEMA_CONFUSION_REPRODUCED=true`.

The defect is not that SQLite violates its contract. The defect is treating
statement success as evidence that the reviewed authority table exists. Rev0812
instead inspects `main.sqlite_schema`, creates without `IF NOT EXISTS` only on
true absence, and attests exact durable geometry before any owner row is
interpreted.
