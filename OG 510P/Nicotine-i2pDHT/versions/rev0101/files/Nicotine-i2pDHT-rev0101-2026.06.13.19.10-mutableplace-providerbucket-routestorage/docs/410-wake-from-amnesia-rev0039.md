# rev0039 wake-from-amnesia

Restart from here:

1. Read `docs/393-rev0039-serviceops-healthdrain-journalfold.md`.
2. Inspect `continuityjournal.py` for restart-memory and hard-negative preservation.
3. Inspect `probeloop.py` for metadata and family-pressure gates.
4. Inspect `successionrepair.py` before changing catalog successor behavior.
5. Run the rev0039 tests and both fold audits before packaging.

Do not treat a healthy probe, a safe drain, or a valid journal record as a universal permission.
