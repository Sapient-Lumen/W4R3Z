# 863. Release-builder negative-control runtime and rebuild-probe refactor

**Track:** Shared / Release engineering / Gate reliability
**Status:** v855/v856 release-gate coherence repair

rev0850 also fixes a release-gate reliability problem that had become operationally risky: filesystem-policy negative controls were exercising the full cube repeatedly when most probes only needed builder semantics. That made `scripts/check_release_builder_filesystem_policy.py` vulnerable to long runtime or apparent hangs in this cloudtainer, especially during symlink/special-file negative controls.

The check now uses tiny synthetic release roots for symlink, FIFO, unsafe-path, source-swap, parent-swap, and output-route probes. The real archive still has its manifest and release ZIP verified by the normal manifest/ZIP checks; the negative controls no longer need to hash or package thousands of unrelated files just to prove fail-closed filesystem behavior.

Measured result in this cloudtainer:

```text
check_release_builder_filesystem_policy.py: PASS
observed runtime after refactor: about 5–7 seconds
```

The rebuild-from-extract probe was also adjusted so a rebuilt ZIP that is byte-identical to an already verified fresh ZIP does not receive a redundant second full verifier pass. Its scratch cleanup is best-effort and outside the archive root so a slow local `rmtree` cannot turn a completed byte-reproducibility verdict into a release-gate timeout.

Boundary: this is a release-gate runtime/refactor fix. It does not change the synthetic-only posture, does not prove production signer authority, and does not authorize current voter instruction, certification, legal reliance, or a live pilot.
