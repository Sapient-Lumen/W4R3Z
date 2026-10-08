- rev0137 settled that the posture matrix alone was not enough; the second-adapter bring-up now needs a witness-driven branch guard that can classify concrete route/title/text/auth evidence into continue, continue-with-caution, or stop before proof actions begin.
## 2026-03-21 — The ChatGPT first proof needs a posture classifier, not just selector heuristics

Context:
- rev0135 defined how to probe the ChatGPT baseline once inside the page, but it still left too much ambiguity about whether the landed shell was actually the plain chat lane.
- Current OpenAI help surfaces now make several distinct postures explicit: plain home chat, search-capable home chat, Projects, Canvas, and the GPT builder workspace.

Decision:
- Add a machine-readable ChatGPT posture matrix that classifies baseline-safe, cautionary, and branch shells for the first proof.
- Treat Projects, Canvas, and GPT builder as stop-and-preserve branches, while allowing search-capable home chat as a caution variant when the main composer and latest-turn lane remain intact.

Consequence:
- Future ChatGPT bring-up runs can decide whether to continue or stop before writing/submitting, and the resulting support bundle can explain which shell was actually proven.


## 2026-03-21 — The second-adapter bring-up path should exist as a proof kit and queue object, not just prose

Context:
- rev0134 turned the ChatGPT choice into an execution brief, but the first proof still depended on too much operator interpretation.
- Without a named proof kit, future sessions could keep re-deciding probe text, selector priorities, failure classes, and artifact expectations.

Decision:
- Add a machine-readable ChatGPT first-proof kit with selector contract, benign exact-match probe, branching hazards, and failure taxonomy.
- Materialize that path as a named candidate support bundle so the review queue can point at one inspectable bring-up object.

Consequence:
- Future ChatGPT work should start from the proof kit and candidate bundle, then replace planning-only evidence with live route/composer/submit/readback artifacts instead of improvising a new baseline plan each time.


## 2026-03-19 — Feature work must be traceable to workflows, state, evidence, and release claims

Context:
- The repo now has broader ambitions, but broad ambition can still devolve into disconnected feature language.
- Future implementers need a way to test whether a proposed feature is merely appealing or actually buildable inside the GlassTTY model.

Decision:
- Treat feature traceability as a project rule.
- Major feature themes should be expressible in terms of affected workflows, state families, evidence outputs, support-truth effects, and release-claim consequences.

Consequence:
- Future planning docs should be able to answer not just “why add this?” but also “what workflows, artifacts, and support changes does it imply?”

## 2026-03-19 — Autonomy should widen through explicit ladder levels, not a binary switch

Context:
- GlassTTY now explicitly wants to support local/private LLM control, but the repo’s current strength comes from visible operator control and durable evidence.
- A binary “manual vs autonomous” framing would be too coarse for safe evolution.

Decision:
- Use a laddered autonomy model with bounded levels, approval expectations, stop conditions, and execution reporting.
- Treat broader autonomous behavior as a later capability that must inherit the lower-level discipline first.

Consequence:
- Future agent work should specify its autonomy level and required artifacts instead of hand-waving around “agent mode.”

## 2026-03-19 — Support records are living operational truth, not one-time planning notes

Context:
- The repo now has seeded support records, but seeded records are not the same as current operational truth.
- Without lifecycle rules, support records could drift into decorative placeholders.

Decision:
- Treat support records as living docs with seeded, backfilled, current, and stale states.
- Require updates when workflow proof, drift, lane meaning, or support tier changes.

Consequence:
- Future support records should reflect both the latest evidence posture and the date/reason they changed, rather than pretending support truth is static.

## 2026-03-19 — GlassTTY is now officially a multi-surface browser control plane

Context:
- The repo had already become more than a one-off Claude helper: it had a generic bridge, adapter language, fixture-lab work, and durable evidence lanes.
- The docs still described a browser-app-agnostic core with Claude as the first adapter, but the intended product had grown larger than that framing.
- Future implementers needed permission to design for multiple browser AI surfaces up front rather than treat them as distant “maybe later” work.

Decision:
- Treat GlassTTY as a local-first control plane for browser-native AI systems, not just a Claude-first bridge.
- Make Claude, ChatGPT, Google AI Studio, Grok, Kimi, and Z.ai official first-class browser surfaces in the repo canon.

Consequence:
- The repo should maintain explicit surface records, workflow targets, support truth, and evidence for those surfaces instead of naming them only in freeform notes.

## 2026-03-19 — Structured browser state is a first-class product surface

Context:
- The bridge already exposed useful reads and diagnostics, but too much meaning still lived in ad hoc payloads, human interpretation, or surface-specific output shapes.
- Multi-surface support and future agent operation both need stable state families with documented degradation behavior.

Decision:
- Promote a structured state API to first-class status in the project.
- Organize future reads and diagnostics around shared state families such as surface, receiver, composer, generation, conversation, turn, diagnostics, support, evidence, and action outcome.

Consequence:
- Future implementation work should prefer evolving current outputs into named state families instead of adding more bespoke commands with one-off schemas.

## 2026-03-19 — Drift detection and adaptation are core infrastructure, not side tooling

Context:
- Web AI surfaces change frequently.
- The repo already had fixture capture, comparison, and support-bundle instincts, but those capabilities still looked like local debugging tools rather than part of the product’s maintenance story.
- Multi-surface support will fail quickly unless the repo can detect and classify drift early.

