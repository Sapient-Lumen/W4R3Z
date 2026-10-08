# Research notes — share-safe Linux support dossiers (2026 Q1)

This revision pushes VHK's installed-host dossier toward a more realistic support posture: collect raw evidence locally under XDG state, then generate a share-safe copy plus a redaction report before external handoff.

## Current references that informed this pass

- The XDG Base Directory spec says `$XDG_STATE_HOME` is for user-specific state that persists across restarts but is not important or portable enough for `$XDG_DATA_HOME`, including logs/history. That keeps the raw and redacted dossier roots in the right Linux-native place instead of mixing them into project data. 
- `journalctl` remains the standard interface for reading journal entries accessible to the calling user, which means support packets can legitimately include sensitive user-service logs if they are archived blindly.
- The Desktop Entry spec's additional actions model is explicitly additive, which supports VHK exposing support/report actions without making them the only way to reach the application.
- OWASP's Logging Cheat Sheet warns against needlessly logging sensitive data, and GitHub's secret-scanning docs focus on exposed tokens/credentials as a class of leak worth catching early. VHK should borrow that lesson for support packets too: the first export should not assume raw logs are safe to share.

## Product direction this supports

The repo now has a stronger operator story:

1. reviewed bundle
2. native install + service composition
3. host rehearsal + live status
4. host dossier collection under XDG state
5. share-safe dossier export with a redaction report

That is still not a full GUI support center, but it is a much more believable Linux-native support workflow than “zip whatever is in the state directory and hope it is fine.”
