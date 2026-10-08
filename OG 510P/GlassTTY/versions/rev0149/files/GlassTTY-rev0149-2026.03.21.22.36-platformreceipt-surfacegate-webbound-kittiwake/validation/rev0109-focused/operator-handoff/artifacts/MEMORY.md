## rev0109 memory

- The newest audited baseline before this revision was `GlassTTY-rev0108-2026.03.18.01.44-attemptledger-prepost-livewrap-redshank.zip`, unpacked here as `GlassTTY-rev0108-2026.03.18.01.44-attemptledger-prepost-livewrap-redshank`.
- Current official browser guidance still points GlassTTY toward isolated Chromium profiles, persistent Chromium extension contexts, and explicit native-host/browser identity rather than magical generic browser launches. The most useful new lesson for this session was that our remaining pain is *interrupted browser startup archaeology*, not lack of another launcher knob.
- rev0109 therefore makes the browser-launch phase itself durable evidence: `scripts/e2e-fixturelab.py` now preserves `browser_attempt_inflight` and finalizes interrupted launches into `browser_attempts[]`, while `scripts/e2e-fixturelab-capture.py` surfaces interruption counts and last-attempted modes in smoke-history summaries.
- Honest proof remained partial. The pre-fix live attempt was terminated during browser launch. The first post-fix rerun reset the container runtime during that same phase, so there is still no fresh trustworthy browser/native round-trip proof in this environment.
- Future sessions should treat `validation/rev0109-focused/`, `docs/handoff-rev0109-2026-03-18.md`, and the new research note as the shortest path back into this revision.

## rev0108 memory

- The highest-leverage next move was to make a *single attempted run* a first-class evidence unit. GlassTTY already preserved current state well, but future sessions still had to infer which command somebody actually tried and compare separate captures by hand.
- `scripts/operator_attempt.py` now wraps one run in paired before/after snapshots: `doctor`, `readiness`, `operator_handoff` artifact inventory, tracked next-action summary, `attempt-diff.json`, `history-diff.json`, and the root ledger `validation/operator-attempts.json`.
- `scripts/doctor.py` now exposes `operator_attempt.commands`, the current in-progress attempt summary, and the finished-attempt history so the next session can either finish the open bundle or start a new one deliberately.
- Focused proof for this revision should preserve the new operator-attempt unit tests, nearby operator-handoff/readiness regressions, extension typecheck/build, package verification, archive audit, and a deterministic sample operator-attempt bundle under `validation/rev0108-focused/`.

## rev0107 memory

- The newest audited baseline before this revision was `GlassTTY-rev0106-2026.03.18.00.55-readinessboard-nextaction-evidencehub-lapwing.zip`.
- The highest-leverage next move was not another browser/profile subcommand but a **durable operator handoff bundle**. GlassTTY already knew how to rank next actions, but future sessions still had to decide which ledgers, docs, and latest bundles to gather before they could reason.
- `scripts/operator_handoff.py` now freezes the current doctor/readiness surface, linked validation/smoke/profile/readiness artifacts, and core archive-memory docs into one support pack backed by `validation/operator-handoff-captures.json`.
- Focused proof for this revision should preserve the new operator-handoff unit tests, nearby doctor/readiness regressions, extension typecheck/build, package verification, archive audit, and a deterministic sample operator-handoff bundle under `validation/rev0107-focused/`.

## rev0106 memory

- The newest audited baseline before this revision was `GlassTTY-rev0105-2026.03.18.00.19-validatecapture-resumediagnostics-wrapperledger-guillemot.zip`.
- The highest-leverage next move was not another profile/browser command but a **condensed readiness board**. GlassTTY had durable ledgers for profiles, fleets, smoke, and validate-release, but future sessions still had to manually reconcile them into a next step.
- `scripts/readiness_report.py` now distills that state into one prioritized action list, exposes `python scripts/readiness-report.py --pretty`, and can freeze the board plus the underlying doctor report into `validation/readiness-report-captures.json`.
- Focused proof for this revision should preserve the new readiness-report unit tests, one nearby validate-release/doctor regression, extension typecheck/build, package verification, archive audit, and a deterministic sample readiness-capture bundle under `validation/rev0106-focused/`.

# rev0105 memory

- New validation handoff primitive: `python scripts/validate-release-capture.py --source-dir validation/latest --output-dir validation/latest/validate-release-capture`
- Root validation ledger: `validation/validate-release-captures.json`
- Validate-release bundles now preserve `report.json`, saved `steps/` logs, `current_step.json`, `bundle-summary.json`, `capture-history.json`, `capture-diff.json`, and a resume/focus command summary.
- `scripts/validate-release.py` now adds pytest `faulthandler_timeout` and `--durations` diagnostics by default for its pytest steps.
- Doctor now exposes `validation.latest_report`, `validation.capture_history`, and exact resume/capture/history commands for the umbrella validation lane.

# rev0104 memory

- New browser-proof handoff primitive: `python scripts/e2e-fixturelab-capture.py --report validation/latest/e2e-fixturelab.json --output-dir validation/latest/e2e-fixturelab-capture`
- Root smoke ledger: `validation/e2e-fixturelab-captures.json`
- Bundle contents: raw report, copied trace/screenshot siblings when present, `smoke-summary.json`, `smoke-history.json`, `smoke-diff.json`, `SUMMARY.md`
- Doctor now exposes `fixture_lab.latest_smoke_report`, `fixture_lab.smoke_capture_history`, and exact capture/history commands.

## rev0103 memory

- Newest audited baseline before this revision: `GlassTTY-rev0102-2026.03.17.23.11-profiletriage-bestnext-fleetlane-whimbrel.zip`.
- Online guidance still points at the same durable boundary: Chrome 136+ wants a non-default `--user-data-dir` for remote debugging, Playwright extension work still lives in persistent Chromium contexts, and MV3/native-messaging recovery remains easiest to reason about per managed profile.
- GlassTTY now exposes `./scripts/glasstty-profile.sh fleet-capture --output-dir ...` and `./scripts/glasstty-profile.sh fleet-captures --pretty`, which preserve the current triage/doctor/profile surface in a root-level ledger instead of leaving fleet drift as a conversational reconstruction.
- Focused proof for this revision lives under `validation/rev0103-focused/` (py_compile, bash -n, fleet-capture + triage/doctor pytest logs, extension typecheck/build, package verification, archive audit).
- Honest gap remains: no fresh live browser/native-messaging restart-proof run completed in this container.

## rev0102 memory

- Newest audited baseline before this revision: `GlassTTY-rev0101-2026.03.17.22.07-captureledger-proofdiff-historylane-shelduck.zip`.
- Online guidance still points at the same boundary: Chrome 136+ wants a non-default `--user-data-dir` for remote debugging, Playwright extension work still lives in persistent Chromium contexts, and MV3/native-messaging recovery remains easiest to reason about per managed profile.
- GlassTTY now exposes a fleet-level `triage` summary that ranks saved profiles by leverage and emits the exact next command (`resume-proof`, `reopen_debug`, or portable fallback reopen) instead of making future sessions inspect every profile manually.
- Focused proof for this revision lives under `validation/rev0102-focused/` (py_compile, bash -n, triage/profile pytest logs, extension typecheck/build, package verification, archive audit).
- Honest gap remains: no fresh live browser/native-messaging restart-proof run completed in this container.

## rev0101 memory

- Newest audited baseline before this revision: `GlassTTY-rev0100-2026.03.17.21.32-profilecapture-proofbundle-handofflane-sanderling.zip`.
- Online guidance still points the same way: Chrome 136+ remote debugging requires a non-default `--user-data-dir`, Playwright extension work still lives in persistent Chromium contexts, and MV3/native-messaging behavior is easiest to understand when evidence stays attached to one managed profile instead of a remembered port string.
- GlassTTY now keeps a profile-local `glasstty-profile-captures.json` ledger, exposes it through `glasstty-profile.sh captures`, and writes `capture-history.json` plus `capture-diff.json` into each durable bundle so future sessions can compare one managed-profile proof against the previous one.

## rev0100 memory

- newest audited baseline before this revision: `GlassTTY-rev0099-2026.03.17.20.59-profileportable-browserfallback-nativehosttruth-merlin.zip`
- managed profiles now expose `commands.capture`, and `./scripts/glasstty-profile.sh capture PROFILE --output-dir ...` writes one durable evidence bundle around the current profile state
- the capture bundle freezes `profile-info.json`, `doctor.json`, browser-aware native-host reports, `SUMMARY.md`, and copied profile-local artifacts (`glasstty-profile.json`, `glasstty-native-host.json`, `DevToolsActivePort`, MV3 resume report/summary)
- doctor attach-ready and saved-resume hints now point at the capture command so future live runs can be preserved deliberately instead of reconstructed from scattered files
- focused proof for this revision should live under `validation/rev0100-focused/` (py_compile, bash -n, targeted profile/doctor pytest, extension typecheck/build, package zip + verify-package + archive-audit)
- honest gap remains: no fresh live browser/native-messaging restart-proof run completed in this container

## rev0099 memory

- newest audited baseline before this revision: `GlassTTY-rev0098-2026.03.17.20.49-profilereplay-reopenproof-relaunchlane-kestrel.zip`
- managed profiles now preserve browser-family metadata and expose two replay modes: strict reopen with the saved browser path, and explicit discovered-browser fallback when that saved path no longer exists on the current machine
- `doctor.py` now distinguishes 'stale CDP endpoint' from 'saved browser path missing' so future sessions do not waste time blaming MV3/native messaging for a moved browser binary
- focused proof for this revision should live under `validation/rev0099-focused/` (py_compile, bash -n, targeted profile/doctor pytest, extension typecheck/build, package zip + verify-package + archive-audit)
- honest gap remains: no fresh live browser/native-messaging restart-proof run completed in this container

## rev0098 memory

- newest confirmed starting point for this session was the uploaded archive/folder `GlassTTY-rev0097-2026.03.17.20.21-profiledoctor-attachready-resumecommand-linnet.zip` / `GlassTTY-rev0097-2026.03.17.20.21-profiledoctor-attachready-resumecommand-linnet/`
- managed profiles now expose executable `reopen_plan` / `reopen_debug_plan` metadata plus `commands.reopen` / `commands.reopen_debug`, not just remembered CDP state
- `./scripts/glasstty-profile.sh reopen PROFILE ...` is now the preferred way to replay a known-good managed profile recipe, optionally forcing `--remote-debugging-port auto` for a fresh attach-ready run
- doctor stale-profile hints now point at replay commands grounded in saved metadata instead of telling future sessions to rebuild launch args from memory
- still unproven here: one fresh live browser restart-proof run against an actually running GlassTTY profile in this container

## rev0097 memory