Decision:
- Treat fixture-lab, probe captures, smoke bundles, comparison artifacts, and support ledgers as one drift-and-adaptation program.
- Define proactive baselines, drift severity, and next-action guidance as core support infrastructure.

Consequence:
- Future implementers should design evidence outputs so they can explain not only that a workflow failed, but what likely drifted and what should be tried next.

## 2026-03-19 — Support claims must be tracked per surface and per workflow

Context:
- “GlassTTY supports X” is too vague once the project spans multiple browser apps and multiple workflows per app.
- The repo already preserves many truthful artifacts, but not yet a clean support matrix that ties claims to workflows and evidence.

Decision:
- Define support truth per surface, per workflow, and per browser lane.
- Use explicit support tiers such as unsupported, investigated, experimental, provisional, and supported.
- Gate stronger claims on named evidence artifacts and release-gate questions.

Consequence:
- Future status reports should talk in terms like “ChatGPT: write/submit/read-latest experimental on Chromium lane” instead of all-or-nothing surface claims.

## 2026-03-19 — Human-piloted by default, agent-capable by design

Context:
- The repo has always valued a visible browser and user-driven control.
- The new direction explicitly includes allowing a local/private LLM to drive browser AI surfaces through GlassTTY.
- That expansion creates safety and observability requirements that need explicit design, not just optimism.

Decision:
- Keep human-piloted visible operation as the default interaction mode.
- Design agent-capable execution as a first-class extension of the same system, with policy classes, approval surfaces, stop conditions, and structured action outcomes.

Consequence:
- Future agent work should build on the existing operator-visible bridge and evidence lanes rather than bypass them.

## 2026-03-19 — Canonical product/design docs should carry strategy; handoff notes should carry history

Context:
- The repo’s archive discipline is strong, but strategic direction had started to spread across handoffs, research notes, and partial draft files.
- Future implementers should not have to reconstruct the intended product from historical notes.

Decision:
- Keep top-level docs and a small set of canonical design docs as the primary source of current direction.
- Treat handoff notes and research notes as historical memory, evidence, and nuance rather than the only place where major direction changes live.

Consequence:
- Strategic updates should land in the canon first, with handoff notes summarizing the delta and pointing back to the canonical docs.

## 2026-03-18 — Preserve one attempted run as a first-class artifact

Context:
- GlassTTY already preserves many truthful *state* ledgers (profiles, fleets, smoke, validate-release, readiness, operator handoff), but future sessions still have to infer which command somebody actually tried and compare separate snapshots by hand.
- The next expensive failure mode is attempt archaeology, not missing raw state.

Decision:
- Add a first-class paired `python scripts/operator-attempt.py start ...` / `finish ...` lane that freezes the before/after doctor/readiness/operator-handoff surface around one real validation/profile/browser run.
- Preserve finished attempts in a root-level `validation/operator-attempts.json` ledger and surface start/finish/history commands directly through `doctor.py`.

Consequence:
- Future sessions can inherit a true before/after attempt diff tied to the exact tried command instead of reconstructing one attempted run from unrelated captures.

## 2026-03-18 — Freeze the whole operator story, not just one ledger

Context:
- Chrome's current remote-debugging hardening still makes isolated profile state the durable browser boundary, while Playwright and MV3 guidance still reward preserving post-run artifacts instead of trusting ephemeral runtime state.
- rev0106 finally answered "what should the next session do first?" with a readiness board, but it still left the next session to gather the underlying ledgers, capture bundles, and memory docs by hand.
- The next expensive failure mode was not missing evidence; it was scattered evidence.

Decision:
- Add a first-class `python scripts/operator-handoff.py capture --output-dir ...` lane that freezes the current doctor/readiness surface, linked latest ledgers/bundles, and the core archive-memory docs into one durable support pack.
- Preserve that lane in a root-level `validation/operator-handoff-captures.json` history so future sessions can compare whole-operator state across runs, not just one subsystem.

Consequence:
- Future sessions can inherit one bundle that already answers both "what should I do next?" and "what evidence explains that recommendation?" instead of reconstructing the support pack manually.

## 2026-03-18 — The validation wrapper needs the same durable freeze lane as browser/profile evidence

Context:
- The remaining pain in this container is not lack of per-profile evidence; it is that long `validate-release.py` runs can still stop mid-flight.
- The wrapper already checkpoints state and supports `--resume`, but future sessions still have to spelunk `validation/latest/` manually to preserve or compare that partial state.
- Pytest's current documentation still recommends faulthandler timeout dumps and duration profiling for stuck/slow tests, which fits the exact forensic gap here.

Decision:
- Add default pytest diagnostics (`faulthandler_timeout`, `--durations`) to validation pytest steps.
- Add a first-class `validate-release-capture` lane plus a root `validation/validate-release-captures.json` ledger so interrupted wrapper state can be frozen, compared, and handed off like every other GlassTTY evidence lane.

Consequence:
- Future sessions can resume or compare umbrella validation runs from durable artifacts instead of inferring progress from a mutable `validation/latest/` directory.

## 2026-03-17 — The fleet-level profile view needs its own ledger

Context:
- Chrome's current remote-debugging hardening still makes the non-default managed profile directory the durable unit of CDP truth.
- rev0102 finally answered "which profile should I use next?", but the answer still disappeared unless a future session reran triage and doctor live.
- The next pain point is no longer ranking profiles; it is preserving and comparing the whole fleet view across sessions.

