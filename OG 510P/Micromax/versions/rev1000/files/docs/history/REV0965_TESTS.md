# Revision 0965 validation

## Focused release/provenance slice

The final preflight source passed:

```text
112 passed, 1 expected duplicate-ZIP-member warning
```

The slice covers `mxrepro`, deterministic revision ZIPs, release policy,
context generation, revision/docs indexes, structural audit, and effect
contracts. It includes regressions for compact receipt validation, live-byte
mutation, POSIX file-mode mutation, restrictive-umask snapshot normalization,
workflow least authority/full-SHA pins, wheel verification, and receipt/source
binding.

## Packaging and installed resources

A separate packaging and installed-resource run passed:

```text
3 passed
```

It includes the real wheel build/load test and the installed runtime-resource
journey. The packaging audit also reproduced the prior failure under modern
setuptools before applying the PEP 639 correction.

## Permission reproducibility probe

Before mode normalization, two builds from byte-identical 0644 and 0600 source
materializations produced different wheel SHA-256 digests while every wheel
member payload matched. Forty-nine member external attributes differed.

The first whole-lane `umask 077` run also exposed two unit fixtures that had
implicitly relied on the ordinary process umask. They now establish their valid
0644/0755 starting state before testing byte or permission drift.

After the correction, the release lane is run under caller `umask 077`; its
independent wheel materializations still use the explicit 0644/0755 snapshot
policy. Exact wheel equality and installed-artifact checks are required before
the embedded receipt can exist.

## Final artifact evidence

The final revision archive is produced only by the complete `tools/mxrepro.py`
lane: one capture, focused tests, two independently built and verified wheels,
exact-wheel installation/probe, sealed receipt, two independently materialized
byte-identical archives, and final archive verification. The embedded
`micromax.release-receipt.v1` and manifest are the authoritative per-artifact
hash and phase evidence.

## Scope

No complete repository-suite, cross-platform reproducibility, power-loss,
package signing, public CI execution, publication, SLSA, or hostile-concurrent-
writer claim is made.
