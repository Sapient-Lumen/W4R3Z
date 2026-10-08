# Resilio disclosure ceiling, link-fragment locality, relay blindness, and telemetry fragmentation evaluation

## Why this seam matters

The archive already has strong doctrine for **exposure budgets**, **artifact preview**, **control-surface binding**, **telemetry consent**, and **route provenance**.
What it still lacked was one direct evaluation for another ordinary operator question:

> when I share, open, relay, browse, or leave defaults on, who can actually learn what — the peer, the browser, Resilio infrastructure, relay infrastructure, or nobody but my local machine — and what is the strongest honest sentence the product can say about that?

Current official Resilio documentation makes this seam sharper than a generic `end-to-end encrypted` reassurance.
Across current Resilio Sync help they still say all of the following:

- `Can others see my files? How secure is sharing by Resilio Sync?` still says data is transferred directly between chosen peers, data is AES-128 encrypted in transit, X.509 certificates are used for mutual authentication, and usage statistics are collected and sent in the clear.
- `Can Resilio team see and block/remove any Sync folders?` still says Resilio neither hosts nor caches folder content, does not distribute links, and that link-specific information lives after the `#` fragment and is therefore not sent from the browser to the Resilio server.
- `Link structure and flow` still says the landing page on Resilio's server can show basic folder info such as folder name and size, that the server replaces `https://` with `btsync://` so the local app can open the link, and that the fragment parameters include folder name, approximate size, folder ID, temporary key, expiration, and client version while still not being sent to the server.
- `What is a Relay Server?` still says relay is used when direct connection is impossible, that files pass through the relay path, and that the relay cannot read them and does not store them.
- `What ports and protocols are used by Sync?` still says Sync downloads `sync.conf`, communicates public and local IPs plus the list of shares to tracker infrastructure, and then learns peer addresses through that discovery path.
- `Power user preferences` still says `send_statistics` is enabled by default and sends anonymous statistical metrics such as OS, Sync version, and whether Sync is active.

That is useful candor.
It is also a good reason not to clone the page contract.

## What Resilio gets right

### 1) It openly distinguishes several different observer classes

Current official docs do not flatten all outsiders into `the internet`.
They distinguish at least:

- chosen peers
- relay infrastructure
- tracker/config infrastructure
- browser landing-page infrastructure
- Resilio telemetry collection
- local browser / handler / app handoff state

That is a useful start.

### 2) It openly distinguishes ciphertext carriage from fact visibility

The docs still make clear that encrypted relay carriage is not the same thing as invisibility of all metadata, and that `not hosting your content` is not the same statement as `no infrastructure learns anything at all`.
That is a valuable distinction.

### 3) It openly admits that carriers and handlers matter

Current docs still treat the browser landing page, the `btsync://` handoff, and the share link fragment as operationally meaningful, not decorative.
That is useful because operator trust often rises or falls at the carrier boundary.

## Why AnonSync still should not clone it

One ordinary operator question is still fragmented:

> what exact facts become visible to which observer class when I use this sharing or connectivity path, and what stronger privacy sentence is the product refusing to claim?

In current Resilio, that answer can still depend on hopping across:

- the security/privacy FAQ
- the `Can Resilio team see...` FAQ
- link-structure docs
- relay docs
- ports/protocols discovery docs
- telemetry settings docs

That is too much archaeology for a question that shapes trust.

## Hard decisions for AnonSync

1. **Disclosure ceiling becomes a first-class contract object.** Every serious share, open, relay, tracker, telemetry, or browser-handoff path must publish who can learn what.
2. **Ciphertext carriage and fact visibility stay separate axes.** `Relay cannot read payload` does not answer whether infrastructure learns route facts, presence facts, or share identifiers.
3. **Carrier and observer are different objects.** Browser landing page, `btsync://` handoff, relay carriage, tracker discovery, and telemetry export are not one generic `network use` bucket.
4. **The product must publish the blocked stronger sentence.** If the safe sentence is `payload not readable by relay`, the interface must reject the stronger sentence `relay learns nothing at all` unless it can actually prove that.
5. **Local-only parsing and off-device preview stay explicitly different.** If preview information is produced from a local fragment parse, the product should say so; if a remote service rendered it, the product should say that instead.
6. **Receipts preserve disclosure lineage.** Later audits must still show which facts were visible to peers, relays, browser handlers, trackers, and telemetry lanes at the moment of action.

## Interface family implied by this evaluation

This pass therefore adds five more page-shaped obligations:

1. **Disclosure boundary contract sheet**
2. **Carrier disclosure review**
3. **Third-party knowledge proof**
4. **Browser-open boundary**
5. **Disclosure lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> current Resilio docs are good evidence that direct peers, relays, trackers, telemetry, and browser handoff all have different knowledge ceilings; they are also good evidence that the ordinary operator answer about `who learned what from this action?` still leaks across several documents instead of one stable product-owned contract.
