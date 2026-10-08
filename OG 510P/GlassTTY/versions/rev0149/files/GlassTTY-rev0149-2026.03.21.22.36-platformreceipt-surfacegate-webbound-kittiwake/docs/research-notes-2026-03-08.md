# Research notes — 2026-03-08

## Key upstream takeaways

- Playwright’s current Chrome-extension docs say extensions only work in Chromium when launched with a persistent context, and use the `chromium` channel to opt into the newer headless mode.
- Playwright’s `connect_over_cdp()` API docs explicitly warn that CDP attach is lower fidelity than the Playwright protocol connection.
- Playwright’s browser docs show that browser binaries normally live under `~/.cache/ms-playwright` on Linux, and that `PLAYWRIGHT_BROWSERS_PATH` is the supported way to share or override that location.

## What this changed in GlassTTY

1. The smoke harness now has explicit Playwright browser-install discovery instead of assuming the browser bundle exists whenever the Python package imports.
2. `browser_env()` preserves a shared `PLAYWRIGHT_BROWSERS_PATH` into temp-home runs when a real shared cache exists.
3. `doctor.py` now reports whether the current machine has a bundled Playwright Chromium, or only a system-Chromium fallback.
4. The e2e lane now attempts a Playwright persistent-context probe first and only falls back to raw Chromium+CDP when that launch path is unavailable or fails.

## Honest local conclusion

In this container, the Playwright Python package is installed, but no bundled Chromium cache is present. That means the persistent-context lane is conceptually the right one, but any actual launch here currently depends on falling back to `/usr/bin/chromium`, which still needs live proof.

## Additional upstream takeaways for rev0023

- Chrome’s native-messaging docs explicitly distinguish `connectNative()` from `sendNativeMessage()`: the former keeps a host process attached to a live port, while the latter starts a host for a single request/response.
- ChromeDriver’s startup troubleshooting docs warn that running Chrome as root on Linux is unsupported, even though `--no-sandbox` can sometimes be used as a workaround in constrained lab environments.

## What this changed in GlassTTY for rev0023

1. `bridge.probe` now has a truthful fallback: when the persistent native port is absent, it can try a one-shot native bootstrap ping instead of only reporting “not connected.”
2. The probe page now considers that one-shot bootstrap response meaningful native-host evidence, rather than failing every disconnected-but-installed case.
3. `scripts/e2e-fixturelab.py` now records partial native bootstrap evidence separately from full socket/CLI proof.
4. `doctor.py` now surfaces root-account Chromium execution as a meaningful warning, not just an implicit property of the environment.

## Honest local conclusion after rev0023

The product is better instrumented than rev0022: GlassTTY can now separate “native host manifest/launcher works” from “long-lived daemon socket came up.” In this specific container, the latest full browser smoke still failed earlier at extension-page visibility, so the new one-shot native proof path is ready in code and tests but not yet demonstrated by a fresh real-browser artifact here.


## Additional upstream takeaways for rev0025

- Chrome’s native-messaging docs now distinguish Google Chrome, Google Chrome for Testing, and Chromium manifest locations on macOS and Linux, and explicitly note that Chrome for Testing used the same locations as Google Chrome before Chrome 146.
- Chrome for Testing’s own availability page remains the right source of truth for current released versions and download assets, which matters because the native-host-path split now depends on browser version as well as browser family.

## What this changed in GlassTTY for rev0025

1. Browser resolution now carries native-host target semantics with it, instead of leaving the smoke harness to assume `chromium`.
2. `doctor.py` now recommends browser-aware install commands and surfaces the Chrome-for-Testing pre-146 compatibility note directly in its output.
3. The e2e harness now installs the native host into the target(s) implied by the actual chosen browser.

## Honest local conclusion after rev0025

The best new result is conceptual and test-backed rather than browser-round-trip-backed: GlassTTY now stops making the wrong native-host install recommendation for current Chrome-for-Testing builds. In this container the live browser proof is still fragile, but the archive now preserves a simulated doctor artifact showing that a local CfT 136 install correctly maps to the `chrome` native-host target.


## Additional upstream takeaways for rev0026

- Playwright’s current extension docs still recommend bundled Chromium for side-loaded extensions, not branded/system browsers.
- Playwright’s general browser docs and library intro continue to treat `playwright install chromium` as the normal way to provision that browser substrate.
- Chrome for Testing remains the recommended browser family for raw browser automation and remote-debugging scenarios, which is useful for GlassTTY’s raw CDP lane but does not replace the bundled-Chromium requirement for the Playwright extension lane.

## What this changed in GlassTTY for rev0026

1. Playwright browser discovery and launch planning now live in a shared helper module instead of being partially duplicated inside the smoke harness and doctor script.
2. The Playwright persistent extension lane now skips by default when no bundled Chromium cache is present.
3. GlassTTY still preserves a system-browser fallback for experiments, but only behind `GLASSTTY_PLAYWRIGHT_ALLOW_SYSTEM_EXECUTABLE=1`, and the resulting plan is explicitly labeled risky.
4. `doctor.py` and the fixture-lab smoke now expose that launch-plan truth directly, which should reduce false confidence from unsupported fallback runs.

## Honest local conclusion after rev0026

