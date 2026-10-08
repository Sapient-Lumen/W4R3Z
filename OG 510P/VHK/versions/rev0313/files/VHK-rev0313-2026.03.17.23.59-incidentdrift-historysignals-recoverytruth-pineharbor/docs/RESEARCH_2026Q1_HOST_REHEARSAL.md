# Research — host rehearsal and desktop/service probes

This note captures the practical lessons behind VHK's host rehearsal pack.

## Why desktop validation and launch ids matter

A local install lane should not stop at “the files copied somewhere.” A desktop
entry needs to validate cleanly, and the launch id should be explicit enough
that a maintainer can probe it with the same desktop-facing toolchain the shell
already understands.

That does **not** prove every desktop menu indexes or surfaces the launcher the
same way, but it is still a better proof surface than hoping the right `.desktop`
file happened to land nearby.

## Why user-service status and logs need first-class scripts

Once a project owns a long-lived watcher plane, install alone is not enough.
The useful questions become:

- is the user socket enabled?
- is the service actually active after login?
- where did recent logs land?

Those are systemctl/journalctl questions, so the rehearsal pack makes them
explicit rather than asking maintainers to remember ad-hoc shell commands.

## Related patterns worth borrowing

- desktop entry validation is a lightweight but useful packaging truth check
- `gtk-launch` is a practical launcher-id probe for GTK/freedesktop-oriented
  app installs
- `systemctl --user` and `journalctl --user` are the honest status/log surfaces
  for bundle-native watcher lanes running under the user manager
- together they point toward a simple VHK rule: reviewed payloads should come
  with reviewed **operability** scripts, not just reviewed bundles


## Why one rehearsal report is better than scattered stdout

Once the native launcher itself can emit live status JSON and Markdown, the next honest move is not another ad-hoc shell checklist; it is one host-facing report that captures those installed-lane surfaces together with desktop/service probes. That keeps operators reviewing one coherent artifact instead of bouncing between `status`, launcher docs, and user-manager commands.

## Why unit-path and verify probes belong in the report

Two systemd questions matter during rehearsal and are easy to miss if they are not scripted:

- where is the running user manager actually loading units from?
- do the installed unit files still parse cleanly as unit files before we argue about runtime behavior?

That is why the report bridge now leans on `systemctl --user show -p UnitPath --value` for live unit-search visibility and `systemd-analyze --user verify` for static unit-file correctness.
