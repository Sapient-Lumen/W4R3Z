# Automated voter-information assistant surface checklist

- State plainly that the assistant helps users find or summarize official election information and is not the standalone authority for jurisdiction-specific rules.
- Publish the official source classes the assistant may rely on for action-changing answers.
- Require explicit official anchors or abstention for dates, hours, locations, ID rules, registration/update paths, absentee deadlines, and high-risk special-case questions.
- Route unanswered or uncertain questions to an official office/help path instead of letting the assistant guess.
- Preserve a clear escalation path for rights, intimidation, accessibility failures, discrimination concerns, or emergency safety issues (`307`).
- Stop on materially conflicting official sources; do not synthesize a confident answer from fragments.
- Record a bounded answer trace for action-changing answers: timestamp, source anchors, policy/model version, answer outcome, and official handoff path.
- Prefer digests and source-anchor identifiers over indefinite storage of raw free-text conversations.
- Publish a minimization rule for personal data and route record-specific matters to official secure channels when needed.
- Treat source, model, prompt, or policy changes that materially affect public answers as change-controlled public-surface updates.
- Check parity between the assistant's guidance and the current official page / signed notice / office directory it depends on.
- Re-test the assistant after major deadline, site, office-hour, or emergency-routing changes.
- Include AI-misuse and bad-answer scenarios in tabletop exercises or other rehearsal work.
- Publish `last_verified_at` for the assistant surface and its current source-anchor policy.