Decision:
- Add a first-class `glasstty-profile.sh fleet-capture --output-dir ...` lane plus `fleet-captures --pretty` history inspection.
- Freeze triage, full profile summaries, doctor output, and a fleet-vs-previous diff into one bundle while also updating a root-level `glasstty-profile-fleet-captures.json` ledger.

Consequence:
- Future sessions can answer "what changed across all managed profiles since last time?" from a durable artifact instead of reconstructing it from a new live scan.

## 2026-03-17 — Managed profiles need a fleet-level triage lane

Context:
- Chrome's current remote-debugging hardening still makes the non-default managed profile directory the unit of CDP truth.
- Recent revisions made single profiles replayable, portable, captureable, and ledger-backed, but future sessions still had to inspect one profile at a time to decide what to do next.
- The highest leverage is no longer another profile file; it is a ranked answer to "which saved profile should I use right now, and what exact command should I run?"

Decision:
- Add a first-class managed-profile triage summary that ranks saved profiles by live leverage and emits one exact next command per profile.
- Prefer attach-ready `resume-proof`, then strict `reopen_debug`, then portable fallback reopen, and only fall back to fresh `open_debug` when no saved launch recipe is reusable.

Consequence:
- `glasstty-profile.sh triage --pretty` and `doctor.py` now tell future sessions which isolated profile is the best current lane instead of leaving them to grep multiple profile reports by hand.

## 2026-03-17 — Freeze managed-profile proof into one bundle

Context:
- Chrome's current remote-debugging hardening keeps pushing GlassTTY toward managed non-default profiles as the unit of CDP truth.
- MV3 service workers still terminate on inactivity, and GlassTTY's live-profile state now spans more than one file (`glasstty-profile.json`, `glasstty-native-host.json`, `DevToolsActivePort`, MV3 resume artifacts, doctor/native-host reports).
- Recent revisions made profiles replayable and portable, but the next browser-capable session still had to remember which files to preserve after a live run.

Decision:
- Add a first-class `glasstty-profile.sh capture PROFILE --output-dir ...` lane that writes a durable evidence bundle for one managed profile.
- The bundle should include the current profile summary, a fresh doctor report, browser-aware native-host reports for current/saved/effective browser choices, copied profile-local artifacts, and a concise human-readable `SUMMARY.md`.

Consequence:
- Future live replay or restart-proof runs have an obvious freeze step, and future LLMs inherit a coherent bundle instead of a stale port string plus scattered JSON files.

## 2026-03-17 — Managed profiles should be replayable, not just inspectable

### Decision

GlassTTY should preserve an executable relaunch recipe for each managed Chromium profile and surface it directly through profile reports and doctor hints.

### Why

- Chrome's current remote-debugging rules still make the non-default profile directory the important boundary, so the saved profile recipe is worth reusing verbatim
- rev0097 could say a remembered CDP endpoint was stale, but it still forced the next session to reconstruct Chromium args by hand
- future LLMs need a deterministic relaunch path that reuses the saved browser binary, extension-load choice, start URL, and remote-debugging intent

### Consequence

`scripts/profile_metadata.py` now builds `reopen_plan` / `reopen_debug_plan`, `glasstty-profile.sh` exposes a `reopen` wrapper, and `doctor.py` points stale-profile recovery at a concrete replay command.

## 2026-03-17 — Remembered CDP endpoints must be graded as live or stale

### Decision

GlassTTY should not treat a saved `DevToolsActivePort` file as proof that a profile is still attachable. Managed profile metadata should explicitly say whether the remembered endpoint is currently reachable from localhost and should carry the exact `resume-proof` command to use next.

### Why

- Chrome's March 2025 remote-debugging security change makes non-default user-data-dirs the required unit for modern debugging, so GlassTTY profiles are now the right boundary to preserve and reuse
- a stale `DevToolsActivePort` file is easy to misread as a live browser, which wastes time during LLM handoffs and leads to fake confidence about restart harness readiness
- future sessions need one obvious command to rerun the MV3 worker-resume harness instead of reconstructing it from README fragments

### Consequence

`scripts/profile_metadata.py` now performs a loopback TCP probe for remembered CDP ports, `glasstty-profile.sh` exposes a `resume-proof` wrapper, and `doctor.py` can tell the difference between an attach-ready profile and one that merely remembers old debugging state.

## 2026-03-17 — MV3 restart proof should attach through GlassTTY-managed profiles

### Decision
When operators already launched Chromium through `glasstty-profile.sh`, the MV3 restart harness should attach through that saved profile metadata instead of requiring a manually copied CDP endpoint.

### Why
- current Chrome guidance still recommends isolated custom user-data-dirs for debugging/security-sensitive remote-debugging flows
- GlassTTY already preserves per-profile launch metadata plus `DevToolsActivePort`, so the harness can reuse trustworthy local evidence instead of asking humans to transcribe ports/URLs
- future sessions benefit more from a saved profile-local restart summary than from another transient console instruction

### Consequence
`mv3-worker-resume.py` now accepts `--profile` / `--profile-dir`, `glasstty-profile.sh info` exposes `cdp_endpoint_hint` plus saved MV3 resume artifacts, and restart-proof runs can leave a durable summary directly inside the same profile tree they exercised.

