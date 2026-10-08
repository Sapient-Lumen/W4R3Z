# Cloudtainer quiescence record

An abandoned `/tmp/anonsync-r0840-BaqqwP` command left a watchdog that scanned process
arguments and sent SIGTERM to groups mentioning `/tmp/anonsync-r0840/build-debug`.
Consequently, two otherwise progressing CTest commands ended at tests 13 and 42.

The exact stale process group and command line were observed with `ps`, terminated, and
confirmed absent. Partial and overlapping logs are not used in the release count. The
final 132 tests were executed in nine complete, exact, non-overlapping index ranges over
one immutable build. `gcc14-debug-final-quiescent-build.log` then records `ninja: no work
to do.`

This is operational evidence, not an application defect. Future revision automation
should use unique roots, process-group ownership, no path-matching kill loops, immutable
validation roots, and explicit quiescence checks before sealing.
