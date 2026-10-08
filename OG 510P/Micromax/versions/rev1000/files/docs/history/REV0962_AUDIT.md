# Revision 0962 audit

## Priority judgment

The plugin-generation journey was complete enough to stop being the critical
path. The highest expected-loss defect was save recovery relying mainly on
same-process exceptions. That evidence could not answer what survives when
Python cleanup never runs.

## Corrected findings

1. **Confidentiality race:** atomic payload temps inherited ordinary destination
   readability before commit. They now begin `0600`; only an empty probe observes
   ordinary create mode.
2. **Durability overclaim:** a single boolean represented a request, file sync,
   and directory sync. Completion witnesses are now separate and real directory
   errors remain visible.
3. **Missing process-death evidence:** named fault points now terminate a fresh
   interpreter with no unwinding and restart classification is asserted.
4. **Worker lifecycle duplication:** parent creation, freshness, and atomic write
   workers joined before result drain and had inconsistent cleanup. One collector
   owns receive, join, timeout, termination, temp cleanup, queue teardown, and
   process close.
5. **Cleanup masking risk:** direct `is_alive()` calls in finalizers could throw
   and obscure both the original result failure and IPC cleanup. Liveness is now
   a non-throwing best-effort probe.
6. **Broken-feeder hang:** after an incomplete or failed queue receive, joining
   the queue feeder could wait on a corrupted/partial publication from a killed
   producer. Abnormal receive paths now cancel feeder joining before close; a
   fully consumed result still receives deterministic `join_thread()` cleanup.

## Cloudtainer evidence and waste

The initial broad save slice exceeded its bounded command window, so validation
was split by behavior rather than allowed to become another abandoned long run.
No orphaned test workers remained. The crash matrix then passed independently on
overlayfs and tmpfs. Temporary pytest roots and bytecode/cache residue are
removed before packaging.

## Residual findings

- Hard process death can strand private temp files. Safe automatic deletion needs
  explicit ownership/lease evidence; indiscriminate startup sweeping would be a
  worse authority bug.
- Atomic commit has an unavoidable syscall window where the new target is `0600`
  before final permissions return. Future recovery metadata should support an
  explicit fingerprint-verified mode repair.
- The direct writer is recoverable but not atomic across process death after
  truncate.
- Filesystem-specific persistence remains broader than this two-filesystem
  process-crash matrix. Controlled power-loss testing is still needed for any
  stronger release claim.
