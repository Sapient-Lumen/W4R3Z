# Memory

- Scope is ChatGPT-only. Do not preserve multi-provider scaffolding in the
  working cube.
- User wants linked revisions named like
  `Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`.
- Latest live capsule: prompt editor is `#prompt-textarea`; route is plain
  `/c/...`; explicit author-role nodes are present; empty-composer send
  detection incorrectly found `#composer-plus-btn` / `Add files and more`.
- Current preferred next artifact: Tampermonkey oracle safe send-state drill.
- Keep probes local-only and privacy-first: no cookies/storage, no network
  writes, no auto-submit without explicit arming.


rev0346: Added `proof-autopilot` as conservative resumable command. Dry-run by default; `--execute-live` required for live ingest/finalize/publish.

rev0352: Added a ChatGPT side-panel recovery vault in local extension storage, with auto-save, restore, download, and clear controls for the assembled proof JSON.


## rev0352 note

Added static extension readiness (`proof-extension-readiness`) plus side-panel attempt readiness evidence (`proof.operator_readiness`) so the live browser attempt is guided before any download/ingest step.

- Rev0350: Download proof JSON is now gated by side-panel attempt readiness; `proof-attempt-audit` verifies ordered proof events.

- Rev0352 added `proof-pack-integrity` because artifact-ledger rows can stale after privacy review rewrites `privacy-redaction-review.md`.

## rev0353

- **Scope correction:** GlassTTY is a generalized ChatGPT commandline tool. The
  `proof-*` lane is a sibling capability, not the product. Do not let the working
  tree collapse back into the proof cube.
- The adapter exposes a generation lifecycle (`generation.state`:
  streaming-or-stoppable / needs-continue / settled-or-idle) and `prompt.continue`.
  This is what makes "wait for the answer, then return it" possible at all.
- `glassttyd mock-tab` runs a real broker and emulates the tab. Use it for
  development and tests instead of requiring a live browser.
- User's queuer (Tampermonkey v6.46) is the reference workload. Most of its bulk
  is browser tax (DOM trimming, localStorage quota, memory/heap guards, nag
  dismissal) and should NOT be ported. The parts that matter: queue, template
  vars, response capture, auto-continue, pacing, resume — all landed in rev0353.
  Still missing and genuinely needed: **file upload**, then the T1/T2
  auto-recovery loop, then model/version pinning.
- `jsonschema` is a real dependency (proof-lane schema validation). It was
  undeclared for a long time and silently failed 5 tests on clean installs.

## rev0354

- **Surface intelligence wing.** The old `surface-contract-*` tooling could only
  check known signals; it was blind to anything new, and every ChatGPT break has
  arrived as something new. The probe now inventories EVERY control, classifies it
  against a role atlas (`extension/src/adapters/surface-probe.ts`), and reports
  what it cannot name.
- `ask --diagnose` correlates a failed turn with live surface damage.
- `surface-repair --apply` writes runtime selector overrides into
  `chrome.storage.local`; the adapter consults them before its compiled selectors.
  **Fixes drift without a rebuild.**
- Hard safety rules, both regression-tested:
  - an override is a hint, not a bypass (still passes send-intent scoring);
  - a repair is only applied when positively identified. Early scorer bug: it
    proposed `send -> #prompt-textarea` (the text editor). Never again.
- `mock-tab --drift <scenario>` rehearses UI changes offline. Add a scenario when
  you spot something new in ChatGPT.
- When the wing reports an unknown composer control: add it to ROLE_ATLAS. That is
  how the tool learns the UI over time.

## rev0355

- **Attachments land.** Write to the hidden `input[type=file]` with DataTransfer;
  never try to drive the OS file picker. Chunk at 384 KB — Chrome's native-messaging
  host→extension cap is 1 MB, which is the whole reason the queuer needed an HTTP server.
- **Never submit an unwitnessed attachment.** Poll for the composer chip; refuse to
  send without it. A fileless prompt looks like ChatGPT ignoring you, not like a bug.
- **Never attach a zero-byte file.** Refuse, don't warn. (v6.44 incident.)
- The chip selector is NOT hardcoded — it is learned by diffing the composer before
  and after the file lands. Fold it into ROLE_ATLAS once observed.
- **From the live 2026-07-11 capture (read `docs/live-surface-findings-2026-07-11.md`):**
  - ChatGPT renders NO send button until the composer has text. Probing empty and
    concluding "send is gone" is a false positive. Use `--probe-with-draft`.
  - `radix-*` ids are regenerated every page load (65 of them live). NEVER persist
    one as a selector. Same for `div:nth-of-type(...)` paths.
  - Composer contains: `#composer-plus-btn` (attach), `.__composer-pill` (effort
    tier, e.g. "Pro"), "Start dictation". New chat is `[data-testid=create-new-chat-button]`.