- newest confirmed starting point for this session was the uploaded archive `GlassTTY-rev0096-2026.03.17.18.38-profileattach-managedproof-resumeledger-bobolink.zip`
- managed profiles now expose `commands.resume_proof`, `commands.resume_proof_direct`, loopback `tcp_probe` attachability, and `attach_warning` when `DevToolsActivePort` looks stale
- `./scripts/glasstty-profile.sh resume-proof PROFILE ...` is now the preferred way to run a profile-native MV3 restart proof because it preserves the exact same profile boundary Chrome now expects for remote debugging
- doctor hints now call out one attach-ready profile and one saved MV3 resume summary when present, which should reduce future handoff archaeology
- still unproven here: one fresh live browser restart-proof run against an actually running GlassTTY profile in this container

## rev0096 memory

- The newest archive actually available in this container when this session resumed was `GlassTTY-rev0094-2026.03.17.17.35-mv3resume-cdpkill-prooflane-spoonbill.zip`. Earlier chat referenced rev0095, but that artifact/worktree was not present after the sandbox reset, so this revision was rebuilt honestly from rev0094 on disk.
- Current Chrome guidance still ties secure/debuggable remote debugging to **non-default user-data-dirs**, while Playwright's current CDP docs still allow attaching to an existing Chromium instance with lower fidelity than the full Playwright protocol. That combination made GlassTTY-managed profile attach the next best leverage point.
- `scripts/profile_metadata.py` now derives a `cdp_endpoint_hint` from profile metadata + `DevToolsActivePort`, preserves profile-local MV3 resume reports/summaries, and surfaces those through `glasstty-profile.sh info`.
- `scripts/mv3-worker-resume.py` now supports `--profile` / `--profile-dir` attach flows, skips native-host install in attach mode, and writes profile-scoped restart proof artifacts when a profile was the source of truth.
- `worker_resume_summary(...)` now distinguishes strict context-aware recovery from legacy boot/native-only recovery so future sessions can tell whether restart proof included extension-context evidence.

## rev0094 memory

- The newest audited baseline before this revision was `GlassTTY-rev0093-2026.03.17.16.55-localhistory-resumetruth-workerledger-whimbrel.zip`.
- Chrome's current MV3 lifecycle/testing guidance kept pointing at the same missing proof: GlassTTY had durable restart history, but it still lacked a first-class harness that deliberately kills the service worker and captures whether the next probe recovered the persistent native lane.
- `scripts/mv3-worker-resume.py` now stages that proof lane around the extension probe page itself: build extension, install native host, launch persistent Playwright Chromium, capture a before snapshot, terminate the extension worker via browser CDP, rerun the probe, and compute a compact `resume_proof` summary.
- `scripts/e2e-fixturelab.py` now exposes reusable helpers for probe-page-only opening, worker termination, and shared persistent-context launch so future browser labs do not have to duplicate MV3 orchestration.
- Honest gap remains: this container still did not complete a full live before/after resume proof. The best real run got through extension build plus native-host install and was then terminated by signal 15 before Playwright finished the browser phase.

## rev0093 memory

- The newest audited baseline before this revision was `GlassTTY-rev0092-2026.03.17.16.35-nativelane-selfheal-probetruth-avocet.zip`.
- Chrome's current storage docs still say `chrome.storage.session` is in-memory only and is cleared when the extension is reloaded, updated, disabled, or when the browser restarts. That meant rev0092's native-lane truth was useful within one loaded extension session but easy to lose across exactly the MV3 restart boundaries we most care about.
- GlassTTY now keeps a bounded durable history under `chrome.storage.local` (`bridgePersistentHistory`) with worker boots plus native-lane events (`native.connected`, `native.disconnected`, `native.reconnect_*`, `native.opportunistic_reconnect`, `native.oneshot_reachable`).
- `extension/src/shared/persistent-history.ts` derives a compact `runtimeHint` so future sessions can quickly see whether the current worker boot has already reclaimed the persistent port, has only one-shot reachability proof, is still pending after a previous healthy boot, or is showing restart churn.
- The side panel now renders both the structured durable diagnostics and the raw mirrored local-history blob, and the probe page includes the durable runtime hint in native-health failure output.
- Honest gap remains unchanged: no fresh live Chromium/native-host/browser round-trip was proven in this container.

## rev0092 memory

- The newest audited baseline before this revision was `GlassTTY-rev0091-2026.03.17.16.25-deferredintent-secondarytruth-lazybroker-tern.zip`.
- Chrome's current docs still keep `connectNative()` and `sendNativeMessage()` sharply separate, and the service-worker lifecycle docs still say MV3 workers should be resilient to unexpected termination. That suggested a higher-leverage next move than yet another passive status field: use successful one-shot diagnostics as evidence that the native host is reachable now, then immediately try to reseat the long-lived port while the operator is already asking for status/probe truth.
- `extension/src/background/main.ts` now opportunistically calls back into `connectNative()` during explicit `bridge.status` / `bridge.probe` requests after a successful one-shot native check, instead of waiting only for the background reconnect alarm.
- `extension/src/shared/native-lane.ts` now derives a compact `laneDiagnosis` state (`persistent_healthy`, `persistent_degraded`, `oneshot_only`, `reconnect_pending`, `native_host_unreachable`, `unknown`) so future sessions can tell whether GlassTTY merely has local manifest reachability or a truly healthy persistent bridge.
- Honest gap remains: this revision still does **not** prove a fresh live Chromium/native-host/browser round-trip in this container; the new behavior is validated here by extension build/typecheck plus focused helper-proof artifacts rather than a real browser session.

## rev0091 memory

- The newest audited baseline before this revision was `GlassTTY-rev0090-2026.03.17.11.56-nativebrokerlease-oneshotsecondary-hostidentity-stonechat.zip`.
- Chrome's current native-messaging docs still say `connectNative()` keeps one host process alive while `sendNativeMessage()` starts a fresh process per request and only returns the first reply. That exposed a remaining GlassTTY truth gap after rev0090: a one-shot status helper could still become broker owner if it happened to start before the persistent lane claimed the lease.
- `daemon/src/glassttyd/native_host.py` now defers broker ownership until the first browser message and interprets per-message broker intent. `bridge.status` and one-shot probe pings can stay `secondary_only`, while persistent-port health pings remain owner candidates.
- Broker-server construction is now lazy, so secondary helper processes can answer diagnostics without instantiating or binding the local broker at all.
- The extension background now marks persistent health pings with `broker_intent: owner_candidate` and one-shot `bridge.status` / probe health pings with `broker_intent: secondary_only`, which keeps the browser↔CLI ownership split explicit instead of heuristic.
- Honest gap remains: this revision still does **not** prove a fresh live Chromium/native-host/browser round-trip in this container; the new deferred-ownership lane is validated here by focused tests, full smoke, and a direct temp-home proof bundle rather than a real browser session.

## rev0090 memory

- The newest audited baseline before this revision was `GlassTTY-rev0089-2026.03.17.11.24-nativestatus-oneshot-overflowprobe-redstart.zip`.
- Chrome's current native-messaging docs still distinguish `connectNative()` from `sendNativeMessage()` in the strongest possible way: long-lived port versus fresh process per request. That meant GlassTTY's one-shot native status snapshots needed explicit broker-ownership discipline instead of assuming every host invocation could safely bind the same local broker socket.
- `daemon/src/glassttyd/broker_lock.py` now gives the long-lived host an ownership lease over `GLASSTTY_HOME/run/daemon.sock`; helper one-shot processes become `secondary` broker roles instead of unlinking/rebinding the broker path, and native-host status payloads now preserve `host_identity` plus `broker` metadata.
- The extension background now records persistent-host identity from `health.ping`, compares one-shot native status snapshots against that identity, and surfaces whether a snapshot came from the same host process or from a secondary helper process.
- `scripts/doctor.py --pretty` and `python scripts/native-host-report.py --pretty` now surface broker-owner runtime metadata directly, which should make future handoffs much faster when a profile already has a live owner process.
- Honest gap remains: this revision still does **not** prove a fresh live Chromium/native-host/browser round-trip in this container; the new ownership guard is validated here by focused tests plus a direct two-process temp-home proof that the owner socket survives a one-shot status invocation.

## rev0089 memory

- The newest audited baseline before this revision was `GlassTTY-rev0088-2026.03.17.11.00-overflowprune-retention-inventory-spurwing.zip`.
- Current Chrome docs still treat `connectNative()` and `sendNativeMessage()` as different tools: the former keeps a long-lived host/port alive, while the latter is the single-request/single-response lane. That suggested a better operator surface than more raw state mirroring: use a compact one-shot native status snapshot for diagnostics instead of trying to tunnel full local state through the steady-state bridge.
- `daemon/src/glassttyd/overflow_artifacts.py` now has a compact inventory summary helper, and the native host includes that compact digest in `bridge.status` so local status can be surfaced without retransmitting a giant artifact list.
- The extension background now refreshes and caches a one-shot native status snapshot for `bridge.status` / `bridge.probe`, and the side panel plus probe page can show that compact local truth directly.
- Honest gap remains: this revision still does **not** prove a fresh live Chromium/native-host/browser round-trip in this container; the browser-facing half is validated here by TypeScript typecheck/build plus native-host-side proofs, not a live browser session.

## rev0088 memory

- The newest audited baseline before this revision was `GlassTTY-rev0087-2026.03.17.10.19-nativeoverflowreport-hostsignal-operatorsight-whimbrel.zip`.
- Chrome's current native-messaging docs still make long-lived native ports and the 1 MB host→extension cap central facts, which means overflow spill artifacts can accumulate during sustained sessions even when the bridge survives.
- `python -m glassttyd.cli overflow-report` now carries overflow inventory context, and the new `python -m glassttyd.cli overflow-prune` lane can dry-run or apply retention without deleting the latest linked artifact by default.
- `scripts/doctor.py --pretty` and `scripts/native-host-report.py --pretty` now surface overflow inventory counts/bytes as part of the same audit loop, so future sessions can distinguish “latest overflow happened” from “overflow evidence is now piling up.”
- Honest gap unchanged: this container still does not prove a fresh live Chromium/native-host/browser round-trip, so the new retention loop is validated by focused CLI/script proofs rather than a browser-captured repeated-overflow session here.

## rev0087 memory

- The newest audited baseline before this revision was `GlassTTY-rev0086-2026.03.17.10.03-nativeoverflow-spoolguard-budgetsafety-bobolink.zip`.
- Chrome's current native-messaging docs still cap host→extension messages at 1 MB while extension→host messages can be much larger, so GlassTTY should treat oversized host replies as an operator-reporting problem, not just a crash-avoidance problem.
- `python -m glassttyd.cli overflow-report` is now the fastest local way to inspect the latest oversized-host spill artifact without printing the full payload by default.
- `scripts/doctor.py --pretty` and `scripts/native-host-report.py --pretty` now surface the latest oversized-host summary directly, and the extension background/side panel preserve native-host overflow notices as `lastOversizedHostMessage` instead of leaving them as generic unhandled native messages.
- Honest gap unchanged: this container still does not prove a fresh live Chromium/native-host/browser round-trip, so the new extension-side overflow visibility is validated by typecheck/build and host-side focused proofs rather than a browser-captured overflow event here.

