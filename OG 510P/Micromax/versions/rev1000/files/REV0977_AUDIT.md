# Rev0977 audit — browser-process containment and finite deadlines

## Highest-risk finding

The roadmap asked for one real plugin-accessible primitive that existing fuel,
preflight, and regex containment could not own. `ed.open-url` supplied it. The
hostcall was capability-gated and URL-validated, but the product default called
Python's `webbrowser.open()` on the editor/plugin thread. Python documents that a
Unix text-mode browser can block the calling process until browser exit. Once VM
dispatch entered that call, plugin instruction fuel no longer advanced.

A real hostcall test selects a text-mode `BROWSER` helper that records its PID and
sleeps. The reproduced wait was therefore a product failure, not a theoretical
API concern or a helper-only benchmark.

## Substantive correction

The product default now starts an absolute `open_url_child.py` through
`python -I -S`. The child alone imports `webbrowser`; the parent applies the shared
argv-process boundary: six seconds, 16 KiB of combined diagnostics, a fresh
process group where supported, and terminate/kill teardown. URL authority and
validation remain in the editor. The hostcall still returns a boolean.

The end-to-end timeout regression proves that the browser PID is gone on POSIX
and that the same VM executes subsequent code. A second process-owner test
proves a descendant that creates its own POSIX session is still found through
Linux `/proc` and terminated at the deadline. Another real background-browser
regression found and closes a successful-path leak: a detached browser could
inherit the helper's captured stdout/stderr pipes and keep reader threads alive
until browser exit. The child now temporarily maps descriptors 1 and 2 to the
null device while launching; the regression inspects the browser's actual
`/proc` descriptors.

The successful-path regression also exposed a host-dependent desktop discovery
delay: CPython may invoke `xdg-settings` while registering controllers before
it consults the requested browser. That platform probe is intentionally inside
the bounded child too. The descriptor test clears display variables only to
isolate pipe ownership; the product preserves the caller environment and lets
the parent deadline contain controller discovery as well as browser waiting. A
separate executable regression supplies a blocking `xdg-settings`, observes its
PID, and proves that discovery process is gone after the parent deadline.

## Audit/refactor

The process work exposed a second cross-cutting defect: several timeout
producers accepted malformed booleans, `NaN`, or infinity. Those values can
invalidate monotonic deadline comparisons or turn `join(timeout=...)` into an
accidental unbounded wait.

Rev0977:

- extracts one shared subprocess capture loop for argv and shell execution while
  retaining exact public return-code and diagnostic behavior;
- reuses one multiprocessing terminate/join/kill helper in filesystem, save,
  and plugin workers;
- adds one finite worker-timeout normalizer and applies it to filesystem
  read/list/stat, save freshness, parent creation, atomic write, plugin discovery
  and package capture;
- rejects malformed, boolean, and non-finite shell and hostcall deadlines and
  rejects non-finite external-clipboard deadlines; and
- preserves deliberate direct mode only for finite non-positive values or a
  declared `None` escape in APIs that already exposed it.

The generated high-risk effect contract and structural audit now name the
`ed.open-url` process owner and the finite-deadline normalization seam.

## Waste removed

- no browser-controller wait on the editor/plugin thread;
- no successful detached browser retaining captured pipes;
- no duplicate argv/shell pipe, deadline, output-cap, and teardown loops;
- no duplicate filesystem/save/plugin worker kill sequence;
- no malformed boolean, `NaN`, or infinity as an accidental
  “disable timeout” value; and
- no generic sandbox, browser registry, worker registry, or process/Wasm host
  added without a second measured failure.

## Residual risk

The parent deadline starts after `Popen` returns because no child handle exists
before then. POSIX process-group plus `/proc` descendant evidence is stronger
than the current Windows direct-child fallback; no Windows Job Object claim is
made. A successfully detached browser is an intentional external effect. The
helper does not sandbox browser code, filter syscalls, cap total memory, survive
interpreter corruption, or contain arbitrary native crashes. The next boundary
should again begin with an executable product/plugin transcript.
