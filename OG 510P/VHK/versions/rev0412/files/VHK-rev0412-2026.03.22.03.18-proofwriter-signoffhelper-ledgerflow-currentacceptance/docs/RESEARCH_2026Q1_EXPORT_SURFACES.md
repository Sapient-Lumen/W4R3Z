# Research notes: export surfaces and desktop-lane carry-through

This note captures the product lesson behind rev0167: the release lane should
travel with the exported artifact, not stay trapped in planning docs.

Why that matters on Linux:

- AutoKey's upstream project still describes itself as an X11 application and
  warns that it will not function correctly under Wayland. That means exported
  launchers/bundles cannot safely imply generic Linux parity.
- Espanso still documents Wayland as experimental on Linux and still notes that
  app-specific configurations are not supported there. That means user-facing
  entrypoints should preserve caveats instead of collapsing them.
- The GlobalShortcuts portal remains session-oriented and requires applications
  to create a session and bind shortcuts. Exported entrypoints need to remember
  when the trigger story is portal/session-shaped instead of pretending it is a
  timeless always-on hook.
- The freedesktop autostart spec remains a real deployment lane. Startup/autostart
  choices should therefore appear in outward-facing packaging/install surfaces,
  not only in architecture notes.
- keyd and xremap keep reinforcing the split between fast helper/remapper edges
  and the richer macro/runtime layer. Export surfaces should make that split
  legible to operators.

Product takeaway:

- a launcher, desktop entry, WM bundle, or shareable zip should carry enough
  support/release metadata that a recipient can tell which desktop/session lane
  is flagship, which ones are caveated, and which docs to read next
- that is a better Linux-native product shape than assuming every export target
  deserves the same claim language
