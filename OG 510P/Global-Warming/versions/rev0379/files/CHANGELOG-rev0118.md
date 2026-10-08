# Changelog — rev0118

## Added
- `121-ideal-solutions-five-dispute-resolution-rules-when-readiness-status-is-contested.md`

## Updated
- `58-ideal-solutions-one-page-answer.md` — added pointer to the new readiness-dispute note
- `95-ideal-solutions-question-router-common-prompts-to-best-first-files.md` — added a readiness-dispute routing entry and kept the numbered sequence intact
- `README.md` — updated revision summary and start-here list
- `manifest.json` — advanced revision metadata, archive name, and file list

## Rationale
The readiness cluster had a real remaining front-door gap: it could classify status, upgrade it, downgrade it, and prevent flapping, but it still lacked the shortest rule for what should govern when the status itself is disputed. This revision closes that gap with one compact bridge note instead of another doctrinal branch.
