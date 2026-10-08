# 564 — Nuclear emergency preparedness: adjudication docket, AV quote provenance, and run-provenance refactor

## Why this revision exists

Rev0356 proved that a first-drop forensic intake CLI can classify payload-like files without creating a readiness claim. The remaining dangerous shortcut is the next handoff: an operator or reviewer may treat *candidate for adjudication* as *accepted evidence*, treat a public-meeting quote as a finding, treat a transcript as the source of truth, or trust a tool output without preserving the tool/run provenance that produced it.

Rev0357 adds the second-stage evidence firewall:

`forensic dropbox result → adjudication docket → two-reviewer evidence screen → AV/transcript quote provenance gate → tool/run provenance ledger → candidate-only release to claim kernel`

## Hard rule

A forensic intake result, candidate lane, adjudication docket row, reviewer note, AV recording, transcript, timecode, quote, content-credential assertion, media-forensics score, tool-run hash, public notice, public meeting statement, preliminary finding, AAR paragraph, dashboard, PI page, MSEL event, extent-of-play statement, source ID, duplicate URL, or complete-looking packet can demand, cap, route, contradict, or reopen a claim. It cannot automatically close local emergency-readiness evidence.

## What is now first-class

1. **Adjudication docket:** every rev0356 smoke-test intake row is routed to a human-review state that preserves rejected, hold, candidate, reopen, and context-only outcomes. None of those states closes readiness.
2. **Promotion gate:** each of the 60 must-capture packets now has a promotion state. The default remains loss-capped until a real or anonymized local packet is adjudicated, verified, and linked to CAP/retest where applicable.
3. **AV/transcript quote provenance:** public-meeting video, audio, transcript, quote excerpts, speaker identity, timecodes, corrections, and synthetic-media/deepfake flags are treated as provenance inputs, not performance proof.
4. **Tool/run provenance:** the scripts that classify or validate evidence now need their own hash, run ID, input hash set, output hash, operator, and claim boundary.
5. **Fork hygiene:** the cloudtainer contains a sibling rev0356 AV/transcript fork. Rev0357 records it and merges the useful theme as new canonical tables without copying the conflicting numbered canon.

## Non-claim boundary

No real Beaver Valley exercise packet is imported in this revision. Rev0357 improves the path from first-drop intake to adjudication and public-meeting quote control. It does not claim any site, jurisdiction, ORO, evaluator, controller, alerting authority, EOC/EOF/JIC, or facility is ready, unready, passed, failed, green, safe, sufficient, reasonable-assurance-ready, demonstrated, released, or closed.
