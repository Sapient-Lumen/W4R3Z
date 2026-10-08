# Research notes — rehearsal and stage truth on Linux-native automation (2026-03-16)

This revision keeps pushing one idea: the more VHK moves toward staged delivery, installed-lane rehearsal, and support packets, the more dangerous it becomes to flatten Linux reality back into static packaging prose.

## What others taught us

- `xdg-desktop-portal` is only the frontend. Real capability comes from backend implementations exposed under `org.freedesktop.impl.portal.*`, and interface routing is per desktop/session via `portals.conf`. That means configured routing, installed backend manifests, and live D-Bus interfaces are three different truths.
- wlroots-class desktops no longer have only one obvious backend story. Luminous is explicitly trying to be an alternative backend, which means VHK should not hard-code one backend assumption into its Wayland planning story.
- Support across compositors is still uneven enough that a project can have installed backend candidates and still miss live interfaces. That is exactly the sort of Linux-native mismatch a rehearsed install or staged release packet should keep visible.
- AutoKey remains a useful cautionary lesson because it still describes itself around Linux/X11. Espanso is useful for a different reason: it keeps precedence and active-scope boundaries explicit. VHK should keep learning that lesson on Linux too — be ambitious, but keep boundary truth visible.

## Product lesson for VHK

The repo now has several increasingly user-facing surfaces:

1. setup
2. native install
3. service composition
4. release deployment
5. release stage
6. host rehearsal
7. host dossier/support export

If the early stages surface host truth but the later ones revert to static prose, the project becomes less trustworthy exactly where operators need the most confidence.

That is why this revision carries the same compact truth model farther forward:

- `host_truth`
- `host_requirements`
- `portal_route_contract`

## Practical design rule

For Linux-native automation, every serious operator-facing handoff should answer three questions clearly:

- what does the host say should happen
- what is installed and selectable
- what is live right now

VHK does not need to solve every compositor/backend problem in one revision, but it should keep those questions visible all the way from planning to staged delivery to support packets.
