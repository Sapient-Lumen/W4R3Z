# 33 — Operator I/O Layer (Broadcast, tmux, hygiene) (v0.19)

The router can be perfect and you can still lose if your I/O layer lies.
Broadcast bugs look like “agents can’t follow instructions.”

## Terminator broadcast hazards
- Known behavior: duplicated keystrokes/characters in non-active panes on some setups.
- Treat broadcast as unsafe for:
  - long commands
  - non-idempotent actions
  - interactive typing

See: 29_broadcast_ops_guidance.md for guard rails.

## tmux synchronize-panes (alternative)
tmux can broadcast keystrokes to visible panes via `setw synchronize-panes`.
Advantages:
- stable + scriptable
- works over SSH/tailscale/etc
Tradeoff:
- usually only visible panes; you may need workflow adaptations.

## “File broadcast” best practice
Maintain `boot_prompt.txt` and broadcast:
- `cat boot_prompt.txt | <llm_cli>`
This is the highest leverage mitigation because it reduces keystrokes to one paste.

## Operator incident logging
When broadcast or terminal behavior misfires:
- log it as a first-class event (ledger)
- do not let it masquerade as model failure