## rev0086 memory

- The newest audited baseline before this revision was `GlassTTY-rev0085-2026.03.17.09.05-playwrightrawtruth-gcowners-auditsignal-merlin.zip`.
- Chrome's current native-messaging docs still cap host→extension messages at 1 MB and extension→host messages at 64 MiB, which means GlassTTY must treat rich fixture/diagnostic payload size as a runtime reliability concern, not just an offline lint.
- The native host now spills oversized outbound messages to `GLASSTTY_HOME/state/fixtures/oversized-host-outbound-*.json`, mirrors a summary to `state/latest/oversized-host-outbound.json`, exposes that summary through `bridge.status`, and emits a compact `error.report` so the browser loop survives an overflow.
- Focused proof for this revision should live under `validation/rev0086-focused/`, but there is still no fresh live Chromium/native-messaging/browser round-trip in this container.

## rev0085 memory

- The newest audited baseline before this revision was `GlassTTY-rev0084-2026.03.17.08.51-playwrightmarker-stalesurvival-cacheproof-lapwing.zip`.
- Fresh upstream docs still point to `install --list` plus stale-browser GC as the browser-cache truth surfaces, but local proof in this environment exposed a subtle GlassTTY problem: running the prepared `install --list` path first could create the current `.links` entry and accidentally hide a missing-current-link state.
- `scripts/playwright_browsers.py` now preserves a raw non-mutating list path (`ensure_links=False`), records browser ownership aggregated from `.links`, distinguishes foreign-only retention from current-driver ownership, and flags local installs that currently satisfy Playwright's stale-browser removal rules.
- `scripts/playwright-browsers.py inspect` and `scripts/doctor.py` now carry both `install_list_raw` and `install_list_prepared`, while the audit lane keeps the raw registry snapshot instead of inspecting a cache root after it has already been healed.
- Honest proof in this container is still cache/tooling proof, not a live browser/native-host/browser round-trip. The new value is that future sessions can now see when a cache root only *looks* healthy because GlassTTY prepared it first.

## rev0084 memory

- The newest audited baseline before this revision was `GlassTTY-rev0083-2026.03.17.08.23-playwrightrepair-shadowalign-upstreamcache-curlew.zip`.
- Playwright's current browser docs still frame `install --list` and stale-browser removal as ownership truth, but local validation in this container exposed a sharper bug: GlassTTY-imported `chromium-1208` became visible to `install --list` in rev0081+, yet a later raw `python -m playwright install chromium` still deleted it because the imported directory lacked `INSTALLATION_COMPLETE`.
- GlassTTY now restores that marker on archive/CfT import, on already-aligned cache reuse, and through the repair lane (`python scripts/playwright-browsers.py repair --apply --write-missing-markers ...`). Future sessions should treat missing-marker audits as a serious survival risk, not cosmetic metadata.
- Focused proof for this revision should live under `validation/rev0084-focused/`, including one temp-root before/after command pair showing that the marker-preserving import survives a later raw `python -m playwright install chromium` here even though the install still fails on FFmpeg DNS.

## rev0083 memory

- The newest audited baseline before this revision was `GlassTTY-rev0082-2026.03.17.03.52-playwrightaudit-shadowtruth-versionlock-wryneck.zip`.
- The next useful Playwright step was not more cache observation but **cache repair**. Current upstream docs keep `install --list` and stale-browser removal as first-class lifecycle features, so warning about shadow installs without a repair path was leaving leverage on the table.
- `scripts/playwright_browsers.py` now has a repair lane: `plan_playwright_cache_repair()` identifies repairable shadow installs and broken `.links` entries, and `repair_playwright_cache()` can align those installs to the current package-owned names plus prune broken links.
- `python scripts/playwright-browsers.py repair --pretty` is the dry-run report; `--apply --align-shadow-installs --prune-broken-links` performs the reconciliation. `doctor.py` and `inspect` now carry the same repair plan so future sessions get an explicit command, not just GC-risk warnings.
- Honest proof for this revision should preserve one temp-root cache that starts with a shadow install + broken link, one dry-run repair plan artifact, one applied repair artifact, and one raw `python -m playwright install --list` output showing the repaired install under the expected current package name.
- Honest gap remains: this container still does not prove a fresh live Chromium/native-host/browser round-trip or a successful direct Playwright browser download into the main cache root here.

## rev0082 memory

- The newest audited baseline before this revision was `GlassTTY-rev0081-2026.03.17.07.36-playwrightregistry-upstreamtruth-linkheal-siskin.zip`.
- The most useful next Playwright improvement was not another import path but a **cache-audit truth lane**. GlassTTY can now compare on-disk browser directories, `.links` registry references, and parsed `install --list` output so future sessions can see shadow installs and stale registrations instead of guessing from silence.
- `scripts/playwright-browsers.py audit --pretty`, `inspect --pretty`, and `doctor.py --pretty` now expose that truth directly, including notes about shadow installs, broken links, and missing registered paths.
- A real archive-hygiene bug surfaced during this audit: `extension/manifest.json` was still at `0.1.36` while npm metadata had moved to `0.1.37`. rev0082 fixes the drift at `0.1.38` and teaches `scripts/verify-package.py` to fail future archives when manifest/package/package-lock versions disagree.

## rev0081 memory

- The newest audited baseline before this revision was `GlassTTY-rev0080-2026.03.17.03.03-playwrightlist-linksprep-cachetruth-godwit.zip`.
- The next real bug after rev0080 was that `install --list` still could not see GlassTTY-imported browser directories. Local Playwright source inspection showed why: the CLI walks `.links/<sha1(package_path)>` files, not the cache directories directly.
- `scripts/playwright_browsers.py` now has `ensure_playwright_registry_link()` plus idempotent registry repair in `playwright_install_list()`, archive import, CfT import, and already-installed/already-aligned paths. Future sessions should treat this as the upstream-visible cache-registration primitive, not just a cosmetic helper.
- Focused proof for this revision should preserve one raw `python -m playwright install --list` artifact against a temp imported cache root, because the point of rev0081 is that GlassTTY-seeded installs are now visible to upstream Playwright tooling instead of only to local cache scans.

## rev0080 memory

- The newest audited baseline before this revision was `GlassTTY-rev0079-2026.03.17.02.36-playwrightbootstrap-directdownload-proofluxury-sungrebe.zip`.
- A fresh upstream clue turned into a local bug fix: Playwright now documents `install --list`, but in this container the real command failed with `ENOENT ... /.links` whenever the cache registry directory had never been created. GlassTTY now treats that registry prep as part of inspection instead of leaving operators to trip over it.
- `scripts/playwright_browsers.py` now has a structured `playwright_install_list()` lane plus `parse_playwright_install_list()` and `ensure_playwright_links_dir()`. Future sessions should prefer this before assuming Playwright's own list command is trustworthy in an empty environment.
- Focused proof for this revision should preserve one real `playwright-browsers.py list --pretty` artifact and one real `doctor.py --pretty` artifact, because the point of rev0080 is that the real container behavior changed from hard failure to explicit empty state.

## rev0079 memory

- The newest audited baseline before this revision was `GlassTTY-rev0078-2026.03.17.01.52-browserbudget-playwrighttimeout-fastpath-redshank.zip`.
- The most leverageful next Playwright improvement was to stop assuming a human would preseed the browser cache. GlassTTY can now try the exact current Playwright browser archive URL directly from the dry-run metadata, validate the payload, and then import it into the expected install name.
- Direct download is still explicit and still honest: `scripts/playwright-browsers.py sync --download` now reports structured `download-error` output (for example DNS failure in this container) and rejects non-zip payloads instead of misreporting success.
- Focused proof for this revision should preserve both the deterministic local-HTTP download tests and one real in-container `sync --download` artifact, because the environment-specific failure mode is now part of the product evidence.

## rev0078 memory

- The newest audited baseline before this revision was `GlassTTY-rev0077-2026.03.17.01.31-workerhealth-stalerecovery-mv3resilience-sandpiper.zip`.
- The most useful next fix was not another MV3 breadcrumb but a **budgeted Playwright discovery lane**. The smoke harness and `doctor.py` were both willing to spend a full default `playwright install --dry-run chromium` probe inside a 25-second smoke budget, which made early termination harder to interpret and easier to misattribute.
- `scripts/playwright_browsers.py` now treats Playwright dry-run metadata as advisory: it records timeout/error state, preserves partial stdout/stderr when available, and still falls back to cache/system-browser discovery instead of crashing or blocking the whole lane.
- `scripts/e2e-fixturelab.py` now injects a bounded `GLASSTTY_PLAYWRIGHT_DRY_RUN_TIMEOUT` for the smoke environment, records that budget in the report, and reuses a single discovery result through the persistent-lane attempt instead of rediscovering browser state multiple times.
- Honest in-container progress improved: the real smoke reached `browser_selected=headless-new` before signal 15 instead of dying before browser selection. That still is **not** a full live browser/native-host proof, but it makes the next failure meaningfully later and easier to reason about.

## rev0077 memory

- The newest audited baseline before this revision was `GlassTTY-rev0076-2026.03.17.01.13-workerforensics-swbreadcrumbs-contextsignals-turnstone.zip`.
- A fresh March 2026 Playwright issue made the next move clearer: MV3 extension service workers can restart without a fresh `serviceworker` event when Chrome reuses the same CDP target ID, which means a previously observed worker handle can go stale even though the extension is alive.
- `scripts/e2e-fixturelab.py` now waits for a *healthy* extension worker instead of trusting the first handle. The new helper polls `context.service_workers()`, retries through `worker.evaluate(...)` failures, and records `service_worker_wait` plus `service_worker_initial_snapshot` so future sessions can see whether the smoke recovered from a stale worker or never found a healthy one.
- Focused tests now cover explicit stale-worker recovery plus the new report fields in both Playwright persistent-launch and Playwright CDP-attach paths.
- The honest in-container smoke attempt still terminated with signal 15 before browser selection completed, so this revision does **not** claim a fresh live proof of the new worker-health recovery against a real browser run here.

## rev0076 memory

