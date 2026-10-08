# Router side-effect warning page, UPnP/NAT-PMP device fragility, and rollback boundary interface spec

## Purpose

Current official Resilio docs still include a small but important warning:
some printers, scanners, and other network equipment may mishandle UPnP packets and stop processing network requests.

That warning is too important to live as a footnote under one preference.
It means the user is not only changing this runtime.
They may be perturbing adjacent infrastructure.

AnonSync should therefore route certain ingress-widening actions through a dedicated **router side-effect warning** page.

## When this page appears

Render this page when all of the following are true:

- the operator is about to enable automatic router mapping or equivalent discovery/mutation beyond the host
- the runtime is on a network where adjacent equipment fragility cannot be ruled out
- the product cannot honestly collapse the risk into `local-only preference`

Also render when:

- the network previously showed device instability after UPnP/NAT-PMP activity
- the operator is enabling automatic mapping on a shared home or office network with unmanaged devices
- rollback may require router-level action or waiting for lease expiry

## Review sections

### 1) Adjacent infrastructure touched

Show:

- router or gateway candidate
- discovery/mutation protocols to be spoken
- whether the target is confirmed or only inferred
- whether non-router devices on the segment may also observe or mishandle the traffic

### 2) Side-effect classes

Show candidate side effects such as:

- `no-known-side-effect`
- `adjacent-device-fragility-possible`
- `gateway-behavior-unknown`
- `rollback-may-be-delayed`
- `prior-instability-observed`

### 3) Rollback boundary

Show:

- whether disabling the toggle retracts the request immediately, only locally, or only partially
- whether residual lease or rule state may survive outside the host
- whether manual router inspection may still be required

### 4) Safer alternatives

Offer explicit alternatives such as:

- keep relay fallback and do not request ingress widening
- pin a fixed port and perform deliberate manual forwarding later
- keep local/LAN discovery only
- seek external-admin review before mutation

### 5) Acceptance sentence

The operator must accept one explicit sentence such as:

`This action may send router-mutation traffic beyond this host and may have side effects or residual state outside the runtime even if direct connectivity is not ultimately proven.`

## Main surface

A compact warning should read like one of these:

- `router-side mutation may affect adjacent devices; rollback may outlive this toggle`
- `adjacent gateway behavior unknown; safer alternative is relay/directless mode`
- `automatic mapping allowed only after explicit acceptance of off-host side effects`

## Event language

Use phrases such as:

- `router-side-effect warning shown`
- `off-host mutation accepted`
- `rollback boundary disclosed`
- `local-only alternative chosen instead`

Avoid phrases such as:

- `minor network tweak`
- `harmless optimization`
- `revert is automatic`

## Design tests

The page fails if any of these remain true:

- the user can enable automatic mapping without being told that off-host infrastructure may change
- disabling the feature implies stronger rollback certainty than the product can prove
- adjacent-device fragility remains buried in help text instead of surfaced at decision time
