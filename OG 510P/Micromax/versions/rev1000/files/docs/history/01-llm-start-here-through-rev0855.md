# Archived `docs/01-llm-start-here.md` through rev0855

Preserved during the rev0856 mission/context reset. The corresponding living document now contains only current handoff material.

---

Rev0855 note: docs-cues zero-viewport payloads now keep the same metric schema as active payloads; the next docs-cues split should remain preservation-tested.

# LLM start here (rev0855)

Read `TODO.md` and `docs/43-worklist.md` first. The live docs were split from historical revision logs in rev0823; old append-only ledgers are under `docs/history/`.

## Current state

Micromax is a Python reference VM plus a headless/curses editor substrate for capability-scoped editor automation. The current high-risk lane is keeping handoff truth and aggregate evidence current while continuing only narrow runtime seams. Rev0837 reduced evidence waste with chunk-scoped source-dependency digests and curated installed help. Rev0838 keeps the doctor/preflight command from advancing a side manifest, gives the default doctor children bounded failure modes, and prevents budget-limited aggregate resumes from discarding later matching pass evidence. Rev0839 makes manifest summaries point at the earliest incomplete chunks so aggregate resumption is easier to steer. Rev0840 makes doctor timeout cleanup safer by requiring confirmed process-group identity before group signaling. Rev0841 completes the current-source aggregate evidence lane. Rev0842 deliberately paid a runtime invalidation cost to centralize picker prompt refresh mutation behind `prompt_refresh.py`. Rev0843 continues that seam by moving picker query/limit/browse-budget row policy into the same module. Rev0844 moved active prompt-kind guarding into the seam. Rev0845 centralizes active picker refresh dispatch and fixes help link/outline/nav Tab reseeding after suggestions are cleared. Rev0846 removes the separate prompt-complete picker-kind allowlist so picker eligibility follows the active dispatch map. Rev0847 fixes a source-dependency blind spot so Makefile/workflow and pyproject/config-sensitive tests depend on the matching non-runtime partitions, and prevents interrupted resumes from erasing later matching passed chunks. Rev0848 makes the aggregate handoff commands cloudtainer-safe by default: `make test-all-chunks` and `mxdoctor --chunked` now ask mxtest to stop gracefully after 25 seconds unless explicitly overridden. Rev0849 aligns the Makefile `doctor-chunked` target with that lane by forwarding `TEST_MANIFEST` and `MAX_RUNTIME_SECONDS` into `mxdoctor --chunked`. Rev0850 completes that parity by forwarding `MAX_NEW_TESTS`, `MAX_NEW_FILES`, `TEST_BATCH_SIZE`, and `FILE_TIMEOUT` too, so doctor and test-all chunked lanes use the same work slicing. Rev0851 does not change runtime behavior; it fixes stale living-doc claims, brings `mxcontext.py` forward through the latest revision notes and repo map, and records the next waste-reduction/audit seams. Rev0852 adds the missing repo-map freshness guard, makes `mxcontext.py` derive newest revision docs from `docs/revision-index.json`, and extracts shared picker submit target resolution into `prompt_refresh.py`. Rev0853 continues that same runtime seam with a whole-row resolver for helpnav/helpoutline submissions and shared heading-location parsing. Rev0854 keeps the seam concrete by extracting recent/recentdir submit handling and fixing stale-suggestion raw-open fallback in recent-file pickers. Rev0855 makes the first docs-cues cut by centralizing the zero-valued metric schema so zero-sized viewports expose the same keys as active docs-cues payloads without splitting parsing behavior yet.

The archive carries `.artifacts/mxtest-all-64.json` as the aggregate evidence lane. After any runtime/doc/workflow/tooling source edit, verify it with `make test-verify-current`; rev0855 must carry a refreshed current-source result.

## Useful commands

```bash
python tools/mxlint.py
python tools/mxcontext.py --check
PYTHONPATH=src python tools/mxtest.py --manifest-summary .artifacts/mxtest-all-64.json
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q tests/test_mxdoctor.py tests/test_mxtest.py
```

Bounded aggregate progress command:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make test-all-chunks
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make test-verify-current
```

Equivalent explicit command:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py \
  --run-chunks 64 \
  --strategy segment \
  --isolate-files \
  --resume \
  --checkpoint-tests \
  --max-new-tests 120 \
  --max-new-files 8 \
  --test-batch-size 0 \
  --file-timeout 180 \
  --max-runtime-seconds 25 \
  --json .artifacts/mxtest-all-64.json \
  --durations 0
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py \
  --verify-current .artifacts/mxtest-all-64.json
```

## Current refactor map

Recent mechanical splits are already landed: startup, package resources, markdown/docs cues, prompt suggestions, prompt refresh row application, row budgeting, kind guarding, active dispatch, prompt-complete picker allowlist cleanup, and shared picker submit target and row resolution, hostcall/core registries, command families, installed help curation, mxtest source dependencies, doctor handoff/timeout hardening, budget-stop remainder preservation, and manifest-summary next-incomplete reporting.

