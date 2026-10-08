# rev0006 U-123 duplicate-token microprobe

Purpose: prove the narrow state invariant without a full network harness. This is not yet an end-to-end exploit reproduction.

Harness: `tools/replay_u123_duplicate_token_probe.py` imports each source lane, monkeypatches the minimal `core.users.watch_user` and `events.schedule` dependencies, constructs two download `Transfer` objects for the same username, then calls `Transfers._activate_transfer()` twice with the same token.

Result: all three source lanes keep only one `active_users["alice"][4242]` entry, and that entry points to the second transfer. The first transfer retains token/timer fields but is no longer reachable through the active transfer map.

Raw JSONL:

```jsonl
{"active_tokens": [4242], "active_user_keys": ["alice"], "active_virtual_path": "\\Music\\b.mp3", "first_timer": "timer-1", "first_transfer_still_indexed": false, "first_transfer_token": 4242, "lane": "github-tag-3.3.10", "second_timer": "timer-2", "second_transfer_indexed": true, "second_transfer_token": 4242, "watch_calls": [["alice", "downloads"], ["alice", "downloads"]]}
{"active_tokens": [4242], "active_user_keys": ["alice"], "active_virtual_path": "\\Music\\b.mp3", "first_timer": "timer-1", "first_transfer_still_indexed": false, "first_transfer_token": 4242, "lane": "github-branch-3.3.x", "second_timer": "timer-2", "second_transfer_indexed": true, "second_transfer_token": 4242, "watch_calls": [["alice", "downloads"], ["alice", "downloads"]]}
{"active_tokens": [4242], "active_user_keys": ["alice"], "active_virtual_path": "\\Music\\b.mp3", "first_timer": "timer-1", "first_transfer_still_indexed": false, "first_transfer_token": 4242, "lane": "github-branch-master", "second_timer": "timer-2", "second_transfer_indexed": true, "second_transfer_token": 4242, "watch_calls": [["alice", "downloads"], ["alice", "downloads"]]}
```

Interpretation:

- This confirms the collision/overwrite primitive in the local state map.
- It does **not** yet prove a hostile peer can reliably choose or collide with a token in a live flow.
- It is strong enough to move U-123 to the next dynamic repro slot.
- It is not strong enough to promote U-123 into the strict final document.
