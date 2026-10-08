# Support record — ChatGPT

## Metadata
- **surface key:** `chatgpt`
- **record status:** `seeded`
- **default browser lane:** `chromium-live`
- **last reviewed:** `2026-03-21`
- **rollout priority:** `recommended second adapter`

## Scope and assumptions
Chosen second-adapter target because it best tests whether the generic core widens beyond Claude without forcing a richer workspace abstraction too early. The first proof should stay on the plain browser chat lane before branching into Projects, GPT builder, Canvas, or other richer workspaces.

## Workflow rows

| workflow | current tier | lane | evidence refs / posture | caveats | promotion requirement |
|---|---|---|---|---|---|
| surface-detect | investigated | chromium-live | current first-party route anchors reviewed; no formal live bundle yet | route and entry posture may vary by auth state | capture first baseline and support bundle |
| receiver-resolve | investigated | chromium-live | current browser/home posture reviewed; no formal live bundle yet | overlays or account gates may interrupt first baseline | capture first baseline and support bundle |
| composer-read | investigated | chromium-live | initial accessible-first selector heuristics documented; no formal live bundle yet | composer affordances may vary by mode or tool state | capture first baseline and support bundle |
| composer-write | investigated | chromium-live | initial accessible-first selector heuristics documented; no formal live bundle yet | write path may drift across tool states | capture first baseline and support bundle |
| turn-submit | investigated | chromium-live | harmless-probe plan defined; no formal live bundle yet | submit affordance may differ across modes | capture first baseline and support bundle |
| generation-read | investigated | chromium-live | streaming/readback plan defined; no formal live bundle yet | streaming/latest-turn semantics may shift during generation | capture first baseline and support bundle |
| latest-turn-read | investigated | chromium-live | conversation-region-first readback plan defined; no formal live bundle yet | latest-turn grouping may drift with layout changes | capture first baseline and support bundle |
| support-capture | investigated | chromium-live | second-adapter brief plus ChatGPT first-proof kit now define artifact targets, selector priorities, and failure taxonomy | evidence still needs a named live bundle before promotion | capture first baseline and support bundle |

## Known blockers and risk notes
- route and layout variation
- tool/mode changes in the composer area
- search-capable home-lane variants that should be recorded without being mistaken for a route failure
- sidebar chat-history search cues that should not be mistaken for main-lane web search
- streaming/latest-turn parsing differences
- transient overlays or modal interruptions
- richer branch shells such as Projects, Canvas, or GPT builder

## Baseline capture plan
- start at the plain ChatGPT browser route and freeze the route/title/posture before touching richer modes
- confirm `surface-detect` and `receiver-resolve` first
- classify the landed shell with `CHATGPT-POSTURE-MATRIX.json` before assuming the route is baseline-safe
- run the resulting witness through `CHATGPT-BRANCH-GUARD.json` so route/auth/title/text cues resolve to continue, continue-with-caution, or stop before proof actions
- grade the same witness with `CHATGPT-ROUTE-WITNESS-RECEIPT.json` so sparse captures pause for recapture instead of silently inheriting high confidence
- grade the first concrete composer witness with `CHATGPT-COMPOSER-WITNESS-RECEIPT.json` so a discovered textbox cannot overclaim writability without actionability and readback proof
- grade the submit/generation/latest-turn witness with `CHATGPT-SUBMIT-WITNESS-RECEIPT.json` so a typed prompt does not overclaim a completed turn without dispatch, completion, and final readback proof
- grade the whole proof window with `CHATGPT-PROOF-BUNDLE-RECEIPT.json` so route, composer, submit, and artifact coherence all clear one bundle-level promotion gate before the slice moves to a stronger held bundle
- grade repeated held-quality windows with `CHATGPT-PROMOTION-STABILITY-RECEIPT.json` so stronger ChatGPT support language depends on repeatable proof rather than one lucky window
- bound the final wording with `CHATGPT-SUPPORT-CLAIM-RECEIPT.json` so repeated Chromium proof does not silently expand into broader browser or workspace guarantees
- bound the final wording again with `CHATGPT-CAPABILITY-PROFILE-RECEIPT.json` so a plain text-only baseline does not silently expand into Search, uploads, data analysis, voice, image, or other tool-mode support
- bound the session story with `CHATGPT-AUTH-WORKSPACE-RECEIPT.json` so guest, personal, Business, Enterprise, or Edu evidence does not silently blur together
- bound the subscription story with `CHATGPT-PLAN-ENVELOPE-RECEIPT.json` so guest, Free, Plus, Pro, Business, Enterprise, or Edu evidence does not silently blur together
- bound the browser story with `CHATGPT-BROWSER-ENVELOPE-RECEIPT.json` so one explicit Chromium lane does not silently blur into Chrome, Edge, Firefox, WebKit, or mobile support
- bound the conversation-retention story with `CHATGPT-RETENTION-ENVELOPE-RECEIPT.json` so standard saved-history chats, Temporary Chats, memory-off runs, and reused storage-state sessions do not silently blur together
- capture at least one composer state snapshot and one route/diagnostics snapshot
- preserve one failed candidate and one successful candidate so selector drift is reviewable
- use the exact-match benign probe from `CHATGPT-FIRST-PROOF-KIT.json` unless a safer lower-ambiguity probe is freshly justified
- treat the first useful failed run as evidence, not as wasted work

## Promotion notes
- To reach `experimental`, this surface needs at least one named support bundle or equivalent artifact for one lane.
- To reach `provisional`, the record needs current evidence, known caveats, and clearer drift posture.
- Stronger claims without named artifact refs should be treated as incomplete.

## Next action
Run the route-first baseline from `CHATGPT-FIRST-PROOF-KIT.json`, classify the landed shell with `CHATGPT-POSTURE-MATRIX.json`, evaluate the witness with `CHATGPT-BRANCH-GUARD.json`, confirm route proof readiness with `CHATGPT-ROUTE-WITNESS-RECEIPT.json`, confirm composer writability with `CHATGPT-COMPOSER-WITNESS-RECEIPT.json`, prove the submit/read-latest slice only when both receipts are honest enough to hand off, then repeat that baseline on a second distinct proof window, require `CHATGPT-PROMOTION-STABILITY-RECEIPT.json`, require `CHATGPT-SUPPORT-CLAIM-RECEIPT.json`, require `CHATGPT-CAPABILITY-PROFILE-RECEIPT.json`, require `CHATGPT-AUTH-WORKSPACE-RECEIPT.json`, require `CHATGPT-PLAN-ENVELOPE-RECEIPT.json`, require `CHATGPT-BROWSER-ENVELOPE-RECEIPT.json`, require `CHATGPT-RETENTION-ENVELOPE-RECEIPT.json`, and finally require `CHATGPT-PLATFORM-ENVELOPE-RECEIPT.json` before widening support language across tools, auth postures, workspace modes, subscription tiers, browsers, conversation-retention modes, or product surfaces.
