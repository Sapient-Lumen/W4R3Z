# ChatGPT selector notes

## Bootstrap heuristics

Prompt candidates:
- visible textbox-like control in the main chat region first
- `textarea`
- `[contenteditable="true"]`

Submit candidates:
- visible `button` with accessible name resembling `Send` or `Submit`
- keyboard submit only after the writable composer path is proven and preserved as a fallback

Latest-turn candidates:
- `main`
- conversation region / landmark with visible turn grouping
- most recent assistant turn inside the main conversation region, with response-action cues preserved separately from the final readback

## Route posture

Start from the plain ChatGPT browser surface before branching into Projects, GPT builder, Canvas, or other richer workspaces. The first baseline should prove the generic chat lane, not every feature mode.

## Current mode and composer hazards

- the current ChatGPT home-page help article says the plain route is `chatgpt.com` and logged-out usage is limited to one conversation at a time
- the current chat-history search help article means a visible sidebar search affordance should not be mistaken for evidence that the main chat lane is in web-search mode
- Projects are logged-in workspaces and should be treated as a later branch, not the first baseline
- Canvas can open from prompt intent, the composer toolbox, or `/canvas`, so it should be treated as a route/mode branch when it appears
- current web-only model/thinking-time controls can change the shape of the composer neighborhood, so selectors should anchor to the active writable receiver instead of a fixed nearby button cluster
- the most recent response may expose retry or branch actions; preserve those as cues, but do not confuse them with the final latest-turn extraction target

## Expectations

These are only first-pass heuristics. Prefer accessible, user-facing locators and saved fixtures over brittle class chains or transient data attributes.
- `CHATGPT-POSTURE-MATRIX.json` should decide whether the landed shell is baseline-safe, cautionary-but-usable, or a branch that should stop the first proof
- `CHATGPT-BRANCH-GUARD.json` should evaluate the actual witness and preserve matched/conflicting cues before proof actions begin
- `CHATGPT-ROUTE-WITNESS-RECEIPT.json` should grade whether that witness is actually proof-ready or still too sparse to trust
- `CHATGPT-SUPPORT-CLAIM-RECEIPT.json` should bound the strongest honest support wording so repeated Chromium route-first proof does not silently imply broader browser or workspace coverage
- `CHATGPT-CAPABILITY-PROFILE-RECEIPT.json` should bound the strongest honest capability wording so a plain text-only pass does not silently imply Search, uploads, data analysis, voice, image, or other tool-mode coverage
- `CHATGPT-PLAN-ENVELOPE-RECEIPT.json` should bound the strongest honest subscription wording so guest, Free, Plus, Pro, Business, Enterprise, or Edu evidence does not silently blur together

## Breakage discipline

When ChatGPT UI changes:
- capture a fixture
- note whether the breakage was route detection, composer discovery, submit, generation, or latest-turn readback
- preserve at least one failed candidate and one winning candidate in the next bundle so drift is reviewable

## Composer witness discipline

- preserve main-region scope, not just the winning node
- record actionability (`visible`, `enabled`, `editable`) before calling a candidate writable
- preserve one post-write readback so the exact probe can be verified in the active composer
- when the winning family is `contenteditable`, keep rejected higher-priority candidates so the fallback stays reviewable
