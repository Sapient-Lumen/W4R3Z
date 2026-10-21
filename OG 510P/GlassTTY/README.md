# GlassTTY

## Bring a browser conversation into a terminal workflow

GlassTTY lets a shell command work with a real ChatGPT tab in the operator's browser. A log can become input to a question; a response can become a file; a queue can carry successive prompts and retain their results. The point is to make conversation usable inside ordinary local work without replacing the browser session with an API-key service.

The supplied rev0359 connects a command-line client, a local Unix-socket broker, a native-messaging host, a Chromium extension and a ChatGPT page adapter. Prompts and files still travel to ChatGPT through the page. Local orchestration means that queue state and captured responses can live in files; it does not mean the conversation is offline or that browser behavior has ceased to matter.

## A turn needs more than a Send click

The [conversation interface](versions/rev0359/files/GlassTTY-rev0359-2026.07.15.02.21-transactional-turns-sandclaude-browser/docs/conversation-cli.md) has three principal forms. `ask` submits one prompt and returns text; `chat` provides an interactive loop; `run` works through named or templated prompts and records responses. Standard output carries answer text while diagnostics use standard error, allowing familiar shell composition. For example, the supplied interface supports `cat error.log | glassttyd ask "what caused this?" | tee triage.md`: local material becomes a question and the returned text becomes a reviewable file. The captured output is visible text, not a lossless export of Markdown, code-block structure, canvases or generated attachments.

The difficult part is knowing what the command may return. The [engine](versions/rev0359/files/GlassTTY-rev0359-2026.07.15.02.21-transactional-turns-sandclaude-browser/daemon/src/glassttyd/conversation.py) records the preceding output, stages the prompt, observes composer readback, submits, and polls the adapter's generation state, inferred from visible page controls such as Stop and Continue rather than supplied by an authoritative server lifecycle. Streaming and a Continue gate differ from settled output. Stable repeated observations help determine when to return. If the adapter cannot supply a generation lifecycle, the engine explicitly identifies its fallback as text-stability detection.

Composer readback is available without being unconditionally enforced: mismatch refusal requires `--require-readback`, and the implementation compares text after trimming surrounding whitespace rather than enforcing byte-for-byte equality. The result preserves how completion was detected, the submission outcome, timing, observations and errors. These fields are useful because a returned string alone cannot tell a caller whether the intended turn completed.

### An important rev0359 source discrepancy

The prose promises that an unfollowed Continue gate is never reported as success. The supplied implementation does not consistently meet that promise. In `_await_settled`, disabling continuation or exhausting its limit returns `needs-continue-not-followed` through `_settle`, which sets `ok=True`. The [CLI](versions/rev0359/files/GlassTTY-rev0359-2026.07.15.02.21-transactional-turns-sandclaude-browser/daemon/src/glassttyd/cli.py) uses that flag for its success exit and queue accounting; resume can then skip the matching successful record.

A caller must therefore inspect the reason as well as the flag before treating that result as a complete answer. This is a specific disagreement between source and documentation, not a reason to discard the useful lifecycle model. The preserved source remains unchanged.

## Carrying a file is an observable operation

The [attachment path](versions/rev0359/files/GlassTTY-rev0359-2026.07.15.02.21-transactional-turns-sandclaude-browser/docs/attachments.md) bridges a local file into the browser's file input in bounded chunks rather than creating another upload server. The Python sender streams chunks; the browser reassembles the file. This avoids a whole-file sender buffer, not whole-file storage everywhere.

Authentication and input availability are checked before streaming. Empty files are rejected. Setting the input is not the same as witnessing the page accept the attachment, so the adapter compares controls and newly visible filename evidence. Repeated controls are compared by multiplicity rather than assumed to be unique. The default send path requires an attachment witness; an explicit override can relax that requirement.

That distinction supports a concrete use: “review this package” should not silently become a prompt with no package. The supplied first-flight record established a live bridge and composer observations on 14 July 2026, but its anonymous session did not establish authenticated upload. The [recorded findings](versions/rev0359/files/GlassTTY-rev0359-2026.07.15.02.21-transactional-turns-sandclaude-browser/docs/live-first-flight-findings-2026-07-14.md) and current attachment design are different kinds of evidence.

## Transactional staging, not an undo button for the service

Rev0359 protects the boundary between local preparation and a possibly external effect. The engine refuses an existing operator draft rather than overwriting it. Attachment-backed staging records a clean baseline; failures trigger attachment cleanup and restoration of composer text, with separate witnesses. The existing-file check runs when a new attachment is staged, not on a plain send with no new attachment, so the broader prose promise that every normal send refuses pre-existing files is too strong. Unverified cleanup leaves an explicit inspection requirement.

