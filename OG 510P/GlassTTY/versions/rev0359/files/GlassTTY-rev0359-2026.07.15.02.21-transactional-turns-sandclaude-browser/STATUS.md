# Status

- Active provider: ChatGPT only.
- Active host scope: `https://chatgpt.com/*`.
- Extension version: `0.1.126`.
- Daemon version: `0.1.12`.
- Current revision: `rev0359` transactional turns and crash-safe resume.
- Live proof status: not captured yet.
- Surface status: live bridge and root composer measured on 2026-07-14; authenticated attachment chip still unmeasured.
- Active surface contract: `validation/latest/chatgpt-live-surface-contract-rev0352-2026.06.13.json`.

## Most recent product changes

- A failed multi-file or blocked send rolls staged files and command text back to
  the exact pre-command composer baseline. The turn record includes both cleanup
  witnesses; an unverified rollback marks the composer unsafe and fails loudly.
- Normal sends refuse to mix with pre-existing operator files or known chips,
  even when ChatGPT has already consumed the hidden input's `FileList`.
- Turn results distinguish `not-attempted`, `submitted`, and transport-`unknown`
  outcomes. Queue resume never automatically repeats the latter two.
- Queue successes are content-addressed over rendered prompt, name, attachment
  path, size, and SHA-256. Changed queues, variables, or files cannot inherit an
  unrelated successful index.
- A durable in-flight marker closes the process-crash gap between submission and
  transcript append. Response files are written atomically and reconstructed from
  a verified transcript if a completed output file is missing.
- Attachment transfer is preflighted before bytes move, limited to 512 MiB and
  four active transfers, streamed from disk, decoded into one final browser
  buffer, abortable on failure/interruption, and expired after 30 minutes.
- Attachment witnesses use multiset control diffs, a known chip role, or a
  filename that became newly visible. Merely mentioning the filename in a prompt
  or seeing an unrelated new control cannot satisfy the guard.
- Attachment clear now covers every live file input and returns a cleanup witness.
  First-flight blocks its canary unless the input count and composer-control set
  both return to their pre-attachment baseline.
- First-flight never stages a probe over an existing draft, never promotes an
  unclassified/indeterminate-auth baseline, and requires an exact canary answer.
- Composer emptiness accounts for both hidden-input files and visible classified
  chips, so a browser-reset input cannot hide an existing operator attachment.
- The standalone `attach` command now exits nonzero and reports `FAILED` when the
  file moved but no chip was witnessed.
- A self-describing `SANDCLAUDE-BROWSER.json` lets Sandclaude validate and load
  the built extension plus native host before Chromium starts. A desktop handoff
  now consists of the Sandclaude script and one `*-sandclaude-browser.zip`.
- `./scripts/install-sandclaude.sh` persists the native-host manifest after the
  archive is unpacked, while `./glassttyd` provides a dependency-free project CLI.
- `scripts/sandclaude-browser-probe.sh` proves a real extension -> native host ->
  broker round trip; Sandclaude's deep doctor runs it inside the browser boundary.
- The first live, read-mostly flight proved the CLI/broker/native-host/extension/tab
  path without submitting a prompt; current code refuses to promote its anonymous,
  attachment-incomplete surface as a baseline.
- Surface probes now record authentication posture and disable attachment capability
  while ChatGPT visibly presents login/signup controls.
- `first-flight` now checks unknown composer controls across idle and drafted phases,
  reports `ok`/`failed_steps`, and exits nonzero when anything remains unresolved.
- The current root composer role atlas knows the live upload inputs, idle-only Start
  Voice action, and exact legal/help link text observed on 2026-07-14.
- Unpacked-extension builds embed their version; a mismatched stale service worker
  reloads at most once and otherwise fails closed instead of running mixed
  manifest/bundle code.
- All compatibility launchers work under `PYTHONSAFEPATH=1` and `python -S`.

