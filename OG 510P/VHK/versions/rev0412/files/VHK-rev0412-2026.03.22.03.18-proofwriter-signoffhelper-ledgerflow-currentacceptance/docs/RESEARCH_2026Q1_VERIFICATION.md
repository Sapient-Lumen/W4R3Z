# Research 2026 Q1 - verification-driven Linux automation planning

This note captures why VHK now emits `verification_gates` instead of stopping
at strategy-only recommendations.

## 1) Portals are still capability-specific, not one blanket Wayland feature

The current portal stack still exposes separate interfaces for global
shortcuts, screenshot/screencast, remote desktop, input capture, clipboard,
and other surfaces. That means a project should verify each capability it
depends on instead of treating “Wayland support” like a single boolean.

## 2) Wayland text, pointer, and capture paths still diverge by mechanism

Text entry, pointer injection, and capture continue to live on different
mechanisms:

- virtual-keyboard oriented tools for text-heavy paths
- portal/helper/uinput seams for harder input automation
- portal-first or compositor-specific capture for vision flows

That split is not merely implementation detail. It affects what teams should
prove before shipping.

## 3) Dedicated remappers still occupy a different product layer from macro runtimes

keyd / kanata / KMonad / xremap-class tools remain better fits for always-on
key semantics, layers, tap-hold, and low-latency remap behavior than a
macro-oriented runner core.

So verification should preserve that separation too:

- VHK validates macro behavior and export surfaces
- remapper configs validate leader/layer/raw-key behavior
- helper boundaries validate capability-specific seams

## 4) Capability-specific release gates are a better Linux-native contract

The old implicit contract looked like:

- “does this project support Linux?”

The better contract is:

- text path verified
- capture path verified
- trigger path verified
- pointer path verified or explicitly helper-boundary only
- raw input capture remains opt-in unless separately proven

This is the reasoning behind the new planner surface.
