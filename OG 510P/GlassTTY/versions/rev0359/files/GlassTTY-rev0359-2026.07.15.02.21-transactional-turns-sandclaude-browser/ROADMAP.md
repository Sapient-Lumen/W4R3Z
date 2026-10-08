# Roadmap

## Now

- Keep the ChatGPT-only proof path coherent.
- Make every non-live dry run clearly not-live.
- Make every live path stop before submit if the UI drifted.
- Make the evidence pack mechanically complete before human review.

## Next live-capable step

Run a real side-panel checkpoint attempt and produce:

```text
<downloaded-sidepanel-proof.json>
validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack/
```

Then run:

```bash
glassttyd proof-finalize-pack --input <downloaded-sidepanel-proof.json> --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack --clean --no-placeholder-screenshot --pretty
glassttyd proof-check-pack --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack --require-live --pretty
glassttyd proof-privacy-review --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack --require-live --require-pass --reviewer <name> --decision pass --attest-screenshot-reviewed --attest-no-unrelated-content --attest-local-only --pretty
```

## After first live failure

Do not broaden scope. Use the failed pack/check/evaluator output to fix the narrow missing witness: route, composer readback, gated submit, latest assistant/user turn, same-frame order, same-conversation settled witness, screenshot, or privacy review.

## After first live success

Freeze the exact passing contract, evaluator summary, artifact ledger, and privacy-review-pass output. Only then consider packaging or operator UX cleanup.


## Publish/support bundle and verifier gates

Use `glassttyd proof-publish-bundle` only after a live evidence pack passes `proof-check-pack --require-live --require-privacy-pass`. Rehearsal packs are expected to block and create no publish zip.


## Resumable operator-state reporting and publish bundle verification

Run `glassttyd proof-publish-verify --bundle <publish-zip> --expected-sha256 <hash>` before sharing a support bundle. It extracts the zip safely, verifies manifest hashes, and reruns the live/privacy pack gate.


## rev0346 roadmap adjustment

The immediate product direction is to make the first live attempt boring: run `proof-autopilot`, follow its next action, and only publish after verified live evidence plus privacy pass.

## rev0352 roadmap adjustment

Near-live risk moved from command resumption to browser-side capture durability. The proof helper now has a local recovery vault; next work should validate quota behavior with real screenshots and feed recovery hints into operator status/autopilot.


## rev0352 note

Added static extension readiness (`proof-extension-readiness`) plus side-panel attempt readiness evidence (`proof.operator_readiness`) so the live browser attempt is guided before any download/ingest step.

- Rev0350 product path: make Download proof JSON the safe transfer gate and require attempt-order audit before live ingest.

## rev0353 roadmap correction

The stated purpose of GlassTTY is a generalized commandline tool for working with
ChatGPT. Across rev0300–rev0352 the working tree narrowed to a single-purpose
proof pipeline whose one deliverable has still never been captured. rev0353 does
not delete that lane — it restores the product around it.

### Now

- `ask` / `chat` / `run` exist and are covered end-to-end against `mock-tab`.
- The next work is what makes `run` a true queuer replacement, in this order:

### Next (rev0354): file attachment

`--attach PATH` on `ask` and `run`, driven through an adapter action on the
composer's file input, with an upload-completion witness. This is the blocker for
everything below it.

### Then (rev0355): the auto-recovery loop

The userscript queuer's crown jewel: send a package, wait for the revision to
come back, capture the download, re-send. It needs attachment (rev0354) plus a
download-completion witness. This is the feature that justified 4,800 lines of
Tampermonkey; it is worth doing properly here.

### Then (rev0356): model / tier / version pinning

Adapter support for the model picker and its submenus. The queuer's v6.45 notes
(captured against the live 5.6 menu) are a ready-made spec.

### Standing rule

A turn that did not settle must never be reported as a success. The queuer learned
this the expensive way (an empty zip that was truthy; a sync baseline that skipped
silently). Defend that property as attachment and recovery land.

## rev0354: the surface wing

Shipped. GlassTTY can now watch ChatGPT's UI, notice it change, explain what the
change broke, and patch itself without a rebuild.

### Next (rev0355): file attachment

The single highest-value gap. `--attach PATH` on `ask`/`run`, an adapter action on
the composer's file input, and an **upload-completion witness** (the chip must be
attached before submit, or you send a fileless prompt). Guard zero-byte files: the
queuer's v6.44 incident proves an empty attachment is worse than a missing one.

### Then (rev0356): the auto-recovery loop

Attach a package → wait for the revision → capture the download → re-send. Needs a
download-completion witness. This is the queuer's crown jewel.

### Then: model pinning, conversation control, streaming, parallel workers,
### rate-limit backoff, response fidelity (see docs/missing-features.md).

### Standing rule (unchanged)

A turn that did not settle is never reported as a success. A repair that is not
identified is never applied.

## rev0355: attachments (shipped)

`--attach` works, chunked past the 1 MB bridge limit, with a zero-byte refusal and
a fileless-prompt guard.

### Next (rev0356): the download witness → the auto-recovery loop

The last piece. The engine must wait for the returned archive, verify it is
non-empty (quarantine it if not — port the queuer's logic verbatim, it was learned
expensively), and hand it to the next turn:

```bash
glassttyd loop --package ./Project.zip --out ./revisions/ --max-rounds 20
```

### Then

- Model / tier / version pinning (the composer effort pill is now classified; its
  id is volatile, so drive it by class/text).
- Conversation targeting (`--conversation <id>`), `--stream`, `run --workers N`.
- Rate-limit backoff: `surface-watch` can already see the banner; nothing acts on it.