- The newest audited baseline before this revision was `GlassTTY-rev0075-2026.03.17.00.55-checkpointreport-smokedurability-signalledger-whimbrel.zip`.
- The next high-leverage move after durable smoke reports was **richer service-worker evidence**. The smoke harness already knew whether an extension worker existed, but it still discarded the worker's own console/close lifecycle and any service-worker-originated network breadcrumbs that could explain a half-booted MV3 session.
- `scripts/e2e-fixturelab.py` now preserves worker snapshots, worker console/close events, service-worker request breadcrumbs, and context-level console/weberror events in the Playwright lane, and focused tests cover both persistent launches and Playwright CDP attaches.
- The honest in-container smoke attempt still ended with signal 15 before browser selection completed, so this revision does **not** claim a fresh live proof of the new telemetry against a real page; it does leave a durable JSON report again, and the new telemetry fields are now ready for the first browser-capable environment that gets farther.
- Honest gap remains unchanged: no fresh live Chromium/native-host/browser round-trip against a real target site was proven in this container.

## rev0075 memory

- The newest audited baseline before this revision was `GlassTTY-rev0074-2026.03.17.00.36-tracecarry-playwrightforensics-smokeevidence-kittiwake.zip`.
- The highest-leverage next fix was not another browser feature but **durable smoke evidence**. The real rev0074 smoke attempt could still vanish without leaving a usable report, which made every later diagnosis shakier than it needed to be.
- `scripts/e2e-fixturelab.py` now writes its report atomically from the beginning, checkpoints major phases (`starting`, `environment_ready`, `doctor_complete`, `extension_ready`, `probe_ready`, `bridge_wait_complete`, `cli_complete`, `failed`, `terminated`, `finished`), and records signal-driven exits before final cleanup.
- Focused tests now cover the new atomic/checkpoint/signal-report helpers, and the in-container honest smoke attempt now proves the key property rev0075 wanted: a signal-terminated run still left behind a parseable JSON artifact with phase and event history.
- Honest gap remains unchanged: no fresh live Chromium/native-host/browser round-trip against a real target site was proven in this container.

## rev0074 memory

- The newest audited baseline before this revision was `GlassTTY-rev0073-2026.03.17.00.21-identitytight-packagerename-manifestlock-oystercatcher.zip`.
- The next practical leverage point was not another manifest tweak but **better live-browser evidence**. Current Playwright guidance still treats persistent Chromium contexts as the supported extension-testing lane, and its own trace viewer is the preferred post-failure debugging artifact.
- `scripts/e2e-fixturelab.py` now saves a `playwright-trace.zip` artifact beside the JSON report whenever the persistent Playwright lane runs, and the report preserves whether tracing was requested, started, saved, or failed.
- Focused regressions now cover both bundled-Chromium and explicitly opted-in system-browser fallback paths so trace handling does not silently rot while the main browser/native-host acceptance gap remains open.
- Honest gap remains unchanged: no fresh live Chromium/native-host/browser round-trip against a real target site was proven in this container.

## rev0073 memory

- The newest audited baseline before this revision was `GlassTTY-rev0072-2026.03.16.23.59-profilepreflight-nativehostledger-browseranchor-curlew.zip`.
- A real archive-integrity bug surfaced during continuation work: rev0072’s outer zip filename said rev0072, but the root folder inside the zip and the manifest identity still pointed at rev0071. Future sessions should treat archive identity drift as a first-class failure, not as harmless cosmetic noise.
- `scripts/package-release.sh` now stages real GlassTTY release zips under the output archive name, which means the packaged root follows the release filename even when the working directory basename is stale.
- `scripts/refresh-archive.py` now accepts `--root` and `--archive-name`, so copied/staged worktrees can refresh `ARCHIVE_MANIFEST.json` without pretending the script’s own repo path is the active archive identity.
- `scripts/verify-package.py` and `scripts/archive-audit.py` now both check archive identity drift (top-level root uniqueness plus manifest/root consistency), and focused regressions cover the new lane.
- Honest gap remains unchanged: no fresh live Chromium/native-host/browser round-trip was proven in this container.

## rev0072 memory

- The newest audited baseline before this revision was `GlassTTY-rev0071-2026.03.16.23.29-nativehostaudit-autotarget-browserfit-lapwing.zip`.
- Chrome’s current native-messaging and remote-debugging guidance pushed GlassTTY toward a tighter debugging invariant: every isolated profile should carry not just launch metadata but also the native-host readiness snapshot for the exact browser binary that was launched.
- `scripts/native_host_report.py` now exposes machine-readable recommended-target readiness (`primary_target_ready`, missing targets, extension-ID mismatches, host-path mismatches) and accepts an explicit browser binary so reports can describe the launch reality instead of an ambient default.
- `scripts/launch-chromium-profile.sh` now writes `glasstty-native-host.json` into the profile before launch, and `profile-report.py` / `glasstty-profile.sh info` / `doctor.py` surface that snapshot for future archaeology.
- The options page helper text was still stale and Chromium-specific; it now points users at `--target auto`, `native-host-report.py`, and profile-aware launch/info commands.
- Honest gap remains unchanged: no fresh live Chromium/native-host/browser round-trip was proven in this container.

## rev0071 memory

- The newest audited baseline before this revision was `GlassTTY-rev0070-2026.03.16.23.10-profileledger-debugport-doctorvisibility-avocet.zip`.
- Current Chrome native-messaging docs strengthened an older nuance into a product requirement: Chrome for Testing has its own documented `NativeMessagingHosts` locations now, but versions before Chrome 146 still used the Google Chrome locations. GlassTTY should therefore resolve native-host install targets automatically and audit installed manifests directly instead of trusting operators to remember the split.
- `scripts/install-native-host.sh` now defaults to `--target auto` and can install all browser-recommended targets with `--all-recommended`.
- `scripts/native_host_manifest.py` and `scripts/native-host-report.py` now preserve concrete install archaeology: standard target paths, parsed manifest JSON, allowed extension IDs, expected-wrapper matches, and browser-aware recommendations.
- `scripts/doctor.py` now carries those richer native-host checks into its main environment report, which should make the next real browser/native-host failure much less mysterious.
- Honest gap remains unchanged: no fresh live Chromium/native-host/browser round-trip was proven in this container.

## rev0070 memory

- The newest audited baseline before this revision was `GlassTTY-rev0069-2026.03.16.22.47-archivelean-proofcarry-sizeaudit-slimhandoff-sanderling.zip`.
- Chrome's current remote-debugging guidance made the next leverage point clearer: GlassTTY already launches isolated profiles, but future sessions still had to reconstruct *how* a given profile was launched and whether remote debugging had been requested at all.
- `scripts/launch-chromium-profile.sh` now records `glasstty-profile.json` in the profile itself before Chromium starts, including browser path, extension-loaded status, start URL, extra args, and remote-debugging mode/port.
- `scripts/profile-report.py` / `scripts/glasstty-profile.sh info` now surface saved launch metadata plus `DevToolsActivePort` when present, and `doctor.py` carries that profile/debug state into its JSON report and hint set.
- Honest gap remains the same: this container still does not prove a fresh live Chromium/native-host/browser round-trip, but the next machine should have a much easier time preserving profile/CDP archaeology when that proof fails or flakes.

## rev0069 memory

- The newest audited baseline before this revision was `GlassTTY-rev0068-2026.03.16.18.37-resumeproof-classicworkerimports-handoffclarity-albatross.zip`.
- The biggest practical archive problem was not source code but redundant validation binaries: the uploaded rev0068 handoff zip was ~60 MB and `validation/` alone dominated the unpacked tree because old `package-check.zip` and `.patch` artifacts were being carried forward.
- `scripts/package-release.sh` now defaults to excluding validation `.zip` / `.patch` blobs while keeping an explicit `GLASSTTY_PACKAGE_INCLUDE_VALIDATION_BINARIES=1` override for forensic packages.
- `scripts/verify-package.py` now records zip size, entry count, and sha256, and `scripts/validate-release.py` can preserve that proof via `package_zip_proof` without retaining `validation/.../package-check.zip` unless `--keep-package-zip` is requested.
- `scripts/archive-audit.py` is now the fastest way to explain why a GlassTTY tree is large; it surfaces top-level directory sizes, largest files, duplicate groups, and redundant validation artifacts in one JSON report.
- In this container, the slimmed package produced by the new default packager was about 1.2 MB and still passed `scripts/verify-package.py`.
- Honest gap unchanged: no fresh live Chromium/native-host/browser round-trip was proven in this session.

## rev0068 memory

- The package verifier now understands **classic worker dependency edges**, not just module-style ones. If a built extension page or worker reaches for a script through `importScripts(...)` or `new Worker("...")`, GlassTTY can now catch a missing packaged file before a human loads the unpacked extension.
- `validate-release.py` is now worth resuming instead of only autopsying. Use `--start-at` / `--end-at` for narrow forensic runs and `--resume` to continue a partial report without redoing already-successful steps.
- If a resumed run reaches `verify_package` but the old temp zip is gone, the validator now re-inserts `package_release` automatically. That keeps partial package-validation runs honest and usable instead of silently trusting a vanished artifact.
- `scripts/refresh-archive.py` now understands rev0068-style focused `summary.json` bundles. Future archive manifests should point at the focused validation dir directly instead of leaving `validation_summary` half-empty just because the wrapper was not the proving lane.
- Focused proof for this revision lives in `validation/rev0068-focused/`, and the concrete resume artifact trail lives in `validation/rev0068-resume-proof/`.

## rev0067 memory — 2026-03-16

- audited and continued from `GlassTTY-rev0066-2026.03.16.17.12-cssassetgraph-checkpointproof-zippathrepair-kestrel.zip`
- online Chrome docs kept reinforcing that extension assets used from content scripts/web pages are addressed through root-relative paths and `chrome.runtime.getURL(...)`, while content-script-facing assets must be declared in `web_accessible_resources`; rev0067 therefore extends package verification beyond manifest/HTML/CSS graphs into JS-discovered asset paths and worker/module entrypoints
- the sandbox exposed a real packager bug rather than just “wrapper flakiness”: asking `package-release.sh` to write a zip inside the repo tree could recurse into the archive it was still creating. rev0067 stages in-tree outputs outside the repo first, then moves the finished zip into place
- interrupted validation evidence is now more actionable: `validate-release.py` records `current_step.json` and a `running_step` field in partial summaries before each step launches, so future sessions can see what was in flight when the wrapper was terminated

## rev0066 memory — 2026-03-16

- audited and continued from `GlassTTY-rev0065-2026.03.16.12.45-resourcegraph-wartruth-archiveproof-whimbrel.zip`
- online Chrome docs reinforced a blind spot that rev0065 still missed: content-script CSS commonly reaches additional packaged assets (images, fonts, nested CSS) and Chrome's docs explicitly say those assets must be web-accessible when used from content scripts, so package verification now follows CSS asset graphs and separately checks WAR coverage for those reachable assets
- the full validation wrapper still gets interrupted in this container before a clean all-steps finish, but rev0066 no longer loses the evidence: it writes partial `report.json` / `SUMMARY.md` checkpoints after every finished step and stages the package-check zip outside the repo tree to avoid validating against an in-tree archive target
- `scripts/package-release.sh` now resolves relative output paths before changing directories, which closes a real operator/LLM footgun that surfaced during rev0066 validation work

