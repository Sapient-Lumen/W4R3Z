# tokio_notify_coalesces_repeated_notify_one_without_skip_count

Tokio `Notify` documents that it carries no data, stores at most one permit, and that repeated `notify_one` calls before consumption collapse to one stored permit.

This scenario exists to keep **coalesced wake eligibility** separate from **counted sequence delivery**.
