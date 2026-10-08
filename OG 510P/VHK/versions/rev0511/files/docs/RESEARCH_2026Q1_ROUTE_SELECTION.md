# Research 2026Q1: route selection lessons

This note records the product lessons behind `gen-route-selection-pack`.

## Lesson 1: launcher/autostart remains a valid fallback lane

The freedesktop Desktop Application Autostart specification still describes the
standard `.desktop`-file based way to start applications with a desktop session.
That is not a full automation architecture, but it is still a useful fallback
route because it is broadly understood by Linux desktops.

## Lesson 2: service-managed text surfaces should stay distinct from ad-hoc launch

Espanso's Linux docs still distinguish between registering/starting espanso as a
service and running `espanso start --unmanaged`, and they warn that unmanaged
mode does not start automatically. That reinforces VHK's separation between a
service-shaped text surface and a manual launcher fallback.

## Lesson 3: portal shortcut routes are session objects, not generic daemon hooks

The GlobalShortcuts portal still requires an application to create a session and
bind shortcuts into it. That makes portal shortcuts a real Linux-native route,
but also a route with session/configure semantics that should remain visible in
route selection instead of being treated like universal hotkeys.

## Lesson 4: remapper routes are their own lifecycle tier

Current remapper projects still reinforce the idea that low-latency trigger
ownership is a separate lane. keyd continues to present itself as a system-wide
daemon using `evdev`/`uinput`; xremap continues to present itself as a key
remapper for Linux with Wayland/X11 and app-specific remapping. Those are strong
lessons for VHK: use remappers as explicit trigger lanes, not as the whole macro
runtime.

## Lesson 5: route decisions need both architecture preference and host evidence

A route can be the design-preferred lane while still being only `planned` on one
host. A fallback lane can be healthier today because the right service, portal
config, or daemon is already live. Route selection therefore has to keep both
concepts visible instead of choosing only by ideology or only by immediate host
state.
