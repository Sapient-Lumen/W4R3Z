# 565 — End-to-End Adjudication Replay, Claim-Kernel Dry Run, and Manifest Cleanfix

## Compact canon

Rev0358 proves the first-drop evidence path end to end: media quarantine, forensic intake, custody/hash/source-clock checks, adjudication docket, AV/quote provenance, release-egress/DLP, public-statement linting, and the integrated claim kernel.

**Hard invariant:** a file, hash, scan pass, transcript, quote, public-meeting clip, public notice, AAR paragraph, dashboard, PI page, MSEL event, source ID, duplicate URL, local packet candidate, release manifest row, or complete-looking packet can demand, cap, route, contradict, or reopen evidence. It cannot automatically close local emergency-readiness evidence.

## Cleanfix

The selected rev0357 base had a metadata trust defect: root `manifest.json` reported rev0357, while `cube/manifest.json` still reported rev0354. Rev0358 rewrites both manifests, schemas, validation rules, and validation reports to rev0358 and adds root/cube manifest-alignment checks.

## Operational route

```text
exercise/public clock → media quarantine → forensic intake → custody/hash/source-clock gate → adjudication docket → AV quote provenance → release-egress/DLP → public-statement sandbox → integrated claim kernel → CAP/retest/verifier if applicable → release gate
```

No real/anonymized June 2026 Beaver Valley evidence is imported. This is a synthetic end-to-end replay and package-integrity refactor only.
