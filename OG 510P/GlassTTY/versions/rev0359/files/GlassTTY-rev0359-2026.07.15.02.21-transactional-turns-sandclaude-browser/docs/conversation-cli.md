# Conversation CLI (rev0353)

This is the layer GlassTTY was always *for*: working with ChatGPT from the
commandline. Everything before rev0353 built the substrate — an adapter that can
read/write the composer, a native host, a broker socket, and one-shot request
primitives. What was missing was the loop that makes those primitives usable:
**send a prompt, wait for the answer to finish, hand back the text.**

## The three commands

```bash
glassttyd ask "explain this stack trace"      # one prompt, print the answer
glassttyd chat                                # interactive REPL
glassttyd run prompts.txt --out-dir ./out     # a queue of prompts, captured to disk
```

Plus one for working without a browser:

```bash
glassttyd mock-tab                            # offline ChatGPT emulator
```

## Why this is not just "write-prompt + submit-prompt"

The old primitives could stage text and click send. They could not tell you
*when the answer was done*, so there was nothing to return. rev0353 adds a
generation lifecycle to the adapter (`generation.state`) and a settle loop that
consumes it:

```text
write → readback check → submit → poll generation
   streaming?      → keep waiting
   needs-continue? → click Continue (up to --max-continues), keep waiting
   settled?        → require N stable polls, then return the text
```

Because the adapter reports the lifecycle explicitly, the engine is not guessing
from "has the text stopped changing" alone — that heuristic mistakes a slow
model for a finished one. When the lifecycle is unavailable (older extension
build), the engine degrades to text-stability detection and says so in
`detection`, rather than pretending precision it does not have.

Every exit is honest. An answer that never started, never settled, or stopped at
an un-followed continue gate is reported as a failure with a reason —
never as a silent success holding partial text.

## `ask`

Answer goes to **stdout**; diagnostics go to **stderr**. So it composes:

```bash
glassttyd ask "summarize this" < notes.md > summary.md
cat error.log | glassttyd ask "what caused this?" | tee triage.txt
glassttyd ask --file prompt.md --out answer.md
glassttyd ask "..." --json | jq -r .text
```

Useful flags:

| flag | effect |
|---|---|
| `--json` | full structured `TurnResult` instead of bare text |
| `--no-continue` | stop at a "Continue generating" gate instead of clicking it |
| `--max-wait N` | hard ceiling for one answer (default 180s) |
| `--start-grace N` | how long to wait for generation to *begin* (default 15s) |
| `--settle-polls N` | consecutive stable polls required to accept (default 2) |
| `--require-readback` | fail if the composer readback ≠ prompt exactly |
| `--no-submit` | stage the prompt in the composer, do not send |
| `--debug-snapshots` | attach every raw poll to `--json` output |

Exit codes: `0` settled, `1` did not settle, `3` broker unavailable.

## `run` — the queue

This is the commandline replacement for the userscript queuer's core loop.

Two formats. **Blocks** (`.txt`), split on `---`, optionally named:

```text
--- audit
Audit {{project}} for dead code.

--- roadmap
Given that audit, propose the next revision of {{project}}.
```

**JSONL** (`.jsonl`), one prompt per line, string or object:

```jsonl
"a bare string prompt"
{"prompt": "Audit {{project}}", "name": "audit", "vars": {"project": "GlassTTY"}}
```

Run it:

```bash
glassttyd run prompts.txt --out-dir ./out --var project=GlassTTY
```

Output:

```text
out/001-audit.md        # each answer as its own file
out/002-roadmap.md
out/transcript.jsonl    # one machine-readable record per turn
```

`transcript.jsonl` carries `ok`, `settle_reason`, `submission_outcome`,
`continues`, `polls`, `elapsed_s`, `detection`, and a content-addressed queue-input
fingerprint per turn — so a run is auditable after the fact.

Resume verifies rather than assumes:

```bash
glassttyd run prompts.txt --out-dir ./out --var project=GlassTTY --resume
```

A successful turn is skipped only when its rendered prompt, name, attachment paths,
sizes, and SHA-256 values still match. A definitely unsubmitted failure may be
retried; a submitted or transport-ambiguous failure stops to prevent a duplicate.
The hidden `.glasstty-inflight.json` marker is written durably before each call and
removed only after the transcript and response are persisted, so a process crash in
that interval also fails safe. A missing response file is reconstructed from its
verified transcript record.

Flags: `--stop-on-error`, `--resume`, `--json`,
`--format {auto,jsonl,blocks}`, `--var KEY=VALUE` (repeatable), plus all the engine
flags above.

## `mock-tab` — develop without a browser

`mock-tab` stands up a **real broker** on the normal socket and plays the role of
the extension + content script + ChatGPT tab, including a simulated streaming
lifecycle. `ask` / `chat` / `run` cannot tell the difference.

```bash
glassttyd mock-tab &          # terminal 1
glassttyd ask "hello"         # terminal 2 → "MOCK REPLY #1 to: hello"
```

Prompt markers the default responder understands:

| marker | behavior |
|---|---|
| `[[continue]]` | answer arrives in two parts (exercises auto-continue) |
| `[[stall]]` | submit succeeds, generation never starts |
| `[[error]]` | submit is refused |

Script it with `--rules rules.json`:

```json
[
  {"contains": "deploy", "reply": "Never on a Friday."},
  {"contains": "flaky",  "reply": ["part one", "part two"]},
  {"contains": "boom",   "refuse": true}
]
```

Use `--no-generation` to force the text-stability fallback path and prove your
tooling still works against an older extension build.

This is how the whole conversation stack is tested in CI: no browser, no network,
no ChatGPT account.

## Relationship to the proof lane

The proof lane (`proof-*`) is untouched and still gates its own artifacts. The
conversation layer is a *sibling*, not a replacement: it uses the same adapter,
the same broker, and the same envelope protocol. Nothing here can produce a
live-proof artifact, and nothing in the proof lane is required to use `ask`.
