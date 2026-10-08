# Research — 2026 Q1 — session-service composition

The next truthful step after a reversible native install is not “yet another
package format.” It is the **login/session composition layer**.

Linux-native automation depends on more than shipping one binary or one zip:

- how the watcher/event plane starts
- how user-service environment variables are exported
- how login-time startup is bridged across desktop environments
- how external helper daemons are kept explicit instead of turning into hidden
  assumptions

Patterns worth borrowing:

- **systemd user units** for long-lived VHK-owned watcher/event planes
- **socket activation** where it keeps startup cheap and on-demand
- **environment.d** for reviewable service environment exports
- **XDG autostart desktop files** as an interoperable bridge layer when a
  desktop still expects login-time `.desktop` startup semantics

The big lesson is compositional honesty:

- a VHK-owned busd service is one part of the story
- an autostart bridge is another part
- helper daemons like `ydotoold` are often still separate lifecycle objects
- none of those pieces should be flattened into “Linux works like AHK now”
