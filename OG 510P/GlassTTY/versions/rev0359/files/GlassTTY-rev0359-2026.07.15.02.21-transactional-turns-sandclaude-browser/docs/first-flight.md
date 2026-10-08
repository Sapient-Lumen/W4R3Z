# First flight — measuring GlassTTY against a real ChatGPT tab

GlassTTY first reached a live ChatGPT tab on 2026-07-14. That read-mostly flight
proved the complete bridge and corrected several assumptions that the offline
mock could not challenge. The authenticated attachment path is still unproven:
the browser profile used for that flight was logged out.

Treat every later flight as a *measurement*, not a demo. ChatGPT's UI moves and a
mock remains only a model of what we already know.

## 0. Install (Chrome or Chromium — not Firefox)

```bash
npm --prefix extension install
npm --prefix extension run build
# chrome://extensions → Developer mode → Load unpacked → select extension/
python scripts/extension-id.py            # note the id
# install the native host manifest (see daemon/README.md), then restart Chrome
```

Verify the bridge before anything else:

```bash
glassttyd doctor
glassttyd ping
```

`ping` now proves a round trip through the live Unix-socket broker; it is not a
local CLI no-op. If it fails, nothing below will work. The usual causes are that
the native-host manifest points at the wrong extension id or Chrome was not
restarted. Follow it with `glassttyd bridge-status --wait` to prove that a
supported browser tab can answer through the complete bridge.

## 1. Measure

Open a normal, **logged-in** ChatGPT conversation (`https://chatgpt.com/c/…`),
leave the composer empty, and run:

```bash
printf 'GlassTTY first-flight probe file.\n' > /tmp/probe.txt
glassttyd first-flight --learn-attachment /tmp/probe.txt --out flight.json
```

This is read-mostly. It will:

1. confirm the bridge is alive;
2. prove the composer contains no draft or attachment that could be overwritten;
3. probe the **idle** surface (expect: no send button — that is correct, see below);
4. probe again **with a draft staged** (expect: send visible; this is the definitive read);
5. promote only a fully classified, authenticated known-good baseline;
6. **attach a tiny file once and identify an attachment-chip candidate**;
7. clear every file input and prove the file count and composer-control multiset
   returned to their pre-attachment baseline.

If the tab is logged out or authentication cannot be verified, attachment preflight
stops before file bytes move. If the composer was not empty, no draft probe,
attachment, or canary mutation occurs. Any failed step or unresolved control makes
`first-flight` exit nonzero and records `ok: false` plus `failed_steps` in the report.

Add `--canary` to also send one real prompt and verify the round trip. It runs only
after a clean surface preflight and verified attachment cleanup, and succeeds only
when the settled answer is exactly `GLASSTTY-FIRST-FLIGHT-OK`.

Hand `flight.json` and the printed "things to resolve" list to Claude Code.

## 2. The remaining live unknown

**GlassTTY has not yet captured a real authenticated ChatGPT attachment chip.**
The 2026-07-14 anonymous experiment set the file input successfully both through
GlassTTY and through Playwright's native upload control, but ChatGPT emitted no
upload request or chip because the account was logged out. We deliberately do
not hardcode a guessed selector. The chip candidate is discovered by a multiset
diff of composer controls plus newly visible filename evidence. A filename already
present in the prompt cannot satisfy that witness. `--learn-attachment` prints it:

```
[glassttyd] ATTACHMENT CHIP CANDIDATE:
[glassttyd]   selector : …
[glassttyd]   testid   : …
[glassttyd]   aria     : …
[glassttyd]   classes  : …
```

Then: add it to `ROLE_ATLAS` in `extension/src/adapters/surface-probe.ts`, update the
placeholder in `mock_tab.build_mock_probe`, and delete the "this is a guess" comment.

Until that lands, `--attach` still refuses to submit an unwitnessed attachment — so
the worst case is a refusal, never a fileless prompt.

## 3. Risk register — what is most likely to break, in order

| # | Risk | How you'll know | What to do |
|---|---|---|---|
| 1 | **Browser profile is anonymous or indeterminate** | `authentication.posture` is not `authenticated`; attachment capability is false | Log in in the same persistent browser profile, then rerun. Do not weaken the check. |
| 2 | **Native host not wired** | `glassttyd ping` fails | Check the extension id in the host manifest; restart Chrome. Everything else is downstream of this. |
| 3 | **The attachment chip never renders while authenticated** | `first-flight` says "attached but NO chip" | Confirm the upload request occurred. The witness may be too narrow if the chip renders outside the `form`; inspect the live diff before widening `regionOf()`. |
| 4 | **ProseMirror ignores our text** | `prompt.write` returns `ok` but `readback` is empty/wrong | ProseMirror manages its own document model; a raw `textContent` write can be silently discarded. Fall back to the hidden `textarea[name=prompt-textarea]`, or dispatch a proper `beforeinput`/paste event. |
| 5 | **Send is found but the click does nothing** | `submit` returns `ok`, then `no-generation-detected` | Run `glassttyd ask "…" --diagnose`. React may need a real pointer event sequence rather than `.click()`. |
| 6 | **Generation lifecycle misread** | Answers truncate, or `ask` hangs to `--max-wait` | Check `detection` in `--json`. If it says `text-stability`, the stop/continue terms didn't match the live DOM. |
| 7 | **Chunked upload too slow** | A large `--attach` crawls | Each chunk is a broker round trip. Raise `ATTACH_CHUNK_BYTES` (conversation.py) toward the 1 MB ceiling, or pipeline the chunks. |
| 8 | **Route posture blocks submit** | `submit was blocked` on a valid page | The adapter refuses to submit outside a plain-chat route. Check `route.posture` in `surface-probe`. |
| 9 | **Attachment clear leaves a React-owned chip** | cleanup witness retains added keys after all file inputs are empty | Do not use `--canary`; inspect the chip's remove control and teach the adapter a measured removal action. |

## 4. Expected weirdness that is NOT a bug

- **The idle probe reports `surface-drift-cosmetic`, not `surface-ok`.** Correct.
  With an empty composer, `submit_prompt` is *unknowable*, not broken. That's why
  step 3 re-probes with a draft.
- **`generation_stop` and `generation_continue` are "not found".** Correct — nothing
  is generating.
- **`radix-*` ids everywhere.** Correct, and deliberately ignored. They change every
  page load; we never persist them as selectors.
- **A logged-out run refuses `--learn-attachment`.** Correct. Anonymous ChatGPT
  advertises login as a prerequisite for uploads, and the report preserves that
  authentication posture.
- **A nonempty composer blocks mutation.** Correct. First-flight will not test its
  restore logic on a draft or attachment the operator cares about.

## 5. When the UI changes later

```bash
glassttyd surface-watch --interval 300 &        # early warning
glassttyd ask "…" --diagnose                    # on any failure
glassttyd surface-repair --apply                # hot-patch, no rebuild
```

And to rehearse a change before it happens:

```bash
glassttyd surface-scenarios
glassttyd mock-tab --drift send-renamed
```

## 6. After first flight

Update the role atlas and mock so they match what you actually saw. The mock is
only worth anything if it is field-for-field faithful to the real page — it has
quietly disagreed with reality before while every offline test still passed.
