# Revision addendum — service/browser control, install-path splits, and cross-surface destructive-toggle fragmentation after rev0285

Current official Resilio material is still admirably candid that browser control, service deployment, install path, and destructive folder behavior are all real operator concerns.
The live v3 personal line still runs through `3.1.2.1076`.
Current `Running Sync as a service on Windows` docs still say Sync can run as a service regardless of whether a user is logged in and that service installation opens Sync WebUI in the default browser.
Current `Installing Sync package on Linux` docs still publish manual, repository, and official Docker-image paths, while also saying personal/non-commercial users can install `v3` and Sync Business users should stay on `v2.8.1`.
Current `Download Sync` pages still say Sync is for personal non-commercial use and warn NAS users not to update current Sync Business installations to v3 because configured-share access will be lost.
Current `Configuring WebUI` and browser-warning docs still say listener binding, password posture, HTTP/HTTPS choice, self-signed certificates, and browser exceptions are normal parts of operation.
Current Android interface docs still expose `Use Archive`, `Overwrite changed files`, relay, tracker, LAN search, and host overrides as ordinary per-share controls.

That is real candor.
It still does **not** earn direct interface cloning.

The reason is the next clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still makes the ordinary dangerous-control question sprawl across:

- product-line and upgrade pages
- install and service pages
- WebUI binding and browser-warning pages
- desktop folder preferences
- mobile per-share settings

So the product idea stays useful while the page contract still fails.

The missing operator-owned question is simple:

> before I use a browser or service surface to approve destructive healing, what exact runtime am I controlling, what trust grade does this session really have, what residue can I preserve first, and what approval is still valid *right now*?

Current official docs still expose ingredients of that answer without one stable product-owned object.
They still show that:

- service-mode control and browser control are normal, not edge cases
- listener scope and certificate/trust posture are not the same question
- install path and product line can change what upgrade is even allowed
- mobile and desktop both surface destructive controls, but not inside one reviewed danger grammar
- `overwrite` can still feel like a preference long before it feels like a receipt-bearing destructive action

That is why this revision adds five narrower replacement pages and component families:

- `857` Danger session capsule and persistent review-context rail
- `858` Trust bootstrap review page
- `859` Salvage export page
- `860` Salvage export receipt page
- `861` Destructive execution ticket page

These pages keep the Resilio candor and reject the need to improvise dangerous-control truth from install notes, browser-warning folklore, and per-surface toggles.

## Why this matters for AnonSync

A serious sync product should not let a dangerous browser session feel trustworthy just because it is open, authenticated, or familiar.
The product should own at least these distinctions explicitly:

- **runtime identity** — which endpoint and storage world this dangerous page belongs to
- **trust unlock** — whether control is on managed trust, pinned trust, reviewed self-issued trust, or a bootstrap exception that still blocks destructive apply
- **rescue-first option** — what residue can be exported or preserved before approval
- **approval freshness** — whether the reviewed basis still matches the current endpoint, trust grade, loss matrix, and salvage receipts
- **one-shot commit** — whether the final destructive approval still binds only this action and this scope

Resilio's current docs still make those classes legible only if the operator already knows how to splice service bringup, Linux install, product-line split, WebUI trust bootstrap, and mobile/desktop overwrite toggles.
AnonSync should not clone that burden.

## Concrete product stance

Borrow from Resilio:

- candid admission that service/browser control is normal
- candid admission that install/upgrade constraints matter
- candid admission that destructive folder behavior shows up on multiple surfaces
- candid admission that browser trust warnings are operational reality

Do not clone from Resilio:

- leaving dangerous-control meaning split across install, upgrade, WebUI, browser-warning, desktop, and mobile docs
- letting destructive approval ride on a browser-exception mental model
- letting `approve after export` remain a promise without its own export object and receipt
- letting final destructive authority persist as ambient session familiarity rather than a one-shot reviewed ticket

## Evaluation summary

Resilio still deserves credit for publishing the ingredients of service/browser/destructive operation honestly.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `what runtime am I controlling, under what trust grade, with what pre-destructive preservation, and with what still-valid final approval?`

AnonSync should therefore make **danger-session context, trust-bootstrap review, salvage export, and one-shot destructive execution** first-class product objects.
