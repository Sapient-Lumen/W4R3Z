# rev0266 mail-ready draft and send-proof carry-forward

rev0266 carries forward the mail-ready `.eml` and send-proof controls while adding the inbound-capture shell as the next downstream guard. The `.eml` remains marked `NOT-SENT`, the send-proof record remains `not-sent-no-proof`, and neither can start a response clock or create a failed-gate shell.

The only allowed use of these surfaces is human review before a future authorized send. If a send later occurs, the operator must capture `sent_at`, sender role, transport channel, message/header source, private transport trace locator, and deadline computation before any response/no-response handling. A draft, body hash, public email, authorization card, send-proof placeholder, inbound-vault precommit, or capture shell remains non-operative until those actual proofs exist.
