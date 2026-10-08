# Review packet state machine — rev0020

The state machine blocks the dangerous shortcut from “we found a source family”
to “the cube says X happened.” The intended transition chain is:

route memory → packet draft → source family → lifecycle map → source carrier →
custody/fixity/privacy/identity/legal gates → source voice/modality → defeater
scan → evidence atom candidate → claim candidate → review → private admission
or rejection → display review → public display only by explicit receipt.

Rev0020 only opens states through definitional/synthetic use. Future states such
as private admission, public display, correction, rollback, and retirement are
modeled but not entered.
