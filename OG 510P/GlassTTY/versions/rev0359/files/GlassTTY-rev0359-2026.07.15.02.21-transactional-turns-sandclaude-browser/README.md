# GlassTTY

**A commandline tool for working with ChatGPT.**

```bash
./glassttyd ask "explain this stack trace" < error.log
./glassttyd chat
./glassttyd run prompts.txt --out-dir ./out --var project=GlassTTY
```

GlassTTY drives a real ChatGPT tab in your own browser through a local
extension, a native-messaging host, and a Unix-socket broker. Your session, your
browser, your machine — no API key and no extra upload server. Prompts and files
still go to ChatGPT through the browser, exactly as they do when you use the site
directly.

## Before you trust it: first flight

The first live, read-mostly flight ran on 2026-07-14. It proved the complete
CLI → broker → native host → extension → ChatGPT-tab round trip and corrected
the live root-composer role atlas. It did **not** prove authenticated attachment
upload: the persistent browser profile was logged out, and ChatGPT disables file
uploads while anonymous.

```bash
glassttyd first-flight --learn-attachment ./small.txt --out flight.json
```

Read-mostly. It checks the bridge, requires an empty composer, probes the surface
idle and with a draft, promotes only a fully classified authenticated baseline,
and attempts to discover what an attachment chip actually looks like. Run it from
an authenticated ChatGPT tab. Attachment cleanup is witnessed before an optional
canary can run; any unresolved step makes the command exit nonzero. See
**[docs/first-flight.md](docs/first-flight.md)** for the runbook and
the ranked risk register,
**[docs/live-first-flight-findings-2026-07-14.md](docs/live-first-flight-findings-2026-07-14.md)**
for the measured result, and `CLAUDE.md` for the invariants.

**Chrome/Chromium only** (MV3, `sidePanel`, `offscreen`). Firefox is not supported.

## Sandclaude desktop handoff

The `rev0359` release is packaged as a self-describing
`*-sandclaude-browser.zip`. Put that archive and the Sandclaude script in the
directory Claude should own, then run Sandclaude. Sandclaude validates the archive,
loads this extension before Chromium starts, installs the matching native host in
the isolated browser home, and gives Claude complete Playwright control of that
browser. No `chrome://extensions` folder picker or browser restart is required.

After Claude unpacks the archive, the persistent project-side setup is one command:

```bash
./scripts/install-sandclaude.sh
./glassttyd ping
```

The first command only writes the native-host manifest inside Sandclaude's isolated
browser home. The release also carries a browser probe that verifies the real
extension -> native host -> Unix-socket broker round trip during Sandclaude doctor.

## Quick start

```bash
# 1. build + load the extension (unpacked, from extension/) in your browser
npm --prefix extension run build

# 2. ask something
./glassttyd ask "hello"
```

No browser handy? Everything below works offline against a built-in emulator:

```bash
./glassttyd mock-tab &        # a fake ChatGPT tab on the real broker
./glassttyd ask "hello"       # -> MOCK REPLY #1 to: hello
```

## The three commands

| command | what it does |
|---|---|
| `ask` | send one prompt, wait for the answer to finish, print it |
| `chat` | an interactive REPL against the live tab |
| `run` | work through a queue of prompts, capture every answer to disk |

`ask` prints the answer on **stdout** and diagnostics on **stderr**, so it pipes:

```bash
cat error.log | glassttyd ask "what caused this?" | tee triage.md
glassttyd ask "summarize" --file notes.md --json | jq -r .text
```

`run` is the commandline replacement for a browser prompt-queuer: template
variables, response capture, auto-continue, pacing, and `--resume`.

See **[docs/conversation-cli.md](docs/conversation-cli.md)** for the full
reference, and **[docs/queuer-to-commandline.md](docs/queuer-to-commandline.md)**
for how this maps onto (and mostly deletes) a Tampermonkey queuer.

## Attachments

```bash
glassttyd ask "review this package" --attach ./GlassTTY-rev0355.zip
```