In this container, the best new result is a clearer split between labs rather than a new browser proof. The raw browser lane still resolves to `/usr/bin/chromium`, the Playwright persistent lane now reports `missing-bundled-chromium` by default, and the explicit override artifact proves that the old system-browser fallback is still available when deliberately requested.


## Additional upstream takeaways for rev0028

- Playwright 1.57+ now runs on Chrome for Testing builds rather than older Chromium bundles. The current release notes say headed mode uses `chrome` and headless mode uses `chrome-headless-shell`.
- In this container, `python -m playwright install --dry-run chromium` is enough to reveal the concrete package/install names Playwright expects: `chromium-1208` for the browser package and `chromium_headless_shell-1208` for headless shell.
- Playwright still documents `python -m playwright install chromium` as the normal way to provision that substrate, but dry-run turns out to be a very useful local truth source even when downloads are blocked.

## What this changed in GlassTTY for rev0028

1. Playwright cache discovery is now package-aware instead of version-label-only.
2. Offline archive import and CfT import now prefer the current Playwright install names when dry-run data is available.
3. Doctor and the Playwright-browser inspection CLI now surface the expected package matrix directly, including headless shell.
4. Future sessions can tell whether a cache is aligned with current Playwright package naming before attempting a persistent extension launch.

## Honest local conclusion after rev0028

The strongest new result is not a browser round-trip but a package-truth correction: GlassTTY now knows that current Playwright expects cache directories like `chromium-1208` and `chromium_headless_shell-1208`, and it can seed offline archives into those names. That should make future persistent-lane experiments less ambiguous and less dependent on ad hoc cache conventions.


## Additional upstream takeaways for rev0029

- Playwright's Chrome-extension docs still say extensions only work in Chromium when launched with a persistent context, and explicitly say to use bundled Playwright Chromium rather than branded browsers for side-loaded extensions.
- Playwright's browser-management docs still treat `PLAYWRIGHT_BROWSERS_PATH` as the supported way to share/cache browser packages across runs and machines.
- Playwright Python's `connect_over_cdp()` docs now expose an `is_local` option in v1.58, which is relevant because GlassTTY's CDP observer lane is attaching to a browser on the same host.
- Chrome for Testing's availability data still shows both `chrome` and `chrome-headless-shell` assets per release, which reinforces the value of keeping GlassTTY's package matrix aware instead of assuming a single Chromium payload.

## What this changed in GlassTTY for rev0029

1. GlassTTY now has a single package-sync command that aligns local archives or same-version local Chrome-for-Testing installs with the current Playwright dry-run package names.
2. The sync flow can align both the extension browser package and the headless-shell package in one pass.
3. `doctor.py` now previews that alignment path and recommends the sync command when the persistent Playwright lane is blocked by a missing bundled browser.
4. The Playwright-over-CDP helper now opts into `is_local=True` when the current runtime supports it.

## Honest local conclusion after rev0029

rev0029 makes the Playwright lab more operator-friendly and less network-dependent, but it still does not prove a successful persistent Playwright browser launch in this container. The strongest fresh proof is narrower and honest: local archive fixtures can now be synced into the exact Playwright install names expected here, while the real networked installer still fails on DNS.


## Additional upstream takeaways for rev0030

- Chrome's extension testing docs still explicitly point to `--headless=new` for headless extension loading.
- The DevTools Protocol's `Target` domain is the browser-level source of truth for inspectable targets, and `Target.getTargets` plus `Target.targetCreated`/`targetInfoChanged` are the right primitives when `/json/list` alone is too lossy.
- Playwright's extension docs still revolve around service-worker visibility for MV3, which reinforces the value of preserving worker/page target evidence even in GlassTTY's raw-browser lane.

## What this changed in GlassTTY for rev0030

1. `scripts/cdp_inspect.py` now captures browser-level target truth from the DevTools browser websocket in addition to `/json/list`.
2. The raw-browser smoke lane now treats browser-level extension pages/service workers as real visibility evidence.
3. The validation bundle now includes a fresh manual artifact proving dual-view extension probe visibility in this container.

## Honest local conclusion after rev0030

rev0030 improves diagnostic truth more than product scope: GlassTTY can now prove extension probe-page visibility from two different CDP surfaces in this container. That is stronger than the previous single-surface proof, but it still does not prove the native-host/socket round-trip.


## rev0031 browser-target watch notes

- Chrome's MV3 service-worker docs keep emphasizing lifecycle and suspension rather than steady-state presence, which reinforced that GlassTTY needed a time-aware proof path rather than only a snapshot path.
- Chrome DevTools Protocol's `Target.setDiscoverTargets` and the related `targetCreated` / `targetInfoChanged` events provide exactly that time-aware substrate at the browser websocket level.
- Playwright still documents persistent Chromium contexts as the supported extension lane, but for this container the highest leverage remained better raw-CDP truth, because the persistent Playwright lane is still blocked on a stronger bundled-browser proof.


## Additional upstream takeaways for rev0032

- Chrome's runtime API docs now make `runtime.getContexts()` a first-class way to enumerate live extension contexts, and explicitly define `BACKGROUND` as the service-worker context type.
- The DevTools Protocol `Target.setAutoAttach` docs say it attaches to existing and new related targets, exposes flat `sessionId` routing, and is intended for workers/related targets; `attachedToTarget` is the corresponding event surface.
- Chrome's MV3 lifecycle docs still emphasize that service workers are ephemeral, and selected cases like native messaging and debugger sessions extend lifetime, which reinforces GlassTTY's need for multiple proof surfaces rather than one static target list.

