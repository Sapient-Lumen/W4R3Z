# Delegation Power Model

## Purpose

Define the current planning posture for looper power inside the house.

This room exists because "power" is too coarse by itself.
The house needs a truthful way to say:

- who may decide,
- who may technically touch the machine,
- who may coordinate with whom,
- and whose outputs may become action without another layer of review.

Nothing here is immutable canon.
It is the current planning stance for a house that is still being built.

## Thesis

Do not collapse looper power into one scalar clearance level.

The house should separate at least four axes:

1. `authority`
   - what a worker is allowed to decide or mutate for its mission
2. `capability`
   - what the worker can technically read, write, invoke, or control on the host
3. `coordination`
   - whether the worker acts alone, reviews peers, or cooperates with peers
4. `result_acceptance`
   - whether outputs are proposals, require Overseer review, or may apply directly

The planning bias is:

- keep the primary interactive thread fully powerful
- keep same-family Codex delegates broad in capability but bounded in authority
- keep future external collaborator agents narrow in both capability and result acceptance
- keep the first ecology as `manager -> worker`, not coequal peer handoffs

## Current planning decision

### 1. Primary interactive dialogue

The primary interactive Overseer dialogue remains the sovereign thread.

Current posture:

- full house authority
- full host capability
- root-capable
- normal network access
- direct access to auth, browser, load balancer, deadman, and root surfaces
- allowed to widen, narrow, or replace other loop profiles and harnesses

Reason:

- this is the operator-reachable recovery and construction surface
- if this thread cannot repair the house, the house becomes harder to recover honestly

### 2. Same-family Codex finite loops

Current planning stance:

- do **not** hard-sandbox same-family Codex loopers by default
- do bound them aggressively at the control-plane layer

That means:

- separate local Codex session by default
- explicit mission
- explicit loop class
- explicit turn budget
- self-stop allowed
- explicit receipts, checkpoints, and reconstruction packets
- subordinate to the primary interactive thread
- no hidden respawn or scheduler folklore

The key distinction is:

- `capability` is still broad
- `authority` is narrow and class-bound

### Why capability stays broad for same-family Codex loops

Because the house is asking those loops to do real Overseer work:

- inspect and repair host surfaces
- reason across the repo and state rooms
- restart or recover engines
- eventually handle auth, browser, and machine repair

If the house clipped those loops too early with hard host sandboxes, it would likely produce:

- false comfort
- brittle repair paths
- duplicated special-case escape hatches
- and a quiet split between "allowed in theory" and "possible in practice"

So the current bias is:

- keep same-family Codex delegates technically powerful enough to do real house work
- constrain them by declared mission and receipts first

### 3. Loop classes should bound authority

The current planning model is that loop class should constrain what a same-family delegate is supposed to do even when its host capability remains broad.

Examples:

- `green-loop`
  - prove health, reconcile drift, tiny obvious repair only
- `red-loop`
  - diagnose and repair one fault family
- `refactor-loop`
  - reduce entropy without intended behavior change
- `frontier-loop`
  - build one bounded next capability
- `audit-loop`
  - search for problems, contradictions, weak assumptions, stale doctrine, and missing tests
  - should not fix by default

So the house should think:

- broad capability does not imply broad legitimacy
- the loop class is the first authority boundary

### 4. Deadman rescue is narrower than ordinary looping

Deadman rescue is not weaker because the model is less trusted.
It is narrower because the mission is more dangerous.

Current planning posture:

- same-family Codex
- separate-session finite-loop execution
- broad technical capability if real rescue requires it
- but stronger launch constraints:
  - silence or health trigger
  - duplicate suppression
  - cooldowns
  - grouped receipts
  - bounded rescue framing

Current default rescue envelope remains:

- diagnosis
- machine-legibility restoration
- minimal engine restart posture

Not yet default:

- auth mutation
- browser reauth
- wide machine surgery

That remains an explicit expansion seam, not ambient authority.

### 5. External collaborator agents should start hard-bounded

Future Gemini participation changes the picture.

Current planning stance:

- Gemini and similar external collaborator agents should **not** inherit ambient house power
- they should start under explicit hard capability limits

The initial bias should be:

- trust class: `experimental` or `guarded`
- read scope: declared bundle only
- write scope: scratch, proposal, or bounded artifact paths only
- no direct access to `/home/overseer/authcreds/`
- no direct mutation of `/home/overseer/.codex/auth.json`
- no root-capable envelope
- no host-broad process visibility
- no direct mutation of canonical loop, deadman, or load-balancer state
- result acceptance: `proposal_only` or `requires_overseer_review`

This is where hard host-enforced boundaries become worth the cost early.

### Gemini first implementation

That planning stance now has a first live room:

- placard: `/home/overseer/GEMINI.md`
- runtime root: `/home/overseer/state/gemini-collab/runtime`
- control tool: `/home/overseer/scripts/gemini_collab.py`

The first implementation keeps the planning bias intact:

- imported auth reach from a neighboring sandworm lab profile
- sandbox-only provider execution
- declared bundle staging into a bounded workspace
- card/proposal outputs only
- no sovereign mutation of house state

## Practical split

The house should plan around this split:

### Same-family Codex delegates

- trust: high enough for real house work
- capability: broad by default
- authority: narrow, class-bound, mission-bound
- coordination: explicit and reconstructable
- result acceptance: bounded auto-apply may be legitimate within class

### External collaborator agents

- trust: lower or less stable
- capability: hard-bounded from day one
- authority: proposal-first
- coordination: explicit profile only
- result acceptance: Overseer-reviewed by default

## What this means operationally

### Good current limits for Codex loopers

- explicit class
- explicit mission
- explicit max turns
- explicit self-stop contract
- explicit receipts
- explicit group membership when relevant
- explicit reopen packet
- explicit priority under the load balancer

### Not the right first limits for Codex loopers

- filesystem clipping so tight they cannot repair the house
- root removal for loops that may need to restore root-shaped machinery
- hidden approval bureaucracy that the interactive thread then has to bypass anyway

## When to revisit hard limits for same-family Codex loops

The house should revisit this stance if any of these become true:

- multiple concurrent Codex delegates become normal rather than exceptional
- real accidents show that authority-only limits are not enough
- deadman rescue grows into auth or browser repair
- loop groups start coordinating in ways that create higher blast radius
- the house develops a narrow host-verb gateway strong enough to replace ambient host reach

At that point, systemd- or transient-unit-backed hardening may become worth the complexity.

## Candidate future hardening layers

If the house later wants harder capability envelopes, the likely primitives are:

- separate worktrees or declared writable roots
- separate Codex homes or auth mirrors for loop classes
- transient units or services with explicit writable paths
- `ProtectSystem=`, `ProtectHome=`, `ReadWritePaths=`, `NoNewPrivileges=`, and related host hardening
- narrower host-verb gateways instead of ambient shell reach

These should arrive only when they improve truth more than they increase repair friction.

## Current recommendation

The house should plan like this now:

1. keep the primary interactive thread fully powerful
2. keep same-family Codex loopers broad in capability but narrow in authority
3. make loop class, mission, turn budget, and receipts the real first boundaries
4. keep deadman rescue narrower by mission and escalation ladder
5. give future Gemini-style collaborator agents hard capability limits from the start

That is the least misleading current model.
It keeps the house repairable while still admitting that not every worker deserves equal freedom.