Files are streamed from disk into the composer's hidden file input in 384 KB chunks
to cross Chrome's 1 MB native-messaging ceiling — no local HTTP server and no
whole-file Python buffer. Transfers are preflighted, bounded to 512 MiB, abortable,
and reassembled into one browser buffer. A zero-byte file is **refused**, and
GlassTTY **will not submit** a prompt whose attachment it could not witness (that
is a fileless prompt, and it looks like ChatGPT ignoring you rather than like a
bug). See
**[docs/attachments.md](docs/attachments.md)**.

## When ChatGPT's UI changes underneath you

It will. When it does, GlassTTY diagnoses itself:

```console
$ glassttyd ask "hello?" --diagnose
[glassttyd] diagnosis: surface-drift-blocking
[glassttyd] likely cause: submit was refused because the send control no longer
                          matches the expected surface
[glassttyd]   repair (confident): send -> [data-testid="composer-send-v2"]

$ glassttyd surface-repair --apply     # live patch, no rebuild
$ glassttyd ask "hello?"               # works again
```

The surface wing probes every control on the page, classifies it, keeps a history,
and reports anything it cannot name — so a new picker or a nag dialog shows up
*before* it breaks a queue run. `glassttyd mock-tab --drift send-renamed` lets you
rehearse a UI change that hasn't happened yet.

A repair is only ever applied when the replacement is **positively identified**.
When the real send button is gone and only an "Add files" decoy remains, GlassTTY
proposes nothing and stays broken — which is the correct answer.

See **[docs/surface-intelligence.md](docs/surface-intelligence.md)**, and
**[docs/missing-features.md](docs/missing-features.md)** for what is still absent.

## How an answer is known to be finished

This is the part that makes a CLI possible at all. The adapter reports an
explicit generation lifecycle, and the engine consumes it:

```text
write -> readback check -> submit -> poll generation
   streaming?      -> keep waiting
   needs-continue? -> click Continue, keep waiting
   settled?        -> require N stable polls, then return the text
```

If the page cannot report a lifecycle, the engine falls back to text-stability
detection and *says so* (`detection: text-stability`) rather than faking
precision. A turn that never started, never settled, or stopped at an unfollowed
continue gate comes back `ok: false` with a `settle_reason` — **never a silent
success holding partial text.**

## Architecture

```text
your shell
  -> glassttyd CLI            (ask / chat / run)
  -> conversation engine      (send -> settle -> continue -> return)
  -> broker (unix socket)
  -> native messaging host
  -> browser extension
  -> ChatGPT adapter          (composer, send control, turn witnesses, generation state)
  -> your ChatGPT tab
```

The adapter refuses to submit if the live surface drifted from the known-good
contract (wrong route, missing composer, an "Add files" control masquerading as
send). Safety is not humanization — it is verifying the control before clicking it.

## Layout

| path | what |
|---|---|
| `daemon/src/glassttyd/conversation.py` | the turn engine (send / settle / auto-continue) |
| `daemon/src/glassttyd/surface.py` | drift detection: snapshot / diff / triage / repair |
| `extension/src/adapters/surface-probe.ts` | the oddity hunter (control inventory + role atlas) |
| `daemon/src/glassttyd/mock_tab.py` | offline ChatGPT emulator on the real broker |
| `daemon/src/glassttyd/cli.py` | all commands |
| `daemon/src/glassttyd/broker.py` | unix-socket broker |
| `extension/src/adapters/chatgpt.ts` | ChatGPT DOM adapter |
| `extension/src/content/main.ts` | in-page message handlers |
| `scripts/chatgpt_proof_*.py` | the checkpoint-proof lane (see below) |

## Verify

```bash
npm --prefix extension run typecheck
npm --prefix extension run build
PYTHONPATH=$PWD/daemon/src:$PWD/scripts python -m pytest -q      # 310 passing
./scripts/smoke.sh
python scripts/verify-package.py
```

The conversation stack is fully covered without a browser: `mock-tab` stands up a
real broker and plays the tab, so `ask` / `chat` / `run` are exercised end-to-end
in CI.

