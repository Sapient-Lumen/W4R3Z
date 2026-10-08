# Rev0951 — cloudtainer heart and timely summary honesty

Date: 2026-07-08

This revision is both a deep mission read and a small correctness repair. It does
not claim a new sandbox, full-suite release evidence, or a completed owner graph.
It corrects one evidence artifact that could make an interrupted cloudtainer run
look healthier than it was.

## Executive judgment

The heart of Micromax is **capability-scoped end-user automation**: one small,
inspectable language should be able to configure, script, macro, and extend real
work while the host makes authority, provenance, resource budgets, and cleanup
truth visible. The editor is the first hard host, not the whole product. Its job
is to prove that a calm user-facing tool can still be explicit about effects.

The current project is healthiest when it turns implicit power into a named,
measured, testable seam: filesystem reads, regex work, process output, plugin
metadata, prompt/path scans, retained marks, recent files, prompt history,
clipboard rows, recovery stacks, and generated effect-contract rows all point in
that direction.

The current project is least healthy when it grows more evidence and revision
machinery without shrinking the lived contract. The archive now contains hundreds
of micro-docs, a very large editor coordinator, a large plugin-runtime snapshot,
and increasingly sophisticated local runners. Those are useful only if they keep
telling the truth about what completed, what failed, and what remains partial.

## What is missing

1. **A phase-aware host-effect contract.** The generated effect/resource rows are
a good start, but the product still needs a living contract that says, for each
host effect, whether it is a declaration, reversible session state, document
edit, durable internal state, irreversible external effect, observation, or
resource allocation; which capability gates it; who owns it; what is staged; and
what happens on load failure, callback failure, reload, unload, revoke, timeout,
and crash.

2. **A typed owner graph, not endless field-by-field rollback.** The owner seams
added through rev0950 are useful, but the broad `RuntimeRegistrationSnapshot` and
large `Editor` coordinator still make ownership a distributed proof. Keep moving
families behind public owner methods only when live route tests and generated
rows can prove the behavior.

3. **Evidence artifacts that distinguish partial from passed.** A bounded
cloudtainer lane is valuable, but its JSON handoff must be unable to say `ok`
unless every planned step for that invocation has completed successfully.

4. **Release provenance only when release exists.** Archive-member provenance,
package-input reports, and local summary JSON are useful local evidence. They are
not a signed supply-chain story and should not be made to look like one until a
real package/binary lane exists.

5. **Compaction as product work.** The normal working set should keep shrinking
toward living contracts plus generated ledgers. Historical notes should remain
available, but a new root-level micro-note should not be the default proof of
progress forever.

## What went severely wrong or wasteful

### The survivor loop still dominates design rhythm

The recent sequence is very competent but repetitive: discover one more retained
plugin-owned row, add a sidecar/owner seam, add route tests, add audit and effect
contract evidence, then repeat. This is safer than ignoring the rows, but it is
also proof that the host-effect lifecycle model is still implicit.

### Coordinator gravity is still expensive

Current `mxaudit` output reports `src/micromax_editor/editor.py` as the largest
file, with the `Editor` class spanning tens of thousands of lines and more than a
thousand methods. That is not just style debt; it makes authority review harder.
The correct response remains contract-first extraction, not a broad rewrite.

### The cloudtainer evidence lane could overstate success

In this session, an outer tooltimer stopped `make timely` during the `doctor`
step after context, audit, lint, and portability had completed. The incremental
`.artifacts/mxtimely-summary.json` was fresh, which is better than the stale
rev0924 failure mode, but it still said `"ok": true` while containing only the
completed prefix. That is a serious handoff truth bug: an interrupted five-step
lane should leave fresh **partial** evidence, not a success claim.

### Documentation and evidence are crowding the product loop

The docs/history machinery and test/release runners are now significant systems
in their own right. They are justified only when they keep future turns from
rediscovering the same facts. This revision therefore changes a small executable
truth path instead of adding another broad audit-only essay.

## Online research implications

The external references still support Micromax's direction and also explain why
this repair matters:

- Python documents that `Popen.communicate(timeout=...)` does not kill the child
  automatically; a well-behaved application must kill and finish communication,
  and `communicate()` buffers output in memory. This supports the project's
  emphasis on explicit timeout/output/process-tree evidence:
  https://docs.python.org/3/library/subprocess.html
- Python futures cannot cancel work that is already running, and Python 3.14
  added explicit `ProcessPoolExecutor.terminate_workers()` and `kill_workers()`
  methods. Cancellation and resource release are separate lifecycle facts:
  https://docs.python.org/3/library/concurrent.futures.html