## rev0065 memory

- The newest audited baseline before this revision was `GlassTTY-rev0064-2026.03.16.13.18-churntruth-packagecoherence-archivepolish-peregrine.zip`.
- Chrome's current MV3 docs keep emphasizing that packaged resource declarations are relative to the extension root: content-script JS/CSS paths must point at extension-root files, and `web_accessible_resources` maps relative resource patterns to specific allowed origins or extension IDs. rev0065 therefore treats package verification as **resource-graph truth**, not just file presence.
- `scripts/verify-package.py` now checks transitive ES-module imports from packaged extension entrypoints, HTML-linked assets such as stylesheets, manifest icon/page/script references, and `web_accessible_resources` glob coverage. Future release claims should point at the saved verifier JSON, not just “zip exists”.
- Focused proof for this revision lives in `validation/rev0065-focused/`, but the full `validate-release.py` wrapper again terminated early in this container before writing its report. Treat the saved focused bundle as the honest gate and the wrapper behavior as an environment artifact still worth debugging later.

## rev0064 memory

- The newest audited baseline before this revision was `GlassTTY-rev0063-2026.03.16.11.47-releaseintegrity-coverageproof-archiveclarity-quartz.zip`.
- Chrome's current instant-navigation guidance keeps reinforcing that `documentId` is the right identity for a document while `frameId` can persist across navigations and multiple outermost frames can coexist. rev0064 therefore treats coverage-experiment comparison as a **shape-matching** problem, not a raw frame-ID/count problem.
- `scripts/compare-coverage-experiments.py` now preserves legacy status counts plus new stable/coarse gap signatures and warns when a post-reload artifact only matches the baseline prediction numerically. Future live proof bundles should keep this JSON output beside the raw before/after probes.
- `scripts/verify-package.py` now checks manifest and HTML entrypoint references in the packaged zip, so archive readiness covers more than “did a few important files survive packaging”.
- Focused proof for this revision lives in `validation/rev0064-focused/`, but there is still no fresh live Chromium/native-messaging/browser session proving the new comparator against a real supported tab reload.

## rev0063 memory

- The newest audited baseline before this revision was `GlassTTY-rev0062-2026.03.09.12.32-runtimeexperiment-dynamicregister-coverageflight-skylark.zip`.
- Chrome's current docs say dynamic content-script registrations default `persistAcrossSessions` to true and that `unregisterContentScripts()` does **not** remove already-injected scripts, so GlassTTY now preserves an explicit offline comparison lane for before/after experiment artifacts instead of assuming operators will remember every caveat from docs or chat.
- The new evidence lane is `scripts/compare-coverage-experiments.py` and `glassttyd compare-coverage-experiments`. Future live sessions should save a baseline probe, run one experiment, reload or renavigate the supported tab, save the second probe, then run the comparator before arguing for any default manifest-policy change.
- Release packaging was not as trustworthy as the archive implied: `scripts/package-release.sh` had been dropping `extension/dist`. rev0063 fixes that and adds `scripts/verify-package.py` plus focused tests so future sessions can trust that a packaged zip still contains the runnable MV3 bundle.
- `scripts/refresh-archive.py` now derives archive identity from the folder name and summarizes validation state directly in `ARCHIVE_MANIFEST.json`, which should make future handoffs much less brittle.

## rev0062 memory

- The newest audited baseline before this revision was `GlassTTY-rev0061-2026.03.09.12.10-experimentmatrix-manifestdeltas-coverageplanner-heron.zip`.
- Coverage planning should not stop at passive advice. GlassTTY can now register a **non-persistent dynamic content-script experiment** that clones the existing static content script with runtime `all_frames`, `match_about_blank`, or `match_origin_as_fallback` deltas.
- Effective coverage policy now needs to include dynamic registrations, not only the static manifest. `bridge.probe.manifest.contentScriptPolicy` and receiver coverage audits now reflect the current runtime policy if an experiment is active.
- The new CLI lane is `glassttyd content-script-experiment`, `glassttyd set-content-script-experiment …`, and `glassttyd clear-content-script-experiment`. Future live sessions should use that path, then reload or renavigate the supported tab before comparing before/after coverage.
- Focused proof for this revision lives in `validation/rev0062-focused/`, but there is still no fresh live Chromium session proving that a dynamic experiment changes observed receiver coverage exactly the way the saved experiment plan predicts.

## rev0061 memory

- The newest audited baseline before this revision was `GlassTTY-rev0060-2026.03.09.11.18-policyhints-manifestaudit-gapadvice-sunbird.zip`.
- Receiver coverage artifacts should preserve **what each Chrome lever would change**, not only which lever a gap suggests. `receiverAudit.coverageAudit.experimentPlan` now saves the current runtime-priming baseline plus manifest-delta scenarios, projected remaining-gap counts, and a recommended next experiment.
- Live `fixture.capture` metadata now preserves `receiver_coverage_experiment_plan`, so future sessions can compare saved browser evidence against a deliberate manifest experiment without recomputing the tradeoff matrix by hand.
- The probe page summary can now tell an operator whether the current conservative path is still recommended or whether a focused `match_about_blank` / `match_origin_as_fallback` experiment would shrink the observed gap set.
- Focused proof for this revision lives in `validation/rev0061-focused/`, but there is still no fresh live Chromium session proving the experiment-plan fields against a real supported related-frame tab and an actual manifest variant.

## rev0060 memory

- The newest audited baseline before this revision was `GlassTTY-rev0059-2026.03.09.10.42-relatedframe-coverageaudit-gaptruth-lantern.zip`.
- Receiver coverage artifacts should preserve **which Chrome policy lever a gap suggests**, not just that a gap exists. `bridge.probe.manifest.contentScriptPolicy` now records the current declarative posture, and `receiverAudit.coverageAudit.policyHints` now summarizes when the evidence points toward runtime priming versus manifest experiments like `all_frames`, `match_about_blank`, or `match_origin_as_fallback`.
- Live `fixture.capture` metadata now preserves `receiver_coverage_policy_hints` alongside the broader coverage audit, so future sessions can compare saved browser evidence against deliberate manifest experiments without recomputing advice by hand.
- Focused proof for this revision lives in `validation/rev0060-focused/`, but there is still no fresh live Chromium session proving the new policy-hint fields against a real supported related-frame tab.

## rev0059 memory

- The newest audited baseline before this revision was `GlassTTY-rev0058-2026.03.09.10.20-probeaudit-fixturerank-prooflane-oriole.zip`.
- Receiver archaeology should distinguish **supported subframes we can currently prime** from **related-frame URLs Chrome docs call out separately**. The new coverage audit now marks `about:` / `data:` / `blob:` / `filesystem:` frames as `related_frame_url` instead of hiding them under a generic unsupported bucket.
- `bridge.probe.receiverAudit.coverageAudit` and fixture metadata now preserve both the priming plan and the frame-by-frame gap list, so future sessions can explain missing receivers without replaying navigation by hand.
- Focused proof for this revision lives in `validation/rev0059-focused/`, but there is still no fresh live Chromium session proving the new related-frame coverage signals against a real supported tab.

## rev0058 memory

- The newest audited baseline before this revision was `GlassTTY-rev0057-2026.03.09.09.57-resolvertruth-explainrank-audubon.zip`.
- Resolver ranking evidence should not stay CLI-only. `bridge.probe.receiverAudit` now preserves `resolverPolicy`, `receiverResolution`, and `rankedMatches`, which means future live probe artifacts can explain receiver choice without a second diagnostic command.
- Live `fixture.capture` metadata now preserves the same ranking evidence under `receiver_resolver_policy`, `receiver_resolution`, and `receiver_ranked_matches`. Future sessions should save those fields whenever receiver choice matters.
- Focused proof for this revision lives in `validation/rev0058-focused/`, but there is still no fresh live Chromium session proving the new browser-side audit fields against a real multi-receiver tab.

## rev0057 memory

- The newest audited baseline before this revision was `GlassTTY-rev0056-2026.03.09.09.31-outermosttruth-lifecyclefilter-resolver-sparrow.zip`.
- `glassttyd resolve-receiver` should no longer trust incidental receiver row order. It now sorts matches by lifecycle preference, outermost-ness, readiness, frame depth, and recency so shell decisions stay deterministic and closer to GlassTTY's browser-side receiver truth.
- `glassttyd resolve-receiver --explain` now returns ranking evidence (`resolverPolicy`, `receiverResolution`, `rankedMatches`) that future sessions should preserve in live proof bundles whenever receiver choice is in doubt.
- Focused proof for this revision lives in `validation/rev0057-focused/`, but there is still no fresh live Chromium session proving the new explanation lane against a real multi-frame/prerendering tab.

# MEMORY

## rev0056 memory

- The newest audited baseline before this revision was `GlassTTY-rev0055-2026.03.09.09.05-lifecycletruth-docswap-navtrace-kestrel.zip`.
- Chrome instant-navigation guidance says `frameId == 0` is not a safe universal outermost-frame test anymore; GlassTTY's daemon/CLI now mirrors the extension's richer outermost test instead of treating non-zero prerendered outermost documents like ordinary subframes.
- `glassttyd resolve-receiver` now has `--active-outermost` and `--document-lifecycle`, which gives shell automation a precise way to ask for the active outermost receiver instead of only the broad `--top-frame` concept.
- Focused proof for this revision lives in `validation/rev0056-focused/`, but there is still no fresh live Chromium session proving the new resolver flags against a real prerender→active transition.

## rev0055 memory

- The newest audited baseline before this revision was `GlassTTY-rev0054-2026.03.09.08.29-receiverpriming-docinject-idempotentretry-wayfinder.zip`.
- Chrome's current instant-navigation/document model makes `documentId` the safer identity than `frameId` across navigations, so GlassTTY should treat a same-frame new document as a replacement, not as a sibling receiver.
- Known inactive lifecycles (`prerender`, `cached`, `pending_deletion`) should not outrank an active or lifecycle-unknown receiver just because they are outermost-frame-shaped.
- `receivers.frame_navigation` now preserves `documentLifecycle`, which should make future live trace bundles much easier to interpret when active and prerendered documents coexist in the same tab.
- The focused rev0055 proof is green, but `scripts/validate-release.py` still stalled after its early steps in this container, so future sessions should keep treating the focused validation bundle as the honest release gate here.

## rev0054 memory

