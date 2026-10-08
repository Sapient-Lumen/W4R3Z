# Source-family signal triage

Rev0008 recognizes six source-signal families:

1. DOJ source-page status labels.
2. Official DOJ press releases.
3. Court orders and judgments.
4. Motions, responses, and party requests.
5. Closing letters and agreement-completion letters.
6. Local/monitor/assessment carriers.

Only court orders or verified docket entries can support court-effect atoms, and even those atoms remain noncurrent until freshness checks are complete. Press releases can trigger acquisition tickets. Source-page labels can trigger resnapshot rows. Neither becomes a public status banner on its own.

The most dangerous mistakes this prevents are treating a motion as an order, treating a press release as a docket, treating a stale page label as current status, and treating closure/completion/retraction as deletion of history.