## rev0094 decisions

- Chose a **browser-driven MV3 worker termination harness** as the next highest-leverage step instead of another passive diagnostic field. rev0093 already preserved durable restart history; the bigger gap was that nothing in-tree deliberately forced a restart and compared before/after evidence.
- Kept the harness centered on the extension's own probe page rather than a fixture site dependency. That lowers variability and makes the artifact about worker recovery first, not page-routing noise.
- Used browser-level CDP `Target.closeTarget` against the extension `service_worker` target rather than faking a restart in app code. The point of the lane is to exercise MV3 lifecycle reality, not only GlassTTY's internal reconnect handlers.
- Preserved checkpointed partial-report semantics even for the new harness so a SIGTERM still leaves a meaningful forensic artifact.

## 2026-03-17 — MV3 restart evidence should survive session storage resets

### Decision

Keep fast-changing bridge state in `chrome.storage.session`, but preserve a compact bounded history of worker boots and native-lane events in `chrome.storage.local` so GlassTTY can diagnose restart-driven failures across extension reloads and browser restarts.

### Why

- Chrome's current storage docs still say `storage.session` is cleared when the extension is reloaded, updated, disabled, or when the browser restarts.
- Chrome's MV3 lifecycle and testing guidance still emphasizes resilience to unexpected service-worker termination, and browser-driven suspension tests remain important because DevTools/WebDriver can distort normal worker lifetime behavior.
- rev0092 had strong per-session lane truth, but future sessions could still lose the evidence needed to answer whether the current boot had actually reclaimed the persistent native port.

### Consequence

GlassTTY now keeps a bounded durable history in local storage, derives a compact `runtimeHint`, and surfaces that hint in `bridge.status`, `bridge.probe`, and the side panel. Operators and future LLMs can now distinguish “current boot healthy” from “current boot only has one-shot reachability” and “recent restart churn” without reconstructing that story from transient session state alone.

## 2026-03-17 — Explicit diagnostics should opportunistically reseat the persistent native lane

### Decision

When a user explicitly asks GlassTTY for `bridge.status` or `bridge.probe`, and those diagnostics prove the native host is reachable through one-shot `sendNativeMessage()`, the extension should immediately try to restore the long-lived `connectNative()` lane instead of waiting only for the next reconnect alarm.

### Why

- Chrome's current native-messaging docs still distinguish `connectNative()` as the long-lived host/port lane and `sendNativeMessage()` as a fresh host process per request.
- Chrome's current MV3 lifecycle docs still say service workers should be resilient to unexpected termination, and native-port loss is part of that reality.
- By the time GlassTTY has a successful one-shot diagnostic reply, it has stronger evidence than a timer or stale storage flag that the host manifest is currently reachable.

### Consequence

Explicit diagnostics now serve two purposes: they still report native-lane truth, and they also opportunistically reseat the persistent lane. Bridge state now carries a compact lane diagnosis so future sessions can tell the difference between “one-shot helper reachable” and “persistent bridge actually healthy.”

## 2026-03-17 — Native-host broker ownership must be deferred until message intent is known

### Decision
GlassTTY should not decide broker ownership when the native host process starts. It should decide ownership only after the first browser message is read, and that message should be able to declare whether the process is an owner candidate (`connectNative()` lane) or a secondary one-shot helper (`sendNativeMessage()` lane).

### Why
- Chrome's current native-messaging docs still say `sendNativeMessage()` starts a fresh host process for each request, so treating every new host process like a potential broker owner was over-eager
- rev0090 prevented one-shot helpers from stealing the broker away from an already-live owner, but it still allowed a helper to become a transient owner when no persistent lane had connected yet
- GlassTTY's local broker is part of the long-lived browser↔CLI bridge, not something a one-shot diagnostic should create accidentally

### Consequence
Persistent-port health pings remain owner candidates, one-shot status/probe helpers stay secondary, and broker-server construction is now lazy so secondary helpers can report local state without binding `GLASSTTY_HOME/run/daemon.sock`.

---

## 2026-03-16 — rev0067 package proof should follow JS-discovered asset paths

- Treat `chrome.runtime.getURL(...)` and `new URL(..., import.meta.url)` as package-verification roots, not just implementation details, because built extension pages and workers can depend on assets/modules that are invisible to manifest/HTML/CSS-only graph checks.
- Treat an in-repo package output path as unsafe for direct zipping; always stage the archive outside the repo tree first and move it into place afterward.

## 2026-03-16 — Partial validation evidence is better than an all-or-nothing wrapper

### Decision
When `scripts/validate-release.py` cannot reliably complete in this container, it should still checkpoint partial `report.json` and `SUMMARY.md` artifacts after every completed step instead of waiting until the end of the suite.

### Why
- rev0065 kept leaving future sessions with an empty or misleading validation directory when the wrapper was interrupted mid-run
- the project already values archive truth and handoff quality more than polished but fragile happy-path automation
- partial validation evidence is directly useful to the next LLM or operator even when the wrapper still needs more debugging

### Consequence
rev0066 writes rolling validation artifacts after each finished step and stages the package-check zip outside the repo tree, so interruption no longer erases the proof that did complete.

---

## 2026-03-09 — Coverage experiments should be runnable, not only suggested

### Decision
GlassTTY should support **non-persistent dynamic content-script experiments** through the existing browser↔CLI bridge instead of leaving manifest-variant trials as a purely manual archive instruction.

