# Research — deployment-truth surfaces and Linux-native install lessons

## Why this note exists

VisualHotKey is trying to learn from existing Linux automation tools without
copying their blind spots. The next useful lesson is not only about runtime
features, but about how deployment/install surfaces stay honest.

## External lessons worth keeping

### 1) Portals are a routed system, not a single feature bit

Upstream portal docs keep the split clear: `xdg-desktop-portal` is the frontend,
while real implementations come from backend services that expose
`org.freedesktop.impl.portal.*`. Routing is configured per interface and can be
desktop-specific. That means configured routing, installed backend manifests,
and live D-Bus availability are different truths.

Product lesson for VHK:
- deployment docs should keep those truths visible together
- host review should not stop at "portal package present"
- operator-facing packs should explain why a host is degraded, not only that it
  is degraded

### 2) wlroots reality is still plural

Luminous is now a real wlroots-oriented portal backend alternative rather than a
thought experiment, and it advertises RemoteDesktop/InputCapture in addition to
screen capture interfaces. That is exactly the sort of ecosystem drift that a
Linux-native tool has to model honestly.

Product lesson for VHK:
- keep alternative backend ids visible
- avoid assuming one compositor family has one canonical backend forever
- preserve configured vs installed vs live backend truth in docs and JSON

### 3) AutoKey still teaches scope honesty

AutoKey still documents itself as a Linux/X11 automation utility. That is not a
weakness to hide; it is a product-shape lesson. Strong Linux tools often stay
honest by making scope boundaries explicit.

Product lesson for VHK:
- prefer explicit session/desktop truth over flattened "Linux support" language
- let deployment docs surface why a lane is limited on a given host
- keep reviewable generated artifacts instead of burying platform assumptions in
  internals

### 4) Espanso still teaches precedence honesty

Espanso's docs are unusually clear that only one app-specific configuration is
active at a time. That kind of precedence rule matters because it keeps host and
operator expectations aligned with reality.

Product lesson for VHK:
- deployment packs should surface one compact truth model instead of mixing
  several hidden precedence rules
- setup/native/service/release packs should not each invent their own host-story
  summary
- a shared deployment-truth contract is better than four slightly different
  approximations

## What VHK should do with these lessons

The right next move is to make deployment-facing packs carry a shared truth
contract, not just package hints.

Concrete direction:
- `gen-setup-pack` should show observed deployment truth before asking operators
  to apply package/helper recipes
- `gen-native-install-pack` should keep current host truth attached to the local
  app handoff
- `gen-service-compose-pack` should keep that same truth attached to long-lived
  service setup
- `gen-release-deploy-pack` should keep lane claims tied to the observed host
  truth instead of floating as static copy

This keeps VHK closer to the AHK-level product goal in the right way: not by
pretending Linux is one platform, but by making the platform boundaries legible
and reviewable.
