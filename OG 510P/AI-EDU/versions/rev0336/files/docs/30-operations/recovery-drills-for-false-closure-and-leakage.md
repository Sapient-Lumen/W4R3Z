# Recovery drills for false closure and leakage

Negative fixtures show what must fail at import time. Recovery drills show what the maintainer
should do after a false-closure, leakage, stale-evidence, or waiver incident is detected.

A recovery drill is not a simulation result and not a safety claim. It is a rehearsed response path
so the archive does not improvise under pressure.

## Drill states

| Code | Meaning |
|---|---|
| `DR0` | no recovery drills exist |
| `DR1` | incidents are named but not tied to tools |
| `DR2` | detection tools and human artifacts are named |
| `DR3` | pass conditions and closure boundaries are explicit |
| `DR4` | drills are reviewed with release candidate state |
| `DRX` | drill contradicts a validator or permits false closure |

## Minimum drill families

The rev0222 drill packet covers:

- synthetic example misclassified as real evidence;
- protected-route leakage into a public record;
- hidden action authority above the service ceiling;
- public claim beyond evidence grade/source truth;
- stale external source after public-summary publication;
- conflicted or missing signoff quorum;
- policy exception attempting to waive non-waivable controls;
- release audit hash mismatch after packaging.

## Recovery rule

Every drill has the same first principle: restore source truth, protected separation, and public
claim limits before attempting closure. A drill may reopen or downgrade a release. It may not close
`FT-0181` without real source evidence and closeout.

See `examples/recovery-drills/rev0224-ft0181-recovery-drills.json` and
`tools/check_recovery_drills.py`.