### Why
- rev0061 could explain which Chrome lever looked promising, but it still forced a human or later LLM to edit the extension package just to try the experiment
- Chrome's dynamic content-script registration API supports runtime declarations with `allFrames`, `matchAboutBlank`, `matchOriginAsFallback`, and `persistAcrossSessions`, which is exactly the right scope for reversible proof work
- future live sessions need effective-policy truth in probe artifacts once an experiment is active

### Consequence
GlassTTY now exposes runtime experiment registration/clear/status lanes, updates `bridge.probe.manifest.contentScriptPolicy` to reflect effective policy rather than only static manifest state, and preserves the active experiment in browser-side diagnostics.

---

## rev0059 — 2026-03-09

- Keep GlassTTY conservative about manifest reach for now. Chrome's docs clearly distinguish `all_frames` and `match_origin_as_fallback`, but this revision stops short of widening policy and instead makes the current gap visible through coverage audits and fixture metadata.
- Treat related-frame URLs (`about:`, `data:`, `blob:`, `filesystem:`) as a first-class diagnostic category. They are operator-actionable in a way that plain `unsupported_url` is not, even before GlassTTY decides whether broader manifest policy is justified.
- Prefer richer browser-side proof artifacts over silent heuristics. `bridge.probe` and `fixture.capture` should preserve frame-coverage explanations so future sessions can compare real browser evidence against any later manifest experiments.

## 2026-03-09 — Resolver audit evidence should surface in browser-side proof artifacts

### Decision
GlassTTY should preserve receiver ranking evidence in `bridge.probe.receiverAudit` and live `fixture.capture` metadata instead of keeping that explanation lane daemon-CLI-only.

### Why
- future live proof bundles are stronger when one artifact already contains both the chosen receiver and the ranking logic behind that choice
- Chrome's frame/document model makes receiver selection a real operational decision rather than incidental UI decoration
- future LLM sessions should not have to reconstruct ranking truth from raw receiver rows when the product already knows that truth

### Consequence
Shared receiver helpers now emit `resolverPolicy`, `receiverResolution`, and `rankedMatches`, and the background threads that evidence into `bridge.probe.receiverAudit` plus live `fixture.capture` metadata.

---

# DECISIONS

## 2026-03-09 — Receiver resolver ranking must be explicit and auditable

### Decision
`glassttyd resolve-receiver` should rank matching receivers deterministically and expose an explanation surface instead of implicitly trusting whatever row order `bridge.status` happened to return.

### Why
- Chrome's instant-navigation model already made receiver identity more nuanced than a single top-frame heuristic
- GlassTTY had accumulated enough receiver metadata that a black-box first-match choice was avoidable
- future live browser debugging will be much easier if resolver outcomes carry their own audit trail

### Consequence
The daemon CLI now sorts matches by lifecycle preference, outermost-ness, readiness, frame depth, and recency, and `--explain` exposes that ranking policy directly in JSON output.

---

## 2026-03-06 — Chromium first, Firefox no longer primary

### Decision
GlassTTY will target Chromium first.

### Why
- better alignment with future automation and extension-testing tooling
- easier long-run path toward headed/headless experimentation
- user accepted the tradeoff

### Consequence
Firefox can remain a secondary compatibility target later, but the repo and tooling will optimize for Chromium now.

---

## 2026-03-06 — Generic product, Claude-first adapter

### Decision
The product identity stays generic. Claude.ai is the first real working adapter, not the whole product.

### Why
- prevents project identity from collapsing into a one-off site hack
- keeps future adapters possible
- improves protocol and code hygiene

### Consequence
Shared protocol names and core docs must avoid Claude-specific naming unless inside adapter folders.

---

## 2026-03-06 — Archive as source of truth

### Decision
The repo archive is the durable memory layer for multi-session LLM work.

### Why
Chat logs are transient and fragmented.

### Consequence
Every meaningful session should leave behind updated repo memory files.

---

## 2026-03-06 — Local broker socket in v0

### Decision
The Python native host will expose a local UNIX-socket broker early rather than waiting for a later transport layer rewrite.

### Why
- it gives the CLI a clean local interface immediately
- it lets browser-originated events be watched from the terminal without scraping logs
- it creates a stable seam for a future Rust rewrite

### Consequence
The daemon now owns both browser-native-messaging framing and a local JSON-over-socket control plane.

---

## 2026-03-06 — Side panel as operator surface

### Decision
Use Chrome's side panel as the main in-browser diagnostics and control surface.

### Why
- it stays open alongside the active page
- it is less cramped than an action popup
- it pairs well with a user-driven browser-open workflow

### Consequence
Bridge state should be mirrored into extension storage so the side panel can survive service-worker restarts gracefully.

---

## 2026-03-06 — Restrict mirrored bridge state to trusted extension contexts

### Decision
Treat mirrored bridge state as extension-internal by default and restrict `storage.local` access to trusted contexts.

### Why
- Chrome exposes `storage.local` to content scripts by default
- GlassTTY's bridge state is more sensitive and operational than ordinary page-facing settings
- the side panel and service worker can still access it without issue

### Consequence
The background should harden storage access on startup/install and avoid assuming content scripts can read mirrored state.

---

## 2026-03-06 — Tab targeting is now part of the product shape

### Decision
GlassTTY should remember recently supported tabs and accept explicit `tab_id` targeting from the terminal and side panel.

