# 470 — Intake-failure classification, handoff-vs-artifact separation, and manual fallback lanes

## One-line thesis

When consequential notices, appeals, evidence packets, or supplier submissions fail to arrive, open, or register, the archive should distinguish bad artifact from bad delivery or handoff and preserve a typed manual fallback lane so rights do not disappear into one broken digital path.

## Why this matters

A surprising amount of public-process harm begins with a deceptively small ambiguity: *did the artifact fail, or did the route fail?*

A claimant opens a decision link and nothing happens. An operator follows an incident packet handoff and lands on a dead route. A reviewer receives a corrupted attachment and assumes the submitter failed. A supplier upload times out and the institution later says no evidence was received. In all of these cases, one generic “submission failed” or “link invalid” message can silently convert delivery trouble into procedural loss.

The datacube already requires appeal routes, equivalent human channels, evidence packets, and durable case state. What it still lacked was one note dedicated to the **intake seam itself**: the boundary where artifacts are passed from one person, system, channel, or surface into the governed process.

## Pattern pack

### 1. Classify failure at the right layer

Intake failures should distinguish at least the following classes:

- artifact missing,
- artifact malformed or corrupt,
- artifact present but unauthorized for this route,
- handoff failure between browser, app, portal, or inbox,
- registration failure after delivery,
- temporary capacity or outage,
- and unsupported channel or file type.

A bad route should not be mistaken for a bad claim.

### 2. Preserve the original attempted route as evidence

When digital intake fails, the archive should retain enough witness information to reconstruct what was attempted, such as:

- link or token used,
- submission time,
- route or form version,
- user-facing error or absence of confirmation,
- and whether the artifact ever reached the receiving boundary.

Otherwise later review will falsely compress all failure into submitter fault.

### 3. Provide a manual or assisted fallback lane that keeps the same rights intact

If the primary digital route fails, there should be an alternate lane such as:

- staffed phone intake,
- assisted webchat,
- in-person support,
- secure email or upload,
- or operator-mediated entry on the user’s behalf.

The fallback lane should not silently downgrade clocks, rights, review priority, or evidentiary weight.

### 4. Separate receipt from validation

A system can acknowledge that it received an artifact before deciding whether the artifact is valid for the process. These are different moments.

- **receipt** means the artifact reached the governed boundary,
- **validation** means it passed the route’s checks,
- **acceptance** means it entered the process,
- **rejection** means the process refused it with a named reason.

Collapsing those states makes intake disputes much harder to reconstruct.

### 5. Do not require one brittle handoff path to exercise a right

A consequential route should not depend entirely on one browser deep link, one protocol handler, one attachment type, or one portal widget. If that accelerator fails, the archive should preserve a typed alternative path rather than forcing users to start from rumor or guesswork.

### 6. Keep support staff on the same intake truth as the public

If staff assist with fallback intake, they should operate from the same route rules, versions, and explanatory surfaces the public sees. Otherwise assisted channels turn into folklore instead of governed continuity.

### 7. Measure handoff failure as governance telemetry

Repeated intake failures should count as evidence about:

- broken recourse,
- inaccessible submission design,
- fragile vendor integrations,
- or misleading public instructions.

A rights-bearing service should treat route failure as governance debt, not only technical noise.

## Guardrails

- Do not let broken delivery impersonate invalid content.
- Do not make the manual lane weaker than the primary digital lane.
- Do not treat lack of automated confirmation as proof that no attempt occurred.
- Do not merge receipt, validation, and acceptance into one vague success state.
- Do not require users to rediscover the process from scratch when a handoff fails.

## Failure modes

- **route-failure blame shift**: the institution treats channel failure as claimant or submitter fault.
- **receipt-collapse ambiguity**: nobody can tell whether the artifact arrived, failed validation, or was never registered.
- **single-lane fragility**: one browser or portal failure quietly suspends a right.
- **fallback downgrade**: assisted or manual intake exists but loses timing, priority, or evidentiary force.
- **support folklore**: staff invent ad hoc workarounds because the official fallback lane is not real.

## Practical tests

An intake boundary passes when it can answer yes to all of the following:

1. Can the archive distinguish bad artifact from bad route or handoff?
2. Is the attempted route preserved well enough to reconstruct the failure later?
3. Does a manual or assisted fallback lane preserve the same clocks and rights?
4. Are receipt, validation, acceptance, and rejection kept as separate intake states?
5. Are repeated intake failures measured and escalated as governance signal?

## Compression rule for the archive

If a consequential service can say **your submission did not go through** but cannot also say **whether the artifact failed, the route failed, what was preserved, and which fallback lane keeps your rights alive**, then it is still letting **channel brittleness impersonate due process**.