- `glassttyd proof-privacy-review` now writes a structured JSON sidecar and a human-readable markdown review, with explicit pass/fail/pending attestation fields.
- The finalizer now runs privacy review automatically and includes its verdict in the operator handoff.
- `proof-check-pack --require-privacy-pass` can block publication/review flows until `privacy-review-pass` is recorded.
- `glassttyd proof-publish-bundle` now creates a support/publication zip only after live and privacy-pass gates succeed; rehearsals create a blocked summary and no zip.

- `glassttyd proof-publish-verify` verifies a generated support bundle after transfer by extracting it safely, checking manifest-listed file hashes, and rerunning the live/privacy pack gate.
- `glassttyd proof-status` now writes `chatgpt-proof-operator-state.json` and reports the exact next resumable operator step.

- The side panel now captures a real visible-tab PNG into the proof JSON, guarded so it does not silently capture the wrong tab or non-ChatGPT URL.
- The side panel can download the assembled proof JSON and copy it to the clipboard as a fallback; the preview redacts embedded image data so it stays usable.
- `glassttyd proof-ingest` validates downloaded proof JSON integrity, writes a normalized capture, and writes a redacted preview before finalization.
- `glassttyd proof-finalize-pack` now runs export + pack check as one operator-facing gate.
- The finalizer writes `OPERATOR-HANDOFF.md` and `operator-handoff.json` with blocker-specific next actions.
- `--require-live` blocks rehearsal placeholders, 1x1 screenshots, and non-reviewable evaluator verdicts.

## Known live surface facts

- Prompt editor: `#prompt-textarea`.
- Strict send: `#composer-submit-button`, `data-testid="send-button"`, `aria-label="Send prompt"`.
- Known false send: `#composer-plus-btn`, `aria-label="Add files and more"`.
- Current upload inputs: `#upload-photos`, `#upload-camera`, and the general
  `#upload-files` input observed in the live anonymous root composer.
- Anonymous posture: visible `[data-testid="login-button"]` or
  `[data-testid="signup-button"]`; attachments are unavailable in this state.
- Explicit assistant/user author-role nodes are present in the saved known-good reports.

## Still missing

- Real live `GLASSTTY-CHECKPOINT` proof bundle.
- Authenticated first-flight attachment-chip capture.
- Live 30-slot evidence pack.
- Live ledger, schema validation, bundle audit, evaluator output, explicit privacy-review-pass attestation, and publish bundle.


## recent recovery-vault status

The side-panel recovery vault can auto-save, restore, download, and CLI-ingest a recovered full proof document. Preview-only vault records remain blocked.

## rev0352 status

Added `glassttyd proof-extension-readiness` and a side-panel `Run attempt readiness` button. Operators can now verify the unpacked extension/side-panel proof controls before browser work, and the side panel records `proof.operator_readiness` evidence with the next exact action. Extension version is now 0.1.116.

Rev0350 adds a gated Download proof JSON path: the side panel now runs attempt readiness before download and `proof-attempt-audit` verifies the ordered proof event sequence.

## rev0352 status

Added `glassttyd proof-transfer-audit` and wired it into live autopilot before attempt-order audit and ingest. The new gate checks downloaded proof JSON transfer integrity: actions/raw envelopes, sequence indices, attempt IDs, final ready-to-download envelope, and embedded screenshot presence.

## Rev0352 status

Added `proof-pack-integrity`. The immediate bug fixed was stale `artifact-ledger.json` rows after `privacy-redaction-review.md` was rewritten by structured privacy review. `proof-finalize-pack` now refreshes the ledger and writes `evidence-pack-integrity.json` after operator handoff artifacts are emitted.

## rev0353 status — conversation CLI

- Extension version: `0.1.117`.
- GlassTTY now has the layer it was always for: **a conversation loop.**
  `glassttyd ask` / `chat` / `run` send a prompt, wait for the answer to settle,
  and hand back the text.
- New adapter capability: `generation.state` (streaming / needs-continue /
  settled) plus `prompt.continue`. The engine polls the lifecycle instead of
  guessing from transcript-text stability, and degrades to text-stability
  detection (reported as `detection`) when the lifecycle is unavailable.