### Why
- multiple supported tabs are a normal operator workflow
- side panel usage should not collapse routing back to the currently focused browser tab only
- generic browser-app bridging gets stronger when routing is explicit

### Consequence
Bridge state, CLI commands, and side-panel UX now need to represent target-tab choices clearly.

---

## 2026-03-06 — Prefer session storage for operational bridge state

### Decision
Operational bridge state should live in `chrome.storage.session` by default, not `storage.local`.

### Why
- Chrome recommends `storage.session` as one of the storage areas that works well with service workers
- `storage.session` is in-memory and not persisted to disk
- GlassTTY's mirrored bridge state is operational and transient, not long-lived user preferences

### Consequence
The side panel and service worker should treat session storage as the default shared memory plane, leaving `storage.local` for any future durable settings.

---

## 2026-03-06 — User-driven context menus are part of the operator model

### Decision
GlassTTY should expose a few carefully chosen Chromium context-menu actions.

### Why
- they are explicit user gestures
- they reduce friction when the operator is already in the browser
- Chrome's side-panel APIs can be opened from user interactions such as context menus

### Consequence
The extension now supports lightweight context-menu flows for targeting a tab, opening the side panel, reading state, and writing selected text into the prompt draft.



---

## 2026-03-08 — Keep raw Chromium+CDP as the primary in-container proof lane

### Decision
Use raw Chromium plus DevTools/CDP inspection as the primary in-container proof claim, while treating Playwright-over-CDP as a secondary lab observer.

### Why
- current Chrome and Playwright guidance still points extension automation toward Chromium contexts, so Playwright remains strategically valuable
- in this container, manual raw CDP artifacts already prove the unpacked extension probe page is reachable in `--headless=new` Chromium
- the parallel manual Playwright attach connected successfully but only surfaced `chrome-error://chromewebdata/`, which is weaker than the raw CDP evidence

### Consequence
The archive should preserve both artifact types, but claims of live-browser proof in this environment should be anchored to raw CDP until the Playwright lane is equally trustworthy.


---

## 2026-03-08 — Treat Playwright persistent launch as the right extension-lab shape, but keep fallback proof honest

### Decision
Move GlassTTY’s automation lab toward Playwright persistent-context launch semantics, while still preserving raw Chromium/CDP fallback and refusing to over-claim live-browser success where only diagnostics improved.

### Why
- current Playwright extension guidance is centered on persistent Chromium contexts, not CDP attach after the fact
- Playwright’s own API docs warn that `connect_over_cdp()` is lower fidelity than the Playwright protocol
- in this container, the package is installed but there is no bundled Chromium cache, so launch strategy itself must be diagnosed explicitly

### Consequence
The smoke harness and doctor now surface bundled-vs-system launch strategy directly, and future sessions should prefer persistent launch when the browser environment is actually present.


---

## 2026-03-08 — Chrome for Testing becomes the preferred hermetic lab browser

### Decision
GlassTTY should prefer a locally installed Chrome for Testing bundle for lab/browser-proof work when one is available.

### Why
- current Chrome guidance increasingly points automation users toward Chrome for Testing
- GlassTTY’s proof lane has been too dependent on whichever Chromium happens to be on PATH
- a local CfT cache gives future sessions a stable browser substrate without changing the core product architecture

### Consequence
System Chromium remains a fallback, but doctor output, profile launch, and the smoke lane now surface browser choice explicitly and can prefer a local CfT bundle.


---

## 2026-03-08 — Separate the hermetic raw-browser lane from the Playwright extension lane

### Decision
Use Chrome for Testing (or another resolved raw Chromium-family browser) for the raw browser/CDP lane, but require bundled Playwright Chromium by default for the Playwright persistent extension lane.

### Why
- current Playwright extension docs recommend bundled Chromium for side-loaded extensions
- Chrome for Testing remains valuable for raw automation and remote-debugging flows, but that is not the same thing as the supported Playwright extension path
- treating `/usr/bin/chromium` as the default Playwright browser was producing weaker, more ambiguous failures than an explicit skip

### Consequence
GlassTTY now skips the Playwright persistent lane by default when no bundled Chromium cache is present, and only uses a system-browser fallback when `GLASSTTY_PLAYWRIGHT_ALLOW_SYSTEM_EXECUTABLE=1` is set. This keeps the lab truthful while preserving an escape hatch for experiments.

---

## 2026-03-08 — Treat the offscreen document as a hidden DOM utility, not only a proof flag

### Decision
Keep the MV3 offscreen document, but promote it from passive diagnostics into a small reusable hidden-DOM lane.

### Why
- Chrome's offscreen docs explicitly position offscreen pages as the right place for DOM/window work that cannot live in the service worker
- GlassTTY's last revision could create and enumerate the hidden document, but that still left it as a mostly passive proof surface
- a hidden DOM parser is generic enough for future fixture/headless work without baking Claude-only assumptions into the core extension protocol

### Consequence
GlassTTY now has an active `bridge.offscreen_dom` / `glassttyd offscreen-dom` path, and future sessions should treat the offscreen document as an intentional lab primitive rather than a one-off diagnostics artifact.



---

## 2026-03-08 — Let the offscreen document become a generic hidden fixture parser

### Decision
Keep the offscreen document and extend it from DOM summary work into a generic fixture-like HTML parser that can emit candidate reports and HTML samples.