## The proof lane

GlassTTY also carries a `proof-*` command family: a strict, heavily gated
pipeline that captures a live ChatGPT checkpoint reply into a 30-slot evidence
pack (ingest -> finalize -> integrity -> privacy review -> publish -> verify). It
is **untouched by rev0353** and still works.

It is a *sibling* of the conversation lane, not the product. Both use the same
adapter, broker, and protocol. Nothing in the conversation lane can forge a live
proof artifact, and nothing in the proof lane is required to run `ask`.

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-status --pretty
```

Its remaining work is unchanged: the live checkpoint capture has still not been
run. See `docs/chatgpt-first-proof-runbook.md`. The previous (rev0352)
proof-first README is preserved at `docs/README-rev0352-proof-cube.md`.

## rev0358 attachment lifecycle hardening

Extension `0.1.125` and daemon `0.1.11` make the attachment path fail closed from
preflight through cleanup. Anonymous or indeterminate authentication is rejected
before any file bytes cross the bridge. The sender streams from disk, malformed or
abandoned transfers are bounded and abortable, repeated identical chip controls
are diffed by multiplicity, and filename evidence must become newly visible.
`first-flight` will not overwrite an existing composer, promote an unclassified
baseline, or submit its exact canary until attachment cleanup is witnessed.

## rev0359 transactional turns and crash-safe resume

Extension `0.1.126` and daemon `0.1.12` make attachment-backed turns atomic up to
the browser boundary. Failed staging or submission clears command-owned files,
restores the original composer text, and records both cleanup witnesses;
pre-existing operator drafts, files, or known chips are never silently overwritten
or mixed into a send. If cleanup cannot be proved, the error explicitly says the
composer must be inspected before reuse.

`run --resume` no longer trusts queue position alone. It verifies the rendered
prompt, name, attachment paths, sizes, and SHA-256 values before skipping a settled
turn, and refuses to replay any attempt whose submit succeeded or became ambiguous.
A durable in-flight marker closes the crash window before transcript persistence,
while atomic response writes can be reconstructed from a verified transcript.

## rev0356 live-flight status

Extension `0.1.123` is loaded and speaking to the native host on a real ChatGPT
tab. The 2026-07-14 flight verified correlated native health, idle and drafted
surface probes, and a fully classified root composer. It
also found and fixed three assumptions the offline mock did not expose: the
current upload-input ids, idle-only Start Voice control, and legal links rendered
inside the composer form.

The remaining first-flight gap is narrow and explicit: log in to the persistent
browser profile, rerun `first-flight --learn-attachment`, then fold the observed
attachment chip into the role atlas and mock. No canary prompt has been submitted.

## rev0355 focus

File attachment — the capability that unblocks the queuer's T1/T2 auto-recovery
loop. Plus two bugs found by reading a live surface capture: ChatGPT renders no
send button until you type (probing empty and crying "drift" is a false positive),
and 65 of the page's ids are Radix-generated and change every load (persisting one
as a repair would work exactly once). See
**[docs/live-surface-findings-2026-07-11.md](docs/live-surface-findings-2026-07-11.md)**.

## rev0354 focus

The surface intelligence wing. rev0353 made GlassTTY usable; rev0354 keeps it
usable while ChatGPT's UI moves. Probe → snapshot → diff → triage → repair, with
auto-diagnosis wired into `ask --diagnose` and live selector overrides that fix a
drift without rebuilding the extension.

## rev0353 focus

Restored the stated purpose. The substrate could already read the composer,
write it, click send, and read turns — but nothing could tell you *when an
answer was done*, so nothing could hand one back. rev0353 adds the generation
lifecycle to the adapter and the settle loop above it, then the three commands
that were the point of the project: `ask`, `chat`, `run`.

Also fixed: `jsonschema` was a hard requirement of the proof lane but was never
declared as a dependency — a clean install silently failed schema validation and
five tests. It is now declared in `daemon/pyproject.toml`.
