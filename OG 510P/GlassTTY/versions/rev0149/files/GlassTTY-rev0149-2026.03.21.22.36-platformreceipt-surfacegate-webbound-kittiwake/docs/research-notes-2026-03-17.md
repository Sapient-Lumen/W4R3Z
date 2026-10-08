## rev0107 research addendum

- Chrome's March 2025 remote-debugging hardening still says `--remote-debugging-port` / `--remote-debugging-pipe` only work with a non-default `--user-data-dir`, which keeps GlassTTY centered on isolated managed-profile state rather than remembered ports.
- Playwright's current extension docs still say extension work belongs in a persistent Chromium context and that Chrome/Edge removed the old side-load flags, so the durable value is in preserved run artifacts and reproducible profile state, not one-off browser launches.
- Playwright's trace-viewer guidance still treats saved traces as the right post-run debugging primitive, and Chrome DevTools' current trace-sharing work also emphasizes preserving extra data for your future self or a colleague. That combination argues for one higher-level support bundle that copies the latest evidence neighbors instead of leaving them implicit.

## rev0105 research addendum

- Current pytest documentation still recommends faulthandler timeout dumps for long or stuck tests and still exposes duration profiling for the slowest tests. That lines up directly with GlassTTY's remaining wrapper-forensics problem: the most leveraged next step is richer validation-step evidence, not another speculative runtime path.
- Chrome's current remote-debugging hardening and Playwright's persistent-context extension guidance still keep GlassTTY centered on durable profile/browser evidence. That made the complementary missing piece a durable validation wrapper capture lane, so future sessions can compare browser-proof state *and* wrapper state instead of freezing only one side of the project.

## rev0103 research addendum

- Chrome's current remote-debugging hardening still makes the non-default `--user-data-dir` the durable debugging boundary, which means GlassTTY should preserve evidence at the managed-profile and fleet-of-profiles level rather than around ephemeral CDP ports alone.
- Playwright's current extension docs still anchor extension work in persistent Chromium contexts, which reinforces the idea that GlassTTY's best operator memory is not a one-off launch command but a durable snapshot of the current managed-profile fleet.
- Chrome's MV3/native-messaging lifecycle still rewards reconnect-ready, explicit evidence capture; the missing piece after rev0102 was not another profile command but a fleet-level ledger that can say how the ranked next-step surface changed between sessions.

## rev0096 research note — managed profiles should be the attach surface

- Chrome's March 2025 remote-debugging security change still recommends a custom user-data-dir for debugging and automation isolation, which matches GlassTTY's multi-profile direction better than ad hoc CDP URLs.
- Playwright's current `connectOverCDP` docs still describe CDP attach as a lower-fidelity but supported way to connect to an existing Chromium instance; that makes it a good pragmatic recovery lane when fresh browser startup is the unstable part.
- Chrome's service-worker termination guidance still emphasizes persisting important state and explicitly testing termination, so attaching the restart harness to a GlassTTY-managed profile should preserve both the run target and the evidence in one place.

## rev0084 research note — registry visibility was not enough; cache survival needed the marker too

- Playwright's current browser docs still make `install --list`, stale-browser removal, and `PLAYWRIGHT_SKIP_BROWSER_GC=1` first-class lifecycle features. That means GlassTTY should model not just whether a browser is visible to Playwright, but whether it will survive the next real install run. citeturn402796search0
- Inspecting the installed Playwright 1.58 source in this container showed why rev0083 was still incomplete: `_deleteStaleBrowsers(...)` only keeps referenced browser directories when the expected marker file exists, and that marker is `INSTALLATION_COMPLETE` inside the browser directory.
- Local temp-root validation matched that model. A GlassTTY-imported `chromium-1208` without the marker was deleted by a later raw `python -m playwright install chromium`; once the marker was restored, the same imported browser survived and still appeared in `python -m playwright install --list`, even though the install later failed here on FFmpeg DNS.
- Product consequence for rev0084: treat missing `INSTALLATION_COMPLETE` as a first-class cache-health problem, restore it on import/skip paths automatically, expose it in audit/doctor output, and add an explicit repair action for already-imported caches.


