# ChatGPT selector notes

## Bootstrap heuristics

Prompt candidates:

- visible textbox-like control in the main chat region first
- `textarea`
- `[contenteditable="true"]`
- `[contenteditable="plaintext-only"]`
- `data-placeholder` composer roots
- ProseMirror-like editable roots under `main`

Submit candidates:

- visible in-scope `button` with accessible name resembling `Send`
- scoped `form button[type="submit"]` fallback
- keyboard submit is disabled for the first proof; submit must remain button/
  operator attested

Latest-turn candidates:

- explicit `[data-message-author-role="assistant"]` nodes or descendants first
- conversation region / landmark with visible turn grouping only as fallback
- most recent assistant turn in document order, with explicit `user` role
  excluded from assistant selection
- response-action cues preserved separately from the final readback

## Route posture

Start from the plain ChatGPT browser surface before branching into Projects, GPT
builder, Canvas, or other richer workspaces. The first baseline should prove the
generic chat lane, not every feature mode.

## Current mode and composer hazards

- ChatGPT's composer neighborhood changes frequently; model picker, tools,
  reasoning controls, uploads, voice, canvas/library, search, and email actions
  can sit close to the active receiver.
- Selectors should anchor to the active writable receiver instead of a fixed
  nearby button cluster.
- Send-button scoring should stay scoped to the composer and penalize non-send
  composer-adjacent controls unless a live capture shows a better rule.
- The most recent response may expose retry or branch actions; preserve those as
  cues, but do not confuse them with the final latest-turn extraction target.

## Expectations

These are first-pass heuristics. Prefer accessible, user-facing locators and
saved fixtures over brittle class chains or transient data attributes. The
working cube keeps only the minimal proof-kit and reference atlases in root;
older route, branch, support, capability, and plan receipts remain recoverable
from preserved archives if they become useful again.

## Breakage discipline

When ChatGPT UI changes:

- capture a capsule first
- audit it with `scripts/chatgpt-surface-report-audit.py`
- capture a full megathing fixture
- note whether the breakage was route detection, composer discovery, submit,
  generation, or latest-turn readback
- preserve at least one failed candidate and one winning candidate in the next
  bundle so drift is reviewable

## Composer witness discipline

- preserve main-region scope, not just the winning node
- record actionability (`visible`, `enabled`, `editable`) before calling a
  candidate writable
- preserve one post-write readback so the exact probe can be verified in the
  active composer
- when the winning family is `contenteditable`, keep rejected higher-priority
  candidates so the fallback stays reviewable

## rev0329 paste/report findings

The rev0328 console tool reached the report-object/JSON stage on the user's live
ChatGPT page, but the full JSON did not auto-copy from Firefox/DevTools. rev0329
therefore adds a small capsule tool and print/prompt/copy/download fallbacks.

The adapter now also scores `contenteditable="plaintext-only"`, `data-placeholder`,
and ProseMirror-like prompt roots because current rich composers may not always
look like a simple `textarea` or `contenteditable="true"` node.
