# Resource pressure proof page — actual bottleneck, budget owner, and degraded claim ceiling

## Purpose

Produce a durable proof object for the current best-supported answer to `what is slowing this down right now?`

This page exists to answer:

- `what is the current bottleneck?`
- `how sure are we?`
- `which competing explanations were examined and rejected?`
- `what stronger statement remains unproven?`

## Required sections

### 1. Bottleneck verdict

Must choose exactly one primary verdict:

- WAN bandwidth cap
- LAN bandwidth cap
- disk service pressure
- CPU / hashing / indexing pressure
- metadata / merge pressure
- memory pressure
- free-space stop
- policy pause / schedule stop
- queue starvation / preemption
- mixed / no dominant bottleneck
- unknown; evidence insufficient

### 2. Evidence bundle

Must show evidence rows such as:

- active rate cap in force
- scheduler cell in effect
- queue saturation
- hidden internal work warning
- disk-priority bias in effect
- thread-count constraint
- free-space threshold crossed
- memory-growth / tree-size warning

Each row must say whether it is:

- direct proof
- supporting signal
- conflicting signal
- stale signal

### 3. Rejected alternatives

Must list at least the top two alternative explanations and why they were not chosen as primary.

### 4. Claim ceiling

Must show one of:

- `high-confidence primary bottleneck`
- `likely bottleneck; mixed pressure remains`
- `plausible bottleneck only`
- `insufficient evidence`

### 5. Strongest safe sentence

Examples:

- `Current slowdown is best explained by scheduled WAN rate limiting, with disk pressure as a secondary factor.`
- `No policy cap is active; current delay is dominated by hidden disk/hash work.`

### 6. Blocked stronger sentence

Examples:

- `The network is definitely the only problem.`
- `Removing this one limit will restore full-speed fairness across all shares.`

## Minimum interactions

The page must expose actions to:

- refresh proof
- open governing budget sheet
- inspect rejected alternatives
- export proof receipt