## rev0085 research addendum

- Current Playwright browser docs still make `install --list` and stale-browser GC the canonical browser-cache surfaces, so GlassTTY should not blur the difference between a raw cache root and one it has already prepared for the current package.
- In this environment, local source inspection plus temp-root proofs showed that a cache can look healthy after GlassTTY writes the current `.links` entry even though the browser was actually being retained only by some other Playwright client. That made raw-vs-prepared cache truth the highest-leverage next fix.


## rev0086 research addendum

- Chrome's current native-messaging docs still cap a single native-host message to the browser at 1 MB, while messages from the extension to the native host can be much larger. That asymmetry makes large GlassTTY fixture/diagnostic payloads a host-side resilience problem, not only an offline budgeting problem.
- GlassTTY already had offline budget tooling, but the runtime native host would still raise if a broker/browser event crossed the host→extension ceiling. The better product move is to preserve the full payload on disk and return a compact structured failure to the browser so the operator still learns what happened.
- Product consequence for rev0086: native-host outbound overflow now becomes a recoverable, inspectable artifact path instead of an abrupt bridge failure.


## rev0087 research addendum

- Chrome's current native-messaging docs still make the 1 MB host→browser limit a hard protocol fact, which means any operator surface for oversized messages should stay compact by default instead of re-printing the preserved oversized payload.
- That made a local report lane (`overflow-report`) more useful than only exposing the raw spill artifact path: it turns a crash-prevention mechanism into something a human or future LLM can inspect safely during a handoff.
- Product consequence for rev0087: preserve a compact first-class overflow summary through the CLI, doctor/native-host report, and extension bridge state rather than leaving the spill artifact discoverable only through raw state files.

- Chrome's current native-messaging docs still say `connectNative()` keeps the host process alive until the port is destroyed and still cap host→browser messages at 1 MB; that combination makes overflow spill artifacts a maintenance concern during long-lived sessions, not just a one-shot crash fallback.
- Playwright's current browser docs still frame browser binaries as managed cache state with stale-browser GC, `install --list`, and explicit uninstall flows; that reinforced the same operator pattern for GlassTTY overflow artifacts: inventory first, then deliberate pruning instead of silent buildup.
- Chrome's current runtime/native-messaging docs still distinguish `connectNative()` as the long-lived port and `sendNativeMessage()` as the one-request/one-response lane; that makes one-shot native status capture a good diagnostic supplement when GlassTTY wants browser-visible local state without disturbing the steady-state bridge.
- Product consequence for rev0089: keep the main bridge on `connectNative()`, but let `bridge.status` / `bridge.probe` attach a compact one-shot native-host snapshot (including overflow inventory counts and recent artifact summaries) so side-panel/probe diagnostics can see local spill state without retransmitting full saved artifacts.



## rev0090 research addendum

- Chrome's current native-messaging docs still say `runtime.connectNative()` keeps the native host process alive for the life of the port, while `runtime.sendNativeMessage()` starts a new native host process for each request and only the first host reply is delivered. That means GlassTTY cannot safely assume a browser-visible one-shot status snapshot is talking to the same host instance as the steady-state broker bridge.
- Product consequence for rev0090: the broker socket now has an explicit owner lease, one-shot helper host processes identify themselves as `secondary`, and the extension compares one-shot host identity against the persistent-port host identity instead of silently conflating the two lanes.


## rev0091 research addendum

- Chrome's current native-messaging docs still say `runtime.connectNative()` keeps a host alive for the life of the port, while `runtime.sendNativeMessage()` starts a fresh host process for each request and only returns the first reply. That means rev0090's lease was necessary but not sufficient: a one-shot helper that launched before the persistent lane could still become a misleading transient broker owner.
- Chrome's current service-worker lifecycle docs still emphasize 30-second idle shutdowns and resilience to worker restarts, which makes a truthful secondary-only diagnostic lane more useful than trying to recreate the steady-state broker opportunistically from every one-shot helper.
- Product consequence for rev0091: decide broker ownership only after reading the first browser message, let that message declare ownership intent, and keep one-shot status/probe helpers secondary so diagnostics report local truth without mutating the long-lived browser↔CLI control plane.


