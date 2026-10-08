# Same-source rev0821/rev0822 differential

`sqlite_backup_namespace_authority_test.cpp` is byte-identical in the parent
and current builds (`bff502a0...a808`). The test mutates only the durable
`ledger_instance_id` to another valid 64-hex value while preserving decision
rows and entry count, then requests backup into a missing nested destination.

- rev0821 exits 2: `FATAL: backup accepted a substituted durable ledger identity`
- rev0822 exits 0: 36 passed, 0 failed

The current test also proves the rejected source cannot create the destination
directory, foreign publisher-temp content survives valid backup, and WAL, SHM,
and journal occupants reject without mutation.
