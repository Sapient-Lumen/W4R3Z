# Attachments (rev0359)

```bash
glassttyd ask "review this package" --attach ./GlassTTY-rev0355.zip
glassttyd run queue.jsonl --attach ./package.zip --out-dir ./out
glassttyd attach --attach ./notes.pdf          # stage without sending
```

The ChatGPT tab must be positively identified as logged in. Anonymous and
indeterminate authentication both fail before file bytes cross the bridge; the
existence of a hidden file input by itself is not evidence that ChatGPT will
accept an upload.

This is the capability that unblocks everything else. Your queuer's T1/T2
auto-recovery loop — send a package, get a revision back, re-send — has never been
possible from the commandline because GlassTTY could not put a file into the
composer. Now it can.

## How it gets there

Not by clicking "Add files and more". A page cannot script an OS file dialog, and
trying is how automation projects end up shipping fragile robot-mouse code.
GlassTTY writes straight into the hidden `<input type="file">` with a synthetic
`DataTransfer` — exactly what the page's own drop handler does. A preflight first
checks authentication and the upload input, so a large file is not streamed merely
to discover at commit time that the tab was logged out.

## The 1 MB wall

Chrome caps native-messaging **host → extension** messages at **1 MB**. A real
package is bigger than that, so it cannot cross the bridge in one message.

This is the exact wall that forced your userscript queuer to stand up a 448-line
local HTTP file server and pull the archive back into the page with
`GM_xmlhttpRequest`. GlassTTY does not need a server: the CLI splits the file into
384 KB chunks (≈512 KB of base64, comfortably under the limit), streams them over
the broker that already exists, and the content script reassembles them. The CLI
holds one chunk at a time instead of reading the whole file into memory. The content
script decodes directly into its final buffer instead of retaining a second set of
decoded chunk buffers.

```console
$ glassttyd ask "review this" --attach ./pkg.bin       # 12 MB
[glassttyd] attaching pkg.bin (12000000 bytes)…
[glassttyd] attachment: pkg.bin 12000000B sha256=988ef9485fbb chunks=31 · chip rendered
```

Reassembly is size-checked. Files are limited to 512 MiB; at most four transfers
may be active. Transfer ids, chunk counts, indices, and chunk payloads are bounded.
A failed or interrupted sender issues `attach.abort`, and an abandoned browser
buffer expires after 30 minutes. A truncated or malformed transfer fails loudly
rather than attaching a corrupt archive that looks fine to the eye.

## Two guards, both learned from your changelogs

### 1. The zero-byte trap

An empty `File` object is truthy. It attaches happily. ChatGPT then receives an
empty archive, and the failure surfaces downstream as a mystery — while your sync
baseline quietly advances past it. This is your v6.44 incident.

GlassTTY **refuses** a zero-byte file — at the CLI, and again in the adapter.
Not a warning. A refusal. (Files under 1 KB get a warning: *"is that really the
file you meant?"*)

### 2. The fileless prompt

Worse than a failed upload is one that *half* works: `input.files` is set the
instant we write it, but the file is not really attached until the page renders an
attachment chip. Submit in between and you send a prompt that says "review the
attached package" with **no package**. That doesn't look like a failure — it looks
like ChatGPT ignoring you, and you debug the wrong thing for a day.

So GlassTTY polls for the chip, and **refuses to submit** if it never appears:

```console
$ glassttyd ask "review the attached package" --attach ./pkg.zip
[glassttyd] attachment: pkg.zip 744697B chunks=2 · NO CHIP
[glassttyd] error: attached pkg.zip but no attachment chip rendered in the composer;
                   refusing to send a possibly fileless prompt
$ echo $?
1
```

Override with `--no-require-attachment` if you really mean it.

### Learning the chip selector

We do not hardcode a chip selector, because no authenticated live capture of one
exists yet. The 2026-07-14 anonymous control experiment set the browser file input
but produced neither an upload request nor a chip, matching ChatGPT's visible
login-required upload message.
Instead, GlassTTY snapshots the composer's controls *before* the file lands and
diffs afterwards. A witness requires either a control already classified as an
attachment chip, or both a new control and the uploaded filename becoming newly
visible in the composer. The control diff is a multiset, so adding a second chip
with the same test id or aria label is still observable. A filename already typed
in the prompt is not new evidence.

The first authenticated attachment therefore **self-documents** the attachment UI,
and the new control shows up in `added_controls` on the turn record. Fold it into
the role atlas only after reviewing that evidence.

## Cleanup is also witnessed

`first-flight --learn-attachment` clears every file input, dispatches both `input`
and `change`, and then polls until the file count is zero and the composer-control
multiset matches its pre-attachment baseline. A chip that remains is a hard failure.
If `--canary` was also requested, the canary is blocked rather than risk submitting
the probe file. Older extensions that return no cleanup witness fail closed.

The same rule now applies to ordinary sends. The first attachment captures a clean
composer baseline. If any later file fails, no chip appears, submit is blocked, or
the submit reply is lost, GlassTTY clears the staged files and records the cleanup
witness in `attachment_cleanup`. It also restores the original composer text and
records exact readback in `composer_cleanup`. A failed witness keeps the turn
failed and tells the operator to inspect the composer before sending anything else.

Normal sends also refuse a composer that already contains file-input state or a
known attachment chip, and refuse to overwrite a pre-existing operator draft.
This remains true after ChatGPT consumes `input.files` and leaves only the visible
chip. Standalone `glassttyd attach` still intentionally supports adding another
staged file.

## In a queue

Per-item attachments in JSONL — the T1/T2 shape:

```jsonl
{"name":"audit",  "prompt":"Audit the attached {{project}}.", "attach":"./pkg.zip"}
{"name":"revise", "prompt":"Now produce the next revision of {{project}}."}
```

```bash
glassttyd run queue.jsonl --out-dir ./out --var project=GlassTTY
```

Every turn records `name`, `bytes`, `sha256`, `chunks`, `chip_present`, the
submission outcome, and any cleanup witness in `transcript.jsonl`, so a run is
auditable after the fact.

## Flags

| flag | effect |
|---|---|
| `--attach PATH` | attach a file (repeatable; on `ask`, `run`, and `attach`) |
| `--chip-wait N` | seconds to wait for the attachment chip (default 30) |
| `--attach-timeout N` | whole-file transfer ceiling (default 180) |
| `--no-require-attachment` | submit even if the chip never rendered — risks a fileless prompt |

## What is still missing for the full loop

Attachment is one half. The other half is a **download-completion witness**: the
engine needs to wait for the revision archive to come back, verify it is non-empty,
and hand it to the next turn. That is the next major conversation-lane milestone
and the last piece before

```bash
glassttyd loop --package ./Project.zip --out ./revisions/
```

becomes real.