## What this changed in GlassTTY for rev0032

1. `scripts/cdp_inspect.py` now has an auto-attach lane that preserves `attachedToTarget` evidence and lightweight in-target runtime evaluation for extension pages/service workers.
2. The raw-browser smoke/e2e helpers now record attach-derived extension evidence and runtime-id matches when they appear.
3. GlassTTY now has an `extension_context_summary()` helper that lifts `runtime.getContexts()` data into operator-facing proof, especially whether a `BACKGROUND` context was present.

## Honest local conclusion after rev0032

rev0032 strengthens correlation, not end-to-end success: this container now has a fresh manual artifact showing browser-level auto-attach to the unpacked probe page, but the attached runtime evaluation still surfaced `chrome-error://chromewebdata/` and no service-worker target was observed. The new extension-context summarizer is in place for future runs, but this session did not produce a clean probe-context artifact to claim beyond the focused tests.


## Research refresh for rev0033

- Chrome's current offscreen API docs say MV3 extensions can create one hidden offscreen document per profile with `chrome.offscreen.createDocument()`, must declare the `offscreen` permission, and should use `runtime.getContexts({ contextTypes: ['OFFSCREEN_DOCUMENT'], documentUrls: [...] })` to check whether it already exists.
- Those docs also emphasize that the offscreen document is a bundled static HTML page, cannot be focused, and only has the `runtime` API surface. That makes it a good fit for GlassTTY's hidden diagnostics/headless-lab lane, not a replacement for content scripts or the side panel.
- The current runtime docs explicitly enumerate `BACKGROUND`, `OFFSCREEN_DOCUMENT`, `SIDE_PANEL`, and `TAB` as distinct extension context types, which makes offscreen-context reporting a first-class proof signal rather than an ad hoc marker.
- Current MV3 service-worker guidance still says timers are unreliable across worker shutdown and recommends alarms for recurring work. GlassTTY was already on that path, so the offscreen document complements the existing alarms-based worker lane rather than replacing it.
- Playwright's extension docs still point to persistent Chromium contexts as the supported extension path, so the offscreen work is best understood as strengthening GlassTTY's own extension substrate and diagnostics rather than solving the missing bundled-browser proof in this container.

## What this changed in GlassTTY for rev0033

1. The extension manifest now declares `offscreen`, and GlassTTY bundles `offscreen/index.html` plus `src/offscreen/main.ts`.
2. `bridge.probe` and `bridge.contexts` can now ensure that hidden offscreen document on demand, and the CLI exposes the same control with `--ensure-offscreen`.
3. The probe/e2e helper now surfaces `OFFSCREEN_DOCUMENT` counts so future sessions can distinguish hidden extension-context truth from worker truth.

## Honest local conclusion after rev0033

rev0033 improves GlassTTY's hidden-context substrate in a way that is both more product-shaped and better aligned with current Chrome docs. The focused tests and build are green, but three raw-Chromium attempts still failed before a stable live offscreen probe target could be captured here, so the new release preserves that failed evidence instead of pretending the browser proof landed.

## Research refresh for rev0034

- Chrome's current offscreen API docs now say the offscreen document is explicitly for DOM-capable hidden work that the service worker cannot do, only exposes the `runtime` API, allows one open document per profile, and recommends `runtime.getContexts()` as the existence check before calling `createDocument()`.
- Those same docs also document `DOM_PARSER` as a first-class offscreen reason and say multiple reasons are allowed in modern Chrome, which is a useful fit for GlassTTY now that the hidden document is doing more than a proof-only handshake.
- Chrome's service-worker lifecycle docs still note that messages from an offscreen document reset the worker timer, so an active offscreen ping/parse lane is also a better test substrate than a totally passive hidden page.
- This made the next move more product-shaped than the last few proof-only revisions: instead of only asking whether an offscreen document exists, GlassTTY should ask it to do something uniquely suited to a hidden DOM-capable page.

## What this changed in GlassTTY for rev0034

1. The hidden offscreen document now responds to active pings and returns its ready payload instead of only sending a one-time startup message.
2. GlassTTY now has `bridge.offscreen_dom` and `glassttyd offscreen-dom`, which route saved HTML through a browser-native `DOMParser` in the hidden offscreen document.
3. The returned summary is deliberately generic: title, text sample/length, selector counts, heading samples, and editable-candidate hints. That makes it useful for fixture analysis without baking Claude-specific assumptions into the core protocol.

## Honest local conclusion after rev0034

rev0034 improves the hidden offscreen lane enough that it now feels like a reusable lab primitive instead of a passive diagnostics checkbox. The focused tests and build are green, but there is still no fresh live Chromium artifact proving the new offscreen DOM round-trip in this container.



## Research refresh for rev0035

