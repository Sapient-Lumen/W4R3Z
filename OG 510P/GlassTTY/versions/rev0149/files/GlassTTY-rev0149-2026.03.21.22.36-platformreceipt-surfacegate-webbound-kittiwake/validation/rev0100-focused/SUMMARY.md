# rev0100 focused validation

- py_compile: passed (`scripts/profile-capture.py`, `scripts/profile_metadata.py`, `scripts/doctor.py`, `scripts/profile-report.py`)
- bash -n: passed (`scripts/glasstty-profile.sh`)
- pytest: passed for the new profile-capture bundle plus updated attach-ready/stale-port/saved-resume/doctor hint surfaces
- extension typecheck: passed
- extension build: passed
- synthetic sample capture bundle: `validation/rev0100-focused/profile-capture-sample/` (generated from a deterministic managed-profile fixture, not a live browser run)
- honest gap: no fresh live browser/native-messaging restart-proof run completed in this container
