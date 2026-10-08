# Open feedback (rev331)

Rev331 is another tiny trust/flow follow-up.

The shared `open_file(...)` path was already doing the careful part:

- it parsed `file:line[:col]` targets when `parsecursor` was enabled
- it reused already-open buffers by normalized path instead of duplicating them
- it restored saved cursor positions when no explicit cursor target was given
- it kept scripted/capability-gated open behavior aligned with interactive open

But the command-level UX was still too tacit.

If you ran `open path/to/file` or `open path/to/file:42:3`, the editor would switch buffers and move the cursor correctly, but the command path itself did not say where you actually landed. In a visible TUI that is survivable; in headless use, prompt-driven workflows, scripted `ed.command` paths, and future LLM-guided flows, it is unnecessarily ambiguous.

## What rev331 changes

Explicit command-path opens now report the real landed target in one small shared summary:

- `opened: path/to/file @ 42:3`

That summary is taken from the post-open editor state, so it reflects the truth of where the cursor actually ended up rather than merely echoing the raw argument. That means it works for:

- parsed `file:line[:col]` targets
- savecursor-restored opens
- scripted/capability-gated `open ...` through `ed.command`
- already-open buffers that were simply reactivated

## Why this matters

This is still a tiny change, but it fits the current direction well:

- **trust**: explicit open commands should say what they actually did
- **flow**: after jumping to a file, the user should not have to ask “where did I land?”
- **headless continuity**: future scripts, frontends, and LLMs now inherit a more honest default command summary instead of having to reconstruct one themselves

Like rev329 and rev330, this deliberately stops short of a larger subsystem. It does **not** add a richer open dialog, project browser, or symbol jump surface. It just makes one common command speak more clearly.
