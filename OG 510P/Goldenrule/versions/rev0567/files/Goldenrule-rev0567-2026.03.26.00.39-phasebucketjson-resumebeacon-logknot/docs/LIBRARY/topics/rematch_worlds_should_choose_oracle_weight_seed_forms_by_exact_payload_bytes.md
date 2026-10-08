# Rematch worlds should choose oracle-weight seed forms by exact payload bytes

Once the archive preserves both the packed seed codec and the byteframe seed codec, `oracle_weights` first writes no longer need a live “materialize both candidates and compare them” branch.

The remaining comparison is local and exact:
- build the canonical packed weight payload once,
- compute the minified `packed_seed` length from that payload's JSON scalar lengths,
- compute the minified `byte_seed` length from the same payload's raw byte-token lengths plus unpadded base64url expansion,
- and materialize only the winning body.

This matters because the last measured frontier exception lives entirely inside `oracle_weights` payload shape. Non-weight first writes still go straight to `byte_seed`, and repeats still go straight to `byte_reference`.

## Why this is the right next rule

The archive had already compiled the frontier down to one live comparison: `{packed_seed, byte_seed}` for `oracle_weights`. That was much smaller than the older full-frontier search, but it still made the writer do unnecessary work. The packed payload already contains enough information to know both minified byte counts exactly.

So the archive should now treat the `oracle_weights` choice as an exact payload-byte calculation, not as a mini search.

## Practical consequence for the inheritor

Use this storage rule:
- repeats: `byte_reference`,
- non-weight first writes: `byte_seed`,
- weight first writes: compute exact packed-vs-byte seed lengths from the packed payload and emit only the winner.

That keeps the write rule exact while removing the last live candidate-body duplication from the zepto path.
