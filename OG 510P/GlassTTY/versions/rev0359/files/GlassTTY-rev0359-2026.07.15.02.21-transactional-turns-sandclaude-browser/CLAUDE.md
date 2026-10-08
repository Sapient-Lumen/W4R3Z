# CLAUDE.md — working on GlassTTY

## What this is

A commandline tool for working with ChatGPT through a real browser tab (extension
→ native host → Unix-socket broker → CLI). Not an API client. No API key.

**Chrome/Chromium only.** `manifest_version: 3`, `minimum_chrome_version: 120`,
uses `sidePanel` + `offscreen`. The native-host installer writes to the current
browser HOME's native-messaging directory. Firefox is not supported.

When this tree arrived as a `*-sandclaude-browser.zip`, Sandclaude already loaded
the validated built extension and a temporary matching native host before Claude
started. Unpack the archive, then run `./scripts/install-sandclaude.sh` to point the
manifest at this persistent project tree. Do not claim that the extension requires
the native Chrome folder picker in this environment; the startup handoff already
did that work.

```bash
npm --prefix extension run build            # then load extension/ unpacked
PYTHONPATH=$PWD/daemon/src:$PWD/scripts python -m pytest -q     # 310 passing
./glassttyd mock-tab &                      # offline ChatGPT emulator
./glassttyd ask "hello"
```

## The one rule

> **A silent success is worse than a loud failure.**

Every expensive bug in this project's history was a silent success. An empty zip
that was truthy. A sync that compared `latest === baseline` and skipped. A drift
contract that cried "blocker" on a healthy page until nobody read it. A repair
engine that proposed clicking the text box.

Concretely, and **do not weaken these**:

| invariant | where |
|---|---|
| A turn that did not settle is `ok: false` with a `settle_reason` — never partial text returned as success | `conversation.py` |
| A prompt whose attachment could not be **witnessed** is not submitted | `conversation.py` — the fileless-prompt guard |
| A zero-byte file is **refused**, not warned about | `conversation.py`, `chatgpt.ts` |
| A repair is only applied when the replacement is **positively identified** — an unknown never auto-applies | `surface.py::_score_replacement` |
| A surface override is a **hint, not a bypass** — it still passes send-intent scoring | `chatgpt.ts::findLikelySendButton` |
| Absent-because-idle is **not** damage (`null` ≠ `false`) | `surface.py::triage` |

There are regression tests for each. If one starts failing, the test is right.

## Things that are true about ChatGPT (learned the hard way)

Read `docs/live-surface-findings-2026-07-11.md`. The short version:

1. **There is no send button until the composer has text.** `#composer-submit-button`
   matches zero nodes on a perfectly healthy idle page. Probing empty and concluding
   "send is gone" is a false positive. Use `--probe-with-draft`.
2. **`radix-*` ids are regenerated on every page load** (65 of them live). Never
   persist one as a selector — not `#radix-_r_ds_`, not `button#radix-_r_ds_`. Same
   for `div:nth-of-type(...)` paths. `surface.py::is_stable_selector` enforces this.
3. **`#composer-plus-btn`** = "Add files and more". It is *not* send, and it has
   masqueraded as send before. It is disqualified explicitly.
4. Composer furniture: `.__composer-pill` (effort tier, e.g. "Pro" — id is volatile,
   match by class/text), "Start dictation", `[data-testid=create-new-chat-button]`.
5. The prompt editor is `#prompt-textarea`, a ProseMirror `div[contenteditable]`.
   A hidden `textarea[name=prompt-textarea]` fallback also exists.
6. The 2026-07-14 root page exposes upload inputs as `#upload-files`,
   `#upload-photos`, and `#upload-camera`; its idle-only voice action is labelled
   `Start Voice`; and Terms, Privacy Policy, and Learn more links can appear
   inside the composer form.
7. Visible login/signup controls mean the tab is anonymous. File upload is not a
   live capability in that posture, even if an `<input type=file>` exists.

## The mock is a model of our assumptions, and it has been wrong