- Chrome's current offscreen API docs still say offscreen documents are the MV3 place for DOM APIs in a hidden document, that only the `runtime` extension API is available there, and that an extension can have only one open offscreen document per profile.
- The service-worker migration docs still explicitly say DOM and window calls should move into an offscreen document and communicate through runtime message passing.
- The runtime docs still treat `OFFSCREEN_DOCUMENT` as a first-class extension context type, which keeps GlassTTY's hidden-context reporting aligned with Chrome's own model instead of inventing a custom status concept.
- Playwright's extension docs still say the supported extension lane is Chromium launched with a persistent context, so this revision remains a product/fixture improvement rather than a claim that the live extension automation problem is solved here.

## What this changed in GlassTTY for rev0035

1. `bridge.offscreen_dom` now accepts an optional base URL and returns link/form samples in addition to the older selector/editable summary.
2. GlassTTY now has `bridge.offscreen_fixture` and `glassttyd offscreen-fixture`, which ask the hidden offscreen document to turn saved HTML into a generic fixture-like capture with candidate hints and HTML samples.
3. The archive docs now treat the offscreen document as a reusable hidden fixture parser, not only a diagnostics page.

## Honest local conclusion after rev0035

rev0035 makes the hidden offscreen lane more obviously useful to the rest of GlassTTY: saved HTML can now be turned into a comparable fixture shape through the extension itself. The focused tests and extension build are green here, but there is still no fresh live Chromium artifact proving the new offscreen fixture round-trip in this container.


## Research refresh for rev0036

- Chrome's current offscreen API docs still say the hidden offscreen document is the MV3 place for DOM work that the service worker cannot do, and that only the `runtime` extensions API is available there.
- Chrome's own extension samples still include an offscreen DOM-parsing example, which keeps reinforcing that saved-HTML analysis is a credible use of the hidden context.
- MDN's current HTML label docs still recommend explicit `for`/`id` association for compatibility, while `HTMLLabelElement.control` provides a browser-native way to recover the associated control when parsing HTML.
- MDN's current `DOMParser.parseFromString()` docs still say HTML parsing yields an inert in-memory document, which is exactly what GlassTTY wants for hidden fixture analysis.

## What this changed in GlassTTY for rev0036

1. The hidden offscreen parser now recovers label-aware prompt candidates, submit candidates, form actions/methods, and a compact semantic outline instead of only text/selector summaries.
2. Offscreen fixture captures now preserve that richer interaction metadata so future sessions can compare saved HTML in a browser-native way before changing live adapters.
3. Fixture indexing and comparison now surface top input labels, submit labels, first form action, and semantic-outline drift, which should make archive archaeology less guessy.

## Honest local conclusion after rev0036

rev0036 is a product-and-archive improvement more than a browser-proof improvement. The offscreen lane is more semantically useful and the fixture tools understand that richer shape, but this container still does not provide a fresh live Chromium/native-host proof for the hidden offscreen round-trip.


## Research refresh for rev0037

- Chrome's current offscreen docs still frame the hidden offscreen document as the MV3 DOM-capable lane for work that cannot stay in the service worker, which keeps GlassTTY's saved-HTML analysis path aligned with the platform rather than inventing a second parsing stack.
- MDN's current `aria-describedby` docs say it establishes a relationship to descriptive text, which makes it a good browser-native hint for richer saved-control semantics beyond short labels.
- MDN's current fieldset/legend docs still say `<fieldset>` groups related controls and `<legend>` captions that group, which makes legend recovery a reasonable generic signal for form intent.
- MDN's current `HTMLButtonElement.formAction` / `formMethod` docs still say submit controls can override their owning form's action and method, so GlassTTY should preserve submit-control overrides instead of assuming the enclosing form tells the whole story.

## What this changed in GlassTTY for rev0037

1. The hidden offscreen fixture lane now recovers `description_text`, `fieldset_legend`, `control_kind`, and submit-control override fields like `submit_action` and `submit_method`.
2. Offscreen semantic outlines now preserve prompt descriptions, fieldset legends, and control kinds in addition to the older label/form/link signals.
3. Fixture indexing/comparison now surfaces those fields directly, so future sessions can inspect interaction drift that is closer to how assistive technology and real form submission logic see the page.

## Honest local conclusion after rev0037

rev0037 is another product-and-archive improvement rather than a fresh live-browser proof. The hidden fixture lane now carries a better generic interaction model and the archive tools can compare it, but this container still does not provide a fresh live Chromium/native-host proof of the richer offscreen round-trip.


## Research refresh for rev0038

- Chrome's current offscreen docs still frame the offscreen document as the MV3 hidden DOM lane, which keeps GlassTTY's saved-HTML analysis aligned with the platform instead of introducing a second parser stack.
- MDN's current `aria-labelledby` docs say it has the highest precedence when browsers compute accessible names, which means GlassTTY should preserve an `accessible_name` signal rather than assuming raw `<label>` text always tells the truth.
- MDN's current `<select>` and `<option>` docs still treat them as standard form controls/options with selected values, and the `multiple` attribute changes the control from a single-choice menu into a multi-select list.
- Those docs together make a strong case that hidden fixture parsing should preserve form choice topology, not just text-box labels.

## What this changed in GlassTTY for rev0038

1. Generic hidden input discovery now includes `<select>` and a wider range of non-hidden input types instead of mostly textarea/text/search.
2. Hidden fixture captures now preserve `accessible_name`, `form_name`, `option_count`, `option_labels`, and `selected_options`.
3. Fixture indexing/comparison now surface accessible-name drift, form-name drift, and choice-topology drift directly, and fresh synthetic choice-sample artifacts live under `validation/latest/choice-sample/`.

