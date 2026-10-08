# Open-URL process boundary and finite deadlines (rev0977)

Rev0977 takes the roadmap's next-isolation challenge literally: reproduce one
plugin-accessible blocking native path, contain that path through the real
editor journey, and avoid inventing a general sandbox.

## Measured failure

`ed.open-url` is capability-gated and validates the URL, but the product default
still called Python's `webbrowser.open()` directly on the editor/plugin thread.
That is not a finite hostcall boundary. Python's supported documentation says a
Unix text-mode browser blocks the calling process until the browser exits, and
CPython's current implementation contains controller paths that call
`Popen.wait()`.

A real `ed.open-url` regression sets `BROWSER` to a text-mode helper that writes
its PID and sleeps. Before this change, that wait could monopolize the editor
after one Micromax dispatch; plugin fuel could not interrupt it because control
had already entered Python/native host work.

Primary sources consulted:

- Python `webbrowser` documentation:
  https://docs.python.org/3/library/webbrowser.html
- CPython `Lib/webbrowser.py`:
  https://github.com/python/cpython/blob/main/Lib/webbrowser.py
- Python multiprocessing start-method guidance:
  https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods
- Microsoft Job Objects and kill-on-close process-tree ownership:
  https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects
  https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject
- Python command-line isolation (`-I`) and no-site startup (`-S`):
  https://docs.python.org/3/using/cmdline.html#cmdoption-I
  https://docs.python.org/3/using/cmdline.html#cmdoption-S

## Landed owner

The product default now launches one isolated Python child with an absolute
`open_url_child.py` path and `-I -S`. The child alone imports `webbrowser` and calls
`webbrowser.open(url, new=2)`. The parent uses the existing argv process owner:

- no shell interpolation;
- a finite 6-second deadline;
- a 16 KiB combined diagnostic-output ceiling;
- a fresh process group where supported;
- browser stdout/stderr detached to the null device so a successful background
  browser cannot retain the parent capture pipes;
- terminate, then kill, on timeout or output overflow; and
- a boolean hostcall result with the VM/editor still usable after failure.

The explicit `_open_url_fn` seam remains for tests and embedders. Product code no
longer installs the in-process browser function as its default.

The end-to-end timeout test enters through `ed.open-url`, observes failure
within the finite deadline, proves the blocking browser PID is gone on POSIX,
and then executes `1 2 +` in the same VM. A second real background-browser test
proves file descriptors 1 and 2 resolve to the null device rather than the
parent capture pipes. These test post-failure liveness and successful-detach
cleanup rather than only asserting helper arguments.

That success-path test initially found a separate host-dependent delay: on a
desktop-like environment CPython controller registration can invoke
`xdg-settings` before honoring `BROWSER`. The probe took several seconds in
this cloud container. It remains inside the child and therefore under the same
parent deadline. The descriptor regression clears `DISPLAY` and
`WAYLAND_DISPLAY` only so that test measures inherited descriptors rather than
ambient desktop discovery; product execution preserves the real environment. A
second regression installs a blocking `xdg-settings` probe, observes its PID,
and proves the parent deadline tears it down with the helper process group.

## Audit and refactor

The browser path exposed a broader deadline bug. Several process and
multiprocessing helpers accepted malformed booleans, `NaN`, or infinity. Those values can poison
monotonic deadline arithmetic or turn `join(timeout=...)` into an accidental
unbounded wait.

Rev0977 therefore:

- centralizes argv/shell pipe capture, timeout, output-cap, and teardown logic in
  `host_process.py` while preserving the public return-code/diagnostic contract;
- adds one shared finite worker-timeout normalizer and reuses the shared worker
  terminate/join/kill path across filesystem, save, and plugin workers;
- applies finite normalization to filesystem read/list/stat, save freshness,
  parent creation, atomic write, plugin discovery/package capture, shell, and
  external clipboard timing; and
- preserves deliberate direct mode: `None` or a finite non-positive timeout
  still disables the reference worker only on APIs whose contract already
  exposed that escape hatch. `NaN`, infinity, booleans, and malformed values
  fall back to the documented finite default instead.

The generated high-risk effect contract now names `ed.open-url` as an
`external-browser-process` with its live timeout/output budgets and structural
audit flag.

## Deliberately narrow claims

This is availability containment for one measured browser-launch path, not a
hostile-plugin sandbox.

- `Popen` construction happens before the parent has a process handle and is not
  itself preempted by this deadline.
- POSIX process-group and `/proc` descendant cleanup are stronger than the
  current Windows direct-child fallback; Windows Job Object evidence is still
  missing.
- A browser that successfully detaches is intended to outlive the helper.
- The boundary does not filter syscalls, cap total host memory, survive Python
  interpreter corruption, or contain arbitrary native crashes.
- URL validation and `cap.open-url` remain separate authority checks; process
  isolation does not grant permission.

The next isolation step should again begin with a reproducible product/plugin
transcript. Likely high-value residuals are a Windows descendant-cleanup proof,
a concrete `Popen`-startup stall, another plugin-accessible native primitive, or
an actual pre-decode memory failure—not a generic worker registry.
