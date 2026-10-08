# Recent inventory disk/action truth

Rev511 closes one small but important trust seam in Micromax's recent-file loop.

Micromax already had the nearby honest surfaces:

- plain `recent` showed MRU order plus active/open/dirty/readonly/cursor state
- `recent_inventory_rows()` / `ed.recent-inventory-rows` exposed that same flat register to scripts and future UIs
- exact `showrecent PATH`, palette `Recent Files`, and dedicated `recentpick` rows already kept the stronger tiny `existing file` / `new file` plus `current buffer` / `switch buffer` / `empty buffer @ 1:0` truth when Micromax knew it

But one everyday inspection seam still lagged behind that model: the flat MRU list you reach first to ask “what will `recent N` actually do?” still stopped at open-state flags. That hid whether a row pointed at:

- one boring saved file on disk
- one missing-path scratch reopen
- the current live buffer
- another already-open buffer that `recent N` would only switch to

## What landed

Rev511 keeps the change deliberately small.

- `recent_inventory_rows()` now appends trailing `disk_truth` / `action_truth` fields after the existing stable state prefix
- plain `recent` reuses those same cues in the compact `| existing file | current buffer` dialect already trusted by exact recent-file surfaces
- the existing MRU slot/order and open-state fields stay intact

## Row shape

The shared row now reads:

```text
[index path position active open dirty readonly disk_truth action_truth]
```

Examples:

```text
[1 "/tmp/demo/scratch.md" "1:0" 1 1 0 0 "new file" "current buffer"]
[2 "/tmp/demo/old.txt" "" 0 0 0 0 "existing file" ""]
[3 "/tmp/demo/a.txt" "1:0" 0 1 0 0 "existing file" "switch buffer"]
```

And the matching human command now reads like:

```text
recent: 3 recent file(s), 1:*/tmp/demo/scratch.md @ 1:0 | new file | current buffer; 2:/tmp/demo/old.txt | existing file; 3:/tmp/demo/a.txt [open] @ 1:0 | existing file | switch buffer
```

The goal is simple: once Micromax already knows what one MRU entry will reopen or switch to, the plain inventory should say that truth directly instead of making humans or future LLMs infer it from neighboring commands.
