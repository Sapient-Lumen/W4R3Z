# Remedy-hardening-attestation-revocation-delivery review page — did the revocation or revalidation actually reach every dependent and suppress stale surfaces?

## Review question

Can the product honestly present this corrective wave as merely opened, delivered to the reachable cohort, acknowledged where required, closed for a named cohort, or still residually unsafe because stale surfaces remain live or some dependents cannot be verified?

## Review panels

### 1) Reachability review

Ask whether every dependent that previously relied on the source has a known callback path.
The review must preserve:

- callback path known and tested
- callback path inferred but untested
- callback path missing
- callback path stale or expired
- disconnected or pending lane that may later return

False upgrades to reject include:

- treating registry presence as proof of reachability
- treating one callback channel for one device as proof for all linked or derivative dependents

### 2) Delivery review

Ask what evidence proves that the corrective notice or successor-binding request actually reached the dependent.
The review must classify evidence at least as:

- queued only
- attempted
- transport-confirmed
- opened or fetched
- durable receipt from dependent owner
- successor binding observed

The page must reject `delivered` when the evidence only proves that a message was generated locally.

### 3) Acknowledgement review

Force the operator to decide which dependents merely need delivery and which require affirmative acknowledgement before the case can close.
The review must separate:

- notice-only dependents
- acknowledgement-required dependents
- successor-binding-required dependents
- revalidation-required dependents
- policy-waived acknowledgement cases

### 4) Stale-surface review

Force explicit review of every place the old ruling may still be live:

- dashboards or status pages
- exported packets
- mirrored external copies
- downstream receipts
- policy or template text
- disconnected local bytes that still inform users
- Archive or retained old versions

The review must reject any broad closure claim that outruns stale-surface evidence.

### 5) Residual-risk review

Force review of every reason the corrective wave may still be incomplete:

- unreachable dependent after prior consumption
- expired evidence horizon
- pending or disconnected lane may reconnect later
- clone or fresh-instance ambiguity
- external artifact without callback path
- acknowledgement requested but not returned
- suppression requested but not confirmed

### 6) Closure-threshold review

The page must land on explicit branches such as:

- wave opened, callback map incomplete
- delivered to reachable cohort only
- delivered and acknowledged, suppression pending
- named-cohort closure achieved
- external residual risk preserved
- global all-clear blocked
- downstream safe again for required cohort

### 7) Speakability review

The review must decide which sentence is honestly speakable now:

- `correction issued; delivery not yet proven`
- `delivered to reachable dependents only`
- `acknowledged by required internal dependents only`
- `stale surfaces suppressed for the named cohort`
- `external residual risk preserved; do not claim global closure`
- `downstream safe again for the required cohort only`

## Output states

The page must be able to land on at least these outputs:

- callback coverage incomplete
- delivery confirmed, acknowledgement incomplete
- acknowledgement complete, stale surfaces unsuppressed
- named cohort closed, external cohort unverifiable
- residual-live-surface debt preserved
- permanently blocked from `historical only everywhere` language