- GlassTTY still has **not** widened the manifest to `all_frames`; instead it now uses a conservative receiver-priming lane that programmatically injects the existing content script into supported subframes discovered through Chrome `webNavigation` frame inventory. Treat this as better receiver discovery, not as proof that broad frame policy is now justified.
- Reinjection and recovery should now prefer `documentId` when available. That matters because Chrome frame IDs can outlive a document navigation while `documentId` changes per document.
- Content-script bootstrap is now intentionally idempotent so recovery/priming injections are less likely to stack duplicate listeners and observers in the same frame.
- Focused proof for this revision lives in `validation/rev0054-focused/`, but there is still no fresh live browser proof that a newly discovered supported subframe announced itself through this lane.

## rev0053 memory

- Receiver inventories are now hierarchical, not merely contextual. Prefer `framePathLabel`, `frameDepth`, and `framePathFrameIds` when reasoning about which receiver GlassTTY should target in a multi-frame tab.
- `glassttyd resolve-receiver` can now resolve by receiver ancestry (`--frame-host-contains`, `--frame-path-contains`, `--frame-depth`), which is a better automation surface than copying opaque `doc:...` keys out of `bridge.status`.
- Live `fixture.capture` metadata now preserves receiver ancestry/path fields for the selected receiver, so future archive comparisons can tell not just which receiver won, but where it sat in the frame tree.
- This is still browser-grounded plumbing, not fresh browser proof. The archive does not yet contain one real live multi-frame tab where those ancestry/path fields were exercised end to end.
- Focused proof for this revision lives in `validation/rev0053-focused/`.


## rev0052 memory

- Receiver inventory is now more than keys and readiness. GlassTTY can preserve frame type, parent-frame linkage, frame URL, and origin alongside `documentId` / `frameId`, which makes future multi-frame archaeology and operator choice much more legible.
- `glassttyd resolve-receiver` exists because `select-receiver` alone still forced humans and scripts to copy opaque keys from `bridge.status`. Use the resolver first when you want a receiver by frame semantics rather than raw inventory IDs.
- `bridge.probe.receiverAudit`, side-panel receiver rows, and live `fixture.capture` metadata now preserve receiver frame context too, so future sessions should save those artifacts before claiming a multi-frame tab was understood correctly.
- The extension now depends on the `webNavigation` permission for this auditability layer. That is a purposeful observability increase, but still not the same thing as flipping content-script policy to `all_frames`.
- Focused proof for this revision lives in `validation/rev0052-focused/`.

## rev0051 memory

- GlassTTY's receiver inventory is no longer side-panel-only. The daemon CLI now has first-class receiver inspection and override commands, which means future sessions can audit receiver choice from scripts and validation bundles instead of scraping `bridge.status` JSON by hand.
- `bridge.probe` now exposes a compact `receiverAudit` summary for the currently selected/targeted tab. Use that artifact first when checking whether a multi-frame session is top-frame-selected, operator-overridden, stale, or ambiguous.
- The product still deliberately avoids turning on broader frame injection policy just because receiver plumbing improved. Treat rev0051 as better operator evidence and control, not proof that `all_frames` or `match_origin_as_fallback` should already be enabled.
- Focused proof for this revision lives in `validation/rev0051-focused/`.

## rev0049 memory

- GlassTTY now distinguishes **supported tab identity** from **content receiver inventory**: a tab can preserve multiple observed `documentId` / `frameId` receiver contexts instead of flattening itself to whichever frame last spoke.
- The current preferred-target policy is deliberately conservative: choose a ready top-frame receiver first, then a single ready receiver, then the newest observed fallback. This is groundwork for future `all_frames` / `match_origin_as_fallback`, not proof that those manifest switches are already safe to flip.
- The archive now preserves deterministic receiver-inventory validation under `validation/rev0049-focused/receiver-inventory-check.json`, plus typecheck/build and focused pytest logs.
- Extension version is now `0.1.13`.

## rev0048 memory

- GlassTTY now distinguishes **frame capture coverage** from plain iframe inventory: `frame_capture_status`, `frame_capture_ratio`, `total_iframe_count`, and blocked-frame names/titles/paths are preserved so future sessions can tell when a saved fixture only saw part of a frame tree.
- The planner now warns when saved frame evidence is partial or blocked-only; treat iframe-rooted suggestions more cautiously when those warnings are present.
- The deterministic lab now has `/iframe-partial-shell`, which mixes one same-origin iframe with one sandboxed sibling iframe to model realistic partial capture without needing a live third-party embed.
- The seeded corpus now includes `fixturelab-iframe-partial-live.json`, and `fixtures/corpus/` was regenerated in this revision.

## rev0047 memory

- The newest audited baseline before this revision was `GlassTTY-rev0046-2026.03.08.21.00-iframepaths-sameorigincapture-nestedlocator-orbit.zip`.
- Output scope is now first-class archive evidence, not just input scope: use `top_output_label`, `top_output_locator_strategy`, `top_output_locator_root`, `top_output_frame_path`, and `split_scope_detected` before assuming the read step should inherit the write root.
- `scripts/fixture_plan_lib.py` now warns when write/read roots diverge, especially for frame-rooted input with page-rooted output. Future sessions should preserve those warnings unless a real browser capture disproves them.
- The fixture lab now has deterministic split-scope iframe pages (`/iframe-split-shell`, `/iframe-split-compose`) and the seeded corpus includes `fixturelab-iframe-split-live.json`.
- `scripts/index-fixtures.py` and `scripts/compare-fixtures.py` now surface read-side locator-root/frame-path drift directly, so use them before claiming GlassTTY understands multi-scope flows.
- Honest gap unchanged: no fresh browser-sourced end-to-end fixture save or native-messaging round-trip was proven in this container.

## Snapshot

GlassTTY is a Chromium-first, Nix-friendly browser-to-terminal toolkit.

It is designed as a generic bridge for browser applications, with Claude.ai as the first real adapter and fixture-lab as the deterministic local proving ground.

## Current shape

- Extension model: Manifest V3 extension for Chromium
- Bridge model: native messaging with a long-lived `connectNative()` port
- Backend model: Python native host plus a local UNIX-socket broker
- Terminal interface: CLI commands backed by the broker socket
- Profile model: dedicated Chromium user-data dirs launched by helper scripts
- Browser operator surface: Chrome side panel plus dynamic options page backed by trusted-context extension storage
- Tab model: active supported tab by default, with persistent selected-target routing, explicit `tab_id` overrides, and remembered sender `documentId`/`frameId` hints
- Recovery model: if a supported tab loses its content-script receiver, the background can attempt runtime reinjection with `chrome.scripting.executeScript()` unless the tab is frozen/discarded
- Browser affordance model: per-tab action badge/title hints communicate unsupported, ready, selected-target, frozen, and discarded states
- Dev-install model: stable unpacked extension ID from `manifest.key`, absolute wrapper executable for the native host, and `--extension-id auto` install flow
- Test-page model: localhost fixture-lab adapter for deterministic content-script and fixture-capture work
- Live fixture-capture model: real browser-sourced fixtures should now preserve dialog/form/fieldset/iframe metadata directly in the extension payload instead of depending on the saved-HTML/offscreen lane for that richness

## Important current assumptions

- Primary browser target is Chromium.
- The first real integration is Claude.ai.
- The browser must stay open and visible in the main workflow.
- Headless or heavier automation may exist later, but is not the core v1 path.
- The side panel is a diagnostics/operator surface, not the main user interface.
- Transient bridge state should prefer `storage.session` over disk-backed storage unless user settings genuinely need persistence.
- Playwright is a future lab lane, not the foundation of the product path.
- A local Chrome-for-Testing bundle is now the preferred hermetic browser input for GlassTTY’s automation lab when available.

## Known unknowns

- final Claude.ai selector strategy
- how often transcript deltas will be too noisy in practice
- exact native-host packaging path under Nix-managed installs on every distro
- whether the broker should evolve toward a richer RPC or event subscription protocol
- when it becomes worth moving any hotspot into Rust
- how reliable runtime reinjection is across discarded/frozen/reactivated tabs in live Chromium

## Current repo intent

This archive is the source of truth and durable memory for the project. Chat history is not sufficient memory.

## Next sharp steps

1. Install and exercise a local Chrome-for-Testing bundle against the real smoke lane.
2. Prove native-host ping from extension background with the stable dev ID.
2. Use fixture-lab to verify `bridge.status`, `prompt.read`, `prompt.write`, and `capture-fixture` end to end.
3. Use the broker-backed CLI to request `bridge.status`, `list-tabs`, `select-tab`, `prompt.read`, and `prompt.submit` from live Claude tabs.
4. Save real Claude fixtures and document breakage-resistant selectors.
5. Capture one live offscreen-fixture JSON result and verify that `description_text`, `fieldset_legend`, `control_kind`, `submit_action`, `checked_state`, `autocomplete`, and `constraint_flags` appear when expected.
6. Run `plan-fixture` on a real browser-sourced fixture and compare the planner output against the synthetic rev0040 planner sample before changing adapter actions.
7. Capture one real rev0045 browser fixture and confirm `dialog_samples`, `iframe_samples`, and `semantic_outline` survive the full browser→native-host→CLI save path.

## rev0013 memory

- There is now a deterministic seeded corpus under `fixtures/corpus/`; it exists so future sessions have concrete fixture evidence even without a live browser.
- Use `scripts/compare-fixtures.py` or `python -m glassttyd.cli compare-fixtures` before claiming selector drift.
- `scripts/doctor.py` now emits `hints`, which are often the fastest way to explain why a real-machine proof is blocked.

## rev0014 memory

- The newest audited baseline before this revision was `GlassTTY-rev0013-2026.03.07.00.40-fixturecorpus-compare-doctorhints-archive-luxury-switchyard.zip`.
- The archive now contains MV3 `bridge.contexts` diagnostics through the extension, side panel, and CLI.
- The browser smoke lane now captures CDP targets so future sessions can distinguish “extension never loaded” from “native host never connected”.
- When Chromium is launched as root in a container, add `--no-sandbox` or the browser will fail before any extension evidence appears.
- CDP inspection helper was added so future sessions can distinguish “browser launched” from “extension loaded”.
- Release validation now preserves per-step stdout/stderr files under `validation/latest/steps/`.
- The honest gap remains the real native-messaging/browser round-trip, not static build quality.

## rev0015 memory

- Supported tabs now remember sender `documentId`, `frameId`, and `documentLifecycle`, so a known document can be targeted more precisely after the content script announces itself.
- The extension now distinguishes missing receiver vs frozen/discarded tab states and attempts runtime reinjection only when that is plausible.
- The toolbar action badge/title can now serve as a lightweight operator cue even before the side panel is opened.
- `scripts/validate-release.py` was hardened for timeout artifact capture, but a full end-to-end run of the validator wrapper itself is still not a trustworthy release gate in this container.

## rev0016 memory