## Honest local conclusion after rev0038

rev0038 is a product-and-archive improvement aimed at settings/profile-style forms rather than a fresh live-browser proof. The hidden fixture lane can now model real choice controls more faithfully and the archive tools can compare those signals, but this container still does not provide a fresh live Chromium/native-host proof of the richer offscreen round-trip.


## Research refresh for rev0039

- Chrome's current offscreen docs still frame the offscreen document as the hidden MV3 DOM lane, which keeps GlassTTY's saved-HTML analysis aligned with the platform instead of inventing a second parser/runtime stack.
- MDN's current constraint-validation docs still say form-associated elements expose `checkValidity()` and a `ValidityState`, which means saved HTML parsed in the browser can still reveal whether a control is currently invalid and why.
- MDN's current disabled/readonly docs still emphasize that disabled controls do not participate in constraint validation while readonly controls remain focusable and can still be submitted, so GlassTTY should preserve those states separately instead of flattening them into a single “not editable” guess.
- MDN's current autocomplete, `multiple`, checkbox/radio, and `aria-checked` docs still make it clear that choice controls carry important state/topology beyond raw labels: selected multiplicity, grouping, and checked state all affect how a user can interact with the form.

## What this changed in GlassTTY for rev0039

1. The hidden offscreen fixture lane now preserves control-state and constraint metadata such as `checked_state`, `disabled`, `readonly`, `multiple`, `selected_count`, `autocomplete`, `input_mode`, `constraint_hints`, `constraint_flags`, and `choice_group`.
2. Offscreen semantic outlines now preserve choice groups, autocomplete tokens, state flags, and constraint hints so archive tools can compare them directly.
3. Fixture indexing/comparison now surface those new signals, and fresh synthetic state-sample artifacts live under `validation/latest/state-sample-rev0039/`.

## Honest local conclusion after rev0039

rev0039 is still a product-and-archive improvement rather than a fresh live-browser proof. The hidden fixture lane can now preserve whether controls are operable, selected, and currently invalid, and the archive tools compare those signals directly, but this container still does not provide a fresh live Chromium/native-host proof of the richer offscreen round-trip.


## Playwright locator guidance for rev0040

- current Playwright locator docs recommend prioritizing `getByRole()` and usually pairing it with an accessible name
- the same docs explicitly recommend `getByLabel()` for most form controls and `getByPlaceholder()` when placeholder text is the stable affordance
- this lines up well with GlassTTY's richer offscreen fixture metadata, so a generic fixture planner can stay user-facing and role/label-first instead of collapsing back to CSS

## Research refresh for rev0041

- Playwright's current locator docs still recommend prioritizing user-facing selectors such as `getByRole()`, `getByLabel()`, and `getByPlaceholder()` before falling back to less semantic locators.
- Testing Library's current query docs still point readers to a priority guide centered on semantic queries first, which maps cleanly onto GlassTTY's generic planner problem even though GlassTTY is not a Testing Library project.
- Playwright's current assertions docs still emphasize auto-retrying web assertions like `toBeVisible()`, `toBeEditable()`, `toBeChecked()`, `toHaveValue()`, and `toHaveText()` as the resilient follow-up to locator choice.

## What this changed in GlassTTY for rev0041

1. The fixture planner now emits normalized step objects instead of only target summaries, with stable IDs like `write`, `submit`, and `read`.
2. Each target now preserves prioritized locator candidates, a preferred locator strategy, a value kind, and assertion hints, which makes the saved plan closer to something a future protocol adapter could consume directly.
3. Fixture indexing and comparison now surface locator strategies and locator-strategy drift, which should make archive archaeology better at spotting when semantics are weakening into CSS fallbacks.

## Honest local conclusion after rev0041

rev0041 is a planner/protocol improvement more than a browser-proof improvement. GlassTTY's saved-fixture planner is much closer to an executable action schema, but this container still does not provide a fresh live Chromium/native-host/browser proof of those new steps.


## Research refresh for rev0042

- Chromium's current native-messaging docs still describe an asymmetric size budget: messages from the native host back to the extension are capped at 1 MB, while messages from the extension to the native host can be much larger. That makes host-write budgeting a real product concern instead of a theoretical footnote for GlassTTY.
- The same Chrome docs now document the Chrome-for-Testing user manifest path on Linux, which keeps GlassTTY's Chrome-for-Testing-first installation guidance aligned with current Chromium packaging instead of only classic Chrome/Chromium paths.
- Playwright's current locator docs still recommend role-first, name-aware locators and apply the same model to frame locators, which reinforces GlassTTY's ranked locator-candidate approach.
- Playwright's current assertion docs still emphasize resilient auto-retrying assertions like `toHaveValue()` and `toContainText()`, which makes it worthwhile for GlassTTY to harvest saved expected-value evidence from fixtures when possible.
- Chrome's side panel docs still require user interaction for `sidePanel.open()`, so GlassTTY should keep favoring `openPanelOnActionClick` and operator-driven panel entry rather than assuming background code can always open the panel on demand.

## What this changed in GlassTTY for rev0042

