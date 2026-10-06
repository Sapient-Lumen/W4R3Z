# DeriveBSD rev0521 risk-first host-smoke worker-source audit

Revision: 2026-06-05r554
Package intent: keep the removable-media local fallback lane moving toward a real FreeBSD host proof while correcting evidence paths that could become self-deceptive.

## Highest-risk focus

The first real FreeBSD host smoke will compile and execute the post-detach Capsicum-shaped C worker. Before this cut, the host-smoke path had hardened the fixture tree that becomes the disposable media image, but the checked-in worker source itself was still effectively a live repository path at compile time. That meant a future transcript could prove mount/detach/fd behavior while quietly compiling from mutable live source.

rev0521 changes `tools/freebsd/run_removable_media_local_fallback_host_smoke.py` so the C worker source is admitted as a regular non-symlink repository file, copied into the private work root, rehashed, and compiled from the private copy. The runner fails closed at `worker-source-copy` if the source changes during copy or if the copied source digest diverges.

## Additional command-authority hardening

The host-smoke path now treats host command stdout as authority only after narrow parsing. `mdconfig` and `fstyp` output must be single-line canonical authority tokens before the runner constructs device paths, verifies `ufs`, mounts, or detaches. Malformed `fstyp` output is now covered by `validation/removable-media-local-freebsd-host-smoke.fstyp-output-failure-simulation.json` and fails before mount or worker launch.

Host command rows also bind the sanitized execution envelope: `LC_ALL=C`, a fixed `/sbin:/bin:/usr/sbin:/usr/bin` PATH, command-shape hashes, and private work-root redaction.

## Audit/refactor result

The useful refactor was narrow and implementation-facing: the host-smoke runner now has explicit admission/copy checks for both media fixture input and worker source input, and the checker carries regressions for fixture-copy mutation, directory-aware fixture manifest mutation, worker-source mutation, malformed `fstyp` output, fd-slot identity, and host command redaction.

This cut deliberately avoids adding another broad registry surface.

## Validation notes

The release-critical ledger in `session-reviews/DeriveBSD-rev0521-2026.06.05-release-critical-hygiene-ledger.json` records 35/35 passed rows and was copied to `spec/examples/cube.hygiene.run.ledger.json`. Direct post-copy checks included `check_cube_hygiene_run_ledger.py`, `check_generated_artifact_version_ids.py`, `check_generated_docs.py`, `validate_spec_examples.py`, `check_removable_media_local_fallback_freebsd_host_smoke_runner.py`, `check_removable_media_local_fallback_vertical_slice.py`, and archive hygiene checks.

The cloudtainer still does not claim a real FreeBSD host smoke. The remaining high-risk step is to run this host-smoke path on FreeBSD and bind the compiled C worker binary digest, disposable image/device transcript, real read-only/untrusted mount, real unmount/detach, fd 3/fd 4/fd 5 worker launch, and worker-observed input digest into the same receipt family.