`glassttyd mock-tab` stands up a **real broker** and plays the tab. The whole test
suite runs against it, offline. That is the good news.

The bad news: **a mock can only encode what we already believe.** Three separate
times, the mock quietly disagreed with the real content script (`transcript.latest`
key, witness shape, control classification) and the tests happily passed anyway.

So: **when you change the content script's reply shape, change the mock in the same
commit.** The mock must be field-for-field faithful, or the suite is theatre.

Anything in the mock that is a *guess* must say so in a comment. Currently guessed:
- the attachment chip's shape (no authenticated live capture exists yet — see below).

## Live first-flight status

The first read-mostly live flight ran on 2026-07-14. It proved the complete bridge,
idle and drafted surface probes, and a fully classified root composer. It did not
send a prompt. The remaining first-flight gap is authenticated attachment upload:
the persistent browser profile was anonymous, and current code refuses to promote
that incomplete surface as a baseline.

Before trusting attachment or submission on a new browser profile:

```bash
glassttyd first-flight --learn-attachment ./small.txt --canary --out flight.json
```

It is read-mostly (it only submits with `--canary`). It measures reality against
our assumptions, exits nonzero on any unresolved step, and prints a list of things
to resolve. `--learn-attachment` refuses immediately when the tab is logged out.

**The top unknown it will resolve: what an authenticated attachment chip looks like.**
We deliberately did not hardcode a selector; the chip is discovered by diffing the
composer before/after the file lands. When `first-flight` prints it:

1. add it to `ROLE_ATLAS` in `extension/src/adapters/surface-probe.ts` as `attachment-chip`;
2. update the placeholder in `mock_tab.build_mock_probe`;
3. drop the "this is a guess" comment.

## Layout

| path | what |
|---|---|
| `daemon/src/glassttyd/conversation.py` | turn engine: send → settle → continue → return; attachments |
| `daemon/src/glassttyd/surface.py` | drift: snapshot / fingerprint / diff / triage / repair |
| `daemon/src/glassttyd/mock_tab.py` | offline ChatGPT emulator + drift scenarios |
| `daemon/src/glassttyd/cli.py` | all commands |
| `extension/src/adapters/chatgpt.ts` | DOM adapter + runtime selector overrides |
| `extension/src/adapters/surface-probe.ts` | control inventory, role atlas, oddity hunter |
| `extension/src/content/main.ts` | in-page handlers, chunked attachment transfer |
| `scripts/chatgpt_proof_*.py` | the checkpoint-proof lane — a **sibling**, not the product |

## Do not let the proof lane eat the project again

Revisions ~0300–0352 collapsed into an elaborate pipeline to prove one canned
checkpoint reply, which *still has never been captured*. The conversation lane is
the product. The proof lane is untouched, still passes, and is not required by
anything. Leave it alone; do not expand it.

## Next up

1. **Download-completion witness** → then `glassttyd loop` (attach a package, wait
   for the revision, capture it, re-send). This is the last piece of the userscript
   queuer's T1/T2 auto-recovery loop. Port its quarantine-the-0-byte-zip logic verbatim.
2. Model/effort pinning via the composer pill (by class/text — its id is volatile).
3. `--conversation <id>`, `--stream`, `run --workers N`, rate-limit backoff
   (`surface-watch` can already see the banner; nothing acts on it).

See `docs/missing-features.md` for the full, honest list.

## Verify before you ship

```bash
npm --prefix extension run typecheck
npm --prefix extension run build
PYTHONPATH=$PWD/daemon/src:$PWD/scripts python -m pytest -q
python scripts/verify-package.py
```

Package the Sandclaude handoff as
`GlassTTY-rev####-YYYY.MM.DD.HH.MM-shortcodename-sandclaude-browser.zip`, clean
`__pycache__` and `node_modules` first, and ship `extension/dist/` prebuilt.
Use `python3 scripts/package-release.py --output /absolute/path/to/archive.zip`
from a clean committed tree; it packages only tracked regular files and verifies CRC.
