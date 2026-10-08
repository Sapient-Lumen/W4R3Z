# 524 — Nuclear Emergency Preparedness KLD/Hancock/Tri-State Source-Clock Refactor — Compact Canon

Rev0317 does not add another broad assurance register. It burns down the two most dangerous open real-public gaps in the Beaver Valley emergency-preparedness pilot: the current evacuation-time-estimate source clock and the Hancock/West Virginia offsite seam.

## Correction made

Rev0316 treated the Pennsylvania public ETE table as source-faithful public context and kept a generic KLD release hold. Rev0317 finds a sharper conflict: the 2025 Ohio REP Plan lists a Beaver Valley KLD Engineering evacuation-time-estimate document dated August 29, 2022, while the Pennsylvania public fact sheet still says the KLD report for ETEs had not been released and would update the table once released. The cube must not pick whichever public row is convenient. It now requires a named KLD/ETE artifact packet, hash, scenario list, source-of-truth statement, and public-safe delta table before any route-capacity upgrade.

## Hancock/WV parity rule

The tri-state EPZ cannot be declared ready from Pennsylvania and Ohio public artifacts. Rev0317 records three facts at once: Pennsylvania has public fact-sheet/mailer context; Ohio has a current public state REP plan and Columbiana County plan context; West Virginia/Hancock still has only a stale support-plan locator, a current WV REP reference in the Ohio plan, and a KI-only public page. That is enough to create evidence demands, not enough to close readiness.

## Hard rule

A public source may discover, contradict, cap, route, or refresh an evidence demand. It cannot close local emergency-readiness evidence without a local packet with owner, date, artifact hash, scope, retest or exercise reference where applicable, corrective-action status, verifier, redaction class, and counterevidence path.

## New operational surfaces

- `cube/nuclear-emergency-bvps-kld-ete-source-clock-reconciliation-rev0317.csv`
- `cube/nuclear-emergency-bvps-kld-ete-packet-requirement-rev0317.csv`
- `cube/nuclear-emergency-bvps-hancock-wv-offsite-packet-gap-rev0317.csv`
- `cube/nuclear-emergency-bvps-tristate-evidence-parity-rev0317.csv`
- `cube/nuclear-emergency-bvps-source-authority-ranking-rev0317.csv`
- `cube/nuclear-emergency-bvps-critical-path-burndown-rev0317.csv`
- `cube/nuclear-emergency-bvps-ete-clock-firebreak-test-result-rev0317.csv`
- `cube/nuclear-emergency-bvps-open-action-workorders-rev0317.csv`
- `cube/datacube-rev0317-emergency.sqlite`

## Claim posture

`REAL_BVPS_PUBLIC_ONLY` remains public-context-only. Rev0317 makes no real Beaver Valley readiness or unreadiness claim. It proves a more useful thing: the cube can find a public-source conflict, sharpen it into packet requirements, and keep the claim blocked until local evidence arrives.
