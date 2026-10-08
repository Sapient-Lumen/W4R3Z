# Structural audit rev0355

Base: `Global-Warming-rev0354-2026.06.05.23.47-appendchain-timeseal-publicmeeting-refactor.zip`.

## Main change

Added a first-drop media quarantine and malware/active-content intake firewall before live packets can become candidates for adjudication.

## Controls added

- 60 packet-level media quarantine lanes.
- 360 field-kit media-quarantine subdirectories across inbound, safe copy, scan, rejected, candidate and review lanes.
- file-type allow/hold/deny matrix.
- media provenance packet.
- malware/sandbox scan schema.
- archive, macro, metadata, public-context and replay negative controls.
- public-meeting media lockbox.
- SQLite views with 0 public-context-to-local-closure leaks.

## Claim boundary

Media admission, malware scan pass, DLP pass, hash, transcript, recording, attachment, cloud-link capture, phone export, or complete-looking packet is candidate-for-adjudication only. No readiness closure is added.