### Why
- Chrome's offscreen guidance explicitly positions it as the MV3 place for DOM/window work that the service worker cannot do
- GlassTTY already carries fixture capture/index/compare tooling, but it had no browser-native way to turn saved HTML back into a comparable capture shape
- this keeps the core generic: the hidden parser emits heuristic fixture data without baking more Claude-only assumptions into the protocol

### Consequence
GlassTTY now has `bridge.offscreen_fixture` and `glassttyd offscreen-fixture`. Future sessions can compare hidden offscreen fixture captures against visible-tab captures before promoting any heuristic into adapter-specific logic.


## 2026-03-08 — Make hidden offscreen fixtures interaction-aware, not only text-aware

### Decision
Keep the hidden offscreen fixture parser generic, but enrich it with control labels, submit-candidate recovery, form actions, and a compact semantic outline that downstream tools can compare.

### Why
- Chrome's offscreen guidance explicitly positions the hidden document as the DOM-capable MV3 surface for work that cannot stay in the service worker.
- HTML label association and DOM parsing rules are stable enough that GlassTTY can infer more about likely prompt/submit controls without baking Claude-only selectors into the core.
- Comparing fixtures only by selector hints and text length was too lossy for future LLM sessions trying to reason about form drift.

### Consequence
GlassTTY's hidden fixture lane now carries richer interaction semantics, and the archive tooling can compare those semantics directly before anyone promotes a heuristic into adapter-specific code.


---

## 2026-03-08 — Treat hidden offscreen fixtures as accessibility-aware interaction models

### Decision
Keep the hidden offscreen fixture parser generic, but enrich it with accessibility-oriented semantics such as descriptions, fieldset legends, control kinds, and submit-control overrides.

### Why
- current HTML and ARIA docs make those semantics recoverable from saved DOM without adapter-specific selectors
- GlassTTY's archive tooling was already comparing labels and form actions, but that was still too lossy for reasoning about real interaction drift
- these semantics stay generic enough to help both fixture-lab and future Claude/live captures without turning the core into a Claude-only parser

### Consequence
Future sessions should inspect `description_text`, `fieldset_legend`, `control_kind`, and `submit_action` in offscreen fixture captures before adding new selector heuristics or adapter-specific code.


## 2026-03-08 — Expand hidden fixture parsing from text boxes to general form controls

### Decision
Keep the offscreen fixture lane generic, but widen it to model more real form controls and preserve accessible-name plus choice-topology signals.

### Why
- current HTML/ARIA docs make it clear that `<select>` and related choice controls are first-class form inputs, not edge cases
- GlassTTY's earlier hidden parser still biased too heavily toward text boxes, which made saved HTML from settings/profile flows look thinner than it really was
- accessible names and selected choices are closer to how real users and assistive tech understand a control than raw selector hints alone

### Consequence
GlassTTY's hidden fixture captures now preserve `accessible_name`, `form_name`, `option_count`, `option_labels`, and `selected_options`, and the archive tools compare those fields directly before future sessions invent more brittle selectors.


---

## 2026-03-08 — Treat hidden offscreen fixtures as stateful form models, not only structural captures

### Decision
Keep the hidden offscreen fixture parser generic, but enrich it with control-state and constraint-validation metadata such as checked state, disabled/readonly, multi-select state, autocomplete/inputmode hints, and constraint flags.

### Why
- current HTML and ARIA docs make those semantics recoverable from saved DOM without adapter-specific selectors
- GlassTTY's richer label/name/choice capture was still missing whether a control is actually operable, selected, or currently invalid
- archive comparisons become more useful when they can distinguish structural drift from state/constraint drift in the same generic fixture shape

### Consequence
GlassTTY's hidden fixture lane now preserves more of the actual interaction surface of saved forms, and the archive tooling can compare control-state/constraint drift directly before future sessions promote any heuristic into adapter-specific code.


## 2026-03-08 — Treat saved fixtures as interaction plans, not only evidence blobs

### Decision
Keep GlassTTY's richer fixture captures generic, but add a planner that turns them into write/read/submit recommendations with user-facing locator hints.

### Why
- current Playwright docs explicitly recommend prioritizing role locators with accessible names, then label and placeholder locators, which lines up with GlassTTY's user-driven bridge model
- the offscreen fixture lane had become rich enough to describe interaction semantics, but future sessions still had to mentally translate those fields into actions
- a generic planner keeps the core adapter-neutral while making the saved-fixture archive more operational for future LLMs and humans

### Consequence
Future sessions should inspect `plan-fixture` output before adding selector heuristics or adapter-specific action code. Locator drift is now a first-class archive signal alongside label/name/state drift.


## 2026-03-09 — Preserve manifest-policy advice beside receiver gaps

### Decision
Keep GlassTTY's default manifest posture conservative, but make receiver coverage artifacts preserve the Chrome policy levers a gap suggests.

### Why
- Chrome's content-script docs still treat `all_frames`, `match_about_blank`, and `match_origin_as_fallback` as explicit, distinct levers rather than one generic “iframe mode”.
- rev0059 could already tell future sessions that a gap was a `related_frame_url`, but it still left too much operator interpretation work when deciding whether runtime priming should be enough or whether a manifest experiment was the real next step.
- Capturing the current content-script posture beside evidence-backed hints is cheaper and safer than widening manifest scope blind.

