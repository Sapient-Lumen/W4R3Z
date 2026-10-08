# Portable offer inspection, browser handoff, and local claim continuity interface spec

## Purpose

The archive already distinguishes offer artifacts from claims.
What it still lacked was one explicit answer to the browser/import seam:

> when a person opens a link, scans a QR code, clicks a local handoff, or imports a file, what exactly is allowed to happen **before** the local machine has performed claim review?

Current Resilio link docs are useful here.
A landing page can show basic metadata and then hand the link into the app automatically.
That convenience is worth learning from.
But AnonSync should not let `opened in browser` blur into `accepted locally`.

## Core decision

Portable inspection and local acceptance are separate stages.
A browser page, landing sheet, or imported preview may establish **artifact truth**.
Only a local daemon-backed claim surface may establish **machine-local outcome**.

That yields a fixed ladder:

1. artifact preview
2. handoff choice
3. parsed local claim draft
4. path / authority review as needed
5. apply and receipt

## Stage 1 — artifact preview

A portable preview surface may show:

- offer label or subject label
- approximate size / class hints when safe
- issuer identity summary or pinned issuer expectation
- expiry and redemption limits
- whether the artifact appears valid, expired, revoked, or malformed
- whether redeeming it would later require local path choice or authority review

A portable preview surface may **not** claim:

- that the share is now accepted here
- that a local path has been chosen
- that authority has widened on this seat
- that this machine is now linked, mounted, or synchronized

Artifact preview answers `what is this?`, not `what did my machine just do?`

## Stage 2 — handoff choice

After inspection, the operator should choose how to continue:

- `Continue on this machine`
- `Save offer artifact`
- `Copy to another seat`
- `Open in local web workbench`
- `Open in desktop projection`
- `Stop here`

The key rule is that handoff itself is explicit.
The product should not rely on ambient browser protocol magic as the only available path.

## Stage 3 — parsed local claim draft

Once the local daemon accepts the artifact, it should create a real claim draft and show:

- offer identity / artifact digest
- how the artifact reached this seat
- acting seat
- requested local outcome
- whether local path, compare, or authority review is still needed
- whether the artifact was already seen or previously rejected here

This is where the product moves from `portable thing` to `machine-local intent`.

## Stage 4 — path and authority review

The claim draft should then converge into the already-established intake / compare / continuity workflows whenever necessary.
Examples:

- empty-path local adoption
- non-empty-path compare review
- relationship join review
- authority widening review
- successor or continuity-sensitive handoff

The import channel must not get a special fast path that bypasses the harder but more truthful review objects.

## Stage 5 — apply and receipt

Only now may the product say things like:

- `visible here`
- `claimed here`
- `bound here`
- `joined here`
- `role widened here`

And only the resulting receipt should make those claims durable.

## Browser and local-web continuity rules

When browser or local web is the initial entry point, the operator should not lose context during auth or projection change.
After authentication or handoff, the product should preserve:

- artifact identity
- source page / scan / import origin
- current subject focus
- existing draft handle if created
- any already-parsed warnings or constraints

This is how browser convenience stays honest instead of feeling like a trapdoor into a different product.

## Missing-local-runtime rules

If the artifact is opened on a machine that cannot continue locally, the surface should say exactly why:

- no reachable local daemon
- wrong custody seat
- no filesystem custody for the requested outcome
- unsupported projection for the requested action
- auth or policy requirement not yet met

The fallback action should preserve the artifact and context.
It should not degrade into `install app` as the only meaningful sentence.

## Safe automatic behavior

A small amount of automation is still allowed:

- deep-linking to the exact local claim page
- pre-populating the artifact digest and known constraints
- reopening the same draft after auth repair
- focusing the next required review section

What is not allowed is silent local apply or silent path creation purely because the artifact arrived through a convenience channel.

## What the product must never imply

The import surface must never imply these are the same thing:

- opening a link versus claiming an offer
- parsing an offer versus binding a path
- browser preview versus trusted local receipt
- same-machine convenience versus same-authority proof

If the product compresses those differences, it has recreated the exact `click link and hope` contract that AnonSync is supposed to replace.

## Cross-projection rules

GUI, local web, TUI, and CLI may all originate or continue a claim.
They must preserve the same identity chain:

- artifact reference
- parsed claim reference
- later apply receipt

A headless operator should be able to follow that chain entirely from CLI.
A Linux-first operator should be able to do it entirely from local web.
No projection should require a richer sibling surface merely to learn whether the machine actually accepted the offer.

## Result

A good browser/import contract prevents five failures:

- confusing portable artifact truth with local acceptance truth
- using protocol handlers as hidden mutation steps
- losing context across auth or projection handoff
- treating browser convenience as justification to skip claim review
- leaving the operator unable to prove later what was merely previewed versus what was actually accepted here

If opening an offer can still create a local path or trust change before the product has said so in claim language, AnonSync has not yet fixed the browser/import seam.
