# AGENTS.md

This file is for human and LLM contributors.

## Project identity

- Project name: **GlassTTY**
- Core mission: user-driven bridge between browser state and local terminal workflows
- First adapter: **Claude.ai web app**
- Core product identity is **not Claude-specific**

## Non-negotiables

- Keep the browser open and visible in the primary workflow.
- Keep the user in control of reads, writes, and submit actions.
- Do not design around stolen credentials, hidden automation, or replaying private network traffic.
- Keep protocol boundaries stable and language-neutral.
- Keep the local daemon replaceable later, including a possible Rust rewrite.

## Architecture rules

1. The extension content script **observes and proposes** page state.
2. The extension background/service worker **normalizes and coordinates**.
3. The local daemon **owns persistent state and CLI semantics**.
4. Site-specific logic belongs in adapters, not in the protocol core.
5. The repo root docs are part of the product, not “extra paperwork”.
6. Browser-facing UX must remain user-driven even if automation helpers are added later.

## Memory discipline

Before changing code, read:

- `STATUS.md`
- `MEMORY.md`
- `DECISIONS.md`
- `TASKS.md`
- any adapter README relevant to the task

At the end of a session, update:

- `STATUS.md`
- `MEMORY.md`
- `TASKS.md`
- `CHANGELOG.md`

If the session changed an important design direction, append a short ADR-style note to `DECISIONS.md`.

## Amnesia resistors

Every substantial session should leave behind:

- what changed
- what is known to work
- what is unverified
- the next 1–3 sharp tasks
- any brittle assumptions, especially selector assumptions
- at least one repo-local artifact that a future LLM can inspect without rereading this entire repo

## Archive luxury rules

- Prefer adding small, high-value orientation files over burying decisions in chat.
- Keep repo docs concrete and operational.
- Leave breadcrumbs for unfinished work, not vague aspirations.
- Remove dead code and stale generated files from the archive.

## Coding standards

- TypeScript in the extension
- Python in the daemon/CLI for now
- stdlib-first unless a dependency clearly pays for itself
- shell scripts should be POSIX-ish when practical and include `set -euo pipefail`
- prefer plain JSON or JSONL over opaque binary formats for first versions

## What to avoid

- silently widening permissions in the extension
- baking Claude-only assumptions into shared protocol names
- putting long prose only inside chat history instead of back into the repo
- relying on service-worker globals for durable state
- shipping unnecessary generated cache files like `__pycache__` in release archives