Next safe code seam: continue with either a tiny palette target-kind helper or a carefully tested `docs_cues.py` model-output-preserving sub-builder split. For evidence work, prefer `make test-all-chunks` or the explicit 64-chunk command with `--checkpoint-tests`, `--test-batch-size 0`, and `--max-runtime-seconds`.

## Current watch-outs

- Source-dependency mapping is heuristic. It is safer and less wasteful than one whole-tree digest, and now includes workflow/test-config sensitivity, but it is not a dynamic dependency tracer.
- Installed help is intentionally curated. Source archives still contain the full docs cube; installed help does not.
- `mxdoctor --full` remains an explicit long lane; the default doctor lane is bounded, `--chunked` uses the handoff manifest, and timeout teardown now avoids blind process-group signaling.


## Rev0855 audit note

The first docs-cues cut deliberately avoided moving parser logic. It fixed a real schema bug: zero-sized docs-cues payloads returned an older top-level counter subset, while normal active payloads returned newer heading-level, fragment-source, fenced-code-role, literal, raw-HTML, and escaped-markdown counters. Rev0855 centralizes the zero-valued metric schema and adds a regression comparing zero-viewport and active key sets. Future docs-cues work should preserve model output first, then extract one sub-builder at a time.

## Rev0854 audit note

The concrete risk in this pass was stale picker authority: with old recent-file suggestions still present, typed unmatched text could be submitted as a raw `open` target. Rev0854 makes recent-file pickers resolve only recent-file truth, shares the recent/recentdir submit body, and adds focused tests for both stale-row re-resolution and unmatched raw-open prevention.

## Rev0852 audit note

The riskiest unfinished item from rev0851 was not another ledger entry; it was the lack of enforcement. Rev0852 adds a focused `docs/02-repo-map.md` freshness test tied to Makefile defaults, removes the newest-revision-doc maintenance burden from `mxcontext.py`, and makes a narrow runtime cut by centralizing picker submit target resolution. Do not expand this into a broad prompt registry unless a focused test exposes a specific duplicate side-effect seam.

## Rev0851 audit note

The severe drift in this handoff was not runtime behavior; it was truth decay in the living repo map. `docs/02-repo-map.md` still described rev0836, a 240-second aggregate command, pending aggregate evidence, repo-wide source attestation, and an uncurated installed-help surface; `mxcontext.py` also stopped at rev0798-era notes, so the context command omitted the newest audit trail. Rev0851 brings those claims back in line with the current Makefile, mxtest manifest, installed-help manifest, and audit findings. Next code work should remain narrow: prompt provider seams, hostcall subfamily splits, and evidence-cost accounting before broad editor rewrites.

## Rev0850 audit note

Rev0849 closed the side-manifest/runtime-budget bug, but it left a subtler same-manifest drift: `make test-all-chunks` and `make doctor-chunked` could still use different new-test budgets, new-file budgets, test batching, and per-file timeouts. Rev0850 pushes the full budget shape through `mxdoctor --chunked` and covers both the command builder and Makefile target. This keeps the two aggregate entrypoints boringly equivalent unless the caller explicitly overrides a knob.

## Rev0849 audit note

The narrow workflow drift was that `make test-all-chunks` respected `TEST_MANIFEST` and `MAX_RUNTIME_SECONDS`, while `make doctor-chunked` invoked `mxdoctor --chunked` with only `--chunks`. That could silently send a custom doctor aggregate run back through the default manifest or default runtime budget. Rev0849 forwards both knobs from the Makefile target, preserving one handoff lane without adding a broader registry.

## Rev0848 audit note

The previous cloudtainer pattern was wasteful: `mxtest` could catch external interruptions, but `make test-all-chunks` still asked for a 240-second run and `mxdoctor --chunked` asked for no graceful aggregate budget by default. Rev0848 makes both defaults 25 seconds so each invocation reaches a planned checkpoint before the surrounding cloudtainer usually intervenes. It also fixes the child-timeout edge exposed by that shorter budget: runtime-budget-derived child stops become checkpointed `not_run` remainders, not real `timed_out` failures. Combined bounded-stop reasons now preserve later matching passed chunks too. Longer local runs remain available with `MAX_RUNTIME_SECONDS=...`, `--max-runtime-seconds 0`, or `MXDOCTOR_CHUNKED_MAX_RUNTIME_SECONDS`.

## Rev0847 audit note

The source manifest already partitioned `Makefile` as `workflow` and packaging files such as `pyproject.toml` as `test-config`, but selected-test dependency inference did not request those partitions. That meant a workflow/config edit could refresh the whole source digest while incorrectly preserving a chunk that actually reads those files. Rev0847 extends token inference and tests the Makefile and installed-resource/package-data cases directly. The aggregate rebuild also exposed an interrupt-stop preservation gap, now fixed so `interrupted-*` stops preserve later matching passed chunks instead of overwriting tail evidence with `not_run`.
