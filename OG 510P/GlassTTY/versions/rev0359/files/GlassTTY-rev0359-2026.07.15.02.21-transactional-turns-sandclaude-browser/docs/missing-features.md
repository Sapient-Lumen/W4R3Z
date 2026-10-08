# What GlassTTY is still missing

An honest map, updated after the rev0359 transactional-turn pass. Ordered by how much each gap actually costs
you, not by how interesting it is to build.

## Landed

| | |
|---|---|
| rev0353 | **Conversation engine.** `ask` / `chat` / `run` — send a prompt, wait for the answer to settle, get the text. The thing the project was for. |
| rev0354 | **Surface intelligence.** Probe, history, diff, triage, auto-diagnosis on failure, and live repair without a rebuild. The thing that keeps rev0353 working as ChatGPT moves. |
| rev0355 | **Attachment transport and guards.** Chunked native-messaging transfer, zero-byte refusal, and fileless-prompt protection. |
| rev0356 | **First-flight measurement.** Live bridge/surface validation, authentication posture, and fail-truthful first-flight reports. |
| rev0357 | **Sandclaude browser handoff.** Self-describing extension/native-host bundle loaded before Chromium starts. |
| rev0358 | **Attachment lifecycle hardening.** Preflight, streaming sender, bounded/abortable transfers, multiset chip evidence, witnessed cleanup, and canary interlocks. |
| rev0359 | **Transactional turns and safe resume.** Attachment rollback, pre-existing-state refusal, explicit submit outcomes, content-addressed skips, and a durable in-flight journal. |

## Immediate blocker: authenticated attachment witness

The attachment transport exists and is deeply covered offline. What is not yet
proven is the final live witness: the attachment chip rendered by an authenticated
ChatGPT tab.

Your queuer's T1/T2 auto-recovery loop — attach a package, get a revision back,
capture it, re-send — is the feature that justified 4,800 lines of Tampermonkey.
It should not be trusted until this witness is measured rather than guessed.

What remains:

1. authenticate the persistent browser profile;
2. run `first-flight --learn-attachment` without `--canary`;
3. capture the real chip's stable attributes and add them to the role atlas and mock;
4. rerun the live attachment path and prove the new cleanup witness before
   submitting anything;
5. only then run one exact canary.

```bash
glassttyd ask "review this" --attach ./Project-rev0368.zip
glassttyd run queue.jsonl --attach-from ./packages/
```

## Then: the auto-recovery loop

With attachment in place, this becomes a natural `run` mode:

```bash
glassttyd loop --package ./Project.zip --out ./revisions/ --until "no more changes"
```

Needs one more primitive: a **download-completion witness** so the engine can wait
for the returned archive, verify it is non-empty, and feed it into the next turn.
Your queuer's quarantine-the-0-byte-zip logic is the spec; it was learned the
expensive way and should be ported as-is.

## Then: model / tier / version pinning

Your v6.45 notes captured the live 5.6 menu verbatim
(`Instant | Medium | High | Extra High | Pro | GPT-5.6 Sol ▸`). That is a
ready-made spec. It needs adapter support for the model picker and its submenus —
and it is exactly the kind of thing the surface wing should now be *watching*, so
that when the menu changes again (it will), you get a diagnosis instead of a
mystery.

```bash
glassttyd ask "..." --model "GPT-5.6 Sol" --effort pro
```

## Conversation and thread control

Currently the engine talks to whatever tab is there. `glassttyd new-chat` can
start a conversation, but it cannot:

- target a specific conversation (`--conversation <id>`)
- list your conversations
- branch or regenerate a turn

This is cheap to build and immediately useful: `run` should probably start a fresh
conversation per queue by default, rather than piling 200 prompts into one thread
and hitting the context wall.

## Live streaming to stdout

`ask` currently waits for the answer, then prints it. A CLI wants the tokens as
they arrive:

```bash
glassttyd ask "long thing" --stream | tee out.md
```

The adapter already emits `transcript.delta`. This is mostly plumbing, and it
makes `ask` feel native rather than batch.

## Parallelism

Your queuer ran many tabs at once. `run` is strictly sequential. `run --workers 4`
across several ChatGPT tabs would be a large real speedup — and GlassTTY already
has per-tab targeting (`--tab-id`) and a receiver model to make it safe.

## Retry

- `run --retry N` — a turn that fails for a *transient* reason (rate limit,
  network) should retry with backoff. Right now every failure is terminal.
  The surface wing can now tell transient from structural — use it.

## Rate-limit awareness

`surface-watch` can already see a rate-limit banner. Nothing acts on it. `run`
should notice, back off, and resume — rather than burning through a 200-prompt
queue against a wall.

## Response fidelity

`readLatestOutput` returns visible text. It loses:

- code-block boundaries and language tags
- markdown structure
- canvas / artifact content
- attachments the model produced

For a tool whose whole job is getting text *out* of ChatGPT, this is a bigger gap
than it looks. A `--format markdown` that reconstructs fenced blocks would make
`ask` genuinely pipeable into a file you can use.

## Deliberately not doing

From the queuer, and not coming back: DOM trimming, localStorage offload, memory
thresholds, heap-growth alerts, frame canaries, `pauseWhenHidden`, mouse-movement
humanization. These are rent paid for living in a browser tab. The commandline
does not pay it. See `docs/queuer-to-commandline.md`.

## The standing rule

Everything above is subordinate to one property, learned from your own changelogs:

> **A turn that did not settle is never reported as a success.**

The empty zip that was truthy. The sync that compared `latest === baseline` and
silently skipped. Those bugs cost you days, and they were both *silent successes*.
The conversation engine returns `ok: false` with a reason instead of partial text;
the repair engine proposes nothing rather than a wrong click. Defend that as the
list above lands.
