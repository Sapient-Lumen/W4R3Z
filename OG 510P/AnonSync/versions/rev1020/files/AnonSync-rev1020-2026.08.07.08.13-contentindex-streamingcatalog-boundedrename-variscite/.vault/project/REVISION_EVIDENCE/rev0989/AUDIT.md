# Rev0989 audit

## Defect

Rev0988 removed the complete folder-catalog projection from each metadata-only dematerialization reproof, but the same effect still rebuilt the complete replica model three times. At the admitted 4,096-effect frontier and 10,000 retained operation envelopes, that shape could decode up to 122,880,000 operation rows in one pass.

## Correction

Rev0989 adds one transactionally pinned, path-local replica cutpoint. It reads typed metadata, at most two visible rows, the sole visible operation when one exists, and at most one distinct retained catalog predecessor. The folder owner pairs three such cutpoints with its three catalog cutpoints around rooted removal. No writer transaction spans filesystem work, and complete replica snapshots remain global planning and settlement authority.

## Adjacent audit/refactor

The first donor result copied global generations and digests without recomputing their complete source sets. Those fields were removed. Complete and targeted readers now share one exact operation-row decoder, same-operation target/predecessor roles share one owned envelope, and the inherited rev0988 lexical audit recognizes the consolidated runtime-test name without weakening its required query-shape phrases.

## Executable proof

The SQLite-owner suite passes 356 checks and the folder-owner suite 536 checks. Statement traces prove one exact visible query, one or two operation primary-key reads, one fixed schema/foreign-key proof per cutpoint, zero complete operation or visible projections, and 24 targeted replica cutpoints for eight dematerialized files while complete projections remain pass-bounded.

## Nonclaim

The cutpoint does not prove unrelated paths, recompute aggregate replica digests, hold a writer fence across filesystem work, or qualify million-path/multi-terabyte RSS. Target-scale measurement, insertion-resilient delta, rename/move identity, directory semantics, Android, and live public route qualification remain open.
