
# Revision addendum — Resilio product-line split, local-web candor, and destructive-contract fragmentation after rev0284

Current official Resilio materials are still useful precisely because they are not pretending to be simpler than they are.
The live personal line still runs through `Sync v3` and the 3.0 change log currently reaches `3.1.2.1076 (31/Oct/2025)`.
Current support docs still publish `Sync v3` support tables while also retaining a separate `Sync v2` support section.
Current Resilio site pages also say:

- Sync on the public download page is for personal non-commercial use
- Sync Business should not be updated to v3
- existing Sync Business customers remain supported on `v2.8`
- `2.8` is the final upgrade available in the portal for that business line
- new business buyers should look at Active Everywhere instead

That is honest.
It is also exactly why the non-clone case is stronger now.

The useful Resilio ideas remain real:

- local web / WebUI / service-style operation is a first-class deployment reality
- unsupported upgrade paths are named plainly instead of hidden behind marketing optimism
- destructive overwrite is still admitted to be destructive
- archive-bearing, encrypted custody, and defaults still materially shape the rescue envelope

But the present operator contract is still fragmented in three different ways at once.

## 1) Product-line fragmentation

One operator story now lives across at least three lanes:

- `Sync v3` personal / non-commercial
- `Sync Business v2.8` for existing customers
- `Active Everywhere` for new business demand

That is a real business decision.
AnonSync should not clone it as the primary interface grammar.
Capability differences may be commercial reality; destructive-review semantics should still remain one product language.
The product should not require the operator to translate between different era/product names before they can understand custody, trust, or repair.

## 2) Local-web bootstrap fragmentation

Current official docs also show that local web is normal on Linux and services, with listener binding living in config and with self-signed certificate/browser-warning behavior documented separately.
Again, that is useful candor.
The non-clone problem is that the durable operator answer still has to be reconstructed from:

- service / config-mode docs
- WebUI binding docs
- browser-trust-warning docs

AnonSync should keep the local-web reality and reject the folklore.
The operator should not have to remember whether `localhost`, `0.0.0.0`, self-signed TLS, or a browser warning is merely bootstrap, a wider listener exposure, or a trust downgrade worth pausing over.
Danger surfaces must own those distinctions on-page.

## 3) Destructive-contract fragmentation

Current official Resilio docs still leave one destructive-heal answer spread across:

- one-way / read-only sync FAQ
- folder preferences
- archive behavior
- encrypted folders
- power-user defaults
- Android and iOS surface docs
- configuration-mode prose

So even after the prior overwrite-preview tranche, another conclusion becomes clearer:

> the non-clone reason is no longer only `their docs are scattered`; it is `their present-day operator contract is scattered across product lines, bootstrap notes, and feature pages at the same time`.

## What AnonSync should borrow

Borrow these traits aggressively:

- speak plainly about product-line boundaries and unsupported upgrade paths
- speak plainly about local web, service operation, and listener binding
- speak plainly about destructive overwrite and rescue dependence on archive/custody/defaults

## What AnonSync should refuse to clone

Do not clone these traits:

- product understanding that depends on translating between `v3 personal`, `v2.8 business`, and `Active Everywhere`
- control trust posture that depends on remembered WebUI/browser-warning folklore
- destructive actions that still feel like settings rather than reviewed operations

## Hard decision

AnonSync should keep **one operator grammar** across all projections and capability tiers.
A tier may change limits, integrations, or automation.
It may not change the meaning of:

- endpoint authority
- seat capability
- destructive review
- loss preview
- salvage ladder
- durable receipt

That is the stronger reason we are not cloning Resilio directly.
