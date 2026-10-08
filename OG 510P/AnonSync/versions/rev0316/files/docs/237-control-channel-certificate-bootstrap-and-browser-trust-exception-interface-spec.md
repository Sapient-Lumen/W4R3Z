# Control-channel certificate bootstrap and browser-trust exception interface spec

## Purpose

The archive already had local-web-first, listener-binding, credential-recovery, and headless-intake language.
What it still lacked was one stricter contract for a control-surface problem current sync products still leave dangerously casual:

> if the daemon is controlled through a browser, what exactly is the trust story for that browser session, and does the product really expect the operator to treat `Proceed anyway`, `clear HSTS`, and `install your own cert` as equivalent answers to one security question?

Current Resilio docs make this seam concrete.
Their current WebUI docs still say HTTPS is optional, that enabling it uses a self-signed certificate unless the operator provides their own, and that browsers will therefore show an insecure-connection warning.
Their current browser-warning page still tells the operator to inspect the certificate, proceed unsafely, clear HSTS so the browser falls back to HTTP, or provide a trusted certificate through configuration.

That means browser trust for local control is still not one explicit contract.
It is several different rituals with materially different security posture.

## Core decision

AnonSync must treat browser control trust as a first-class reviewed object.
The product must distinguish:

- loopback-only local control trust
- LAN-exposed control trust
- externally proxied control trust
- custom-certificate control trust
- degraded trust exception mode

A browser warning may never be the primary explanation surface.
The operator must be able to answer, before continuing:

- which endpoint am I talking to
- why does the browser distrust it
- what trust grade does this session actually have
- what safer upgrade path exists from here

## Why this matters

Current Resilio behavior still leaves too much meaning scattered across help pages and browser UI:

- Linux and service seats use WebUI as the normal control surface
- HTTPS with the built-in certificate triggers a browser warning by design
- one workaround is to continue unsafely
- another is to clear HSTS so the browser prefers HTTP again
- another is to switch to a configured certificate and private key

Those are not the same decision.
AnonSync should therefore hold one stronger rule:

> every control endpoint carries an explicit trust grade, and every trust downgrade or trust exception creates a receipt.

## Fixed review order

Every first browser connection, trust exception, or certificate swap must render the same sections in the same order:

1. **Endpoint identity**
2. **Current trust grade**
3. **Allowed bootstrap paths**
4. **Exception or upgrade consequences**
5. **Control-trust receipt**

### 1) Endpoint identity

Show:

- endpoint class (`loopback`, `lan`, `remote`, `proxied`, `other`)
- listener address and port
- runtime seat and host name
- whether this endpoint is expected for this seat profile
- whether this endpoint was discovered locally or handed off from elsewhere

### 2) Current trust grade

Show one explicit grade:

- `pinned local bootstrap`
- `trusted certificate`
- `user-approved temporary exception`
- `plaintext local only`
- `degraded / unverified`

The grade must explain why the browser warning exists instead of outsourcing the meaning to browser chrome.

### 3) Allowed bootstrap paths

Offer only explicit paths such as:

- `trust once for this loopback endpoint`
- `pin this local control endpoint`
- `install or select certificate`
- `switch back to local-only plaintext control`
- `abort and inspect`

The operator must never be asked to type a browser easter egg or clear unrelated browser state just to understand what they are doing.

### 4) Exception or upgrade consequences

Show:

- whether the action widens who can reach the endpoint
- whether the action changes protocol or certificate
- whether browser trust remains local to one browser profile or becomes system-wide
- whether restart is required
- whether previously issued receipts remain valid

### 5) Control-trust receipt

Record:

- endpoint identity
- old and new trust grade
- certificate fingerprint or local pin id
- actor and seat
- whether a temporary exception or durable upgrade was chosen
- expiry or rotation posture

## Main surface

Every browser-controlled seat should expose one **Control trust** page.
That page should answer:

- `why the browser is warning`
- `whether this is a local bootstrap or a remotely reachable endpoint`
- `what the safest next trust grade is`
- `what receipt proves the decision taken`

No browser warning page should be the primary semantic home of this decision.

## Acceptance criteria

This spec is satisfied when:

- temporary exception, plaintext local control, and trusted-certificate control are never conflated
- browser trust state can be explained without leaving the product
- no trust downgrade occurs without a receipt
- the operator can tell whether they are protecting a loopback bootstrap or a remotely reachable control channel
