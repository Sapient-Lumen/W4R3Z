# discoverable_passkey_uv_required_chromium_virtual

This scenario is the honest first “good lane” for `passkeylab`.

It keeps the ceremony simple:

- register a discoverable passkey,
- require user verification,
- prefer platform attachment,
- no extra extensions,
- and use a Chromium-class WebDriver virtual authenticator.

The point is not to claim “Chromium equals the world”.
The point is to freeze one repeatable automation lane that can support bundle exchange, shrinking, and release triage.