1. The protocol/native-host layer now knows about native-message byte budgets and rejects oversize host writes before they become confusing runtime failures.
2. GlassTTY now has a standalone and CLI-exposed native-message budgeting lane for saved fixtures/corpora.
3. The planner now turns saved prompt/output evidence into stronger `fill` / `innerText` snippets plus concrete `toHaveValue(...)` and `toContainText(...)` hints.
4. Archive packaging/handoff quality improved: focused validation outputs, refreshed memory/worklog docs, and executable-bit repair all ship with rev0042.

## Honest local conclusion after rev0042

rev0042 is still a product-and-archive improvement rather than a fresh live-browser proof. GlassTTY is better prepared for realistic payload sizes and future executable adapter work, but this container still does not provide a fresh Chromium/native-host/browser round-trip artifact.


## Research refresh for rev0043

- Playwright's current locator docs still recommend role/name-first, then label and placeholder, which reinforces GlassTTY's semantic-first planner strategy instead of drifting toward CSS too early.
- Playwright's current frame-locator docs still treat `frameLocator(...)` as the correct entry point for iframe work and emphasize that frame locators are strict, auto-waiting locator surfaces rather than a separate ad hoc API.
- MDN's current HTML docs say `<form>` has an implicit `form` role and `<fieldset>` has an implicit `group` role, while `<legend>` supplies the group label; that gives GlassTTY a standards-backed way to preserve named form/group scope in saved plans instead of only flat element locators.
- Taken together, those docs suggest the next planning upgrade should be scope-aware locator roots, not merely more fallback selectors.

## What this changed in GlassTTY for rev0043

1. The planner now builds scoped locator roots from saved `form_name`, `fieldset_legend`, `dialog_name`, and optional `frame_*` hints before generating element locators.
2. Normalized steps and target summaries now preserve `preferred_locator_root`, `preferred_locator_relative`, `locator_root_strategy`, and full locator-root candidate lists.
3. Fixture indexing/comparison now surface locator-root fields and locator-root drift directly, with fresh scoped-plan artifacts under `validation/rev0043-focused/`.

## Honest local conclusion after rev0043

rev0043 is still a planner/archive improvement rather than a fresh live-browser proof. GlassTTY is materially better at describing where an action lives — page, named form/group, or iframe-rooted scope — but this container still does not provide a fresh live Chromium/native-host/browser round-trip or a browser-sourced scoped fixture.


## Research refresh for rev0044

- Playwright's current docs still push semantic locators first and treat `frameLocator(...)` as the right entry point for iframe work, which reinforces GlassTTY's scope-aware planner rather than encouraging ad hoc CSS once an iframe appears.
- MDN's current dialog docs still frame `<dialog>` as the standards-backed modal/non-modal dialog primitive, which makes dialog-root preservation a better investment than only preserving nearby button text.
- MDN's current accessibility guidance around frame labeling still points to `title` as the practical label surface for frame/iframe elements, which means GlassTTY should preserve iframe title/name inventory if it wants future sessions to reason about frame roots honestly.
- MDN's current form/fieldset docs still support using named forms and legends as meaningful grouping surfaces, so dialog/form/fieldset/frame should be treated as complementary scope layers, not competing heuristics.

## What this changed in GlassTTY for rev0044

1. The offscreen saved-HTML lane now preserves dialog metadata on candidate controls and carries dialog/iframe inventories in DOM summaries and fixture metadata.
2. The deterministic fixture lab and seeded corpus now include explicit dialog and iframe pages/fixtures, which gives future sessions a more realistic scoped corpus for planner/index/compare work.
3. Fixture indexing and comparison now surface dialog-name plus iframe-name/title drift directly, and rev0044-focused validation artifacts preserve those outputs.

## Honest local conclusion after rev0044

rev0044 is a substrate-and-archive improvement rather than a fresh live-browser proof. GlassTTY is better at preserving where a control lives — including dialogs and named frames — and the archive now has better scoped fixtures and validation artifacts, but this container still does not provide a fresh live Chromium/native-host/browser round-trip or browser-sourced dialog/iframe capture.


## rev0045 research note — live semantic parity

- Playwright still recommends semantic locators over CSS/XPath and still treats iframe work as `frameLocator(...)`-first, so GlassTTY benefits when saved fixtures preserve user-facing frame/dialog/form names instead of only CSS hints.
- MDN still documents `<iframe title>` as the primary accessibility label for embedded content, which makes `frame_title` worth preserving as first-class planner evidence rather than an afterthought.
- Chrome's current content-script docs still highlight `all_frames` plus `match_origin_as_fallback` for frame coverage; rev0045 does not enable those yet, but the research raises the priority of deciding whether GlassTTY wants that path for future real iframe captures.
- Outcome: implement the richer live fixture metadata first, then decide separately whether to broaden frame injection policy.

## rev0046 additional upstream takeaways

- Playwright still recommends semantic locators and frame-specific scoping through `frameLocator(...)` rather than flattening iframe content into page-wide selectors.
- Chrome content-script frame policy still leaves `all_frames` and `match_origin_as_fallback` as explicit manifest decisions rather than defaults, which matters now that GlassTTY has stronger iframe evidence but has not yet switched to multi-frame injection.
- MDN still treats iframe access as same-origin constrained and treats `title` as important labeling surface, so preserving both frame path selectors and human-facing frame names/titles is worth the extra fixture bytes.

