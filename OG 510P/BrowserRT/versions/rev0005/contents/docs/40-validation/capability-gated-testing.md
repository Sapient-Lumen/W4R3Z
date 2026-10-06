# Capability-gated testing

Revision: rev0005.

BrowserRT will target capabilities that are not uniformly available in every
browser or cloudtainer environment. The test facility must separate three cases:

1. capability absent and correctly reported absent;
2. capability present and smoke test passes;
3. capability present but provider path fails.

A skipped capability test is only acceptable when the skip is explicit, traced,
and tied to a capability report. Silent skips are forbidden.

Future browser slices should begin with capability reports before they run OPFS,
SAB, WebGPU, OffscreenCanvas, media, or mesh checks.