- VS Code Workspace Trust is the right comparison for restricted automatic
  execution, and its own docs warn that it cannot prevent a malicious extension
  from executing code or ignoring Restricted Mode. Micromax should keep this same
  honesty: application-level policy is not hostile-code containment:
  https://code.visualstudio.com/docs/editing/workspaces/workspace-trust
- WASI's capability model starts components with no ambient authority and grants
  only what the host provides. That is a plausible future boundary, but only
after Micromax's hostcall/effect contract is small enough to export:
  https://wasi.dev/
- OWASP API4:2023 lists missing execution timeouts, memory limits, file/process
  limits, upload-size limits, operation counts, record counts, and spending
  limits as unrestricted resource-consumption risks. Micromax's budget work is
  aligned with that guidance:
  https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- Starlark remains a useful neighbor because it is deterministic and hermetic by
  default. Micromax differs in syntax and host, but the lesson is similar: the
  embedded language is only as safe as the host effects it can reach:
  https://starlark-lang.org/spec.html
- SLSA's entry-level provenance is useful for debugging and source/build
  visibility but is not tamper protection by itself. Local zip provenance should
  stay described as local evidence, not release-chain assurance:
  https://slsa.dev/spec/v1.0/levels
- WIT in the WebAssembly Component Model describes interfaces/worlds with types
  and functions. It is an attractive future shape for plugin API declarations,
  but it should follow, not precede, the native effect-contract cleanup:
  https://component-model.bytecodealliance.org/design/wit.html

## Landed change

- `tools/mxtimely.py` now writes `micromax.mxtimely.summary.v3` summaries.
- Summary JSON now includes `status`, `complete`, `planned_steps`,
  `planned_step_count`, `completed_steps`, and `pending_steps`.
- Incremental writes pass the full planned step list, so an outer interruption
  after a successful prefix leaves `status: "partial"`, `complete: false`, and
  `ok: false` instead of claiming success.
- Completed skip-doctor lanes still report `status: "passed"` and `ok: true`
  because their planned step set is only context/audit/lint/portable.
- `tests/test_mxtimely.py` now pins both completed summaries and interrupted
  prefix summaries.
- `tools/mxaudit.py --check` now hard-checks
  `timely_summary_completion_honest` alongside incremental summary persistence.
- The top TODO was compacted by archiving the rev0950 handoff trail into
  `docs/history/TODO-through-rev0950.md`; this keeps the current working file
  under its living-document budget while preserving the old text.

## Validation

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxtimely.py tests/test_mxaudit.py` → 12 passed.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxcontext.py tests/test_revision_index.py tests/test_docs_living_hygiene.py tests/test_effect_contracts.py` → passed when run as focused files in this cloudtainer.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxcontext.py --check` → Rev: 951 and curated handoff entrypoints current.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxaudit.py --check` → release hygiene reports `timely_summary_incremental=True` and `timely_summary_completion_honest=True`.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxlint.py` → `mxlint: ok`.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxportable.py --quiet` → 156/156 portability cases passed.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtimely.py --skip-doctor --summary-json .artifacts/mxtimely-summary.json` → context, audit, lint, and portable passed; summary v3 reported `status: passed`, `complete: true`, and no pending steps for the four planned skip-doctor steps.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxdoctor.py` → doctor preflight passed; warnings were limited to transient caches, optional missing `ruff`/`mypy`, and multiprocessing fork deprecations from the Python runtime.
- A full `make timely` attempt in this ChatGPT cloudtainer was externally stopped during doctor before the code patch. This revision therefore does not claim full `make timely` completion; it fixes the artifact semantics for that kind of stop.

## Remaining risks

- A hard process kill during a step still cannot run final cleanup code; the last
  written summary will be the last completed prefix. The new invariant is that
  this prefix is marked partial unless it equals the planned step list.
- The summary schema changed from v2 to v3. Current in-repo consumers are string
  and field based, but future external consumers should treat unknown schema
  versions as non-release evidence until parsed explicitly.
- The large owner graph, docs volume, and release-provenance gaps remain.

## What should change next

1. Add a tiny `mxtimely --verify-summary` or `mxaudit` payload check that reads
   the actual `.artifacts/mxtimely-summary.json` and reports whether it is a full
   passed lane, a passed skip-doctor lane, or a partial prefix.
2. Continue owner-row consolidation only where tests pin shared behavior first;
   `effect_contracts.py` duplicated owner validation remains a good small target.
3. Decide whether successful plugin option and mark writes need explicit retained
   ownership or should remain committed editor effects.
4. Keep release locks, CI, and signatures deferred until there is a real release
   lane, but do not let local evidence use release-looking language.