## What this changed in GlassTTY for rev0046

1. Live fixture capture now descends through same-origin iframes instead of pretending the top document is the whole truth.
2. Fixture metadata/index/compare outputs now preserve iframe path/depth counts directly, not just iframe names/titles.
3. The seeded corpus and fixture lab now include nested iframe cases so future sessions can pressure-test frame-aware planning without needing a live browser first.

## Honest local conclusion after rev0046

The strongest new result is archive-backed and planner-visible rather than browser-e2e-visible: GlassTTY can now capture, index, compare, and plan around nested same-origin iframe context using the live extension schema, but this container still does not provide a fresh real browser/native-host round-trip proof.


## rev0047 additional upstream takeaways

- Playwright's current frame guidance still treats page-level actions as main-frame by default and uses `frameLocator(...)` when interaction moves into an iframe, which makes explicit read-vs-write root divergence important rather than optional.
- Playwright's locator guidance still prioritizes semantic/user-facing locators over brittle CSS, so preserving separate read-side locator roots and text-based output hints is worthwhile when output scope differs from input scope.
- Chrome's current content-script guidance still makes `all_frames` and `match_origin_as_fallback` explicit policy choices, so GlassTTY should preserve split-scope evidence first and only widen injection policy once it has real browser captures that justify the added complexity.

## What this changed in GlassTTY for rev0047

1. GlassTTY can now preserve and compare output scope directly instead of inferring it from the input side.
2. The planner now warns when a read step should not inherit the write root.
3. The fixture lab and seeded corpus now include a deterministic split-scope iframe case for future browser/adapter work.

## Honest local conclusion after rev0047

rev0047 improves the planner/archive substrate for mixed-scope flows in a way that is directly visible in validation artifacts: read-side frame/page roots are now preserved and compared explicitly, and split-scope warnings survive plan generation. This is still not a fresh live browser/native-host round-trip proof.


## rev0048 — partial frame coverage

- Playwright still treats page-level actions as main-frame actions and recommends `frameLocator(...)` for iframe interaction; that makes it important for GlassTTY to preserve not only the chosen frame root, but also whether the frame inventory was complete or partial before trusting a suggested root.
- Chrome extension manifest docs still make `all_frames` and `match_origin_as_fallback` explicit levers for iframe/script reach, rather than something GlassTTY gets “for free” from top-frame injection.
- MDN still documents that sandboxed iframes without `allow-same-origin` are treated as a special origin that fails same-origin checks, which makes them a useful deterministic lab shape for “blocked iframe” evidence.
- MDN also still recommends a `title` on `<iframe>` for accessibility, which makes blocked-frame titles worth preserving even when DOM descent fails.


## rev0049 — receiver inventory before all-frames policy

- Chrome's current manifest docs still make `all_frames` opt-in and keep `match_origin_as_fallback` as a separate choice for related-frame URLs such as `about:`, `data:`, `blob:`, and `filesystem:`; that means GlassTTY should not treat richer frame planning as proof that the extension already has multi-frame receiver plumbing.
- Chrome's current scripting docs still let extensions target all frames or explicit `frameIds`, but not both at once. That makes receiver selection a real policy problem once multiple frame-local content scripts exist in one tab.
- Playwright still treats the page as the main-frame surface by default and uses frame-specific roots for iframe work, which reinforces a conservative top-frame preference unless GlassTTY has stronger live evidence that a subframe receiver should own the request.
- MDN still documents same-origin DOM access limits and `postMessage()` as the cross-origin escape hatch, which is why rev0049 stops at multi-receiver-aware extension state instead of pretending cross-origin child frames are suddenly observable from top-frame DOM descent alone.

## What this changed in GlassTTY for rev0049

1. Supported tabs can now carry multiple observed content receivers instead of one flattened sender snapshot.
2. Bridge targeting/reinjection now run through an explicit receiver-selection policy rather than whichever frame happened to speak last.
3. The side panel, trace log, and validation bundle now make that selection policy visible enough for future browser sessions to audit before turning on broader frame injection.

## Honest local conclusion after rev0049

rev0049 is architecture-first rather than browser-e2e-first: the extension now has a defensible place to store and choose among multiple frame-local receivers, but this container still does not prove a real all-frames browser session or a live multi-receiver GlassTTY round-trip.


## rev0050 — receiver override grounded in Chrome targeting primitives

- Chrome's current `tabs.sendMessage()` docs still allow targeting a specific content-script document or frame via `documentId` or `frameId`, rather than broadcasting blindly to every frame in a tab.
- Chrome's current `runtime.MessageSender` docs still expose `documentId`, `documentLifecycle`, and `frameId`, which means GlassTTY's observed receiver inventory already contains the identifiers needed for an explicit operator override.
- Chrome's current scripting docs still distinguish between `allFrames`, `frameIds`, and `documentIds`, reinforcing that multi-frame behavior should remain explicit policy rather than a hidden side effect.
- Playwright still treats page actions as main-frame actions and frame work as `frameLocator(...)`-scoped, which makes a human-visible non-default frame override more useful than yet another page-global locator heuristic.

