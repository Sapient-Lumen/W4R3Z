# Research — 2026 Q1 — native local installs

The next practical lesson after runtime embedding is not another abstract
package format. It is one conservative local-install lane that behaves like a
real Linux application without pretending that all helper or compositor
boundaries disappeared.

Patterns worth borrowing:

- XDG-local placement for per-user data and launchers
- one isolated runtime per application, exposed through one stable command path
- desktop metadata that can be installed and removed alongside the app tree
- an uninstall path that is as explicit as install

That combination does not make VHK equivalent to AHK on every Linux desktop.
It does create a better proving ground: maintainers can validate bundle,
runtime, launcher, and discoverability as one coherent lane before layering on
Flatpak/AppImage or privileged helper stories.
