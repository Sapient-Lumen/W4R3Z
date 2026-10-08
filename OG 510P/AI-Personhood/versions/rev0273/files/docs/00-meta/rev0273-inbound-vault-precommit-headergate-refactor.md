# rev0273 inbound-vault precommit headergate carry-forward

rev0273 upgrades the inbound-vault precommit to `external-contact-inbound-vault-precommit-v0.2` by binding it to `examples/external-contact-inbound-capture-shell-rev0273-no-inbound.json` and `tools/stage_external_contact_inbound_capture.py`.

The precommit still records no inbound artifact, no selected private vault root, no headers, no authentication results, no response clock, no retention permission, no counterparty authority, and no live-floor effect. Its job is now narrower and more enforceable: future raw email or provider-export bytes must be staged outside the public release tree before any public shell is emitted, and the shell cannot substitute for custody, authority, response, intake, import, recognition, waiver, adverse inference, or floor movement.