### Consequence
`bridge.probe.manifest.contentScriptPolicy`, `receiverAudit.coverageAudit.policyHints`, and fixture metadata now preserve both the current declarative stance and the likely next policy experiments, so future live bundles can compare reality against those hints before changing GlassTTY defaults.

---

## 2026-03-16 — Compare coverage experiments by stable gap shape, not only by counts

### Decision
Treat saved before/after coverage-experiment artifacts as a **shape comparison** problem instead of a pure frame-count or frame-ID comparison.

### Why
- current Chrome instant-navigation guidance says `documentId` identifies a document while `frameId` can persist across navigations, so a real reload can make naive frame-ID diffs misleading
- a post-reload artifact can numerically match the predicted remaining-gap count while still representing a different surviving gap shape
- GlassTTY already saves enough frame status / URL / frame-type evidence to build a useful stable signature without pretending the browser gave us perfectly durable identities

### Consequence
`compare-coverage-experiments.py` now emits stable/coarse signature comparisons and warnings for count-only matches. Future live proof bundles should preserve that comparator JSON beside the raw probes before anyone argues for widening manifest policy.

---

## 2026-03-16 — Release verification should check archive self-consistency, not only file presence

### Decision
Make package verification inspect manifest-referenced assets and HTML entrypoint module references in addition to a small required-file allowlist.

### Why
- a package can contain the “important” files yet still be self-inconsistent if a manifest or HTML entrypoint references a missing built asset
- GlassTTY's MV3 workflow depends on built bundles such as `extension/dist/options/main.js`, not only on the existence of the surrounding folders

### Consequence
`verify-package.py` now parses `extension/manifest.json` and the entrypoint HTML files during archive verification. Future release readiness claims can rely on a stronger self-consistency check than rev0063 had.

## 2026-03-19 — Support records are canonical support truth artifacts

Context:
- The project now speaks about support at the level of surface × workflow × browser lane.
- Without a canonical record, those claims would keep dissolving into scattered notes, handoffs, and memory.
- Future implementers need a stable place to record support tiers, caveats, evidence posture, and promotion requirements.

Decision:
- Treat `docs/support-records/*.md` as the living per-surface support truth artifacts.
- Treat the support matrix as a roll-up view, not the primary source of truth.

Consequence:
- When implementation or evidence changes support posture, the support record should change with it.
- Broad “surface supported” language should be replaced by lane- and workflow-scoped record updates.

## 2026-03-19 — Canonical keys should be stabilized before feature expansion accelerates

Context:
- rev0121 defined the broad product model, but future docs and implementation could still drift semantically if every session used slightly different names for the same workflows, tiers, or artifact kinds.
- Multi-surface support, drift reporting, and agent execution all become harder to compare when vocabulary is unstable.

Decision:
- Maintain a single canonical key registry in `docs/canon-keys.md` for the main shared nouns of the system.
- Add new shared keys deliberately there before using them widely in docs, support records, or future schemas.

Consequence:
- The repo gains a more durable shared language for support truth, state contracts, evidence, and agent policy.
- Future implementers can compare records and outputs across surfaces with less translation overhead.

## 2026-03-21 — Turn the locked second adapter into an execution brief

Context:
- rev0133 locked ChatGPT as the second adapter, but the repo still left too much tactical judgment around how the first proof should be executed.
- OpenAI's current first-party help surfaces now give stronger anchors for the plain ChatGPT browser route and for richer branches like Canvas, file uploads, and Projects.
- Without an execution brief, future sessions could still jump straight into richer modes and burn time proving the wrong slice first.

Decision:
- Add `SECOND-ADAPTER-BRIEF.json` and `scripts/second-adapter-brief.py` as the machine-readable plan for the locked second adapter.
- Make the plain ChatGPT browser chat lane the explicit first baseline, and treat Projects, GPT builder, Canvas, and other richer modes as follow-on branches.
- Seed a first `adapters/chatgpt/` scaffold so route/selector notes live beside the future adapter instead of only inside prose docs.

Consequence:
- Future sessions inherit an ordered plan with source anchors, phase goals, artifact targets, selector principles, and promotion criteria instead of reopening tactical planning from scratch.

## 2026-03-21 — Lock ChatGPT as the second adapter

Context:
- The repo already had a narrative decision frame and a seeded ChatGPT support record, but the choice still lived more as recommendation than as a locked operational decision.
- Current official browser/product surfaces still make ChatGPT the closest broad browser-native chat lane to the current Claude reference adapter, while AI Studio is more developer/workspace-shaped and Kimi/Grok/Z.ai look either richer or riskier for the very next proof.
- The source-freshness lane is now strong enough to demand that next-adapter selection stay tied to current first-party product surfaces, not stale assumptions.

Decision:
- Lock ChatGPT as the second adapter.
- Use `SECOND-ADAPTER-MATRIX.json` and `python scripts/second-adapter-report.py --pretty` as the repeatable artifact that explains that choice.
- Treat Google AI Studio as the next-wave follow-on once the ChatGPT second-adapter proof lands.

Consequence:
- Future sessions should spend effort on a real ChatGPT baseline and support bundle rather than reopening the adapter-selection debate unless fresher evidence materially changes the tradeoffs.
- The first desired proof slice is `surface-detect` + `receiver-resolve` + `composer-read` + `composer-write` + `turn-submit` + `latest-turn-read` on `chromium-live`.

