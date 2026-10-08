# Official voter-information navigation-menu surface checklist

Use this checklist for official voter-information routes where **the controlling destination, office page, or current answer lane is reached through expandable site navigation menus, fly-outs, mega-menus, hamburger navigation, or similar structures**.

## Trigger and destination posture

- [ ] Record which official routes rely on expandable navigation to expose controlling destinations.
- [ ] Review whether the menu opens through explicit click/tap/keyboard activation rather than hover-only posture.
- [ ] Review whether voters can distinguish direct destination links from submenu toggles.
- [ ] Review whether the navigation identifies clearly which section, branch, or page is current.
- [ ] Review whether the route preserves a usable parent-page fallback when important destinations live inside a submenu.

## Desktop/mobile continuity and semantics

- [ ] Review whether compact/mobile navigation preserves the same destination naming and hierarchy as desktop navigation.
- [ ] Review whether touch users can reach the same official destinations without hidden hover-only behavior.
- [ ] Review whether ordinary site navigation uses truthful navigation/list/link semantics rather than application-menu semantics.
- [ ] Review whether dropdown/fly-out posture remains open long enough for ordinary use and closes predictably.
- [ ] Review whether the same destination can be re-found without reopening unrelated branches or exploring the whole site again.

## Accessibility and evidence review

- [ ] Review whether top-level navigation items receive visible focus and keyboard users can inspect submenu content predictably.
- [ ] Review whether `Esc` or ordinary focus movement closes open menu posture without trapping users in the navigation region.
- [ ] Review whether screen-reader users receive enough navigation structure to understand the hierarchy and current branch.
- [ ] Preserve a small public digest of which routes use expandable navigation, whether parent-page fallbacks exist, and whether compact/mobile navigation keeps the same destination continuity.
- [ ] Do not retain hover telemetry, session replay, individualized click trails, or other interaction exhaust merely to prove that the destination existed in a menu.
