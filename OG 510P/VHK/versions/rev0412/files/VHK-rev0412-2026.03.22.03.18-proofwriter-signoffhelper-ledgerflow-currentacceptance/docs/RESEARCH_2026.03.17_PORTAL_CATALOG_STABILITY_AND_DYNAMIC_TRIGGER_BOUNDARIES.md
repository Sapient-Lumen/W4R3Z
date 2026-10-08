# Research — portal catalog stability and dynamic trigger boundaries

## Question

What should VHK learn from current Wayland trigger surfaces beyond the already
captured “portal shortcut support varies by desktop” lesson?

## Takeaway

The sharper lesson is not just **whether** portal shortcuts exist. It is **which
kind of project inventory fits them**.

The current Linux ecosystem keeps reinforcing that portal-managed shortcuts are
strongest when an app can present a stable, predeclared action catalog:

- the GlobalShortcuts portal itself is session-oriented and built around binding
  explicit shortcuts into a session-owned catalog
- Kando’s Linux/Hyprland docs also lean on stable shortcut identifiers and then
  let the compositor own the real bind, which is another form of “catalog first,
  desktop-owned trigger second”

That is a different shape from:

- helper-sensitive hotkeys that wake capture/pointer-heavy flows
- recorder churn where bindings appear/disappear rapidly
- routes that are better owned by compositor config, remapper layers, or
  launcher hubs

## Why this matters for VHK

Before this revision, VHK already had:

- portal surface/route output
- launcher/menu-hub planning
- helper-boundary planning
- linting for freedesktop shortcut export gaps

But the planner still under-modeled **catalog stability**. On Wayland, that made
it too easy for a project to look portal-shaped simply because it had hotkeys.

That is not honest enough for an AHK-class Linux tool.

## Product conclusion

So the planner should reason explicitly about:

- how many bindings look like stable portal-catalog actions
- how many bindings are dynamic/helper-sensitive and should prefer native or
  launcher fallbacks
- whether a specific hotkey macro should try portal first or not

That leads to the product change in this revision:

- surface evidence now names `stable_shortcut_candidates` and
  `dynamic_shortcut_candidates`
- reference patterns now include `portal-session-catalog-lane`
- activation routing and per-macro route ownership now stop defaulting every
  Wayland hotkey toward the portal lane

## Practical hierarchy

For trigger ownership on modern Linux desktops, the clearer hierarchy is:

1. portal shortcut session for stable action catalogs
2. compositor/native bind route for hotter or desktop-shaped trigger ownership
3. launcher/palette surface for discoverable or fallback activation

Those are not interchangeable. They are different Linux-native product lanes.
