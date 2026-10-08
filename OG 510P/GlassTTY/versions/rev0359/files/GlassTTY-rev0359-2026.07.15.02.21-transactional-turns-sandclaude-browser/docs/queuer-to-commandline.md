# From the userscript queuer to the commandline

The ChatGPT Promptrequest Queuer (v6.46, ~4.8k lines of Tampermonkey + a 448-line
local file server) is the working proof that this workflow is *wanted*. It is
also the working proof that the browser is a hostile place to run it. This
document maps it onto GlassTTY, and is honest about which parts are ported,
which parts are **deliberately not ported**, and which parts are still missing.

## The central claim

**Most of the queuer's complexity is not queue logic. It is the cost of living
inside a browser tab.**

Read the v6.44–v6.46 changelogs: storage offload to disk because dozens of tabs
sharing one origin exhausted localStorage and *broke ChatGPT's own boot*; a DOM
trimmer because the transcript grows without bound; memory thresholds, heap
growth alerts, a frame canary; a "session reset guard"; a nag dismisser;
`pauseWhenHidden` because background tabs get throttled. None of that is the
job. All of it is rent.

A commandline tool does not pay that rent. The prompt queue lives in a file. The
responses live in files. The state lives in a process that no one is scrolling.
So the correct migration is not "port 4,800 lines" — it is "keep the ~15% that is
the actual job, and let the browser tax evaporate."

## Parity map

### Ported in rev0353

| Queuer feature | Commandline equivalent |
|---|---|
| Prompt queue + loop | `glassttyd run queue.txt` |
| `templateVarsEnabled` | `--var KEY=VALUE`, `{{KEY}}` in prompts, per-item `vars` in JSONL |
| `responseCaptureEnabled` | `--out-dir` → `001-name.md` per answer + `transcript.jsonl` |
| `autoContinueEnabled` | automatic; `--no-continue` to disable, `--max-continues N` to cap |
| `stallTimeoutSecs` / `genStallTimeoutSecs` | `--start-grace` (never started) / `--max-wait` (never finished) |
| `minDelay` / `maxDelay` / `jitterPct` | `--min-delay` / `--max-delay` (uniform random between them) |
| Pause / resume | `--resume` — skips turns already settled in `transcript.jsonl` |
| `autoRecoverErrors` (partial) | `--stop-on-error`, plus honest per-turn `settle_reason` to retry on |
| Stats / Full Report | `transcript.jsonl`: `ok`, `settle_reason`, `continues`, `polls`, `elapsed_s`, `detection` |
| Reports-to-disk (v6.46) | every command writes to disk by default; there is no chat paste pipeline to eat it |

### Deliberately **not** ported — the browser tax

| Queuer feature | Why it disappears |
|---|---|
| `domTrimmerEnabled`, `maxVisibleMessages`, `adaptiveTrim*` | Nothing renders a 500-turn transcript. There is no DOM to trim. |
| Storage offload to `queuer-state/*.json` (v6.44) | State is already on disk. There is no localStorage quota to fight ChatGPT for. |
| `memThresholdMB`, `heapGrowthAlertMBmin`, `frameCanary*` | A short-lived CLI process is not a long-lived tab accumulating heap. |
| `pauseWhenHidden`, `suppressAnimations`, `silentAudio` | No tab visibility, no animations, no audio. |
| `nagDismisserEnabled`, `stopOnSessionReset` | Page-chrome babysitting; the adapter's drift gate is the principled version. |
| `mouseSimEnabled` / humanization | GlassTTY submits by clicking the real, verified send control and refuses if the surface drifted. It does not pretend to be a mouse. |
| The 448-line file server | It existed to feed archives *back into the browser*. On the commandline the files are simply… there. |

That is the honest headline: **the majority of your userscript is load-bearing
only for the browser, and the commandline deletes it.**

### Not yet ported — the real remaining work

These are genuine capabilities, not browser tax, and they are the next revisions:

| Queuer feature | What it needs |
|---|---|
| File upload / `additionalPackages` / archive attach | An adapter action to drive the file input; a `--attach PATH` flag on `ask`/`run`. |
| T1/T2 auto-recovery loop (send a package, get a revision back, re-send) | Upload + a settle-triggered download watcher. This is the queuer's crown jewel and it depends on upload. |
| Model / tier / version pinning (`pinModelTarget`, `pinVersion`, "5.6 Sol Pro only") | Adapter support for the model picker and its submenus — the queuer's v6.45 notes are a ready-made spec. |
| Archive download capture (`autoDownloadEnabled`) | A download-completion witness the engine can wait on. |
| `refreshEveryNLoops`, in-place reload recovery | A tab-lifecycle action (reload + re-attach) in the adapter. |

Note the ordering: **file upload unblocks the auto-recovery loop**, which is the
single feature that made the queuer worth 4,800 lines. That is rev0354's job.

## What `run` looks like next to the queuer panel

```bash
# the queuer, minus the browser
glassttyd run prompts.txt \
  --out-dir ./out \
  --var project=GlassTTY \
  --min-delay 30 --max-delay 90 \
  --resume
```

```text
out/001-audit.md
out/002-roadmap.md
out/transcript.jsonl
```

No panel, no session ids, no localStorage, no quarantine directory for 0-byte
zips, no `__resetPkgBaseline()` escape hatch. If a turn fails you get a reason,
and `--resume` continues only after verifying each settled turn's rendered prompt,
name, and attachment content. Submitted-but-unsettled, transport-ambiguous, or
crash-interrupted turns stop for operator inspection instead of risking a duplicate.

## The one thing the queuer had that the CLI must not lose

The queuer's hard-won lesson — encoded in the v6.45/v6.46 changelogs — is that
**a silent success is worse than a loud failure**. An empty zip that was truthy;
a sync that compared `latest === baseline` and skipped; a "current" that was
actually a poisoned baseline.

The conversation engine is built with that lesson in the foreground. A turn that
never started, never settled, or stopped at an un-followed continue gate is
`ok: false` with a `settle_reason` — never a silent success holding partial text.
That is the property to defend as upload and auto-recovery land.