## rev0092 research addendum

- Chrome's current native-messaging docs still say `runtime.connectNative()` keeps the native host alive for the life of the port, while `runtime.sendNativeMessage()` starts a new host process per request and only uses the first reply. That means a successful one-shot diagnostic is strong evidence that the host manifest is reachable *now*, even if GlassTTY's persistent lane has gone stale.
- Chrome's current service-worker lifecycle docs still say MV3 workers should be resilient to unexpected termination, and they specifically call out reconnecting native messaging from `onDisconnect`. That makes explicit operator diagnostics a good place to do one more opportunistic reconnect instead of waiting only for alarm/backoff recovery.
- Product consequence for rev0092: keep one-shot diagnostics truthful, but let them immediately reseat the persistent lane when they succeed, and summarize the resulting lane state in a compact diagnosis field rather than forcing future sessions to reconstruct it from raw timestamps and error strings.


## rev0093 research addendum

- Chrome's current storage docs still say `chrome.storage.session` is only in-memory while the extension is loaded and is cleared when the extension is disabled, reloaded, updated, or when the browser restarts. That means GlassTTY should not treat session storage as durable evidence for MV3 restart debugging.
- Chrome's current service-worker lifecycle docs still emphasize persisting important state instead of relying on globals and explicitly note that native-messaging reconnect belongs in `onDisconnect`.
- Chrome's current MV3 testing guidance also now has an explicit Puppeteer guide for service-worker termination, while the eyeo suspension write-up still warns that DevTools/ChromeDriver can distort normal worker lifetime behavior.
- Product consequence for rev0093: keep hot bridge state in `storage.session`, but preserve a small bounded cross-restart ledger in `storage.local` and make the next serious live-proof push a browser-driven worker-suspension harness rather than another inference-only session.


## rev0097 research addendum

- Chrome's current remote-debugging security update says that from Chrome 136 onward, `--remote-debugging-port` and `--remote-debugging-pipe` are ignored for the default Chrome data directory and must be paired with a non-standard `--user-data-dir`. That reinforces GlassTTY's decision to treat managed profiles as the debugging unit instead of passing raw endpoints around by hand.
- Playwright's current Chrome-extension docs still say extensions only work in Chromium persistent contexts and warn that Google Chrome and Microsoft Edge removed the side-load flags those flows used to depend on. That makes profile-native, Chromium-first restart proof more valuable than another generic system-browser hint.
- Product consequence for rev0097: remember the profile boundary, but also grade whether its CDP endpoint is currently alive and emit the exact `resume-proof` command that reuses it.


## rev0098 research addendum

- Chrome's March 2025 remote-debugging hardening still says debugging switches must be paired with a non-default user-data-dir, which means the saved GlassTTY profile recipe is the right thing to replay instead of asking humans or future LLMs to retype Chromium flags from memory.
- Playwright's current Chrome-extension guidance still pushes extension work into Chromium persistent contexts rather than ad hoc Chrome launches, which makes a profile replay lane more valuable than a one-off stale-port warning.
- Product consequence for rev0098: keep attach-ready detection, but also surface an executable relaunch recipe that can reopen the same managed profile with fresh remote debugging when the remembered endpoint has gone stale.

## rev0099 research addendum

