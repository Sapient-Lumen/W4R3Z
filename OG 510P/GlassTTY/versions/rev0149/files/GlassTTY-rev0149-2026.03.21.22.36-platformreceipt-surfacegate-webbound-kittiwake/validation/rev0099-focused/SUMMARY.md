# rev0099 focused validation

- `python -m py_compile scripts/profile_metadata.py scripts/reopen-profile.py scripts/profile-report.py scripts/doctor.py`
- `bash -n scripts/glasstty-profile.sh scripts/launch-chromium-profile.sh`
- targeted pytest for strict reopen, portable fallback reopen, missing-browser followups, doctor missing-browser hints, and stale-profile attachability
- `npm --prefix extension run typecheck`
- `npm --prefix extension run build`
- `python scripts/doctor.py --pretty`
- `./scripts/package-release.sh REPO_DIR OUTPUT_ZIP`
- `python scripts/verify-package.py OUTPUT_ZIP`
- `python scripts/archive-audit.py REPO_DIR`

All focused checks above passed in this container. Honest remaining gap: no fresh live browser/native-messaging restart-proof run completed here.

Final package was regenerated after the last archive-manifest refresh, and `verify-package-final.json` also passed.
