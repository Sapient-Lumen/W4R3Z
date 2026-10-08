# Subsecond struct layout change requires reinstancing or restart

This scenario exists to force **P-0537** to keep layout-affecting edits separate from ordinary function-body hotpatch wins.

Current `subsecond` docs say struct hot reloading is not supported because generated code assumes a particular layout and alignment.
Frameworks may mitigate this with reinstancing, but the crate should still export the barrier honestly.