- New `glassttyd mock-tab`: an offline ChatGPT emulator that stands up a **real**
  broker and plays the tab. The whole conversation stack is now testable with no
  browser, no network, and no ChatGPT account.
- Test suite: **190 passing** (169 prior + 21 new).
- Fixed: `jsonschema` was a hard requirement of the proof lane but was undeclared.
  On a clean install its import guard tripped, `schema_validation_ok` went false,
  and five tests failed with no obvious cause. Now declared in `daemon/pyproject.toml`.
- Hardened: the broker no longer dumps `BrokenPipeError` tracebacks when a client
  disconnects mid-write (the per-request CLI clients do exactly this).

## rev0353 known gaps

- No file upload / attachment action yet — this blocks a commandline version of
  the userscript queuer's T1/T2 auto-recovery loop.
- No model / tier / version pinning yet.
- The live proof capture is still not done. rev0353 did not touch that lane.

## rev0354 status — surface intelligence

- Extension version: `0.1.118`. Test suite: **220 passing**.
- New wing: `surface-snapshot`, `surface-diff`, `surface-triage`, `surface-history`,
  `surface-watch`, `surface-repair`, `surface-overrides`, `surface-scenarios`.
- `ask --diagnose` / `run --diagnose`: a failed turn now probes the live surface,
  diffs it against the known-good baseline, and correlates the two into a cause
  ("submit did nothing because the send button is now X") plus a repair.
- **Runtime selector overrides**: `surface-repair --apply` patches the live adapter
  through `chrome.storage.local`. A drift is fixed without rebuilding the extension.
- **Drift rehearsal**: `mock-tab --drift <scenario>` simulates 8 UI failures
  (send renamed/removed, decoy send, composer gone, nag dialog, rate-limit banner,
  new composer control, no generation signal). Mock *behaviour* is derived from the
  same capability map its probe reports, so it cannot look broken while secretly working.

## rev0354 safety properties

- An override is a **hint, not a bypass**: an overridden node still passes the same
  send-intent scoring. A wrong override degrades to the normal search and can never
  cause a click GlassTTY would otherwise refuse.
- A repair is only auto-applied when the replacement is **positively identified**.
  Non-controls are disqualified outright; attach/dictate/picker roles are
  disqualified outright. Under `decoy-send` the engine proposes nothing and stays broken.
- Transient anchors (`generation_stop`/`continue`) and transient capabilities never
  produce findings — a false-positive drift detector is one that gets ignored.

## rev0354 known gaps

See `docs/missing-features.md`. The headline: **file attachment** is still absent
and it blocks the queuer's T1/T2 auto-recovery loop.

## rev0355 status — attachments + live-surface corrections

- Extension `0.1.119`. Test suite: **239 passing**.
- **File attachment** (`--attach` on `ask`/`run`, plus a standalone `attach`).
  Files are written straight into the composer's hidden `<input type=file>` via a
  synthetic DataTransfer. Chunked at 384 KB to cross Chrome's 1 MB native-messaging
  ceiling — no local HTTP server, unlike the userscript queuer. Verified with a
  12 MB payload (31 chunks, byte-exact reassembly).
- **Zero-byte refusal** and **fileless-prompt guard**: GlassTTY polls for the
  attachment chip and refuses to submit if it never renders. `--no-require-attachment`
  overrides.
- New: `glassttyd stop` (abort a generation — the adapter could always find the
  stop control, nothing ever called it) and `glassttyd new-chat`.
- New: `surface-triage --probe-with-draft` / `surface-snapshot --probe-with-draft`.

## rev0355 corrections from the live 2026-07-11 surface report

Two shipped bugs, both found by reading a real capture. See
`docs/live-surface-findings-2026-07-11.md`.

1. **Send is hidden, not gone, on an empty composer.** The live page shows ZERO
   matches for `#composer-submit-button` while being perfectly healthy; the old
   contract called that `surface-drift-blocker`. Capabilities are now tri-state
   (`true`/`false`/`null`); `null` is never reported as damage.