- Chrome explicitly recommends reconnecting `connectNative()` from `onDisconnect`; GlassTTY now attempts that immediately instead of only nulling the port.
- The extension now keeps a recent background trace ring in `chrome.storage.session`, queryable through `bridge.trace` and the side panel.
- The browser smoke now has a place to capture CLI diagnostics like `bridge-status`, `contexts`, `trace`, `read-prompt`, and `read-latest` whenever the broker socket comes up.

## rev0017 memory

- Chrome recommends `chrome.alarms` over timers for delayed MV3 work; GlassTTY now uses alarms-backed backoff when native reconnects fail.
- `bridge.status` now has a native reconnect snapshot, and the side panel renders it separately from the larger mirrored bridge-state blob.
- Immediate reconnect is still attempted first, but repeated failures now schedule a later retry instead of only churning in the current worker session.


## rev0018 memory

- Chrome may clear alarms on browser restart, so a worker bootstrap should verify or restore any scheduled reconnect alarm instead of assuming the delay survived.
- `connectNative()` can keep the service worker alive while connected, but health visibility is still useful because the background can otherwise look connected while the host path is unclear.
- `runtime.getContexts()` now carries enough context metadata to make `bridge.contexts` materially more useful for side-panel and CDP correlation.
- In this container, Chromium headless-new can expose CDP and the page target, but the unpacked extension service worker still was not honestly proven.


## rev0019 memory

- The newest audited baseline before this revision was `GlassTTY-rev0018-2026.03.08.00.37-alarmresume-nativehealth-headlesslab-contextlens.zip`.
- GlassTTY now has a dedicated extension probe page plus `bridge.probe`; future sessions should use that before inventing new ad hoc smoke routes.
- The native host should treat unknown `bridge.*` response types as bridge passthroughs unless they are explicitly special-cased like `bridge.status`.
- In this container, the best-effort smoke is now more honest but still not successful: the extension build may need a fallback because of mixed ownership, and Chromium still exits before CDP with zygote/crash diagnostics even after writable XDG paths are set.
- The main remaining gap is no longer “we cannot observe anything”; it is “we still need one environment where the probe page and native host both survive long enough to prove the round-trip.”
- rev0020: headless Chromium with container-safe flags exposed the unpacked probe page over CDP, but native-host socket proof still lagged.



## rev0021 memory

- The newest audited baseline before this revision was `GlassTTY-rev0020-2026.03.08.02.03-cliproof-cdptruth-headlesswitness-lantern.zip`.
- The extension now keeps a worker-pulse snapshot in mirrored bridge state so future sessions can tell whether a new MV3 worker boot happened instead of inferring it from traces alone.
- The fixture-lab smoke now has a Playwright-over-CDP probe helper, but that lane is still secondary: in this container the raw headless Chromium `/json/list` proof is more trustworthy than the Playwright attach result.
- Manual rev0021 artifacts proved that Chromium `--headless=new` can list the unpacked extension probe page over DevTools in this container, which is stronger than the old “browser died before CDP” state.
- Manual rev0021 Playwright artifacts also proved that `connect_over_cdp()` can attach here, but the attached context currently surfaced `chrome-error://chromewebdata/` rather than the probe page, so Playwright should remain a lab lane, not the primary proof claim.
- The honest remaining gap is now narrower: not “can headless Chromium load the unpacked extension at all,” but “why does native-host/socket proof and Playwright page-level proof still lag behind the raw CDP evidence here?”


## rev0022 memory

- The newest audited baseline before this revision was `GlassTTY-rev0021-2026.03.08.03.00-playwrightlane-workerpulse-proofgarden-radiant.zip`.
- Playwright’s extension docs point to persistent-context launch as the first-class extension path, while `connect_over_cdp()` is explicitly lower fidelity; GlassTTY now encodes that distinction directly in the smoke harness and doctor output.
- `browser_env()` now preserves a shared `PLAYWRIGHT_BROWSERS_PATH` when one exists, so moving `HOME` into a temp harness directory no longer silently severs Playwright from its browser cache on real machines.
- In this container, `doctor.py` proves the current Playwright reality: the Python package is installed, no bundled Chromium cache is present, and any persistent-context attempt would need to fall back to `/usr/bin/chromium`.
- The honest gap remains live-browser proof: rev0022 sharpens launch strategy and diagnostics, but it still does not claim a successful native-host/socket round-trip in this container.

## rev0023 memory

- The newest audited baseline before this revision was `GlassTTY-rev0022-2026.03.08.04.10-persistentlane-browserdoctor-sharedcache-aurora.zip`.
- `bridge.probe` can now fall back to a one-shot native-host bootstrap ping via `sendNativeMessage()` when the long-lived `connectNative()` port is absent.
- The probe page now treats a successful one-shot native ping as real native-bootstrap evidence, even if the persistent daemon socket has not appeared yet.
- The e2e harness now records that one-shot bootstrap evidence separately under `native_bootstrap`, so future sessions can distinguish “native host launcher works” from “full socket/CLI round-trip works.”
- `doctor.py` now records `geteuid` and warns when Chromium is being checked from a root account, which matters in this container because root-plus-`--no-sandbox` remains a shaky lab-only condition.
- The latest full rev0023 smoke still failed before extension-page confirmation in this container, so the new one-shot probe path is product-ready and test-covered but not yet demonstrated end to end here.

## rev0026 memory

- The newest audited baseline before this revision was `GlassTTY-rev0025-2026.03.08.06.05-targetsense-cftcompat-nativepath-beacon.zip`.
- Chrome for Testing and Playwright bundled Chromium are now treated as different labs with different truth criteria: CfT is the preferred hermetic raw-browser/CDP substrate, while the Playwright persistent extension lane now defaults to bundled Chromium only.
- `scripts/playwright_browsers.py` is the shared source of truth for Playwright browser-cache discovery and extension-lane launch planning.
- In this container, `doctor.py` now shows `missing-bundled-chromium` by default for the Playwright persistent lane, and only shows a system-browser strategy when `GLASSTTY_PLAYWRIGHT_ALLOW_SYSTEM_EXECUTABLE=1` is set.
- This makes failed persistent-lane runs more honest: future sessions should not treat `/usr/bin/chromium` as the default Playwright extension browser unless they explicitly opt into that risk.

## rev0027 memory

- The newest audited baseline before this revision was `GlassTTY-rev0026-2026.03.08.07.10-lanematrix-playwrighttruth-bundlefirst-airstream.zip`.
- `python -m playwright install chromium` failed in this container on DNS (`EAI_AGAIN`), which turned out to be a real product insight: GlassTTY's browser-lab workflow needed an offline/local-archive path, not just better hints.
- GlassTTY can now seed the Playwright Chromium cache from either a local browser archive or an existing local Chrome-for-Testing install.
- The Playwright persistent lane now launches the cached executable path directly, so imported/offline bundles are usable by the lab harness instead of only being discoverable in doctor output.
- rev0027 includes artifacts proving that a seeded cache flips doctor output from `missing-bundled-chromium` to a supported `bundled-executable` plan, but it still does not claim a successful live browser/native-host round-trip in this container.


## rev0028 memory

- The newest audited baseline before this revision was `GlassTTY-rev0027-2026.03.07.08.25-offlinecache-playwrightseed-bundlebridge-harbor.zip`.
- Current local Playwright is `1.58.0`, and `python -m playwright install --dry-run chromium` now gives GlassTTY a concrete browser-package matrix even without downloading anything. In this container it reports `chromium-1208` (Chrome for Testing 145.0.7632.6) plus `chromium_headless_shell-1208`.
- GlassTTY no longer has to invent offline Playwright cache names blindly: archive imports and Chrome-for-Testing imports can now prefer the install names Playwright itself expects for the current package version.
- The persistent extension lane still wants the regular Playwright browser package, not the headless-shell package; headless-shell support is now visible in doctor/inspect output but is not treated as sufficient proof for the extension lane.
- rev0028 still does not claim a fresh live browser/native-host round-trip in this container; its real advance is better package-truth and offline cache alignment.


## rev0029 memory

- The newest audited baseline before this revision was `GlassTTY-rev0028-2026.03.08.08.25-playwrightcft-dryruntruth-cachematrix-skylight.zip`.
- GlassTTY now has a first-class Playwright package-sync command (`python scripts/playwright-browsers.py sync ...`) instead of only separate archive/CfT import primitives.
- The new sync path aligns against the current dry-run matrix first, so it can seed both `chromium-*` and `chromium_headless_shell-*` into the exact install names Playwright currently expects.
- In this container, a real `python -m playwright install chromium` still fails on DNS (`EAI_AGAIN` against `cdn.playwright.dev`), but the new sync command succeeds against local fixture archives and proves the package-alignment path independently of the networked installer.
- `wait_for_probe_result_playwright()` now passes `is_local=True` when available, which is a low-risk improvement for the local CDP observer lane but not yet a new browser-proof claim.


## rev0030 memory

- The newest audited baseline before this revision was `GlassTTY-rev0029-2026.03.08.11.15-playwrightsync-packagealign-localproof-orbit.zip`.
- `scripts/cdp_inspect.py` now captures two complementary views of Chromium targets: the familiar HTTP `/json/list` view and the browser-level `Target.getTargets` view from the DevTools browser websocket.
- The raw-browser smoke harness now treats browser-level extension pages or service workers as meaningful visibility evidence, which should make future headless failures less ambiguous.
- In this container, a fresh manual headless-new run proved the extension probe page through both target views, but still did not prove native-host socket availability or a full browser↔CLI round-trip.


## rev0031 memory

- The newest audited baseline before this revision was `GlassTTY-rev0030-2026.03.08.11.35-cdptargettruth-browsergraph-dualprobe-meridian.zip`.
- `scripts/cdp_inspect.py` now has a bounded browser-target watch path driven by `Target.setDiscoverTargets`, so future sessions can preserve transient extension target lifecycle events instead of only snapshots.
- In this container, the new watch path observed a real `Target.targetCreated` event for the unpacked extension probe page, which proves the browser event stream is wired correctly even though the MV3 service worker still was not seen.
- A fresh full `scripts/e2e-fixturelab.py` rerun was attempted for rev0031 but did not leave a usable JSON report here; the focused test slice plus the manual target-watch artifact are the honest release evidence.


## rev0033 memory

- The newest audited baseline before this revision was `GlassTTY-rev0032-2026.03.08.12.37-targetattach-contexttruth-probefusion-quartz.zip`.
- GlassTTY now has an optional hidden offscreen diagnostics document, created through the official MV3 offscreen API and discoverable through `runtime.getContexts()` as `OFFSCREEN_DOCUMENT`.
- The CLI and probe lane can request that offscreen context explicitly (`contexts --ensure-offscreen`, `probe --ensure-offscreen`, or `?offscreen=1` on the probe page), which makes the extension's hidden-context truth less dependent on transient tabs or workers.
- In this container, focused tests, typecheck/build, doctor, and py_compile passed, but three honest raw-Chromium attempts still failed before a stable live offscreen probe target could be listed, so rev0033 is not claiming a stronger live-browser proof than the saved failure artifacts.

