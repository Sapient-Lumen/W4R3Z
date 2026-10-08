# PB-01 reachability and compatibility audit — rev0074

## Audit question

Did the old packet prove a defect reachable from an adversarial network input, or did it prove only that a synthetic object graph can be constructed?

## Current state transitions

### Direct `PeerInit`

`_process_peer_init_message()` accepts a parsed `PeerInit`, assigns it to `init`, and calls `_replace_existing_connection(init)`. That helper removes the username/type mapping, copies the prior `outgoing_msgs` to the new `PeerInit`, clears the old queue, and closes the old socket. The current-behavior witness confirms this on the exact supported source.

What it does **not** prove is which socket deserves ownership. `PeerInit`'s username is a claim, and its token is documented as zero/ignored. First-wins and last-wins are both unauthenticated policies unless another state machine fact supplies freshness.

### Valid indirect secondary

The indirect path is narrower. A `PierceFireWall` frame is accepted only when its token exists in `_token_init_msgs`, which means the local client previously requested the indirect connection. If a direct connection already exists, current code keeps it primary but deliberately leaves the indirect socket open. When post-init traffic arrives on that socket, current code promotes it.

That is the path exercised by rev0074. It is not equivalent to “any remote socket can steal any primary.”

## Historical intent

The local Git history establishes a causal sequence:

1. `34b442a1218e42d906286d4ffd7c560ed993bb04` stopped aggressively rejecting an indirect connection after a direct connection was established. Its commit message says this fixes connectivity with some SoulseekQt users and relates the change to issue #2829, where browsing shares often failed on the first attempt.
2. `4932ef94c09956861e65b411c729cd74d947c4b9` is the immediate child. It updates `init.sock` when a message arrives over that retained secondary and logs promotion to primary.
3. The current protocol document explicitly describes modern clients attempting direct and indirect paths in the same connection sequence.

This does not prove every promotion is ideal. It does prove that deleting promotion merely because a primary is established is a compatibility-sensitive policy change, not an obvious hardening patch.

## Executable counterexample to rev0038

The new two-peer test models the same race from both ends:

```text
initiator A: direct leg established; valid indirect response retained as secondary
responder B: outgoing indirect response established; incoming direct leg arrives
```

Under the old rev0038 blanket guard:

```text
A keeps A→B direct as primary
B rejects A→B direct and keeps B→A indirect as primary
```

The peers now choose opposite TCP legs. The test passes only in the rev0038 lane because it demonstrates the undesirable split that the patch creates. Baseline and the origin-aware experiment fail that assertion, as intended.

## Narrow experiment and unresolved policy

The origin-aware prototype distinguishes an established outgoing response to an indirect request (`response_token` present) from another established primary. It allows the direct leg to replace the former and rejects direct-over-direct replacement.

This removes the specific split counterexample but does not authenticate the first direct claimant, define reconnection generations, or prove behavior under real socket teardown. It therefore remains an experiment. No patch is selected in rev0074.

## Evidence boundary

| Claim | Evidence level reached | Missing step |
|---|---|---|
| Direct-over-direct replacement exists | exact-current executable witness | safe desired election policy |
| Valid indirect secondary can be promoted | exact-current executable witness plus protocol/history | proof that this valid-race behavior is harmful |
| Arbitrary remote secondary can steal a primary | not reached | network construction outside a valid outstanding token |
| rev0038 prevents its chosen transitions | reached | compatibility correctness; counterexample disproves blanket policy |
| origin-aware guard is production-safe | not reached | end-to-end reconnect, liveness, mixed-client, and identity evidence |

The correct outcome is a split disposition, not a stronger single label.
