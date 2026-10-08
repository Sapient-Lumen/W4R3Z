# Preserved rev0790 replay-row acceptance defect

`replay_row_orphan_reproducer.cpp` is compiled once against the supplied
rev0790 parent and once against rev0791. It creates a valid integrated replay
reservation, disables foreign-key enforcement on a tampering connection, and
changes the reservation's `prepared_sequence` to nonexistent sequence `999`.

Rev0790 exits 0 and reports:

```text
orphaned_replay_row_reload_accepted=true
```

Rev0791 exits 2 and reports rejection by `PRAGMA foreign_key_check`. Exit 2 is
the expected outcome of this reproducer because its success criterion is that
reload must refuse the tampered database. No generated executables are shipped.
