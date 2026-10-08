# Delegation-and-serve proof page — onward-share authority, unmodified-byte serving, and peer-cascade ceiling

## Purpose

After any serious `can this peer help others?` or `why could that supposedly read-only peer still upload something?` dispute, a later operator must be able to answer without reopening protocol folklore.
This page exists because writeback authority, onward-share authority, and byte-serving are different planes.

## Proof ladder

### Rung 1 — grant label only

We know the visible grant label.
We do **not** yet know effective posture, serve-right, or delegation authority.

Allowed sentence:

- `seat label known, effective capabilities still weak`

Blocked stronger sentence:

- `this peer cannot help anyone else`

### Rung 2 — effective posture proven

We know whether the seat is direct, linked-family owner default, inherited local share, or encrypted hard-wired.
We may still not know whether unchanged bytes may be served or whether onward sharing is allowed.

Allowed sentence:

- `effective posture known`

Blocked stronger sentence:

- `effective posture alone proves serve-right`

### Rung 3 — delegation authority proven

We know whether this seat may onward-share or revoke.

Show:

- owner versus non-owner basis;
- special ceilings for Standard, Advanced, local-share, or encrypted derivatives;
- whether any share artifact may be forwarded only in a narrower family.

Allowed sentence:

- `delegation authority proven`

Blocked stronger sentence:

- `delegation authority implies writeback and serve-right are identical`

### Rung 4 — serve-right proven

We know whether the seat may serve already-approved bytes, and along what lane.

Show:

- whether bytes are ordinary approved swarm bytes or parent-source-only local-share bytes;
- whether serving is allowed despite narrow mutation posture;
- whether encryption or local-derivation narrows the serve plane.

Allowed sentence:

- `serve-right proven for this lane`

Blocked stronger sentence:

- `serve-right means the peer can author new mutations`

### Rung 5 — cascade ceiling explained

We know the farthest authority this seat can project to others.

Show:

- whether it can publish mutations;
- whether it can only relay unchanged bytes;
- whether it can issue further shares, only encrypted shares, or no shares at all;
- whether parent-source dependence blocks wider claims.

Allowed sentence:

- `peer-cascade ceiling explained`

Blocked stronger sentence:

- `all visible peers participate with identical authority`

## Required side proofs

The page must also show:

- whether linked-family ownership is creating a misleading appearance of direct delegation;
- whether RO serving happened only for unchanged bytes;
- whether a local share's help is limited to the parent-source lane;
- whether encrypted custody can onward-share only in encrypted form;
- whether any observed upload was actually repair/heal traffic rather than new-author mutation.

## Compact output

The page must produce:

- `effective_posture_proof_grade`
- `delegation_authority_class`
- `serve_right_class`
- `peer_cascade_ceiling`
- `blocked_stronger_sentence`