- Chrome's March 2025 remote-debugging hardening still ties `--remote-debugging-port` to a non-default user-data-dir, which means GlassTTY should keep treating the managed profile recipe as the unit of reuse instead of only remembering a stale port string. citeturn876755search0
- Playwright's current Chrome-extension guidance still says extension work belongs in Chromium persistent contexts and warns that Chrome/Edge removed the sideload flags, which reinforces the idea that saved profile recipes are worth preserving even when the original browser binary has moved. citeturn876755search1turn876755search4
- Chrome's native-messaging docs still make the host manifest browser-specific through explicit `allowed_origins` and platform-specific install locations, so a 'portable reopen' should stay explicit and should surface the native-host follow-up for the saved browser family instead of silently pretending every Chromium-family browser is interchangeable. citeturn993815search1turn993815search11
- Product consequence for rev0099: GlassTTY now distinguishes strict reopen from explicit discovered-browser fallback, records browser-family metadata in profile launch state, and lets `doctor.py` explain when a profile recipe failed because the original browser path disappeared rather than because MV3/native messaging regressed.


## rev0100 research addendum

- Chrome's current MV3 lifecycle docs still say extension service workers can terminate after roughly 30 seconds of inactivity and that important state should be persisted rather than assumed to live in globals.
- Chrome's current native-messaging docs still distinguish long-lived `connectNative()` from one-shot `sendNativeMessage()` and keep browser authorization in the manifest via explicit extension origins.
- Product consequence for rev0100: after any real replay or restart-proof run, GlassTTY should freeze the managed-profile state into one durable evidence bundle (`profile-info`, doctor report, browser-aware native-host reports, and copied profile-local artifacts) so future sessions inherit proof instead of a stale port string plus scattered files.

## rev0101 capture-ledger notes

- Chrome's remote-debugging hardening still ties trustworthy CDP reuse to a non-default `--user-data-dir`, so GlassTTY's managed profile remains the right unit of continuity rather than a remembered host:port.
- The extension service-worker lifecycle docs still say `connectNative()` can keep the worker alive while the native port is open and recommend reconnecting on disconnect, which makes cross-run evidence comparison more valuable than a single-point snapshot when a worker or host disappears between sessions.
- Playwright still frames extension work around Chromium persistent contexts, which again points at accumulating evidence per profile directory instead of treating each validation folder as isolated trivia.
- That combination made the next leverage point clear: rev0101 adds a profile-local capture ledger plus current-vs-previous capture diffs so future sessions can compare managed-profile proof drift directly.


## rev0104 smoke-capture addendum

- Chrome's current remote-debugging hardening still makes the non-default profile directory the durable debugging boundary, so a browser-proof handoff should preserve the run bundle around that boundary instead of treating one live `e2e-fixturelab.json` file as enough.
- Playwright's extension docs still push work into Chromium persistent contexts, and Trace Viewer is explicitly aimed at post-run debugging, which makes saved trace/report/screenshot bundles more valuable than another one-shot smoke verdict.
- Chrome's MV3 lifecycle docs still emphasize reconnect resilience around `connectNative()`, so comparing one smoke run against the previous one is more informative than a single isolated failure when the worker or host disappears.
- Product consequence for rev0104: GlassTTY now has a durable fixture-lab smoke capture ledger with current-vs-previous diffs and doctor hints that point at the exact freeze/history commands.

## 2026-03-18 readiness-board note

- Chrome's 2025 remote-debugging hardening still makes the isolated profile directory the durable debugging boundary, not a remembered port.
- Playwright still frames extension work around persistent Chromium contexts, and Chrome native messaging still requires explicit `allowed_origins` plus reconnect-aware service-worker handling.
- That combination argues for a condensed operator summary over more one-off browser commands: the durable unit is now the collected evidence around a profile/fleet/run, so GlassTTY benefits from a single next-action board that reconciles those ledgers before another live attempt.

## 2026-03-18 operator-attempt note

- Chrome's current remote-debugging hardening still makes the managed profile directory the durable debugging boundary, not a remembered port.
- Playwright Trace Viewer is explicitly about understanding traces *after* a run, which keeps reinforcing the same product lesson for GlassTTY: preserve the attempted run as an artifact, not just the latest ambient state.
- That combination argues for a paired before/after attempt wrapper over another one-off launcher tweak. Product consequence for rev0108: GlassTTY now has a durable operator-attempt bundle and root ledger so one real validation/profile/browser attempt can be frozen, compared, and handed off directly.
