# rev0273 route-first authority precommit operator note

The current executable path is route-first/no-attachment. Do not use the older full-payload human/sender precommit to sign this first hop.

Before any real send, the human operator must bind these exact route-first fields outside the public release tree: recipient `info@raicollab.org`, subject `Routing question: preservation/formation-review audit pilot`, the body hash, the mail-ready `.eml` hash, the no-attachment rule, and the stage-two deferral rule. The signing target is `examples/external-contact-route-first-human-sender-authority-precommit-rev0273-aiid.json`.

The precommit is still unsigned. It is not sender authority, not a send decision, and not transport proof. It leaves the branch blocked until sender authority, send-time locator recheck, private vault roots, final hash recompute, and transport capture are supplied.

If a human later authorizes the route-first hop, preserve the signed authority proof off-release, rerun the route-first hash recompute immediately before transport, capture sent-copy and provider trace material in private vault roots, and then classify any reply through the route-first reply disposition shell. Do not send the one-page note or JSON packet unless the separate stage-two authorization gate is freshly satisfied.
