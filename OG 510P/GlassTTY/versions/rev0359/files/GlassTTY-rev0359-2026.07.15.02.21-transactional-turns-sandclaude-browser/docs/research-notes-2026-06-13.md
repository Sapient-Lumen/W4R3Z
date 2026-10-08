# Online research notes for rev0329

Date: 2026-06-13 UTC / 2026-06-12 America/New_York.

## ChatGPT web surface drift

OpenAI release notes show ongoing ChatGPT web changes in June 2026, including
model picker placement in the message composer and web conversation/composer
adjacent feature changes. This supports the cube strategy of live surface
inspection before adapter tuning.

Relevant sources checked:

- OpenAI Help Center, ChatGPT release notes.
- OpenAI Help Center, ChatGPT Enterprise & Edu release notes.

## Composer-adjacent controls

OpenAI's release notes describe composer and model-picker changes, and older
workspace release notes describe moving tools into a single Tools dropdown. The
adapter and surface inspector should therefore explicitly distinguish Send from
Tools, model picker, reasoning controls, search, uploads, voice, library/canvas,
and email/send-mail controls.

## CSP / console / extension model

The user's first console attempt showed CSP console noise plus a JavaScript
syntax failure caused by hard-wrapped source. The latest attempt reached the
report object and JSON logging stage, so rev0329 focuses on export reliability.

CSP itself is expected on modern web apps: MDN describes CSP as browser-enforced
restrictions on what page code can load or execute. Chrome extension content
scripts run in isolated worlds, and `chrome.scripting` can inject files into
isolated or main worlds. For this cube, the console inspector should not depend
on page `<script>` injection or `eval`; the extension should continue using
packaged content-script files.

## Clipboard / export path

MDN's Clipboard API documentation notes that writes require permission or
transient user activation. Browser/DevTools behavior can therefore make automatic
copy brittle even when the inspector successfully creates a report. rev0329 adds
small capsule output plus print, prompt, copy, and local download helpers.

Relevant sources checked:

- MDN, Clipboard API.
- MDN, WebExtension clipboard notes.
- MDN, Content Security Policy guide.
- Chrome for Developers, Content scripts.
- Chrome for Developers, `chrome.scripting` API / ExecutionWorld.

## rev0331: userscript oracle research

- Tampermonkey documents the exact convenience APIs this cube needs for a
  repeatable live-surface collector: `@match`, `@run-at`,
  `GM_registerMenuCommand`, `GM_setClipboard`, and `GM_download`.
- Browser content scripts and userscripts can read and modify page content with
  standard DOM APIs once the host is matched, which is enough for our adapter
  goals: composer discovery, safe write/readback, send-state detection, turn
  discovery, and mutation timing.
- Chrome content scripts run in an isolated world by default. This reinforces
  the product posture: the adapter should rely on DOM facts and readback rather
  than page-world monkeypatching.
- MDN and W3C input-event references continue to support dispatching
  `beforeinput`/`input` for contenteditable and text-editing hosts, but the
  cube still treats readback as the proof rather than event dispatch alone.
- OpenAI ChatGPT release notes continue to show web composer/model-picker churn
  in June 2026. The current live capsule's `composer-plus` false positive is
  consistent with that direction: composer-adjacent controls must be treated as
  hostile to naive send discovery.

## rev0333: drift contract and CLI direction

- The ChatGPT web surface is still too dynamic to trust static selectors alone.
  OpenAI release notes and current coverage of ChatGPT's product direction both
  point toward more composer-adjacent tools, model/tool controls, and agentic
  UI changes.
- The product should therefore keep a small executable surface contract close to
  the adapter. The contract should block only proof-path breakage: host/route,
  prompt editor, strict send, explicit author roles, and known false-positive
  submit controls.
- `MutationObserver` remains the right passive primitive for local drift
  observation because it watches DOM-tree changes without page-world injection.
- `beforeinput`/`input` remain useful for exercising contenteditable write
  paths, but readback is still the proof. Event dispatch without readback is not
  treated as success.
- The CLI should expose `doctor`, `surface-audit`, and `surface-contract-check`
  as first-class commands; stale fixture/coverage shims that referenced deleted
  scripts were removed from the parser.

## rev0334: proof rehearsal and release hygiene

The riskiest non-live gap was that the proof evaluator could only be exercised by hand-built tests. Rev0334 adds an offline rehearsal path that builds a synthetic checkpoint-shaped bundle, evaluates it, and deliberately returns `rehearsal-harness-ok-not-live` instead of a live-reviewable verdict. Package verification now rejects Python/test runtime caches before release.
