# Rev0942 focused audit

## Mission guard

The change advances the Resilio-replacement product spine: interrupted larger
regular files continue through the existing retained C++ peer service over the
same direct, Tor, or I2P stream boundary. Crash and namespace machinery remain
implementation discipline, not a separate mission.

## Waste removed: range-file fan-out and second assembly

Rev0941 persisted every response range as another immutable private file and
then allocated a whole-file assembly. Rev0942 uses one raw prefix file. Its
canonical basename is the durable commit record, eliminating both namespace
fan-out and the second full-sized receiver copy for new transfers.

## Severe defect corrected: pre-rename ctime retained as authority

Rename updates inode ctime on Linux. The draft retained the pre-rename `stat`
and later required exact observation equality, so a correctly committed complete
prefix could reject itself before publication. The owner now fsyncs the commit
rename, refreshes the open inode with `fstat`, verifies the new name, and binds
that post-commit observation.

## Capacity correction

Operator snapshots report physical transient bytes, including an uncommitted
crash tail. Admission separately reserves each prefix's complete declared size.
The runtime matrix proves that four physical bytes of a ten-byte owner consume
the full ten-byte completion reservation and block a second transfer under a
ten-byte budget.

## Restart and compatibility

A longer fsynced physical tail is truncated to the basename-committed cutpoint
on restart. Exact replay below the cutpoint is a no-op; conflicting replay and
gaps fail. A rev0941 range-file owner is detected and completed through its
retained implementation without creating a prefix competitor.

## Remaining risk

The hot path still traverses all private basenames, the maximum admitted file is
64 MiB, local/source APIs retain whole-file assumptions, shifted edits do not
reuse content, and no reachability/GC owner exists. Real workload and public
Tor/I2P qualification remain more important than further proof taxonomy.
