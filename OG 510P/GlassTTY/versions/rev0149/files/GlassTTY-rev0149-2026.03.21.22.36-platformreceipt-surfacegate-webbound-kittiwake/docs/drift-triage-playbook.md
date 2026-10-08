# Drift triage playbook

Use this playbook when a workflow that used to work stops working or becomes ambiguous.

## Step 1 — Confirm the symptom
Decide whether the problem is:
- no surface detected
- wrong receiver resolved
- composer unreadable
- write no-op
- submit no-op
- generation state unclear
- latest turn unreadable
- support capture incomplete

## Step 2 — Classify severity
Use the canon severities:
- informational
- low-risk
- degraded
- blocking
- unknown

Do not skip directly to “blocking” when the lane may simply be under-instrumented.

## Step 3 — Capture comparison-friendly evidence
Prefer collecting:
- state snapshot
- probe capture
- fixture capture when DOM drift is suspected
- support bundle or workflow proof
- comparison bundle if a baseline exists

## Step 4 — Localize the likely change
Ask which layer moved:
- route or surface detection
- frame/receiver resolution
- editor model
- submit control
- streaming or turn parsing
- modal/interstitial/auth state
- browser lane or profile assumptions

## Step 5 — Choose the next action class
Typical next actions:
- inspect receiver candidates
- capture fresh fixture
- compare against prior baseline
- widen selector audit without widening default behavior
- downgrade support tier temporarily
- rerun on a better-known lane
- mark record stale pending proof

## Step 6 — Update support truth
A drift incident is not complete until the support record or support matrix reflects the current posture.

## Good outcome
A good drift run ends with:
- a severity
- named artifacts
- a likely affected layer
- a recommended next action
- a support-truth update or pending-update note