A lost submission reply is not proof that submission failed. The engine records an unknown outcome rather than assuming permission to send again. Clearing local inputs cannot retract a request the service may already have received. “Transactional turns” names these bounded staging and recovery contracts, not a distributed exactly-once transaction with ChatGPT.

The [queue implementation](versions/rev0359/files/GlassTTY-rev0359-2026.07.15.02.21-transactional-turns-sandclaude-browser/daemon/src/glassttyd/cli.py) extends that distinction across a process crash. Before calling the turn engine, it durably writes an in-flight marker. Afterward it persists the transcript and response before removing the marker. Resume checks a successful record against the rendered prompt, name and attachment identities rather than trusting queue position. A submitted or ambiguous failed attempt, or an unresolved in-flight marker, stops automatic replay. A missing response file can be reconstructed from its recorded transcript.

This policy belongs specifically to resume. Explicitly starting a fresh run is not the same as proving that an earlier external effect never happened.

## Adapting to a page that changes

The surface machinery inventories page controls, classifies their roles, compares observations and proposes repairs to known selectors. It aims to distinguish the real Send control from a nearby attachment control rather than click whatever looks plausible. Read the [surface account](versions/rev0359/files/GlassTTY-rev0359-2026.07.15.02.21-transactional-turns-sandclaude-browser/docs/surface-intelligence.md) alongside the adapter when investigating a particular change.

The offline mock exercises the conversation protocol through a real local broker with a simulated tab. It is useful for streaming, stalls, continuation and drift cases. It is not evidence that a current live page exposes the same controls. The supplied browser integration is Chromium/MV3-specific.

## A direction distinct from a complete package-return loop

GlassTTY relocates orchestration into shell processes and files while retaining a browser adapter. [qomrade](../../guides/qomrade.md) sustains adaptive research, writing and construction through repeated continuation opportunities in a browser conversation. Both can support more than repetitive questioning, but their mechanisms and shipped scope should not be merged.

GlassTTY's [historical migration note](versions/rev0359/files/GlassTTY-rev0359-2026.07.15.02.21-transactional-turns-sandclaude-browser/docs/queuer-to-commandline.md) argues for moving queue state out of the tab. Its stronger rhetoric about eliminating browser costs should be read as a design argument, not a measured abolition of the browser's DOM, memory, authentication or lifecycle constraints. Its older parity table also predates the implemented attachment path.

The current [remaining-work account](versions/rev0359/files/GlassTTY-rev0359-2026.07.15.02.21-transactional-turns-sandclaude-browser/docs/missing-features.md) still identifies the missing download-completion witness needed to receive a revised archive and feed it into the next turn. A sequential prompt queue is not yet that complete construction loop. Model pinning, parallel workers and richer response extraction are also distinct proposed extensions.

The separate proof pipeline assembles checkpoint evidence; it is not required for an ordinary question and does not confer extra authority on conversation results. This separation lets the project be understood as a useful bridge with a development direction, rather than only as a record-certification apparatus.

## Read across the change in purpose

Start with the [current product introduction](versions/rev0359/files/GlassTTY-rev0359-2026.07.15.02.21-transactional-turns-sandclaude-browser/README.md), then the [conversation contract](versions/rev0359/files/GlassTTY-rev0359-2026.07.15.02.21-transactional-turns-sandclaude-browser/docs/conversation-cli.md), [attachment contract](versions/rev0359/files/GlassTTY-rev0359-2026.07.15.02.21-transactional-turns-sandclaude-browser/docs/attachments.md) and their implementation. Compare the early bridge and intermediate control-plane snapshots below to see what was retained and what the later CLI-first entrance brought forward. These are historical editions, not an assertion of present website compatibility.

Read beside [VHK](../VHK/README.md) for desktop-level interaction and [Sandcodex](../../guides/Sandcodex.md) for a separately maintained project environment.

## Version shelf and preservation

### Supplied snapshots

The reading route above is selective. This shelf retains every supplied snapshot and its original identity.

- [rev0003](versions/rev0003/README.md): 78 preserved members; `GlassTTY-rev0003-2026.03.06.21.15-sidepanel-broker-multiprofile-archive-luxury-switchyard.zip`.
- [rev0149](versions/rev0149/README.md): 2,280 preserved members; `GlassTTY-rev0149-2026.03.21.22.36-platformreceipt-surfacegate-webbound-kittiwake.zip`.
- [rev0359](versions/rev0359/README.md): 319 preserved members; `GlassTTY-rev0359-2026.07.15.02.21-transactional-turns-sandclaude-browser.zip`.

[Original identities](PROVENANCE.json) · [Back to OG 510P](../README.md)
