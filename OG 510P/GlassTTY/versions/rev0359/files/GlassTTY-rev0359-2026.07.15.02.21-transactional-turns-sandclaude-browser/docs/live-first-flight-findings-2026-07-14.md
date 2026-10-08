# Live first-flight findings — 2026-07-14

## Scope

This was GlassTTY's first read-mostly run against a real `https://chatgpt.com/`
tab. The browser was an isolated, persistent Chromium profile launched by
Sandclaude. No canary prompt was submitted.

The final verification used extension `0.1.122` after an explicit unpacked-
extension reload and fresh service-worker start.

## Proven live

- The complete CLI → Unix-socket broker → native host → extension → content
  script → ChatGPT-tab path works.
- The persistent native lane reported `persistent_healthy`; a correlated health
  request returned from `com.glasstty.bridge` in 2 ms.
- Exactly one supported top-frame receiver answered for the active ChatGPT tab.
- Idle and drafted probes both returned coherent snapshots. Draft text was
  restored and never submitted.
- The current root composer can be fully classified with zero unknown composer
  controls after the role-atlas corrections below.
- `first-flight` now exits nonzero when a step fails and writes explicit `ok`,
  `failed_steps`, and `unknowns` fields.

## Live surface corrections

The live page exposed details the offline mock did not:

- upload inputs: `#upload-files`, `#upload-photos`, and `#upload-camera`;
- an idle-only `Start Voice` control;
- Terms, Privacy Policy, and Learn more links rendered inside the composer form.

The legal/help links use exact-text classification. A broad substring matcher
would conceal a future action button containing the same words.

Unknown composer controls must be unioned across idle and drafted phases. The
old first-flight implementation checked only the drafted snapshot and therefore
missed controls, such as Start Voice, that disappear after text is staged.

## Attachment control experiment

The profile was anonymous. ChatGPT visibly offered login/signup and stated that
login was required for file uploads.

Two small-file experiments were compared:

1. GlassTTY's synthetic `DataTransfer` path set `input.files` to one file.
2. Playwright's native `setInputFiles` control path did the same.

Both produced the same result: no upload request and no attachment chip. Both
were cleaned up, leaving `input.files` empty and no filename or chip in the page.
This isolates the current blocker to authentication or server-side UI behavior,
not merely the synthetic file-assignment mechanism.

GlassTTY now records authentication posture in every surface snapshot, reports
anonymous attachment loss as `authentication-required`, and refuses
`--learn-attachment` immediately while logged out.

## Current command result

With the login dialog open, this command was run without `--canary`:

```bash
glassttyd first-flight \
  --learn-attachment validation/live-first-flight-probe.txt \
  --out /tmp/glasstty-first-flight-anonymous-0.1.122.json \
  --pretty
```

Observed result:

- bridge reachable: pass;
- composer fully classified: pass;
- authentication posture: `anonymous`;
- attachment capability: false, cause `authentication-required`;
- attachment-chip observation: fail before file transfer;
- overall `ok`: false;
- process exit status: 1;
- prompts submitted: zero.

## Next live step

1. Complete ChatGPT login in the same persistent browser profile.
2. Rerun the command above without `--canary`.
3. Capture the real attachment chip's stable attributes.
4. Add the chip to the role atlas and mock, rebuild, reload, and rerun.
5. Only then consider one exact canary prompt to prove submit and settling.

## Follow-up worker hardening — 0.1.123

The unpacked-extension path was hardened after the initial `0.1.122` flight.
Builds now require the package and manifest versions to agree and embed that
version in the generated bundles.

A deliberate mixed-build test then loaded manifest `0.1.123` with a temporary
`0.1.122` background bundle. The worker attempted exactly one automatic reload,
remained stable for a further six seconds rather than entering a reload loop,
did not expose a broker socket, and returned an explicit stale-bundle error to
the extension probe. All top-level event handlers remain inactive in that state.

After rebuilding and reloading the genuine `0.1.123` bundle, Chrome showed the
expected version and a live service worker. `bridge-status --wait --timeout 10`
exited zero with one connected broker client, a `persistent_healthy` native
lane, a correlated 3 ms health round trip, and the intended ChatGPT tab selected.
No prompt was submitted and the login form remained empty.

The same live run also exposed a first-flight reporting error: the draft check
was marked failed when send was present merely because anonymous sessions lack
attachment capability. Draft/send verification and baseline eligibility are now
separate. The corrected result reports `submit_prompt=true`, refuses to promote
an anonymous baseline, and identifies authentication as the sole attachment
blocker. The repository suite passes **279 tests** after this correction.