## What this changed in GlassTTY for rev0050

1. GlassTTY can now preserve, expose, and honor a per-tab receiver override instead of only a background-selected default receiver.
2. Live fixture captures now record which receiver actually answered, giving future archive analysis a way to distinguish “top frame default” from “operator forced subframe.”
3. The side panel became a real operator-control surface for receiver inventories rather than only a passive status mirror.

## Honest local conclusion after rev0050

rev0050 is still an architecture-and-archive improvement rather than a fresh live multi-frame browser proof. The extension now has a real override lane grounded in Chrome's own document/frame targeting APIs, but this container still does not prove a human- or test-driven multi-frame tab session using that override end to end.


## rev0051 — non-UI receiver audit before broader frame policy

- Chrome's current `tabs.sendMessage()` docs still support sending to a specific `documentId` or `frameId`, and `tabs.connect()` offers the same shape for ports. That means GlassTTY can expose receiver selection directly to operators without inventing a private routing layer first.
- Chrome's current `chrome.scripting` docs still distinguish `allFrames`, `frameIds`, and `documentIds` as explicit targeting choices, which argues for better operator inspection and override first, broader manifest policy later.
- Playwright still treats page actions as main-frame actions and frame work as `frameLocator(...)`-scoped, which keeps receiver choice operationally important rather than cosmetic when a supported tab contains more than one relevant browsing context.
- MDN still documents same-origin DOM limits and `postMessage()` as the cross-origin bridge, so GlassTTY should keep being honest about which receiver actually answered instead of implying whole-tab omniscience.

## What this changed in GlassTTY for rev0051

1. Non-UI automation can now inspect and control receiver choice directly through `glassttyd`, not only via the side panel.
2. Probe artifacts can now summarize the active receiver decision in one compact block (`receiverAudit`) instead of forcing future sessions to inspect raw status state manually.
3. The archive is better positioned for a true live multi-frame proof because the inspection/control tools now exist in both UI and CLI form.

## Honest local conclusion after rev0051

rev0051 is a control-surface and archive-ergonomics improvement grounded in current Chrome targeting APIs, not a fresh browser-e2e proof. The next high-value step is to use the new CLI commands against one real multi-frame tab and preserve the resulting probe/status/fixture evidence.


## rev0052 — receiver frame context before broader frame injection

- Chrome's current `webNavigation` docs still make `documentId`, `frameId`, `frameType`, `parentDocumentId`, `parentFrameId`, and `url` available as first-class navigation truth, and `getAllFrames()` / `getFrame()` require the explicit `webNavigation` permission. That means GlassTTY can enrich receiver inventories with browser-known frame context without pretending content scripts already run everywhere.
- Chrome's current `tabs.sendMessage()` docs still support `documentId` and `frameId` targeting, so the real usability gap is no longer raw routing capability; it is whether operators can pick the right receiver without memorizing opaque keys.
- Playwright still treats iframe work as frame-rooted rather than page-global, which reinforces the value of preserving receiver frame URL/type/parent context in status and fixture metadata before claiming a subframe receiver is the right automation root.
- MDN still documents same-origin access limits for `contentWindow`, which keeps GlassTTY honest: richer receiver frame context is an audit/control improvement, not proof that cross-origin child DOM is now directly inspectable.

## What this changed in GlassTTY for rev0052

1. Receiver inventories, probe audits, and fixture metadata can now preserve browser-sourced frame context instead of only internal receiver keys.
2. Shell automation can now resolve a receiver by human-meaningful frame filters with `glassttyd resolve-receiver`, rather than copying `doc:...` keys out of raw JSON.
3. The archive is now better prepared for a real live multi-frame proof because receiver choice can be explained in terms of frame URL/type/parent context instead of only extension-local identifiers.

## Honest local conclusion after rev0052

rev0052 is still an observability-and-operator-ergonomics improvement, not a fresh browser-e2e proof. The extension now has a stronger browser-grounded story for why a receiver was chosen, but this container still does not prove one live multi-frame tab where the resolver, override, and saved fixture metadata all line up end to end.


## rev0053 research note — receiver ancestry/path context

Current Chrome docs still treat frame identity as an explicit platform concept: `chrome.webNavigation` requires its own permission and exposes navigation/frame metadata including parent relationships, while `chrome.scripting` and `chrome.tabs` still target specific `documentId` / `frameId` values rather than pretending all content-script work is page-global. Playwright still frames page actions as main-frame actions and iframe work as frame-scoped. That combination supports a stronger GlassTTY receiver model where operators and saved fixtures preserve not just receiver IDs and URLs, but the receiver's ancestry through the frame tree.

That led rev0053 to prefer ancestry/path metadata over another shallow filter: GlassTTY now computes `frameDepth`, frame-id/url/host chains, and a human-facing `framePathLabel`, then exposes those through status/probe/side-panel/fixture metadata plus CLI resolver filters. This is a practical operator improvement because it lets scripts choose a receiver by hierarchical meaning (for example, a nested embed under a known shell) without widening extension injection policy yet.

rev0053 is still preparatory plumbing rather than live-browser proof. The archive now has a better model for describing multi-frame receiver choice, but it still needs one real multi-frame browser session where the new ancestry/path filters, override flow, and saved fixture metadata all line up end to end.