## rev0034 memory

- The newest audited baseline before this revision was `GlassTTY-rev0033-2026.03.08.13.24-offscreencontext-hiddenlab-probeflow-lantern.zip`.
- Chrome's current offscreen docs made the next move clearer: offscreen documents are meant for DOM/window work the service worker cannot do, only expose the `runtime` API, and should be checked with `runtime.getContexts()` before creation.
- GlassTTY's offscreen document is no longer just a hidden proof flag. It can now answer a live ping and parse saved HTML into a structured DOM summary with selector counts, headings, and editable-candidate hints.
- The new operator entrypoint is `python -m glassttyd.cli offscreen-dom FILE.html --selector ...`, which routes through `bridge.offscreen_dom` and the hidden offscreen document.
- In this container, the rev0034 evidence is focused tests plus extension build/typecheck; no fresh live Chromium proof of the new DOM lane is claimed.



## rev0035 memory

- The newest audited baseline before this revision was `GlassTTY-rev0034-2026.03.08.13.50-offscreendom-hiddenparser-contextping-cinder.zip`.
- GlassTTY's hidden offscreen document can now do two related jobs: return an enriched DOM summary with base-URL/link/form detail, and build a generic fixture-like capture through the new `bridge.offscreen_fixture` lane.
- The new CLI entrypoint is `python -m glassttyd.cli offscreen-fixture FILE.html --base-url ...`, which keeps the feature operator-facing without requiring a custom UI first.
- In this container, the honest proof is still focused tests plus extension typecheck/build/py_compile. No fresh live Chromium artifact is claimed for the new offscreen fixture round-trip.


## rev0036 memory

- The newest audited baseline before this revision was `GlassTTY-rev0035-2026.03.08.14.12-offscreenfixture-baseurl-fixtureloom-harbor.zip`.
- Hidden offscreen fixture captures now carry richer interaction semantics: recovered control labels, submit candidates, form actions/methods, and a compact semantic outline.
- `scripts/index-fixtures.py` and `scripts/compare-fixtures.py` now surface top input labels, submit labels, first form action, and semantic-outline drift; future sessions should check those before inventing new adapter selectors.
- The archive now includes synthetic semantic-diff artifacts under `validation/latest/semantic-sample/` specifically so future LLMs can see the new richer comparison shape without needing a live browser.
- The honest gap is unchanged: this container still does not provide a fresh live Chromium/native-host/offscreen round-trip proof for the new hidden interaction-model lane.


## rev0037 memory

- The hidden offscreen fixture lane now preserves more accessibility-oriented interaction semantics: `description_text`, `fieldset_legend`, `control_kind`, and submit-control overrides like `submit_action`.
- `scripts/index-fixtures.py` and `scripts/compare-fixtures.py` now surface those fields directly, so future sessions should compare the semantic sample artifacts before inventing new selector heuristics.
- In this container, the honest proof remains synthetic/tool-level rather than live-browser: the new semantics are validated through extension build plus focused fixture-tool tests, not a fresh offscreen browser round-trip.


## rev0038 memory

- The newest audited baseline before this revision was `GlassTTY-rev0037-2026.03.08.15.25-a11ydescriptions-submitoverride-controlmap-aurora.zip`.
- The hidden offscreen fixture lane no longer behaves like a textarea-only heuristic pass: it now includes `<select>` and a wider set of user-editable/choice controls in generic input discovery.
- Fixture captures now preserve `accessible_name`, `form_name`, `option_count`, `option_labels`, and `selected_options`, which is materially better for settings/profile-style flows than raw label/selector hints alone.
- `scripts/index-fixtures.py` and `scripts/compare-fixtures.py` now surface accessible-name drift, form-name drift, and choice-topology drift, and `validation/latest/choice-sample/` plus the paired index/compare JSON files are the quickest artifacts to inspect first.
- The honest proof remains tool-level rather than live-browser: the richer control model is validated through extension build plus focused fixture-tool tests, not a fresh live offscreen browser round-trip.


## rev0039 memory

- The hidden offscreen fixture lane now preserves control-state and constraint metadata such as `checked_state`, `disabled`, `readonly`, `multiple`, `selected_count`, `autocomplete`, `input_mode`, `constraint_hints`, `constraint_flags`, and `choice_group`.
- `scripts/index-fixtures.py` and `scripts/compare-fixtures.py` now surface those signals directly, so future sessions should use them before inventing new ad hoc state-drift notes.
- The synthetic stateful examples live under `validation/latest/state-sample-rev0039/` and are the fastest way to inspect the new shape without a live browser.


## rev0040 memory

- The newest audited baseline before this revision was `GlassTTY-rev0039-2026.03.08.16.02-constraintstate-choicegroup-validitygraph-compass.zip`.
- GlassTTY now has `scripts/plan-fixture.py` and `glassttyd plan-fixture`, which turn one saved fixture into a generic write/read/submit playbook with Playwright-style locator hints.
- The archive tools now surface action kinds and locator-hint drift directly, so future sessions can reason about interaction strategy drift before editing adapters.
- The new planner is intentionally user-facing and role/label/placeholder-first; CSS remains a fallback, not the preferred strategy.

## rev0041 memory

- The newest audited baseline before this revision was `GlassTTY-rev0040-2026.03.08.16.43-locatorplan-rolehint-actionplaybook-sextant.zip`.
- GlassTTY's fixture planner now emits normalized `steps` with stable step IDs, action kinds, locator strategies, value kinds, and assertion hints instead of only free-form locator lists.
- Locator planning now encodes the current cross-tool priority directly: role first when an accessible name exists, then label, placeholder, visible text, explicit name attribute, and only then CSS fallback.
- `scripts/index-fixtures.py` and `scripts/compare-fixtures.py` now surface locator strategies and locator-strategy drift so future sessions can see when a fixture is sliding from semantic selectors toward structural fallbacks.
- In this container the honest rev0041 proof is focused Python tests, extension typecheck/build, py_compile, and fresh synthetic planner-step artifacts; there is still no fresh live Chromium/native-host/browser round-trip claim.


## rev0042 memory

- baseline archive used for this session: `GlassTTY-rev0041-2026.03.08.17.07-actionschema-assertplaybook-querypriority-polaris.zip`
- highest-leverage web takeaways applied here:
  - Chromium native messaging is asymmetric: extension→host requests can be much larger, but host→extension messages are capped at `1 MB`; GlassTTY should budget fixture-shaped envelopes before trying to ship them
  - Playwright's current guidance still strongly favors `getByRole(...)` with accessible names, then label/placeholder locators and auto-retrying assertions
  - MV3 offscreen documents remain runtime-message-oriented hidden DOM helpers, which keeps the saved-fixture/offscreen lane a good long-term lab surface
- code outcome:
  - `glassttyd.protocol` now exposes native-message sizing helpers and a hard oversize guard for host writes
  - `scripts/native_message_budget_lib.py` and `scripts/native-message-budget.py` estimate payload/envelope headroom for fixture JSON
  - `glassttyd native-message-budget` and saved-fixture warnings make message-size risk visible from the CLI
  - `fixture_plan_lib` now turns saved prompt/output evidence into better action/assertion snippets for future adapters
- honest test state:
  - focused protocol/CLI/fixture/dev-tool/validate-release tests passed in this container
  - `scripts/validate-release.py` still stopped early when run as a single long pass here, so rev0042 also preserves a manual focused validation bundle with command outputs instead of pretending the long pass is stable
- unchanged honest gap:
  - no fresh real Chromium↔extension↔native-host round-trip was proven in this container


## rev0043 memory

- The newest audited baseline before this revision was `GlassTTY-rev0042-2026.03.08.18.36-nativebudget-playassert-releasehygiene-wayfinder.zip`.
- Fixture planning is no longer page-flat only. Saved plans can now preserve a locator root such as `page`, `page.getByRole("form", ...)`, `page.getByRole("group", ...)`, or `page.frameLocator(...).getByRole("form", ...)` before generating the final target locator.
- `scripts/index-fixtures.py` and `scripts/compare-fixtures.py` now surface locator-root fields and locator-root drift, which should help future sessions notice when the same control moved into a dialog, group, or iframe.
- rev0043 still does not claim a live browser-sourced scoped fixture or a real browser/native-host round-trip in this container.


## rev0044 memory

- The newest audited baseline before this revision was `GlassTTY-rev0043-2026.03.08.19.06-scoperoot-framelocator-contextplaybook-keystone.zip`.
- The hidden offscreen HTML lane now preserves dialog context (`dialog_name`, dialog role, modal/open hints) on candidate controls and exposes dialog/iframe inventories in summary/fixture metadata.
- The deterministic fixture lab and seeded corpus now include explicit dialog and iframe cases, so future browser-lab work can compare scoped plans against something closer to a real repeated-control/frame surface instead of only hand-authored JSON.
- Honest proof for rev0044 remains focused: extension typecheck/build, focused pytest around planner/index/fixture-lab scope cases, CLI/native-host tests, and saved scoped-corpus artifacts. There is still no fresh live Chromium↔extension↔native-host round-trip claim in this container.


## rev0045 memory

- The newest audited baseline before this revision was `GlassTTY-rev0044-2026.03.08.20.00-dialoginventory-iframelab-scopelab-aurora.zip`.
- Live extension fixture capture now has a shared semantic helper layer in `extension/src/content/generic.ts`; future selector work should prefer extending that shared lane before growing adapter-only metadata islands.
- The deterministic corpus now includes `fixturelab-dialog-live.json`, which is intentionally shaped like a browser-sourced fixture rather than an offscreen one. Use it when checking whether archive tools treat live and synthetic captures consistently.
- `validation/rev0045-focused/compare-live-vs-offscreen-dialog.json` is the quickest artifact for seeing how the new live-like dialog fixture differs from the older offscreen dialog sample.


## rev0050 memory

- The newest audited baseline before this revision was `GlassTTY-rev0049-2026.03.08.22.21-receiverinventory-targetpolicy-multiframe-switchboard.zip`.
- Receiver inventory is no longer only passive telemetry: the side panel and background can now preserve a per-tab receiver override and route content-script messages through that chosen `documentId` / `frameId` target.
- The receiver override is honest about staleness. If the chosen receiver disappears from the current inventory, GlassTTY falls back to the default policy and marks the override `stale` instead of silently pretending the override still worked.
- Live `fixture.capture` responses now record which receiver actually answered, which will matter once future sessions collect real multi-frame browser fixtures instead of only deterministic helper proofs.