2. **Volatile framework ids.** 65 `[id^="radix-"]` nodes; they change every load.
   rev0354's repair engine would have persisted one as an override. Volatile ids
   and structural paths are now rejected as selectors, and a repair with no durable
   selector can never be confident.
3. Send-replacement scoring inverted: only a *confirmed* send or an honest unknown
   may stand in for send. Enumerating bad roles meant every new ChatGPT control was
   a fresh hole — the live composer's effort pill sailed straight through.

## rev0356 — handoff to the commandline and first live flight

- Extension `0.1.123`. Test suite: **279 passing**.
- New `glassttyd first-flight`: measures a REAL ChatGPT tab against GlassTTY's
  assumptions. Read-mostly (only submits with `--canary`). Probes idle, then with a
  draft, promotes a baseline, lists unclassified composer controls, and — with
  `--learn-attachment` — **discovers the attachment-chip selector**, which nobody has
  ever captured.
- `CLAUDE.md` at the repo root: invariants, ChatGPT facts learned the hard way, and
  the warning that the mock encodes assumptions rather than reality.
- `docs/first-flight.md`: ordered runbook + a ranked risk register for first contact.
- Fixed (found by first-flight running against the mock): the prompt editor was
  classified `unknown`, so every healthy composer reported an oddity; and the mock's
  attachment witness returned a chip count without the control descriptors, so it
  could not have identified a chip it had just seen.
- Live 2026-07-14 result: correlated native health and idle/drafted probes
  succeeded, and the corrected composer has zero unknown controls. An anonymous
  attachment attempt correctly produced no upload/chip; current code detects that
  state before attempting the file and does not promote it as a healthy baseline.

## rev0357 — automatic Sandclaude browser handoff

- Extension `0.1.124`. Test suite: **281 passing**.
- The release archive carries a strict browser-bundle descriptor. Sandclaude can
  preload the extension and matching native host from the archive itself, so an
  agent does not need to drive Chrome's native "Load unpacked" folder picker.
- `./scripts/install-sandclaude.sh` replaces the temporary native-host path with
  the unpacked project path. `./glassttyd ping` is the first local health check.
- The ordinary browser and GlassTTY safety models are unchanged: the browser owns
  its isolated profile and unrestricted network, while project source remains
  read-only to the browser process tree and writable to Claude through Sandclaude.

## rev0358 — fail-closed attachment lifecycle

- Extension `0.1.125`, daemon `0.1.11`. Test suite: **297 passing**.
- File bytes no longer cross the bridge until the tab proves authenticated and
  exposes an upload input. Unknown authentication fails closed.
- The Python sender keeps one 384 KiB chunk in memory rather than the whole file;
  the content script decodes directly into its final buffer instead of materializing
  every decoded chunk plus a concatenated copy.
- Transfer ids, sizes, counts, indices, and chunk envelopes are bounded. Failed or
  interrupted transfers are aborted; abandoned buffers expire independently.
- Repeated controls are diffed as a multiset, so a second identical chip remains
  observable. Filename evidence must be newly visible after attachment.
- Cleanup is a measured step. A sticky chip is a hard first-flight failure and
  blocks the optional exact canary from submitting.

## rev0359 — transactional turns and crash-safe resume

- Extension `0.1.126`, daemon `0.1.12`. Test suite: **310 passing**.
- Attachment sends now have an explicit transaction boundary. Partial staging,
  missing chips, blocked submits, and unknown submit replies trigger witnessed
  file and composer-text rollback; cleanup failure remains visible in the
  structured turn result.
- A send refuses pre-existing input files and classified chips rather than
  silently combining operator state with command-owned files. The content script
  also rejects attachment state that changes during a chunked transfer.
- `run --resume` verifies content-addressed inputs and blocks submitted or
  ambiguous failures. A durable in-flight marker prevents a process death after
  submit from becoming a duplicate prompt on restart.

## Standing risk

The bridge and read-mostly surface path are now proven on a live ChatGPT tab. Prompt
submission, answer settling, and authenticated attachment remain unproven on that
live profile; offline coverage cannot close those gaps. `first-flight --canary`
must remain an explicit operator choice. Chrome/Chromium only.
