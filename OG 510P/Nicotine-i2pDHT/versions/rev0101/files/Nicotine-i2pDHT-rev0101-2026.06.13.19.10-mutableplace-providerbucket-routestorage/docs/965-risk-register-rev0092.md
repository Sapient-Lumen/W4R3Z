# Risk register — rev0092

| Risk | Current posture |
| --- | --- |
| Re-entry evidence becomes load permission | `nativeloadreentry.py` accepts request-only and sets native load/dispatch false. |
| Stale native lane evidence is reused | `revalidationseal.py` expires and requires all required lane digests. |
| Native call happens during re-entry | `nativecallhold.py` quarantines any native execution. |
| Python oracle forgotten | Call hold requires Python fallback execution. |
| Restart hides old quarantine/fault memory | All new reports carry tombstone/quarantine/crash/fallback memory. |
| Native branch becomes opaque | `nativefoldspine.py` now includes rev0092. |
